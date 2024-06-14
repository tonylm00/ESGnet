"""
Module to scrape ESG scores from Sustainalytics and update a MongoDB database.

Functions:
    scrape_sustainalytics(ticker: str) -> float
        Scrapes the Sustainalytics page for the ESG esg_company_data of a given ticker.

    add_to_mongodb(company_name: str, esg: float) -> None
        Adds the ESG esg_company_data to the MongoDB entry for the specified company.

    update_all_companies() -> None
        Updates all companies in the MongoDB database with their ESG scores from Sustainalytics.

Usage:
    To update all companies in the database with their ESG scores, run this module directly.
"""

import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import connector


def scrape_sustainalytics(ticker):
    """
    Scrapes the Sustainalytics page for the ESG esg_company_data of a given ticker.

    Args:
        ticker (str): The stock ticker of the company.

    Returns:
        float: The ESG esg_company_data of the company, or 'null' if not found.
    """
    score = 'null'

    # browser options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # initialize the webdriver
    driver = webdriver.Chrome(options=options)

    driver.get('https://www.sustainalytics.com/esg-ratings')
    action = ActionChains(driver)

    # accept cookies
    cookies_button = driver.find_element(By.ID, 'hs-eu-confirmation-button')
    cookies_button.click()

    driver.find_element(By.ID, 'searchInput').send_keys(':')

    for char in ticker:
        driver.find_element(By.ID, 'searchInput').send_keys(char)
        sleep(0.5)

    sleep(1)
    action.send_keys(Keys.TAB).perform()
    action.send_keys(Keys.ENTER).perform()

    element = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'row')))
    info = element[14].text + element[15].text

    # find pattern in the text
    match = re.search(r"Identifier:\s*(\S+)", info)
    if match:
        identifier = match.group(1)
        if ticker == identifier[-ticker.__len__():]:
            score = float(info.split()[info.split().index('Rating') + 2])
            print(f"{ticker} - {identifier[-ticker.__len__():]:} - Score: {score}")
        else:
            print(f"!match for {ticker} - {identifier[-ticker.__len__():]:}")

    return score


def add_to_mongodb(company_name, esg):
    """
    Adds the ESG esg_company_data to the MongoDB entry for the specified company.

    Args:
        company_name (str): The name of the company.
        esg (float): The ESG esg_company_data of the company.
    """
    query = {"name": company_name}
    existing_entry = connector.companies.find_one(query)
    if existing_entry and 'esg' not in existing_entry:
        connector.companies.update_one(query, {"$set": {"esg": esg}})


def update_all_companies():
    """
    Updates all companies in the MongoDB database with their ESG scores from Sustainalytics.
    """
    for company_doc in connector.companies.find({"esg": {"$exists": False}}):
        if company_doc['ticker'] != 'null':
            esg = scrape_sustainalytics(ticker=company_doc['ticker'])
            add_to_mongodb(company_name=company_doc['name'], esg=esg)
    print('Done')
