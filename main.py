import cv2
import numpy as np
import imutils
import time
import os

# ==== CONFIGURABLE PARAMETERS ====

PHOTO_COOLDOWN_SEC = 10  # Time interval (in seconds) between saved photos to avoid excessive captures
FRAME_UPDATE_INTERVAL = 50  # Number of frames before updating the background model (helps adapt to scene changes)
MOTION_CONTOUR_AREA = 500  # Minimum contour area for detecting motion (adjust for sensitivity)
MOTION_PERSISTENCE_FRAMES = 3  # Number of consecutive frames where motion is detected before triggering an alert
CAMERA_WARMUP_TIME = 2  # Seconds to wait after initializing the camera before processing frames
FRAME_WIDTH = 500  # Width to resize the video frame for faster processing
GAUSSIAN_BLUR_KERNEL = (11, 11)  # Kernel size for Gaussian blur (helps reduce noise)
EDGE_DETECTION_THRESHOLDS = (30, 150)  # Canny edge detection min and max thresholds
MOTION_THRESHOLD_VALUE = 20  # Threshold for detecting differences between frames

# ==== SETUP ====

# Folder to save captured images
if not os.path.exists("captured_movement"):
    os.makedirs("captured_movement")

def save_photo(frame, count):
    """Saves a photo with a timestamp when motion is detected."""
    timestamp = time.strftime("%d-%m-%Y_%H-%M-%S")
    filename = f"captured_movement/motion_{count}_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Photo saved: {filename}")

def send_alert():
    """Prints an alert message when motion is detected."""
    print("Motion detected! Sending alert...")

# Initialize the camera
cap = cv2.VideoCapture(0)
time.sleep(CAMERA_WARMUP_TIME)  # Allow the camera to warm up

first_frame = None
motion_counter = 0
detection_count = 0
frame_counter = 0  # Tracks total frames processed
last_photo_time = time.time()  # Tracks last time a photo was saved

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for faster processing
    frame = imutils.resize(frame, width=FRAME_WIDTH)

    # Convert to grayscale and apply Gaussian blur
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, GAUSSIAN_BLUR_KERNEL, 0)  # Helps reduce noise

    # Initialize the first frame for background comparison
    if first_frame is None:
        first_frame = gray
        continue

    # Compute absolute difference between the current frame and the background
    frame_delta = cv2.absdiff(first_frame, gray)

    # Apply edge detection to improve small motion detection
    edges = cv2.Canny(frame_delta, *EDGE_DETECTION_THRESHOLDS)

    # Apply thresholding to highlight motion areas
    thresh = cv2.threshold(frame_delta, MOTION_THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Combine thresholding and edge detection for better motion analysis
    combined = cv2.bitwise_or(thresh, edges)

    # Find contours of moving objects
    contours = cv2.findContours(combined.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    motion_detected = False
    for contour in contours:
        if cv2.contourArea(contour) < MOTION_CONTOUR_AREA:
            continue  # Ignore small movements
        motion_detected = True
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Trigger alert if motion is detected for a set number of consecutive frames
    if motion_detected:
        motion_counter += 1
        if motion_counter >= MOTION_PERSISTENCE_FRAMES:
            detection_count += 1
            send_alert()

            # Capture a photo only if enough time has passed
            current_time = time.time()
            if current_time - last_photo_time >= PHOTO_COOLDOWN_SEC:
                save_photo(frame, detection_count)
                last_photo_time = current_time  # Reset the timer
    else:
        motion_counter = 0  # Reset counter if no motion

    # Update the background model periodically to adjust to new scene conditions
    frame_counter += 1
    if frame_counter % FRAME_UPDATE_INTERVAL == 0:
        first_frame = gray.copy()

    # Display frames for debugging
    cv2.imshow("Motion Detection", frame)
    cv2.imshow("Threshold", thresh)
    cv2.imshow("Edges", edges)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
