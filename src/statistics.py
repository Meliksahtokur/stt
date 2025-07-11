# src/statistics.py
from collections import defaultdict
from typing import List, Dict, Any
from datetime import datetime, date

def calculate_statistics(processed_animals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates various statistics about the animals."""
    if not processed_animals:
        return {}

    total_animals = len(processed_animals)
    cow_count = sum(1 for animal in processed_animals if animal.get('sinif') == 'İnek')
    heifer_count = sum(1 for animal in processed_animals if animal.get('sinif') == 'Düve')
    average_inseminations = sum(len(animal.get('tohumlamalar', [])) for animal in processed_animals) / total_animals if total_animals else 0

    # Calculate the average age of animals (assuming 'dogum_tarihi' exists)
    total_age_days = sum((date.today() - animal.get('dogum_tarihi')).days for animal in processed_animals if animal.get('dogum_tarihi'))
    average_age_days = total_age_days / total_animals if total_animals else 0
    average_age_years = round(average_age_days / 365.25, 1) # Account for leap years

    return {
        "toplam_hayvan_sayisi": total_animals,
        "inek_sayisi": cow_count,
        "duve_sayisi": heifer_count,
        "ortalama_tohumlama_sayisi": round(average_inseminations, 1),
        "ortalama_yas_gun": round(average_age_days, 1),
        "ortalama_yas_yil": average_age_years,
    }

def get_animal_specific_stats(animal_uuid: str, all_processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Returns specific statistics for a given animal."""
    animal_record = next((animal for animal in all_processed_data if animal.get('uuid') == animal_uuid), None)

    if not animal_record:
        return {"hata": "Hayvan bulunamadı."}

    total_inseminations = len(animal_record.get('tohumlamalar', []))
    last_insemination = animal_record.get('son_tohumlama', {}).get('tohumlama_tarihi')

    animal_stats = {
        "toplam_tohumlama_sayisi": total_inseminations,
        "sinif_tahmini": animal_record.get('sinif', 'Bilgi Yok'),
        "son_tohumlama": last_insemination,
    }
    return animal_stats

