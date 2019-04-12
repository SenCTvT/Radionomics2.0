import os
from pymongo import MongoClient

#get the mongoclient
mongo = MongoClient(
    os.environ['DB_PORT_27017_TCP_ADDR'],
    27017
)

#select database
db = mongo.radionomics