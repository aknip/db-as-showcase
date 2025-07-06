import unittest
import sys
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import Role, is_admin, can_read, can_write

class TestRoleValidationLogic(unittest.TestCase):
    def test_is_admin(self):
        self.assertTrue(is_admin(Role.ADMIN))
        self.assertFalse(is_admin(Role.EDITOR))
        self.assertFalse(is_admin(Role.VIEWER))

    def test_can_read(self):
        self.assertTrue(can_read(Role.ADMIN, 1, 2, False))
        self.assertTrue(can_read(Role.EDITOR, 1, 1, False))
        self.assertTrue(can_read(Role.VIEWER, 1, 1, True))
        self.assertFalse(can_read(Role.VIEWER, 1, 2, False))

    def test_can_write(self):
        self.assertTrue(can_write(Role.ADMIN, 1, 2))
        self.assertTrue(can_write(Role.EDITOR, 1, 1))
        self.assertFalse(can_write(Role.VIEWER, 1, 1))

if __name__ == '__main__':
    unittest.main()
