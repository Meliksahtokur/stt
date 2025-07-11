# src/display.py
from tabulate import tabulate
from src.data_processor import get_display_name

def display_animal_summary(processed_animals: list):
    """İşlenmiş hayvan verisinin özetini konsolda gösterir."""
    if not processed_animals:
        print("Gösterilecek hayvan kaydı bulunamadı.")
        return
        
    headers = ["Görünür Ad", "Sınıf", "İşletme Küpesi", "Devlet Küpesi", "Tohumlama Sayısı"]
    table_data = []
    
    for animal in processed_animals:
        row = [
            get_display_name(animal),
            animal.get('sinif', 'N/A'),
            animal.get('isletme_kupesi', 'N/A'),
            animal.get('devlet_kupesi', 'N/A'),
            len(animal.get('tohumlamalar', []))
        ]
        table_data.append(row)
        
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
