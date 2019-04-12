from FlaskApp.config.dbconnector import db
from bson.objectid import ObjectId

import datetime


class Auth(object):

    def __init__(self, username, datetime):
        self.username = username
        self.datetime = datetime

    #This method checks if a username and password pair is valid, returns a dictionary containing attrs 'success' and 'key'
    @classmethod
    def authorize(cls, username, password):
        count = db.User.find({'username':username,'password':password}).count()
        result = {}
        if count > 0:            
            result['success'] = True
            auth = Auth(username, datetime.datetime.now())
            result['key'] = str(db.Auth.insert_one(auth.__dict__).inserted_id)
        else:
            result['success'] = False
        return result
    
    
    #This method checks if a key is valid, returns a dictionary containing attrs 'valid' and 'username'
    #This method should be called in all api call where key is required to check the validity of key and find its related username
    @classmethod
    def checkKeyValidity(cls, key):
        result = {}
        try:
            object_id = ObjectId(key)
        except:
            result['valid'] = False
            return result

        auth = db.Auth.find_one({'_id': object_id})
        
        if auth is None:
            result['valid'] = False
            return result
        valid_upto = auth['datetime'] + datetime.timedelta(hours = 12)
        if valid_upto < datetime.datetime.now():
            result['valid'] = False
            return result
        else:
            result['valid'] = True
            result['username'] = auth['username']
            return result