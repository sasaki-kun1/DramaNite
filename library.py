import json
import inquirer
import requests
from utils import clear_screen, print_header

BASE_URL = "https://kissasian.lu/"
LIBRARY_FILE = 'data/library.json'

def read_library():
    try:
        with open(LIBRARY_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def write_library(library):
    with open(LIBRARY_FILE, 'w') as file:
        json.dump(library, file, indent=4)

def library_menu():
    from player import episode_menu
    from kissasian import get_series_details
    session = requests.Session()
    
    while True:
        clear_screen()
        print_header()
        library = read_library()

        if not library:
            print("Your library is empty.")
            input("Press Enter to go back...")
            break

        choices = [series['title'] for series in library] + ['Go Back to Main Menu']
        questions = [inquirer.List('series', message="Select a series", choices=choices)]
        series_selection = inquirer.prompt(questions)['series']

        if series_selection == 'Go Back to Main Menu':
            break

        selected_series = next(item for item in library if item['title'] == series_selection)
        clear_screen()
        print_header()
        # Assuming get_series_details returns the expected values
        summary, date_aired, cast, no_eps, eps_list = get_series_details(selected_series['url'])
        print(f"Title: {selected_series['title']}\n\n{date_aired}\n\nSummary: {summary}\n\nCast: {', '.join(cast)}\n\nNumber of Episodes: {no_eps}\n")

        choices = ['Go Back to Library', 'Remove From Library', 'Episode List']
        questions = [inquirer.List('action', message="Select an action", choices=choices)]
        answer = inquirer.prompt(questions)['action']

        if answer == 'Remove From Library':
            library = [item for item in library if item['url'] != selected_series['url']]
            write_library(library)
            print("Series removed from library.")
            input("Press Enter to continue...")
        elif answer == 'Episode List':
            series_id = selected_series['url'].split('/')[-1]
            # Now passing BASE_URL and session as required
            episode_menu(eps_list, series_id, BASE_URL, session)
