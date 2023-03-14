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


#use the regex date pattern for template matching
date_pattern = '/(0[1-9]|1[012])[- \/.](0[1-9]|[12][0-9]|3[01])[- \/.]((?:19|20)\d\d)/'

#helper functions
def displayImages(images):
    for i in range(len(images)):
        plt.subplot(121 + i),plt.imshow(images[i])
    plt.show()

def textAudio():
    try:
        textToRead = open("imageText.txt", "r")
        readResult = gtts.gTTS(textToRead)
        readResult.save("scannedFile.mp3")
        #playsound("hello.mp3")
    except:
        print("No File Read")


def drawBoxes(img):
    #Converts input to grayscale image, then applies nonlocal means algo to remove noise
    image = img
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    #nldenoise = cv.fastNlMeansDenoising(gray, None, 20, 7, 21) 
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
    gray = cv.cvtColor(temp,cv.COLOR_BGR2GRAY)
    thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    # Defining a kernel length
    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    verti_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 8))
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv.getStructuringElement(cv.MORPH_RECT, (15, 1))
    # A kernel of (3 X 3) ones.
    replacement_verti = cv.getStructuringElement(cv.MORPH_RECT, (1, 9))
    replacement_hori = cv.getStructuringElement(cv.MORPH_RECT, (16, 1))
    # Morphological operation to detect vertical lines from an image
    img_temp1 = cv.erode(thresh, verti_kernel, iterations=3)
    vertical_lines_img = cv.dilate(img_temp1, replacement_verti, iterations=3)
    cv.imwrite("vertical_lines.jpg",vertical_lines_img)
    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv.erode(thresh, hori_kernel, iterations=3)
    horizontal_lines_img = cv.dilate(img_temp2, replacement_hori, iterations=3)
    cv.imwrite("horizontal_lines.jpg",horizontal_lines_img)

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha
    # Combine images
    img_final_bin = cv.addWeighted(vertical_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    cv.imwrite("img_final_bin.jpg",img_final_bin)
    contours = cv.findContours(img_final_bin, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    contours = sort_contours(contours, method="top-to-bottom")
    tFile = open("FinalimageText.txt", "w")
    img_final_bin = cv2.cvtColor(img_final_bin,cv2.COLOR_GRAY2RGB)

    for c in range(len(contours)):
        x,y,w,h = cv.boundingRect(contours[c])
        #cv.rectangle(temp, (x, y), (x + w, y + h), (36,255,12), 2)  <-- use this to draw rectangles to visualize ROI
        cropped_image = temp[y:y+h, x:x+w]
        sectionText = pytesseract.image_to_string(cropped_image)
        print(sectionText)
        print("SEPARATOR---------------------------")
        if (sectionText.find('/') != -1) and dateFound == False:
            tFile.write("Year/Annee: "+ sectionText[sectionText.find('/') - 2: sectionText.find('/') + 8]+ "\n")
            dateFound = True

        if ('Actual amount of eligible dividends' in sectionText) and 'Année' not in sectionText:
            sectionText = sectionText.replace('24', '', 1)
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace('Actualamountofeligibledividends', '')
            sectionText = sectionText.replace('Montantréeldesdividendesdéterminés', '')
            tFile.write("Actual amount of eligible dividends / Montant réel des dividendes déterminés: "+ sectionText + '\n')
        
        if ('Taxable amount of eligible dividends' in sectionText) and ('Année' not in sectionText) and ('Box' not in sectionText):
            sectionText = sectionText.replace('25', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('i', '')
            sectionText = sectionText.replace('Taxableamountofelgbledvdends', '')
            sectionText = sectionText.replace("Montantmposabledesdvdendes‘détermnés", '')
            tFile.write("Taxable amount of eligible dividends / Montant imposable des dividendes déterminés: "+ sectionText + '\n')

        if ('Dividend tax credit for eligible' in sectionText) and 'Année' not in sectionText:
            sectionText = sectionText.replace('26', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('Dividendtaxcreditforeligibledividends', '')
            sectionText = sectionText.replace('Créditdimpétpourdividendesdéterminés', '')
            tFile.write("Dividend tax credit for eligible dividends / Crédit dimpét pour dividendes déterminés: "+ sectionText + '\n')
        
        if ('Interest from Canadian sources' in sectionText) and 'Année' not in sectionText:
            sectionText = sectionText.replace('13]', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('.', '', 1)
            sectionText = sectionText.replace('InterestfromCanadiansources', '')
            sectionText = sectionText.replace('Intérétsdesourcecanadienne', '')
            tFile.write("Interest from Canadian sources / Intéréts de Source Canadienne: "+ sectionText + '\n')
        
        if ('Capital gains dividends' in sectionText) and 'Année' not in sectionText:
            sectionText = sectionText.replace('18', '', 1) 
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('Capitalgainsdividends', '')
            sectionText = sectionText.replace('Dividendessurgainsencapital', '')
            tFile.write("Capital gains dividends / Dividendes sur gains en capital: "+ sectionText + '\n')

        if ('Actual amount of dividends' in sectionText) and 'Année' not in sectionText:
            sectionText = sectionText.replace('10', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('Actualamountofdividendsotherthaneligibledividends', '')
            sectionText = sectionText.replace('Montantréeldesdividendesautresquedesdividendesdéterminés', '')
            tFile.write("Actual amount of dividends other than eligible dividends / Montant réel des dividendes autres que des dividendes déterminés: "+ sectionText + '\n')
        
        if ('Taxable amount of dividends' in sectionText) and ('Année' not in sectionText) and ('other than eligible dividends' in sectionText):
            sectionText = sectionText.replace('1', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('W', '')
            sectionText = sectionText.replace('Taxableamountofdividendsotherthaneligibledividends', '')
            sectionText = sectionText.replace('Montantimposabledesdividendesautresquedesdividendesdéterminés', '')
            tFile.write("Taxable amount of dividends other than eligible dividends / Montant imposable des dividendes autres que des dividendes déterminés: "+ sectionText + '\n')

        if ('Crédit dimpét pour dividendes' in sectionText) and ('Année' not in sectionText) and ('autres que des dividendes déterminés' in sectionText):
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('12|‘Drvidendtaxcreditfordividends:otherthaneligibledividends', '')
            sectionText = sectionText.replace('4D|‘Ulvicandtexcredittordividends:otherthaneligibledividends', '')
            sectionText = sectionText.replace('4p|‘Drvicandtexcracktorcividancs:otherthaneligibledividends', '')
            sectionText = sectionText.replace('12|‘PNidendtaxcreckforcividencs:otherthaneligibledividends', '')
            sectionText = sectionText.replace('Créditdimpétpourdividendesautresquedesdividendesdéterminés', '')
            tFile.write("Dividend tax credit for dividends other than eligible dividends / Crédit dimpét pour dividendes autres que des dividendes déterminés: "+ sectionText + '\n')
        
        if ('Report Code' in sectionText) and ('Année' not in sectionText):
            sectionText = sectionText.replace('21]', '', 1)
            sectionText = sectionText.replace('21|', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('ReportCode', '')
            sectionText = sectionText.replace('Codedufeuillet', '')
            tFile.write("Report Code / Code du Feuillet: "+ sectionText + '\n')
        
        if ('Recipient identification number' in sectionText) and ('Année' not in sectionText):
            sectionText = sectionText.replace('22]', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('Recipientidentificationnumber', '')
            sectionText = sectionText.replace("Numérod'identificationdubénéficiaire", '')
            tFile.write("Recipient identification number / Numéro d'identification du bénéficiaire: "+ sectionText + '\n')

        if ('Recipient type' in sectionText) and ('Année' not in sectionText):
            sectionText = sectionText.replace('23', '', 1)
            sectionText = sectionText.replace('\n', '')
            sectionText = sectionText.replace(' ', '')
            sectionText = sectionText.replace('|Recipienttype', '')
            sectionText = sectionText.replace('Typedebénéficiaire', '')
            sectionText = sectionText.replace('‘', '')
            tFile.write("Recipient Type / Type de bénéficiaire: "+ sectionText + '\n')
        
        if ('Other information' in sectionText) and ('Autres renseignements' in sectionText) and ('Année' not in sectionText):
            
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
                    
        if ("Recipient's name (last name first) and address — Nom, prénom et adresse du bénéficiaire" in sectionText) and ("Payer's name and address — Nom et adresse du payeur" not in sectionText) and ('Année' not in sectionText):
            xt,yt,wt,ht = cv.boundingRect(contours[c+1])
            tempBox = temp[yt:yt+ht, xt:xt+wt]
            boxText = pytesseract.image_to_string(tempBox)
            boxText = boxText.strip()
            boxText = boxText.replace('\n', ' ')
            tFile.write("Recipient's name (last name first) and address / Nom, prénom et adresse du bénéficiaire: "+ boxText + '\n')
            
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
            tFile.write("Foreign Currency / Devises étrangères: "+ boxText + '\n')

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
            tFile.write("Recipient account number / Numéro de compte du bénéficiaire: "+ boxText + '\n')
            tFile.write("\n")

    tFile.close()  
    cv.imwrite('newresult.png', temp)

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


#Driver Code
def readFile():
#TESTING
    #image = cv.imread('./testingImages/johnTest.jpeg')
    #image = cv.imread('./testingImages/test.jpg')
    #image = cv.imread('./testingImages/stocks.jpeg')
    #image = cv.imread('./testingImages/ECETB.png')
    #image = cv.imread('./testingImages/cra.png')
    image = cv.imread('./PDFoutput/page0.jpg')
    #checkFile('./testingPDF/t5-22b.pdf')

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    #dst = cv.GaussianBlur(image,(5,5),0)
    #image=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    #dst = cv.fastNlMeansDenoisingColored(image,None,10,10,7,21)
    #craTest = craProcessing(image)
    #text = pytesseract.image_to_string(craTest)
    #createFile(text)
    #cv.imwrite('result.png', craTest)
    #drawBoxes(craTest)
    boxcraProcessing(image)

#driver code
readFile()
