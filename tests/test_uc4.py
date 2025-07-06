import sys
import unittest
from io import StringIO
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import get_connection, create_schema, insert_sample_data, run_uc4  # noqa: E402



class TestUseCase4(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(':memory:')  # Use in-memory database for testing
        create_schema(self.conn)
        insert_sample_data(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_run_uc4_output(self):
        expected_output = "Added Note by bernd.mueller for Karl Offen: New note created by Bernd for Karl"
        captured_output = StringIO()
        sys.stdout = captured_output
        run_uc4(self.conn)
        sys.stdout = sys.__stdout__
        self.assertIn(expected_output, captured_output.getvalue())

if __name__ == '__main__':
    unittest.main()
