import sys
import os
import urllib.request
import pyttsx3
import google.generativeai as genai
from ultralytics import YOLO
from config import WEIGHTS_FILE, WEIGHTS_URL, GOOGLE_API_KEY
import mediapipe as mp
import logging

# Suppress mediapipe and TensorFlow warnings
logging.getLogger('mediapipe').setLevel(logging.ERROR)
logging.getLogger('absl').setLevel(logging.ERROR)

if not os.path.exists(WEIGHTS_FILE):
    print(f"{WEIGHTS_FILE} not found. Attempting to download...")
    try:
        urllib.request.urlretrieve(WEIGHTS_URL, WEIGHTS_FILE)
        print(f"Downloaded {WEIGHTS_FILE} successfully.")
    except Exception as e:
        print(f"Error downloading {WEIGHTS_FILE}: {e}")
        print("Please download it manually from https://github.com/ultralytics/assets/releases and place it in the script directory.")
        sys.exit(1)

engine = pyttsx3.init()
engine.setProperty('rate', 150)
model = YOLO(WEIGHTS_FILE)
model.overrides['verbose'] = False
genai.configure(api_key=GOOGLE_API_KEY)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)