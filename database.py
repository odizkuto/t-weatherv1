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
        self.migrate_subscription_location()

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

    def migrate_subscription_location(self):
        """
        DB cũ (tạo trước khi có tính năng vị trí động) sẽ chưa có
        2 cột latitude/longitude -> thêm vào nếu thiếu, không xoá
        dữ liệu subscription hiện có.
        """

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(subscriptions)")

        existing_columns = [row[1] for row in cursor.fetchall()]

        if "latitude" not in existing_columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN latitude REAL")

        if "longitude" not in existing_columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN longitude REAL")

        if "updated_at" not in existing_columns:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN updated_at TEXT")

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

    def add_subscription(self, endpoint, p256dh, auth, latitude=None, longitude=None):

        conn = self.connect()

        cursor = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""

        INSERT INTO subscriptions(endpoint, p256dh, auth, latitude, longitude, created_at, updated_at)
        VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(endpoint) DO UPDATE SET
            p256dh = excluded.p256dh,
            auth = excluded.auth,
            latitude = excluded.latitude,
            longitude = excluded.longitude,
            updated_at = excluded.updated_at

        """, (

            endpoint,
            p256dh,
            auth,
            latitude,
            longitude,
            now,
            now

        ))

        conn.commit()

        conn.close()

    def update_subscription_location(self, endpoint, latitude, longitude):
        """
        Điện thoại di chuyển -> cập nhật lại vị trí mới nhất cho
        subscription này, để lần quét nền tiếp theo dùng đúng toạ độ.
        """

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

        UPDATE subscriptions
        SET latitude = ?, longitude = ?, updated_at = ?
        WHERE endpoint = ?

        """, (
            latitude,
            longitude,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            endpoint
        ))

        conn.commit()

        conn.close()

        return cursor.rowcount > 0

    def get_subscriptions(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute(
            "SELECT endpoint, p256dh, auth, latitude, longitude FROM subscriptions"
        )

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
