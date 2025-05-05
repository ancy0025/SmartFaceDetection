import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_db_write():
    try:
        conn = sqlite3.connect('smartface.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS attendance
                     (name TEXT, time TEXT, date TEXT)''')
        name = "TestUser"
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        c.execute("INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)",
                  (name, current_time, current_date))
        conn.commit()
        logging.info(f"Inserted test record for {name}")
        c.execute("SELECT * FROM attendance")
        records = c.fetchall()
        logging.info(f"Records in attendance: {records}")
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    test_db_write()