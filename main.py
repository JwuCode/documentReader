import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import pytesseract

#helper functions
def removeImgBackground(img):

    print("Background Removed")

def processImage(img):
    grayImg = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

def displayImages(images):
    for i in range(len(images)):
        plt.subplot(121 + i),plt.imshow(images[i])
    plt.show()

def drawBoxes(img):
    image = img
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    cnts = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        x,y,w,h = cv.boundingRect(c)
        cv.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)
    displayImages([image])

#image = cv.imread('./testingImages/johnTest.jpeg')
#image = cv.imread('./testingImages/test.jpg')
#image = cv.imread('./testingImages/stocks.jpeg')
image = cv.imread('./testingImages/ECETB.png')


gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
cnts = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    x,y,w,h = cv.boundingRect(c)
    cv.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)

#dst = cv.GaussianBlur(image,(5,5),0)
#image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
#dst = cv.fastNlMeansDenoisingColored(image,None,10,10,7,21)
drawBoxes(image)
#text = pytesseract.image_to_string(dst)
#print(text)