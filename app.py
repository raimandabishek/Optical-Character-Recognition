
from flask import Flask, request, render_template, session, send_from_directory
import cv2
import numpy as np
import pytesseract
import os
import json
from pdf2image import convert_from_path
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your secret key

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

UPLOAD_FOLDER = 'uploads'
JSON_FOLDER = 'json'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_FOLDER'] = JSON_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(JSON_FOLDER):
    os.makedirs(JSON_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return render_template('index.html', extracted_text='No file part')

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', extracted_text='No selected file')

    if not allowed_file(file.filename):
        return render_template('index.html', extracted_text='File type not allowed')

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    text = ""
    try:
        if file.filename.lower().endswith('.pdf'):
            try:
                images = convert_from_path(file_path)
                for image in images:
                    preprocessed_image = preprocess_image(image)
                    text += pytesseract.image_to_string(preprocessed_image) + "\n"
            except Exception as e:
                text = f"Error processing PDF: {e}"
        else:
            image = Image.open(file_path)
            preprocessed_image = preprocess_image(image)
            text = pytesseract.image_to_string(preprocessed_image)
    except Exception as e:
        text = f"Error processing file: {e}"
    
    os.remove(file_path)
    
    # Store the extracted text in session
    session['extracted_text'] = text

    # Write the extracted text to a JSON file
    json_data = {'extracted_text': text}
    json_filename = os.path.splitext(file.filename)[0] + '.json'
    json_filepath = os.path.join(app.config['JSON_FOLDER'], json_filename)
    with open(json_filepath, 'w') as json_file:
        json.dump(json_data, json_file)
    
    session['json_filepath'] = json_filepath

    return render_template('index.html', extracted_text=text)

@app.route('/download')
def download():
    json_filepath = session.get('json_filepath', '')
    if json_filepath and os.path.exists(json_filepath):
        return send_from_directory(app.config['JSON_FOLDER'], os.path.basename(json_filepath), as_attachment=True)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
