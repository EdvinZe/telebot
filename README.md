# Maxima Discounts Bot

This repository contains a bot for finding and displaying current discounts at Maxima stores in Lithuania. It consists of three main parts:

- **Parser**: Scrapes discount data from the Maxima website.
- **Database**: Stores parsed data in a SQLite database.
- **Bot**: Provides users with an interface to browse discounts using Telegram.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Code Explanation](#code-explanation)
  - [Parser](#parser)
  - [Database](#database)
  - [Bot](#bot)
- [Future Plans](#future-plans)

---

## Overview

The bot periodically scrapes the Maxima website to fetch the latest discounts. The data is stored in a SQLite database and presented to the user via a Telegram bot. Users can select categories and view relevant discount details.

---

## Features

- Scrapes discount data from the Maxima website.
- Stores data in a structured SQLite database.
- Interactive Telegram bot for easy access to discounts.

---

## Technologies Used

- **Python**
- **Requests** for web scraping.
- **BeautifulSoup** for parsing HTML.
- **SQLite** for database storage.
- **Aiogram** for Telegram bot development.

---

## Code Explanation

### Parser

The parser scrapes the Maxima website for discounts and updates the database with the latest data.

```python
import time
import requests
from bs4 import BeautifulSoup
import lxml
from db import update_data

def parser():
    url = "https://www.maxima.lt/pasiulymai"

    data = []

    headers = {"Accept": "*/*",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}

    req = requests.get(url, headers=headers)
    src = req.text

    soup = BeautifulSoup(src, "lxml")

    containers = soup.find_all("section", class_="container-xl container-fluid my-5 my-lg-6")
    for _ in containers:
        cards = _.find_all("div", class_="card card-small is-pointer h-100")
        prod_type = _.find("h2", class_="mb-3 mb-lg-4").text
        for item in cards:
            product = item.find("h4", class_="mt-4 text-truncate text-truncate--2").text.strip()
            date_to = item.find("p", class_="text-small offer-dateTo-wrapper d-inline-block").find("span").text.strip()
            try:
                discount = item.find("div", class_="discount")
                if discount != None:
                    discount = f"{discount.text.strip()}%"
                else:
                    discount = "With Ačiū card"
            except AttributeError:
                discount = "-"

            price_discount = "-"
            price_nodisc = "-"

            data.append({
                "product_type": prod_type,
                "product": product,
                "discount": discount,
                "price_with_discount": price_discount,
                "price_no_discount": price_nodisc,
                "discount_to": date_to
            })

    update_data(data)
```

### Database

This module manages the database, including creating tables, updating data, and fetching records.

#### Creating the Database Table

```python
import sqlite3

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

        con.commit()
```

#### Updating Data

```python
import pandas as pd

def update_data(data):
    df = pd.DataFrame(data, columns=["product_type", "product", "discount", "price_with_discount", "price_no_discount", "discount_to"])

    with db_connect() as con:
        df.to_sql("product_info", con, if_exists="replace", index=False)
        con.commit()
```

#### Fetching Data

```python
# Fetch all records

def fetch_all():
    with db_connect() as con:
        return pd.read_sql("SELECT * FROM product_info", con)

# Fetch by product type

def fetch_by_type(product_type):
    with db_connect() as con:
        query = "SELECT * FROM product_info WHERE product_type = ?"
        df = pd.read_sql(query, con, params=(product_type,))
    return df
```

### Bot

The bot interacts with users via Telegram. Users can choose product categories to view available discounts.

#### Generating the Keyboard

```python
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup

def generate_keyboard():
    buttons = [[KeyboardButton(text=product_type)] for product_type in product_types]

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Choose the category"
    )
    return keyboard
```

#### Handling Commands and User Input

```python
from aiogram.filters import Command

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.reply("Hey... \n I'm here, to help you save money. \n I will find you discounts at Maxima shop in Lithuania",
                        reply_markup=generate_keyboard())

@dp.message()
async def process_product_type(message: types.Message):
    product_type = message.text

    if product_type not in product_types:
        await message.reply("Please select a valid category from the list.")
        return

    products = fetch_by_type(product_type)

    if products.empty:
        await message.reply(f"No discounts available for {product_type}.")
        return

    response = f"Here are some discounts for {product_type}:\n\n"
    for _, row in products.iterrows():
        response += (
            f'🛒 {row["product"]}\n'
            f'💵 {row["price_no_discount"]}\n'
            f'({row["discount"]})\n'
            f'💵 {row["price_with_discount"]}\n'
            f'⏳ {row["discount_to"]}\n\n'
        )

    if len(response) > 4000:
        for chunk in [response[i:i + 4000] for i in range(0, len(response), 4000)]:
            await message.reply(chunk)
    else:
        await message.reply(response)
```

---

## Future Plans

- Add support for multiple stores.
- Implement a more sophisticated data storage system.
- Enable user notifications for specific products or categories.

---

Feel free to contribute or report any issues!
