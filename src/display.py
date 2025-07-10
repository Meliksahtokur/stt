# src/display.py

from datetime import datetime
from tabulate import tabulate # Sizin kodunuzdaki kütüphane

def display_animals(animals):
    """Displays animal data in a console-friendly table format, sorted by expected birth date."""
    print("\n--- TÜM HAYVAN KAYITLARI (Beklenen Doğum Tarihine Göre Sıralı) ---")
    
    if not animals:
        print("Gösterilecek hayvan kaydı bulunamadı.")
        return

    # Sort animals by expected birth date (None values go to the end)
    sorted_animals = sorted(
        animals, 
        key=lambda x: x.get('beklenen_dogum_tarihi') or datetime(9999, 12, 31) # None'ları sona atar
    )

    # Hazırlanacak tablo verisi
    table_data = []
    headers = [
        "ID", "Küpe No", "Sperma", "Belge No", "Irkı", "Not", 
        "Tohumlama", "Onay Tarihi", "Beklenen Doğum", "Durum"
    ]
    table_data.append(headers) # Başlıkları ilk satır olarak ekle

    for animal in sorted_animals:
        beklenen_dogum_str = animal['beklenen_dogum_tarihi'].strftime('%d.%m.%Y') if animal['beklenen_dogum_tarihi'] else 'N/A'
        ilk_tohumlama_str = animal['ilk_tohumlama_tarihi'].strftime('%d.%m.%Y') if animal['ilk_tohumlama_tarihi'] else 'N/A'
        gebeli_onay_str = animal['gebeli_onay_tarihi'].strftime('%d.%m.%Y') if animal['gebeli_onay_tarihi'] else 'N/A'
        
        row = [
            animal['id'] if animal['id'] is not None else 'N/A',
            animal['kupeno'],
            animal['Sperma'],
            animal['belgeno'],
            animal['irki'],
            animal['Not'],
            ilk_tohumlama_str,
            gebeli_onay_str,
            beklenen_dogum_str,
            animal['gebelik_durumu_metin']
        ]
        table_data.append(row)
    
    print(tabulate(table_data, headers="firstrow", tablefmt="grid"))


def display_notifications(animals):
    """Displays animals needing notification (Doğuma Son 2 Ay ve 20 Gün)."""
    print("\n--- ACİL BİLDİRİMLER (DOĞUMA YAKIN HAYVANLAR) ---")
    
    notification_animals = [
        animal for animal in animals 
        if "Doğuma SON 2 AY!" in animal['gebelik_durumu_metin'] or 
           "Doğuma SON 20 GÜN!" in animal['gebelik_durumu_metin']
    ]
    
    if not notification_animals:
        print("Şu anda acil bildirim bulunmamaktadır.")
        return

    # Sort notifications by urgency (closest to birth)
    sorted_notifications = sorted(
        notification_animals, 
        key=lambda x: (x['beklenen_dogum_tarihi'] - datetime.now()).days if x.get('beklenen_dogum_tarihi') else float('inf')
    )

    notification_table_data = []
    headers = ["ID", "Küpe No", "Sperma", "Beklenen Doğum", "Durum"]
    notification_table_data.append(headers)

    for animal in sorted_notifications:
        beklenen_dogum_str = animal['beklenen_dogum_tarihi'].strftime('%d.%m.%Y') if animal['beklenen_dogum_tarihi'] else 'N/A'
        row = [
            animal['id'] if animal['id'] is not None else 'N/A',
            animal['kupeno'],
            animal['Sperma'],
            beklenen_dogum_str,
            animal['gebelik_durumu_metin']
        ]
        notification_table_data.append(row)
    
    print(tabulate(notification_table_data, headers="firstrow", tablefmt="grid"))
