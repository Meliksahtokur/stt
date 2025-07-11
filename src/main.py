# src/main.py

import sys
import os

# Proje ana dizinini Python'un arama yoluna ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.auth_manager import AuthManager
from src.sync_manager import SyncManager
from src.permissions_manager import PermissionsManager
from src.data_processor import get_display_name

def main_app():
    """
    Uygulamanın ana mantık akışı.
    Kivy arayüzü bu fonksiyonları çağıracak.
    """
    print("--- Sürü Yönetim Platformu ---")
    auth = AuthManager()
    
    # 1. Kimlik Doğrulama
    user = auth.get_current_user()
    if not user:
        print("Giriş yapılmamış. Lütfen önce giriş yapın.")
        # Gerçek uygulamada bu bir giriş ekranı açacak.
        # Test için manuel giriş yapıyoruz.
        try:
            email = "test@example.com" # Burayı kendi test kullanıcınızla değiştirin
            password = "password"      # Burayı kendi şifrenizle değiştirin
            user = auth.sign_in(email, password)
            print(f"Giriş başarılı: {user.email}")
        except Exception as e:
            print(f"Test girişi başarısız: {e}")
            return

    # 2. Yetki ve Senkronizasyon Yöneticilerini Başlat
    permissions = PermissionsManager(auth.supabase, user.id)
    sync = SyncManager(user.id, auth.supabase)

    # 3. Veri Çekme ve Gösterme
    if permissions.can_read_animals():
        print("\nHayvan verileri çekiliyor...")
        try:
            all_animals = sync.get_all_animal_data()
            print(f"Toplam {len(all_animals)} hayvan kaydı bulundu.")
            
            if all_animals:
                print("\n--- Sürü Listesi ---")
                for animal in all_animals:
                    display_name = get_display_name(animal)
                    tohumlama_sayisi = len(animal.get('tohumlamalar', []))
                    print(f"- {display_name} (Tohumlamalar: {tohumlama_sayisi})")
            
        except Exception as e:
            print(f"Veri çekilirken bir hata oluştu: {e}")
    else:
        print("Hayvan verilerini görme yetkiniz yok.")

if __name__ == "__main__":
    main_app()
