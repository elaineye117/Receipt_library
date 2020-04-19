import requests
from bs4 import BeautifulSoup
import time
import json

BASE_URL = 'http://www.recipepuppy.com/about/api/'
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}


ingredient = input('What do you have in your refrigerator(use common between each ingredients e.g. onions,garlic): ')

params = {
    'i': ingredient
}

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

## Load the cache, save in global variable
CACHE_DICT = load_cache()

## Make the soup for the recipe page
url_text = make_url_request_using_cache(BASE_URL, CACHE_DICT)
soup = BeautifulSoup(url_text, 'html.parser')
print(soup)