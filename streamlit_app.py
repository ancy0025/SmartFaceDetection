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
import bcrypt

# ---------------------- Logging Setup ----------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------------- Database Setup ----------------------
def init_db():
    conn = sqlite3.connect('smartface.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    name TEXT,
                    time TEXT,
                    date TEXT
                )''')

    # Insert default admin user if not exists
    c.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not c.fetchone():
        hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt())
        c.execute("INSERT INTO users VALUES (?, ?)", ("admin", hashed_pw))
    conn.commit()
    conn.close()

# ---------------------- Face Recognition ----------------------
def load_known_faces(images_path='images'):
    known_encodings = []
    known_names = []

    if not os.path.exists(images_path):
        os.makedirs(images_path)
        return [], []

    for file in os.listdir(images_path):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            image = face_recognition.load_image_file(os.path.join(images_path, file))
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(os.path.splitext(file)[0])
    return known_encodings, known_names

def recognize_faces(image, known_encodings, known_names):
    rgb_image = np.array(image.convert('RGB'))
    small_image = cv2.resize(rgb_image, (0, 0), fx=0.25, fy=0.25)

    locations = face_recognition.face_locations(small_image)
    encodings = face_recognition.face_encodings(small_image, locations)
    recognized = []

    for encoding in encodings:
        matches = face_recognition.compare_faces(known_encodings, encoding)
        name = "Unknown"
        if matches:
            distances = face_recognition.face_distance(known_encodings, encoding)
            best_match_index = np.argmin(distances)
            if matches[best_match_index] and distances[best_match_index] < 0.6:
                name = known_names[best_match_index]
                recognized.append(name)
                save_attendance(name)
    return recognized

def save_attendance(name):
    conn = sqlite3.connect('smartface.db')
    c = conn.cursor()
    now = datetime.now()
    c.execute("INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)", 
              (name, now.strftime("%H:%M:%S"), now.strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

# ---------------------- Authentication ----------------------
def verify_user(username, password):
    conn = sqlite3.connect('smartface.db')
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return bcrypt.checkpw(password.encode(), result[0])
    return False

def register_user(username, password):
    conn = sqlite3.connect('smartface.db')
    c = conn.cursor()
    try:
        hash_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hash_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# ---------------------- Streamlit App ----------------------
def export_attendance():
    conn = sqlite3.connect('smartface.db')
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    conn.close()
    return df

def main():
    st.set_page_config(page_title="Smart Face Attendance", layout="wide")
    init_db()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

        st.subheader("Register")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("User registered. Please login.")
            else:
                st.warning("Username already exists.")
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        option = st.sidebar.selectbox("Choose Option", ["Face Recognition", "Dashboard", "Logout"])

        if option == "Logout":
            st.session_state.logged_in = False
            st.experimental_rerun()

        elif option == "Face Recognition":
            st.title("Face Recognition")
            uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
            known_encodings, known_names = load_known_faces()

            if uploaded:
                image = Image.open(uploaded)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                if known_encodings:
                    results = recognize_faces(image, known_encodings, known_names)
                    if results:
                        st.success("Recognized: " + ", ".join(results))
                    else:
                        st.warning("No known faces detected.")
                else:
                    st.warning("No known faces loaded. Please add face images to /images folder.")

        elif option == "Dashboard":
            st.title("Attendance Records")
            df = export_attendance()
            if not df.empty:
                st.dataframe(df)
                st.download_button("Download CSV", df.to_csv(index=False), "attendance.csv", "text/csv")
            else:
                st.warning("No records found.")

if __name__ == "__main__":
    main()
