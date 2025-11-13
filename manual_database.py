# manual_database.py
from db_sqlite import DataBase


class ManualDatabase(DataBase):
    def __init__(self):
        super().__init__()
        self._ensure_tables()

    def _ensure_tables(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS MANUAL (
                ManualId INTEGER PRIMARY KEY AUTOINCREMENT,
                Make TEXT,
                Model TEXT,
                Year INTEGER,
                PoliceOrCivil TEXT
            );
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS SEARCH (
                ManualSectionId INTEGER PRIMARY KEY AUTOINCREMENT,
                ManualId INTEGER,
                ParentSectionId INTEGER,
                StartPage INTEGER,
                EndPage INTEGER,
                SectionName TEXT
            );
        """)

        self.execute("""
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

    # --- Inserts ---
    def add_manual(self, make: str, model: str, year: int, police_or_civil: str) -> int:
        self.execute(
            "INSERT INTO MANUAL (Make, Model, Year, PoliceOrCivil) VALUES (?, ?, ?, ?)",
            (make, model, year, police_or_civil),
        )
        return self.cursor.lastrowid

    def add_section(self, manual_id: int, parent_section_id, start_page: int, end_page: int, name: str) -> int:
        self.execute(
            "INSERT INTO SEARCH (ManualId, ParentSectionId, StartPage, EndPage, SectionName) VALUES (?, ?, ?, ?, ?)",
            (manual_id, parent_section_id, start_page, end_page, name),
        )
        return self.cursor.lastrowid

    def add_image(self, manual_id: int, page: int, x: float, y: float, w: float, h: float, desc: str) -> int:
        self.execute(
            "INSERT INTO IMAGES (ManualId, Page, X, Y, W, H, Description) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (manual_id, page, x, y, w, h, desc),
        )
        return self.cursor.lastrowid

    # --- Queries ---
    def get_manual(self, manual_id: int):
        rows = self.query("SELECT * FROM MANUAL WHERE ManualId = ?", (manual_id,))
        return rows[0] if rows else None

    def get_sections_by_manual(self, manual_id: int):
        return self.query("SELECT * FROM SEARCH WHERE ManualId = ?", (manual_id,))

    def get_images_by_manual(self, manual_id: int):
        return self.query("SELECT * FROM IMAGES WHERE ManualId = ?", (manual_id,))
