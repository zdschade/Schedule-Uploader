from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from flask_dropzone import Dropzone
import os
from PIL import Image
from OCR import *
from Calendar import *
import time


UPLOAD_FOLDER = 'static/uploads/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
dropzone = Dropzone(app)

global id
id = ''


@app.route('/')
def upload_file():
   return render_template('home.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        #file = request.files['file']
        file = request.files.get('file')
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        global global_filename
        #print("DEFINED")
        global_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        #print("GLOBAL FILENAME: " + str(global_filename))

        return render_template("crop.html", schedule_image=global_filename)


@app.route('/crop', methods=['GET', 'POST'])
def crop():
    return render_template("crop.html", schedule_image=global_filename)


@app.route('/schedule_prep', methods=['GET', 'POST'])
def schedule_prep():
    if request.method == "POST":
        coords = request.form['coords']
        coords = coords.split(',')
        #print("coords: " + str(coords))
        coords = [float(coord) for coord in coords]
        #print(coords)

        img = Image.open(global_filename)

        cropped = img.crop((coords[0], coords[1], coords[0] + coords[2], coords[1] + coords[3]))
        #cropped.show()

        cropped.save(global_filename[0:-4] + "_cropped.jpg")
        global global_filename_cropped
        global_filename_cropped = (global_filename[0:-4] + "_cropped.jpg")
        print(global_filename_cropped)

        split = split_schedule(global_filename_cropped, 7)  # defaults to 7 for now, implement change to 5 later
        ocr = split_ocr(global_filename_cropped[:-4])
        global ocr_results
        ocr_results = ocr
        print(ocr_results)
        readable_ocr = visual_format(ocr)


        return render_template("scheduleprep.html", ocr_text=readable_ocr, schedule_image=global_filename)

@app.route('/google_login', methods=['GET', 'POST'])
def cal_login():
    if request.method == "POST":
        startdate = request.form['startdate']
        startdate = format_date(startdate)
        print("STARTDATE: " + str(startdate))

        schedule = format_schedule(ocr_results, startdate, 'America/Los_Angeles')
        
        google_login(id)
        create_events(schedule)

        return render_template("googlelogin.html")


if __name__ == '__main__':
   app.run(debug=True)
