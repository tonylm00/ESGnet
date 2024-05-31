from utils.connector import companies

all_companies_with_ticker = companies.find({'$and': [
    {'ticker': {'$exists': True}},
    {'ticker': {'$ne': 'null'}}
]})
