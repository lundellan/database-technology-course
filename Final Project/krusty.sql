PRAGMA foreign_keys=OFF;

DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS cookies;
DROP TABLE IF EXISTS pallets;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS orderedPallets;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS transports;

CREATE TABLE ingredients (
    ingredient              TEXT,
    unit                    TEXT,
    quantity                INT,
    deliveryTime            DATE,
    last_delivery_quantity  INT,
    PRIMARY KEY (ingredient)
);

CREATE TABLE recipes (
    amount                  TEXT,
    name                    TEXT,
    ingredient              TEXT,
    PRIMARY KEY (amount, name, ingredient),
    FOREIGN KEY (name) REFERENCES cookies(name),
    FOREIGN KEY (ingredient) REFERENCES ingredients(ingredient) 
);

CREATE TABLE cookies (
    name                    TEXT,
    PRIMARY KEY (name)
);

CREATE TABLE pallets (
    pallet_ID               TEXT DEFAULT (lower(hex(randomblob(16)))),
    location                TEXT,
    is_blocked              INT,
    manufacture_time        DATETIME,
    name                    TEXT,
    PRIMARY KEY (pallet_ID)
    FOREIGN KEY (name) REFERENCES cookies(name)
);

CREATE TABLE orders (
    order_ID                TEXT,
    delivery_date           DATE,
    transport_ID            TEXT,
    customer_ID             TEXT,
    PRIMARY KEY (order_ID)
    FOREIGN KEY (transport_ID) REFERENCES transports(transport_ID)
    FOREIGN KEY (customer_ID) REFERENCES customers(customer_ID)
);

CREATE TABLE orderedPallets (
    quantity                INT,
    cookie                  TEXT,
    order_ID                TEXT,
    PRIMARY KEY (quantity, cookie, order_ID),
    FOREIGN KEY (cookie) REFERENCES cookies(cookie),
    FOREIGN KEY (order_ID) REFERENCES orders(order_ID)
);

CREATE TABLE customers (
    customer_ID             TEXT DEFAULT (lower(hex(randomblob(16)))),
    name                    TEXT,
    address                 TEXT,
    PRIMARY KEY (customer_ID)
);

CREATE TABLE transports (
    transport_ID            TEXT DEFAULT (lower(hex(randomblob(16)))),
    PRIMARY KEY (transport_ID)
);

DROP TRIGGER IF EXISTS update_ingredients;
CREATE TRIGGER update_ingredients
AFTER INSERT ON pallets
BEGIN

    UPDATE  ingredients
    SET     quantity = quantity - (
        SELECT  amount*54
        FROM    recipes 
        WHERE   name = NEW.name AND ingredients.ingredient = ingredient
    )
    WHERE   ingredient in (
        SELECT  ingredient
        FROM    recipes
        WHERE   name = NEW.name AND ingredient = recipes.ingredient
    );

    SELECT CASE
    WHEN (
        SELECT quantity
        FROM   ingredients
        WHERE quantity < 0
    ) IS NOT NULL
    THEN
        RAISE (ROLLBACK, "Not enough ingredients")
    END;

END;

