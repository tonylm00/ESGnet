import requests
from bs4 import BeautifulSoup
from utils import connector


def get_ticker(company_name):
    """
    Retrieves the stock ticker symbol for a given company name from Investing.com.

    Args:
        company_name (str): The name of the company.

    Returns:
        str: Stock ticker symbol.
    """

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
    """
    Adds the stock ticker symbol for a company to the MongoDB database.

    Args:
        company_name (str): The name of the company.
        ticker (str): Stock ticker symbol.
    """
    
    query = {"name": company_name}
    existing_entry = connector.companies.find_one(query)
    if existing_entry and 'ticker' not in existing_entry:
        new_values = {"$set": {"ticker": ticker}}
        connector.companies.update_one(query, new_values)


def update_all_companies_tickers():
    """
    Updates the stock ticker symbols for all companies in the database that do not have ticker information.

    This function fetches the necessary ticker data from Investing.com and updates the company's
    information in the MongoDB database.
    """

    for company_doc in connector.companies.find({"ticker": {"$exists": False}}):
        ticker = get_ticker(company_doc["name"])

        if ticker:
            add_one_ticker_to_mongodb(company_doc["name"], ticker)
    print('Done')


if __name__ == '__main__':
    update_all_companies_tickers()
