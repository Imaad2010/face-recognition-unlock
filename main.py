import cv2
import os
import face_recognition
import pyttsx3
import numpy as np
import logging
import socket
import time

# ========== Setup and Initialization ==========

# Setup logging to track events with timestamps
logging.basicConfig(filename='recognition_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Initialize the Text-to-Speech engine
engine = pyttsx3.init()

# Function to audibly announce recognized person
def speak(text):
    engine.say(text)
    engine.runAndWait()

# ========== Load Reference Images ==========

# Path where reference images are stored
desktop_path = '/home/jetson/Downloads'

# List of known face images (filenames) to be recognized
reference_images = ['']  # 🔁 Add your image filenames here, e.g., ['imaad.jpg']
reference_encodings = []

# Names that match the reference_images list in order
known_names = ['']  # 🔁 Add matching names here, e.g., ['Imaad']

# Load and encode all reference images
for image_name in reference_images:
    reference_image_path = os.path.join(desktop_path, image_name)
    if os.path.exists(reference_image_path):
        reference_image = face_recognition.load_image_file(reference_image_path)
        reference_encoding = face_recognition.face_encodings(reference_image)

        if len(reference_encoding) > 0:
            reference_encodings.append(reference_encoding[0])
        else:
            print(f"Error: No face found in the reference image {image_name}.")
    else:
        print(f"Error: Image file {image_name} not found at {desktop_path}")

# Exit if no faces were successfully encoded
if not reference_encodings:
    print("Error: No valid reference faces found. Exiting.")
    exit()

# ========== UDP Broadcast Setup ==========

# Function to send unlock signal over UDP
def udp_broadcast(message):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_ip = '192.168.0.200'  # 🔁 Replace with your network's broadcast IP
    port = XXXX  # 🔁 Replace with the correct port (e.g., 5005)
    udp_socket.sendto(message.encode('utf-8'), (broadcast_ip, port))
    logging.info(f"UDP Broadcast sent: {message}")

# ========== Camera Feed and Recognition Loop ==========

# Start video capture from default camera
cap = cv2.VideoCapture(0)

# Timing variables to control recognition and broadcast frequency
last_broadcast_time = 0
broadcast_interval = 10  # seconds between broadcasts
face_seen_start_time = None  # timestamp when face is first seen
required_time_in_view = 2  # seconds face must stay in view before unlock

# Main recognition loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture video frame.")
        break

    # Resize frame for performance (25% size)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect face locations and encodings in current frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    face_recognized = False  # Track if a valid face was recognized in this frame

    for face_encoding in face_encodings:
        face_distances = face_recognition.face_distance(reference_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        # If the face matches a known reference
        if face_distances[best_match_index] < 0.45:
            name = known_names[best_match_index]
            face_recognized = True

            # If this is the first time the face is seen
            if face_seen_start_time is None:
                face_seen_start_time = time.time()

            # If face has stayed for long enough
            elif time.time() - face_seen_start_time >= required_time_in_view:
                current_time = time.time()
                if current_time - last_broadcast_time >= broadcast_interval:
                    confidence = (1 - face_distances[best_match_index]) * 100
                    speak(f"Unlock for {name} with {int(confidence)}% confidence.")
                    logging.info(f"Face recognized: Unlock for {name} with {int(confidence)}% confidence.")

                    # Send unlock message over UDP
                    udp_broadcast(f"Unlock: {name} recognized with {int(confidence)}% confidence.")
                    last_broadcast_time = current_time

                # Reset view timer after successful unlock
                face_seen_start_time = None
            break  # Avoid processing more faces in the same frame

    # If no face was recognized, reset timer
    if not face_recognized:
        face_seen_start_time = None

    # Show the video feed (for debugging or monitoring)
    cv2.imshow('Face Recognition Door Lock System', frame)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ========== Cleanup ==========

# Release camera and destroy OpenCV windows
cap.release()
cv2.destroyAllWindows()
