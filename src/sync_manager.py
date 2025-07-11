import asyncio
import aiohttp
from supabase import create_client, Client
from config.secrets import SUPABASE_URL, SUPABASE_KEY

class SyncManagerError(Exception):
    pass

class SyncManager:
    def __init__(self, user_id: str, supabase_client: Client = None):
        if not user_id:
            raise SyncManagerError("Senkronizasyon için kullanıcı ID'si gereklidir.")
        self.supabase = supabase_client or create_client(SUPABASE_URL, SUPABASE_KEY)
        self.user_id = user_id

    async def get_all_animal_data_async(self):
        try:
            # Önce hayvanları çek
            response = await self.supabase.table('animals').select('*').eq('owner_id', self.user_id).execute()
            animals = response.data

            # Her hayvan için tohumlamaları çek
            for animal in animals:
                insemination_response = await self.supabase.table('inseminations').select('*').eq('animal_uuid', animal['uuid']).order('tohumlama_tarihi', desc=True).execute()
                animal['tohumlamalar'] = insemination_response.data

            return animals
        except Exception as e:
            raise SyncManagerError(f"Uzak veriler çekilirken hata oluştu: {e}")

    # ... (rest of SyncManager class remains the same) ...
