import requests
from bs4 import BeautifulSoup
import time
import json

baseurl = 'http://www.recipepuppy.com/'
CACHE_FILENAME = "cache.json"
CACHE_DICT = {}


# def load_cache():
#     try:
#         cache_file = open(CACHE_FILE_NAME, 'r')
#         cache_file_contents = cache_file.read()
#         cache = json.loads(cache_file_contents)
#         cache_file.close()
#     except:
#         cache = {}
#     return cache


# def save_cache(cache):
#     cache_file = open(CACHE_FILE_NAME, 'w')
#     contents_to_write = json.dumps(cache)
#     cache_file.write(contents_to_write)
#     cache_file.close()

# def make_url_request_using_cache(url, params, cache):
#     if (url in cache.keys()): # the url is our unique key
#         print("Using cache")
#         return cache[url]
#     else:
#         print("Fetching")
#         time.sleep(1)
#         response = requests.get(url,params=params)
#         cache[url] = response.text
#         save_cache(cache)
#         return cache[url+params.values]

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



## Make the soup for the recipe page



if __name__ == "__main__":
    ingredient = input('What do you have in your refrigerator(use common between each ingredients e.g. onions,garlic): ')

    params = {
        'i': ingredient
    }

    CACHE_DICT = open_cache()
    url_text = make_url_request_using_cache(baseurl, params, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')
    print(soup)