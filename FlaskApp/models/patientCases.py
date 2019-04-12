from FlaskApp.config.dbconnector import db
from bson import ObjectId
import datetime
import pymongo

class PatientCases(object):

    def __init__(self, username, case_name, patient_name, patient_age, files):
        self.username = username
        self.patient_name = patient_name
        self.patient_age = patient_age
        if case_name != None:
            self.case_name = case_name
        self.files = []
        self.datetime = datetime.datetime.now()
        for file in files:
            self.files.append(file.__dict__)

    #saves a patient case to db and return the case id
    def save(self):
        case_id = db.PatientCases.insert_one(self.__dict__).inserted_id
        return str(case_id)

    #find a case by its case id
    @classmethod
    def findCase(cls, case_id):
        try:
            return db.PatientCases.find_one({"_id" : ObjectId(case_id)})
        except:
            return None

    #find a series within a case
    @classmethod
    def findSeries(cls, case_id, index_1):
        try:
            case = db.PatientCases.find_one({"_id" : ObjectId(case_id)})
            files = case['files'][index_1]
            return files
        except:
            return None

    #find a image ie. a dict of org_filename and disk_filename
    @classmethod
    def findImage(cls, case_id, index_1, index_2, t2 = False):
        try:
            case = db.PatientCases.find_one({"_id" : ObjectId(case_id)})
            file = case['files'][index_1]['images'][index_2]
            if t2 and ('t2' in case['files'][index_1]['series_description'] or 'T2' in case['files'][index_1]['series_description']):
                return file
            elif not t2:
                return file
            else:
                return None
        except:
            return None

    #return true if the user has authentication to access a case
    @classmethod
    def userHasAuthentication(cls, case_id, username):
        try:
            count = db.PatientCases.find({"_id" : ObjectId(case_id), 'username' : username}).count()
            return count > 0
        except:
            return False

    @classmethod
    def find(cls, username, page=None):
        try:
            case = db.PatientCases.find({"username" : username}).sort("datetime", pymongo.DESCENDING)
            if page != None and page > 0:
                case = case.skip((page-1)*10).limit(10)
            return list(case)
        except Exception as e:
            return None


class DicomSeries(object):
    #initialize dicom series with the series time, series description, list of DicomImage
    def __init__(self, series_time, series_description, images):
        self.series_time = series_time
        self.series_description = series_description
        self.images = []
        for image in images:
            self.images.append(image.__dict__)

class DicomImage(object):
    def __init__(self, org_filename, disk_filename):
        self.org_filename = org_filename
        self.disk_filename = disk_filename
