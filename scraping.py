import requests
from bs4 import BeautifulSoup
import time
import json

baseurl = 'http://www.recipepuppy.com/'
CACHE_FILENAME = "cache.json"
CACHE_DICT = {}


class Recipe:

    def __init__(self, name, url, website):
        self.name = name
        self.url = url
        self.website = website


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILENAME, 'w')
    contents_to_write = json.dumps(cache_dict)
    cache_file.write(contents_to_write)
    cache_file.close()

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and
    repeatably identify an API request by its baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs

    Returns
    -------
    string
        the unique key as a string
    '''

    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key

def make_url_request_using_cache(baseurl, params, CACHE_DICT):
    requests_key = construct_unique_key(baseurl,params)
    if requests_key in CACHE_DICT.keys():
        print('Using Cache')
        return CACHE_DICT[requests_key]
    else:
        print('Fetching')
        CACHE_DICT[requests_key] = requests.get(baseurl, params=params).text.replace('\n','')
        save_cache(CACHE_DICT)
        return CACHE_DICT[requests_key]

def get_recipe_instance(url_text):
    '''Make an instances from the site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a recipe page in recipepuppy.com
    
    Returns
    -------
    instance
        a national site instance
    '''
    soup = BeautifulSoup(url_text, 'html.parser')
    div_right = soup.find_all('div', class_='result')
    recipe_list = []

    for i in div_right:
        try:
            name = i.find('h3').text
        except:
            name = 'None'

        try:
            url = i.find('div', class_='url').text.split(' ')[0]
        except:
            url = 'None'

        try:
            website = i.find('a')['href']
        except:
            website = 'None'

        recipe_list.append(Recipe(name, url, website))
    # recipe_instance = Recipe(name, url, website)
    return recipe_list

if __name__ == "__main__":
    ingredient = input('What do you have in your refrigerator(use common between each ingredients e.g. onions,garlic): ')

    params = {
        'i': ingredient
    }

    CACHE_DICT = open_cache()

    test = get_recipe_instance(make_url_request_using_cache(baseurl, params, CACHE_DICT))
    print(len(test))
    print(test[0].website)
