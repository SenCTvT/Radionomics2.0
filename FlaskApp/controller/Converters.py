'''
Created on Jan 30, 2016

@author: ritwik
'''

from DicomDecoder import *
import sys


#for converting DicomDecoder to Pixmap
class Converter:
    def __init__(self,dd,widthFactor = 1,centerFactor = 1):
        self.palette =[]
        self.pal = False
        #get all the importaint details for convertion from the DicomDecoder object
        self.height = dd.height
        self.width = dd.width

        #windowCenter and windowWidth will be required for computing the lookup table
        self.windowCenter = dd.windowCenter
        self.windowWidth = dd.windowWidth

        #get the 16-bit raw pizels
        self.pixels16 = dd.pixels16
        self.minPix = min(self.pixels16)
        self.maxPix = max(self.pixels16)
        self.dd = dd

        if (self.dd.signedImage):
            self.windowCenter -= (-0x7FFF)

        if (abs(self.windowWidth) < 0.001):
            self.windowWidth = self.maxPix - self.minPix;

        if ((self.windowCenter == 0) or (self.minPix > self.windowCenter) or (self.maxPix < self.windowCenter)):
            self.windowCenter = (self.maxPix + self.minPix) / 2

        #for contrast and brightness changes
        self.windowCenter-=centerFactor
        self.windowWidth-=widthFactor

        #print "wc: " + str(self.windowCenter) + " ww: " + str(self.windowWidth)

        #compute the minimum and maximum pixel from the current windowCenter and windowWidth
        self.maxPix = int(self.windowCenter + 0.5 * self.windowWidth)
        self.minPix = int(self.maxPix - self.windowWidth)

        #compute the lookup table
        self.computeLookUpTable()

    #this function needs to be called to get 8-bit pixel list
    def convertToPixelList(self):
        l = []
        for i in range (self.dd.width):
            for j in range(self.dd.height):
                pix=self.lut16[self.pixels16[i*self.dd.width+j]]
                l.append(pix)
        return l

    #compute the lookup table
    def computeLookUpTable(self):
        self.lut16 = []
        #get the range of pixels
        r = self.maxPix - self.minPix
        if (r < 1):
            r = 1
        #compute the factor of division of the 16-bit space to 8-bit space
        factor = 255.0 / r
        for i in range(65536):
            if (i <= self.minPix):
                self.lut16.append(0)
            elif (i >= self.maxPix):
                self.lut16.append(255)
            else:
                self.lut16.append(int((i - self.minPix) * factor))

#end of DicomDecoderToPixmap
