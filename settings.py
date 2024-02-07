import inquirer
from utils import clear_screen, print_header
from history import clear_watch_history

from utils import clear_cookies
from downloads import delete_downloads

def settings_menu():
    from main import clear_search_history
    while True:
        clear_screen()
        print_header()
        print("Settings\n")

        choices = [
            'Clear Search History', 
            'Clear Watch History', 
            'Clear Cookies',
            'Delete All Downloads', 
            'Go Back to Main Menu'
        ]
        questions = [inquirer.List('setting', message="Select an option", choices=choices)]
        setting_selection = inquirer.prompt(questions)['setting']

        if setting_selection == 'Go Back to Main Menu':
            break
        elif setting_selection == 'Clear Watch History':
            clear_watch_history()
        elif setting_selection == 'Clear Search History':
            clear_search_history() 
        elif setting_selection == 'Delete All Downloads':
            # Implement privacy settings adjustment functionality
            delete_downloads()
        elif setting_selection == 'Clear Cookies':
            clear_cookies()

        # Add additional elif blocks for other settings options as necessary
