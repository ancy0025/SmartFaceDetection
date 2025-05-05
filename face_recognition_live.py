import cv2
import face_recognition
import numpy as np
import sqlite3
import pandas as pd
from datetime import datetime
import os
import logging
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def init_attendance_db():
    try:
        conn = sqlite3.connect('smartface.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS attendance
                     (name TEXT, time TEXT, date TEXT)''')
        conn.commit()
        logging.info("Attendance table initialized")
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

def load_known_faces(images_path='images'):
    known_face_encodings = []
    known_face_names = []
    if not os.path.exists(images_path):
        logging.error(f"Images folder {images_path} not found")
        return [], []
    for image_file in os.listdir(images_path):
        if image_file.endswith('.jpg'):
            image_path = os.path.join(images_path, image_file)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(os.path.splitext(image_file)[0])
                logging.info(f"Loaded face encoding for {known_face_names[-1]}")
            else:
                logging.warning(f"No face encodings found in {image_file}")
    return known_face_encodings, known_face_names

def export_to_excel():
    try:
        conn = sqlite3.connect('smartface.db')
        df = pd.read_sql_query("SELECT * FROM attendance", conn)
        conn.close()
        df.to_excel('attendance_export.xlsx', index=False)
        logging.info("Attendance exported to attendance_export.xlsx")
    except Exception as e:
        logging.error(f"Excel export error: {e}")

def run_face_recognition():
    init_attendance_db()
    known_face_encodings, known_face_names = load_known_faces()
    if not known_face_encodings:
        logging.error("No known faces loaded. Exiting.")
        return

    webcam_index = 0
    backends = [(cv2.CAP_AVFOUNDATION, "CAP_AVFOUNDATION"), (cv2.CAP_ANY, "CAP_ANY"), (cv2.CAP_V4L2, "CAP_V4L2")]
    cap = None
    for backend, backend_name in backends:
        logging.info(f"Trying webcam at index {webcam_index} with {backend_name}")
        cap = cv2.VideoCapture(webcam_index, backend)
        if cap.isOpened():
            logging.info(f"Webcam opened with index {webcam_index} and {backend_name}")
            break
        logging.warning(f"Failed to open webcam with {backend_name}")
        cap.release()
    else:
        logging.error(f"Could not open webcam at index {webcam_index}. Check permissions or hardware.")
        return

    # Set webcam resolution to improve quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    time.sleep(2)  # Stabilize camera

    retries = 5
    for attempt in range(retries):
        ret, frame = cap.read()
        if ret:
            logging.info("Successfully read frame")
            break
        logging.warning(f"Failed to read frame, attempt {attempt + 1}/{retries}")
        time.sleep(1)
    else:
        logging.error(f"Failed to read frames after {retries} attempts. Exiting.")
        cap.release()
        return

    confidence_threshold = 0.6  # Lowered from 0.85
    recognized_faces = set()
    process_this_frame = True

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error("Failed to read frame from webcam")
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        if process_this_frame:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            logging.info(f"Detected {len(face_locations)} faces")

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    confidence = 1 - face_distances[best_match_index]
                    logging.info(f"Best match confidence: {confidence:.2f} for {known_face_names[best_match_index]}")
                    if matches[best_match_index] and confidence >= confidence_threshold:
                        name = known_face_names[best_match_index]
                        logging.info(f"Recognized {name} with confidence {confidence:.2f}")

                        if name not in recognized_faces:
                            recognized_faces.add(name)
                            current_time = datetime.now().strftime("%H:%M:%S")
                            current_date = datetime.now().strftime("%Y-%m-%d")
                            try:
                                conn = sqlite3.connect('smartface.db', check_same_thread=False)
                                c = conn.cursor()
                                c.execute("INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)",
                                          (name, current_time, current_date))
                                conn.commit()
                                logging.info(f"Attendance marked for {name}")
                                c.execute("SELECT * FROM attendance WHERE name = ?", (name,))
                                logging.info(f"Verified record: {c.fetchall()}")
                            except sqlite3.DatabaseError as e:
                                logging.error(f"Database error: {e}")
                            finally:
                                conn.close()

        process_this_frame = not process_this_frame

        for (top, right, bottom, left) in face_locations:
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, f"Attendance Marked: {name}", (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.putText(frame, f"Attendees: {len(recognized_faces)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    export_to_excel()
    logging.info(f"Recognition ended. Total attendees: {len(recognized_faces)}")

if __name__ == '__main__':
    run_face_recognition()