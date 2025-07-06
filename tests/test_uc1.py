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
        expected_output = """UC-1: Admin Overview (Anna Schmitt)
Expected: See all persons and notes
Person: Max Beispiel, Note: Note 1 for person 1
Person: Max Beispiel, Note: Note 2 for person 1
Person: Max Beispiel, Note: Note 3 for person 1
Person: Max Beispiel, Note: Note 4 for person 1
Person: Olaf Gemein, Note: Note 17 for person 5
Person: Olaf Gemein, Note: Note 18 for person 5
Person: Olaf Gemein, Note: Note 19 for person 5
Person: Olaf Gemein, Note: Note 20 for person 5
Person: Karl Offen, Note: Note 10 for person 3
Person: Karl Offen, Note: Note 11 for person 3
Person: Karl Offen, Note: Note 12 for person 3
Person: Karl Offen, Note: Note 9 for person 3
Person: Lisa Privat, Note: Note 13 for person 4
Person: Lisa Privat, Note: Note 14 for person 4
Person: Lisa Privat, Note: Note 15 for person 4
Person: Lisa Privat, Note: Note 16 for person 4
Person: Eva Team, Note: Note 5 for person 2
Person: Eva Team, Note: Note 6 for person 2
Person: Eva Team, Note: Note 7 for person 2
Person: Eva Team, Note: Note 8 for person 2
Total records: 20
"""
        captured_output = StringIO()
        sys.stdout = captured_output
        run_uc1(self.conn)
        sys.stdout = sys.__stdout__
        self.assertEqual(captured_output.getvalue(), expected_output)

if __name__ == '__main__':
    unittest.main()
