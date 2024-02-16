import requests
import inquirer
from bs4 import BeautifulSoup
from utils import clear_screen, print_header
from library import write_library, read_library

BASE_URL = "https://kissasian.lu/"
session = requests.Session()

def get_soup(url, headers=None):
    session = requests.Session()
    response = session.get(url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser'), response

def search_kissasian(query, BASE_URL):
    BASE_URL = "https://kissasian.lu/"
    url = BASE_URL + "Search/SearchSuggest"
    params = {'type': 'drama', 'keyword': query}
    session = requests.Session()
    response = session.post(url, data=params)
    soup = BeautifulSoup(response.content, 'html.parser')
    search_results = []

    for a_tag in soup.find_all("a"):
        detail_url = BASE_URL + a_tag.get("href").lstrip('/')
        result = {"title": a_tag.text, "url": detail_url}
        search_results.append(result)

    return search_results
        
def get_series_details(url):
    BASE_URL = "https://kissasian.lu/"
    soup, response = get_soup(url)

    if response.status_code == 200:
        # Get the series summary
        summary_tag = soup.find_all('p')[6]  # Use the correct index for the summary
        summary = summary_tag.get_text(strip=True) if summary_tag else "Summary not found"

        # Get Date Aired
        date_aired_tag = soup.find_all('p')[2]  # Adjust index according to actual position
        date_aired = date_aired_tag.get_text(strip=True) if date_aired_tag else "Date aired not found"

        # Get the cast list
        cast_list = [actor_info.text.strip() for actor_info in soup.findAll("div", class_="actor-info")]

        # Get the list of episodes
        eps_list = []
        content_list = soup.find("ul", class_="list")
        if content_list:
            eps_list = [BASE_URL + ele.get('href').lstrip('/') for ele in content_list.findAll('a')]

        return summary, date_aired, cast_list, len(eps_list), eps_list
    else:
        print("Failed to retrieve series details")
        return "", [], 0, []

def series_detail_menu(series):
    from player import episode_menu
    while True:
        clear_screen()
        print_header()
        summary, date_aired, cast, no_eps, eps_list = get_series_details(series['url'])

        print(f"Title: {series['title']}\n\n{date_aired}\n\nSummary: {summary}\n\nCast: {', '.join(cast)}\n\nNumber of Episodes: {no_eps}\n")

        library = read_library()
        in_library = any(item['url'] == series['url'] for item in library)

        choices = ['Go Back to Search Results']
        if not in_library:
            choices.insert(0, 'Add to Library')
        choices.append('List Episodes')

        questions = [inquirer.List('action', message="Select an action", choices=choices)]
        answer = inquirer.prompt(questions)['action']

        if answer == 'Add to Library':
            library.append(series)
            write_library(library)  # Ensure write_library is properly implemented
            print("Series added to library.")
            input("Press Enter to continue...")
        elif answer == 'List Episodes':
            series_id = series['url'].split('/')[-1]
            # Now passing BASE_URL and session to episode_menu
            episode_menu(eps_list, series_id, BASE_URL, session)
        elif answer == 'Go Back to Search Results':
            return 'GoBackToResults'
        
def display_search_results(results):
    clear_screen()
    print_header()
    
    if not results:
        print("No results found.")
        input("Press Enter to start a new search...")
        return 'NewSearch'
    
    choices = [series['title'] for series in results] + ['Start New Search', 'Go Back to Main Menu']
    questions = [inquirer.List('series', message="Select a series:", choices=choices)]
    series_selection = inquirer.prompt(questions)['series']
    
    if series_selection == 'Start New Search':
        return 'NewSearch'
    elif series_selection == 'Go Back to Main Menu':
        return None
    else:
        return next(item for item in results if item['title'] == series_selection)


