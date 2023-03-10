# documentReader
Program that helps the visually impaired by using OCR to scan the t5-22b tax file and extract the contents in the form of an MP3 file.
Tesseract OCR was chosen so that the program is capable of reading the contents of scanned images, which PDF parsers cannot access, improving accessibility and flexibility with which documents can be read

## Technologies used
Modules: Gtts, numpy, matplotlib, pytesseract, playsound

## How it works
The program first converts the pdf in the "testingPDF" directory to a set of jpg images, storing the output in the PDFoutput directory. Then vertical and horizontal lines are mapped to the grids in the original file (outputs of the mapping can be viewed in vertical_lines.jpg and horizontal_lines.jpg).
The vertical line and horizontal line maps are then combined to form a grid map, which can be viewed in (img_final_bin.jpg)

<p float="left">
  <img src="https://github.com/JwuCode/documentReader/blob/main/img_final_bin.jpg?raw=true" width="300" height="300">
  <img src="https://github.com/JwuCode/documentReader/blob/main/result.png?raw=true" width="300"  height="300" /> 
</p>

After (img_final_bin.jpg) is created, contour mapping is performed to find the boxes which need to be scanned by the Tesseract model. The mapped boxes are shown in (result.png). After each box is scanned, the text and key information is stored in imageText.txt, which is then converted to an MP3 file using Google-text-to-speech (gtts)

## How to test
Just put any modification of the t5-22b tax pdf in the testingPDF file and run the main.py file. The program will read the form and automatically replace the current image, text, and MP3 files.
