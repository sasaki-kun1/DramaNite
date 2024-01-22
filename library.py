import json
import inquirer
from utils import clear_screen, print_header


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
    from kissasian import get_series_details  # Deferred import
    from player import episode_menu
    while True:
        clear_screen()
        print_header()
        library = read_library()

        if not library:
            print("Your library is empty.")
            input("Press Enter to go back...")
            break

        choices = [series['title'] for series in library] + ['Go Back to Main Menu']
        questions = [inquirer.List('series', message="Select a series:", choices=choices)]
        series_selection = inquirer.prompt(questions)['series']

        if series_selection == 'Go Back to Main Menu':
            break

        selected_series = next(item for item in library if item['title'] == series_selection)
        clear_screen()
        print_header()
        # Update to unpack summary as well
        summary, date_aired, cast, no_eps, eps_list = get_series_details(selected_series['url'])  # Retrieve eps_list
        print(f"Title: {selected_series['title']}\n\n{date_aired}\n\nSummary: {summary}\n\nCast: {', '.join(cast)}\n\nNumber of Episodes: {no_eps}\n")

        choices = ['Go Back to Library', 'Remove From Library', 'Episode List']  # Add Episode List option
        questions = [inquirer.List('action', message="Select an action", choices=choices)]
        answer = inquirer.prompt(questions)['action']

        if answer == 'Remove From Library':
            library = [item for item in library if item['url'] != selected_series['url']]
            write_library(library)
            print("Series removed from library.")
            input("Press Enter to continue...")
        elif answer == 'Episode List':
            series_id = selected_series['url'].split('/')[-1]  # Extract series_id
            episode_menu(eps_list, series_id)  # Call episode_menu with eps_list and series_id
        # No need for an else branch as 'Go Back to Library' will just continue the loop
