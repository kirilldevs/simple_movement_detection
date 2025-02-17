import cv2
import numpy as np
import imutils
import time
import os

PHOTO_COOLDOWN_SEC = 10

# Folder to save captured images
if not os.path.exists("captured_movement"):
    os.makedirs("captured_movement")

def save_photo(frame, count):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"captured_movement/motion_{count}_{timestamp}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Photo saved: {filename}")

def send_alert(counter):
    print(f"Motion detected! Sending alert... (Count: {counter})")

# Initialize the camera
cap = cv2.VideoCapture(0)
time.sleep(2)  # Allow the camera to warm up

first_frame = None
motion_counter = 0
detection_count = 0
frame_update_interval = 50  # Update background every 50 frames
frame_counter = 0  # Track total frames processed
photo_cooldown = PHOTO_COOLDOWN_SEC  # Take a photo only every 3 seconds
last_photo_time = time.time()  # Track last photo time

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for faster processing
    frame = imutils.resize(frame, width=500)

    # Convert to grayscale and apply Gaussian blur
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (11, 11), 0)  # Slightly higher blur for noise reduction

    # Initialize the first frame
    if first_frame is None:
        first_frame = gray
        continue

    # Compute absolute difference between frames
    frame_delta = cv2.absdiff(first_frame, gray)

    # Apply edge detection to better detect small movements
    edges = cv2.Canny(frame_delta, 30, 150)  # Edge detection on frame difference

    # Thresholding to detect actual movement
    thresh = cv2.threshold(frame_delta, 20, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Combine threshold and edges for better motion detection
    combined = cv2.bitwise_or(thresh, edges)

    # Find contours
    contours = cv2.findContours(combined.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    motion_detected = False
    for contour in contours:
        if cv2.contourArea(contour) < 500:  # Lowered to detect small movements
            continue
        motion_detected = True
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Trigger alert if motion persists for several frames
    if motion_detected:
        motion_counter += 1
        if motion_counter >= 3:  # Require 3 consecutive frames instead of 5
            detection_count += 1
            send_alert(detection_count)

            # Capture a photo only if enough time has passed (to avoid spamming)
            current_time = time.time()
            if current_time - last_photo_time >= photo_cooldown:
                save_photo(frame, detection_count)
                last_photo_time = current_time  # Reset the timer
    else:
        motion_counter = 0  # Reset counter if no motion

    # **Update the background every 50 frames to prevent outdated reference**
    frame_counter += 1
    if frame_counter % frame_update_interval == 0:
        first_frame = gray.copy()

    # Show frames
    cv2.imshow("Motion Detection", frame)
    cv2.imshow("Threshold", thresh)
    cv2.imshow("Edges", edges)  # Debugging view of edges

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
