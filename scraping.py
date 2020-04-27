import requests
from bs4 import BeautifulSoup
import time
import json
from flask import Flask, render_template, request

baseurl = 'http://www.recipepuppy.com/'
CACHE_FILENAME = "cache.json"
CACHE_DICT = {}

##################
##  Scrapping   ##
##################

class Recipe:

    def __init__(self, index, name, url, website, image):
        self.name = name
        self.url = url
        self.website = website
        self.image = image
        self.index = index


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

    for index, i in enumerate(div_right, 1):
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
        try:
            image = i.find('img', class_='thumb')['src']
        except:
            image = 'None'

        recipe_list.append(Recipe(index, name, url, website, image))
    # recipe_instance = Recipe(name, url, website)
    return recipe_list


##################
##     HTML     ##
##################

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') # just the static HTML

@app.route('/handle_form', methods=['POST'])
def handle_the_form():

    ingre = request.form["ingre"]

    params = {
        'i': ingre
    }

    CACHE_DICT = open_cache()
    test = get_recipe_instance(make_url_request_using_cache(baseurl, params, CACHE_DICT))

    return render_template('results.html', 
        ingre = ingre,
        test = test
        )


@app.route('/favorite', methods=['POST'])
def get_fav_db():

    index = request.form.getlist("number")



    return render_template('favorite.html', 
        index = index,

        )


print(get_fav_db)










if __name__ == "__main__":
    app.run(debug=True)





