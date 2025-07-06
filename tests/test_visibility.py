import unittest
import sys
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import get_connection, create_schema, insert_sample_data, fetch_visible_persons_notes

class TestVisibilityQuery(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(':memory:')  # Use in-memory database for testing
        create_schema(self.conn)
        insert_sample_data(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_admin_sees_all(self):
        visible_data = fetch_visible_persons_notes(self.conn, 1)  # Admin user
        self.assertEqual(len(visible_data), 20)

    def test_viewer_sees_own(self):
        visible_data = fetch_visible_persons_notes(self.conn, 3)  # Viewer user
        persons = set(d['person_name'] for d in visible_data)
        self.assertEqual(persons, {'Person Five'})
        self.assertEqual(len(visible_data), 4)

if __name__ == '__main__':
    unittest.main()
