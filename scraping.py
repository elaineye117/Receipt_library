import requests
from bs4 import BeautifulSoup
import time
import json
from flask import Flask, render_template, request
import sqlite3
import plotly.graph_objects as go

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
##   Database   ##
##################



def get_fav():
    conn = sqlite3.connect("recipe.sqlite")
    cur = conn.cursor()
    q = '''
        SELECT *
        FROM Recipe
        ORDER BY ID
    '''
    results = cur.execute(q).fetchall()
    conn.close()
    return results



def get_website():
    conn = sqlite3.connect("recipe.sqlite")
    cur = conn.cursor()
    q = '''
        select website, count(website) as count
        from Recipe
        group by website
        order by count desc
        limit 5
    '''
    results = cur.execute(q).fetchall()
    conn.close()
    return results

def get_ingredient():
    conn = sqlite3.connect("recipe.sqlite")
    cur = conn.cursor()
    q = '''
        select ingredients, count(ingredients) as count
        from Recipe
        group by ingredients
        order by count desc
    '''
    results = cur.execute(q).fetchall()
    conn.close()
    return results



##################
##     HTML     ##
##################

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
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
    
    conn = sqlite3.connect("recipe.sqlite")
    cur = conn.cursor()

    number = request.form.getlist("number")
    rec_list = []
    db_recipe = []
    for i in number:
        i_list = i.split(',')
        image = i_list[0]
        name = i_list[1]
        url = i_list[2]
        website = i_list[3]
        rec_list.append(Recipe(None, name,website,url,image))
        db_recipe.append(i_list[:5])
    
    insert_recipes = '''
    INSERT INTO Recipe
    VALUES (Null, ?, ?, ?, ?, ?)
    '''
    for rec in db_recipe:
        print("inserting", rec)
        cur.execute(insert_recipes, rec)

    conn.commit()

    return render_template('favorite.html', 
        test = rec_list,
        number=number
        )

@app.route('/my_favorite', methods=['POST'])
def my_fav_db():


    results = get_fav()

    return render_template('my_favorite.html', 
        result = results
        )


@app.route('/plot', methods=['POST', 'GET'])
def plot():

    results = get_website()

    x_vals = []
    y_vals = []

    for row in results:
        x_vals.append(row[0])
        y_vals.append(row[1])

    bars_data = go.Bar(
        x=x_vals,
        y=y_vals
    )
    fig = go.Figure(data=bars_data)
    div = fig.to_html(full_html=False)
    return render_template("plot.html", 
    plot_div=div,
    result = results)


@app.route('/ingredients', methods=['POST', 'GET'])
def cloud():
    results = get_ingredient()

    x_vals = []
    y_vals = []

    for row in results:
        x_vals.append(row[0])
        y_vals.append(row[1])

    bars_data = go.Bar(
        x=x_vals,
        y=y_vals
    )
    fig = go.Figure(data=bars_data)
    div = fig.to_html(full_html=False)
    return render_template("ingredients.html", plot_div=div, result = results)

if __name__ == "__main__":
    # conn = sqlite3.connect("recipe.sqlite")
    # cur = conn.cursor()

    # drop_recipe = '''
    #     DROP TABLE IF EXISTS 'Recipe';
    # '''

    # create_recipe = '''
    #     CREATE TABLE 'Recipe' (
    #     'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    #     "image" TEXT,
    #     'Recipe_Name' TEXT NOT NULL,
    #     "url" TEXT,
    #     "website" TEXT
    #     ); 
    # '''

    # cur.execute(drop_recipe)
    # cur.execute(create_recipe)

    # conn.commit()

    app.run(debug=True)
