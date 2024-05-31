import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["jala_svn"]

companies = database["companies"]
links = database["links"]


def clean_employees():
    documents = companies.find({"employees": {"$exists": True}})
    for doc in documents:
        employees_value = doc['employees']
        try:
            if isinstance(employees_value, str) and employees_value.replace(',', '').isdigit():
                update = {
                    'employees': int(employees_value.replace(',', '')),
                }
                companies.update_one(
                    {'_id': doc['_id']},
                    {'$set': update}
                )
        except ValueError as e:
            print(f"Errore di conversione per il documento con _id {doc['_id']}: {e}")


def clean_altman_piotroski_score():
    documents = companies.find({"altman_score": {"$exists": True}, "piotroski_score": {"$exists": True}})

    for doc in documents:
        if doc['altman_score'] != 'null' and doc['piotroski_score'] != 'null':
            updates = {
                'altman_score': float(doc['altman_score']),
                'piotroski_score': int(doc['piotroski_score']),
            }
            unset_fields = {
                'update_time': '',
                'username': ''
            }

            companies.update_one(
                {'_id': doc['_id']},
                {
                    '$set': updates,
                    '$unset': unset_fields
                }
            )


def reset_param_from_null(param):
    documents = companies.find({param: {"$exists": True}})

    for doc in documents:
        if doc[param] == 'null':
            unset_fields = {
                param: '',
            }
            companies.update_one(
                {'_id': doc['_id']},
                {
                    '$unset': unset_fields
                }
            )


def remove_fields():
    documents = companies.find()
    for doc in documents:
        unset_fields = {
            'update_time': '',
            'username': ''
        }
        companies.update_one({'_id': doc['_id']}, {'$unset': unset_fields})


if __name__ == '__main__':

    columns = ['ticker',
               'involvement',
               'involvement_msci',
               'employees',
               'industry',
               'sector',
               'altman_score',
               'piotroski_score',
               'Controversies',
               'Decarbonization Target',
               'Temperature Goal',
               'sdg'
               'esg'
               ]

    for col in columns:
        reset_param_from_null(col)
