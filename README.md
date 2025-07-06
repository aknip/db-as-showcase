# db-as-showcase

## Project Goal
The goal is to be able to display the five most important use cases in a small, sample database using DB queries. To do this, the five use cases must be defined with sample users and sample data.

Database: Personal data, notes. Any number of notes can be attached to individuals.

The database should be accessible to multiple users. Individuals and notes can optionally be viewed or modified by multiple users. 

The access rules (“who can see what”) should also be mapped via the DB schema.

For more details see [specs.md](specs.md).

## Installation & Execution
1. Ensure Python 3.8 or higher is installed.
2. Clone the repository.
3. Navigate to the project directory.
4. Install dependencies if any are specified (currently, only the standard library and pytest are used).
5. Run the main script using:
   ```bash
   python demo_db.py
   ```

## Test Workflow
- The project uses `pytest` for testing.
- To run tests, execute:
  ```bash
  pytest tests/
  ```
- Ensure all tests pass before committing changes.

## Linting
- Run `pylint` or `flake8` to ensure code quality.