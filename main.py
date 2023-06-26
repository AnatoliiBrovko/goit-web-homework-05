import datetime
import asyncio
import platform
import logging
import sys

import aiohttp
import pandas


async def request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    resp = await response.json()
                    return (resp)
                logging.error(f"Error status{response.status}for {url}")
        except aiohttp.ClientConnectionError as error:
            logging.error(f"Error{error}")
        return None


def get_date(days):
    today = datetime.date.today()
    end_date = datetime.date.today() - datetime.timedelta(int(days) - 1)
    date_list = pandas.date_range(
        min(today, end_date),
        max(today, end_date)
    ).strftime("%d.%m.%Y").tolist()
    print(date_list)
    return date_list

def get_urls(days):
    dates = get_date(days)
    urls = []
    for date in dates:
        urls.append(str('https://api.privatbank.ua/p24api/exchange_rates?date=') + date)
    return urls


async def get_exchange(days):
    urls = get_urls(days)
    r = []
    for url in urls:
        result = await request(url)
        res = {}
        date = result.get("date")
        currency = result.get("exchangeRate")
        for cur in currency:
            if cur.get("currency") == "EUR" or cur.get("currency") == "USD":
                res.update({cur.get("currency"): {"sale": cur.get(
                    "saleRateNB"), "purchase": cur.get("purchaseRateNB")}})
        r.append({date: res})
    return (r)



if __name__ == "__main__":
    days = int(sys.argv[1])
    if days == 0 or days > 10:
        print("Enter the number of days from 1 to 10")
    else:
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        r = asyncio.run(get_exchange(days))
        print(r)