from pymongo import MongoClient

def get_db_collection():
    client = MongoClient("localhost",27017)
    db = client["data"]
    collection = db["sensors_data"]
    return collection

def send_data():
    post = {
        "temperatur": 37.7,
        "kelembapan": 51
    }

    collection = get_db_collection()
    
    try:
        collection.insert_one(post)
        print("Data has been Successfully added into the collection")
    except Exception as e:
        print("An Unexpected Error has Occured: ", e)

# Get all of the data and average it
def get_data():
    collection = get_db_collection()

    temp_data = 0
    kel_data = 0
    average = {}

    try:
        for i in collection.find():
            temp_data += i["temperatur"]
            kel_data += i["kelembapan"]
        
        average = {
            "temp_average": temp_data/collection.count_documents({}),
            "kel_average": kel_data/collection.count_documents({})
        }

        return average
    
    except Exception as e:
        print("An Unexpected Error has Occured: ", e)


