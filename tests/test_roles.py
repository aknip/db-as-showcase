import sys
import unittest
from pathlib import Path

# Ensure the demo_db module can be found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo_db import Role, is_admin, can_read, can_write


class TestRoles(unittest.TestCase):
    """Test role-based permissions."""

    def test_is_admin(self):
        """Test admin role detection."""
        self.assertTrue(is_admin(Role.ADMIN))
        self.assertFalse(is_admin(Role.EDITOR))
        self.assertFalse(is_admin(Role.VIEWER))

    def test_can_read(self):
        """Test read permissions for different roles."""
        # Test admin can read anything
        self.assertTrue(can_read(Role.ADMIN, 1, 2, False))
        self.assertTrue(can_read(Role.ADMIN, 1, 2, True))

        # Test editor can read their own content
        self.assertTrue(can_read(Role.EDITOR, 1, 1, False))
        # Test editor can read assigned content
        self.assertTrue(can_read(Role.EDITOR, 2, 1, True))
        # Test editor cannot read unassigned content
        self.assertFalse(can_read(Role.EDITOR, 2, 1, False))

        # Test viewer can read their own content
        self.assertTrue(can_read(Role.VIEWER, 1, 1, False))
        # Test viewer can read assigned content
        self.assertTrue(can_read(Role.VIEWER, 2, 1, True))
        # Test viewer cannot read unassigned content
        self.assertFalse(can_read(Role.VIEWER, 2, 1, False))

    def test_can_write(self):
        """Test write permissions for different roles."""
        # Test admin can write anything
        self.assertTrue(can_write(Role.ADMIN, 1, 2))
        # Test editor can write anything
        self.assertTrue(can_write(Role.EDITOR, 1, 2))
        # Test viewer can only write their own content
        self.assertTrue(can_write(Role.VIEWER, 1, 1))
        self.assertFalse(can_write(Role.VIEWER, 1, 2))


if __name__ == "__main__":
    unittest.main()
