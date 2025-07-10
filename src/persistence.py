# src/persistence.py

import json
import os
from datetime import datetime

def save_animals(animals, filename):
    """
    Saves processed animal data to a JSON file.
    Converts datetime objects to ISO format strings for serialization.
    """
    serializable_animals = []
    for animal in animals:
        serializable_animal = animal.copy()
        for key, value in serializable_animal.items():
            if isinstance(value, datetime):
                serializable_animal[key] = value.isoformat()
        serializable_animals.append(serializable_animal)
        
    os.makedirs(os.path.dirname(filename), exist_ok=True) # Klasör yoksa oluştur
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(serializable_animals, f, ensure_ascii=False, indent=4)
    print(f"Veriler '{filename}' dosyasına kaydedildi.")

def load_animals(filename):
    """
    Loads animal data from a JSON file and converts date strings back to datetime objects.
    """
    if not os.path.exists(filename) or os.stat(filename).st_size == 0:
        print(f"Uyarı: '{filename}' dosyası bulunamadı veya boş. Yeni veri çekilecek.")
        return []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            animals = json.load(f)
        # Convert ISO format strings back to datetime objects
        for animal in animals:
            if animal.get('ilk_tohumlama_tarihi'):
                try: animal['ilk_tohumlama_tarihi'] = datetime.fromisoformat(animal['ilk_tohumlama_tarihi'])
                except ValueError: animal['ilk_tohumlama_tarihi'] = None
            if animal.get('gebeli_onay_tarihi'):
                try: animal['gebeli_onay_tarihi'] = datetime.fromisoformat(animal['gebeli_onay_tarihi'])
                except ValueError: animal['gebeli_onay_tarihi'] = None
            if animal.get('beklenen_dogum_tarihi'):
                try: animal['beklenen_dogum_tarihi'] = datetime.fromisoformat(animal['beklenen_dogum_tarihi'])
                except ValueError: animal['beklenen_dogum_tarihi'] = None
        return animals
    except json.JSONDecodeError as e:
        print(f"Hata: '{filename}' dosyası bozuk veya geçersiz JSON formatında. Hata: {e}")
        return []
    except Exception as e:
        print(f"Lokal veri yüklenirken beklenmeyen bir hata oluştu: {e}")
        return []
