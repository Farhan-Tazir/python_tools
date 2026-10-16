"""
web_to_mp4.py
Convert WebP (animated) or WebM files to MP4.

Install once:
    pip install pillow imageio imageio-ffmpeg

Usage:
    python web_to_mp4.py input.webp
    python web_to_mp4.py input.webm output.mp4
"""

import subprocess
import sys
from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
from PIL import Image, ImageSequence


def webm_to_mp4(src: Path, dst: Path) -> None:
    """WebM is already a video, so we just ask ffmpeg to re-encode it."""
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()  # ffmpeg bundled with imageio-ffmpeg
    cmd = [
        ffmpeg, "-y",                 # -y = overwrite output if it exists
        "-i", str(src),               # input file
        "-c:v", "libx264",            # H.264 video codec (works everywhere)
        "-pix_fmt", "yuv420p",        # pixel format compatible with most players
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",  # make width/height even
        "-c:a", "aac",                # audio codec (ignored if no audio)
        str(dst),
    ]
    subprocess.run(cmd, check=True)


def webp_to_mp4(src: Path, dst: Path) -> None:
    """Animated WebP is a set of frames, so we read each frame and write a video."""
    img = Image.open(src)
    frames = []
    durations = []

    for frame in ImageSequence.Iterator(img):
        # Convert to RGB: MP4 has no transparency (alpha) channel
        rgb = frame.convert("RGB")
        frames.append(rgb)
        durations.append(frame.info.get("duration", 100))  # milliseconds

    if not frames:
        raise ValueError("No frames found in the WebP file.")

    # Average frame time -> frames per second
    avg_ms = sum(durations) / len(durations)
    fps = max(1, round(1000 / avg_ms)) if avg_ms > 0 else 10

    # H.264 needs even width and height, so crop 1 pixel if needed
    w, h = frames[0].size
    w -= w % 2
    h -= h % 2

    with imageio.get_writer(
        str(dst), fps=fps, codec="libx264", pixelformat="yuv420p"
    ) as writer:
        for f in frames:
            writer.append_data(imageio.core.util.Array(
                __import__("numpy").asarray(f.crop((0, 0, w, h)))
            ))


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python web_to_mp4.py input.(webp|webm) [output.mp4]")
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"File not found: {src}")
        sys.exit(1)

    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".mp4")
    ext = src.suffix.lower()

    if ext == ".webm":
        webm_to_mp4(src, dst)
    elif ext == ".webp":
        webp_to_mp4(src, dst)
    else:
        print("Unsupported file type. Use .webp or .webm")
        sys.exit(1)

    print(f"Done! Saved: {dst}")


if __name__ == "__main__":
    main()