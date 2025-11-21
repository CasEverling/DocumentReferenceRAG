# manual_database.py
import sqlite3
import os

DB_PATH = "data/Manuals.db"

class ManualDatabase:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS MANUAL (
                ManualId INTEGER PRIMARY KEY AUTOINCREMENT,
                Make TEXT,
                Model TEXT,
                Year INTEGER,
                PoliceOrCivil TEXT
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SECTIONS (
                SectionId INTEGER PRIMARY KEY AUTOINCREMENT,
                ManualId INTEGER,
                Level INTEGER,
                Page INTEGER,
                Description TEXT
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS IMAGES (
                ImageId INTEGER PRIMARY KEY AUTOINCREMENT,
                ManualId INTEGER,
                Page INTEGER,
                X REAL,
                Y REAL,
                W REAL,
                H REAL,
                Description TEXT
            );
        """)

        self.conn.commit()

    # ---- Insertions ----
    def add_manual(self, make, model, year, police_or_civil):
        self.cursor.execute(
            "INSERT INTO MANUAL (Make, Model, Year, PoliceOrCivil) VALUES (?, ?, ?, ?)",
            (make, model, year, police_or_civil)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def add_section(self, manual_id, level, page, description):
        self.cursor.execute(
            "INSERT INTO SECTIONS (ManualId, Level, Page, Description) VALUES (?, ?, ?, ?)",
            (manual_id, level, page, description)
        )
        self.conn.commit()

    def add_image(self, manual_id, page, x, y, w, h, desc):
        self.cursor.execute(
            "INSERT INTO IMAGES (ManualId, Page, X, Y, W, H, Description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (manual_id, page, x, y, w, h, desc)
        )
        self.conn.commit()

    def __del__(self):
        try:
            self.conn.close()
        except:
            pass
