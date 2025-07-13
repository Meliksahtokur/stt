import unittest
from unittest.mock import MagicMock, patch
from src.permissions_manager import PermissionsManager

class TestPermissionsManager(unittest.TestCase):

    def setUp(self):
        self.mock_supabase_client = MagicMock()
        self.test_user_id = "user123"
        self.permissions_manager = PermissionsManager(self.mock_supabase_client, self.test_user_id)

    def test_log_action(self):
        action = "test_action"
        details = {"key": "value"}
        self.permissions_manager._log_action(action, details)
        self.mock_supabase_client.table.assert_called_with('audit_log')
        self.mock_supabase_client.table.return_value.insert.assert_called_once_with({
            "user_id": self.test_user_id,
            "action": action,
            "details": details
        })
        self.mock_supabase_client.table.return_value.insert.return_value.execute.assert_called_once()

    @patch('src.permissions_manager.print') # Mock print to avoid console output during test
    def test_log_action_failure(self, mock_print):
        self.mock_supabase_client.table.return_value.insert.side_effect = Exception("DB Error")
        self.permissions_manager._log_action("failed_action", {})
        mock_print.assert_called_with(unittest.mock.ANY) # Check that print was called with an error message

    def test_can_read_animals(self):
        # Current implementation always returns True
        self.assertTrue(self.permissions_manager.can_read_animals())
        # Verify that _log_action was called
        self.mock_supabase_client.table.assert_called_with('audit_log')
        self.mock_supabase_client.table.return_value.insert.assert_called_once()

    def test_can_edit_animal_default_true(self):
        animal_uuid = "animal_abc"
        # Current implementation always returns True
        self.assertTrue(self.permissions_manager.can_edit_animal(animal_uuid))
        # Verify that _log_action was called
        self.mock_supabase_client.table.assert_called_with('audit_log')
        self.mock_supabase_client.table.return_value.insert.assert_called_once()

    # To test actual permission logic, uncomment the try/except block in can_edit_animal
    # and provide mock responses for self.db.table('profiles').select()...
    # Example for future implementation (requires uncommenting actual logic in src/permissions_manager.py):
    # @patch('src.permissions_manager.print')
    # def test_can_edit_animal_with_roles(self, mock_print):
    #     # Test admin role
    #     mock_response_admin = MagicMock(data={'role': 'admin'})
    #     self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response_admin
    #     self.assertTrue(self.permissions_manager.can_edit_animal("animal_123"))
    #     self.mock_supabase_client.table.assert_called_with('profiles') # Verify DB call
    #     self.mock_supabase_client.table.reset_mock() # Reset mock for next test

    #     # Test editor role
    #     mock_response_editor = MagicMock(data={'role': 'editor'})
    #     self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response_editor
    #     self.assertTrue(self.permissions_manager.can_edit_animal("animal_123"))
    #     self.mock_supabase_client.table.reset_mock()

    #     # Test viewer role (should return False)
    #     mock_response_viewer = MagicMock(data={'role': 'viewer'})
    #     self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response_viewer
    #     self.assertFalse(self.permissions_manager.can_edit_animal("animal_123"))
    #     self.mock_supabase_client.table.reset_mock()

    #     # Test no role found (should return False)
    #     mock_response_none = MagicMock(data=None)
    #     self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response_none
    #     self.assertFalse(self.permissions_manager.can_edit_animal("animal_123"))
    #     self.mock_supabase_client.table.reset_mock()

    #     # Test exception during DB call
    #     self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("DB Error")
    #     self.assertFalse(self.permissions_manager.can_edit_animal("animal_123"))
    #     mock_print.assert_called_with(unittest.mock.ANY)


if __name__ == '__main__':
    unittest.main()
