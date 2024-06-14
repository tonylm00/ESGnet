import time
import requests
from bs4 import BeautifulSoup
from utils import connector
import re


def get_employees(ticker):
    """
    Retrieves the number of employees for a given stock ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        str: Number of employees.
    """

    search_url = f"https://stockanalysis.com/stocks/{ticker}/company/"
    response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; "
                                                               "rv:96.0) Gecko/20100101 Firefox/96.0"})

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        result_string = re.sub(' +', ' ', soup.find("div", class_='mt-7 rounded border border-gray-200 bg-gray-50 '
                                                                  'px-3 pb-2 pt-3 dark:border-dark-700 '
                                                                  'dark:bg-dark-775 xs:px-4 xs:pt-4 lg:mt-1').text)
        if result_string.__contains__("Employees"):
            employees = result_string.split("Employees")[1].split()[0]
            print(f"{ticker} - {employees}")
            return employees
        else:
            return 'null'
    else:
        if response.status_code == 404:
            return 'null'
        else:
            print(f"{ticker} - Status code:{response.status_code}")
            if response.status_code == 429:
                time.sleep(60)
                update_all_companies_employees()


def add_one_employees_to_mongodb(company_name, employees):
    """
    Adds the number of employees for a company to the MongoDB database.

    Args:
        company_name (str): The name of the company.
        employees (str): Number of employees.
    """

    query = {"name": company_name}
    existing_entry = connector.companies.find_one(query)
    if existing_entry and 'employees' not in existing_entry:
        new_values = {
            "$set": {
                "employees": employees,
            }
        }
        connector.companies.update_one(query, new_values)


def update_all_companies_employees():
    """
    Updates the number of employees for all companies in the database that do not have employee esg_company_data.

    This function fetches the necessary employee data from the Stock Analysis website and updates the company's
    esg_company_data in the MongoDB database.
    """

    for company_doc in connector.companies.find({"employees": {"$exists": False}}):
        if company_doc['ticker'] != 'null':
            employees = get_employees(ticker=company_doc['ticker'])
            if employees != 'null':
                employees = int(employees.replace(',', ''))
            add_one_employees_to_mongodb(company_name=company_doc['name'], employees=employees)
