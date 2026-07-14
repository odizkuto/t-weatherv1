"""
=========================================
T-Weather
database.py
SQLite Database
=========================================
"""

import sqlite3
from datetime import datetime

from config import DATABASE


class Database:

    def __init__(self):

        self.create_table()
        self.create_subscription_table()

    def connect(self):

        return sqlite3.connect(DATABASE)

    def create_table(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS weather_history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            time TEXT,

            temperature REAL,

            humidity REAL,

            rain REAL,

            rain_probability REAL,

            cloud REAL,

            uv REAL,

            wind REAL,

            status TEXT,

            created_at TEXT

        )

        """)

        conn.commit()

        conn.close()

    def create_subscription_table(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

        CREATE TABLE IF NOT EXISTS subscriptions(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            endpoint TEXT UNIQUE,

            p256dh TEXT,

            auth TEXT,

            created_at TEXT

        )

        """)

        conn.commit()

        conn.close()

    def save(self, weather, status):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

        INSERT INTO weather_history(

            time,

            temperature,

            humidity,

            rain,

            rain_probability,

            cloud,

            uv,

            wind,

            status,

            created_at

        )

        VALUES(?,?,?,?,?,?,?,?,?,?)

        """, (

            weather["time"],

            weather["temperature"],

            weather["humidity"],

            weather["rain"],

            weather["rain_probability"],

            weather["cloud"],

            weather["uv"],

            weather["wind"],

            status,

            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ))

        conn.commit()

        conn.close()

    def latest(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

        SELECT *

        FROM weather_history

        ORDER BY id DESC

        LIMIT 1

        """)

        row = cursor.fetchone()

        conn.close()

        return row

    def history(self, limit=50):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

        SELECT *

        FROM weather_history

        ORDER BY id DESC

        LIMIT ?

        """, (limit,))

        rows = cursor.fetchall()

        conn.close()

        return rows

    def add_subscription(self, endpoint, p256dh, auth):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

        INSERT OR IGNORE INTO subscriptions(endpoint, p256dh, auth, created_at)
        VALUES(?,?,?,?)

        """, (

            endpoint,
            p256dh,
            auth,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ))

        conn.commit()

        conn.close()

    def get_subscriptions(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("SELECT endpoint, p256dh, auth FROM subscriptions")

        rows = cursor.fetchall()

        conn.close()

        return rows

    def remove_subscription(self, endpoint):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("DELETE FROM subscriptions WHERE endpoint = ?", (endpoint,))

        conn.commit()

        conn.close()


db = Database()


if __name__ == "__main__":

    print(db.latest())
