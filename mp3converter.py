import os
# Updated for MoviePy 2.0+
from moviepy import AudioFileClip

def convert_file_to_mp3():
    # Prompt for the single input file path and strip extra quotes from drag-and-drop
    input_file = input("Drag and drop the video/audio file here (or paste the file path): ").strip().strip('"\'')
    
    if not os.path.isfile(input_file):
        print(f"[ERROR] File not found: {input_file}")
        return

    # Save the MP3 in the exact same folder with the same filename
    file_dir = os.path.dirname(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(file_dir, f"{base_name}.mp3")

    print("\nLoading video...")
    try:
        # 1. Target your video file
        video = AudioFileClip(input_file)

        print("Converting to MP3...")
        # 2. Extract and save the audio as an MP3[cite: 2]
        video.write_audiofile(output_file)

        # 3. Close the file to free up system memory[cite: 2]
        video.close()
        print(f"\nDone! Saved to: {output_file}")
    except Exception as e:
        print(f"\n[ERROR] Conversion failed: {e}")

if __name__ == "__main__":
    convert_file_to_mp3()
