import unittest
import sys
from io import StringIO
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import get_connection, create_schema, insert_sample_data, run_uc2, run_uc3

class TestUseCase3(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(':memory:')  # Use in-memory database for testing
        create_schema(self.conn)
        insert_sample_data(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_run_uc3_output(self):
        # First, update the note using run_uc2
        run_uc2(self.conn)
        expected_output = "Note 1: Updated Note Content\n"
        captured_output = StringIO()
        sys.stdout = captured_output
        run_uc3(self.conn)
        sys.stdout = sys.__stdout__
        self.assertIn(expected_output, captured_output.getvalue())

if __name__ == '__main__':
    unittest.main()
