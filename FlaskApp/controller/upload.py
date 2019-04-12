from FlaskApp.controller.DicomDecoder import DicomDecoder
from FlaskApp.controller.DicomValidator import DicomValidator
from FlaskApp.config.appconfig import UPLOAD_DIR
import os
class Upload(object):
    def __init__(self, files):
        #takes uploaded files and checks validity of files
        self.files = files
        self.error = {}
        self.errorPresent = False
        self.series = []
        self.error['error'] = False
        self.errorfiles = []
        self.validators = []
        self.checkFileValidity()

    def checkFileValidity(self):
        invalidfilesArray = {} #dictionary to store invalid flime names and reason
        for f in self.files:
            try:
                dv = DicomValidator(UPLOAD_DIR, f['name_on_disk'])
                if not dv.validDicom:
                    self.errorPresent = True
                    invalidfiles = {}
                    invalidfiles['reason'] = 'Corrupt Dicom File'
                    invalidfiles['file_name'] = f['original_name']
                    self.errorfiles.append(invalidfiles)
                else:
                    #append the validator
                    self.validators.append({'org_filename': f['original_name'], 'disk_filename' : f['name_on_disk'], 'validator':dv})
            except:
                #change error message later
                self.errorPresent = True
                invalidfiles = {}
                invalidfiles['reason'] = 'Not a Dicom File'
                invalidfiles['file_name'] = f['original_name']
                self.errorfiles.append(invalidfiles)

        if self.errorPresent:
            self.error['error'] = True
            self.error['error_message'] = 'Some files are corrupt or is of invalid format'
            self.error['error_type'] = 'ERROR_FILE' #change to error code later
            self.error['files'] = self.errorfiles
            for f in self.files:
                filename = os.path.join(UPLOAD_DIR,f['name_on_disk'])
                os.remove(filename)
