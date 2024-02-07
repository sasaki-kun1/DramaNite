import subprocess
import os
import inquirer
import shutil
import logging
import ffmpeg
from history import update_watch_history
from tqdm import tqdm
from utils import *

DOWNLOADS_DIR = 'data/downloads/'
logging.basicConfig(level=logging.INFO, filename='data/app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

def ensure_downloads_dir_exists():
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def downloads_menu():
    while True:
        clear_screen()
        print_header()
        downloads = get_downloads()

        if not downloads:
            print("Your downloads folder is empty.")
            input("Press Enter to go back...")
            break

        choices = downloads + ['Go Back to Main Menu']
        questions = [inquirer.List('download', message="Select a download to play", choices=choices)]
        download_selection = inquirer.prompt(questions)['download']

        if download_selection == 'Go Back to Main Menu':
            break

        # Assuming play_downloaded_episode is a function you implement to play the selected download
        play_downloaded_episode(os.path.join(DOWNLOADS_DIR, download_selection))

def get_downloads():
    """Retrieve a list of all downloaded episodes."""
    try:
        # Ensure the downloads directory exists
        if not os.path.exists(DOWNLOADS_DIR):
            os.makedirs(DOWNLOADS_DIR)
        # List all files in the downloads directory
        files = [f for f in os.listdir(DOWNLOADS_DIR) if os.path.isfile(os.path.join(DOWNLOADS_DIR, f))]
        return files
    except Exception as e:
        print(f"Error retrieving downloads: {e}")
        return []
    
def play_downloaded_episode(file_path):
    """
    Play the selected downloaded episode using a local media player (e.g., mpv)
    and update the watch history.
    """
    # Verify the file exists
    if not os.path.exists(file_path):
        print("The selected file does not exist:", file_path)
        return
    # Extract series_id and episode_number from the file_path for history update
    # Assuming file naming convention: "series_id - Episode episode_number.mp4"
    try:
        series_id, episode_str = os.path.basename(file_path).split(' - Episode ')
        episode_number = episode_str.split('.')[0]  # Assuming ".mp4" extension
    except ValueError:
        print("Unable to parse series ID and episode number from filename.")
        return
    # Construct and execute the command to play the video
    try:
        print(f"Playing {file_path}...")
        subprocess.run(['mpv', '--no-ytdl', file_path], check=True)
        # Update watch history after successful playback
        update_watch_history(series_id, episode_number)
    except subprocess.CalledProcessError as e:
        print(f"Failed to play the episode. Error: {e}")
    except FileNotFoundError:
        print("Media player (mpv) not found. Please ensure it's installed and accessible.")

def is_episode_downloaded(series_id, episode_number):
    """
    Check if an episode is already downloaded.
    """
    expected_filename = f"{series_id} - Episode {episode_number}.mp4"  # Adjust based on your filename format
    file_path = os.path.join(DOWNLOADS_DIR, expected_filename)
    return os.path.exists(file_path)

def delete_downloads():
    # Prompt the user for confirmation before deleting downloads
    questions = [
        inquirer.Confirm('confirm', message="Are you sure you want to delete all downloads?", default=False),
    ]
    answers = inquirer.prompt(questions)

    # Proceed with deletion if confirmed
    if answers.get('confirm', False):
        try:
            # Check if the downloads directory exists and then remove it
            if os.path.exists(DOWNLOADS_DIR) and os.path.isdir(DOWNLOADS_DIR):
                shutil.rmtree(DOWNLOADS_DIR)
                print("All downloads have been deleted.")
                
                # Recreate the downloads directory after deletion
                os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            else:
                print("No downloads directory found.")
        except Exception as e:
            print(f"Error deleting downloads: {e}")
    else:
        print("Deletion cancelled.")

def download_episode(stream_url, series_title, episode_number, iframe_host):
    ensure_downloads_dir_exists()
    filename = f"{series_title} - Episode {episode_number}.mp4"
    output_path = os.path.join(DOWNLOADS_DIR, filename)

    # Format headers correctly for ffmpeg
    headers = f"Referer: {iframe_host}\\r\\n" + \
              "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    cmd = [
        'ffmpeg',
        '-headers', f"{headers}",
        '-i', f"{stream_url}",
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        f"{output_path}"
    ]

    try:
        # Use subprocess.run for simpler error handling and output management
        subprocess.run(cmd, check=True, text=True, stderr=subprocess.PIPE)
        print(f"Download completed: {output_path}")
    except subprocess.CalledProcessError as e:
        logging.exception(f"Error downloading episode: {e.stderr}")
        print(f"Error downloading episode: {e.stderr}")