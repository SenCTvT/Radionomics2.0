﻿'''
Created on Jan 24, 2016
@author: Krishanu
'''
from __future__ import division
import os
import struct as _struct
class DicomValidator:

    #Dicom Tags
    PIXEL_REPRESENTATION = 0x00280103
    TRANSFER_SYNTAX_UID = 0x00020010
    MODALITY = 0x00080060
    SLICE_THICKNESS = 0x00180050
    SLICE_SPACING = 0x00180088
    IMAGER_PIXEL_SPACING = 0x00181164
    SAMPLES_PER_PIXEL = 0x00280002
    PHOTOMETRIC_INTERPRETATION = 0x00280004
    PLANAR_CONFIGURATION = 0x00280006
    NUMBER_OF_FRAMES = 0x00280008
    ROWS = 0x00280010
    COLUMNS = 0x00280011
    PIXEL_SPACING = 0x00280030
    BITS_ALLOCATED = 0x00280100
    WINDOW_CENTER = 0x00281050
    WINDOW_WIDTH = 0x00281051
    RESCALE_INTERCEPT = 0x00281052
    RESCALE_SLOPE = 0x00281053
    RED_PALETTE = 0x00281201
    GREEN_PALETTE = 0x00281202
    BLUE_PALETTE = 0x00281203
    ICON_IMAGE_SEQUENCE = 0x00880200
    ITEM = 0xFFFEE000
    ITEM_DELIMINATION = 0xFFFEE00D
    SEQUENCE_DELIMINATION = 0xFFFEE0DD
    SERIES_TIME = 0x00080031
    SERIES_DESCRIPTION = 0x0008103E
    PIXEL_DATA = 0x7FE00010
    PATIENT_NAME = 0x00100010
    IMAGE_NUMBER = 0x00200013
    SERIES_NUMBER = 0x00200011


    #VR's
    IMPLICIT_VR = 0x2D2D

    AE=0x4145
    AS=0x4153
    AT=0x4154
    CS=0x4353
    DA=0x4441
    DS=0x4453
    DT=0x4454
    FD=0x4644
    FL=0x464C
    IS=0x4953
    LO=0x4C4F
    LT=0x4C54
    PN=0x504E
    SH=0x5348
    SL=0x534C
    SS=0x5353
    ST=0x5354
    TM=0x544D
    UI=0x5549
    UL=0x554C
    US=0x5553
    UT=0x5554
    OB=0x4F42
    OW=0x4F57
    SQ=0x5351
    UN=0x554E
    QQ=0x3F3F


    def __init__(self,directory,fileName):

        #instance varriables
        self.path = os.path.join(directory, fileName)
        self.bitsAllocated = 0
        self.width = 1
        self.height = 1
        self.offset = 1
        self.nImages = 1
        self.samplesPerPixel = 1
        self.photoInterpretation = ""
        self.unit = "mm"
        self.windowCenter = 0
        self.windowWidth = 0
        self.signedImage = False
        self.widthTagFound = False
        self.heightTagFound = False
        self.pixelDataTagFound = False
        self.rescaleIntercept = 0.0
        self.rescaleSlope = 1.0

        self.bitsAllocated = 16
        self.nImages = 0
        self.pixelDepth = 1.0
        self.pixelWidth = 1.0
        self.pixelHeight = 1.0
        self.typeofDicomFile = "NotDicom"
        self.dicmFound = False

        self.littleEndian = True
        self.oddLocations = False
        self.bigEndianTransferSyntax = False
        self.inSequence =False
        self.location = 0
        self.elementLength = 0
        self.vr = 0x0000
        self.min8 = -128
        self.max8 = 255
        self.min16 = -32768
        self.max16 = 0xFFFF
        self.pixelRepresentation = 0
        self.pixels16=[]
        self.pixels16Int=[]
        self.rescaleIntercept = 0.0
        self.rescaleSlope = 1.0

        self.vrLetters = [0,0]

        self.seriesTime = ""
        self.seriesDescription = ""
        self.patientName = ""

        self.previousGroup=""
        self.previousInfo=""
        self.dicomInfo = []
        self.modality = ""
        self.validDicom = False

        if(os.path.exists(self.path)):
            self.file = open(self.path,"rb")
            readResult = self.readFileInfo()
            if(readResult and self.widthTagFound and self.heightTagFound and self.pixelDataTagFound):
                self.validDicom = True
            else:
                self.validDicom = False
            self.file.close()


    #get the data from the file

    def getString(self,length):
        self.location+=length
        s=self.file.read(length)
        return s

    def getUNString(self,length):
        s= self.getString(length)
        if(s!=None and len(s)>60):
            s=s[:60]
        return s

    def getByte(self):
        b=self.file.read(1)
        if(b==''):
            self.validDicom = False
        self.location+=1
        if(len(b) != 0):
            return ord(b)

    def getShort(self):
        b0=self.getByte()
        b1=self.getByte()
        if(self.littleEndian):
            return((b1 << 8)+ b0)
        else:
            return((b0 << 8)+ b1)

    def getInt(self):
        b0 = self.getByte()
        b1 = self.getByte()
        b2 = self.getByte()
        b3 = self.getByte()
        if (self.littleEndian):
            return ((b3<<24) + (b2<<16) + (b1<<8) + b0)
        else:
            return ((b0<<24) + (b1<<16) + (b2<<8) + b3)

    def getDouble(self):
        b0 = self.getByte()
        b1 = self.getByte()
        b2 = self.getByte()
        b3 = self.getByte()
        b4 = self.getByte()
        b5 = self.getByte()
        b6 = self.getByte()
        b7 = self.getByte()
        res = 0
        if (self.littleEndian):
            res += b0
            res += ( b1 << 8)
            res += ( b2 << 16)
            res += ( b3 << 24)
            res += ( b4 << 32)
            res += ( b5 << 40)
            res += ( b6 << 48)
            res += ( b7 << 56)
        else:
            res += b7
            res += ( b6 << 8)
            res += ( b5 << 16)
            res += ( b4 << 24)
            res += ( b3 << 32)
            res += ( b2 << 40)
            res += ( b1 << 48)
            res += ( b0 << 56)

        return self.longBitsToDouble(res)

    def longBitsToDouble(self,bits):
        return _struct.unpack('d', _struct.pack('Q', bits))[0]

    def getFloat(self):
        b0 = self.getByte()
        b1 = self.getByte()
        b2 = self.getByte()
        b3 = self.getByte()
        res = 0
        if (self.littleEndian):
            res += b0
            res += ( b1 << 8)
            res += ( b2 << 16)
            res += ( b3 << 24)
        else:
            res += b3
            res += ( b2 << 8)
            res += ( b1 << 16)
            res += ( b0 << 24)

        return self.intBitsToFloat(res)

    def intBitsToFloat(self,bits):
        s=_struct.pack('>f',bits)
        return _struct.unpack('>f',s)[0]

    def getLut(self,length):
        if ((length&1)!=0):
            dummy = self.getString(length)
            return None
        length /= 2
        lut = []
        for i in range(length):
            lut.append(self.getShort()>>8)
        return lut

    def getLength(self):
        b0 = self.getByte()
        b1 = self.getByte()
        b2 = self.getByte()
        b3 = self.getByte()

        # We cannot know whether the VR is implicit or explicit
        # without the full DICOM Data Dictionary for public and
        # private groups.

        # We will assume the VR is explicit if the two bytes
        # match the known codes. It is possible that these two
        # bytes are part of a 32-bit length for an implicit VR.

        self.vr = (b0<<8) + b1

        if(self.vr == self.OB or self.vr == self.OW or self.vr == self.SQ or self.vr == self.UN or self.vr == self.UT):
            # Explicit VR with 32-bit length if other two bytes are zero
            if ( (b2 == 0) or (b3 == 0) ):
                return self.getInt()
            # Implicit VR with 32-bit length
            self.vr = self.IMPLICIT_VR
            if (self.littleEndian):
                return ((b3<<24) + (b2<<16) + (b1<<8) + b0)
            else:
                return ((b0<<24) + (b1<<16) + (b2<<8) + b3)
        elif([self.AE, self.AS, self.AT, self.CS, self.DA, self.DS, self.DT,  self.FD,
            self.FL, self.IS, self.LO, self.LT, self.PN, self.SH, self.SL, self.SS,
            self.ST, self.TM,self.UI, self.UL, self.US, self.QQ].__contains__(self.vr)):
            # Explicit vr with 16-bit length
            if (self.littleEndian):
                return ((b3<<8) + b2)
            else:
                return ((b2<<8) + b3)
        else:
            # Implicit VR with 32-bit length...
            self.vr = self.IMPLICIT_VR
            if (self.littleEndian):
                return ((b3<<24) + (b2<<16) + (b1<<8) + b0)
            else:
                return ((b0<<24) + (b1<<16) + (b2<<8) + b3)

    def getNextTag(self):
        groupWord = self.getShort()
        if(groupWord == 0x0800 and self.bigEndianTransferSyntax):
            self.littleEndian = False
            groupWord = 0x0008

        elementWord = self.getShort()
        tag = groupWord<<16 | elementWord

        self.elementLength = self.getLength()
        if(self.elementLength==13 and not(self.oddLocations)):
            self.elementLength = 10;

        if(self.elementLength==-1):
            self.elementLength = 0
            self.inSequence = True
        return tag

    def readFileInfo(self):
        self.bitsAllocated = 16
        self.file.seek(128)
        self.location+= 128

        if(not(self.getString(4)) == "DICM"):
            self.file.close()
            self.file = open(self.path,"rb")
            self.location = 0
            #Older DICOM files do not have the preamble and prefix
            self.dicmFound = False
            # Continue reading further.
            # See whether the width, height and pixel data tags
            # are present. If these tags are present, then it we conclude that this is a
            # DICOM file, because all DICOM files should have at least these three tags.
            # Otherwise, it is not a DICOM file.

        else:
            self.dicmFound = True
            # We have a DICOM 3.0 file
        self.samplesPerPixel = 1
        planarConfiguration = 0
        self.photoInterpretation = ""
        decodingTags = True
        while (decodingTags):
            tag = self.getNextTag()
            #print "\nTag: %08x, Length: %d, %s" % (tag,self.elementLength,self.dictionary[tag])
            if (self.location&1 != 0):
                self.oddLocations = True
            if (self.inSequence):
                self.addInfo(tag, None)
                continue
            if(tag == self.TRANSFER_SYNTAX_UID):
                s = self.getString(self.elementLength)
                self.addInfo(tag,s)
                if("1.2.4" in s or "1.2.5" in s):
                    self.file.close()
                    self.typeofDicomFile = "DicomUnknownTransferSyntax"
                    # Return gracefully indicating that this type of
                    # Transfer Syntax cannot be handled
                    return False;
                if ("1.2.840.10008.1.2.2" in s):
                    self.bigEndianTransferSyntax = True;

            elif(tag == self.MODALITY):
                self.modality = self.getString(self.elementLength)
                self.addInfo(tag, self.modality)
            elif(tag == self.NUMBER_OF_FRAMES):
                s = self.getString(self.elementLength);
                self.addInfo(tag, s);
                frames = self.s2d(s)
                if (frames > 1.0):
                    self.nImages = int(frames)

            elif(tag == self.SAMPLES_PER_PIXEL):
                self.samplesPerPixel = self.getShort()
                self.addInfo(tag, self.samplesPerPixel)
            elif(tag == self.PHOTOMETRIC_INTERPRETATION):
                self.photoInterpretation = self.getString(self.elementLength)
                self.photoInterpretation = self.photoInterpretation.strip()
                self.addInfo(tag, self.photoInterpretation)
            elif(tag == self.PLANAR_CONFIGURATION):
                self.planarConfiguration = self.getShort()
                self.addInfo(tag, planarConfiguration)
            elif(tag == self.ROWS):
                self.height = self.getShort()
                self.addInfo(tag, self.height)
                self.heightTagFound = True
            elif(tag == self.COLUMNS):
                self.width = self.getShort()
                self.addInfo(tag, self.width)
                self.widthTagFound = True
            elif(tag == self.PIXEL_SPACING):
                self.scale = self.getString(self.elementLength)
                self.getSpatialScale(self.scale)
                self.addInfo(tag, self.scale)
            elif(tag == self.SLICE_THICKNESS or tag == self.SLICE_SPACING):
                self.spacing = self.getString(self.elementLength)
                self.pixelDepth = self.s2d(self.spacing)
                self.addInfo(tag, self.spacing)
            elif(tag == self.BITS_ALLOCATED):
                self.bitsAllocated = self.getShort()
                self.addInfo(tag, self.bitsAllocated)
            elif(tag == self.PIXEL_REPRESENTATION):
                self.pixelRepresentation = self.getShort()
                self.addInfo(tag, self.pixelRepresentation)
            elif(tag == self.WINDOW_CENTER):
                center = self.getString(self.elementLength)
                index = -1
                try:
                    index = center.index('\\')
                except:
                    pass
                if (not(index == -1)):
                    center = center[(index + 1):]
                self.windowCenter = self.s2d(center)
                self.addInfo(tag, center);
            elif(tag == self.WINDOW_WIDTH):
                widthS = self.getString(self.elementLength)
                index = -1
                try:
                    index = widthS.index('\\')
                except:
                    pass
                if (index != -1):
                    widthS = widthS[(index + 1):]
                self.windowWidth = self.s2d(widthS)
                self.addInfo(tag, widthS)
            elif(tag == self.RESCALE_INTERCEPT):
                intercept = self.getString(self.elementLength)
                self.rescaleIntercept = self.s2d(intercept)
                self.addInfo(tag, intercept)

            elif(tag == self.RESCALE_SLOPE):
                slop = self.getString(self.elementLength)
                self.rescaleSlope = self.s2d(slop)
                self.addInfo(tag, slop)
                break
            elif(tag == self.RED_PALETTE):
                self.reds = self.getLut(self.elementLength)
                self.addInfo(tag, self.elementLength / 2)
            elif(tag == self.GREEN_PALETTE):
                self.greens = self.getLut(self.elementLength)
                self.addInfo(tag, self.elementLength / 2)
            elif(tag == self.BLUE_PALETTE):
                self.blues = self.getLut(self.elementLength)
                self.addInfo(tag, self.elementLength / 2)
            elif(tag == self.SERIES_TIME):
                self.seriesTime = self.getString(self.elementLength)
                self.addInfo(tag, self.seriesTime)
            elif(tag == self.SERIES_DESCRIPTION):
                self.seriesDescription = self.getString(self.elementLength)
                self.addInfo(tag, self.seriesDescription)
            elif(tag == self.PATIENT_NAME):
                self.patientName = self.getString(self.elementLength)
                #self.sequenceName()
                self.addInfo(tag, self.patientName)
            elif(tag == self.IMAGE_NUMBER):
                self.imageNumber = int(self.getString(self.elementLength))
                self.addInfo(tag, self.imageNumber)
            elif(tag == self.SERIES_NUMBER):
                self.seriesNumber = int(self.getString(self.elementLength))
                self.addInfo(tag, self.seriesNumber)
            elif(tag == self.PIXEL_DATA):
                if (self.elementLength != 0):
                    self.offset = self.location
                    self.addInfo(tag, self.location)
                    decodingTags = False
                else:
                    self.addInfo(tag, None)
                self.pixelDataTagFound = True

            else:

                self.addInfo(tag, None)
        return True
    def sequenceName(self):
        self.patientName = self.patientName.split('^')
        self.patientName = self.patientName[0:2]
        self.patientName = self.patientName[1] +  " " + self.patientName[0]
    def getSignedShort(self,i):
        if(i & 0x8000):
            cmp_ = ~i + 1;
            sign = cmp_ & 0xffff
            return -sign
        else:
            return i


    def getHeaderInfo(self, tag, value):
        if (tag==self.ITEM_DELIMINATION or tag==self.SEQUENCE_DELIMINATION):
            self.inSequence = False
            return None
        id_ = None
        try:
            id_ = self.dictionary[tag]
        except:
            pass

        #print "ID: " + str(id_)
        #print "VR1: %08x"%self.vr
        if (id_!=None):
            #print "id: " + id_
            if (self.vr==self.IMPLICIT_VR and id_!=None):
                self.vr = (ord(id_[0])<<8) + ord(id_[1])
            id_ = id_[2:]
        if (tag==self.ITEM):
            if(id_ != None):
                return id_
            else:
                return None
        if (value!=None):
            return str(id_)+": "+value;

        #print "VR2: %08x"%self.vr

        if(self.vr == self.FD):
            if(self.elementLength == 8):
                value = str(self.getDouble())
        elif([self.AE, self.AS, self.AT, self.CS, self.DA, self.DS, self.DT,  self.IS, self.LO,
            self.LT, self.PN, self.SH, self.ST, self.TM, self.UI].__contains__(self.vr)):
            value = self.getString(self.elementLength)
        elif(self.vr == self.UN):
            value = self.getUNString()
        elif(self.vr == self.US):
            if (self.elementLength==2):
                value = str(self.getShort())
            else:
                n = int(self.elementLength/2);
                value = ""
                for i in range(n):
                    value = value + str(self.getShort()) + " "

        elif(self.vr == self.IMPLICIT_VR):
            value = self.getString(self.elementLength)
            if (self.elementLength>44):
                value=None
        elif(self.vr == self.SQ):
            value = ""
            privateTag = ((tag>>16)&1)!=0
            if(tag!=self.ICON_IMAGE_SEQUENCE and not(privateTag)):
                self.file.seek(self.elementLength,1)
                self.location += self.elementLength;
                value = ""
        else:
            self.file.seek(self.elementLength,1)
            self.location += self.elementLength
            value = ""

        if (value!=None and id_==None and not (value == "")):
            return "---: "+value
        elif (id_==None):
            return None
        else:
            return id_+": "+value

    def s2d(self,s):
        if (s==None):
            return 0.0
        if (s.startswith("\\")):
            s = s[1:]
        d=None
        try:
            d = float(s)
        except:
            d = None
        if (d!=None):
            return d
        else:
            return 0.0

    def addInfo(self,tag,value):
        if(value == None):
            info = self.getHeaderInfo(tag, value)
        else:
            info = self.getHeaderInfo(tag, str(value))
        if (self.inSequence and info!=None and self.vr!=self.SQ):
            info = ">" + info
        if (info!=None and  tag!=self.ITEM):
            group = tag>>16
            self.previousGroup = group
            self.previousInfo = info
            self.dicomInfo.append(str(tag)+ ":" + str(info))
    def getSpatialScale(self,scale):
        xscale=0.0
        yscale=0.0
        i = -1
        try:
            i = scale.index('\\')
        except:
            pass
        if (i>0):
            yscale = self.s2d(scale[0:i])
            xscale = self.s2d(scale[i+1:])
        if (xscale!=0.0 and yscale!=0.0):
            self.pixelWidth = xscale
            self.pixelHeight = yscale
            self.unit = "mm"


    #dicomDictionary
    dictionary={
        0x00020002:"UIMedia Storage SOP Class UID",
        0x00020003:"UIMedia Storage SOP Inst UID",
        0x00020010:"UITransfer Syntax UID",
        0x00020012:"UIImplementation Class UID",
        0x00020013:"SHImplementation Version Name",
        0x00020016:"AESource Application Entity Title",
        0x00080005:"CSSpecific Character Set",
        0x00080008:"CSImage Type",
        0x00080010:"CSRecognition Code",
        0x00080012:"DAInstance Creation Date",
        0x00080013:"TMInstance Creation Time",
        0x00080014:"UIInstance Creator UID",
        0x00080016:"UISOP Class UID",
        0x00080018:"UISOP Instance UID",
        0x00080020:"DAStudy Date",
        0x00080021:"DASeries Date",
        0x00080022:"DAAcquisition Date",
        0x00080023:"DAImage Date",
        0x00080024:"DAOverlay Date",
        0x00080025:"DACurve Date",
        0x00080030:"TMStudy Time",
        0x00080031:"TMSeries Time",
        0x00080032:"TMAcquisition Time",
        0x00080033:"TMImage Time",
        0x00080034:"TMOverlay Time",
        0x00080035:"TMCurve Time",
        0x00080040:"USData Set Type",
        0x00080041:"LOData Set Subtype",
        0x00080042:"CSNuclear Medicine Series Type",
        0x00080050:"SHAccession Number",
        0x00080052:"CSQuery/Retrieve Level",
        0x00080054:"AERetrieve AE Title",
        0x00080058:"AEFailed SOP Instance UID List",
        0x00080060:"CSModality",
        0x00080064:"CSConversion Type",
        0x00080068:"CSPresentation Intent Type",
        0x00080070:"LOManufacturer",
        0x00080080:"LOInstitution Name",
        0x00080081:"STInstitution Address",
        0x00080082:"SQInstitution Code Sequence",
        0x00080090:"PNReferring Physician's Name",
        0x00080092:"STReferring Physician's Address",
        0x00080094:"SHReferring Physician's Telephone Numbers",
        0x00080100:"SHCode Value",
        0x00080102:"SHCoding Scheme Designator",
        0x00080104:"LOCode Meaning",
        0x00080201:"SHTimezone Offset From UTC",
        0x00081010:"SHStation Name",
        0x00081030:"LOStudy Description",
        0x00081032:"SQProcedure Code Sequence",
        0x0008103E:"LOSeries Description",
        0x00081040:"LOInstitutional Department Name",
        0x00081048:"PNPhysician(s) of Record",
        0x00081050:"PNAttending Physician's Name",
        0x00081060:"PNName of Physician(s) Reading Study",
        0x00081070:"PNOperator's Name",
        0x00081080:"LOAdmitting Diagnoses Description",
        0x00081084:"SQAdmitting Diagnosis Code Sequence",
        0x00081090:"LOManufacturer's Model Name",
        0x00081100:"SQReferenced Results Sequence",
        0x00081110:"SQReferenced Study Sequence",
        0x00081111:"SQReferenced Study Component Sequence",
        0x00081115:"SQReferenced Series Sequence",
        0x00081120:"SQReferenced Patient Sequence",
        0x00081125:"SQReferenced Visit Sequence",
        0x00081130:"SQReferenced Overlay Sequence",
        0x00081140:"SQReferenced Image Sequence",
        0x00081145:"SQReferenced Curve Sequence",
        0x00081150:"UIReferenced SOP Class UID",
        0x00081155:"UIReferenced SOP Instance UID",
        0x00082111:"STDerivation Description",
        0x00082112:"SQSource Image Sequence",
        0x00082120:"SHStage Name",
        0x00082122:"ISStage Number",
        0x00082124:"ISNumber of Stages",
        0x00082129:"ISNumber of Event Timers",
        0x00082128:"ISView Number",
        0x0008212A:"ISNumber of Views in Stage",
        0x00082130:"DSEvent Elapsed Time(s)",
        0x00082132:"LOEvent Timer Name(s)",
        0x00082142:"ISStart Trim",
        0x00082143:"ISStop Trim",
        0x00082144:"ISRecommended Display Frame Rate",
        0x00082200:"CSTransducer Position",
        0x00082204:"CSTransducer Orientation",
        0x00082208:"CSAnatomic Structure",
        0x00100010:"PNPatient's Name",
        0x00100020:"LOPatient ID",
        0x00100021:"LOIssuer of Patient ID",
        0x00100030:"DAPatient's Birth Date",
        0x00100032:"TMPatient's Birth Time",
        0x00100040:"CSPatient's Sex",
        0x00101000:"LOOther Patient IDs",
        0x00101001:"PNOther Patient Names",
        0x00101005:"PNPatient's Maiden Name",
        0x00101010:"ASPatient's Age",
        0x00101020:"DSPatient's Size",
        0x00101030:"DSPatient's Weight",
        0x00101040:"LOPatient's Address",
        0x00102150:"LOCountry of Residence",
        0x00102152:"LORegion of Residence",
        0x00102180:"SHOccupation",
        0x001021A0:"CSSmoking Status",
        0x001021B0:"LTAdditional Patient History",
        0x00104000:"LTPatient Comments",
        0x00180010:"LOContrast/Bolus Agent",
        0x00180015:"CSBody Part Examined",
        0x00180020:"CSScanning Sequence",
        0x00180021:"CSSequence Variant",
        0x00180022:"CSScan Options",
        0x00180023:"CSMR Acquisition Type",
        0x00180024:"SHSequence Name",
        0x00180025:"CSAngio Flag",
        0x00180030:"LORadionuclide",
        0x00180031:"LORadiopharmaceutical",
        0x00180032:"DSEnergy Window Centerline",
        0x00180033:"DSEnergy Window Total Width",
        0x00180034:"LOIntervention Drug Name",
        0x00180035:"TMIntervention Drug Start Time",
        0x00180040:"ISCine Rate",
        0x00180050:"DSSlice Thickness",
        0x00180060:"DSkVp",
        0x00180070:"ISCounts Accumulated",
        0x00180071:"CSAcquisition Termination Condition",
        0x00180072:"DSEffective Series Duration",
        0x00180073:"CSAcquisition Start Condition",
        0x00180074:"ISAcquisition Start Condition Data",
        0x00180075:"ISAcquisition Termination Condition Data",
        0x00180080:"DSRepetition Time",
        0x00180081:"DSEcho Time",
        0x00180082:"DSInversion Time",
        0x00180083:"DSNumber of Averages",
        0x00180084:"DSImaging Frequency",
        0x00180085:"SHImaged Nucleus",
        0x00180086:"ISEcho Numbers(s)",
        0x00180087:"DSMagnetic Field Strength",
        0x00180088:"DSSpacing Between Slices",
        0x00180089:"ISNumber of Phase Encoding Steps",
        0x00180090:"DSData Collection Diameter",
        0x00180091:"ISEcho Train Length",
        0x00180093:"DSPercent Sampling",
        0x00180094:"DSPercent Phase Field of View",
        0x00180095:"DSPixel Bandwidth",
        0x00181000:"LODevice Serial Number",
        0x00181004:"LOPlate ID",
        0x00181010:"LOSecondary Capture Device ID",
        0x00181012:"DADate of Secondary Capture",
        0x00181014:"TMTime of Secondary Capture",
        0x00181016:"LOSecondary Capture Device Manufacturer",
        0x00181018:"LOSecondary Capture Device Manufacturer's Model Name",
        0x00181019:"LOSecondary Capture Device Software Version(s)",
        0x00181020:"LOSoftware Versions(s)",
        0x00181022:"SHVideo Image Format Acquired",
        0x00181023:"LODigital Image Format Acquired",
        0x00181030:"LOProtocol Name",
        0x00181040:"LOContrast/Bolus Route",
        0x00181041:"DSContrast/Bolus Volume",
        0x00181042:"TMContrast/Bolus Start Time",
        0x00181043:"TMContrast/Bolus Stop Time",
        0x00181044:"DSContrast/Bolus Total Dose",
        0x00181045:"ISSyringe Counts",
        0x00181050:"DSSpatial Resolution",
        0x00181060:"DSTrigger Time",
        0x00181061:"LOTrigger Source or Type",
        0x00181062:"ISNominal Interval",
        0x00181063:"DSFrame Time",
        0x00181064:"LOFraming Type",
        0x00181065:"DSFrame Time Vector",
        0x00181066:"DSFrame Delay",
        0x00181070:"LORadionuclide Route",
        0x00181071:"DSRadionuclide Volume",
        0x00181072:"TMRadionuclide Start Time",
        0x00181073:"TMRadionuclide Stop Time",
        0x00181074:"DSRadionuclide Total Dose",
        0x00181075:"DSRadionuclide Half Life",
        0x00181076:"DSRadionuclide Positron Fraction",
        0x00181080:"CSBeat Rejection Flag",
        0x00181081:"ISLow R-R Value",
        0x00181082:"ISHigh R-R Value",
        0x00181083:"ISIntervals Acquired",
        0x00181084:"ISIntervals Rejected",
        0x00181085:"LOPVC Rejection",
        0x00181086:"ISSkip Beats",
        0x00181088:"ISHeart Rate",
        0x00181090:"ISCardiac Number of Images",
        0x00181094:"ISTrigger Window",
        0x00181100:"DSReconstruction Diameter",
        0x00181110:"DSDistance Source to Detector",
        0x00181111:"DSDistance Source to Patient",
        0x00181120:"DSGantry/Detector Tilt",
        0x00181130:"DSTable Height",
        0x00181131:"DSTable Traverse",
        0x00181140:"CSRotation Direction",
        0x00181141:"DSAngular Position",
        0x00181142:"DSRadial Position",
        0x00181143:"DSScan Arc",
        0x00181144:"DSAngular Step",
        0x00181145:"DSCenter of Rotation Offset",
        0x00181146:"DSRotation Offset",
        0x00181147:"CSField of View Shape",
        0x00181149:"ISField of View Dimensions(s)",
        0x00181150:"ISExposure Time",
        0x00181151:"ISX-ray Tube Current",
        0x00181152:"ISExposure",
        0x00181153:"ISExposure in uAs",
        0x00181154:"DSAverage Pulse Width",
        0x00181155:"CSRadiation Setting",
        0x00181156:"CSRectification Type",
        0x0018115A:"CSRadiation Mode",
        0x0018115E:"DSImage Area Dose Product",
        0x00181160:"SHFilter Type",
        0x00181161:"LOType of Filters",
        0x00181162:"DSIntensifier Size",
        0x00181164:"DSImager Pixel Spacing",
        0x00181166:"CSGrid",
        0x00181170:"ISGenerator Power",
        0x00181180:"SHCollimator/grid Name",
        0x00181181:"CSCollimator Type",
        0x00181182:"ISFocal Distance",
        0x00181183:"DSX Focus Center",
        0x00181184:"DSY Focus Center",
        0x00181190:"DSFocal Spot(s)",
        0x00181191:"CSAnode Target Material",
        0x001811A0:"DSBody Part Thickness",
        0x001811A2:"DSCompression Force",
        0x00181200:"DADate of Last Calibration",
        0x00181201:"TMTime of Last Calibration",
        0x00181210:"SHConvolution Kernel",
        0x00181242:"ISActual Frame Duration",
        0x00181243:"ISCount Rate",
        0x00181250:"SHReceiving Coil",
        0x00181251:"SHTransmitting Coil",
        0x00181260:"SHPlate Type",
        0x00181261:"LOPhosphor Type",
        0x00181300:"ISScan Velocity",
        0x00181301:"CSWhole Body Technique",
        0x00181302:"ISScan Length",
        0x00181310:"USAcquisition Matrix",
        0x00181312:"CSPhase Encoding Direction",
        0x00181314:"DSFlip Angle",
        0x00181315:"CSVariable Flip Angle Flag",
        0x00181316:"DSSAR",
        0x00181318:"DSdB/dt",
        0x00181400:"LOAcquisition Device Processing Description",
        0x00181401:"LOAcquisition Device Processing Code",
        0x00181402:"CSCassette Orientation",
        0x00181403:"CSCassette Size",
        0x00181404:"USExposures on Plate",
        0x00181405:"ISRelative X-ray Exposure",
        0x00181450:"CSColumn Angulation",
        0x00181500:"CSPositioner Motion",
        0x00181508:"CSPositioner Type",
        0x00181510:"DSPositioner Primary Angle",
        0x00181511:"DSPositioner Secondary Angle",
        0x00181520:"DSPositioner Primary Angle Increment",
        0x00181521:"DSPositioner Secondary Angle Increment",
        0x00181530:"DSDetector Primary Angle",
        0x00181531:"DSDetector Secondary Angle",
        0x00181600:"CSShutter Shape",
        0x00181602:"ISShutter Left Vertical Edge",
        0x00181604:"ISShutter Right Vertical Edge",
        0x00181606:"ISShutter Upper Horizontal Edge",
        0x00181608:"ISShutter Lower Horizontal Edge",
        0x00181610:"ISCenter of Circular Shutter",
        0x00181612:"ISRadius of Circular Shutter",
        0x00181620:"ISVertices of the Polygonal Shutter",
        0x00181700:"ISCollimator Shape",
        0x00181702:"ISCollimator Left Vertical Edge",
        0x00181704:"ISCollimator Right Vertical Edge",
        0x00181706:"ISCollimator Upper Horizontal Edge",
        0x00181708:"ISCollimator Lower Horizontal Edge",
        0x00181710:"ISCenter of Circular Collimator",
        0x00181712:"ISRadius of Circular Collimator",
        0x00181720:"ISVertices of the Polygonal Collimator",
        0x00185000:"SHOutput Power",
        0x00185010:"LOTransducer Data",
        0x00185012:"DSFocus Depth",
        0x00185020:"LOPreprocessing Function",
        0x00185021:"LOPostprocessing Function",
        0x00185022:"DSMechanical Index",
        0x00185024:"DSThermal Index",
        0x00185026:"DSCranial Thermal Index",
        0x00185027:"DSSoft Tissue Thermal Index",
        0x00185028:"DSSoft Tissue-focus Thermal Index",
        0x00185029:"DSSoft Tissue-surface Thermal Index",
        0x00185050:"ISDepth of Scan Field",
        0x00185100:"CSPatient Position",
        0x00185101:"CSView Position",
        0x00185104:"SQProjection Eponymous Name Code Sequence",
        0x00185210:"DSImage Transformation Matrix",
        0x00185212:"DSImage Translation Vector",
        0x00186000:"DSSensitivity",
        0x00186011:"SQSequence of Ultrasound Regions",
        0x00186012:"USRegion Spatial Format",
        0x00186014:"USRegion Data Type",
        0x00186016:"ULRegion Flags",
        0x00186018:"ULRegion Location Min X0",
        0x0018601A:"ULRegion Location Min Y0",
        0x0018601C:"ULRegion Location Max X1",
        0x0018601E:"ULRegion Location Max Y1",
        0x00186020:"SLReference Pixel X0",
        0x00186022:"SLReference Pixel Y0",
        0x00186024:"USPhysical Units X Direction",
        0x00186026:"USPhysical Units Y Direction",
        0x00181628:"FDReference Pixel Physical Value X",
        0x0018602A:"FDReference Pixel Physical Value Y",
        0x0018602C:"FDPhysical Delta X",
        0x0018602E:"FDPhysical Delta Y",
        0x00186030:"ULTransducer Frequency",
        0x00186031:"CSTransducer Type",
        0x00186032:"ULPulse Repetition Frequency",
        0x00186034:"FDDoppler Correction Angle",
        0x00186036:"FDSterring Angle",
        0x00186038:"ULDoppler Sample Volume X Position",
        0x0018603A:"ULDoppler Sample Volume Y Position",
        0x0018603C:"ULTM-Line Position X0",
        0x0018603E:"ULTM-Line Position Y0",
        0x00186040:"ULTM-Line Position X1",
        0x00186042:"ULTM-Line Position Y1",
        0x00186044:"USPixel Component Organization",
        0x00186046:"ULPixel Component Mask",
        0x00186048:"ULPixel Component Range Start",
        0x0018604A:"ULPixel Component Range Stop",
        0x0018604C:"USPixel Component Physical Units",
        0x0018604E:"USPixel Component Data Type",
        0x00186050:"ULNumber of Table Break Points",
        0x00186052:"ULTable of X Break Points",
        0x00186054:"FDTable of Y Break Points",
        0x00186056:"ULNumber of Table Entries",
        0x00186058:"ULTable of Pixel Values",
        0x0018605A:"ULTable of Parameter Values",
        0x00187000:"CSDetector Conditions Nominal Flag",
        0x00187001:"DSDetector Temperature",
        0x00187004:"CSDetector Type",
        0x00187005:"CSDetector Configuration",
        0x00187006:"LTDetector Description",
        0x00187008:"LTDetector Mode",
        0x0018700A:"SHDetector ID",
        0x0018700C:"DADate of Last Detector Calibration",
        0x0018700E:"TMTime of Last Detector Calibration",
        0x00187010:"ISExposures on Detector Since Last Calibration",
        0x00187011:"ISExposures on Detector Since Manufactured",
        0x00187012:"DSDetector Time Since Last Exposure",
        0x00187014:"DSDetector Active Time",
        0x00187016:"DSDetector Activation Offset From Exposure",
        0x0018701A:"DSDetector Binning",
        0x00187020:"DSDetector Element Physical Size",
        0x00187022:"DSDetector Element Spacing",
        0x00187024:"CSDetector Active Shape",
        0x00187026:"DSDetector Active Dimension(s)",
        0x00187028:"DSDetector Active Origin",
        0x00187030:"DSField of View Origin",
        0x00187032:"DSField of View Rotation",
        0x00187034:"CSField of View Horizontal Flip",
        0x00187040:"LTGrid Absorbing Material",
        0x00187041:"LTGrid Spacing Material",
        0x00187042:"DSGrid Thickness",
        0x00187044:"DSGrid Pitch",
        0x00187046:"ISGrid Aspect Ratio",
        0x00187048:"DSGrid Period",
        0x0018704C:"DSGrid Focal Distance",
        0x00187050:"LTFilter Material LT",
        0x00187052:"DSFilter Thickness Minimum",
        0x00187054:"DSFilter Thickness Maximum",
        0x00187060:"CSExposure Control Mode",
        0x00187062:"LTExposure Control Mode Description",
        0x00187064:"CSExposure Status",
        0x00187065:"DSPhototimer Setting",
        0x0020000D:"UIStudy Instance UID",
        0x0020000E:"UISeries Instance UID",
        0x00200010:"SHStudy ID",
        0x00200011:"ISSeries Number",
        0x00200012:"ISAcquisition Number",
        0x00200013:"ISImage Number",
        0x00200014:"ISIsotope Number",
        0x00200015:"ISPhase Number",
        0x00200016:"ISInterval Number",
        0x00200017:"ISTime Slot Number",
        0x00200018:"ISAngle Number",
        0x00200020:"CSPatient Orientation",
        0x00200022:"USOverlay Number",
        0x00200024:"USCurve Number",
        0x00200030:"DSImage Position",
        0x00200032:"DSImage Position (Patient)",
        0x00200037:"DSImage Orientation (Patient)",
        0x00200050:"DSLocation",
        0x00200052:"UIFrame of Reference UID",
        0x00200060:"CSLaterality",
        0x00200070:"LOImage Geometry Type",
        0x00200080:"UIMasking Image UID",
        0x00200100:"ISTemporal Position Identifier",
        0x00200105:"ISNumber of Temporal Positions",
        0x00200110:"DSTemporal Resolution",
        0x00201000:"ISSeries in Study",
        0x00201002:"ISImages in Acquisition",
        0x00201004:"ISAcquisition in Study",
        0x00201040:"LOPosition Reference Indicator",
        0x00201041:"DSSlice Location",
        0x00201070:"ISOther Study Numbers",
        0x00201200:"ISNumber of Patient Related Studies",
        0x00201202:"ISNumber of Patient Related Series",
        0x00201204:"ISNumber of Patient Related Images",
        0x00201206:"ISNumber of Study Related Series",
        0x00201208:"ISNumber of Study Related Images",
        0x00204000:"LTImage Comments",
        0x00280002:"USSamples per Pixel",
        0x00280004:"CSPhotometric Interpretation",
        0x00280006:"USPlanar Configuration",
        0x00280008:"ISNumber of Frames",
        0x00280009:"ATFrame Increment Pointer",
        0x00280010:"USRows",
        0x00280011:"USColumns",
        0x00280030:"DSPixel Spacing",
        0x00280031:"DSZoom Factor",
        0x00280032:"DSZoom Center",
        0x00280034:"ISPixel Aspect Ratio",
        0x00280051:"CSCorrected Image",
        0x00280100:"USBits Allocated",
        0x00280101:"USBits Stored",
        0x00280102:"USHigh Bit",
        0x00280103:"USPixel Representation",
        0x00280106:"USSmallest Image Pixel Value",
        0x00280107:"USLargest Image Pixel Value",
        0x00280108:"USSmallest Pixel Value in Series",
        0x00280109:"USLargest Pixel Value in Series",
        0x00280120:"USPixel Padding Value",
        0x00280300:"CSQuality Control Image",
        0x00280301:"CSBurned In Annotation",
        0x00281040:"CSPixel Intensity Relationship",
        0x00281041:"SSPixel Intensity Relationship Sign",
        0x00281050:"DSWindow Center",
        0x00281051:"DSWindow Width",
        0x00281052:"DSRescale Intercept",
        0x00281053:"DSRescale Slope",
        0x00281054:"LORescale Type",
        0x00281055:"LOWindow Center & Width Explanation",
        0x00281101:"USRed Palette Color Lookup Table Descriptor",
        0x00281102:"USGreen Palette Color Lookup Table Descriptor",
        0x00281103:"USBlue Palette Color Lookup Table Descriptor",
        0x00281201:"USRed Palette Color Lookup Table Data",
        0x00281202:"USGreen Palette Color Lookup Table Data",
        0x00281203:"USBlue Palette Color Lookup Table Data",
        0x00282110:"CSLossy Image Compression",
        0x00283000:"SQModality LUT Sequence",
        0x00283002:"USLUT Descriptor",
        0x00283003:"LOLUT Explanation",
        0x00283004:"LOMadality LUT Type",
        0x00283006:"USLUT Data",
        0x00283010:"SQVOI LUT Sequence",
        0x30020011:"DSImage Plane Pixel Spacing",
        0x30020022:"DSRadiation Machine SAD",
        0x30020026:"DSRT IMAGE SID",
        0x0032000A:"CSStudy Status ID",
        0x0032000C:"CSStudy Priority ID",
        0x00320012:"LOStudy ID Issuer",
        0x00320032:"DAStudy Verified Date",
        0x00320033:"TMStudy Verified Time",
        0x00320034:"DAStudy Read Date",
        0x00320035:"TMStudy Read Time",
        0x00321000:"DAScheduled Study Start Date",
        0x00321001:"TMScheduled Study Start Time",
        0x00321010:"DAScheduled Study Stop Date",
        0x00321011:"TMScheduled Study Stop Time",
        0x00321020:"LOScheduled Study Location",
        0x00321021:"AEScheduled Study Location AE Title(s)",
        0x00321030:"LOReason for Study",
        0x00321032:"PNRequesting Physician",
        0x00321033:"LORequesting Service",
        0x00321040:"DAStudy Arrival Date",
        0x00321041:"TMStudy Arrival Time",
        0x00321050:"DAStudy Completion Date",
        0x00321051:"TMStudy Completion Time",
        0x00321055:"CSStudy Component Status ID",
        0x00321060:"LORequested Procedure Description",
        0x00321064:"SQRequested Procedure Code Sequence",
        0x00321070:"LORequested Contrast Agent",
        0x00324000:"LTStudy Comments",
        0x00400001:"AEScheduled Station AE Title",
        0x00400002:"DAScheduled Procedure Step Start Date",
        0x00400003:"TMScheduled Procedure Step Start Time",
        0x00400004:"DAScheduled Procedure Step End Date",
        0x00400005:"TMScheduled Procedure Step End Time",
        0x00400006:"PNScheduled Performing Physician's Name",
        0x00400007:"LOScheduled Procedure Step Description",
        0x00400008:"SQScheduled Action Item Code Sequence",
        0x00400009:"SHScheduled Procedure Step ID",
        0x00400010:"SHScheduled Station Name",
        0x00400011:"SHScheduled Procedure Step Location",
        0x00400012:"LOPre-Medication",
        0x00400020:"CSScheduled Procedure Step Status",
        0x00400100:"SQScheduled Procedure Step Sequence",
        0x00400220:"SQReferenced Standalone SOP Instance Sequence",
        0x00400241:"AEPerformed Station AE Title",
        0x00400242:"SHPerformed Station Name",
        0x00400243:"SHPerformed Location",
        0x00400244:"DAPerformed Procedure Step Start Date",
        0x00400245:"TMPerformed Procedure Step Start Time",
        0x00400250:"DAPerformed Procedure Step End Date",
        0x00400251:"TMPerformed Procedure Step End Time",
        0x00400252:"CSPerformed Procedure Step Status",
        0x00400253:"SHPerformed Procedure Step ID",
        0x00400254:"LOPerformed Procedure Step Description",
        0x00400255:"LOPerformed Procedure Type Description",
        0x00400260:"SQPerformed Action Item Sequence",
        0x00400270:"SQScheduled Step Attributes Sequence",
        0x00400275:"SQRequest Attributes Sequence",
        0x00400280:"STComments on the Performed Procedure Steps",
        0x00400293:"SQQuantity Sequence",
        0x00400294:"DSQuantity",
        0x00400295:"SQMeasuring Units Sequence",
        0x00400296:"SQBilling Item Sequence",
        0x00400300:"USTotal Time of Fluoroscopy",
        0x00400301:"USTotal Number of Exposures",
        0x00400302:"USEntrance Dose",
        0x00400303:"USExposed Area",
        0x00400306:"DSDistance Source to Entrance",
        0x00400307:"DSDistance Source to Support",
        0x00400310:"STComments on Radiation Dose",
        0x00400312:"DSX-Ray Output",
        0x00400314:"DSHalf Value Layer",
        0x00400316:"DSOrgan Dose",
        0x00400318:"CSOrgan Exposed",
        0x00400320:"SQBilling Procedure Step Sequence",
        0x00400321:"SQFilm Consumption Sequence",
        0x00400324:"SQBilling Supplies and Devices Sequence",
        0x00400330:"SQReferenced Procedure Step Sequence",
        0x00400340:"SQPerformed Series Sequence",
        0x00400400:"LTComments on the Scheduled Procedure Step",
        0x0040050A:"LOSpecimen Accession Number",
        0x00400550:"SQSpecimen Sequence",
        0x00400551:"LOSpecimen Identifier",
        0x0040059A:"SQSpecimen Type Code Sequence",
        0x00400555:"SQAcquisition Context Sequence",
        0x00400556:"STAcquisition Context Description",
        0x004006FA:"LOSlide Identifier",
        0x0040071A:"SQImage Center Point Coordinates Sequence",
        0x0040072A:"DSX offset in Slide Coordinate System",
        0x0040073A:"DSY offset in Slide Coordinate System",
        0x0040074A:"DSZ offset in Slide Coordinate System",
        0x004008D8:"SQPixel Spacing Sequence",
        0x004008DA:"SQCoordinate System Axis Code Sequence",
        0x004008EA:"SQMeasurement Units Code Sequence",
        0x00401001:"SHRequested Procedure ID",
        0x00401002:"LOReason for the Requested Procedure",
        0x00401003:"SHRequested Procedure Priority",
        0x00401004:"LOPatient Transport Arrangements",
        0x00401005:"LORequested Procedure Location",
        0x00401006:" 1Placer Order Number / Procedure S",
        0x00401007:" 1Filler Order Number / Procedure S",
        0x00401008:"LOConfidentiality Code",
        0x00401009:"SHReporting Priority",
        0x00401010:"PNNames of Intended Recipients of Results",
        0x00401400:"LTRequested Procedure Comments",
        0x00402001:"LOReason for the Imaging Service Request",
        0x00402004:"DAIssue Date of Imaging Service Request",
        0x00402005:"TMIssue Time of Imaging Service Request",
        0x00402006:" 1Placer Order Number / Imaging Service Request S",
        0x00402007:" 1Filler Order Number / Imaging Service Request S",
        0x00402008:"PNOrder Entered By",
        0x00402009:"SHOrder Enterers Location",
        0x00402010:"SHOrder Callback Phone Number",
        0x00402016:"LOPlacer Order Number / Imaging Service Request",
        0x00402017:"LOFiller Order Number / Imaging Service Request",
        0x00402400:"LTImaging Service Request Comments",
        0x00403001:"LOConfidentiality Constraint on Patient Data Description",
        0x00408302:"DSEntrance Dose in mGy",
        0x0040A010:"CSRelationship Type",
        0x0040A027:"LOVerifying Organization",
        0x0040A030:"DTVerification DateTime",
        0x0040A032:"DTObservation DateTime",
        0x0040A040:"CSValue Type",
        0x0040A043:"SQConcept-name Code Sequence",
        0x0040A050:"CSContinuity Of Content",
        0x0040A073:"SQVerifying Observer Sequence",
        0x0040A075:"PNVerifying Observer Name",
        0x0040A088:"SQVerifying Observer Identification Code Sequence",
        0x0040A0B0:"USReferenced Waveform Channels",
        0x0040A120:"DTDateTime",
        0x0040A121:"DADate",
        0x0040A122:"TMTime",
        0x0040A123:"PNPerson Name",
        0x0040A124:"UIUID",
        0x0040A130:"CSTemporal Range Type",
        0x0040A132:"ULReferenced Sample Positions",
        0x0040A136:"USReferenced Frame Numbers",
        0x0040A138:"DSReferenced Time Offsets",
        0x0040A13A:"DTReferenced Datetime",
        0x0040A160:"UTText Value",
        0x0040A168:"SQConcept Code Sequence",
        0x0040A180:"USAnnotation Group Number",
        0x0040A195:"SQModifier Code Sequence",
        0x0040A300:"SQMeasured Value Sequence",
        0x0040A30A:"DSNumeric Value",
        0x0040A360:"SQPredecessor Documents Sequence",
        0x0040A370:"SQReferenced Request Sequence",
        0x0040A372:"SQPerformed Procedure Code Sequence",
        0x0040A375:"SQCurrent Requested Procedure Evidence Sequence",
        0x0040A385:"SQPertinent Other Evidence Sequence",
        0x0040A491:"CSCompletion Flag",
        0x0040A492:"LOCompletion Flag Description",
        0x0040A493:"CSVerification Flag",
        0x0040A504:"SQContent Template Sequence",
        0x0040A525:"SQIdentical Documents Sequence",
        0x0040A730:"SQContent Sequence",
        0x0040B020:"SQAnnotation Sequence",
        0x0040DB00:"CSTemplate Identifier",
        0x0040DB06:"DTTemplate Version",
        0x0040DB07:"DTTemplate Local Version",
        0x0040DB0B:"CSTemplate Extension Flag",
        0x0040DB0C:"UITemplate Extension Organization UID",
        0x0040DB0D:"UITemplate Extension Creator UID",
        0x0040DB73:"ULReferenced Content Item Identifier",
        0x00540011:"USNumber of Energy Windows",
        0x00540012:"SQEnergy Window Information Sequence",
        0x00540013:"SQEnergy Window Range Sequence",
        0x00540014:"DSEnergy Window Lower Limit",
        0x00540015:"DSEnergy Window Upper Limit",
        0x00540016:"SQRadiopharmaceutical Information Sequence",
        0x00540017:"ISResidual Syringe Counts",
        0x00540018:"SHEnergy Window Name",
        0x00540020:"USDetector Vector",
        0x00540021:"USNumber of Detectors",
        0x00540022:"SQDetector Information Sequence",
        0x00540030:"USPhase Vector",
        0x00540031:"USNumber of Phases",
        0x00540032:"SQPhase Information Sequence",
        0x00540033:"USNumber of Frames in Phase",
        0x00540036:"ISPhase Delay",
        0x00540038:"ISPause Between Frames",
        0x00540039:"CSPhase Description",
        0x00540050:"USRotation Vector",
        0x00540051:"USNumber of Rotations",
        0x00540052:"SQRotation Information Sequence",
        0x00540053:"USNumber of Frames in Rotation",
        0x00540060:"USR-R Interval Vector",
        0x00540061:"USNumber of R-R Intervals",
        0x00540062:"SQGated Information Sequence",
        0x00540063:"SQData Information Sequence",
        0x00540070:"USTime Slot Vector",
        0x00540071:"USNumber of Time Slots",
        0x00540072:"SQTime Slot Information Sequence",
        0x00540073:"DSTime Slot Time",
        0x00540080:"USSlice Vector",
        0x00540081:"USNumber of Slices",
        0x00540090:"USAngular View Vector",
        0x00540100:"USTime Slice Vector",
        0x00540101:"USNumber of Time Slices",
        0x00540200:"DSStart Angle",
        0x00540202:"CSType of Detector Motion",
        0x00540210:"ISTrigger Vector",
        0x00540211:"USNumber of Triggers in Phase",
        0x00540220:"SQView Code Sequence",
        0x00540222:"SQView Modifier Code Sequence",
        0x00540300:"SQRadionuclide Code Sequence",
        0x00540302:"SQAdministration Route Code Sequence",
        0x00540304:"SQRadiopharmaceutical Code Sequence",
        0x00540306:"SQCalibration Data Sequence",
        0x00540308:"USEnergy Window Number",
        0x00540400:"SHImage ID",
        0x00540410:"SQPatient Orientation Code Sequence",
        0x00540412:"SQPatient Orientation Modifier Code Sequence",
        0x00540414:"SQPatient Gantry Relationship Code Sequence",
        0x00540500:"CSSlice Progression Direction",
        0x00541000:"CSSeries Type",
        0x00541001:"CSUnits",
        0x00541002:"CSCounts Source",
        0x00541004:"CSReprojection Method",
        0x00541100:"CSRandoms Correction Method",
        0x00541101:"LOAttenuation Correction Method",
        0x00541102:"CSDecay Correction",
        0x00541103:"LOReconstruction Method",
        0x00541104:"LODetector Lines of Response Used",
        0x00541105:"LOScatter Correction Method",
        0x00541200:"DSAxial Acceptance",
        0x00541201:"ISAxial Mash",
        0x00541202:"ISTransverse Mash",
        0x00541203:"DSDetector Element Size",
        0x00541210:"DSCoincidence Window Width",
        0x00541220:"CSSecondary Counts Type",
        0x00541300:"DSFrame Reference Time",
        0x00541310:"ISPrimary (Prompts) Counts Accumulated",
        0x00541311:"ISSecondary Counts Accumulated",
        0x00541320:"DSSlice Sensitivity Factor",
        0x00541321:"DSDecay Factor",
        0x00541322:"DSDose Calibration Factor",
        0x00541323:"DSScatter Fraction Factor",
        0x00541324:"DSDead Time Factor",
        0x00541330:"USImage Index",
        0x00541400:"CSCounts Included",
        0x00541401:"CSDead Time Correction Flag",
        0x30020002:"SHRT Image Label",
        0x30020003:"LORT Image Name",
        0x30020004:"STRT Image Description",
        0x3002000A:"CSReported Values Origin",
        0x3002000C:"CSRT Image Plane",
        0x3002000D:"DSX-Ray Image Receptor Translation",
        0x3002000E:"DSX-Ray Image Receptor Angle",
        0x30020011:"DSImage Plane Pixel Spacing",
        0x30020012:"DSRT Image Position",
        0x30020020:"SHRadiation Machine Name",
        0x30020022:"DSRadiation Machine SAD",
        0x30020026:"DSRT Image SID",
        0x30020029:"ISFraction Number",
        0x30020030:"SQExposure Sequence",
        0x30020032:"DSMeterset Exposure",
        0x300A011E:"DSGantry Angle",
        0x300A0120:"DSBeam Limiting Device Angle",
        0x300A0122:"DSPatient Support Angle",
        0x300A0128:"DSTable Top Vertical Position",
        0x300A0129:"DSTable Top Longitudinal Position",
        0x300A012A:"DSTable Top Lateral Position",
        0x300A00B3:"CSPrimary Dosimeter Unit",
        0x300A00F0:"ISNumber of Blocks",
        0x300C0006:"ISReferenced Beam Number",
        0x300C0008:"DSStart Cumulative Meterset Weight",
        0x300C0022:"ISReferenced Fraction Group Number",
        0x7FE00010:"OXPixel Data",
        0xFFFEE000:"DLItem",
        0xFFFEE00D:"DLItem Delimitation Item",
        0xFFFEE0DD:"DLSequence Delimitation Item"
    }
'''
dd = DicomDecoder("","test.dcm")
f = open("test.txt","w")
for pixel in dd.pixels16:
    f.write(str(pixel) + "\n")
f.close()
'''
