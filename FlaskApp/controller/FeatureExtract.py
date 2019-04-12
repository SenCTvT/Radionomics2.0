from Converters import *
from DicomDecoder import *
import time
import sys
import Spectroscopy
# Defination for Disjoint Set
class DisjointSet:
    #Constructor
    def __init__(self, data, pixel=0):
        self.data = data
        self.pixel = pixel
        self.parent = None
        self.elements = 1
    #find the root and optimize the links in the process
    def find(self):
        if self.parent is None:
            return self
        while(self.parent.parent is not None):
            self.parent = self.parent.parent
        return self.parent
    #Join the DisjointSet ds to self
    def join(self, disjointSet):
        root = disjointSet.find()
        selfRoot = self.find()
        root.parent = selfRoot
        selfRoot.elements += root.elements
#end class DisjointSet
#This class is to cluster the pixels in accordance to suspect  of a single File
class SingleClusterer:
    #constructor
    def __init__(self, dicom):
        #pixel values that are to be suspected
        self.dicom = dicom
        self.pixels = dicom.l;
        self.disjointSets = {}
        self.clusters = {}
        self.diseases = {
            'csf': {},
            'edma': {},
            'MS': {},
            'cyst': {},
            'glioma' : {},
            'glioblastoma': {},
            'lymphoma': {},
            'metastesis': {}
        }
        self.diseases_clusters = {
            'csf': {},
            'edma': {},
            'MS': {},
            'cyst': {},
            'glioma' : {},
            'glioblastoma': {},
            'lymphoma': {},
            'metastesis': {}
        }
        self.disease_detector = {
            'csf': self.csf,
            'edma': self.EDEMA,
            'MS': self.multipleSclerosis,
            'cyst': self.CYST,
            'glioma' : self.glioma,
            'glioblastoma': self.glioblastoma,
            'lymphoma': self.lymphoma,
            'metastesis': self.metastesis
        }
        #first form the disjoint Sets by scanning all the pixels
        for j in range(self.dicom.ds.Columns):
            for i in range(self.dicom.ds.Rows):
                pixel = self.pixels[j, i]
                point = (i, j)
                for _key in self.disease_detector.keys():
                    if self.disease_detector[_key](pixel):
                        #create a disjoint set and add it to the dictionary of disjointSets
                        currentSet = self.diseases[_key][point] = DisjointSet(point);
                        #Now check the neighbouring  pixels and group them if needed
                        begin_i = i - 1
                        begin_j = j - 1
                        for ir in range(3):
                            for jr in range(3):
                                i_t = begin_i + ir
                                j_t = begin_j + jr
                                if i_t == i and j_t == j or i_t < 0 or i_t > self.dicom.ds.Rows or j_t < 0 or j_t > self.dicom.ds.Columns:
                                    continue
                                else:
                                    p_t = (i_t, j_t)
                                    #the point exists in the disjoint set so join that set to this
                                    if p_t in self.diseases[_key] and currentSet.find() != self.diseases[_key][p_t].find():
                                        self.diseases[_key][p_t].join(currentSet)
                        break
            #end inner loop
        #end outer loop
        #Now identify the sets formed and group them into clusters
        for _disease_key in self.diseases.keys():
            disjointSets = self.diseases[_disease_key]
            clusters = self.diseases_clusters[_disease_key]
            for _key in disjointSets.keys():
                _set = disjointSets[_key]
                _root = _set.find()
                #if the root of the disjoint set is not present in the cluster, add the root to the cluster
                flag = False
                if _disease_key == 'glioma' and _root.elements*float(self.dicom.ds.PixelSpacing[0]) > 300:
                    flag = True
                elif _disease_key == 'glioblastoma' and _root.elements*float(self.dicom.ds.PixelSpacing[0]) > 250:
                    flag = True
                elif _disease_key == 'lymphoma' and _root.elements*float(self.dicom.ds.PixelSpacing[0]) > 150:
                    flag = True
                elif _disease_key == 'metastesis' and _root.elements*float(self.dicom.ds.PixelSpacing[0]) > 60:
                    flag = True
                elif _disease_key == 'edma' and _root.elements*float(self.dicom.ds.PixelSpacing[0]) > 150:
                    flag = True
                elif _disease_key == 'cyst' and _root.elements*float(self.dicom.ds.PixelSpacing[0]) > 100:
                    flag = True
                elif _disease_key == 'csf' and _root.elements*float(self.dicom.ds.PixelSpacing[0]) > 200:
                    flag = True
                elif _disease_key == 'MS' and _root.elements*float(self.dicom.ds.PixelSpacing[0]) > 100:
                    flag = True
                if flag:
                    if _root.data not in clusters.keys():
                        clusters[_root.data] = Cluster(self.pixels, self.dicom) #create a new cluster
                        clusters[_root.data].nElements = _root.elements
                    clusters[_root.data].elements.append(_set.data)
    def csf(self, pix):
        return pix >=254 and pix <= 255
    def EDEMA(self, pix):
        return pix >= 251 and pix <= 253
    def multipleSclerosis(self, pix):
        return pix >= 246 and pix <= 250
    def CYST(self, pix):
        return pix >= 228 and pix <= 245
    def glioma(self, pix):
        return pix >= 128 and pix <= 150
    def glioblastoma(self, pix):
        return pix >= 150 and pix <= 180
    def lymphoma(self, pix):
        return pix >= 181 and pix <= 191
    def metastesis(self, pix):
        return pix >= 192 and pix <= 212
    #contains logic for suspection of pixel
    def isPixelSuspectable(self, pix):
        return pix >= 128
        #return self.csf(pixel) or self.EDEMA(pixel) or self.multipleSclerosis(pixel) or self.CYST(pixel) or self.glioma(pixel) or self.glioblastoma(pixel) or self.lymphoma(pixel)
#end class Clusterer
#This class in to encapsulate the cluster of pixel locations, and do various operations to extract features
class Cluster:
    def __init__(self, image, dicom):
        self.nElements = 0
        self.elements = []
        self.image = image
        self.dicom = dicom
        self.diseases = {
            'csf': 0,
            'edma': 0,
            'MS': 0,
            'cyst': 0,
            'glioma' : 0,
            'glioblastoma': 0,
            'lymphoma': 0,
            'metastesis': 0
        }
    def compute(self):
        self.max_x = self.max_y = 0
        self.min_x = self.min_y = sys.maxint
        #computing the left, right, top, bottom bounderies of the suspected area
        for element in self.elements:
            if element[0] < self.min_x:
                self.min_x = element[0]
            if element[1] < self.min_y:
                self.min_y = element[1]
            if element[0] > self.max_x:
                self.max_x = element[0]
            if element[1] > self.max_y:
                self.max_y = element[1]
        #computing the points
        self.p1 = (self.min_x,self.min_y)
        self.p2 = (self.max_x,self.min_y)
        self.p3 = (self.min_x,self.max_y)
        self.p4 = (self.max_x,self.max_y)


        #Calculating Tumor Width
        #sort by y coordinate and iterate throught the entire y coordinate domain
        #take the maximum Width in the traversal
        self.elements.sort(key = lambda x : x[1])
        i = 0
        self.tumorwidth = 0
        for y in range(self.min_y, self.max_y):
            min_x = sys.maxint
            max_x = 0
            while i < len(self.elements) and self.elements[i][1] == y:
                min_x = min(min_x, self.elements[i][0])
                max_x = max(max_x, self.elements[i][0])
                i+=1
            self.tumorwidth = max(self.tumorwidth, max_x - min_x)

        #Calculating Tumor Height
        #sort by x coordinate and iterate throught the entire x coordinate domain
        #take the maximum Height in the traversal
        self.elements.sort(key = lambda x : x[0])
        i = 0
        self.tumorheight = 0
        for x in range(self.min_x, self.max_x):
            min_y = sys.maxint
            max_y = 0
            while i < len(self.elements) and self.elements[i][0] == x:
                min_y = min(min_y, self.elements[i][1])
                max_y = max(max_y, self.elements[i][1])
                i+=1
            self.tumorheight = max(self.tumorheight, max_y - min_y)

        self.tumorwidth *= float(self.dicom.ds.PixelSpacing[0])
        self.tumorheight *= float(self.dicom.ds.PixelSpacing[0])

    def getAverageChemicalComposition(self):
        elementsFound = 0
        totalComposition = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        for element in self.elements:
            pixel = self.image[element[1], element[0]]
            try:
                y=Spectroscopy.spectDisc[pixel]
                elementsFound+=1
                for val in range(20):
                    totalComposition[val] += y[val]
            except:
                pass
        for val in range(20):
            totalComposition[val] /= elementsFound
        return totalComposition
    def getArea(self):
        return (self.max_x-self.min_x)*(self.max_y-self.min_y)*float(self.dicom.ds.PixelSpacing[0])
    def getWidth(self):
        return (self.max_x - self.min_x)
    def getHeight(self):
        return (self.max_y - self.min_y)
    def getTightArea(self):
        return self.nElements * float(self.dicom.ds.PixelSpacing[0])
#end class Cluster
