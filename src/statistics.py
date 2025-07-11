# src/statistics.py
from collections import defaultdict
from typing import List, Dict, Any

def calculate_statistics(processed_animals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Tüm istatistikleri hesaplayan ana fonksiyondur."""
    # Bu fonksiyonun içi şimdilik aynı kalabilir, gelecekte geliştirilecek.
    if not processed_animals: return {}
    total_animals = len(processed_animals)
    cow_count = sum(1 for animal in processed_animals if animal.get('sinif') == 'İnek')
    heifer_count = sum(1 for animal in processed_animals if animal.get('sinif') == 'Düve')
    # ... diğer genel istatistikler ...
    return {"toplam_hayvan_sayisi": total_animals, "inek_sayisi": cow_count, "duve_sayisi": heifer_count}

def get_animal_specific_stats(animal_uuid: str, all_processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Belirli bir hayvana ait özel istatistikleri döndürür."""
    animal_record = next((animal for animal in all_processed_data if animal.get('uuid') == animal_uuid), None)

    if not animal_record:
        return {"hata": "Hayvan bulunamadı."}

    total_inseminations = len(animal_record.get('tohumlamalar', []))

    animal_stats = {
        "toplam_tohumlama_sayisi": total_inseminations,
        "sinif_tahmini": animal_record.get('sinif', 'Bilgi Yok'),
    }
    return animal_stats
