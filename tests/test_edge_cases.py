"""Test edge cases for the database application."""
import sys
import unittest
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import (  # noqa: E402
    get_connection,
    create_schema,
    insert_sample_data,
    Role,
    fetch_visible_persons_notes
)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases for the database application."""

    def setUp(self):
        """Set up test database with sample data."""
        self.conn = get_connection(':memory:')  # Use in-memory database for testing
        create_schema(self.conn)
        insert_sample_data(self.conn)

    def tearDown(self):
        """Clean up after tests."""
        self.conn.close()

    def test_person_without_notes(self):
        """Test that a person without notes is handled correctly."""
        # Insert a person without any notes
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO user (username, role) VALUES (?, ?)",
            ("testuser", Role.VIEWER.value)
        )
        user_id = cursor.lastrowid
        
        cursor.execute(
            """
            INSERT INTO person (vorname, nachname, email, telefon, created_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("No", "Notes", "no.notes@example.com", "+49123456789", user_id)
        )
        person_id = cursor.lastrowid
        self.conn.commit()

        # Test that the person is visible to the admin
        admin_data = fetch_visible_persons_notes(self.conn, 1)  # Admin user
        person_found = any(p['person_id'] == person_id for p in admin_data)
        self.assertTrue(person_found, "Admin should see the person without notes")

        # Test that the person is visible to the creator
        creator_data = fetch_visible_persons_notes(self.conn, user_id)
        person_found = any(p['person_id'] == person_id for p in creator_data)
        self.assertTrue(person_found, "Creator should see the person they created")

    def test_note_without_person_fails(self):
        """Test that creating a note without a person fails."""
        cursor = self.conn.cursor()
        with self.assertRaises(Exception):
            # This should fail due to foreign key constraint
            cursor.execute(
                """
                INSERT INTO note (person_id, created_at, text, created_by)
                VALUES (?, datetime('now'), 'Orphaned note', ?)
                """,
                (9999, 1)  # Non-existent person_id
            )
            self.conn.commit()

    def test_user_without_role_fails(self):
        """Test that creating a user without a role fails."""
        cursor = self.conn.cursor()
        with self.assertRaises(Exception):
            # This should fail due to CHECK constraint
            cursor.execute(
                "INSERT INTO user (name, role) VALUES (?, ?)",
                ("norole", "InvalidRole")
            )
            self.conn.commit()


if __name__ == '__main__':
    unittest.main()
