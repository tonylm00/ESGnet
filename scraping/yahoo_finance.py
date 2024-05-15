import requests
from bs4 import BeautifulSoup
import time
from utils import connector


def get_product_involvement_areas(ticker):
    search_url = f"https://finance.yahoo.com/quote/{ticker}/sustainability"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        if search_url == response.url:
            soup = BeautifulSoup(response.text, "html.parser")

            involvement = soup.findAll("td", class_="svelte-jjhdng")

            involvement_dict = {}

            for index, wrapper in enumerate(involvement):
                if index % 2 == 0:
                    involvement_dict[wrapper.text] = ''
                if index % 2 != 0:
                    involvement_dict[involvement[index - 1].text] = wrapper.text

            print("Done for ", ticker, "Dict = ", involvement_dict)
            return involvement_dict
        else:
            print(f"{response.url[8:]} is different than {search_url[8:]}!!! Fuck YahooFinance")
            time.sleep(120)
            update_all_companies_involvements()
    else:
        print("Status code :", response.status_code, "for ", ticker)
        if response.status_code == 404:
            time.sleep(60)
            update_all_companies_involvements()


def add_involvement_to_mongodb(company_name, involvement_dict):
    query = {"name": company_name}
    existing_entry = connector.companies.find_one(query)

    if existing_entry and 'involvement' not in existing_entry:
        new_values = {"$set": {"involvement": involvement_dict}}
        connector.companies.update_one(query, new_values)


def update_all_companies_involvements():
    for company_doc in connector.companies.find({"involvement": {"$exists": False}}):
        company_name = company_doc["name"]
        ticker = company_doc["ticker"]

        if not ticker or ticker == 'null':
            add_involvement_to_mongodb(company_name, involvement_dict="null")
        else:
            involvement_dict = get_product_involvement_areas(ticker)
            if involvement_dict:
                add_involvement_to_mongodb(company_name, involvement_dict)
            else:
                add_involvement_to_mongodb(company_name, involvement_dict="null")


if __name__ == '__main__':
    update_all_companies_involvements()
    connector.client.close()
