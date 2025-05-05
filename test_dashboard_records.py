import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def insert_test_records():
    try:
        conn = sqlite3.connect('smartface.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS attendance
                     (name TEXT, time TEXT, date TEXT)''')
        test_records = [
            ("Anurag", "10:00:00", "2025-05-04"),
            ("TestUser", "10:01:00", "2025-05-04")
        ]
        c.executemany("INSERT INTO attendance (name, time, date) VALUES (?, ?, ?)", test_records)
        conn.commit()
        logging.info(f"Inserted {len(test_records)} test records")
        c.execute("SELECT * FROM attendance")
        records = c.fetchall()
        logging.info(f"Records in attendance: {records}")
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    insert_test_records()