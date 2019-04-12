import os, sys
class DicomSeriesValidator:
    def __init__(self, dv):
        self.dv = []
        self.seriesNumber = dv['validator'].seriesNumber
        self.seriesTime = dv['validator'].seriesTime
        self.seriesDescription = dv['validator'].seriesDescription
        self.patientName =  dv['validator'].patientName
        self.dv.append(dv)

    def matches(self, dv):
        return self.seriesTime == dv['validator'].seriesTime

    def add(self,dv):
        if(not(self.matches(dv))):
            return False
        self.dv.append(dv)
        return True

    def organizeDicoms(self):
        self.dv.sort(key=lambda x : x['validator'].imageNumber)

class DicomDirValidator:
    def __init__(self, validators):
        self.series = []
        self.dicoms = validators
        self.patientName = validators[0]['validator'].patientName
        self.patientAge = 25
        for dv in self.dicoms:
            if len(self.series) == 0:
                self.series.append(DicomSeriesValidator(dv))
            else:
                flag = True
                for s in self.series:
                    if(s.matches(dv)):
                        s.add(dv)
                        flag = False
                        break
                if(flag):
                    self.series.append(DicomSeriesValidator(dv))

        for s in self.series:
            s.organizeDicoms()
        self.series.sort(key = lambda x : x.seriesNumber)
