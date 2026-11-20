"""
Fast movie converter for the Abid house LCD (H.264 Main L3.1 + AAC, 720p max, MP4).

Why this is faster than the old version:
  1. It PROBES the file first. If the video/audio is already LCD-compatible,
     it is copied (no re-encoding) -> finishes in seconds.
  2. If video must be re-encoded, it tries your GPU encoder first
     (NVIDIA NVENC / Intel Quick Sync / AMD AMF). Falls back to the CPU.
  3. The CPU fallback uses preset "veryfast" instead of "medium".
  4. It only keeps the first video + first audio track (skips subtitle
     streams that can crash or slow the MP4 conversion).

Usage:
  python Abid_house_screen_format_fast.py                  (asks for a path)
  python Abid_house_screen_format_fast.py movie1.mkv movie2.avi   (or drag files onto the script)
"""
import json
import os
import shutil
import subprocess
import sys
import time

MAX_HEIGHT = 720
MAX_LEVEL = 31  # H.264 level 3.1, written as the integer 31 by ffprobe
SAFE_PROFILES = {"baseline", "constrained baseline", "main"}

# (ffmpeg encoder name, friendly name, encoder arguments)
HW_ENCODERS = [
    ("h264_nvenc", "NVIDIA NVENC GPU",
     ["-c:v", "h264_nvenc", "-preset", "p4", "-rc", "vbr", "-cq", "23", "-b:v", "0",
      "-profile:v", "main", "-level", "3.1", "-pix_fmt", "yuv420p"]),
    ("h264_qsv", "Intel Quick Sync GPU",
     ["-c:v", "h264_qsv", "-preset", "veryfast", "-global_quality", "23",
      "-profile:v", "main", "-level", "3.1", "-pix_fmt", "nv12"]),
    ("h264_amf", "AMD AMF GPU",
     ["-c:v", "h264_amf", "-quality", "speed", "-rc", "cqp", "-qp_i", "23", "-qp_p", "23",
      "-profile:v", "main", "-level", "3.1", "-pix_fmt", "yuv420p"]),
]
SW_ENCODER = ("libx264", "CPU x264 (veryfast)",
              ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
               "-profile:v", "main", "-level", "3.1", "-pix_fmt", "yuv420p"])


def check_tools():
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            print(f"[ERROR] {tool} is not installed or not in PATH.")
            print("        Install FFmpeg first (e.g., 'winget install ffmpeg' on Windows).")
            sys.exit(1)


def encoder_works(args):
    """Encode 0.2 seconds of fake video to see if this encoder really works on this PC."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error",
           "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=0.2:r=25",
           *args, "-f", "null", "-"]
    try:
        return subprocess.run(cmd, capture_output=True, timeout=30).returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def pick_encoder():
    listed = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"],
                            capture_output=True, text=True).stdout
    for name, label, args in HW_ENCODERS:
        if name in listed and encoder_works(args):
            return name, label, args
    return SW_ENCODER


def probe(path):
    cmd = ["ffprobe", "-v", "error",
           "-show_entries", "stream=codec_type,codec_name,profile,level,height,pix_fmt,channels",
           "-of", "json", path]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    streams = json.loads(out).get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    return video, audio


def video_is_compatible(v):
    level = int(v.get("level") or 0)
    return (v.get("codec_name") == "h264"
            and v.get("pix_fmt") == "yuv420p"
            and (v.get("profile") or "").lower() in SAFE_PROFILES
            and 0 < level <= MAX_LEVEL
            and int(v.get("height") or 99999) <= MAX_HEIGHT)


def audio_is_compatible(a):
    return (a.get("codec_name") == "aac"
            and a.get("profile") == "LC"
            and int(a.get("channels") or 99) <= 2)


def build_command(src, dst, video, audio, encoder_args):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats",
           "-i", src,
           "-map", "0:v:0", "-map", "0:a:0?",  # first video + first audio only
           "-sn", "-dn"]                        # no subtitles / data streams

    if encoder_args is None:  # copy video
        cmd += ["-c:v", "copy"]
    else:
        if int(video.get("height") or 0) > MAX_HEIGHT:
            cmd += ["-vf", f"scale=-2:{MAX_HEIGHT}:flags=bilinear"]
        cmd += encoder_args

    if audio is not None:
        if audio_is_compatible(audio):
            cmd += ["-c:a", "copy"]
        else:
            cmd += ["-c:a", "aac", "-b:a", "128k", "-ac", "2"]

    # Write to a .part file so a cancelled run never leaves a broken .mp4 behind
    cmd += ["-movflags", "+faststart", "-f", "mp4", "-y", dst + ".part"]
    return cmd


def run_ffmpeg(cmd, dst):
    try:
        ok = subprocess.run(cmd).returncode == 0
    except KeyboardInterrupt:
        print("\n[INFO] Cancelled.")
        ok = False
    part = dst + ".part"
    if ok:
        os.replace(part, dst)
    elif os.path.exists(part):
        os.remove(part)
    return ok


def convert_movie(input_path, encoder):
    input_path = input_path.strip().strip('"\'')
    if not os.path.isfile(input_path):
        print(f"[ERROR] File not found: {input_path}")
        return

    folder, base = os.path.split(input_path)
    output_path = os.path.join(folder, f"{os.path.splitext(base)[0]}_LCD_ready.mp4")

    print(f"\n[INFO] File: {base}")
    try:
        video, audio = probe(input_path)
    except subprocess.CalledProcessError:
        print("[ERROR] ffprobe could not read this file.")
        return
    if video is None:
        print("[ERROR] No video stream found.")
        return

    copy_video = video_is_compatible(video)
    enc_name, enc_label, enc_args = encoder
    print("[INFO] Video: " + ("already LCD-compatible -> COPY (instant)"
                              if copy_video else f"re-encode with {enc_label}"))
    if audio is None:
        print("[INFO] Audio: none")
    else:
        print("[INFO] Audio: " + ("already AAC stereo -> COPY"
                                  if audio_is_compatible(audio) else "convert to AAC 128k stereo"))

    start = time.time()
    cmd = build_command(input_path, output_path, video, audio, None if copy_video else enc_args)
    ok = run_ffmpeg(cmd, output_path)

    # If the GPU encoder failed on this particular file, retry on the CPU
    if not ok and not copy_video and enc_name != SW_ENCODER[0]:
        print(f"\n[WARN] {enc_label} failed on this file. Retrying with CPU...")
        cmd = build_command(input_path, output_path, video, audio, SW_ENCODER[2])
        ok = run_ffmpeg(cmd, output_path)

    if ok:
        print(f"\n[SUCCESS] Done in {time.time() - start:.0f} seconds.")
        print(f"[SAVED]   {output_path}")
    else:
        print("\n[ERROR] Conversion failed.")


if __name__ == "__main__":
    check_tools()
    files = sys.argv[1:]
    if not files:
        entered = input("Drag and drop the movie file here (or paste the file path): ").strip()
        files = [entered] if entered else []
    if not files:
        print("[ERROR] No file path provided. Exiting.")
        sys.exit(1)

    print("[INFO] Detecting fastest encoder...")
    encoder = pick_encoder()
    print(f"[INFO] Encoder: {encoder[1]}")

    for f in files:
        convert_movie(f, encoder)