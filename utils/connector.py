import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["jala_svn"]

companies = database["companies"]
links = database["links"]


def remove_null_field(field):
    query = {f"{field}": "null"}
    companies.update_many(query, {"$unset": {f"{field}": ""}})


if __name__ == '__main__':
    field = "industry"
    remove_null_field(field)
