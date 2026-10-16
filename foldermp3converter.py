
from moviepy import AudioFileClip
from pathlib import Path

# Folder containing your videos
source_folder = Path(r"E:\Download\MFT Songs")

# Folder where MP3 files will be saved
output_folder = Path(r"E:\Download\MFT songs mp3")

# Create the output folder automatically if it doesn't exist
output_folder.mkdir(parents=True, exist_ok=True)

# Supported video formats
video_extensions = {
    ".mp4", ".mkv", ".avi", ".mov",
    ".webm", ".mpeg", ".wmv"
}

# Find video files
video_files = [
    file for file in source_folder.iterdir()
    if file.is_file() and file.suffix.lower() in video_extensions
]

if not video_files:
    print("No video files found!")

for video_path in video_files:
    # Save MP3 in the separate output folder
    mp3_path = output_folder / (video_path.stem + ".mp3")

    try:
        print(f"Converting: {video_path.name}")

        with AudioFileClip(str(video_path)) as audio:
            audio.write_audiofile(str(mp3_path), logger=None)

        print(f"Saved: {mp3_path}")

    except Exception as e:
        print(f"Failed: {video_path.name}")
        print(f"Error: {e}")

print("\nAll conversions finished!")
