# This file should contain the main logic for your application,
#  likely importing and using functions from other modules.
#  Since this is a Kivy app, the main application logic will
#  likely reside in kivy_app/app.py

from src.sync_manager import SyncManager
from src.data_processor import process_animal_records
from src.display import display_animal_summary
from src.auth_manager import AuthManager

def get_all_animal_data():
    """Fetches all animal data, processes it, and returns it."""
    auth_manager = AuthManager()
    user = auth_manager.get_current_user()
    if not user:
        return [] # Or handle the case where no user is logged in appropriately

    sync_manager = SyncManager(user.id)
    try:
        raw_data = sync_manager.get_all_animal_data()
        processed_data = process_animal_records(raw_data)
        return processed_data
    except Exception as e:
        print(f"Error fetching or processing animal data: {e}")
        return []

if __name__ == "__main__":
    # Example usage (for testing purposes):
    all_animals = get_all_animal_data()
    display_animal_summary(all_animals)

