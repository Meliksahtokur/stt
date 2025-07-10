# src/main.py

from config.settings import DATA_SOURCE_URL, LOCAL_DATA_FILE
from src.scraper import fetch_and_parse_table
from src.data_processor import process_and_enrich_animal_data, update_animal_statuses
from src.persistence import save_animals, load_animals
from src.display import display_animals, display_notifications

def main():
    print("Hayvan Takip Sistemi Başlatılıyor...")

    # 1. Lokalden daha önce kaydedilmiş veriyi yükle (eğer varsa)
    current_local_animals = load_animals(LOCAL_DATA_FILE)

    # 2. Web sayfasından güncel veriyi çek
    print(f"Veriler '{DATA_SOURCE_URL}' adresinden çekiliyor...")
    scraped_raw_data = fetch_and_parse_table(DATA_SOURCE_URL)
    
    processed_animals = []
    if scraped_raw_data:
        print(f"{len(scraped_raw_data)} adet ham veri çekildi.")
        # Ham veriyi işleyip zenginleştir
        processed_animals = process_and_enrich_animal_data(scraped_raw_data)
        print(f"{len(processed_animals)} adet hayvan kaydı işlendi.")
        
        # Güncel veriyi lokal dosyaya kaydet
        save_animals(processed_animals, LOCAL_DATA_FILE)
    else:
        print("Yeni veri çekilemedi veya çekilen veri boş. Lokaldeki son veriler kullanılacak.")
        processed_animals = current_local_animals # Yeni veri yoksa, lokaldeki veriyi kullan

    if not processed_animals:
        print("Gösterilecek hayvan kaydı bulunamadı. Lütfen veri kaynağını veya lokal dosyayı kontrol edin.")
        return

    # 3. Hayvanların durumlarını (gebelik, bildirim vb.) güncelle
    final_animals = update_animal_statuses(processed_animals)
    
    # 4. Konsolda görüntüle
    display_animals(final_animals)
    display_notifications(final_animals)

    print("\nHayvan Takip Sistemi Tamamlandı.")

if __name__ == "__main__":
    main()
