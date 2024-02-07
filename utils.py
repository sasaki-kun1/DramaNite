import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    YELLOW = '\033[93m'
    END = '\033[0m'
    print(YELLOW + """
______                             _     _ _           
|  _  \\                           | \\ | (_) |      
| | | |_ __ __ _ _ __ ___   __ _  |  \\| |_| |_ ___ 
| | | | '__/ _` | '_ ` _ \\ / _` | | . ` | | __/ _ \\
| |/ /| | | (_| | | | | | | (_| | | |\\  | | ||  __/
|___/ |_|  \\__,_|_| |_| |_|\\__,_| \\_| \\_/_|\\__\\___|
                                                   
    """ + END)
    print("Welcome Back to Drama Nite!\n")

def clear_cookies():
    COOKIES_FILE_PATH = 'data/cookies.json'
    try:
        # Check if the cookies file exists
        if os.path.exists(COOKIES_FILE_PATH):
            # Delete the file
            os.remove(COOKIES_FILE_PATH)
            print("Cookies have been cleared.")
        else:
            print("Cookies file does not exist.")
    except Exception as e:
        print(f"An error occurred while trying to clear cookies: {e}")