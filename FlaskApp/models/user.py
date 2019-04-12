from FlaskApp.config.dbconnector import db

class User(object):

    def __init__(self, name, username, email, phone, password, doctor_id):
        self.name = name
        self.username = username
        self.email = email
        if phone is not None:
            self.phone = phone
        self.password = password
        self.doctor_id = doctor_id

    def save(self):
        user = db.User
        user.insert_one(self.__dict__)

    @classmethod
    def usernameExists(cls, username):
        user = db.User
        count = user.find({'username':username}).count()
        return count > 0

    @classmethod
    def emailExists(cls, email):
        user = db.User
        count = user.find({'email':email}).count()
        return count > 0

    @classmethod
    def doctorIdExists(cls, doctor_id):
        user = db.User
        count = user.find({'doctor_id':doctor_id}).count()
        return count > 0
    
    @classmethod
    def passwordValid(cls, username, password):
        count = db.User.find({'username':username, 'password':password}).count()
        return count > 0

    @classmethod
    def changePassword(cls, username, password):
        user = db.User.update_one(
            {'username':username}, 
            {'$set':{
                'password':password
                }
             })
