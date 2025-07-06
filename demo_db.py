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

def insert_sample_data(conn):
    # Insert users
    users = [
        (1, 'Admin User', 'Admin'),
        (2, 'Editor User', 'Editor'),
        (3, 'Viewer User', 'Viewer')
    ]
    conn.executemany('INSERT INTO user (id, name, role) VALUES (?, ?, ?);', users)

    # Insert persons
    persons = [
        (1, 'Person One', 1),
        (2, 'Person Two', 1),
        (3, 'Person Three', 2),
        (4, 'Person Four', 2),
        (5, 'Person Five', 3)
    ]
    conn.executemany('INSERT INTO person (id, name, created_by) VALUES (?, ?, ?);', persons)

    # Insert notes
    notes = []
    note_id = 1
    for person_id in range(1, 6):
        for _ in range(4):  # 4 notes per person
            notes.append((note_id, f'Note {note_id}', person_id % 3 + 1, person_id))
            note_id += 1
    conn.executemany('INSERT INTO note (id, content, created_by, person_id) VALUES (?, ?, ?, ?);', notes)

    # Insert user_person assignments
    user_person_assignments = [
        (1, 1), (1, 2), (2, 3), (2, 4), (3, 5)
    ]
    conn.executemany('INSERT INTO user_person (user_id, person_id) VALUES (?, ?);', user_person_assignments)

    # Insert user_note assignments
    user_note_assignments = [(user_id, note_id) for user_id in range(1, 4) for note_id in range(1, 21)]
    conn.executemany('INSERT INTO user_note (user_id, note_id) VALUES (?, ?);', user_note_assignments)

def main():
    conn = get_connection()
    create_schema(conn)
    insert_sample_data(conn)
    result = conn.execute("SELECT 1").fetchall()
    print("Test result:", result)
    conn.close()

if __name__ == "__main__":
    main()
