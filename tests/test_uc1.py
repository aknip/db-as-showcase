import unittest
import sys
from io import StringIO
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import get_connection, create_schema, insert_sample_data, run_uc1

class TestUseCase1(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(':memory:')  # Use in-memory database for testing
        create_schema(self.conn)
        insert_sample_data(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_run_uc1_output(self):
        expected_output = """Admin Overview:
Person: Person One, Note: Note 1
Person: Person One, Note: Note 2
Person: Person One, Note: Note 3
Person: Person One, Note: Note 4
Person: Person Two, Note: Note 5
Person: Person Two, Note: Note 6
Person: Person Two, Note: Note 7
Person: Person Two, Note: Note 8
Person: Person Three, Note: Note 9
Person: Person Three, Note: Note 10
Person: Person Three, Note: Note 11
Person: Person Three, Note: Note 12
Person: Person Four, Note: Note 13
Person: Person Four, Note: Note 14
Person: Person Four, Note: Note 15
Person: Person Four, Note: Note 16
Person: Person Five, Note: Note 17
Person: Person Five, Note: Note 18
Person: Person Five, Note: Note 19
Person: Person Five, Note: Note 20
"""
        captured_output = StringIO()
        sys.stdout = captured_output
        run_uc1(self.conn)
        sys.stdout = sys.__stdout__
        self.assertEqual(captured_output.getvalue(), expected_output)

if __name__ == '__main__':
    unittest.main()
