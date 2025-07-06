import sqlite3
from pathlib import Path

def get_connection(path="demo.sqlite"):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def main():
    conn = get_connection()
    result = conn.execute("SELECT 1").fetchall()
    print("Test result:", result)
    conn.close()

if __name__ == "__main__":
    main()
