# src/permissions_manager.py
"""
Kullanıcıların yetkilerini kontrol eder ve denetim kayıtları oluşturur.
"""
from supabase import Client
from typing import Dict, Any

class PermissionsManager:
    def __init__(self, supabase_client: Client, user_id: str):
        self.db = supabase_client
        self.user_id = user_id

    def _log_action(self, action: str, details: Dict[str, Any]):
        """Yapılan her işlemi audit_log tablosuna kaydeder."""
        try:
            self.db.table('audit_log').insert({
                "user_id": self.user_id,
                "action": action,
                "details": details
            }).execute()
        except Exception as e:
            print(f"UYARI: Denetim kaydı oluşturulamadı: {e}")

    def can_read_animals(self) -> bool:
        # TODO: Gerçek yetki kontrolü profiller tablosundan yapılacak.
        # Şimdilik her zaman izin veriyoruz.
        self._log_action("read_animals_list", {"status": "attempted"})
        return True

    def can_edit_animal(self, animal_uuid: str) -> bool:
        self._log_action("edit_animal", {"status": "attempted", "animal_uuid": animal_uuid})
        # This is where you would query your 'profiles' table in Supabase
        # to check if self.user_id has an 'admin' or 'editor' role.
        # For now, we allow it.
        #
        # try:
        #     profile = self.db.table('profiles').select('role').eq('id', self.user_id).single().execute()
        #     if profile.data and profile.data['role'] in ['admin', 'editor']:
        #         return True
        # except Exception as e:
        #     print(f"Permission check failed: {e}")
        #     return False
        return True
