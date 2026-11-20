import os
import sys
import subprocess
import shutil

def check_ffmpeg():
    print("=" * 50)
    print("[INFO] Checking system environment for FFmpeg...")
    if shutil.which("ffmpeg") is None:
        print("[ERROR] FFmpeg is not installed or not in your system PATH.")
        print("        Install FFmpeg first (e.g., 'winget install ffmpeg' on Windows).")
        sys.exit(1)
    print("[SUCCESS] FFmpeg is detected and ready.")
    print("=" * 50)

def convert_movie(input_path):
    # Clean up quotes if the user dragged and dropped the file into the terminal
    input_path = input_path.strip('"\'')
    
    if not os.path.isfile(input_path):
        print(f"[ERROR] File not found: {input_path}")
        return

    file_dir = os.path.dirname(input_path)
    file_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(file_dir, f"{file_name}_LCD_ready.mp4")

    print(f"\n[INFO] Starting conversion for: {os.path.basename(input_path)}")
    print("[INFO] Target format: H.264 (AVC) + AAC in MP4 container (720p max for Abid house LCD compatibility)...\n")

    # FFmpeg command matching your downloader's exact LCD specs:
    # - Video: H.264 (libx264), Main profile Level 3.1 (safest for older TV/LCD hardware decoders), yuv420p pixel format
    # - Scale: Caps height at 720p while keeping aspect ratio and ensuring even dimensions (-2)
    # - Audio: AAC stereo at 128k
    # - Faststart: Moves metadata to the front so USB/media players load it immediately
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "scale=-2:'min(720,ih)'",
        "-c:v", "libx264",
        "-profile:v", "main",
        "-level", "3.1",
        "-pix_fmt", "yuv420p",
        "-crf", "23",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ac", "2",
        "-movflags", "+faststart",
        "-y",
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"\n[SUCCESS] Movie converted successfully for your Abid house LCD screen!")[cite: 1]
        print(f"[SAVED]   {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Conversion failed with error code {e.returncode}")

if __name__ == "__main__":
    check_ffmpeg()
    
    movie_file = input("Drag and drop the movie file here (or paste the file path): ").strip()
    
    if movie_file:
        convert_movie(movie_file)
    else:
        print("[ERROR] No file path provided. Exiting.")