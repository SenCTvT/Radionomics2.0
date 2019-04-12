from FlaskApp.controller.Conversions import *
from FlaskApp.controller.Conversions import *

class GeneratePixelList:
    def __init__(self, images):
        self.images = images
        self.fileList = []
        self.pixelList = []
        getFileList()
        getListOfPixelList()
    def getFileList(self):
        for f in self.images:
            self.fileList.append(f['filename'])

    def getListOfPixelList(self):
        for x in self.fileList:
            dd = Conversions(x)
            self.pixelList.append(dd.l)
