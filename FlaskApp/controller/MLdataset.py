from FlaskApp.models.analysisResult import AnalysisResult
from FlaskApp.models.patientCases import PatientCases
from FlaskApp.controller.Converters import Converter
from FlaskApp.controller.DicomDecoder import DicomDecoder
from FlaskApp.config.appconfig import UPLOAD_DIR

class MLdataset(object):
    diseases = ['normal','csf','edma','MS','cyst','glioma','glioblastoma','lymphoma','metastesis']
    @classmethod
    def getDataSet(cls):
        mlData = AnalysisResult.getMLData()
        res = []
        for case in mlData:
            case.pop('_id')
            i = 0
            case_id = case['case_id']
            index_1 = case['index_1']
            index_2 = case['index_2']
            case.pop('case_id')
            case.pop('index_1')
            case.pop('index_2')
            image = PatientCases.findImage(case_id, index_1, index_2)['disk_filename']
            pix = Converter(DicomDecoder(UPLOAD_DIR,image)).convertToPixelList()
            for infected_area in case['infected_areas']:
                infected_area.pop('points')
                infected_area.pop('detected_result')
                infected_area['average_chemical_composition'] = infected_area['average_chemical_composition']['y']
                #infected_area['image'] = pix
                if 'actual_result' in infected_area:
                    res.append(infected_area)

        #return mlData
        return res

    @classmethod
    def getProcessedDataSet(cls):
        dataset = cls.getDataSet()
        res=[]
        res.append(any)

    @classmethod
    def getDiseases(cls):
        return diseases

    @classmethod
    def convertToDataTrain(cls, lt):
        res = []
        for e in lt:
            res.append(diseases.index(e))

        return res
