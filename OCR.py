import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import copy
import os.path
import sys
import stat
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def split_schedule(filename, days):
    #only works for horizontal schedules rn
    #cropping is too agressive, check?

    if not "static/uploads" in filename:
        file_dir = os.path.join("static/uploads/", filename)
    else:
        file_dir = filename

    #print("FILE_DIR: " + file_dir)
    
    filename = filename.replace("static/uploads/", "")
    #print("HERE + FILENAME: " + filename)

    if not os.path.isdir(file_dir[:-4]):
        file_dir = file_dir[:-4]
        os.mkdir(file_dir)
        #print("MADE DIR")

    filename = filename.replace("static/uploads/", "")

    #print("IMAGE TRIED TO OPEN: " + file_dir + ".jpg")
    if ".jpg" in file_dir:
        working_path = file_dir
    else:
        working_path = file_dir + ".jpg"
        
    img = Image.open(working_path)    
    width, height = img.size

    for i in range(days):  # This part does the cropping
        if i == 0:
            left = (0 + ((width/days)*i)) - 3
        else:
            left = (0 + ((width/days)*i)) - 5

        top = 0

        if i == days:
            right = ((width/days) * (i+1)) + 20
        else: 
            right = ((width/days) * (i+1)) + 20

        bottom = height

        section = img.crop((left, top, right, bottom))
        section_name = str(filename[:-4] + "_" + str(i) + filename[-4:])
        #print("SECTION NAME: " + section_name)
        section.save(os.path.join(working_path[:-4], str(section_name)))

    #print("RETURNED DIR: " + str(file_dir))
    return file_dir[:-3]


def ocr_core(filename):
    """Takes a file, reads the text on it with Pytesseract, cleans the text, and returns it"""

    img = Image.open(filename)
    width, height = img.size

    # brightens the image
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(2)

    # sharpens the image
    enhancer = ImageEnhance.Sharpness(img)
    for i in range(8):
        factor = i / 4.0
        enhancer.enhance(factor) #.show("Sharpness %f" % factor)

    # grayscales the image
    img = ImageOps.grayscale(img)

    #img.show()

    # OCR
    text = pytesseract.image_to_string(img)

    text = clean_text(text)

    return text


def clean_text(text):
    """Takes text from OCR and removes excess characters"""
    # chars to remove
    remove = ['[', ']', '{', '}', '(', ')', '.', ',', "|", "/", ";", "<", ">", "!", "?", "="]

    # replaces chars with empty string
    for i in remove:
        text = text.replace(i, "")

    # fixes fringe misread by OCR and removes spaces
    text = text.replace("+", "-")
    text = text.replace(" ", "")


    # Replaces A and P with AM and PM
    if "A" in text and "AM" not in text:
        text = text.replace("A", "AM")
    if "P" in text and "PM" not in text:
        text = text.replace("P", "PM")


    # splits the times into a list
    text = text.split()

    

    return text

def visual_format(schedule):
    """
    Schedule should be a list of lists containg the OCR results
    [[], ['10:00AM-04:00PM'], [], ['02:00PM-10:00PM'], ['02:00PM-09:00PM'], ['02:00PM-10:00PM'], []]
    """

    formatted = ""
    for times in schedule:
        if len(times) == 0:
            pass
        else:
            if len(formatted) == 0:
                formatted = formatted + times[0]
            else:
                formatted = formatted + ", " + times[0]
    
    return formatted


def split_ocr(dir):
    """
    Combines ocr_core and the folder created in split_schedule to return an accurate schedule
    """

    #time.sleep(7)
    #print("SPLIT OCR DIR: " + dir)
    images = next(os.walk(dir))[2]

    times = []

    for img in images:
        times.append(ocr_core(os.path.join(dir,img)))

    return times
