import json
import os
import inquirer
from downloads import downloads_menu
from settings import settings_menu
from utils import clear_screen, print_header
from history import display_watch_history
from library import library_menu
from kissasian import search_kissasian, display_search_results, series_detail_menu

PREVIOUS_SEARCHES_FILE = 'data/prev_search.json'

def load_previous_searches():
    clear_screen()
    print_header()
    try:
        with open(PREVIOUS_SEARCHES_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    except FileNotFoundError:
        return []

def save_previous_search(query):
    searches = load_previous_searches()
    if query and query not in searches:
        searches.append(query)
        searches = searches[-5:]  # Keep only the last five searches
        with open(PREVIOUS_SEARCHES_FILE, 'w') as file:
            json.dump(searches, file)

def display_previous_searches():
    searches = load_previous_searches()
    if searches:
        print("\nYour previous searches")
        for search in searches[-5:]:
            print("- " + search)
    else:
        print("\nNo previous searches found.")
    print("\n")

def clear_search_history():
    try:
        # Open the file in write mode to clear its contents
        with open(PREVIOUS_SEARCHES_FILE, 'w') as file:
            file.write('[]')  # Assuming the search history is stored as a JSON list
        
        # Print the confirmation message
        print("Search history has been cleared.")
        
        # Prompt the user to press Enter to continue
        input("Press Enter to continue...")
    except Exception as e:
        # Handle potential errors, such as issues with file access
        print(f"An error occurred while clearing search history: {e}")
        input("Press Enter to continue...")

def main_menu():
    clear_screen()
    print_header()
    choices = ['Search', 'My Library', 'Downloads', 'Watch History', 'Settings', 'Exit']
    question = [
        inquirer.List('action', message="Choose an option", choices=choices)
    ]
    answer = inquirer.prompt(question)
    return answer['action']

def search_query():
    return inquirer.prompt([inquirer.Text('search', message="Search for something to watch")])['search']

def main():
    BASE_URL = "https://kissasian.lu/"
    os.makedirs(os.path.dirname(PREVIOUS_SEARCHES_FILE), exist_ok=True)  # Ensure the directory exists

    while True:
        action = main_menu()
        if action == 'Search':
            display_previous_searches()  # Display the last five searches
            query = search_query()  # Prompt the user for a new search
            save_previous_search(query)
            results = search_kissasian(query, BASE_URL)
            while True:
                selected_series = display_search_results(results)
                if selected_series == 'NewSearch':
                    break
                elif selected_series:
                    action = series_detail_menu(selected_series)
                    if action != 'GoBackToResults':
                        break
                else:
                    break
        elif action == 'My Library':
            library_menu()
        elif action == 'Downloads':
            downloads_menu()
        elif action == 'Watch History':
            display_watch_history()
        elif action == 'Settings':
            settings_menu()
        elif action == 'Exit':
            break

if __name__ == "__main__":
    main()
