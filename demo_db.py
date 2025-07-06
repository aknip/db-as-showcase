import sqlite3
from pathlib import Path

def get_connection(path="demo.sqlite"):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_schema(conn):
    conn.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT CHECK(role IN ('Admin', 'Editor', 'Viewer'))
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS person (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        created_by INTEGER,
        FOREIGN KEY(created_by) REFERENCES user(id)
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS note (
        id INTEGER PRIMARY KEY,
        content TEXT NOT NULL,
        created_by INTEGER,
        person_id INTEGER,
        FOREIGN KEY(created_by) REFERENCES user(id),
        FOREIGN KEY(person_id) REFERENCES person(id)
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS user_person (
        user_id INTEGER,
        person_id INTEGER,
        PRIMARY KEY(user_id, person_id),
        FOREIGN KEY(user_id) REFERENCES user(id),
        FOREIGN KEY(person_id) REFERENCES person(id)
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS user_note (
        user_id INTEGER,
        note_id INTEGER,
        PRIMARY KEY(user_id, note_id),
        FOREIGN KEY(user_id) REFERENCES user(id),
        FOREIGN KEY(note_id) REFERENCES note(id)
    );
    ''')

def main():
    conn = get_connection()
    create_schema(conn)
    result = conn.execute("SELECT 1").fetchall()
    print("Test result:", result)
    conn.close()

if __name__ == "__main__":
    main()
