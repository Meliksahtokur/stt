import asyncio
import aiohttp
from src.sync_manager import SyncManager
from src.data_processor import process_animal_records
from src.auth_manager import AuthManager

async def get_all_animal_data():
    """Fetches all animal data asynchronously."""
    auth_manager = AuthManager()
    user = auth_manager.get_current_user()
    if not user:
        return []

    sync_manager = SyncManager(user.id)
    try:
        raw_data = await sync_manager.get_all_animal_data_async()
        processed_data = process_animal_records(raw_data)
        return processed_data
    except Exception as e:
        print(f"Error fetching or processing animal data: {e}")
        return []

