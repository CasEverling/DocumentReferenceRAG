# db_sqlite.py
import sqlite3
import os
from typing import Any, Iterable


DB_PATH = os.getenv("manuals.db")


class DataBase:
    def __init__(self):
        # Ensure directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def execute(self, sql: str, params: Iterable[Any] = ()):
        self.cursor.execute(sql, params)
        self.conn.commit()

    def query(self, sql: str, params: Iterable[Any] = ()):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception:
            pass

    def __del__(self):
        self.close()
