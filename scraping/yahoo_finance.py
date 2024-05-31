from utils import connector
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


def scrape_yf(ticker):
    """
    Retrieves product involvement areas for a given stock ticker from Yahoo Finance.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        dict: Product involvement areas.
    """
    involvement_dict = {}
    url = f"https://finance.yahoo.com/quote/{ticker}/sustainability"
    eq_url = f"https://finance.yahoo.com/quote/{ticker}/sustainability?guccounter=1"

    # browser options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # initialize the webdriver
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    action = ActionChains(driver)

    # accept cookie
    cookies_button = driver.find_element(By.ID, 'scroll-down-btn')
    cookies_button.click()

    for _ in range(6):
        action.send_keys(Keys.TAB).perform()

    action.send_keys(Keys.ENTER).perform()

    if driver.current_url != eq_url:
        print(f'{ticker}: !eq {driver.current_url}')
        return 'null'

    try:
        involvement = driver.find_elements(By.CLASS_NAME, "svelte-jjhdng")[0].text
    except IndexError as e:
        print(f"{ticker}: {e} - {driver.current_url}")
        return 'null'

    # Split the input string into lines
    lines = involvement.split('\n')
    lines.pop(0)
    # Iterate over each line
    for line in lines:
        # Split the line into key and value
        key, value = line.rsplit(' ', 1)
        # Add the key-value pair to the dictionary
        involvement_dict[key] = value

    print(f"{ticker} Dict = {involvement_dict}")
    return involvement_dict


def add_involvement_to_mongodb(company_name, involvement_dict):
    """
    Adds product involvement areas for a company to the MongoDB database.

    Args:
        company_name (str): The name of the company.
        involvement_dict (dict): Product involvement areas.
    """

    query = {"name": company_name}
    existing_entry = connector.companies.find_one(query)

    if existing_entry and 'involvement' not in existing_entry:
        new_values = {"$set": {"involvement": involvement_dict}}
        connector.companies.update_one(query, new_values)


def update_all_companies_involvements():
    """
    Updates product involvement areas for all companies in the database that do not have involvement information.

    This function fetches the necessary involvement data from Yahoo Finance and updates the company's
    information in the MongoDB database.
    """

    for company_doc in connector.companies.find({"involvement": {"$exists": False}, "ticker": {"$exists": True}}):
        if company_doc['ticker'] != 'null':
            add_involvement_to_mongodb(company_doc['name'], scrape_yf(company_doc['ticker']))


if __name__ == '__main__':
    update_all_companies_involvements()
