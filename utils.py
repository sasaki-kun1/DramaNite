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
    print("Welcome Back to Drama Nite!")
