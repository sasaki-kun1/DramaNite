import json

WATCH_HISTORY_FILE = 'data/watch_history.json'

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

def display_watch_history():
    history = read_watch_history()
    if not history:
        print("Your watch history is empty.")
    else:
        for series_id, episodes in history.items():
            print(f"Series: {series_id}, Episodes: {', '.join(map(str, episodes))}")
    input("Press Enter to continue...")

def clear_watch_history():
    write_watch_history({})
    print("Watch history cleared.")
    input("Press Enter to continue...")
