import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google API Key for Gemini AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file. Please set it and try again.")
    import sys
    sys.exit(1)

# Twilio credentials for WhatsApp messaging
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
if not all([TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE]):
    print("Error: One or more Twilio credentials (TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE) not found in .env file. Please set them and try again.")
    import sys
    sys.exit(1)

# YOLO weights configuration
WEIGHTS_FILE = 'yolov8n.pt'
WEIGHTS_URL = 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt'

# Eye landmarks indices (MediaPipe Face Mesh)
# Note: These indices are swapped compared to your original (LEFT_EYE was right eye indices and vice versa)
LEFT_EYE = [33, 160, 158, 133, 153, 144]  # Corrected for left eye
RIGHT_EYE = [362, 385, 387, 263, 373, 380]  # Corrected for right eye

# Constants
EYE_AR_THRESHOLD = 0.25  # Eye Aspect Ratio threshold for detecting closed eyes
EYE_CLOSED_DURATION = 5  # Seconds eyes must be closed to trigger dozing alert
MOBILE_PHONE_THRESHOLD = 5  # Frames a phone must be detected to trigger alert
ALERT_COOLDOWN = 5  # Seconds between consecutive alerts
LOG_DIR = "logs"  # Directory for log files and images
LOG_FILE = os.path.join(LOG_DIR, "distractions.log")  # Path to log file