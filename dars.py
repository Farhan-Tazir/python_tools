import os
import subprocess
import shutil
import sys

def check_and_install_ytdlp():
    print("Checking yt-dlp installation ........")
    
    if shutil.which("yt-dlp") is None:
        print("yt-dlp not found")
        print("Installing yt-dlp.................")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            print("yt-dlp installed successfully")
        except subprocess.CalledProcessError:
            print("Error: Failed to install yt-dlp. Please ensure you have pip installed.")
            sys.exit(1)
    else:
        print("yt-dlp found")

def main():
    check_and_install_ytdlp()

    links_file_path = input("Paste the path of your links file: ").strip().strip("\"'") 
    output_dir = input("Paste the path of out (where you want to download all of the things): ").strip().strip("\"'")

    if not os.path.isfile(links_file_path):
        print(f"Error: The file '{links_file_path}' does not exist.")
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(links_file_path, 'r') as file:
        links = [line.strip() for line in file if line.strip()]

    for n, link in enumerate(links, start=1):
        folder_path = os.path.join(output_dir, str(n))
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        print(f"\n--- Downloading link {n} into folder '{n}' ---")
        
        command = ["yt-dlp", "-x", "--audio-format", "mp3", "-P", folder_path, link]
        
        try:
            # We use Popen instead of run() so we can read the output line by line as it happens
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            for line in process.stdout:
                # Keep showing the normal download progress
                sys.stdout.write(line)
                sys.stdout.flush()
                
                # The moment yt-dlp triggers the audio extraction, print our friendly message
                if "[ExtractAudio]" in line:
                    print("\n" + "="*50)
                    print("converting to mp3 ...... please wait calmly! 😊")
                    print("="*50 + "\n")
                    
            # Wait for the single process to finish before moving to the next link
            process.wait()
            
            if process.returncode != 0:
                print(f"Error downloading link: {link}. Skipping to next...")
                
        except Exception as e:
            print(f"Error processing link {link}: {e}")

    print("\nCongratulations! your all links downloaded successfully")

if __name__ == "__main__":
    main()