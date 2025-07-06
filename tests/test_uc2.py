import sys
import unittest
from io import StringIO
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import get_connection, create_schema, insert_sample_data, run_uc2  # noqa: E402



class TestUseCase2(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(':memory:')  # Use in-memory database for testing
        create_schema(self.conn)
        insert_sample_data(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_run_uc2_output(self):
        # Test has incorrect expected output - UC2 updates note 9 by bernd.mueller, not note 5 by anna.schmitt
        captured_output = StringIO()
        sys.stdout = captured_output
        run_uc2(self.conn)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Check for the header
        self.assertIn("UC-2: Editor Updates Note (Bernd Mueller)", output)
        self.assertIn("Expected: Successfully update a note", output)
        
        # Check for the updated note (correct note is #9, not #5)
        self.assertIn("Updated Note 9", output)
        self.assertIn("bernd.mueller", output)
        self.assertIn("Updated: Note 9 for person 3", output)
        
        # Check for the table headers
        self.assertIn("Bernd Mueller's Visible Persons:", output)
        self.assertIn("Bernd Mueller's Visible Notes:", output)
        
        # Check for content change indication in the Changes column
        self.assertIn("Content changed", output)

if __name__ == '__main__':
    unittest.main()
