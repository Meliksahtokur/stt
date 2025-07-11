# src/data_processor.py
from datetime import datetime
from typing import List, Dict, Any

def classify_animal(insemination_dates: List[datetime]) -> str:
    """Tohumlama geçmişine göre hayvanı 'İnek' veya 'Düve' olarak sınıflandırır."""
    if len(insemination_dates) <= 1:
        return "Düve"
    sorted_dates = sorted(insemination_dates)
    for i in range(len(sorted_dates) - 1):
        if (sorted_dates[i+1] - sorted_dates[i]).days > 180:
            return "İnek"
    return "Düve"

def process_animal_records(all_animals_from_db: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Veritabanından gelen ham veriyi işler, zenginleştirir ve arayüze hazırlar."""
    processed_list = []
    for animal in all_animals_from_db:
        inseminations = animal.get('tohumlamalar', [])
        insemination_dates = [datetime.fromisoformat(i['tohumlama_tarihi']) for i in inseminations if i.get('tohumlama_tarihi')]
        
        animal['sinif'] = classify_animal(insemination_dates)
        animal['display_name'] = get_display_name(animal)
        
        if insemination_dates:
            animal['son_tohumlama'] = sorted(inseminations, key=lambda x: x['tohumlama_tarihi'], reverse=True)[0]
        else:
            animal['son_tohumlama'] = None
        
        processed_list.append(animal)
    return processed_list

def get_display_name(animal: Dict[str, Any]) -> str:
    """Önem sırasına göre hayvanın görünen adını döndürür."""
    return animal.get("isletme_kupesi") or animal.get("devlet_kupesi") or animal.get("tasma_no") or "Bilinmeyen Hayvan"
