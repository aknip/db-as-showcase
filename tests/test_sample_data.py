import sys
"""Test sample data insertion."""
import unittest
import sys
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E402

from demo_db import (  # noqa: E402
    get_connection,
    create_schema,
    insert_sample_data
)


class TestSampleData(unittest.TestCase):
    """Test sample data insertion and validation."""

    def setUp(self):
        """Set up test database with sample data."""
        self.conn = get_connection(":memory:")
        create_schema(self.conn)
        insert_sample_data(self.conn)

    def tearDown(self):
        """Clean up after tests."""
        self.conn.close()

    def test_sample_data_inserted(self):
        """Verify that sample data was inserted correctly."""
        cursor = self.conn.cursor()
        
        # Check users were inserted
        cursor.execute("SELECT COUNT(*) FROM user")
        self.assertEqual(cursor.fetchone()[0], 3)
        
        # Check persons were inserted
        cursor.execute("SELECT COUNT(*) FROM person")
        self.assertEqual(cursor.fetchone()[0], 5)
        
        # Check notes were inserted
        cursor.execute("SELECT COUNT(*) FROM note")
        self.assertEqual(cursor.fetchone()[0], 20)


if __name__ == "__main__":
    unittest.main()
