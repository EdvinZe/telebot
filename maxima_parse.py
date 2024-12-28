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
                    discount = item.find("div",
                                         class_="px-1 px-sm-2 px-lg-250 py-2 text-wrap d-flex align-items-center justify-content-center text-center text-white h-100 benefit-icon").text.strip()
            except AttributeError:
                discount = "With Ačiū card"

            try:
                price_discount = item.find("div",
                                           class_="d-flex px-1 px-sm-2 px-lg-250 flex-column justify-content-center align-items-center h-100")
                if price_discount != None:
                    euro_discount = item.find("div",
                                              class_="d-flex px-1 px-sm-2 px-lg-250 flex-column justify-content-center align-items-center h-100").findChild(
                        "div", class_="my-auto price-eur text-end").text.strip()
                    cnt_discount = item.find("div",
                                             class_="d-flex px-1 px-sm-2 px-lg-250 flex-column justify-content-center align-items-center h-100").findChild(
                        "span", class_="price-cents").text.strip()
                    price_discount = f"{euro_discount},{cnt_discount} euro"
                else:
                    euro_discount = item.find("div", class_="bg-primary text-white h-100 rounded-end-1").findChild(
                        "div",
                        class_="my-auto price-eur text-end").text.strip()
                    cnt_discount = item.find("div", class_="bg-primary text-white h-100 rounded-end-1").findChild(
                        "span",
                        class_="price-cents").text.strip()
                    price_discount = f"{euro_discount},{cnt_discount} euro"
            except AttributeError:
                price_discount = "-"

            try:
                price_nodisc = item.find("div", class_="price-old text-white text-decoration-line-through text-center")
                if price_nodisc != None:
                    price_nodisc = f"{price_nodisc.text.strip()}euro"
                else:
                    eur_nodisc = item.find("div", class_="my-auto price-eur text-end").text.strip()
                    cent_nodisc = item.find("span", class_="price-cents").text.strip()
                    price_nodisc = f"{eur_nodisc},{cent_nodisc} euro"
            except AttributeError:
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
