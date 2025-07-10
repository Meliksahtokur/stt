# src/main.py

"""
Uygulamanın ana giriş noktası. Tüm operasyonu yönetir, modülleri
orkestra şefi gibi çalıştırır ve kullanıcıya sonuçları sunar.
Hata yönetimi, tüm operasyonun çökmesini engellemek için merkezileştirilmiştir.
"""

from config.settings import DATA_SOURCE_URL
from src.scraper import fetch_and_parse_table, ScraperError
from src.data_processor import process_and_enrich_animal_data, DataProcessingError
from src.persistence import save_animals, load_animals, PersistenceError
from src.display import display_animals, display_notifications

def main():
    """
    Ana uygulama döngüsü.
    """
    print("Hayvan Takip ve Gebelik Bildirim Sistemi Başlatılıyor...")

    try:
        # 1. Veriyi Çek
        print(f"Veriler şu adresten çekiliyor: {DATA_SOURCE_URL}")
        raw_data = fetch_and_parse_table(DATA_SOURCE_URL)
        if not raw_data:
            print("Web sitesinden yeni veri çekilemedi veya sitede kayıt yok.")
            # Eski veriyi yüklemeyi deneyebiliriz
            animals = load_animals()
            if not animals:
                print("Lokalde de kayıtlı veri bulunamadı. Uygulama sonlandırılıyor.")
                return
        else:
            # 2. Veriyi İşle ve Zenginleştir
            print("Veriler işleniyor ve zenginleştiriliyor...")
            animals = process_and_enrich_animal_data(raw_data)

            # 3. İşlenmiş Veriyi Kaydet
            print("İşlenmiş veriler kaydediliyor...")
            save_animals(animals)

        # 4. Sonuçları Göster
        if animals:
            print("\n--- Hayvan Durum Raporu ---")
            display_animals(animals)
            print("\n--- Önemli Bildirimler ---")
            display_notifications(animals)
        else:
            print("Gösterilecek işlenmiş veri bulunamadı.")

    except ScraperError as e:
        print(f"\n[HATA] Veri çekme aşamasında kritik bir sorun oluştu: {e}")
        print("Lütfen internet bağlantınızı veya config/settings.py dosyasındaki URL'yi kontrol edin.")
    except DataProcessingError as e:
        print(f"\n[HATA] Veri işleme aşamasında kritik bir sorun oluştu: {e}")
        print("Lütfen web sitesindeki verilerin formatını kontrol edin.")
    except PersistenceError as e:
        print(f"\n[HATA] Veri kaydetme/okuma sırasında kritik bir sorun oluştu: {e}")
        print("Lütfen dosya izinlerini veya disk durumunu kontrol edin.")
    except Exception as e:
        # Beklenmedik diğer tüm hatalar için son kale
        print(f"\n[BEKLENMEDİK HATA] Program çalışırken bir sorunla karşılaştı: {e}")
        print("Lütfen geliştirici ile iletişime geçin.")
    finally:
        print("\nUygulama çalışmasını tamamladı.")

if __name__ == "__main__":
    main()
