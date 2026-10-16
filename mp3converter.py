# Updated for MoviePy 2.0+
from moviepy import AudioFileClip

print("Loading video...")
# 1. Target your video file
video = AudioFileClip("E:\Download\MFT Songs\Rula Diya Mashup ｜ Zack Knight ｜ Darshan Raval ｜ Emotions Chillout 2024 ｜ BICKY OFFICIAL [50aQ9Uek73Q].webm")

print("Converting to MP3...")
# 2. Extract and save the audio as an MP3
video.write_audiofile("E:\Download\MFT songs mp3\Rula Diya Mashup ｜ Zack Knight ｜ Darshan Raval ｜ Emotions Chillout 2024 ｜ BICKY OFFICIAL [50aQ9Uek73Q].mp3")

# 3. Close the file to free up system memory
video.close()
print("Done! Check your folder.")

