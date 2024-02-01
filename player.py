import re
import inquirer
import subprocess
import json
import requests
from utils import *
from kissasian import get_soup
from bs4 import BeautifulSoup
from history import *
from urllib.parse import urljoin

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

def episode_menu(eps_list, series_id):
    BASE_URL = "https://kissasian.lu/"
    while True:
        clear_screen()
        print_header()
        choices = [f'Episode {i+1}' for i in range(len(eps_list))] + ['Go Back']
        questions = [inquirer.List('episode', message="Select an episode", choices=choices)]
        selected = inquirer.prompt(questions)['episode']
        
        if selected == 'Go Back':
            break

        # Retrieve the selected episode index
        episode_index = choices.index(selected)
        
        # The episode number is one more than the index
        episode_number = episode_index + 1

        # Call play_episode with series_id and episode_number
        play_episode(series_id, episode_number)

def get_stream_url(series_id, ep_no, BASE_URL):
    episode_url = BASE_URL + f"Drama/{series_id}/Episode-{ep_no}"
    response = session.get(episode_url)  # Use the session to make the request
    soup = BeautifulSoup(response.content, 'html.parser')

    if response.status_code == 200:
        iframes = soup.find_all("iframe")
        for iframe in iframes:
            try:
                iframe_src = iframe.attrs.get('src')
                if iframe_src:
                    # Make sure the iframe URL is absolute before making the request
                    iframe_url = urljoin(episode_url, iframe_src)
                    vid_res = session.get(iframe_url)  # Use the session to make the request
                    if vid_res.status_code == 200:
                        pattern = re.compile(r'file:"(https?://[^"]+)"')
                        match = re.search(pattern, vid_res.text)
                        if match:
                            # Found the stream URL, return and exit the loop
                            return match.group(1)
                    else:
                        print(f"Failed to access iframe URL {iframe_url}: Status code {vid_res.status_code}")
            except AttributeError as e:
                print(f"Attribute error when processing iframe: {e}")
    else:
        print(f"Failed to access {episode_url}: Status code {response.status_code}")

    # If the code reaches this point, it means no valid stream URL was found in any iframe
    print("Stream URL not found in any iframe response")
    return None

   

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

def play_episode(series_id, ep_no):
    stream_url = get_stream_url(series_id, ep_no, BASE_URL)
    if stream_url:
        print(f"Playing {series_id} Episode {ep_no}... URL: {stream_url}")
        headers = {
            "Referer": "https://vidmoly.to/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Add other necessary headers here if needed
        }
        try:
            # Use the stream URL to play the video directly
            command = ['mpv', '--no-ytdl', '--http-header-fields=' + ','.join(f'{k}: {v}' for k, v in headers.items()), stream_url]
            subprocess.run(command, check=True)
            update_watch_history(series_id, ep_no)
        except subprocess.CalledProcessError as e:
            print(f"MPV failed with exit code {e.returncode}")
            print(e.stderr)
    else:
        print("Stream URL not found or error occurred.")
    session.close()

