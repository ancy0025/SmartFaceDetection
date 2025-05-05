from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import os
import logging
import socket
import atexit
import sys

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# Check if port is available
def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) != 0

# Database setup for users and attendance
def init_users_db():
    db_path = 'smartface.db'
    try:
        if os.path.exists(db_path):
            logging.info(f"Checking database: {db_path}")
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = c.fetchall()
            conn.close()
            if not tables:
                logging.warning(f"Empty or invalid database detected. Removing {db_path}")
                os.remove(db_path)
        else:
            logging.info(f"No existing database found at {db_path}. Creating new one.")
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {e}. Removing {db_path}")
        if os.path.exists(db_path):
            os.remove(db_path)
    
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, password_hash TEXT, role TEXT)''')
        admin_password = generate_password_hash('admin123', method='pbkdf2:sha256')
        c.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                  ('admin', admin_password, 'admin'))
        c.execute('''CREATE TABLE IF NOT EXISTS attendance
                     (name TEXT, time TEXT, date TEXT)''')
        conn.commit()
        logging.info("Users and attendance tables initialized successfully")
    except sqlite3.DatabaseError as e:
        logging.error(f"Failed to initialize database: {e}")
        raise
    finally:
        conn.close()

@app.route('/')
def index():
    logging.info("Accessing root URL")
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = sqlite3.connect('smartface.db', check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            conn.close()
            if user and check_password_hash(user[0], password):
                session['username'] = username
                session['role'] = user[1]
                flash('Login successful!', 'success')
                logging.info(f"User {username} logged in")
                return redirect(url_for('dashboard'))
            flash('Invalid username or password', 'danger')
            logging.warning(f"Failed login attempt for {username}")
        except sqlite3.DatabaseError as e:
            flash(f"Database error: {e}. Please contact the administrator.", 'danger')
            logging.error(f"Login database error: {e}")
    logging.info("Rendering login page")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' not in session or session['role'] != 'admin':
        flash('Only admins can register new users', 'danger')
        logging.warning("Unauthorized access to register page")
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        try:
            conn = sqlite3.connect('smartface.db', check_same_thread=False)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                      (username, password_hash, role))
            conn.commit()
            flash('User registered successfully!', 'success')
            logging.info(f"User {username} registered with role {role}")
        except sqlite3.IntegrityError:
            flash('Username already exists', 'danger')
            logging.warning(f"Registration failed: Username {username} already exists")
        except sqlite3.DatabaseError as e:
            flash(f"Database error: {e}", 'danger')
            logging.error(f"Registration database error: {e}")
        finally:
            conn.close()
        return redirect(url_for('register'))
    logging.info("Rendering register page")
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        logging.warning("Unauthorized dashboard access; redirecting to login")
        return redirect(url_for('login'))
    try:
        conn = sqlite3.connect('smartface.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT name, time, date FROM attendance ORDER BY date DESC, time DESC")
        attendance = c.fetchall()
        conn.close()
        logging.info("Attendance data fetched for dashboard")
    except sqlite3.DatabaseError as e:
        flash(f"Database error: {e}", 'danger')
        logging.error(f"Dashboard database error: {e}")
        attendance = []
    logging.info(f"Rendering dashboard for user {session['username']}")
    return render_template('dashboard.html', attendance=attendance, username=session['username'], role=session['role'])

@app.route('/start_recognition')
def start_recognition():
    if 'username' not in session:
        logging.warning("Unauthorized access to start_recognition; redirecting to login")
        return redirect(url_for('login'))
    try:
        # Run face_recognition_live.py as a subprocess with full Python path
        python_path = sys.executable  # Use the same Python as the Flask app
        script_path = os.path.join(os.getcwd(), 'face_recognition_live.py')
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"face_recognition_live.py not found at {script_path}")
        log_file = 'face_recognition_log.txt'
        with open(log_file, 'a') as f:
            process = subprocess.Popen([python_path, script_path], stdout=f, stderr=f)
            logging.info(f"Face recognition started via subprocess with PID {process.pid}")
        flash('Face recognition started', 'success')
    except Exception as e:
        flash(f"Failed to start face recognition: {e}", 'danger')
        logging.error(f"Subprocess error: {e}")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    username = session.get('username', 'unknown')
    session.pop('username', None)
    session.pop('role', None)
    flash('Logged out successfully!', 'success')
    logging.info(f"User {username} logged out")
    return redirect(url_for('login'))

def shutdown_server():
    logging.info("Cleaning up server resources")
    os._exit(0)

if __name__ == '__main__':
    port = 8000
    if not is_port_available(port):
        logging.error(f"Port {port} is already in use. Please free it or choose another port.")
        exit(1)
    atexit.register(shutdown_server)
    try:
        init_users_db()
        logging.info("Starting Flask app")
        app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
    except KeyboardInterrupt:
        logging.info("Shutting down Flask app")
    except Exception as e:
        logging.error(f"Server error: {e}")