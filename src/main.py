import asyncio
from src.sync_manager import SyncManager
from src.data_processor import process_animal_records, get_display_name # Import get_display_name
from src.persistence import load_animals # Import load_animals for offline-first
from kivymd.app import MDApp # Import MDApp to get sync_manager from app instance

async def get_all_animal_data():
    """
    Fetches all animal data asynchronously, prioritizing local cache and
    then triggering background synchronization.
    """
    app = MDApp.get_running_app()
    
    # 1. First, try to load from local cache for immediate UI responsiveness
    local_data = load_animals()
    if local_data:
        processed_local_data = process_animal_records(local_data)
        print("Hayvan verileri lokal önbellekten yüklendi.")
        # We also need to populate _all_animals if this is the first load
        # This will be handled by HomeScreen.populate_list directly now.
    else:
        processed_local_data = []
        print("Lokal hayvan verisi bulunamadı.")

    # 2. Trigger background synchronization from the remote server
    if app.sync_manager and app.user:
        print("Arka planda senkronizasyon başlatılıyor...")
        try:
            # Pass remote_only=False to ensure queue is processed before fetching remote
            synced_data = await app.sync_manager.synchronize(remote_only=False)
            processed_synced_data = process_animal_records(synced_data)
            print("Senkronizasyon tamamlandı.")
            return processed_synced_data # Return the updated, synced data
        except Exception as e:
            print(f"Arka plan senkronizasyonu sırasında hata oluştu: {e}. Lokal veri gösteriliyor.")
            # If sync fails, return the locally loaded data
            return processed_local_data
    else:
        print("Senkronizasyon yöneticisi veya kullanıcı oturumu mevcut değil. Sadece lokal veri yüklenecek.")
        return processed_local_data # If no sync_manager/user, just return local

