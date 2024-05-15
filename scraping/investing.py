import requests
from bs4 import BeautifulSoup
from utils import connector


def get_ticker_from_investing(company_name):
    try:
        search_url = f"https://www.investing.com/search/?q={company_name}"
        response = requests.get(search_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            ticker = (soup.find("a", class_="js-inner-all-results-quote-item row")
                      .find("span", class_="second").text)

            print('found ', ticker, "for", company_name)

            return ticker
        else:
            print("Error code: ", response.status_code)
    except AttributeError:
        print('No ticker found for ', company_name)
        return "null"


def add_one_ticker_to_mongodb(company_name, ticker):
    query = {"name": company_name}
    existing_entry = connector.companies.find_one(query)
    if existing_entry and 'ticker' not in existing_entry:
        new_values = {"$set": {"ticker": ticker}}
        connector.companies.update_one(query, new_values)


def update_all_companies_tickers():
    for company_doc in connector.companies.find({"ticker": {"$exists": False}}):
        company_name = company_doc["name"]
        ticker = get_ticker_from_investing(company_name)

        if ticker:
            add_one_ticker_to_mongodb(company_name, ticker)


if __name__ == '__main__':
    update_all_companies_tickers()
    connector.client.close()

