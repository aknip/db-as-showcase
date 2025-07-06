Specification

Project: Example “Persons & Notes” Database with Access-Control Demo

(Python 3 + SQLite 3)

⸻

1  Objective

A single Python script (demo_db.py) creates a SQLite database with realistic sample data, defines clear access rules, and demonstrates them in five use-cases.
The script must run on any system with Python ≥ 3.8 and no external dependencies.

⸻

2  Functional Requirements

#	Category	Requirement
F-1	Entities	Persons, Notes, Users, Roles (“Admin”, “Editor”, “Viewer”)
F-2	Person	Columns: id (PK), vorname, nachname, email, telefon, created_by (FK → user)
F-3	Note	Columns: id (PK), person_id (FK → person), created_at (DATETIME), text, created_by (FK → user)
F-4	User	Columns: id (PK), username (UNIQUE), rolle (ENUM Admin
F-5	Access Mapping	Tables user_person(user_id, person_id) and user_note(user_id, note_id) record who has any access (read). Write access is derived from the role.
F-6	Role Logic	Admin: full read/write on every record. Editor: read/write on own and assigned records. Viewer: read-only on own and assigned records.
F-7	Use-Cases	See section 4 – five scenarios covering all permission combinations.
F-8	Script Output	For each use-case: a short functional description, then all persons visible to the active user including every related note with full text.


⸻

3  Technical Architecture

demo_db.py
├─ create_schema()         -- DDL: tables & constraints
├─ insert_sample_data()    -- 3 users, 5 persons, 20 notes, mappings
├─ run_use_cases()         -- loop: print description + execute query
└─ main()                  -- orchestrates: connect → create → insert → run

3.1  Table DDL (excerpt)

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  rolle TEXT CHECK (rolle IN ('Admin','Editor','Viewer')) NOT NULL
);

CREATE TABLE person (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  vorname TEXT NOT NULL,
  nachname TEXT NOT NULL,
  email TEXT NOT NULL,
  telefon TEXT,
  created_by INTEGER NOT NULL REFERENCES user(id)
);

CREATE TABLE note (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id INTEGER NOT NULL REFERENCES person(id) ON DELETE CASCADE,
  created_at DATETIME NOT NULL,
  text TEXT NOT NULL,
  created_by INTEGER NOT NULL REFERENCES user(id)
);

CREATE TABLE user_person (
  user_id INTEGER REFERENCES user(id) ON DELETE CASCADE,
  person_id INTEGER REFERENCES person(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, person_id)
);

CREATE TABLE user_note (
  user_id INTEGER REFERENCES user(id) ON DELETE CASCADE,
  note_id INTEGER REFERENCES note(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, note_id)
);

3.2  Read-Access Query Strategy

For an arbitrary user u:

SELECT p.*, n.id AS note_id, n.created_at, n.text
FROM person        p
LEFT JOIN note     n  ON n.person_id = p.id
LEFT JOIN user_person up ON up.person_id = p.id AND up.user_id = :uid
LEFT JOIN user_note   un ON un.note_id  = n.id AND un.user_id = :uid
WHERE
      :is_admin = 1
   OR p.created_by = :uid
   OR up.user_id   IS NOT NULL          -- person assigned
   OR un.user_id   IS NOT NULL;         -- note directly assigned

Write permission is only checked in Python when a use-case modifies data (role-based).

⸻

4  Sample Data & Use-Cases

Entity	Values
Users (3)	• anna.schmitt (Admin)• bernd.mueller (Editor)• clara.schulz (Viewer)
Persons (5)	e.g. Max Beispiel, Eva Team, Karl Offen, Lisa Privat, Olaf Gemein — each with created_by set appropriately
Notes (20)	Four per person; random text & timestamps
Mappings	Mixture of private, 2-user, and 3-user visibility according to use-cases

Use-Case Matrix

#	Title	Acting User	Flow
UC-1	Global Overview	Admin anna.schmitt	Lists every person and note
UC-2	Shared Person	Editor bernd.mueller edits note on “Max Beispiel”; Viewer clara.schulz reads it	Demonstrates write vs. read
UC-3	Private Data	Viewer clara.schulz sees only “Lisa Privat” and 2 notes	Shows exclusive access
UC-4	Own Note	Editor bernd.mueller creates a new note for “Karl Offen” (visible only to him and Admin)	Create & verify visibility
UC-5	Grant Access	Admin anna.schmitt assigns bernd.mueller & clara.schulz to “Eva Team”; afterwards both query visibility	Dynamic permission change


⸻

5  Error & Edge-Case Handling

Category	Strategy
SQLite connection errors	try/except sqlite3.Error → log and sys.exit(1)
FK violations	Enable PRAGMA foreign_keys = ON; abort with clear message
Invalid enum value (role)	CHECK constraint plus Python pre-validation
Duplicate user/email	UNIQUE constraint; script warns and skips
Empty result set	Print “No visible data” clearly


⸻

6  Test Plan

Level	Tool	Test Cases
Unit	pytest	• Schema validation (FKs, enum)• Role helper functions (can_read, can_write)
Integration	run python demo_db.py	• For each use-case verify exact number of persons/notes (golden file)• UC-4 inserts new note → follow-up query must show it
Edge	manual inserts	• Person without notes• Note without person (must fail)• User without role (must fail)


⸻

7  Directory & Build Guide

project-root/
├─ demo_db.py
├─ README.md          -- run & test instructions
└─ tests/
   └─ test_logic.py

Run:

python demo_db.py      # creates 'demo.sqlite' and runs all use-cases
pytest -q              # execute test-suite


⸻

8  Extensibility
	•	Password Hash: add password_hash column later.
	•	Fine-grained write rights: add boolean can_write in mapping tables; query logic is modular.
	•	ORM Migration: clear separation allows later switch to SQLAlchemy.
	•	Multi-tenant: add tenant_id to all tables + composite PKs.

