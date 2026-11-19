import mysql.connector
from rpms.util.config import DB_CONFIG

class Database:
    @staticmethod
    def connect():
        return mysql.connector.connect(**DB_CONFIG)

    @staticmethod
    def fetch_all(query, params=()):
        conn = Database.connect()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(query, params)
            return cur.fetchall()
        finally:
            cur.close(); conn.close()

    @staticmethod
    def execute(query, params=(), commit=True):
        conn = Database.connect()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            if commit: conn.commit()
            return cur.lastrowid
        except Exception:
            conn.rollback(); raise
        finally:
            cur.close(); conn.close()
