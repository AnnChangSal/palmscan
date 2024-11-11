import os
import random
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def detect_palm_lines(image_path):
    image = cv2.imread(image_path)
    original_image = image.copy()

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Enhance contrast
    gray = cv2.equalizeHist(gray)

    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection using Canny
    edges = cv2.Canny(blurred, 50, 150)

    # Overlay the edges onto the original image
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    overlay = cv2.addWeighted(original_image, 0.8, edges_colored, 0.2, 0)

    return overlay

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the image
        processed_image = detect_palm_lines(filepath)
        processed_filename = 'processed_' + filename
        processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        cv2.imwrite(processed_filepath, processed_image)

        # Simulated palmistry reading
        readings = [
            "You have a strong life line, indicating vitality and energy.",
            "Your heart line suggests deep emotional connections.",
            "A prominent head line shows intellectual prowess.",
            "Your fate line shows significant career success.",
            "The sun line indicates fame or public recognition."
        ]
        result = random.choice(readings)

        return render_template('result.html', result=result, processed_filename=processed_filename)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
