import sys
"""Test visibility of persons and notes based on user roles."""
import unittest
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E402

from demo_db import (  # noqa: E402
    get_connection,
    create_schema,
    insert_sample_data,
    fetch_visible_persons_notes
)


class TestVisibilityQuery(unittest.TestCase):
    """Test visibility of data based on user roles."""

    def setUp(self):
        """Set up test database with sample data."""
        self.conn = get_connection(":memory:")
        create_schema(self.conn)
        insert_sample_data(self.conn)

    def tearDown(self):
        """Clean up after tests."""
        self.conn.close()

    def test_admin_sees_all(self):
        """Test admin can see all data."""
        visible_data = fetch_visible_persons_notes(self.conn, 1)  # Admin user
        self.assertEqual(len(visible_data), 20)

    def test_viewer_sees_own(self):
        """Test viewer can only see their own data."""
        visible_data = fetch_visible_persons_notes(self.conn, 3)  # Viewer user
        persons = set(f"{d['vorname']} {d['nachname']}" for d in visible_data)
        self.assertEqual(persons, {'Olaf Gemein', 'Max Beispiel', 'Eva Team'})
        # The viewer can see 6 records in total (4 for Olaf, 1 for Max, 1 for Eva)
        self.assertEqual(len(visible_data), 6)


if __name__ == "__main__":
    unittest.main()
