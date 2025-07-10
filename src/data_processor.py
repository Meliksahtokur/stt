# src/data_processor.py

from datetime import datetime, timedelta
from src.utils import parse_flexible_date_string, safe_int
from config.settings import GESTATATION_PERIOD_DAYS

def process_and_enrich_animal_data(raw_animal_dicts):
    """
    Processes raw animal data dictionaries, parses dates, calculates birth dates,
    and enriches with initial status.
    """
    processed_animals = []
    for raw_animal in raw_animal_dicts:
        # Güvenli erişim ve varsayılan değerler
        animal_id = safe_int(raw_animal.get('id'))
        sperma = raw_animal.get('Sperma', '').strip()
        belgeno = raw_animal.get('belgeno', '').strip() # Artık ayrılmış belgeno
        kupeno = raw_animal.get('kupeno', '').strip()
        irki = raw_animal.get('irki', '').strip()
        not_info = raw_animal.get('Not', '').strip()
        
        ilk_tohumlama_tarihi_str = raw_animal.get('tarih', '').strip()
        gebeli_onay_tarihi_str = raw_animal.get('Gebe_mi', '').strip()

        ilk_tohumlama_tarihi = parse_flexible_date_string(ilk_tohumlama_tarihi_str)
        gebeli_onay_tarihi = parse_flexible_date_string(gebeli_onay_tarihi_str)

        beklenen_dogum_tarihi = None
        if ilk_tohumlama_tarihi:
            beklenen_dogum_tarihi = ilk_tohumlama_tarihi + timedelta(days=GESTATATION_PERIOD_DAYS)

        # Temel hayvan sözlüğünü oluştur
        processed_animal = {
            'id': animal_id,
            'Sperma': sperma,
            'belgeno': belgeno,
            'kupeno': kupeno,
            'irki': irki,
            'Not': not_info,
            'ilk_tohumlama_tarihi': ilk_tohumlama_tarihi,
            'gebeli_onay_tarihi': gebeli_onay_tarihi,
            'beklenen_dogum_tarihi': beklenen_dogum_tarihi,
            'gebelik_durumu_metin': "Durum Belirlenmedi" # update_animal_statuses'da güncellenecek
        }
        processed_animals.append(processed_animal)
        
    return processed_animals

def update_animal_statuses(animals):
    """Updates the 'gebelik_durumu_metin' for each animal based on current date."""
    today = datetime.now()
    updated_animals = []
    
    for animal in animals:
        current_animal = animal.copy() # Orijinal objeyi değiştirmemek için kopya
        
        # Eğer tohumlama tarihi yoksa, gebelik durumu belirlenemez
        if not current_animal.get('ilk_tohumlama_tarihi'):
            current_animal['gebelik_durumu_metin'] = "Tohumlama Tarihi Bilinmiyor"
            updated_animals.append(current_animal)
            continue

        # Beklenen doğum tarihi zaten tohumlama tarihinden hesaplandı
        # Sadece datetime objelerinden ISO string'lere dönüştürülmüşse, burada geri çevrilmeliydi
        # Ancak, bu fonksiyonu çağırırken datetime objeleri olarak geldiğini varsayıyoruz.

        if current_animal['beklenen_dogum_tarihi']:
            days_until_birth = (current_animal['beklenen_dogum_tarihi'] - today).days

            if days_until_birth < 0:
                current_animal['gebelik_durumu_metin'] = "Doğum Gerçekleşti/Geçti"
            elif 0 <= days_until_birth <= 20:
                current_animal['gebelik_durumu_metin'] = f"Doğuma SON 20 GÜN! ({days_until_birth} gün kaldı)"
            elif 20 < days_until_birth <= 60:
                current_animal['gebelik_durumu_metin'] = f"Doğuma SON 2 AY! ({days_until_birth} gün kaldı)"
            else:
                # Gebeliğin onaylandığı tarih var ve günümüzden önceyse, "Gebelik Onaylandı" diyebiliriz.
                # Aksi takdirde, "Tohumlandı, Gebelik Bekleniyor"
                if current_animal['gebeli_onay_tarihi'] and current_animal['gebeli_onay_tarihi'] <= today:
                    current_animal['gebelik_durumu_metin'] = "Gebelik Onaylandı"
                else:
                    current_animal['gebelik_durumu_metin'] = "Tohumlandı, Gebelik Bekleniyor"
        else:
            current_animal['gebelik_durumu_metin'] = "Beklenen Doğum Tarihi Hesaplamadı" # Tohumlama tarihi yoksa
        
        updated_animals.append(current_animal)
            
    return updated_animals
