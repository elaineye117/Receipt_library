# The precipepuppy api does not request key, so there is no need to create secrets.py file.

import sqlite3

conn = sqlite3.connect("foodreceipt.sqlite")
cur = conn.cursor()

drop_ing = '''
    DROP TABLE IF EXISTS "Ingredients";
'''

create_ing = '''
    CREATE TABLE "Ingredients" (
        "Id"  INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "name"  TEXT NOT NULL
    );
'''

drop_recipe = '''
    DROP TABLE IF EXISTS 'Recipe';
'''

create_recipe = '''
    CREATE TABLE 'Recipe' (
    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'Recipe_Name' TEXT NOT NULL
    ); 
'''
drop_rec_ing = '''
    DROP TABLE IF EXISTS 'Rec_Ing'
'''

create_rec_ing = '''
    CREATE TABLE 'Rec_Ing' (
    'Rec_Id' INTEGER,
    'Ing_ID' INTEGER
    ); 
'''
cur.execute(drop_ing)
cur.execute(create_ing) 
cur.execute(drop_recipe)
cur.execute(create_recipe)
cur.execute(drop_rec_ing)
cur.execute(create_rec_ing)

conn.commit()

##############################
## INSERT multiple ingredients
##############################
ingredients = [
    ["Egg"],
    ["potato"],
    ["onion"],
    ["garlic"]
]

insert_ingredients = '''
    INSERT INTO Ingredients
    VALUES (Null, ?)
'''

for ingre in ingredients:
    print("inserting", ingre)
    cur.execute(insert_ingredients, ingre)

conn.commit()
