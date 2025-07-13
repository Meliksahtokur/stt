

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
    def __init__(self, on_success=None, on_error=None):
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self._on_success_callback = on_success
            self._on_error_callback = on_error
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"Supabase istemcisi başlatılamadı: {e}")
            raise AuthManagerError(f"Supabase istemcisi başlatılamadı: {e}")

    async def sign_up(self, email, password):
        try:
            res = self.supabase.auth.sign_up({"email": email, "password": password})
            if res.user:
                if self._on_success_callback:
                    self._on_success_callback(res.user)
                return res.user
            if res.error:
                error_msg = f"Kayıt başarısız: {res.error.message}"
                if self._on_error_callback:
                    self._on_error_callback(error_msg)
                raise AuthManagerError(error_msg)
        except Exception as e:
            error_msg = f"Kayıt sırasında beklenmedik bir hata oluştu: {e}"
            if self._on_error_callback:
                self._on_error_callback(error_msg)
            raise AuthManagerError(error_msg)

    async def sign_in(self, email, password):
        try:
            res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                if self._on_success_callback:
                    self._on_success_callback(res.user)
                return res.user
            if res.error:
                error_msg = f"Giriş başarısız: {res.error.message}"
                if self._on_error_callback:
                    self._on_error_callback(error_msg)
                raise AuthManagerError(error_msg)
        except Exception as e:
            error_msg = f"Giriş sırasında beklenmedik bir hata oluştu: {e}"
            if self._on_error_callback:
                self._on_error_callback(error_msg)
            raise AuthManagerError(error_msg)

    async def sign_out(self):
        try:
            self.supabase.auth.sign_out()
            if self._on_success_callback:
                self._on_success_callback(None) # Notify that user is logged out
        except Exception as e:
            error_msg = f"Çıkış sırasında beklenmedik bir hata oluştu: {e}"
            if self._on_error_callback:
                self._on_error_callback(error_msg)
            raise AuthManagerError(error_msg)

    async def check_session(self):
        try:
            user = self.supabase.auth.get_user().user
            if user:
                if self._on_success_callback:
                    self._on_success_callback(user)
            else:
                if self._on_success_callback:
                    self._on_success_callback(None)
            return user
        except Exception as e:
            # This usually means no active session or session expired.
            # We don't necessarily show an error, but ensure no user is set.
            if self._on_success_callback:
                self._on_success_callback(None)
            return None
