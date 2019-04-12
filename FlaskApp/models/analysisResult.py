from FlaskApp.config.dbconnector import db
from bson import ObjectId
import datetime
import pymongo


class AnalysisResult(object):

    def __init__(self, case_id, index_1, index_2, infected_areas):
        self.case_id = case_id
        self.index_1 = index_1
        self.index_2 = index_2
        self.infected_areas = []
        for infected_area in infected_areas:
            self.infected_areas.append(infected_area.__dict__)

    def save(self):
        analysisId = db.AnalysisResult.insert_one(self.__dict__).inserted_id
        return str(analysisId)

    @classmethod
    def delete(cls, case_id, index_1, index_2):
        db.AnalysisResult.delete_many({'index_1':index_1, 'case_id':case_id, 'index_2':index_2})

    @classmethod
    def findByCase(cls, case_id, index_1, index_2):
        try:
            return db.AnalysisResult.find_one({'index_1':index_1, 'case_id':case_id, 'index_2':index_2})
        except:
            return None

    @classmethod
    def find(cls, analysisId, case_id, index_1, index_2):
        try:
            return db.AnalysisResult.find_one({"_id" : ObjectId(analysisId), "case_id" : case_id, "index_1" : index_1, "index_2" : index_2})
        except:
            return None

    @classmethod
    def setActualResult(cls, analysisId, analysis_index, result):
        try:
            infected_areas = db.AnalysisResult.find_one({'_id':ObjectId(analysisId)},
                                                        {'_id':0,'case_id':0,'index_1':0,'index_2':0})['infected_areas']
            infected_areas[analysis_index]['actual_result'] = result
            db.AnalysisResult.update_one({'_id':ObjectId(analysisId)}, {'$set' : {'infected_areas' : infected_areas}})
            return True
        except Exception as e:
            return str(e)

    @classmethod
    def getMLData(cls):
        l = list(db.AnalysisResult.find())

        return l


class InfectedAreas(object):
    def __init__(self, coordinate, box_width, box_height, tumor_width, tumor_height, average_chemical_composition, area, detected_result, points):
        self.coordinate = coordinate
        self.box_width = box_width
        self.box_height = box_height
        self.tumor_width = tumor_width
        self.tumor_height = tumor_height
        self.average_chemical_composition = average_chemical_composition
        self.detected_result = detected_result
        self.area = area
        self.points = points
