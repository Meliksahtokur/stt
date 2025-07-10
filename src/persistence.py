# src/persistence.py

"""
Bu modül, işlenmiş verilerin kalıcı olarak saklanması (JSON dosyasına yazma)
ve geri yüklenmesi (JSON dosyasından okuma) işlemlerini yönetir.
Dosya işlemleri sırasında oluşabilecek hatalara karşı sağlamlaştırılmıştır.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from config.settings import LOCAL_DATA_FILE

class PersistenceError(Exception):
    """Dosya okuma/yazma işlemleri sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

def default_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def save_animals(animals: List[Dict[str, Any]]):
    """
    Hayvan verilerini bir JSON dosyasına kaydeder.

    Args:
        animals: Kaydedilecek hayvan verilerinin listesi.
    
    Raises:
        PersistenceError: Dosyaya yazma sırasında bir hata oluşursa.
    """
    try:
        with open(LOCAL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(animals, f, ensure_ascii=False, indent=4, default=default_serializer)
        print(f"Veriler başarıyla {LOCAL_DATA_FILE} dosyasına kaydedildi.")
    except (IOError, TypeError) as e:
        # IOError: Yazma izni yoksa, disk doluysa vb.
        # TypeError: Veri içinde JSON'a çevrilemeyen bir tip varsa.
        raise PersistenceError(f"Veriler kaydedilirken bir hata oluştu: {e}") from e

def load_animals() -> Optional[List[Dict[str, Any]]]:
    """
    Hayvan verilerini bir JSON dosyasından yükler.

    Returns:
        Yüklenen hayvan verilerinin listesi veya dosya yoksa/boşsa None.
    
    Raises:
        PersistenceError: Dosya okunamıyorsa veya bozuk JSON içeriyorsa.
    """
    try:
        with open(LOCAL_DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                print("Veri dosyası boş, yeni bir dosya oluşturulacak.")
                return None
            data = json.loads(content)
            
            # Tarih alanlarını tekrar datetime objesine çevir
            for animal in data:
                for key, value in animal.items():
                    if key.endswith('_dt') or key == 'beklenen_dogum_tarihi':
                        if isinstance(value, str):
                            try:
                                animal[key] = datetime.fromisoformat(value)
                            except (ValueError, TypeError):
                                animal[key] = None # Çevrilemezse None yap
            return data

    except FileNotFoundError:
        print(f"{LOCAL_DATA_FILE} bulunamadı. İlk çalıştırmada oluşturulacak.")
        return None
    except json.JSONDecodeError as e:
        raise PersistenceError(f"Veri dosyası bozuk veya geçersiz JSON formatında: {e}") from e
    except IOError as e:
        raise PersistenceError(f"Veri dosyası okunurken bir G/Ç hatası oluştu: {e}") from e
