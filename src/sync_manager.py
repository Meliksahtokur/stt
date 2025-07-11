# src/sync_manager.py

"""
Lokal veri ile Supabase veritabanı arasındaki senkronizasyonu yönetir.
Çevrimdışı çalışmayı destekler ve bağlantı kurulduğunda verileri birleştirir.
"""

from datetime import datetime
from supabase import create_client, Client
from config.secrets import SUPABASE_URL, SUPABASE_KEY
from src.persistence import load_animals, save_animals

class SyncManagerError(Exception):
    """Veri senkronizasyonu sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

class SyncManager:
    def __init__(self, user_id):
        if not user_id:
            raise SyncManagerError("Senkronizasyon için kullanıcı ID'si gereklidir.")
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.user_id = user_id

    def _get_remote_animals(self):
        """Supabase'den hayvanları çeker."""
        try:
            response = self.supabase.table('animals').select('*').eq('user_id', self.user_id).execute()
            return response.data
        except Exception as e:
            raise SyncManagerError(f"Uzak veriler çekilirken hata oluştu: {e}")

    def synchronize(self):
        """Lokal ve uzak verileri senkronize eder."""
        print("Senkronizasyon başlatılıyor...")
        try:
            local_animals = load_animals() or []
            remote_animals = self._get_remote_animals()
        except Exception as e:
            print(f"UYARI: Sunucuya bağlanılamadı veya veri çekilemedi. Çevrimdışı modda devam ediliyor. Hata: {e}")
            return local_animals # Sunucuya ulaşılamazsa lokal veriyle devam et

        # Basit bir birleştirme mantığı: ID'ye göre birleştir, şimdilik çakışma çözümü yok.
        # Daha gelişmiş bir senkronizasyon için 'last_updated' timestamp'i kullanılmalıdır.
        
        merged_data_dict = {animal['id']: animal for animal in local_animals}
        
        for remote_animal in remote_animals:
            if remote_animal['id'] not in merged_data_dict:
                merged_data_dict[remote_animal['id']] = remote_animal
            # TODO: Çakışma çözümü eklenecek (örn: hangisi daha yeni ise onu al)

        final_animals = list(merged_data_dict.values())
        
        # Birleştirilmiş veriyi hem lokale hem de uzağa yaz
        try:
            save_animals(final_animals) # Lokale kaydet
            
            # Uzağa kaydet (upsert ile: varsa güncelle, yoksa ekle)
            # Her kayda user_id eklediğimizden emin olmalıyız
            for animal in final_animals:
                animal['user_id'] = self.user_id
            
            self.supabase.table('animals').upsert(final_animals).execute()
            print("Senkronizasyon başarıyla tamamlandı.")
            return final_animals
        except Exception as e:
            raise SyncManagerError(f"Birleştirilmiş veri kaydedilirken hata oluştu: {e}")
