# db_check.py

import sqlite3

def query_all(conn, table):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    return cursor.fetchall()

def main():
    db_path = "/Users/cassio/Documents/Coding/RAG System/rag.db"

    conn = sqlite3.connect(db_path)

    print("\n======================")
    print("📘 MANUAL Records")
    print("======================")
    manuals = query_all(conn, "manual")
    for m in manuals:
        print(m)

    print("\n======================")
    print("📗 SECTION Records")
    print("======================")
    sections = query_all(conn, "section")
    for s in sections:
        print(s)

    print("\n======================")
    print("📙 IMAGE Records")
    print("======================")
    images = query_all(conn, "image")
    for img in images:
        print(img)

    conn.close()

if __name__ == "__main__":
    main()
