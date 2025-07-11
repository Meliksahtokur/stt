# src/data_processor.py

"""
Bu modül, scraper'dan gelen ham hayvan verilerini işler, zenginleştirir
ve analiz için hazır hale getirir. Gebelik durumlarını hesaplar ve
kritik tarihleri belirler.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from config.settings import GESTATION_PERIOD_DAYS
from src.utils import parse_flexible_date_string, safe_int

class DataProcessingError(Exception):
    """Veri işleme sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

def process_and_enrich_animal_data(animal_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ham hayvan verilerini işler, gebelik durumunu ve beklenen doğum tarihini hesaplar.

    Args:
        animal_data: Scraper'dan gelen, her biri bir hayvanı temsil eden sözlük listesi.

    Returns:
        İşlenmiş ve zenginleştirilmiş verileri içeren yeni bir sözlük listesi.
    
    Raises:
        DataProcessingError: Veri işleme sırasında bir hata oluşursa.
    """
    processed_animals = []
    required_keys = ['id', 'tohumlama_tarihi']

    for animal in animal_data:
        # Adım 1: Gerekli anahtarların varlığını kontrol et
        if not all(key in animal for key in required_keys):
            print(f"UYARI: Zorunlu alanlar ('id', 'tohumlama_tarihi') eksik olduğu için kayıt atlandı: {animal}")
            continue

        try:
            animal_id = safe_int(animal.get('id'))
            if animal_id is None:
                print(f"UYARI: Geçersiz veya eksik ID, kayıt atlandı: {animal}")
                continue

            tohumlama_tarihi_str = animal.get('tohumlama_tarihi', '')
            tohumlama_tarihi: Optional[datetime] = parse_flexible_date_string(tohumlama_tarihi_str)

            # Zenginleştirilmiş veri için yeni bir sözlük oluştur
            enriched_animal = animal.copy()
            enriched_animal['id'] = animal_id
            enriched_animal['tohumlama_tarihi_dt'] = tohumlama_tarihi
            enriched_animal['beklenen_dogum_tarihi'] = None
            enriched_animal['gebelik_durumu_metin'] = "Bilinmiyor"

            if tohumlama_tarihi:
                beklenen_dogum_tarihi = tohumlama_tarihi + timedelta(days=GESTATION_PERIOD_DAYS)
                enriched_animal['beklenen_dogum_tarihi'] = beklenen_dogum_tarihi

                gun_farki = (datetime.now() - tohumlama_tarihi).days

                if gun_farki <= GESTATION_PERIOD_DAYS:
                    enriched_animal['gebelik_durumu_metin'] = f"GEBE ({gun_farki} gün)"
                else:
                    enriched_animal['gebelik_durumu_metin'] = f"Doğum Geçmiş ({gun_farki - GESTATION_PERIOD_DAYS} gün önce)"
            else:
                # Tohumlama tarihi yoksa veya geçersizse durumu belirt
                enriched_animal['gebelik_durumu_metin'] = "Tohumlama Tarihi Yok/Geçersiz"

            processed_animals.append(enriched_animal)

        except (KeyError, ValueError, TypeError) as e:
            # Beklenen hataları yakala ve daha anlamlı bir hata fırlat
            animal_id_str = animal.get('id', 'Bilinmeyen ID')
            raise DataProcessingError(f"'{animal_id_str}' ID'li hayvan işlenirken hata oluştu: {e}") from e

    return processed_animals

def update_animal_statuses(animals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Mevcut hayvan listesinin durumlarını günceller (Bu fonksiyon process_and_enrich ile birleştirilebilir
    veya daha karmaşık durum güncellemeleri için ayrılabilir. Şimdilik basit tutulmuştur).
    """
    # Bu fonksiyonun mantığı büyük ölçüde process_and_enrich_animal_data içine entegre edildi.
    # Gelecekte daha karmaşık güncellemeler için kullanılabilir.
    # Şimdilik sadece gelen listeyi döndürüyor.
    return animals
