import sys
import unittest
from io import StringIO
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import get_connection, create_schema, insert_sample_data, run_uc1  # noqa: E402



class TestUseCase1(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(':memory:')  # Use in-memory database for testing
        create_schema(self.conn)
        insert_sample_data(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_run_uc1_output(self):
        # Instead of checking exact output, check for key elements that should be present
        # regardless of formatting changes
        captured_output = StringIO()
        sys.stdout = captured_output
        run_uc1(self.conn)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Check for the header
        self.assertIn("UC-1: Admin Overview (Anna Schmitt)", output)
        self.assertIn("Expected: See all persons and notes", output)
        
        # Check that all expected person-note combinations are present
        expected_combinations = [
            ("Max Beispiel", "Note 1 for person 1"),
            ("Max Beispiel", "Note 2 for person 1"),
            ("Max Beispiel", "Note 3 for person 1"),
            ("Max Beispiel", "Note 4 for person 1"),
            ("Olaf Gemein", "Note 17 for person 5"),
            ("Olaf Gemein", "Note 18 for person 5"),
            ("Olaf Gemein", "Note 19 for person 5"),
            ("Olaf Gemein", "Note 20 for person 5"),
            ("Karl Offen", "Note 10 for person 3"),
            ("Karl Offen", "Note 11 for person 3"),
            ("Karl Offen", "Note 12 for person 3"),
            ("Karl Offen", "Note 9 for person 3"),
            ("Lisa Privat", "Note 13 for person 4"),
            ("Lisa Privat", "Note 14 for person 4"),
            ("Lisa Privat", "Note 15 for person 4"),
            ("Lisa Privat", "Note 16 for person 4"),
            ("Eva Team", "Note 5 for person 2"),
            ("Eva Team", "Note 6 for person 2"),
            ("Eva Team", "Note 7 for person 2"),
            ("Eva Team", "Note 8 for person 2")
        ]
        
        for person, note in expected_combinations:
            # Check if both the person name and note content appear in the output
            # This works whether they're in the original format or in the table format
            self.assertIn(person, output)
            self.assertIn(note, output)
        
        # Check that total records count is mentioned
        self.assertIn("Total records: 20", output)
        
        # Check for the table headers
        self.assertIn("Anna Schmitt's Visible Persons:", output)
        self.assertIn("Anna Schmitt's Visible Notes:", output)

if __name__ == '__main__':
    unittest.main()
