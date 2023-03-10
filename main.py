import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import pytesseract
import gtts
from playsound import playsound
from pdf2image import convert_from_path
import os
from sort_funct import *
import re


#use the regex date pattern for date template matching
date_pattern = '/(0[1-9]|1[012])[- \/.](0[1-9]|[12][0-9]|3[01])[- \/.]((?:19|20)\d\d)/'

#helper functions
def displayImages(images):
    for i in range(len(images)):
        plt.subplot(121 + i),plt.imshow(images[i])
    plt.show()

def textAudio():
    try:
        textToRead = open("imageText.txt", "r").read().replace("\n", " ")
        speech = gtts.gTTS(text = str(textToRead),lang='en',slow = False)
        speech.save("scannedFile.mp3")
        #playsound("hello.mp3")
    except:
        print("No File Read")


def drawBoxes(img):
    #Converts input to grayscale image, then applies thresholding to convert to binary image
    image = img
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    #nldenoise = cv.fastNlMeansDenoising(gray, None, 20, 7, 21) <- not using at the moment
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
    dilate = cv.dilate(thresh, kernel, iterations=5)
    cnts = cv.findContours(dilate, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        x,y,w,h = cv.boundingRect(c)
        cropped_image = image[y:y+h, x:x+w]
        print(pytesseract.image_to_string(cropped_image))
        cv.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)
    displayImages([image, dilate])

def createFile(text):
    tFile = open("imageText.txt", "w")
    tFile.write(text)
    tFile.close()   

def craProcessing(image):
    temp = image
    gray = cv.cvtColor(temp,cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    # Remove horizontal lines
    horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (15,1))
    remove_horizontal = cv.morphologyEx(thresh, cv.MORPH_OPEN, horizontal_kernel, iterations=7)
    cnts = cv.findContours(remove_horizontal, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv.drawContours(temp, [c], -1, (255,255,255), 5)

    # Remove vertical lines
    vertical_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1,5))
    remove_vertical = cv.morphologyEx(thresh, cv.MORPH_OPEN, vertical_kernel, iterations=7)
    cnts = cv.findContours(remove_vertical, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv.drawContours(temp, [c], -1, (255,255,255), 5)
    return temp

def boxcraProcessing(image):
    dateFound = False
    temp = image
    boxver = image
    gray = cv.cvtColor(temp,cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    verti_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 8))
    hori_kernel = cv.getStructuringElement(cv.MORPH_RECT, (15, 1))
    replacement_verti = cv.getStructuringElement(cv.MORPH_RECT, (1, 9))
    replacement_hori = cv.getStructuringElement(cv.MORPH_RECT, (16, 1))
    img_temp1 = cv.erode(thresh, verti_kernel, iterations=3)
    vertical_lines_img = cv.dilate(img_temp1, replacement_verti, iterations=3)
    cv.imwrite("vertical_lines.jpg",vertical_lines_img)
    img_temp2 = cv.erode(thresh, hori_kernel, iterations=3)
    horizontal_lines_img = cv.dilate(img_temp2, replacement_hori, iterations=3)
    cv.imwrite("horizontal_lines.jpg",horizontal_lines_img)
    alpha = 0.5
    beta = 1.0 - alpha
    # Combine images
    img_final_bin = cv.addWeighted(vertical_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    cv.imwrite("img_final_bin.jpg",img_final_bin)
    contours = cv.findContours(img_final_bin, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    contours = sort_contours(contours, method="top-to-bottom")
    tFile = open("imageText.txt", "w")
    img_final_bin = cv2.cvtColor(img_final_bin,cv2.COLOR_GRAY2RGB)

    for c in range(len(contours)):
        x,y,w,h = cv.boundingRect(contours[c])

        #used cv rectangle to draw rectangles around scanned areas
        cv.rectangle(boxver, (x, y), (x + w, y + h), (36,255,12), 2)  
        cropped_image = temp[y:y+h, x:x+w]
        sectionText = pytesseract.image_to_string(cropped_image)
        if (sectionText.find('/') != -1) and dateFound == False:
            tFile.write("Year/Annee: "+ sectionText[sectionText.find('/') - 2: sectionText.find('/') + 8]+ "\n")
            dateFound = True

        if ('Actual amount of eligible dividends' in sectionText) and 'Ann??e' not in sectionText:
            sectionText = sectionText.replace('24', '', 1)
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace('Actualamountofeligibledividends', '')
            sectionText = sectionText.replace('Montantr??eldesdividendesd??termin??s', '')
            tFile.write("Actual amount of eligible dividends / Montant r??el des dividendes d??termin??s: "+ sectionText + '\n')
        
        if ('Taxable amount of eligible dividends' in sectionText) and ('Ann??e' not in sectionText) and ('Box' not in sectionText):
            sectionText = sectionText.replace('25', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('i', '')
            sectionText = sectionText.replace('Taxableamountofelgbledvdends', '')
            sectionText = sectionText.replace("Montantmposabledesdvdendes???d??termn??s", '')
            tFile.write("Taxable amount of eligible dividends / Montant imposable des dividendes d??termin??s: "+ sectionText + '\n')

        if ('Dividend tax credit for eligible' in sectionText) and 'Ann??e' not in sectionText:
            sectionText = sectionText.replace('26', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('Dividendtaxcreditforeligibledividends', '')
            sectionText = sectionText.replace('Cr??ditdimp??tpourdividendesd??termin??s', '')
            tFile.write("Dividend tax credit for eligible dividends / Cr??dit dimp??t pour dividendes d??termin??s: "+ sectionText + '\n')
        
        if ('Interest from Canadian sources' in sectionText) and 'Ann??e' not in sectionText:
            sectionText = sectionText.replace('13]', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('.', '', 1)
            sectionText = sectionText.replace('InterestfromCanadiansources', '')
            sectionText = sectionText.replace('Int??r??tsdesourcecanadienne', '')
            tFile.write("Interest from Canadian sources / Int??r??ts de Source Canadienne: "+ sectionText + '\n')
        
        if ('Capital gains dividends' in sectionText) and 'Ann??e' not in sectionText:
            sectionText = sectionText.replace('18', '', 1) 
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('Capitalgainsdividends', '')
            sectionText = sectionText.replace('Dividendessurgainsencapital', '')
            tFile.write("Capital gains dividends / Dividendes sur gains en capital: "+ sectionText + '\n')

        if ('Actual amount of dividends' in sectionText) and 'Ann??e' not in sectionText:
            sectionText = sectionText.replace('10', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('Actualamountofdividendsotherthaneligibledividends', '')
            sectionText = sectionText.replace('Montantr??eldesdividendesautresquedesdividendesd??termin??s', '')
            tFile.write("Actual amount of dividends other than eligible dividends / Montant r??el des dividendes autres que des dividendes d??termin??s: "+ sectionText + '\n')
        
        if ('Taxable amount of dividends' in sectionText) and ('Ann??e' not in sectionText) and ('other than eligible dividends' in sectionText):
            sectionText = sectionText.replace('1', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('W', '')
            sectionText = sectionText.replace('Taxableamountofdividendsotherthaneligibledividends', '')
            sectionText = sectionText.replace('Montantimposabledesdividendesautresquedesdividendesd??termin??s', '')
            tFile.write("Taxable amount of dividends other than eligible dividends / Montant imposable des dividendes autres que des dividendes d??termin??s: "+ sectionText + '\n')

        if ('Cr??dit dimp??t pour dividendes' in sectionText) and ('Ann??e' not in sectionText) and ('autres que des dividendes d??termin??s' in sectionText):
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('12|???Drvidendtaxcreditfordividends:otherthaneligibledividends', '')
            sectionText = sectionText.replace('4D|???Ulvicandtexcredittordividends:otherthaneligibledividends', '')
            sectionText = sectionText.replace('4p|???Drvicandtexcracktorcividancs:otherthaneligibledividends', '')
            sectionText = sectionText.replace('12|???PNidendtaxcreckforcividencs:otherthaneligibledividends', '')
            sectionText = sectionText.replace('Cr??ditdimp??tpourdividendesautresquedesdividendesd??termin??s', '')
            tFile.write("Dividend tax credit for dividends other than eligible dividends / Cr??dit dimp??t pour dividendes autres que des dividendes d??termin??s: "+ sectionText + '\n')
        
        if ('Report Code' in sectionText) and ('Ann??e' not in sectionText):
            sectionText = sectionText.replace('21]', '', 1)
            sectionText = sectionText.replace('21|', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('ReportCode', '')
            sectionText = sectionText.replace('Codedufeuillet', '')
            tFile.write("Report Code / Code du Feuillet: "+ sectionText + '\n')
        
        if ('Recipient identification number' in sectionText) and ('Ann??e' not in sectionText):
            sectionText = sectionText.replace('22]', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('Recipientidentificationnumber', '')
            sectionText = sectionText.replace("Num??rod'identificationdub??n??ficiaire", '')
            tFile.write("Recipient identification number / Num??ro d'identification du b??n??ficiaire: "+ sectionText + '\n')

        if ('Recipient type' in sectionText) and ('Ann??e' not in sectionText):
            sectionText = sectionText.replace('23', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('|Recipienttype', '')
            sectionText = sectionText.replace('Typedeb??n??ficiaire', '')
            sectionText = sectionText.replace('???', '')
            tFile.write("Recipient Type / Type de b??n??ficiaire: "+ sectionText + '\n')
        
        if ('Other information' in sectionText) and ('Autres renseignements' in sectionText) and ('Ann??e' not in sectionText):
            
            for i in range(6, 0, -1):
                xt,yt,wt,ht = cv.boundingRect(contours[c+6 + i])
                tempBox = temp[yt:yt+ht, xt:xt+wt]
                boxText = pytesseract.image_to_string(tempBox)
                boxText = boxText.strip()
                boxText = boxText.strip('\n')
                if (i % 2 == 0): 
                    tFile.write("Box / Case: "+ boxText + '\n')
                else:
                    tFile.write("Amount / Montant: "+ boxText + '\n')
                    
        if ("Recipient's name (last name first) and address ??? Nom, pr??nom et adresse du b??n??ficiaire" in sectionText) and ("Payer's name and address ??? Nom et adresse du payeur" not in sectionText) and ('Ann??e' not in sectionText):
            xt,yt,wt,ht = cv.boundingRect(contours[c+1])
            tempBox = temp[yt:yt+ht, xt:xt+wt]
            boxText = pytesseract.image_to_string(tempBox)
            boxText = boxText.strip()
            boxText = boxText.replace('\n', ' ')
            tFile.write("Recipient's name (last name first) and address / Nom, pr??nom et adresse du b??n??ficiaire: "+ boxText + '\n')
            
            xt,yt,wt,ht = cv.boundingRect(contours[c+2])
            tempBox = temp[yt:yt+ht, xt:xt+wt]
            boxText = pytesseract.image_to_string(tempBox)
            boxText = boxText.strip()
            boxText = boxText.replace('\n', ' ')
            tFile.write("Payer's name and address / Nom et adresse du payeur: "+ boxText + '\n')
            
            xt,yt,wt,ht = cv.boundingRect(contours[c+9])
            tempBox = temp[yt:yt+ht, xt:xt+wt]
            boxText = pytesseract.image_to_string(tempBox)
            boxText = boxText.strip()
            boxText = boxText.replace('\n', ' ')
            tFile.write("Foreign Currency / Devises ??trang??res: "+ boxText + '\n')

            xt,yt,wt,ht = cv.boundingRect(contours[c+6])
            tempBox = temp[yt:yt+ht, xt:xt+wt]
            boxText = pytesseract.image_to_string(tempBox)
            boxText = boxText.strip()
            boxText = boxText.replace('\n', ' ')
            tFile.write("Transit / Succursale: "+ boxText + '\n')

            xt,yt,wt,ht = cv.boundingRect(contours[c+3])
            tempBox = temp[yt:yt+ht, xt:xt+wt]
            boxText = pytesseract.image_to_string(tempBox)
            boxText = boxText.strip()
            boxText = boxText.replace('\n', ' ')
            tFile.write("Recipient account number / Num??ro de compte du b??n??ficiaire: "+ boxText + '\n')
            tFile.write("\n")

    tFile.close()  
    cv.imwrite('result.png', boxver)

def checkFile(filePath):
    if filePath.lower().endswith(('.pdf')):
        if not os.path.exists('./PDFoutput'):
            os.makedirs('./PDFoutput')
        
        for f in os.listdir('./PDFoutput'):
            os.remove(os.path.join('./PDFoutput', f))

        images = convert_from_path(filePath, output_folder='./PDFoutput') 
        for i in range(len(images)):
            images[i].save('./PDFoutput/page'+ str(i) +'.jpg', 'JPEG')
        return len(images)
    else: 
        return filePath

#driver code
def readFile():
    checkFile('./testingPDF/t5-22b.pdf')
    image = cv.imread('./PDFoutput/page0.jpg')
    boxcraProcessing(image)
    textAudio()

readFile()
