import pymongo

from P0.connection import constants


def connect_mongo():
    url = constants.host
    client = pymongo.MongoClient(url)
    db = client[constants.db]
    # collection = db[constants.collection]
    return db
