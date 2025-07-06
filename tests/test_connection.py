import sys
"""Test database connection and basic queries."""
import unittest
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # noqa: E402

from demo_db import get_connection  # noqa: E402


class TestDatabaseConnection(unittest.TestCase):
    """Test database connection and basic queries."""

    def test_connection(self):
        """Test that a database connection can be established."""
        conn = get_connection(":memory:")
        self.assertIsNotNone(conn)
        conn.close()

    def test_select_one(self):
        """Test that a basic SELECT query works."""
        conn = get_connection(":memory:")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 AS value")
        result = cursor.fetchone()
        self.assertEqual(result['value'], 1)
        conn.close()


if __name__ == "__main__":
    unittest.main()
