import time
import requests
from bs4 import BeautifulSoup
from utils import connector
import re


def get_score(ticker):
    # print(ticker)
    search_url = f"https://stockanalysis.com/stocks/{ticker}/statistics/"
    # headers = {"User-Agent": "Mozilla/5.0"}
    # response = requests.get(search_url, headers=headers)
    response = requests.get(search_url, headers={
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/64.0.3282.186 Safari/537.36'})

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            result_string = re.sub(' +', ' ', soup.find("div",
                                                        class_='space-y-5 xs:space-y-6 lg:grid lg:grid-cols-3 '
                                                               'lg:space-x-10 lg:space-y-0 mt-3.5').text)
        except AttributeError as e:
            print(f"{ticker}, {e}")
            return 'null', 'null'

        try:
            alt_score = result_string.split("Altman Z-Score of")[1].split()[0].removesuffix('.')
        except IndexError:
            alt_score = result_string.split("Altman Z-Score")[1].split()[0].removesuffix('.')
            if alt_score == 'n/a':
                alt_score = 'null'

        try:
            pio_score = result_string.split("Piotroski F-Score of")[1].split()[0].removesuffix('.')
        except IndexError:
            pio_score = result_string.split("Piotroski F-Score")[1].split()[0].removesuffix('.')
            if pio_score == 'n/a':
                pio_score = 'null'

        print(f"{ticker} - altman:{alt_score} - piotroski:{pio_score}")

        return alt_score, pio_score
    else:
        if response.status_code == 404:
            return 'null', 'null'
        else:
            print(f"{ticker} - Status code:{response.status_code}")
            if response.status_code == 429:
                time.sleep(60)
                update_all_companies_score()


def add_one_score_to_mongodb(company_name, alt, pio):
    query = {"name": company_name}
    existing_entry = connector.companies.find_one(query)
    if existing_entry and 'altman_score' not in existing_entry and 'piotroski_score' not in existing_entry:
        new_values = {
            "$set": {
                "altman_score": alt,
                'piotroski_score': pio
            }
        }
        connector.companies.update_one(query, new_values)


def update_all_companies_score():
    for company_doc in connector.companies.find({"altman_score": {"$exists": False}, "pio_score": {"$exists": False}}):
        if company_doc['ticker'] != 'null':
            # print(company_doc['ticker'])
            alt, pio = get_score(ticker=company_doc['ticker'])
            add_one_score_to_mongodb(company_name=company_doc['name'], alt=alt, pio=pio)


if __name__ == '__main__':
    update_all_companies_score()
    connector.client.close()
    # get_score('LDCU')
