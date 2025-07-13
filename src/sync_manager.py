# src/sync_manager.py

"""
Lokal veri ile Supabase veritabanı arasındaki senkronizasyonu yönetir.
Çevrimdışı çalışmayı destekler ve bağlantı kurulduğunda verileri birleştirir.
"""

from datetime import datetime
from supabase import create_client, Client
from config.secrets import SUPABASE_URL, SUPABASE_KEY
from src.persistence import load_animals, save_animals, load_sync_queue, save_sync_queue # Import new queue functions
from typing import List, Dict, Any
import uuid # For generating UUIDs for new animals if not already present

class SyncManagerError(Exception):
    """Veri senkronizasyonu sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

class SyncManager:
    def __init__(self, user_id: str):
        if not user_id:
            raise SyncManagerError("Senkronizasyon için kullanıcı ID'si gereklidir.")
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.user_id = user_id

    async def _get_remote_animals(self) -> List[Dict[str, Any]]:
        """Supabase'den hayvanları çeker."""
        try:
            response = self.supabase.table('animals').select('*').eq('user_id', self.user_id).execute()
            return response.data
        except Exception as e:
            raise SyncManagerError(f"Uzak veriler çekilirken hata oluştu: {e}")

    def _add_to_sync_queue(self, action: str, data: Dict[str, Any]):
        """Senkronizasyon kuyruğuna bir eylem ekler."""
        queue = load_sync_queue()
        queue.append({"action": action, "data": data})
        save_sync_queue(queue)

    def _get_sync_queue(self) -> List[Dict[str, Any]]:
        """Senkronizasyon kuyruğunu yükler."""
        return load_sync_queue()

    def _clear_sync_queue(self):
        """Senkronizasyon kuyruğunu temizler."""
        save_sync_queue([])

    async def create_animal(self, animal_data: Dict[str, Any]):
        """Offline-first create. Saves locally immediately, then queues for sync."""
        if 'uuid' not in animal_data or not animal_data['uuid']:
            animal_data['uuid'] = str(uuid.uuid4()) # Ensure UUID exists for new records

        animal_data['user_id'] = self.user_id
        animal_data['sync_status'] = 'pending_create'
        animal_data['last_modified'] = datetime.now().isoformat()

        local_animals = load_animals() or []
        local_animals.append(animal_data)
        save_animals(local_animals)

        self._add_to_sync_queue('create', animal_data)

    async def update_animal(self, animal_uuid: str, animal_data: Dict[str, Any]):
        """Offline-first update. Updates locally immediately, then queues for sync."""
        animal_data['user_id'] = self.user_id # Ensure user_id is always present
        animal_data['sync_status'] = 'pending_update'
        animal_data['last_modified'] = datetime.now().isoformat()

        local_animals = load_animals() or []
        found = False
        for i, animal in enumerate(local_animals):
            if animal.get('uuid') == animal_uuid:
                local_animals[i] = animal_data # Replace old record with updated one
                found = True
                break
        if not found: # Should not happen if uuid is correctly managed
            local_animals.append(animal_data) # Add if somehow not found (e.g., first local edit)

        save_animals(local_animals)

        self._add_to_sync_queue('update', animal_data)

    async def process_sync_queue(self):
        """
        Processes pending local changes and sends them to Supabase.
        """
        queue = self._get_sync_queue()
        if not queue:
            print("Senkronizasyon kuyruğu boş, işlenecek öğe yok.")
            return

        pending_creates = []
        pending_updates = []

        for item in queue:
            if item['action'] == 'create':
                pending_creates.append(item['data'])
            elif item['action'] == 'update':
                pending_updates.append(item['data'])
            # Add 'delete' logic here if implementing deletion

        try:
            if pending_creates:
                print(f"Kuyruktan {len(pending_creates)} yeni hayvan oluşturuluyor...")
                response = self.supabase.table('animals').insert(pending_creates).execute()
                if response.data:
                    print(f"Oluşturulan hayvanlar Supabase'e gönderildi: {len(response.data)} kayıt.")
                else:
                    print("Yeni hayvanlar gönderilirken Supabase'den yanıt alınamadı.")

            if pending_updates:
                print(f"Kuyruktan {len(pending_updates)} hayvan güncelleniyor...")
                # Supabase upsert requires unique constraint, assuming 'uuid' is it.
                # If not, will need to iterate and update individually by uuid.
                for animal_data in pending_updates:
                    response = self.supabase.table('animals').update(animal_data).eq('uuid', animal_data['uuid']).execute()
                    if response.data:
                        print(f"Hayvan güncellendi (UUID: {animal_data['uuid']})")
                    else:
                        print(f"Hayvan güncellenirken Supabase'den yanıt alınamadı (UUID: {animal_data['uuid']})")

            self._clear_sync_queue()
            print("Senkronizasyon kuyruğu başarıyla işlendi ve temizlendi.")

        except Exception as e:
            # Don't clear queue if an error occurs, will retry on next sync
            raise SyncManagerError(f"Senkronizasyon kuyruğu işlenirken hata oluştu: {e}")

    async def synchronize(self, remote_only: bool = False) -> List[Dict[str, Any]]:
        """
        Lokal ve uzak verileri senkronize eder.
        remote_only True ise sadece uzak veriyi çeker ve lokali güncellemez (queue işlemez).
        """
        print("Senkronizasyon başlatılıyor...")
        
        # 1. Önce bekleyen lokal değişiklikleri sunucuya gönder
        if not remote_only:
            try:
                await self.process_sync_queue()
            except SyncManagerError as e:
                print(f"Kuyruk işlenirken hata: {e}. Senkronizasyon devam edecek, kuyrukta kalanlar sonra denenecek.")
                # Hata olsa bile uzak veriyi çekmeye çalış

        # 2. Uzak veriyi çek
        remote_animals = []
        try:
            remote_animals = await self._get_remote_animals()
            print("Uzak veriler başarıyla çekildi.")
        except Exception as e:
            print(f"UYARI: Uzak veriler çekilemedi. Bağlantı sorunları olabilir. Hata: {e}")
            # Bu durumda sadece lokal veriyle devam edeceğiz.

        # 3. Lokal veriyi yükle
        local_animals = load_animals() or []

        # 4. Verileri birleştir
        # Basit birleştirme: UUID'ye göre birleştir, 'last_modified' ile çakışma çözümü
        # Eğer uzaktan veri çekildiyse, uzak veri lokali geçersiz kılar, aksi takdirde lokal kullan.
        # Bu, `process_sync_queue` çalıştıktan sonra uzaktaki verinin en güncel olduğunu varsayar.
        
        merged_data_dict = {animal.get('uuid'): animal for animal in local_animals}
        
        for remote_animal in remote_animals:
            remote_uuid = remote_animal.get('uuid')
            if remote_uuid:
                if remote_uuid in merged_data_dict:
                    # Çakışma varsa daha yeni olanı seç (basit timestamp karşılaştırması)
                    local_last_mod = datetime.fromisoformat(merged_data_dict[remote_uuid].get('last_modified', '1970-01-01T00:00:00'))
                    remote_last_mod = datetime.fromisoformat(remote_animal.get('last_modified', '1970-01-01T00:00:00'))
                    
                    if remote_last_mod > local_last_mod:
                        merged_data_dict[remote_uuid] = remote_animal
                else:
                    merged_data_dict[remote_uuid] = remote_animal

        final_animals = list(merged_data_dict.values())
        
        # 5. Birleştirilmiş veriyi lokale kaydet
        if final_animals:
            try:
                save_animals(final_animals)
                print("Birleştirilmiş veriler lokale kaydedildi.")
            except Exception as e:
                print(f"UYARI: Birleştirilmiş veriler lokale kaydedilirken hata oluştu: {e}")

        print("Senkronizasyon işlemi tamamlandı.")
        return final_animals
