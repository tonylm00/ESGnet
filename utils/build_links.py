import pandas as pd
from utils import connector


def extract_links():
    """
    Extracts links from a MongoDB collection, filters them based on the presence of company names in the provided DataFrame,
    creates a DataFrame for the filtered links, and saves it to a CSV file.
    """

    companies = pd.read_csv('../data/label_with_metrics.csv')
    links = list(connector.links.find())

    # Filter links to only include companies in the db
    company_names = set(companies['name'])
    filtered_links = [
        link for link in links
        if link['home_name'] in company_names and link['link_name'] in company_names
    ]

    cols = ['_id', 'update_time', 'home_domain', 'link_domain', 'username']
    filtered_links_df = pd.DataFrame(filtered_links).drop(columns=cols)
    filtered_links_df.to_csv('../data/filtered_links.csv', index=False)
