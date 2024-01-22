import inquirer
from utils import clear_screen, print_header
from history import display_watch_history, clear_watch_history, update_watch_history
from library import read_library, write_library, library_menu
from kissasian import search_kissasian, get_series_details, display_search_results, series_detail_menu
from player import play_episode

def main_menu():
    clear_screen()
    print_header()
    choices = ['Search', 'My Library', 'Watch History', 'Clear Watch History', 'Exit']
    question = inquirer.List('action', message='Choose an option', choices=choices)
    answer = inquirer.prompt([question])
    return answer['action']

def main():
    BASE_URL = "https://kissasian.lu/"

    while True:
        action = main_menu()
        if action == 'Search':
            query = input("Search For Something to Watch: ")
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
        elif action == 'Watch History':
            display_watch_history()
        elif action == 'Clear Watch History':
            clear_watch_history()
        elif action == 'My Library':
            library_menu()
        elif action == 'Exit':
            break

if __name__ == "__main__":
    main()