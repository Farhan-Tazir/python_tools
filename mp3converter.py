# Updated for MoviePy 2.0+
from moviepy import AudioFileClip

print("Loading video...")
# 1. Target your video file
video = AudioFileClip("F:\Download\MFT songs mp3\Faryad  Ajmal Khattak BaBa  Pashto New Ghazal 2025.mp4")

print("Converting to MP3...")
# 2. Extract and save the audio as an MP3
video.write_audiofile("F:\Download\MFT songs mp3\Faryad  Ajmal Khattak BaBa  Pashto New Ghazal 2025.mp3")

# 3. Close the file to free up system memory
video.close()
print("Done! Check your folder.")

