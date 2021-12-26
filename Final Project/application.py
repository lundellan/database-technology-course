from bottle import get, post, run, request, response
from urllib.parse import quote, unquote
import datetime
import sqlite3

db = sqlite3.connect("krusty.sqlite")
c = db.cursor()

@post('/reset')
def reset():
    c.executescript(
        """
        DELETE FROM ingredients;
        DELETE FROM recipes;
        DELETE FROM cookies;
        DELETE FROM pallets;
        DELETE FROM orders;
        DELETE FROM orderedPallets;
        DELETE FROM customers;
        DELETE FROM transports;
        """,
    )
    db.commit()

    response.status = 205
    return {"location": "/"}

@post('/customers')
def post_customers():
    customer = request.json
    c.execute(
        """
        INSERT
        INTO customers(name, address)
        VALUES (?, ?)
        """,
        [customer['name'], customer['address']]
    )
    db.commit()

    response.status = 201
    return {"location": "/customers/" + quote(customer['name'])}

@get('/customers')
def get_customers():   
    c.execute(
        """
        SELECT  name, address
        FROM    customers
        """,
    )
    db.commit()
    
    found = [{"name": name, "address": address} for name, address in c]
    return {"data" : found}

@post('/ingredients')
def post_ingredients():
    ingredient = request.json

    c.execute(
        """
        INSERT
        INTO ingredients(ingredient, unit, quantity)
        VALUES (?, ?, 0)
        """,
        [ingredient['ingredient'], ingredient['unit']]
    )
    db.commit()

    response.status = 201
    return {"location": "/ingredients/" + quote(ingredient['ingredient'])}

@post('/ingredients/<ingredient>/deliveries')
def post_deliveries(ingredient):
    delivery = request.json

    unquoted_ingredient = unquote(ingredient)

    c.execute(
        """
        UPDATE  ingredients
        SET     deliveryTime = ?, quantity = quantity + ?, last_delivery_quantity = ?
        WHERE   ingredient = ?
        """,
        [delivery['deliveryTime'], delivery['quantity'], delivery['quantity'], unquoted_ingredient]
    )
    db.commit()

    c.execute(
        """
        SELECT  ingredient, quantity, unit
        FROM    ingredients
        WHERE   ingredient = ?
        """,
        [unquoted_ingredient]
    )
    db.commit()

    response.status = 201
    found = [{"ingredient": ingredient, "quantity": quantity, "unit": unit} for ingredient, quantity, unit in c]
    return {"data" : found}

@get('/ingredients')
def get_ingredients():

    c.execute(
        """
        SELECT  ingredient, quantity, unit
        FROM    ingredients
        """
    )
    db.commit()

    response.status = 200
    found = [{"ingredient": ingredient, "quantity": quantity, "unit": unit} for ingredient, quantity, unit in c]
    return {"data" : found}

@post('/cookies')
def post_cookies():
    cookie = request.json

    c.execute(
        """
        INSERT
        INTO cookies(name)
        VALUES (?)
        """,
        [cookie['name']]
    )
    db.commit()

    for x in cookie['recipe']:
        c.execute(
            """
            INSERT
            INTO recipes(name, ingredient, amount)
            VALUES (?, ?, ?)
            """,
            [cookie['name'], x['ingredient'], x['amount']]
        )
    db.commit()

    response.status = 201
    return {"location": "/cookies/" + quote(cookie['name'])}

@get('/cookies')
def get_cookies():

    c.execute(
        """
        SELECT      name, count() as number_of_pallets
        FROM        cookies
        LEFT JOIN   pallets
        USING       (name)
        WHERE       is_blocked = 0 OR is_blocked IS NULL
        GROUP BY    name
        """
    )
    db.commit()

    response.status = 200
    found = [{"name": name, "pallets": number_of_pallets} for name, number_of_pallets in c]
    return {"data" : found}

@get('/cookies/<cookie_name>/recipe')
def get_cookies_recipe(cookie_name):

    unquoted_cookie = unquote(cookie_name)

    c.execute(
        """
        SELECT          recipes.ingredient, amount, unit
        FROM            recipes
        LEFT JOIN       ingredients
        ON              recipes.ingredient = ingredients.ingredient
        WHERE           name = ?      
        """,
        [unquoted_cookie]
    )
    db.commit()

    found = [{"ingredient": ingredient, "amount" : amount, "unit" : unit} for ingredient, amount, unit in c]

    if found:
        response.status = 200
    else:
        response.status = 404
    
    return {"data" : found}


@post('/pallets')
def post_pallets():
    pallet = request.json

    try:
        c.execute(
            """
            INSERT
            INTO    pallets(name, manufacture_time, is_blocked)
            VALUES  (?, ?, 0)
            """, 
            [pallet['cookie'], datetime.datetime.now().strftime("%Y-%m-%d")]
        )
        db.commit()
    except Exception as e:
        if str(e) == "Not enough ingredients":
            response.status = 422
            return {"location": " "}

    c.execute(
        """
        SELECT  pallet_ID
        FROM    pallets
        WHERE   rowid = last_insert_rowid()
        """,
    )
    db.commit()
    id = c.fetchone()[0]

    response.status = 201
    return {"location": "/pallets/" + id}

@get('/pallets')
def get_pallets():
    query = """
        SELECT   pallet_ID, name, manufacture_time, is_blocked
        FROM    pallets
        WHERE 1 = 1
        """
    params = []
    if request.query.cookie:
        query += " AND name = ?"
        params.append(request.query.cookie)

    if request.query.before:
        query += " AND manufacture_time < ?"
        params.append(request.query.before)

    if request.query.after:
        query += " AND manufacture_time > ?"
        params.append(request.query.after)
    c.execute(
        query,
        params
    )

    response.status = 200
    found = [{"id": pallet_ID, "cookie": name, "productionDate": manufacture_time, "blocked": is_blocked} for pallet_ID, name, manufacture_time, is_blocked in c]
    return {"data" : found}


@post('/cookies/<cookie_name>/block/')
def block_cookies(cookie_name):
    
    unquoted_cookie = unquote(cookie_name)

    query = """
        UPDATE  pallets
        SET     is_blocked = 1
        WHERE   name = ?
        """
    params = [unquoted_cookie, ]
    if request.query.before:
        query += " AND manufacture_time < ?"
        params.append(request.query.before)

    if request.query.after:
        query += " AND manufacture_time > ?"
        params.append(request.query.after)
    c.execute(
        query,
        params
    )

    response.status = 205
    return " "


@post('/cookies/<cookie_name>/unblock/')
def unblock_cookies(cookie_name):
    
    unquoted_cookie = unquote(cookie_name)

    query = """
        UPDATE  pallets
        SET     is_blocked = 0
        WHERE   name = ?
        """
    params = [unquoted_cookie, ]
    if request.query.before:
        query += " AND manufacture_time < ?"
        params.append(request.query.before)

    if request.query.after:
        query += " AND manufacture_time > ?"
        params.append(request.query.after)
    c.execute(
        query,
        params
    )

    response.status = 205
    return " "


run(host='localhost', port=8888)
