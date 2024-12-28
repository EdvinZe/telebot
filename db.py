import sqlite3
import pandas as pd
import asyncio


def db_connect():
    return sqlite3.connect("maxima_akcijos.db")


def create_table():
    with db_connect() as con:
        cur = con.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS product_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_type TEXT,
            product TEXT,
            discount TEXT,
            price_with_discount TEXT,
            price_no_discount TEXT,
            discount_to TEXT
            )
        """)

        conn.commit()


def update_data(data):
    df = pd.DataFrame(data, columns=["product_type", "product", "discount", "price_with_discount", "price_no_discount",
                                     "discount_to"])

    with db_connect() as con:
        df.to_sql("product_info", con, if_exists="replace", index=False)
        con.commit()


def fetch_all():
    with db_connect() as con:
        return pd.read_sql("SELECT * FROM product_info", con)


def fetch_by_type(product_type):
    with db_connect() as con:
        query = "SELECT * FROM product_info WHERE product_type = ?"
        df = pd.read_sql(query, con, params=(product_type,))
    return df
