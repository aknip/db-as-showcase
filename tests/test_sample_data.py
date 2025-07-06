import unittest
import sqlite3
import sys
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import get_connection, insert_sample_data, create_schema

class TestSampleData(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(':memory:')  # Use in-memory database for testing
        create_schema(self.conn)
        insert_sample_data(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_users_exist(self):
        users = self.conn.execute("SELECT COUNT(*) FROM user;").fetchone()[0]
        self.assertEqual(users, 3)

    def test_persons_exist(self):
        persons = self.conn.execute("SELECT COUNT(*) FROM person;").fetchone()[0]
        self.assertEqual(persons, 5)

    def test_notes_exist(self):
        notes = self.conn.execute("SELECT COUNT(*) FROM note;").fetchone()[0]
        self.assertEqual(notes, 20)

if __name__ == '__main__':
    unittest.main()
