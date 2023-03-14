import os
from pdf2image import convert_from_path
import re

date_pattern = '^((((0[13578])|([13578])|(1[02]))[\/](([1-9])|([0-2][0-9])|(3[01])))|(((0[469])|([469])|(11))[\/](([1-9])|([0-2][0-9])|(30)))|((2|02)[\/](([1-9])|([0-2][0-9]))))[\/]\d{4}$|^\d{4}$'
test = '12/12/2004'
test2 = "pepepe"
print(re.match(date_pattern, test))
if re.match(date_pattern, test):
    print('poopy')
    
print(re.match(date_pattern, test2))

if re.match(date_pattern, test2):
    print('stinky')