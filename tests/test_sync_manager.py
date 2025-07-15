import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from src.sync_manager import SyncManager, SyncManagerError
from typing import List, Dict, Any

class TestSyncManager(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Mock Supabase client and its methods
        self.mock_supabase_client = MagicMock()
        self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        self.mock_supabase_client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
        self.mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock(data=[])

        # Mock global functions from persistence
        self.patcher_load_animals = patch('src.sync_manager.load_animals')
        self.patcher_save_animals = patch('src.sync_manager.save_animals')
        self.patcher_load_sync_queue = patch('src.sync_manager.load_sync_queue')
        self.patcher_save_sync_queue = patch('src.sync_manager.save_sync_queue')
        # Removed global patch for _add_to_sync_queue.
        # It will be patched per test where needed.

        self.mock_load_animals = self.patcher_load_animals.start()
        self.mock_save_animals = self.patcher_save_animals.start()
        self.mock_load_sync_queue = self.patcher_load_sync_queue.start()
        self.mock_save_sync_queue = self.patcher_save_sync_queue.start()
        # self.mock_add_to_sync_queue = self.patcher_add_to_sync_queue.start() # Removed this line

        # Mock create_client to return our mock client
        self.patcher_create_client = patch('src.sync_manager.create_client', return_value=self.mock_supabase_client)
        self.mock_create_client = self.patcher_create_client.start()

        self.user_id = "test_user_id"
        self.sync_manager = SyncManager(self.user_id)

    def tearDown(self):
        self.patcher_load_animals.stop()
        self.patcher_save_animals.stop()
        self.patcher_load_sync_queue.stop()
        self.patcher_save_sync_queue.stop()
        self.patcher_create_client.stop()
        # Ensure that patcher_add_to_sync_queue is stopped if it was ever started.
        # This will be handled by individual test methods now.
        if hasattr(self, 'patcher_add_to_sync_queue') and self.patcher_add_to_sync_queue.is_started:
             self.patcher_add_to_sync_queue.stop()

    async def test_init_no_user_id(self):
        with self.assertRaises(SyncManagerError):
            SyncManager(None)

    async def test_get_remote_animals_success(self):
        self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"uuid": "1", "name": "Remote Animal"}
        ]
        animals = await self.sync_manager._get_remote_animals()
        self.assertEqual(len(animals), 1)
        self.assertEqual(animals[0]["name"], "Remote Animal")
        self.mock_supabase_client.table.assert_called_with('animals')
        self.mock_supabase_client.table.return_value.select.assert_called_with('*')
        self.mock_supabase_client.table.return_value.select.return_value.eq.assert_called_with('user_id', self.user_id)

    async def test_get_remote_animals_failure(self):
        self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Network error")
        with self.assertRaisesRegex(SyncManagerError, "Uzak veriler çekilirken hata oluştu"):
            await self.sync_manager._get_remote_animals()

    @patch.object(SyncManager, '_add_to_sync_queue', new_callable=MagicMock)
    async def test_create_animal_offline_first(self, mock_add_to_sync_queue):
        self.mock_load_animals.return_value = []
        mock_new_animal = {"isletme_kupesi": "A001"}
        
        await self.sync_manager.create_animal(mock_new_animal.copy())

        self.mock_save_animals.assert_called_once()
        saved_animals = self.mock_save_animals.call_args[0][0]
        self.assertEqual(len(saved_animals), 1)
        self.assertEqual(saved_animals[0]['isletme_kupesi'], 'A001')
        self.assertIsNotNone(saved_animals[0].get('uuid'))
        self.assertEqual(saved_animals[0]['user_id'], self.user_id)
        self.assertEqual(saved_animals[0]['sync_status'], 'pending_create')
        self.assertIsNotNone(saved_animals[0].get('last_modified'))

        mock_add_to_sync_queue.assert_called_once_with('create', saved_animals[0])

    @patch.object(SyncManager, '_add_to_sync_queue', new_callable=MagicMock)
    async def test_update_animal_offline_first(self, mock_add_to_sync_queue): # Add mock to parameters
        existing_animal = {"uuid": "123", "isletme_kupesi": "Old", "user_id": self.user_id}
        self.mock_load_animals.return_value = [existing_animal]
        updated_data = {"uuid": "123", "isletme_kupesi": "New", "user_id": self.user_id}

        await self.sync_manager.update_animal("123", updated_data)

        self.mock_save_animals.assert_called_once()
        saved_animals = self.mock_save_animals.call_args[0][0]
        self.assertEqual(len(saved_animals), 1)
        self.assertEqual(saved_animals[0]['isletme_kupesi'], 'New')
        self.assertEqual(saved_animals[0]['sync_status'], 'pending_update')
        self.assertIsNotNone(saved_animals[0].get('last_modified'))
        
        mock_add_to_sync_queue.assert_called_once_with('update', saved_animals[0]) # Use the local mock

    # This test no longer needs specific patching for _add_to_sync_queue as global patch is removed
    async def test_add_to_sync_queue(self):
        self.mock_load_sync_queue.return_value = []
        test_data = {"id": "test", "action": "test_action"}
        self.sync_manager._add_to_sync_queue("test_action", test_data) # Call the actual method
        self.mock_load_sync_queue.assert_called_once()
        self.mock_save_sync_queue.assert_called_once_with([{"action": "test_action", "data": test_data}])

    async def test_process_sync_queue_creates_updates(self):
        mock_queue = [
            {"action": "create", "data": {"uuid": "create1", "user_id": self.user_id}},
            {"action": "update", "data": {"uuid": "update1", "user_id": self.user_id}}
        ]
        self.mock_load_sync_queue.return_value = mock_queue

        await self.sync_manager.process_sync_queue()

        self.mock_supabase_client.table.return_value.insert.assert_called_once_with([{"uuid": "create1", "user_id": self.user_id}])
        self.mock_supabase_client.table.return_value.update.assert_called_once_with({"uuid": "update1", "user_id": self.user_id})
        self.mock_supabase_client.table.return_value.update.return_value.eq.assert_called_once_with('uuid', 'update1')
        self.mock_save_sync_queue.assert_called_once_with([]) # Queue should be cleared

    async def test_process_sync_queue_empty_queue(self):
        self.mock_load_sync_queue.return_value = []
        await self.sync_manager.process_sync_queue()
        self.mock_supabase_client.table.return_value.insert.assert_not_called()
        self.mock_supabase_client.table.return_value.update.assert_not_called()
        self.mock_save_sync_queue.assert_not_called()

    async def test_process_sync_queue_failure_not_cleared(self):
        mock_queue = [{"action": "create", "data": {"uuid": "create1"}}]
        self.mock_load_sync_queue.return_value = mock_queue
        self.mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception("DB error")

        with self.assertRaisesRegex(SyncManagerError, "Senkronizasyon kuyruğu işlenirken hata oluştu"):
            await self.sync_manager.process_sync_queue()

        self.mock_save_sync_queue.assert_not_called() # Queue should not be cleared on failure

    async def test_synchronize_full_flow_success(self):
        self.mock_load_animals.return_value = [{"uuid": "local1", "last_modified": "2023-01-01T00:00:00"}]
        self.mock_load_sync_queue.return_value = [{"action": "create", "data": {"uuid": "new1", "user_id": self.user_id, "last_modified": datetime.now().isoformat()}}]
        self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"uuid": "remote1", "last_modified": "2023-01-02T00:00:00", "user_id": self.user_id}
        ]

        result = await self.sync_manager.synchronize()

        self.mock_load_sync_queue.assert_called_once()
        self.mock_supabase_client.table.return_value.insert.assert_called_once() # For 'new1'
        self.mock_supabase_client.table.return_value.select.assert_called_once() # For remote fetch
        self.mock_save_sync_queue.assert_called_once_with([]) # Queue cleared
        self.mock_save_animals.assert_called_once() # Final merged data saved

        self.assertEqual(len(result), 2) # local1 (updated by remote) + remote1 (new) + new1 (created) -> should be 3, if local1 not changed, but here it is new.
        # Let's refine the expected result based on the merge logic:
        # local1 is initially in merged_data_dict.
        # remote1 is added.
        # So it should be 2.

    async def test_synchronize_remote_only(self):
        self.mock_load_animals.return_value = [{"uuid": "local1", "last_modified": "2023-01-01T00:00:00"}]
        self.mock_load_sync_queue.return_value = [{"action": "create", "data": {"uuid": "new1", "user_id": self.user_id, "last_modified": datetime.now().isoformat()}}]
        self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"uuid": "remote1", "last_modified": "2023-01-02T00:00:00", "user_id": self.user_id}
        ]

        await self.sync_manager.synchronize(remote_only=True)

        self.mock_load_sync_queue.assert_not_called() # Queue processing skipped
        self.mock_supabase_client.table.return_value.insert.assert_not_called() # No inserts from queue
        self.mock_supabase_client.table.return_value.select.assert_called_once() # Remote fetch still happens

    async def test_synchronize_merge_logic_local_newer(self):
        local_animal = {"uuid": "common_uuid", "data": "local_data", "last_modified": "2024-01-02T00:00:00", "user_id": self.user_id}
        remote_animal = {"uuid": "common_uuid", "data": "remote_data", "last_modified": "2024-01-01T00:00:00", "user_id": self.user_id}
        self.mock_load_animals.return_value = [local_animal]
        self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [remote_animal]
        self.mock_load_sync_queue.return_value = [] # Ensure no pending changes affect merge

        result = await self.sync_manager.synchronize()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['data'], 'local_data') # Local should win

    async def test_synchronize_merge_logic_remote_newer(self):
        local_animal = {"uuid": "common_uuid", "data": "local_data", "last_modified": "2024-01-01T00:00:00", "user_id": self.user_id}
        remote_animal = {"uuid": "common_uuid", "data": "remote_data", "last_modified": "2024-01-02T00:00:00", "user_id": self.user_id}
        self.mock_load_animals.return_value = [local_animal]
        self.mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [remote_animal]
        self.mock_load_sync_queue.return_value = []

        result = await self.sync_manager.synchronize()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['data'], 'remote_data') # Remote should win

if __name__ == '__main__':
    unittest.main()
