import subprocess
import os
import inquirer
import shutil
import logging
import threading
from history import update_watch_history
from utils import *

pending_downloads = {}  # Global dictionary to keep track of pending downloads
# Global flag to signal termination
should_terminate = False
DOWNLOADS_DIR = 'data/downloads/'
logging.basicConfig(level=logging.INFO, filename='data/app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

def ensure_downloads_dir_exists():
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def downloads_menu():
    while True:
        clear_screen()
        print_header()
        downloads = get_downloads()  # Retrieves all files, including those still downloading

        if pending_downloads:
            print("Pending Downloads:")
            for title, progress in pending_downloads.items():
                print(f"{title}: {progress}%")
            print("\n")

        # Filter out pending downloads from the downloads list
        completed_downloads = [d for d in downloads if d not in pending_downloads]

        if not completed_downloads and not pending_downloads:
            print("Your downloads folder is empty.")
            input("Press Enter to go back...")
            break

        choices = completed_downloads + ['Go Back to Main Menu']
        questions = [inquirer.List('download', message="Select an episode", choices=choices)]
        download_selection = inquirer.prompt(questions)['download']

        if download_selection == 'Go Back to Main Menu':
            break

        if download_selection in pending_downloads:
            print(f"{download_selection} is still downloading.")
            input("Press Enter to go back...")
            continue

        # For completed downloads, handle as before
        file_path = os.path.join(DOWNLOADS_DIR, download_selection)
        action_choices = ['Play', 'Delete', 'Go Back']
        action_questions = [inquirer.List('action', message="What would you like to do with the selected download?", choices=action_choices)]
        action_selected = inquirer.prompt(action_questions)['action']

        if action_selected == 'Play':
            play_downloaded_episode(file_path)
        elif action_selected == 'Delete':
            confirm_delete = inquirer.confirm(message="Are you sure you want to delete this download?", default=False)
            if confirm_delete:
                try:
                    os.remove(file_path)
                    print(f"{download_selection} has been deleted.")
                    input("Press Enter to continue...")
                except OSError as e:
                    print(f"Error deleting file: {e}")
                    
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

    # Adding to pending downloads with an initial descriptive status
    pending_downloads[filename] = "Downloading..."

    headers = f"Referer: {iframe_host}\\r\\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    cmd = ['ffmpeg', '-headers', headers, '-i', stream_url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', output_path]

    def run_download():
        try:
            with open(os.devnull, 'w') as devnull:
                subprocess.run(cmd, stderr=devnull, stdout=devnull)

            # Assuming download successful if no exception was raised
            print(f"\nDownload of {filename} completed.\n")
        finally:
            # Remove from pending downloads whether successful or not
            if filename in pending_downloads:
                del pending_downloads[filename]

    print(f"Now downloading Episode {episode_number} in the background...\n")
    print("Do not close application until download is finished.")

    # Start the download in a background thread
    threading.Thread(target=run_download, daemon=True).start()
