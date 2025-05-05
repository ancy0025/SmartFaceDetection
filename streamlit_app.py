import streamlit as st
import sqlite3
import face_recognition
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import os
import logging
from PIL import Image

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Database initialization
def init_db():
    try:
        conn = sqlite3.connect('smartface.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS attendance
                     (name TEXT, time TEXT, date TEXT)''')
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", ("admin", "admin123"))
        conn.commit()
        logging.info("Database initialized")
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

# Load known faces
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

# Recognize faces in uploaded image
def recognize_faces(image, known_face_encodings, known_face_names):
    confidence_threshold = 0.6
    recognized_faces = []
    rgb_image = np.array(image.convert('RGB'))
    small_image = cv2.resize(rgb_image, (0, 0), fx=0.25, fy=0.25)
    face_locations = face_recognition.face_locations(small_image)
    face_encodings = face_recognition.face_encodings(small_image, face_locations)
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
                recognized_faces.append(name)
                # Log to database
                current_time = datetime.now().strftime("%H:%M:%S")
                current_date = datetime.now().strftime("%Y-%m-%d")
                try:
                    conn = sqlite3.connect('smartface.db', check_same_thread=False)
                    c = conn.cursor()
                    c.execute("INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)",
                              (name, current_time, current_date))
                    conn.commit()
                    logging.info(f"Attendance marked for {name}")
                except sqlite3.DatabaseError as e:
                    logging.error(f"Database error: {e}")
                finally:
                    conn.close()
    return recognized_faces, face_locations

# Export attendance to Excel
def export_to_excel():
    try:
        conn = sqlite3.connect('smartface.db')
        df = pd.read_sql_query("SELECT * FROM attendance", conn)
        conn.close()
        df.to_excel('attendance_export.xlsx', index=False)
        logging.info("Attendance exported to attendance_export.xlsx")
        return df
    except Exception as e:
        logging.error(f"Excel export error: {e}")
        return pd.DataFrame()

# Main app
def main():
    init_db()
    st.set_page_config(page_title="Face Recognition Attendance System", layout="wide")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if not st.session_state.logged_in:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            conn = sqlite3.connect('smartface.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
            conn.close()

        st.subheader("Register")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            conn = sqlite3.connect('smartface.db')
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users VALUES (?, ?)", (new_username, new_password))
                conn.commit()
                st.success("Registered successfully! Please login.")
            except sqlite3.IntegrityError:
                st.error("Username already exists")
            finally:
                conn.close()
    else:
        st.title(f"Welcome, {st.session_state.username}")
        st.sidebar.title("Menu")
        page = st.sidebar.selectbox("Select Page", ["Face Recognition", "Dashboard", "Logout"])

        if page == "Logout":
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.experimental_rerun()

        elif page == "Face Recognition":
            st.header("Face Recognition")
            uploaded_file = st.file_uploader("Upload an image for face recognition", type=["jpg", "jpeg", "png"])
            known_face_encodings, known_face_names = load_known_faces()
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                if known_face_encodings:
                    recognized_faces, face_locations = recognize_faces(image, known_face_encodings, known_face_names)
                    if recognized_faces:
                        st.success(f"Recognized: {', '.join(recognized_faces)}")
                    else:
                        st.warning("No known faces recognized")
                else:
                    st.error("No known faces loaded. Add images to 'images/' folder.")

        elif page == "Dashboard":
            st.header("Attendance Dashboard")
            df = export_to_excel()
            if not df.empty:
                st.dataframe(df)
            else:
                st.warning("No attendance records found")
            if st.button("Download Attendance"):
                df.to_csv("attendance.csv", index=False)
                with open("attendance.csv", "rb") as file:
                    st.download_button("Download CSV", file, "attendance.csv")

if __name__ == "__main__":
    main()
