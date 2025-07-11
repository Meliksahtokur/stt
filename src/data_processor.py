# src/data_processor.py
"""
Bu modül, çeşitli kaynaklardan gelen ham hayvan verilerini işler.
Yeni çoklu kimlik sistemine (işletme/devlet/tasma) göre veriyi temizler
ve veritabanına kaydedilecek standart bir formata getirir.
"""
from typing import List, Dict, Any

def normalize_scraped_data(scraped_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Web'den kazınan veriyi yeni veritabanı şemamıza uygun hale getirir.
    Çoklu kimlik alanlarını tanımaya çalışır.
    """
    normalized_list = []
    for row in scraped_data:
        # Bu kısım, web'den gelen verinin sütun adlarına göre özelleştirilmelidir.
        # Varsayımsal bir eşleştirme yapıyoruz:
        normalized_animal = {
            "isletme_kupesi": row.get("id") or row.get("küpe no"), # Birden fazla olası başlığı dene
            "devlet_kupesi": row.get("devlet küpesi") or row.get("resmi no"),
            "tasma_no": row.get("isim") or row.get("tasma"),
            # Diğer alanlar da benzer şekilde eşleştirilir...
            "tohumlama_bilgileri": {
                "tarih": row.get("tohumlama_tarihi"),
                "sperma": row.get("Sperma")
            }
        }
        
        # En az bir kimlik olduğundan emin ol
        if normalized_animal["isletme_kupesi"] or normalized_animal["devlet_kupesi"] or normalized_animal["tasma_no"]:
            normalized_list.append(normalized_animal)
        else:
            print(f"UYARI: Kimlik bilgisi olmayan kayıt atlandı: {row}")
            
    return normalized_list

def get_display_name(animal: Dict[str, Any]) -> str:
    """
    Önem sırasına göre hayvanın listede görünecek adını döndürür.
    """
    return animal.get("isletme_kupesi") or animal.get("devlet_kupesi") or animal.get("tasma_no") or "Bilinmeyen Hayvan"
