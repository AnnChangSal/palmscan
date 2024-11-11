import os
import random
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import cv2
import mediapipe as mp
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def extract_hand_region(image_path):
    # Read the image
    image = cv2.imread(image_path)
    original_image = image.copy()
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_hands.Hands(static_image_mode=True, max_num_hands=1) as hands:
        result = hands.process(image_rgb)

        if result.multi_hand_landmarks:
            height, width, _ = image.shape
            hand_mask = np.zeros((height, width), dtype=np.uint8)

            for hand_landmarks in result.multi_hand_landmarks:
                # Get landmark points
                landmark_points = []
                for lm in hand_landmarks.landmark:
                    x = int(lm.x * width)
                    y = int(lm.y * height)
                    landmark_points.append([x, y])

                # Create convex hull
                landmark_points = np.array(landmark_points, dtype=np.int32)
                hull = cv2.convexHull(landmark_points)
                # Fill the hand region on the mask
                cv2.fillConvexPoly(hand_mask, hull, 255)

            # Extract hand region
            hand_region = cv2.bitwise_and(original_image, original_image, mask=hand_mask)
            return hand_region
        else:
            return None

def detect_palm_lines(hand_region):
    gray = cv2.cvtColor(hand_region, cv2.COLOR_BGR2GRAY)
    # Enhance contrast
    gray = cv2.equalizeHist(gray)
    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)
    return edges

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
        hand_region = extract_hand_region(filepath)
        if hand_region is not None:
            edges = detect_palm_lines(hand_region)
            original_image = cv2.imread(filepath)
            # Overlay the edges onto the original image
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            overlay = cv2.addWeighted(original_image, 0.8, edges_colored, 0.2, 0)
            processed_filename = 'processed_' + filename
            processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
            cv2.imwrite(processed_filepath, overlay)
        else:
            processed_filename = None

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
