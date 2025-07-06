import sqlite3
import sys
import unittest
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import get_connection, create_schema  # noqa: E402



class TestSchema(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(':memory:')  # Use in-memory database for testing
        create_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_tables_exist(self):
        tables = [row[0] for row in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        expected_tables = {'user', 'person', 'note', 'user_person', 'note_assignment'}
        self.assertTrue(expected_tables.issubset(set(tables)))

    def test_role_constraint(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO user (username, role) VALUES ('Test User', 'InvalidRole');")

if __name__ == '__main__':
    unittest.main()
