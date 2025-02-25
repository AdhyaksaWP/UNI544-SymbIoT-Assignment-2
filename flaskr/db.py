from pymongo import MongoClient

def get_db_collection():
    client = MongoClient("localhost",27017)
    db = client["data"]
    collection = db["sensors_data"]

    print("Connected to db collection")
    return collection

def send_data(data):
    collection = get_db_collection()
    
    try:
        collection.insert_one(data)
        print("Data has been Successfully added into the collection")
    except Exception as e:
        print("An Unexpected Error has Occured: ", e)