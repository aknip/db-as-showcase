Specifiations are defined in file "specs.md"

1 – High-Level Blueprint (“Big Picture”)
	1.	Set up project skeleton
	•	Create demo_db.py; ensure Python ≥ 3.8
	•	Establish SQLite connection with PRAGMA foreign_keys = ON
	2.	Define database schema
	•	Create six tables as specified
	•	Verify constraints & indices (PK, FK, UNIQUE, CHECK)
	3.	Insert sample data
	•	3 users, 5 persons, 20 notes, assignments
	4.	Encapsulate role logic (can_read, can_write)
	•	Enum mapping “Admin/Editor/Viewer”
	•	Generic validation helpers
	5.	Build query engine
	•	Visibility SQL statement
	•	Helper fetch_visible_persons_notes(user_id)
	6.	Implement use-case workflow
	•	UC-1 … UC-5 as reusable functions
	•	Output: business description → result dump
	7.	Develop tests
	•	pytest unit & integration tests
	•	Golden-master comparison for use cases
	8.	Error & edge-case handling
	•	try/except sqlite3.Error
	•	Mark empty result sets clearly

⸻

2 – Iterative Chunks (Stage 1)

Iteration	Goal	Delivers a working slice
I-1	Framework & DB connection	empty DB file, connection factory
I-2	Table DDL	schema in SQLite
I-3	Sample data	SELECT * shows 3 table contents
I-4	Role utilities	can_read / can_write with tests
I-5	Visibility query	fetch_visible_persons_notes
I-6	UC-1 demo	admin overview
I-7	UC-2/3	edit/viewer scenarios incl. write demo
I-8	UC-4/5	new note & rights update
I-9	Full test suite	100 % via pytest


⸻

3 – Fine-Grained Breakdown (Stage 2)

(each iteration now split into 2–3 very small steps)

I-1 Framework
	1.	Create file: demo_db.py with main() stub
	2.	Connection helper: get_connection(path="demo.sqlite")
	3.	Enable PRAGMA & test: DB responds to SELECT 1

I-2 Table DDL
	1.	Implement create_schema(conn)
	2.	Mini-test: tables exist via sqlite_master
	3.	Negative test: re-running does not drop anything

I-3 Sample Data
	1.	insert_sample_data(conn) adds users
	2.	Add persons + notes + assignments
	3.	Test: counters == expected amounts

I-4 Role Utilities
	1.	Define enum Role(str, Enum)
	2.	Implement can_read, can_write
	3.	Unit tests per role

I-5 Visibility Query
	1.	Store SQL in constant
	2.	Implement fetch_visible_persons_notes
	3.	Unit test: viewer sees only own data

(… continue similarly for I-6 to I-9 …)

⸻

4 – Prompts for a Code-Generation LLM

Each prompt is self-contained, builds on the previous one, and ends with tests.
(Marked as plain text so the LLM does not confuse code with prompt.)

Prompt 01 – Project Initialization

Task:
1. Create the file demo_db.py.
2. Implement get_connection(path="demo.sqlite") that returns a SQLite connection with PRAGMA foreign_keys = ON.
3. Write a main() function that merely executes SELECT 1 for testing.
4. Create tests/test_connection.py that checks get_connection() returns a valid connection and SELECT 1 == [(1,)].

Constraints:
* Python ≥ 3.8, no external packages.
* Use pathlib for paths.
* Tests must pass with pytest.

Return both the code and the tests.

Prompt 02 – Table Schema

Building on demo_db.py from Prompt 01:

1. Implement create_schema(conn) using the DDL from the specification (tables user, person, note, user_person, user_note).
2. Call create_schema(conn) in main() before SELECT 1.
3. Add tests/test_schema.py that checks all tables exist and that the CHECK constraint on role works (insert with invalid role must fail).

Ensure all existing tests still pass.

Prompt 03 – Insert Sample Data

Extend demo_db.py:

1. Add insert_sample_data(conn). The function inserts:
   * 3 users (Admin, Editor, Viewer)
   * 5 persons with created_by
   * 20 notes (4 per person)
   * Assignments in user_person and user_note per specification
2. Call insert_sample_data(conn) in main() after create_schema().
3. Add tests/test_sample_data.py that checks 3 users, 5 persons, and 20 notes exist.

All tests must remain green.

Prompt 04 – Role Validation Logic

Add:

1. Enum Role(str, Enum) with 'Admin', 'Editor', 'Viewer'.
2. Functions:
   * is_admin(role)
   * can_read(role, creator_id, user_id, has_assignment)
   * can_write(role, creator_id, user_id)
3. Unit tests in tests/test_roles.py for each role (positive & negative).

No existing tests may fail.

Prompt 05 – Visibility Query

Based on the SQL strategy:

1. Define the query constant SELECT_VISIBLE_DATA.
2. Implement fetch_visible_persons_notes(conn, user_id) executing the query and returning a list of dicts.
3. Add tests/test_visibility.py:
   * Admin sees 5 persons & 20 notes
   * Viewer clara.schulz sees only 'Lisa Privat' & 2 notes

Prompt 06 – Use Case 1

1. Implement run_uc1(conn) – admin overview: print business description + query result.
2. Update main() so run_uc1() executes after insert_sample_data().
3. Integration test in tests/test_uc1.py compares output to a golden-master string (snapshot).

Ensure previous tests remain green.

Prompt 07 – Use Cases 2 & 3

1. Implement run_uc2(conn) and run_uc3(conn) per specification.
2. UC-2 must demonstrate a note UPDATE; UC-3 is read-only.
3. Update main() to run UC-2 & UC-3.
4. Tests: snapshot comparison for both use cases.

All tests must stay green.

Prompt 08 – Use Cases 4 & 5

1. Implement run_uc4(conn) (new note by Editor) & run_uc5(conn) (Admin assigns rights).
2. Execute both in main().
3. Tests: UC-4 must add +1 note; UC-5 must reflect new visibility.

All tests must pass.

Prompt 09 – Full Test Coverage & README

1. Finalize tests (edge cases per Test Plan section 6).
2. Write README.md with:
   * Project goal
   * Installation & execution instructions
   * Test workflow description
3. Run pylint/flake8 (if available) with no errors.

All tests must still pass.

