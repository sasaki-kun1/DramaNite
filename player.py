import re
import inquirer
import subprocess
import json
import os
import requests
import logging
from downloads import *
from utils import *
from kissasian import get_soup
from bs4 import BeautifulSoup
from history import *
from urllib.parse import urlparse, urljoin

logging.basicConfig(level=logging.INFO, filename='data/app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

# Create a persistent requests session
session = requests.Session()

BASE_URL = "https://kissasian.lu/"
WATCH_HISTORY_FILE = 'data/watch_history.json'
COOKIES_FILE = 'data/cookies.json'

# Attempt to load cookies if they exist
try:
    with open(COOKIES_FILE, 'r') as f:
        cookies = requests.utils.cookiejar_from_dict(json.load(f))
        session.cookies = cookies
except FileNotFoundError:
    print("No cookies file found. A new one will be created after the first request.")

def episode_menu(eps_list, series_id, BASE_URL, session):
    while True:
        clear_screen()
        print_header()
        choices = [f"Episode {i + 1}" for i in range(len(eps_list))] + ['Go Back']
        questions = [inquirer.List('episode', message="Select an episode", choices=choices)]
        selected = inquirer.prompt(questions)['episode']
        
        if selected == 'Go Back':
            break

        episode_number = int(selected.split(' ')[1])
        
        # Check if the episode is already downloaded
        if is_episode_downloaded(series_id, episode_number):
            # If downloaded, only show options to Play or Go Back
            action_choices = ['Play', 'Go Back']
        else:
            # If not downloaded, offer options to Stream, Download, or Go Back
            action_choices = ['Stream', 'Download', 'Go Back']

        action_questions = [inquirer.List('action', message="What would you like to do?", choices=action_choices)]
        action_selected = inquirer.prompt(action_questions)['action']

        if action_selected == 'Play':
            file_path = os.path.join(DOWNLOADS_DIR, f"{series_id} - Episode {episode_number}.mp4")
            play_downloaded_episode(file_path)
            update_watch_history(series_id, episode_number)  # Make sure this function exists and is imported
        elif action_selected == 'Stream':
            play_episode(series_id, episode_number, BASE_URL, session)
        elif action_selected == 'Download':
            # No need to check if it's downloaded again, since the option won't appear if it's already downloaded
            stream_url, iframe_host = get_stream_url(series_id, episode_number, BASE_URL, session)
            if stream_url:
                download_episode(stream_url, series_id, episode_number, iframe_host)  # Ensure this function is correctly implemented
            else:
                print("Unable to retrieve stream URL for download.")
        elif action_selected == 'Go Back':
            continue

def get_stream_url(series_id, ep_no, BASE_URL, session):
    episode_url = BASE_URL + f"Drama/{series_id}/Episode-{ep_no}"
    response = session.get(episode_url)  # Use the session to make the request
    soup = BeautifulSoup(response.content, 'html.parser')
    
    if response.status_code == 200:
        iframes = soup.find_all("iframe")
        for iframe in iframes:
            try:
                iframe_src = iframe.attrs.get('src')
                if iframe_src:
                    # Ensure the iframe URL is absolute before making the request
                    iframe_url = urljoin(BASE_URL, iframe_src)
                    iframe_host = urlparse(iframe_url).netloc
                    vid_res = session.get(iframe_url)  # Use the session to make the request
                    if vid_res.status_code == 200:
                        pattern = re.compile(r'file:"(https?://[^"]+)"')
                        match = re.search(pattern, vid_res.text)
                        if match:
                            # Found the stream URL, return it and the iframe host
                            return match.group(1), iframe_host
                    else:
                        logging.error(f"Failed to access iframe URL {iframe_url}: Status code {vid_res.status_code}")
            except AttributeError as e:
                logging.exception(f"Attribute error when processing iframe: {e}")
    else:
        logging.error(f"Failed to access {episode_url}: Status code {response.status_code}")

    logging.error("Stream URL not found in any iframe response")
    return None, None


def read_watch_history():
    try:
        with open(WATCH_HISTORY_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def write_watch_history(history):
    with open(WATCH_HISTORY_FILE, 'w') as file:
        json.dump(history, file, indent=4)

def update_watch_history(series_id, ep_no):
    history = read_watch_history()
    if series_id not in history:
        history[series_id] = []
    if ep_no not in history[series_id]:
        history[series_id].append(ep_no)
    write_watch_history(history)

def play_episode(series_id, ep_no, BASE_URL, session):
    stream_url, iframe_host = get_stream_url(series_id, ep_no, BASE_URL, session)
    if stream_url:
        print(f"Playing {series_id} Episode {ep_no}... URL: {stream_url}")
        
        # Set headers with dynamic Referer based on the iframe host URL.
        headers = [
            f"Referer: {iframe_host}",
            f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Include additional headers as needed
        ]
        
        # The headers must be passed as a list of strings, each string being a header line.
        command = ['mpv', '--no-ytdl', '--http-header-fields=' + '\\n'.join(headers), stream_url]
        
        try:
            # Use Popen to open mpv without waiting for it to close.
            process = subprocess.Popen(command)
            # You can wait for the process to complete if needed, or handle it asynchronously.
            process.wait()
            # Assuming update_watch_history is a valid function to call
            update_watch_history(series_id, ep_no)
        except subprocess.CalledProcessError as e:
            print(f"MPV failed with exit code {e.returncode}")
            print(e.stderr.decode() if e.stderr else "No error message")
    else:
        print("Stream URL not found or error occurred.")

