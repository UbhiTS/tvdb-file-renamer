import requests
import json
import os
from bs4 import BeautifulSoup
from os import listdir, path

__author__ = 'Tarunpreet Ubhi'
__copyright__ = 'Copyright 2020, Tarunpreet Ubhi'
__credits__ = ['Tarunpreet Ubhi']
__license__ = 'MIT'
__version__ = '0.1.0'
__maintainer__ = 'Tarunpreet Ubhi'
__email__ = 'ubhits@outlook.com'
__status__ = 'Prototype'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def scrape_site(url):
    ep_dict = {}
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.findAll("h4", {"class": "list-group-item-heading"})

    for result in results:
        href = result.a['href'].lower()
        if href.startswith('https://') and ("/official/" in href or  "/specials/" in href):
            print(f'{bcolors.HEADER}{href}{bcolors.ENDC}')

            season_page = requests.get(result.a['href'])
            season_soup = BeautifulSoup(season_page.content, 'html.parser')
            season_results = season_soup.findAll("table", {"class": "table table-condensed table-bordered"})
            
            for season in season_results:
                #print(f'{season}')
                episodes_table = season.find('tbody')
                for episode in episodes_table.findAll('tr'):
                    for td in episode.findAll('td'):
                        ep_num = td.text.strip()
                        ep_title = td.find_next_sibling("td").text.strip()
                        ep_dict[ep_title] = ep_num
                        #print(f'{ep_num} {ep_title}')
                        break
    return ep_dict


def write_database(ep_dict, db_path):
    episodes = json.dumps(ep_dict)
    f = open(db_path,"w")
    f.write(episodes)
    f.close()


def print_missing_episodes(ep_dict, ep_dict_backup, test_run):
    for ep_title in ep_dict.keys():

        test = f"TEST " if test_run else f""
        missing = test + f"{bcolors.FAIL}MISSING:"
        found = test + f"{bcolors.OKGREEN + bcolors.BOLD} FOUND :"

        if ep_dict[ep_title] is not None:
            print(f'{missing} {ep_dict_backup[ep_title]} - {ep_title}{bcolors.ENDC}')
        else:
            print(f'{found} {ep_dict_backup[ep_title]} - {ep_title}{bcolors.ENDC}')


def rename_files(ep_dict, files_path, test_run):
    for file in sorted(listdir(files_path)):
        for ep_title in sorted(ep_dict.keys()):
            if ' '.join(ep_title.split()).lower() in ' '.join(file.split()).lower():
                _, file_extension = path.splitext(f'{files_path}/{file}')

                old_filename = f'{files_path}/{file}'
                new_filename = f'{files_path}/{ep_dict[ep_title]} - {ep_title}{file_extension}'

                if (old_filename == new_filename):
                    ep_dict[ep_title] = None
                    continue
                else:
                    if ep_dict[ep_title] is not None:
                        ep_dict[ep_title] = None
                        if not test_run:
                            try:
                                os.rename(old_filename, new_filename)
                            except:
                                print(f' ERROR : {old_filename} > {new_filename}')


def main():

    URL = 'https://thetvdb.com/series/darkwing-duck'
    files_path = '/Users/ubhits/Desktop/DD'
    test_run = False

    db_cache_path = URL[URL.rindex("/") + 1:] + ".json"

    ep_dict = {}

    if path.exists(db_cache_path):
        ep_dict = json.load(open(db_cache_path))
    else:
        ep_dict = scrape_site(URL)
        write_database(ep_dict, db_cache_path)
    
    ep_dict_backup = ep_dict.copy()

    rename_files(ep_dict, files_path, test_run)

    print_missing_episodes(ep_dict, ep_dict_backup, test_run)
    

if __name__ == "__main__":
    main()





