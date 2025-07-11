# src/auth_manager.py

"""
Kullanıcı kimlik doğrulama işlemlerini (kayıt, giriş, çıkış) yönetir.
Supabase GoTrue servisi ile etkileşime girer.
"""

from supabase import create_client, Client
from config.secrets import SUPABASE_URL, SUPABASE_KEY

class AuthManagerError(Exception):
    """Kimlik doğrulama sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

class AuthManager:
    def __init__(self):
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            raise AuthManagerError(f"Supabase istemcisi başlatılamadı: {e}")

    def sign_up(self, email, password):
        try:
            res = self.supabase.auth.sign_up({"email": email, "password": password})
            if res.user:
                return res.user
            if res.error:
                raise AuthManagerError(f"Kayıt başarısız: {res.error.message}")
        except Exception as e:
            raise AuthManagerError(f"Kayıt sırasında beklenmedik bir hata oluştu: {e}")

    def sign_in(self, email, password):
        try:
            res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                return res.user
            if res.error:
                raise AuthManagerError(f"Giriş başarısız: {res.error.message}")
        except Exception as e:
            raise AuthManagerError(f"Giriş sırasında beklenmedik bir hata oluştu: {e}")

    def sign_out(self):
        try:
            self.supabase.auth.sign_out()
        except Exception as e:
            raise AuthManagerError(f"Çıkış sırasında beklenmedik bir hata oluştu: {e}")

    def get_current_user(self):
        try:
            return self.supabase.auth.get_user().user
        except Exception as e:
            # Bu genellikle oturumun süresinin dolduğu anlamına gelir, hata olarak değil, None olarak ele alalım.
            return None
