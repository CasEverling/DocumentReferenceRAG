# db_sqlite.py
import os
import sqlite3

DB_PATH = "./database/manuals.db"

class SQLiteDB:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def close(self):
        self.conn.close()

    def create_tables(self):
        cur = self.conn.cursor()

        # MANUALS
        cur.execute("""
        CREATE TABLE IF NOT EXISTS manuals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT,
            model TEXT,
            year INTEGER,
            police_or_civil TEXT
        );
        """)

        # SECTIONS
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manual_id INTEGER,
            parent_id INTEGER,
            start_page INTEGER,
            end_page INTEGER,
            description TEXT,
            level INTEGER,
            FOREIGN KEY(manual_id) REFERENCES manuals(id)
        );
        """)

        # IMAGES
        cur.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manual_id INTEGER,
            page_index INTEGER,
            x REAL, y REAL, w REAL, h REAL,
            text TEXT,
            FOREIGN KEY(manual_id) REFERENCES manuals(id)
        );
        """)

        self.conn.commit()

    # Insert manual
    def add_manual(self, make, model, year, police_or_civil):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO manuals (make, model, year, police_or_civil)
            VALUES (?, ?, ?, ?)
        """, (make, model, year, police_or_civil))
        self.conn.commit()
        return cur.lastrowid

    # Insert section
    def add_section(self, manual_id, parent_id, start_page, end_page, description, level):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO sections (manual_id, parent_id, start_page, end_page, description, level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (manual_id, parent_id, start_page, end_page, description, level))
        self.conn.commit()

    # Insert image
    def add_image(self, manual_id, page_index, x, y, w, h, text):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO images (manual_id, page_index, x, y, w, h, text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (manual_id, page_index, x, y, w, h, text))
        self.conn.commit()
