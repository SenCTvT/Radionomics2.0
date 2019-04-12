from FlaskApp.controller.DicomDecoder import *
from FlaskApp.controller.Converters import *
from FlaskApp.config.appconfig import UPLOAD_DIR
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL_Converter import PILConverter
import numpy as np
import cv2
import io
import StringIO
import pydicom as dicom

class Conversions:

    def __init__(self, dd):
        self.dd = DicomDecoder(UPLOAD_DIR,dd) #change params according to requirement
        self.ds = dicom.read_file(UPLOAD_DIR+dd)
        self.computeLookUpTable()
        self.compute8BitPixels()
        self.createPalette()
        self.generateNumpyArray()

    def dicomToImage(self):
        #img = Image.fromarray(self.data, 'RGB')
        img = Image.fromarray(self.l).convert('L')
        output = StringIO.StringIO()
        draw = ImageDraw.Draw(img)
        fonts_path = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
        #font = ImageFont.truetype(fonts_path, 24)
        #draw.text((0, 0),"Sample Text",(100,200,150),font=font)
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='JPEG')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    def dicomToRIColoredImage(self):
        # contains ri mapped list of list(numpy format)
        self.colored = np.zeros((self.ds.Rows, self.ds.Columns, 3), dtype=np.uint8)
        for i in range(self.ds.Columns):
            for j in range(self.ds.Rows):
                pix = self.l[i, j]
                r = self.palette[pix][0]
                g = self.palette[pix][1]
                b = self.palette[pix][2]
                self.colored[i, j] = [r, g, b]

        img = Image.fromarray(self.colored, 'RGB')
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='JPEG')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr


    def createPalette(self):
        self.palette = [[] for x in xrange(256)]
        f = open("./FlaskApp/Files/RI_Color_Mapper.txt","r")
        f.readline()
        for i in range(256):
            s=f.readline()
            l=s.split()
            for x in l:
                self.palette[i].append(int(x))
        f.close()

    def computeLookUpTable(self):
        #get the 16-bit raw pizels
        self.height = self.dd.height
        self.width = self.dd.width
        self.windowCenter = self.dd.windowCenter
        self.windowWidth = self.dd.windowWidth
        self.pixels16 = self.dd.pixels16
        self.minPix = min(self.pixels16)
        self.maxPix = max(self.pixels16)

        if (self.dd.signedImage):
            self.windowCenter -= (-0x7FFF)
        if (abs(self.windowWidth) < 0.001):
            self.windowWidth = self.maxPix - self.minPix
        if ((self.windowCenter == 0) or (self.minPix > self.windowCenter) or (self.maxPix < self.windowCenter)):
            self.windowCenter = (self.maxPix + self.minPix) / 2
        self.maxPix = int(self.windowCenter + 0.5 * self.windowWidth)
        self.minPix = int(self.maxPix - self.windowWidth)

        self.lut16 = []
        r = self.maxPix - self.minPix
        if (r < 1):
            r = 1
        factor = 255.0 / r
        for i in range(65536):
            if (i <= self.minPix):
                self.lut16.append(0)
            elif (i >= self.maxPix):
                self.lut16.append(255)
            else:
                self.lut16.append(int((i - self.minPix) * factor))

    #Convert To * bit Pixels
    def compute8BitPixels(self):
        self.l = PILConverter.get_LUT_value(self.ds.pixel_array, self.ds.WindowWidth, self.ds.WindowCenter)
        #self.l = Converter(self.dd).convertToPixelList()

    def generateNumpyArray(self):
        self.data = np.zeros((self.ds.Rows, self.ds.Columns, 3), dtype=np.uint8)
        for i in range(self.ds.Columns):
            for j in range(self.ds.Rows):
                self.data[i, j] = [self.l[i, j], self.l[i, j], self.l[i, j]]
