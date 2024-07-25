# from flask import Flask, request, render_template, redirect, url_for
# import cv2
# import numpy as np
# import pytesseract
# import os

# app = Flask(__name__)

# # Set the path to the Tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# def preprocess_image(image_path):
#     img = cv2.imread(image_path)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#     return thresh

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'file' not in request.files:
#         return redirect(request.url)
#     file = request.files['file']
#     if file.filename == '':
#         return redirect(request.url)
#     if file:
#         file_path = os.path.join('uploads', file.filename)
#         file.save(file_path)
#         preprocessed_image = preprocess_image(file_path)
#         text = pytesseract.image_to_string(preprocessed_image)
#         os.remove(file_path)
#         return render_template('index.html', extracted_text=text)
#     return redirect(request.url)

# if __name__ == '__main__':
#     app.run(debug=True)

# app.py

# from flask import Flask, request, render_template, redirect, url_for
# import cv2
# import numpy as np
# import pytesseract
# import os

# app = Flask(__name__)

# # Set the path to the Tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# def preprocess_image(image_path):
#     img = cv2.imread(image_path)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#     return thresh

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'file' not in request.files:
#         return redirect(request.url)
#     file = request.files['file']
#     if file.filename == '':
#         return redirect(request.url)
#     if file:
#         file_path = os.path.join('uploads', file.filename)
#         file.save(file_path)
#         preprocessed_image = preprocess_image(file_path)
#         text = pytesseract.image_to_string(preprocessed_image)
#         os.remove(file_path)
#         return render_template('index.html', extracted_text=text)
#     return redirect(request.url)

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, request, render_template, redirect, url_for
import cv2
import numpy as np
import pytesseract
import os
from pdf2image import convert_from_path
from PIL import Image

app = Flask(__name__)

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
    return render_template('index.html', extracted_text=text)

if __name__ == '__main__':
    app.run(debug=True)



