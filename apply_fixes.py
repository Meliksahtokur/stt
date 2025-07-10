import os
import re
import sys
import subprocess

def apply_fix_to_file(filepath, old_content, new_content):
    """Belirtilen dosyadaki eski içeriği yeni içerikle değiştirir."""
    if not os.path.exists(filepath):
        print(f"HATA: Dosya bulunamadı: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if old_content in content:
        content = content.replace(old_content, new_content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✔ '{filepath}' dosyası güncellendi.")
        return True
    else:
        print(f"✖ '{filepath}' dosyasında değişiklik yapmaya gerek yok veya beklenen içerik bulunamadı.")
        return False

def add_import_if_not_exists(filepath, import_statement, after_import_regex=None):
    """Belirtilen dosyaya import satırı ekler, eğer yoksa."""
    if not os.path.exists(filepath):
        print(f"HATA: Dosya bulunamadı: {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    found = False
    for line in lines:
        if import_statement.strip() in line.strip():
            found = True
            break
    
    if found:
        print(f"✖ '{filepath}' dosyasında '{import_statement.strip()}' zaten mevcut.")
        return False

    # Importu eklemek için uygun yeri bul
    insert_index = -1
    if after_import_regex:
        for i, line in enumerate(lines):
            if re.match(after_import_regex, line):
                insert_index = i + 1
    
    if insert_index != -1:
        lines.insert(insert_index, import_statement + "\n")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✔ '{filepath}' dosyasına '{import_statement.strip()}' eklendi.")
        return True
    else:
        print(f"UYARI: '{filepath}' dosyasına '{import_statement.strip()}' eklemek için uygun yer bulunamadı. Lütfen manuel kontrol edin.")
        return False

def update_requirements_txt(filepath, new_requirements):
    """requirements.txt dosyasını günceller."""
    if not os.path.exists(filepath):
        print(f"HATA: Dosya bulunamadı: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        existing_requirements = [line.strip() for line in f if line.strip()]
    
    updated = False
    with open(filepath, 'a', encoding='utf-8') as f:
        for req in new_requirements:
            if req not in existing_requirements:
                f.write(f"{req}\n")
                print(f"✔ '{filepath}' dosyasına '{req}' eklendi.")
                updated = True
            else:
                print(f"✖ '{req}' zaten '{filepath}' dosyasında mevcut.")
    return updated

def update_buildozer_spec(filepath, full_content):
    """buildozer.spec dosyasını tamamen yeni içerikle değiştirir."""
    if not os.path.exists(filepath):
        print(f"HATA: Dosya bulunamadı: {filepath}")
        return False
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    print(f"✔ '{filepath}' dosyası yeni buildozer.spec içeriği ile güncellendi.")
    return True

def run_terminal_commands(commands):
    """Belirtilen terminal komutlarını çalıştırır."""
    print("\n--- Terminal Komutları Çalıştırılıyor ---")
    for command in commands:
        print(f"\nÇalıştırılıyor: {command}")
        try:
            # shell=True güvenli olmayabilir, ancak kullanıcı ortamında çalıştırılacağı için uygun
            # executable=sys.executable yerine shell=True kullanılıyor
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("Çıktı:\n", result.stdout)
            if result.stderr:
                print("Hata Çıktısı:\n", result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"HATA: Komut çalışırken hata oluştu: {command}")
            print("Hata Kodu:", e.returncode)
            print("Hata Çıktısı:\n", e.stderr)
            return False
        except Exception as e:
            print(f"Beklenmeyen hata: {e}")
            return False
    return True

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    print(f"Proje kök dizini: {project_root}\n")

    # 1. config/settings.py düzeltmesi
    settings_path = os.path.join(project_root, 'config', 'settings.py')
    apply_fix_to_file(
        settings_path,
        "GESTATATION_PERIOD_DAYS = 283",
        "GESTATION_PERIOD_DAYS = 283"
    )

    # 2. src/ui/statistics_screen.py eksik import
    stats_screen_path = os.path.join(project_root, 'src', 'ui', 'statistics_screen.py')
    add_import_if_not_exists(
        stats_screen_path,
        "from kivy.uix.scrollview import ScrollView",
        r"from kivy\.metrics import dp" # Bu satırdan sonra ekle
    )

    # 3. requirements.txt güncelleme
    requirements_path = os.path.join(project_root, 'requirements.txt')
    new_requirements = ["plyer", "buildozer"]
    update_requirements_txt(requirements_path, new_requirements)

    # 4. src/utils.py eksik import
    utils_path = os.path.join(project_root, 'src', 'utils.py')
    add_import_if_not_exists(
        utils_path,
        "from typing import Optional, Any, Dict, List", # Tüm typing importlarını içeren hali
        r"import re" # Bu satırdan sonra ekle
    )
    # Eğer sadece Optional eklenecekse:
    # add_import_if_not_exists(
    #     utils_path,
    #     "from typing import Optional",
    #     r"from datetime import datetime, date, timedelta"
    # )

    # 5. buildozer.spec güncelleme
    buildozer_spec_path = os.path.join(project_root, 'buildozer.spec')
    buildozer_spec_content = """[app]
title = Hayvan Takip Sistemi
package.name = animaltracker
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json
version = 1.0.0
requirements = python3,kivy,requests,beautifulsoup4,tabulate,plyer
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,VIBRATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
orientation = portrait
fullscreen = 0
android.allow_backup = True

# Debug modunda imzalamak için
# release = 0
# debug = 1

# icon.filename = %(source.dir)s/icon.png
# Eğer bir splash screen kullanıyorsanız:
# splash.filename = %(source.dir)s/splash.png
# splash.enable = 1
# splash.time = 5
"""
    update_buildozer_spec(buildozer_spec_path, buildozer_spec_content)

    print("\n--- Dosya Güncellemeleri Tamamlandı ---\n")

    # Terminal komutları
    terminal_commands = [
        "source venv/bin/activate", # Sanal ortam adı 'venv' ise, değilse kendi adınızla değiştirin
        "pip install -r requirements.txt",
        "buildozer init", # Eğer buildozer.spec'i manuel olarak zaten oluşturduysanız, bu adımı atlayabilirsiniz.
        "buildozer android debug"
    ]

    print("Şimdi terminal komutları çalıştırılacak. Eğer sanal ortamınızın adı 'venv' değilse veya farklı bir konumdaysa, lütfen 'source venv/bin/activate' komutunu kendiniz düzenleyin.")
    input("Devam etmek için Enter'a basın...")
    
    # Komutları çalıştırmadan önce, sanal ortam aktivasyonunun ayrı bir süreçte çalıştırılması gerektiğini belirtelim.
    # Bu betik içinden sanal ortamı kalıcı olarak aktifleştirmek zor olduğu için, kullanıcıya rehberlik edeceğiz.

    print("\n--------------------------------------------------------------")
    print("DİKKAT: Sanal ortamın doğru şekilde aktifleştirilmesi için:")
    print("1. Bu betiği çalıştırdıktan sonra terminalinizi Kapatmayın.")
    print("2. 'source venv/bin/activate' komutunu **manuel olarak** terminalde çalıştırın.")
    print("3. Ardından, 'pip install -r requirements.txt' ve diğer 'buildozer' komutlarını manuel olarak çalıştırın.")
    print("--------------------------------------------------------------\n")
    
    print("\nOtomatik dosya düzenlemeleri tamamlandı. Şimdi lütfen yukarıdaki terminal komutlarını manuel olarak sırasıyla çalıştırın.")
