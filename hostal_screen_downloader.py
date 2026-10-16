import sys
import subprocess

def check_system_python():
    print("=" * 50)
    print("[INFO] Checking Python system environment...")
    print(f"Python Version : {sys.version.split()[0]}")
    print(f"Python Path    : {sys.executable}")
    print("=" * 50)
    
    # Check if yt-dlp is installed
    try:
        import yt_dlp
        print("[SUCCESS] yt-dlp module is detected and ready.")
    except ImportError:
        print("[WARNING] yt-dlp not found. Installing via pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        print("[SUCCESS] yt-dlp installed successfully.")
    print("=" * 50)

def download_video(url):
    print(f"\n[INFO] Starting download for: {url}")
    print("[INFO] Target format: H.264 (AVC) + AAC in MP4 container (720p max for your Abid house LCD compatibility)...\n")
    
    # yt-dlp command configured for old LCD compatibility
    command = [
        "yt-dlp",
        "-f", "bv*[vcodec^=avc1][height<=720]+ba[acodec^=mp4a]/b[vcodec^=avc1][height<=720]",
        "--merge-output-format", "mp4",
        url
    ]
    
    try:
        subprocess.run(command, check=True)
        print("\n[SUCCESS] Video downloaded and formatted successfully for your Abid house LCD screen!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Download failed with error code {e.returncode}")

if __name__ == "__main__":
    check_system_python()
    
    # Prompt user for the video link
    video_url = input("provide the link for the vidio: ").strip()
    
    if video_url:
        download_video(video_url)
    else:
        print("[ERROR] No link provided. Exiting.")