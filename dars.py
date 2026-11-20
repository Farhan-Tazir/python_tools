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
        
        # --progress forces the single-line progress bar even when piped
        command = ["yt-dlp", "--progress", "-x", "--audio-format", "mp3", "-P", folder_path, link]
        
        try:
            # Binary mode (no text=True) preserves raw \r characters so lines overwrite in place
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT
            )
            
            line_buffer = b""
            while True:
                byte = process.stdout.read(1)
                if not byte and process.poll() is not None:
                    break
                if byte:
                    # Write raw bytes directly to stdout buffer so \r overwrites the current line
                    sys.stdout.buffer.write(byte)
                    sys.stdout.buffer.flush()
                    
                    if byte in (b"\n", b"\r"):
                        if b"[ExtractAudio]" in line_buffer:
                            sys.stdout.buffer.write(b"\nconverting to mp3.................\n")
                            sys.stdout.buffer.flush()
                        line_buffer = b""
                    else:
                        line_buffer += byte
                    
            process.wait()
            
            if process.returncode != 0:
                print(f"Error downloading link: {link}. Skipping to next...")
                
        except Exception as e:
            print(f"Error processing link {link}: {e}")

    print("\nCongratulations! your all links downloaded successfully")

if __name__ == "__main__":
    main()