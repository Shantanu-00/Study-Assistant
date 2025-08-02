import cv2
import time
import sys
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from ultralytics import YOLO
from utils import eye_aspect_ratio, log_distraction
from config import (WEIGHTS_FILE, EYE_AR_THRESHOLD, EYE_CLOSED_DURATION, 
                   MOBILE_PHONE_THRESHOLD, ALERT_COOLDOWN, LOG_DIR, LEFT_EYE, RIGHT_EYE)
import os
import datetime
from messaging import notify_guardian

class DetectionThread(QThread):
    frame_signal = pyqtSignal(np.ndarray)
    alert_signal = pyqtSignal(str, np.ndarray)

    def __init__(self, model, face_mesh, username):
        super().__init__()
        self.running = True
        self.cap = cv2.VideoCapture(0)
        self.model = model
        self.face_mesh = face_mesh
        self.username = username  # Store username for notifications
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            sys.exit(1)
        self.eye_closed_start_time = None
        self.mobile_phone_counter = 0
        self.last_alert_time = 0
        os.makedirs(LOG_DIR, exist_ok=True)

    def log_event(self, event_type, frame):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(LOG_DIR, "distraction_log.txt")
        img_path = os.path.join(LOG_DIR, f"{event_type}_{timestamp}.jpg")
        
        cv2.imwrite(img_path, frame)
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - {event_type} detected - Image: {img_path}\n")
        print(f"[LOG] {event_type} logged at {timestamp}")
        
        # Notify guardian
        notify_guardian(self.username, event_type, timestamp)

    def run(self):
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break

            results = self.model(frame)
            phone_detected = False
            for result in results:
                for box in result.boxes:
                    label = result.names[int(box.cls[0])]
                    if label.lower() == "cell phone":
                        phone_detected = True
                        print(f"[DEBUG] Cell phone detected with confidence: {box.conf[0]}")
                        break
            if phone_detected:
                self.mobile_phone_counter += 1
            else:
                self.mobile_phone_counter = 0

            if self.mobile_phone_counter >= MOBILE_PHONE_THRESHOLD:
                if time.time() - self.last_alert_time > ALERT_COOLDOWN:
                    self.alert_signal.emit("Put your phone away and focus!", frame)
                    self.log_event("Mobile Phone", frame)
                    self.last_alert_time = time.time()
                    self.mobile_phone_counter = 0

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results_mesh = self.face_mesh.process(rgb_frame)
            if results_mesh.multi_face_landmarks:
                for face_landmarks in results_mesh.multi_face_landmarks:
                    h, w, _ = frame.shape
                    left_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) 
                                for i in LEFT_EYE]
                    right_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) 
                                 for i in RIGHT_EYE]
                    ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0
                    if ear < EYE_AR_THRESHOLD:
                        if self.eye_closed_start_time is None:
                            self.eye_closed_start_time = time.time()
                        elif time.time() - self.eye_closed_start_time >= EYE_CLOSED_DURATION:
                            if time.time() - self.last_alert_time > ALERT_COOLDOWN:
                                self.alert_signal.emit("Wake up! You are dozing off!", frame)
                                self.log_event("Dozing", frame)
                                self.last_alert_time = time.time()
                                self.eye_closed_start_time = None
                    else:
                        self.eye_closed_start_time = None
            else:
                print("[DEBUG] No face detected")

            self.frame_signal.emit(results[0].plot())
            time.sleep(0.033)

        self.cap.release()

    def stop(self):
        self.running = False
        self.wait()