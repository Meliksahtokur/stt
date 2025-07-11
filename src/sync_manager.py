# src/sync_manager.py

"""
Lokal veri ile Supabase veritabanı arasındaki senkronizasyonu yönetir.
Yeni, ilişkisel veritabanı şemasıyla (animals, inseminations) çalışır.
"""

from supabase import create_client, Client
from config.secrets import SUPABASE_URL, SUPABASE_KEY
# Lokal persistence şimdilik devre dışı, senkronizasyon doğrudan Supabase ile yapılacak.
# İleride çevrimdışı mod için lokal veritabanı (SQLite) eklenebilir.

class SyncManagerError(Exception):
    """Veri senkronizasyonu sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

class SyncManager:
    def __init__(self, user_id: str, supabase_client: Client = None):
        if not user_id:
            raise SyncManagerError("Senkronizasyon için kullanıcı ID'si gereklidir.")
        
        self.supabase = supabase_client or create_client(SUPABASE_URL, SUPABASE_KEY)
        self.user_id = user_id

    def get_all_animal_data(self):
        """
        Kullanıcıya ait tüm hayvanları ve ilişkili tohumlama kayıtlarını çeker.
        """
        try:
            # Önce hayvanları çek
            response = self.supabase.table('animals').select('*').eq('owner_id', self.user_id).execute()
            animals = response.data

            # Her hayvan için tohumlamaları çek
            for animal in animals:
                insemination_response = self.supabase.table('inseminations').select('*').eq('animal_uuid', animal['uuid']).order('tohumlama_tarihi', desc=True).execute()
                animal['tohumlamalar'] = insemination_response.data
            
            return animals
        except Exception as e:
            raise SyncManagerError(f"Uzak veriler çekilirken hata oluştu: {e}")

    def add_new_animal(self, animal_data: dict):
        """
        Yeni bir hayvan ve ilk tohumlama kaydını (varsa) ekler.
        """
        try:
            animal_data['owner_id'] = self.user_id
            
            # Tohumlama bilgisini ayır
            tohumlama_bilgisi = animal_data.pop('tohumlamalar', None)

            # Önce ana hayvan kaydını ekle
            animal_response = self.supabase.table('animals').insert(animal_data).execute()
            new_animal = animal_response.data[0]

            # Eğer tohumlama bilgisi varsa, onu da ilişkili olarak ekle
            if tohumlama_bilgisi and isinstance(tohumlama_bilgisi, list) and tohumlama_bilgisi[0]:
                ilk_tohumlama = tohumlama_bilgisi[0]
                ilk_tohumlama['animal_uuid'] = new_animal['uuid']
                self.supabase.table('inseminations').insert(ilk_tohumlama).execute()
            
            return new_animal
        except Exception as e:
            raise SyncManagerError(f"Yeni hayvan eklenirken hata oluştu: {e}")
