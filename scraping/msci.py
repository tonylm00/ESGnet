from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

from utils import connector


def sdg_to_dict(info_scraped):
    """
    Converts scraped Sustainable Development Goals (SDG) information into a dictionary.

    Args:
        info_scraped (list): List of web elements containing SDG information.

    Returns:
        dict: Dictionary with SDG information.
    """

    out_dict = {}

    for value in info_scraped:
        if 'sdg-row' not in value.get_attribute('class') or value.text == '':
            continue
        out_dict[value.text] = msci_attribute_to_string(value.get_attribute('class'))

    return out_dict


def msci_attribute_to_string(string):
    """
    Converts MSCI attribute class string to a human-readable string.

    Args:
        string (str): Class string of the MSCI attribute.

    Returns:
        str: Human-readable string for the MSCI attribute.
    """

    if 'sdg-aligned-row' in string:
        return 'Aligned'
    else:
        if 'sdg-strongly-aligned-row' in string:
            return 'Strongly Aligned'
    return 'No'


def controversies_to_dict(info_scraped):
    """
    Converts scraped controversies information into a dictionary.

    Args:
        info_scraped (list): List of web elements containing controversies information.

    Returns:
        dict: Dictionary with controversies information.
    """

    out_dict = {}

    for info in info_scraped:
        if info.text == '':
            continue
        out_dict[info.text] = string_to_color(info.get_attribute('class'))

    return out_dict


def string_to_color(string):
    """
    Converts class string to color.

    Args:
        string (str): Class string indicating the color.

    Returns:
        str: Color represented by the class string.
    """

    if 'Red' in string:
        return 'Red'
    else:
        if 'Orange' in string:
            return 'Orange'
        else:
            if 'Yellow' in string:
                return 'Yellow'
            else:
                if 'Green' in string:
                    return 'Green'
    return 'No'


def decarbonization_target_to_dict(info_scraped):
    """
    Converts scraped decarbonization target information into a dictionary.

    Args:
        info_scraped (list): List of web elements containing decarbonization target information.

    Returns:
        dict: Dictionary with decarbonization target information.
    """

    out_dict = {
        'Target Year': info_scraped[2].text[-4:],
        'Comprehensiveness': info_scraped[3].text[-6:],
        'Ambition p.a.': info_scraped[4].text.removeprefix("Ambition\nProjected reduction per year to meet "
                                                           "stated target**\n").removesuffix(" p.a.")
    }

    if info_scraped[0].text[-3:] == "YES":
        out_dict['Decarbonization Target'] = 'Yes'
    else:
        if info_scraped[0].text[-2:] == "NO":
            out_dict['Decarbonization Target'] = 'No'

    if info_scraped[1].text[-3:] == "YES":
        out_dict['Decarbonization Target on Temperature Rise'] = 'Yes'
    else:
        if info_scraped[1].text[-2:] == "NO":
            out_dict['Decarbonization Target on Temperature Rise'] = 'No'

    return out_dict


def involvement_to_dict(info_scraped):
    """
    Converts scraped business involvement information into a dictionary.

    Args:
        info_scraped (list): List of web elements containing business involvement information.

    Returns:
        dict: Dictionary with business involvement information.
    """

    business_involvements_dict = {}

    if info_scraped[0].text.removeprefix('Banned Controversial Weapons\n') == "NOT INVOLVED":
        business_involvements_dict['Controversial Weapons'] = 'No'
    else:
        if info_scraped[0].text.removeprefix('Banned Controversial Weapons\n') == "INVOLVED":
            business_involvements_dict['Controversial Weapons'] = 'Yes'

    if info_scraped[1].text.removeprefix('Gambling\n') == "NOT INVOLVED":
        business_involvements_dict['Gambling'] = 'No'
    else:
        if info_scraped[1].text.removeprefix('Gambling\n') == "INVOLVED":
            business_involvements_dict['Gambling'] = 'Yes'

    if info_scraped[2].text.removeprefix('Tobacco\n') == "NOT INVOLVED":
        business_involvements_dict['Tobacco Products'] = 'No'
    else:
        if info_scraped[2].text.removeprefix('Tobacco\n') == "INVOLVED":
            business_involvements_dict['Tobacco Products'] = 'Yes'

    if info_scraped[3].text.removeprefix('Alcohol\n') == "NOT INVOLVED":
        business_involvements_dict['Alcoholic Beverages'] = 'No'
    else:
        if info_scraped[3].text.removeprefix('Alcohol\n') == "INVOLVED":
            business_involvements_dict['Alcoholic Beverages'] = 'Yes'

    return business_involvements_dict


def scrape_msci(ticker):
    """
    Scrapes MSCI website for ESG-related information based on the given ticker.

    Args:
        ticker (str): The stock ticker symbol to search for.

    Returns:
        tuple: Contains decarbonization target dictionary, global temperature goal, controversies dictionary,
               involvement dictionary, and SDG dictionary.
    """

    decarbonization_target_dict = 'null'
    global_temperature_goal = 'null'
    controversies_dict = 'null'
    involvement_dict = 'null'
    sdg_dict = 'null'

    # browser options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # initialize the webdriver
    driver = webdriver.Chrome(options=options)

    # Visita la pagina di MSCI
    driver.get("https://www.msci.com/our-solutions/esg-investing/esg-ratings-climate-search-tool/")
    action = ActionChains(driver)

    # accept cookies
    cookies_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
    cookies_button.click()

    # find search bar and send ticker
    driver.find_element(By.ID, '_esgratingsprofile_keywords').send_keys(ticker)
    sleep(2)
    action.send_keys(Keys.DOWN).perform()
    action.send_keys(Keys.ENTER).perform()
    sleep(1)

    try:
        # retrieve decarbonization target
        driver.find_element(By.ID, "esg-commitment-toggle-link").click()
        sleep(1)
        decarbonization_target = driver.find_elements(By.CLASS_NAME, "decarbonization-target-row")
        decarbonization_target_dict = decarbonization_target_to_dict(decarbonization_target)

    except Exception:
        pass

    try:
        # retrieve climate information
        driver.find_element(By.ID, "esg-climate-toggle-link").click()
        sleep(1)
        global_temperature_goal = float(driver.find_element(By.CLASS_NAME, "implied-temp-rise-value")
                                        .text.removesuffix("°C"))
        sleep(1)

    except Exception:
        pass

    try:
        # retrieve controversies
        driver.find_element(By.ID, 'esg-controversies-toggle-link').click()
        sleep(1)
        parent = driver.find_element(By.ID, "controversies-table")
        controversies_dict = controversies_to_dict(parent.find_elements(By.TAG_NAME, 'div'))

    except Exception:
        pass

    try:
        # retrieve business involvement information
        driver.find_element(By.ID, 'esg-involvement-toggle-link').click()
        sleep(1)
        involvement_dict = involvement_to_dict(driver.find_elements(By.CLASS_NAME, "business-involvement-column"))

    except Exception:
        pass

    try:
        # sustainable development goal
        driver.find_element(By.ID, "esg-sdg-alignment-toggle-link").click()
        sleep(1)
        table = driver.find_element(By.ID, 'esg-sdg-alignment-toggle').find_element(By.CLASS_NAME, "col-md-6")
        value = table.find_elements(By.TAG_NAME, 'div')
        sdg_dict = sdg_to_dict(value)

    except Exception:
        pass

    return decarbonization_target_dict, global_temperature_goal, controversies_dict, involvement_dict, sdg_dict


def update_all_companies_score():
    """
    Updates the ESG scores for all companies in the database that do not have SDG information and have a valid ticker.

    This function fetches the necessary ESG data from the MSCI website and updates the company's information in the
    MongoDB database.
    """

    for company_doc in connector.companies.find({"sdg": {"$exists": False}, "ticker": {"$exists": True}}):
        if company_doc['ticker'] != 'null':
            dec_dict, temp_goal, contr_dict, inv_dict, sdg_dict = scrape_msci(ticker=company_doc['ticker'])
            add_into_mongodb(company_doc['name'], dec_dict, temp_goal, contr_dict, inv_dict, sdg_dict)


def add_into_mongodb(company_name, dec_dict, temp_goal, contr_dict, inv_dict, sdg_dict):
    """
    Updates MongoDB with ESG-related information for a company.

    Args:
        company_name (str): The name of the company.
        dec_dict (dict): Decarbonization target dictionary.
        temp_goal (float): Global temperature goal.
        contr_dict (dict): Controversies dictionary.
        inv_dict (dict): Involvement dictionary.
        sdg_dict (dict): Sustainable Development Goals (SDG) dictionary.
    """

    query = {"name": company_name}
    existing_entry = connector.companies.find_one(query)
    if existing_entry:
        update_fields = {}

        if 'Decarbonization Target' not in existing_entry:
            update_fields["Decarbonization Target"] = dec_dict
        if 'Temperature Goal' not in existing_entry:
            update_fields["Temperature Goal"] = temp_goal
        if 'Controversies' not in existing_entry:
            update_fields["Controversies"] = contr_dict
        if 'involvement msci' not in existing_entry and (
                existing_entry.get('involvement') == 'null' or 'involvement' not in existing_entry):
            update_fields["involvement_msci"] = inv_dict
        if 'sdg' not in existing_entry:
            update_fields["sdg"] = sdg_dict

        if update_fields:
            new_values = {"$set": update_fields}
            connector.companies.update_one(query, new_values)
            print(f'Done for {existing_entry['ticker']}')


if __name__ == '__main__':
    '''
    tickers = ['GOOGL', 'AAPL', 'MSFT']
    for ticker in tickers:
        a, b, c, d, e = scrape_msci(ticker=ticker)
        print(f"{ticker}: Decarbonization Target: {a}, Global Temperature:{b}, Controversies: {c}, Involvement: {d}, SDG: {e}")
    '''
    update_all_companies_score()
