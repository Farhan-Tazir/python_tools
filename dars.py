import os
import subprocess
import shutil
import sys

def check_and_install_ytdlp():
    print("Checking yt-dlp installation ........")
    
    # Check if yt-dlp is available in the system path
    if shutil.which("yt-dlp") is None:
        print("yt-dlp not found")
        print("Installing yt-dlp.................")
        try:
            # Install yt-dlp using pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            print("yt-dlp installed successfully")
        except subprocess.CalledProcessError:
            print("Error: Failed to install yt-dlp. Please ensure you have pip installed.")
            sys.exit(1)
    else:
        print("yt-dlp found")

def main():
    check_and_install_ytdlp()

    # Get paths from the user and remove any accidental quotes from drag-and-drop
    links_file_path = input("Paste the path of your links file: ").strip().strip("\"'") 
    output_dir = input("Paste the path of out (where you want to download all of the things): ").strip().strip("\"'")

    # Validate the text file
    if not os.path.isfile(links_file_path):
        print(f"Error: The file '{links_file_path}' does not exist.")
        sys.exit(1)

    # Create the main output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the links from the text file
    with open(links_file_path, 'r') as file:
        # Read lines and ignore any empty lines
        links = [line.strip() for line in file if line.strip()]

    # Loop through each link with a counter starting at 1
    for n, link in enumerate(links, start=1):
        # Create the numbered folder path
        folder_path = os.path.join(output_dir, str(n))
        
        # mkdir n
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        print(f"\n--- Extracting audio (MP3) for link {n} into folder '{n}' ---")
        
        # Run yt-dlp with audio extraction flags
        # -x extracts audio, --audio-format mp3 converts it, -P sets output path
        command = ["yt-dlp", "-x", "--audio-format", "mp3", "-P", folder_path, link]
        
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            print(f"Error downloading link: {link}. Skipping to next...")

    print("\nCongratulations! your all links downloaded successfully")

if __name__ == "__main__":
    main()