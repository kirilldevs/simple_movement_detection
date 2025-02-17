# Camera Motion Detection

This project was created as a quick solution for detecting motion using a webcam. The goal was to build a simple, functional system that highlights movement and captures images when motion is detected. Most of the code was generated with the help of ChatGPT.

## How it Works:
- Detects movement in real-time using OpenCV.
- Highlights detected motion in the video feed.
- Takes a photo every few seconds when motion is detected.
- Customizable alert system that must be updated in the send_alert function.

## Setup:
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies using "pip install -r requirements.txt".
4. Run the script with "python main.py".

## Customization:
- Motion Sensitivity: Adjust MOTION_CONTOUR_AREA in main.py.
- Photo Capture Delay: Modify PHOTO_COOLDOWN_SEC to change how often images are saved.alerts are sent (e.g., email, Telegram, sound notifications).

This was a quick, functional project with room for improvement. Feel free to modify or expand it as needed.
