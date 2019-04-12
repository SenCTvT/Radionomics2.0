from FlaskApp.controller.Conversions import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np
import io
import PIL


class Segment:

    def __init__(self, dd, coordList):
        self.dd = Conversions(dd)
        self.coordList = coordList
        self.npArray = self.dd.data

    def drawBox(self):
        self.codList = []
        for ls in self.coordList:
            coord = ls[0]
            x = coord[0]
            y = coord[1]
            coord = ls[1]
            h = coord[0]
            w = coord[1]
            coord = ls[2]
            r = coord[0]
            g = coord[1]
            b = coord[2]
            points= ls[3]
            #print points
            self.draw(x, y, h, w, r, g, b, points)
            pt = (x, y, h, w, r, g, b)
            self.codList.append(pt)

        img = Image.fromarray(self.npArray, 'RGB')
        draw = ImageDraw.Draw(img)
        fonts_path = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
        font = ImageFont.truetype(fonts_path, 8)
        k = 0
        for (t,p,h,w,r,g,b) in self.codList:
            x = int(w / 3) + t
            y = int(h / 3) + p
            draw.text((x, y),str(k + 1),(r,g,b),font=font)
            k = k + 1
        basewidth = 500
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='JPEG')
        #img.show()
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    def draw(self, x, y, h, w, r, g, b, points):
        x1 = x
        x2 = x1 + w
        y1 = y
        y2 = y1 + h
        for i in range(x1,x2+1):
            self.npArray[y1,i] = [r,g,b]

        for i in range(y1,y2+1):
            self.npArray[i,x2] = [r,g,b]

        for i in range(x1, x2+1):
            self.npArray[y2, i] = [r,g,b]

        for i in range(y1,y2+1):
            self.npArray[i,x1] = [r,g,b]


	for ls in points:
            x = ls[0]
            y = ls[1]
            n = self.npArray[y,x]
            pix = n[0]
            r = self.dd.palette[pix][0]
            g = self.dd.palette[pix][1]
            b = self.dd.palette[pix][2]
            self.npArray[y, x] = [r,g,b]

#d = Segment('i105846.dcm',[[(10,10),(50,50),(150,100,170),[(10,11),(10,12),(11,11),(11,12)]]])
#d.drawBox()
