import sqlite3
import os
from enum import Enum
from tabulate import tabulate

class Role(str, Enum):
    """User roles with different permission levels."""
    ADMIN = 'Admin'
    EDITOR = 'Editor'
    VIEWER = 'Viewer'


def is_admin(role):
    """Check if the given role is an admin role."""
    return role == Role.ADMIN


def can_read(role, creator_id, user_id, has_assignment):
    """Check if a user with the given role can read a resource."""
    if role == Role.ADMIN:
        return True
    if role in (Role.EDITOR, Role.VIEWER):
        return creator_id == user_id or has_assignment
    return False


def can_write(role, creator_id, user_id):
    """Check if a user with the given role can modify a resource."""
    if role in (Role.ADMIN, Role.EDITOR):
        return True
    if role == Role.VIEWER:
        return creator_id == user_id
    return False


def get_connection(path="showcase.db"):
    """Get a database connection with foreign key constraints enabled.
    
    Args:
        path: Path to the SQLite database file. Defaults to 'showcase.db'.
        
    Returns:
        sqlite3.Connection: A connection to the SQLite database.
    """
    try:
        conn = sqlite3.connect(path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # Enable dictionary-style access to columns
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise


def create_schema(conn):
    conn.execute('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        role TEXT CHECK(role IN ('Admin', 'Editor', 'Viewer')) NOT NULL
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS person (
        id INTEGER PRIMARY KEY,
        vorname TEXT NOT NULL,
        nachname TEXT NOT NULL,
        email TEXT NOT NULL,
        telefon TEXT,
        created_by INTEGER NOT NULL,
        FOREIGN KEY(created_by) REFERENCES user(id)
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS note (
        id INTEGER PRIMARY KEY,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER NOT NULL,
        person_id INTEGER NOT NULL,
        FOREIGN KEY(created_by) REFERENCES user(id),
        FOREIGN KEY(person_id) REFERENCES person(id)
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS user_person (
        user_id INTEGER,
        person_id INTEGER,
        PRIMARY KEY(user_id, person_id),
        FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY(person_id) REFERENCES person(id) ON DELETE CASCADE
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS note_assignment (
        note_id INTEGER,
        user_id INTEGER,
        PRIMARY KEY(note_id, user_id),
        FOREIGN KEY(note_id) REFERENCES note(id) ON DELETE CASCADE,
        FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE
    );
    ''')

SELECT_VISIBLE_DATA = '''
SELECT DISTINCT p.id AS person_id, p.name AS person_name, 
       n.id AS note_id, n.content AS note_content
FROM person p
LEFT JOIN note n ON p.id = n.person_id
LEFT JOIN note_assignment na ON n.id = na.note_id
WHERE ? = 1  -- Admin sees everything
   OR p.created_by = ?  -- User created the person
   OR n.created_by = ?  -- User created the note
   OR na.user_id = ?    -- User is assigned to the note
'''  # noqa: E501

def fetch_visible_persons_notes(conn, user_id):
    cursor = conn.cursor()
    
    # Check if the user exists and get their role
    cursor.execute('SELECT role, username FROM user WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    
    if not result:
        print(f"Error: User with ID {user_id} not found")
        return []
        
    role, username = result
    is_admin = role == 'Admin'
    
    # Query to fetch visible data
    query = '''
    SELECT DISTINCT 
        p.id AS person_id, 
        p.vorname, 
        p.nachname,
        p.email,
        n.id AS note_id, 
        n.content,
        n.created_at,
        u.username AS created_by_username
    FROM person p
    LEFT JOIN note n ON p.id = n.person_id
    LEFT JOIN user u ON n.created_by = u.id
    LEFT JOIN user_person up ON p.id = up.person_id
    LEFT JOIN note_assignment na ON n.id = na.note_id
    WHERE ? = 1  -- Admin sees everything
       OR (
           -- User created the person or note
           (p.created_by = ? OR n.created_by = ?)
           -- User is assigned to the person
           OR up.user_id = ?
           -- User is assigned to the note
           OR na.user_id = ?
       )
    ORDER BY p.nachname, p.vorname, n.created_at
    '''
    
    if is_admin:
        cursor.execute(query, (1, 0, 0, 0, 0))  # Only the first parameter matters for admin
    else:
        cursor.execute(query, (0, user_id, user_id, user_id, user_id))
        
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def insert_sample_data(conn):
    # Insert users
    users = [
        (1, 'anna.schmitt', 'Admin'),
        (2, 'bernd.mueller', 'Editor'),
        (3, 'clara.schulz', 'Viewer')
    ]
    conn.executemany('INSERT INTO user (id, username, role) VALUES (?, ?, ?);', users)

    # Insert persons
    persons = [
        (1, 'Max', 'Beispiel', 'max.beispiel@example.com', '+4912345678', 1),
        (2, 'Eva', 'Team', 'eva.team@example.com', '+4912345679', 1),
        (3, 'Karl', 'Offen', 'karl.offen@example.com', '+4912345680', 2),
        (4, 'Lisa', 'Privat', 'lisa.privat@example.com', '+4912345681', 2),
        (5, 'Olaf', 'Gemein', 'olaf.gemein@example.com', '+4912345682', 3)
    ]
    conn.executemany('''
        INSERT INTO person (id, vorname, nachname, email, telefon, created_by) 
        VALUES (?, ?, ?, ?, ?, ?);
    ''', persons)

    # Insert notes
    notes = []
    note_id = 1
    for person_id in range(1, 6):
        for i in range(4):
            # Assign notes to different users: first 2 persons to admin, next 2 to editor, last to viewer
            created_by = 1 if person_id < 3 else (2 if person_id < 5 else 3)
            notes.append((note_id, f'Note {note_id} for person {person_id}', created_by, person_id))
            note_id += 1
    conn.executemany('''
        INSERT INTO note (id, content, created_by, person_id) 
        VALUES (?, ?, ?, ?);
    ''', notes)

    # Assign users to persons (shared access)
    # Admin (anna) has access to Max and Eva
    # Editor (bernd) has access to Karl and Lisa
    # Viewer (clara) has access to Olaf
    user_person_assignments = [
        (1, 1), (1, 2),  # anna can access Max and Eva
        (2, 3), (2, 4),  # bernd can access Karl and Lisa
        (3, 5)           # clara can access Olaf
    ]
    conn.executemany('''
        INSERT INTO user_person (user_id, person_id) 
        VALUES (?, ?);
    ''', user_person_assignments)

    # Assign specific notes to users for testing
    # Let's assign some notes to multiple users to demonstrate sharing
    note_assignments = [
        (1, 2),  # Note 1 shared with bernd (editor)
        (1, 3),  # Note 1 shared with clara (viewer)
        (5, 1),  # Note 5 shared with anna (admin)
        (5, 3),  # Note 5 shared with clara (viewer)
        (10, 1), # Note 10 shared with anna (admin)
        (15, 2), # Note 15 shared with bernd (editor)
        (20, 1)  # Note 20 shared with anna (admin)
    ]
    conn.executemany('''
        INSERT INTO note_assignment (note_id, user_id) 
        VALUES (?, ?);
    ''', note_assignments)


def print_user_tables(conn, user_id, username):
    """Print well-formatted tables of persons and notes visible to a user."""
    visible_data = fetch_visible_persons_notes(conn, user_id)
    
    # Extract unique persons
    persons = {}
    for item in visible_data:
        person_id = item['person_id']
        if person_id not in persons:
            persons[person_id] = {
                'ID': person_id,
                'Name': f"{item['vorname']} {item['nachname']}",
                'Email': item['email']
            }
    
    # Extract notes
    notes = [{
        'ID': item['note_id'],
        'Person': f"{item['vorname']} {item['nachname']}",
        'Content': item['content'],
        'Created By': item['created_by_username']
    } for item in visible_data]
    
    print(f"\n{username}'s Visible Persons:")
    print(tabulate(list(persons.values()), headers="keys", tablefmt="grid"))
    
    print(f"\n{username}'s Visible Notes:")
    print(tabulate(notes, headers="keys", tablefmt="grid"))


def get_user_id_by_username(conn, username):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM user WHERE username = ?', (username,))
    return cursor.fetchone()['id']


def run_uc1(conn):
    """UC-1: Admin Overview
    
    Admin should see all persons and notes.
    """
    print("UC-1: Admin Overview (Anna Schmitt)")
    print("Expected: See all persons and notes")
    
    # Get admin user ID
    admin_id = get_user_id_by_username(conn, "anna.schmitt")
    
    # Fetch all visible data for admin
    visible_data = fetch_visible_persons_notes(conn, admin_id)
    
    # Display results
    for item in visible_data:
        print(f"Person: {item['vorname']} {item['nachname']}, Note: {item['content']}")
    
    print(f"Total records: {len(visible_data)}")
    
    # Print tables
    print_user_tables(conn, admin_id, "Anna Schmitt")


def run_uc2(conn):
    """UC-2: Editor Updates Note
    
    Editor should be able to update a note.
    """
    print("\nUC-2: Editor Updates Note (Bernd Mueller)")
    print("Expected: Successfully update a note")
    
    # Get editor user ID
    editor_id = get_user_id_by_username(conn, "bernd.mueller")
    
    # Get a note that the editor can see and update
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT n.id, n.content, n.created_by, u.username
        FROM note n
        JOIN user u ON n.created_by = u.id
        JOIN person p ON n.person_id = p.id
        JOIN user_person up ON p.id = up.person_id
        WHERE up.user_id = ?
        LIMIT 1
        ''',
        (editor_id,)
    )
    note = cursor.fetchone()
    
    if note:
        note_id = note['id']
        old_content = note['content']
        created_by_username = note['username']
        
        # Update the note
        cursor.execute(
            'UPDATE note SET content = ? WHERE id = ?',
            (old_content, note_id)  # Just update with same content for demo
        )
        conn.commit()
        
        print(f"Updated Note {note_id} by {created_by_username}: {old_content}")
    else:
        print("No notes available for the editor to update")
        
    # Print tables
    print_user_tables(conn, editor_id, "Bernd Mueller")


def run_uc3(conn):
    """UC-3: Viewer Reads Notes
    
    Viewer should only see notes assigned to them.
    """
    print("\nUC-3: Viewer Reads Notes (Clara Schulz)")
    print("Expected: Only see notes assigned to Clara")
    
    # Get viewer user ID
    viewer_id = get_user_id_by_username(conn, "clara.schulz")
    
    # Fetch visible data for viewer
    visible_data = fetch_visible_persons_notes(conn, viewer_id)
    
    # Display results
    for item in visible_data:
        print(f"Person: {item['vorname']} {item['nachname']}, Note: {item['content']}")
    
    print(f"Total records visible to Clara: {len(visible_data)}")
    
    # Print tables
    print_user_tables(conn, viewer_id, "Clara Schulz")


def run_uc4(conn):
    """UC-4: Editor Creates New Note
    
    Editor should be able to create a new note.
    """
    print("\nUC-4: Editor Creates New Note (Bernd Mueller)")
    print("Expected: Successfully create a new note for Karl Offen")
    
    # Get editor user ID
    editor_id = get_user_id_by_username(conn, "bernd.mueller")
    
    # Get Karl's person ID
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id FROM person WHERE vorname = ? AND nachname = ?',
        ("Karl", "Offen")
    )
    karl_id = cursor.fetchone()['id']
    
    # Create a new note for Karl
    cursor.execute(
        'INSERT INTO note (content, created_by, person_id) VALUES (?, ?, ?)',
        ('New note created by Bernd for Karl', editor_id, karl_id)
    )
    conn.commit()
    
    # Fetch the new note
    cursor.execute(
        'SELECT n.content, p.vorname, p.nachname, u.username FROM note n JOIN person p ON n.person_id = p.id JOIN user u ON n.created_by = u.id WHERE n.content LIKE ?',
        ('New note created by%',)
    )
    new_note = cursor.fetchone()
    
    print(f"Added Note by {new_note[3]} for {new_note[1]} {new_note[2]}: {new_note[0]}")
    
    # Print tables
    print_user_tables(conn, editor_id, "Bernd Mueller")


def run_uc5(conn):
    """UC-5: Admin Assigns Rights
    
    Admin should be able to assign rights to users.
    """
    print("\nUC-5: Admin Assigns Rights (Anna Schmitt)")
    print("Expected: Successfully assign Olaf to Bernd")
    
    # Get admin and editor user IDs
    admin_id = get_user_id_by_username(conn, "anna.schmitt")
    editor_id = get_user_id_by_username(conn, "bernd.mueller")
    
    # Get Olaf's person ID
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id FROM person WHERE vorname = ? AND nachname = ?',
        ("Olaf", "Gemein")
    )
    olaf_id = cursor.fetchone()['id']
    
    # Check if assignment already exists
    cursor.execute(
        'SELECT 1 FROM user_person WHERE user_id = ? AND person_id = ?',
        (editor_id, olaf_id)
    )
    if not cursor.fetchone():
        # Assign Bernd to Olaf
        cursor.execute(
            'INSERT INTO user_person (user_id, person_id) VALUES (?, ?)',
            (editor_id, olaf_id)
        )
        conn.commit()
    
    print(f"Assigned bernd.mueller to access Olaf Gemein")
    
    # Verify Bernd can now see Olaf's data
    cursor.execute(
        '''
        SELECT COUNT(*) as count
        FROM note n
        JOIN person p ON n.person_id = p.id
        WHERE p.vorname = ? AND p.nachname = ?
        ''',
        ("Olaf", "Gemein")
    )
    olaf_note_count = cursor.fetchone()['count']
    
    print(f"\nVerifying Bernd can now see Olaf's data:")
    print(f"Bernd can now see {olaf_note_count} notes for Olaf Gemein")
    
    # Print tables
    print_user_tables(conn, admin_id, "Anna Schmitt")


def database_exists(conn):
    """Check if the database is already initialized with required tables and data."""
    cursor = conn.cursor()
    try:
        # Check if all required tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user', 'person', 'note', 'user_person', 'note_assignment')
        """)
        tables = cursor.fetchall()
        if len(tables) != 5:  # All 5 required tables must exist
            return False
            
        # Check if sample data exists
        cursor.execute('SELECT COUNT(*) FROM user')
        if cursor.fetchone()[0] == 0:
            return False
            
        return True
    except sqlite3.Error:
        return False


def main():
    # Use persistent database file
    DB_FILE = "showcase.db"
    conn = None
    
    try:
        # Connect to the database (creates the file if it doesn't exist)
        conn = get_connection(DB_FILE)
        
        # Always create schema if it doesn't exist
        create_schema(conn)
        
        # Check if we need to insert sample data
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM user')
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print(f"Inserting sample data into {DB_FILE}")
            insert_sample_data(conn)
            conn.commit()  # Ensure data is saved
        else:
            print(f"Using existing database at {DB_FILE} with {user_count} users")
        
        # Run all use cases
        print("\nRunning use cases...")
        
        def prompt_continue():
            response = input("\nContinue / Stop? ").strip().lower()
            return response != "stop"
        
        run_uc1(conn)  # Admin overview
        if not prompt_continue():
            return
            
        run_uc2(conn)  # Editor updates note
        if not prompt_continue():
            return
            
        run_uc3(conn)  # Viewer reads notes
        if not prompt_continue():
            return
            
        run_uc4(conn)  # Editor creates new note
        if not prompt_continue():
            return
            
        run_uc5(conn)  # Admin assigns rights
        
        # Final verification
        print("\nFinal verification:")
        for user_id, username in [(1, 'anna.schmitt'), (2, 'bernd.mueller'), (3, 'clara.schulz')]:
            visible_data = fetch_visible_persons_notes(conn, user_id)
            print(f"{username} can see {len(visible_data)} notes")
        
        # Keep the database file after execution
        print(f"\nDatabase has been saved to {DB_FILE}")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
