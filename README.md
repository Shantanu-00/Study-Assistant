# EduVisionAI – Study Enhancer

## Description
AI-powered tool for focus detection and automated summarization to help students study smarter. Detects distractions, summarizes content, and provides actionable insights.

## Tech Stack
- Python, OpenCV, YOLOv8, NLP
- Focus & distraction detection
- Automated summarization

## Screenshots

<!-- Two per row for wider screens, fallback to vertical on narrow -->
<p>
  <img src="./images/home.png" alt="Home dashboard" width="48%" />
  <img src="./images/login.png" alt="Login screen" width="48%" />
</p>

<p>
  <img src="./images/detection.png" alt="Distraction detection view" width="48%" />
  <img src="./images/quiz.png" alt="Quiz interface" width="48%" />
</p>

<p>
  <img src="./images/summary.png" alt="Summarized study material" width="60%" />
</p>


## Setup
```bash
git clone https://github.com/Shantanu-00/eduvision.git
cd eduvision
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

## Usage
python main.py

