# src/data_processor.py

"""
Bu modül, scraper'dan gelen ham hayvan verilerini işler, zenginleştirir
ve analiz için hazır hale getirir. Hayvan sınıflandırması (İnek/Düve tahmini),
gebelik durumlarını hesaplama ve kritik tarihleri belirleme gibi
akıllı analizler yapar.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from config.settings import GESTATION_PERIOD_DAYS
from src.utils import parse_flexible_date_string, safe_int

class DataProcessingError(Exception):
    """Veri işleme sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

def _tahmin_hayvan_sinifi(tohumlama_gecmisi: List[datetime]) -> str:
    """
    Hayvanın tohumlama geçmişine bakarak sınıfını (İnek/Düve) tahmin eder.
    
    Kural: Eğer sıralı tohumlamalar arasında 6 aydan (yaklaşık 180 gün)
    daha uzun bir boşluk varsa, bu hayvanın doğum yapıp tekrar tohumlandığı
    varsayılır ve 'İnek' olarak sınıflandırılır. Aksi halde 'Düve'dir.
    """
    if len(tohumlama_gecmisi) <= 1:
        return "Düve" # Tek bir tohumlama veya hiç tohumlama yoksa düvedir.
    
    # Geçmişi eskiden yeniye doğru sırala
    sirali_gecmis = sorted(tohumlama_gecmisi)
    
    for i in range(len(sirali_gecmis) - 1):
        fark = (sirali_gecmis[i+1] - sirali_gecmis[i]).days
        if fark > 180: # 6 ay ~ 180 gün
            return "İnek" # Arada büyük bir boşluk var, bu bir inektir.
            
    return "Düve" # Büyük bir boşluk bulunamadı, bu bir düvedir.

def process_and_enrich_animal_data(animal_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ham hayvan verilerini işler, hayvan sınıfını tahmin eder, gebelik durumunu
    ve beklenen doğum tarihini hesaplar.
    """
    processed_animals = []
    
    # Veriyi hayvan ID'sine göre grupla
    hayvanlar_gruplu: Dict[int, List[Dict[str, Any]]] = {}
    for animal in animal_data:
        animal_id = safe_int(animal.get('id'))
        if animal_id is None:
            print(f"UYARI: Geçersiz veya eksik ID, kayıt atlandı: {animal}")
            continue
        if animal_id not in hayvanlar_gruplu:
            hayvanlar_gruplu[animal_id] = []
        hayvanlar_gruplu[animal_id].append(animal)

    # Her bir hayvan grubunu işle
    for animal_id, tohumlamalar in hayvanlar_gruplu.items():
        try:
            # Tohumlama tarihlerini topla
            tohumlama_tarihleri_dt: List[datetime] = []
            for kayit in tohumlamalar:
                tarih_str = kayit.get('tohumlama_tarihi', '')
                tarih_dt = parse_flexible_date_string(tarih_str)
                if tarih_dt:
                    tohumlama_tarihleri_dt.append(tarih_dt)
            
            # Hayvan sınıfını tahmin et
            hayvan_sinifi = _tahmin_hayvan_sinifi(tohumlama_tarihleri_dt)
            
            # En son tohumlama kaydını baz alarak işlem yap
            en_son_kayit = sorted(tohumlamalar, key=lambda x: parse_flexible_date_string(x.get('tohumlama_tarihi', '')) or datetime.min, reverse=True)[0]
            
            en_son_tohumlama_tarihi = parse_flexible_date_string(en_son_kayit.get('tohumlama_tarihi'))

            enriched_animal = en_son_kayit.copy()
            enriched_animal['id'] = animal_id
            enriched_animal['sinif'] = hayvan_sinifi # YENİ ALAN
            enriched_animal['tohumlama_gecmisi_sayisi'] = len(tohumlama_tarihleri_dt) # YENİ ALAN
            enriched_animal['tohumlama_tarihi_dt'] = en_son_tohumlama_tarihi
            enriched_animal['beklenen_dogum_tarihi'] = None
            enriched_animal['gebelik_durumu_metin'] = "Bilinmiyor"

            if en_son_tohumlama_tarihi:
                beklenen_dogum_tarihi = en_son_tohumlama_tarihi + timedelta(days=GESTATION_PERIOD_DAYS)
                enriched_animal['beklenen_dogum_tarihi'] = beklenen_dogum_tarihi
                gun_farki = (datetime.now() - en_son_tohumlama_tarihi).days
                if gun_farki <= GESTATION_PERIOD_DAYS:
                    enriched_animal['gebelik_durumu_metin'] = f"GEBE ({gun_farki} gün)"
                else:
                    enriched_animal['gebelik_durumu_metin'] = f"Doğum Geçmiş ({gun_farki - GESTATION_PERIOD_DAYS} gün önce)"
            else:
                enriched_animal['gebelik_durumu_metin'] = "Tohumlama Tarihi Yok/Geçersiz"

            processed_animals.append(enriched_animal)

        except Exception as e:
            raise DataProcessingError(f"'{animal_id}' ID'li hayvan işlenirken bir hata oluştu: {e}") from e

    return processed_animals

# update_animal_statuses fonksiyonu şimdilik aynı kalabilir.
def update_animal_statuses(animals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return animals
