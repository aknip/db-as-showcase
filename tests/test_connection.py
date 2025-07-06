import unittest
import sys
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import get_connection

class TestConnection(unittest.TestCase):
    def test_get_connection(self):
        conn = get_connection()
        result = conn.execute("SELECT 1").fetchall()
        self.assertEqual(result, [(1,)])
        conn.close()

if __name__ == '__main__':
    unittest.main()
