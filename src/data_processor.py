# src/data_processor.py
from datetime import datetime
from typing import List, Dict, Any
import logging

logging.basicConfig(filename='animal_tracker.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

def classify_animal(insemination_dates: List[datetime]) -> str:
    """Tohumlama geçmişine göre hayvanı 'İnek' veya 'Düve' olarak sınıflandırır."""
    if not insemination_dates:
        return "Bilinmiyor"  # Handle empty insemination_dates
    if len(insemination_dates) <= 1:
        return "Düve"
    sorted_dates = sorted(insemination_dates)
    for i in range(len(sorted_dates) - 1):
        if (sorted_dates[i + 1] - sorted_dates[i]).days > 180:
            return "İnek"
    return "Düve"


def process_animal_records(all_animals_from_db: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Veritabanından gelen ham veriyi işler, zenginleştirir ve arayüze hazırlar."""
    processed_list = []
    for animal in all_animals_from_db:
        try:
            # Convert insemination dates from string to datetime
            inseminations = animal.get('tohumlamalar', [])
            processed_inseminations = []
            insemination_dates_dt = []
            for i in inseminations:
                if 'tohumlama_tarihi' in i and isinstance(i['tohumlama_tarihi'], str):
                    try:
                        insem_dt = datetime.fromisoformat(i['tohumlama_tarihi'])
                        processed_inseminations.append({**i, 'tohumlama_tarihi': insem_dt})
                        insemination_dates_dt.append(insem_dt)
                    except ValueError:
                        processed_inseminations.append(i) # Keep as string if parsing fails
                else:
                    processed_inseminations.append(i) # Keep as is if not string or not present
            animal['tohumlamalar'] = processed_inseminations # Update with processed dates

            animal['sinif'] = classify_animal(insemination_dates_dt)
            animal['display_name'] = get_display_name(animal)

            # Convert 'dogum_tarihi' if it exists and is a string
            dogum_tarihi_str = animal.get('dogum_tarihi')
            if isinstance(dogum_tarihi_str, str):
                try:
                    animal['dogum_tarihi'] = datetime.fromisoformat(dogum_tarihi_str)
                except ValueError:
                    animal['dogum_tarihi'] = None # Set to None if conversion fails
            # Ensure it's None if it's not a valid string or doesn't exist
            elif not isinstance(dogum_tarihi_str, datetime):
                 animal['dogum_tarihi'] = None

            if insemination_dates_dt:
                # Find the latest insemination datetime object
                animal['son_tohumlama'] = max(insemination_dates_dt)
            else:
                animal['son_tohumlama'] = None

            processed_list.append(animal)
        except (KeyError, ValueError, TypeError, AttributeError) as e: # Added AttributeError for safe date operations
            logging.error(f"Error processing animal record: {animal}, Error: {e}")
            # Decide how to handle invalid records (skip, return partial, etc.)
            # For now, we'll continue, but the malformed record might cause downstream issues.
            # A more robust solution would be to return a list of valid records + errors.

    return processed_list


def get_display_name(animal: Dict[str, Any]) -> str:
    """Önem sırasına göre hayvanın görünen adını döndürür."""
    return animal.get("isletme_kupesi") or animal.get("devlet_kupesi") or animal.get("tasma_no") or "Bilinmeyen Hayvan"

