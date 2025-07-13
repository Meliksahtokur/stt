# src/statistics.py
from collections import defaultdict
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import matplotlib.pyplot as plt
import io
import base64
import logging

def calculate_statistics(processed_animals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates various statistics about the animals."""
    if not processed_animals:
        return {}

    total_animals = len(processed_animals)
    cow_count = sum(1 for animal in processed_animals if animal.get('sinif') == 'İnek')
    heifer_count = sum(1 for animal in processed_animals if animal.get('sinif') == 'Düve')
    
    total_inseminations = sum(len(animal.get('tohumlamalar', [])) for animal in processed_animals)
    average_inseminations = total_inseminations / total_animals if total_animals else 0

    # Calculate the average age of animals (assuming 'dogum_tarihi' exists and is datetime)
    valid_ages_days = [(date.today() - animal['dogum_tarihi']).days 
                       for animal in processed_animals 
                       if animal.get('dogum_tarihi') and isinstance(animal['dogum_tarihi'], datetime)]
    
    average_age_days = sum(valid_ages_days) / len(valid_ages_days) if valid_ages_days else 0
    average_age_years = round(average_age_days / 365.25, 1) # Account for leap years

    return {
        "toplam_hayvan_sayisi": total_animals,
        "inek_sayisi": cow_count,
        "duve_sayisi": heifer_count,
        "ortalama_tohumlama_sayisi": round(average_inseminations, 1),
        "ortalama_yas_gun": round(average_age_days, 1),
        "ortalama_yas_yil": average_age_years,
    }

def calculate_breed_distribution(animals: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculates the count of animals per breed (irk)."""
    breed_counts = defaultdict(int)
    for animal in animals:
        breed = animal.get('irk', 'Bilinmiyor')
        breed_counts[breed] += 1
    return dict(breed_counts)

def generate_pie_chart_base64(data: Dict[str, int], title: str) -> Optional[str]:
    """Generates a pie chart from a dictionary of counts and returns its base64 string."""
    if not data:
        logging.warning(f"No data to generate pie chart for {title}.")
        return None

    labels = data.keys()
    sizes = data.values()

    fig1, ax1 = plt.subplots(figsize=(6, 6))
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.set_title(title)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig1) # Close the figure to free memory
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def calculate_births_per_month(animals: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculates the number of births per month from animal birth dates."""
    births_per_month = defaultdict(int)
    for animal in animals:
        birth_date = animal.get('dogum_tarihi')
        if isinstance(birth_date, datetime):
            month_year_key = birth_date.strftime('%Y-%m') # e.g., '2023-01'
            births_per_month[month_year_key] += 1
    
    # Sort by month-year for consistent plotting
    sorted_births = dict(sorted(births_per_month.items()))
    return sorted_births

def generate_bar_chart_base64(data: Dict[str, int], title: str, xlabel: str, ylabel: str) -> Optional[str]:
    """Generates a bar chart from a dictionary and returns its base64 string."""
    if not data:
        logging.warning(f"No data to generate bar chart for {title}.")
        return None

    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color='skyblue')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    plt.xticks(rotation=45, ha='right') # Rotate labels for better readability
    plt.tight_layout() # Adjust layout to prevent labels from overlapping

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig) # Close the figure to free memory
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def get_animal_specific_stats(animal_uuid: str, all_processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Returns specific statistics for a given animal."""
    animal_record = next((animal for animal in all_processed_data if animal.get('uuid') == animal_uuid), None)

    if not animal_record:
        return {"hata": "Hayvan bulunamadı."}

    total_inseminations = len(animal_record.get('tohumlamalar', []))
    last_insemination = animal_record.get('son_tohumlama', {}).get('tohumlama_tarihi')
    
    # Placeholder for pregnancy success rate if data becomes available
    # For now, it's just a general note based on the overall animal status.
    pregnancy_status = animal_record.get('gebelik_durumu_metin', 'Bilinmiyor')


    animal_stats = {
        "toplam_tohumlama_sayisi": total_inseminations,
        "sinif_tahmini": animal_record.get('sinif', 'Bilgi Yok'),
        "son_tohumlama": last_insemination,
        "mevcut_gebelik_durumu": pregnancy_status, # Add current pregnancy status
        "dogum_tarihi": animal_record.get('dogum_tarihi').strftime('%Y-%m-%d') if isinstance(animal_record.get('dogum_tarihi'), datetime) else "Bilgi Yok"
    }
    return animal_stats

