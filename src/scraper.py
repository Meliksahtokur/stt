# src/scraper.py

"""
Bu modül, belirtilen bir web sayfasından hayvan kayıtlarını çekmek,
HTML tablosunu ayrıştırmak ve veriyi yapılandırılmış bir formatta döndürmekle
sorumludur. Hata yönetimi ve sağlamlık ön planda tutulmuştur.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

# Kendi özel hata sınıfımızı tanımlıyoruz. Bu, projenin diğer
# kısımlarının scraper kaynaklı hataları kolayca yakalamasını sağlar.
class ScraperError(Exception):
    """Web kazıma işlemleri sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

def fetch_and_parse_table(url: str) -> List[Dict[str, Any]]:
    """
    Belirtilen URL'den HTML tablosunu çeker ve verileri bir sözlük listesi olarak döndürür.

    Args:
        url: Verinin çekileceği web sayfasının URL'si.

    Returns:
        Her biri bir hayvan kaydını temsil eden sözlüklerden oluşan bir liste.

    Raises:
        ScraperError: Ağ hatası, siteye ulaşılamaması veya beklenen
                      tablonun bulunamaması durumunda fırlatılır.
    """
    print("Veri çekme işlemi başlatılıyor...")
    try:
        # Timeout eklemek, sitenin yanıt vermemesi durumunda sonsuza kadar beklemeyi önler.
        response = requests.get(url, timeout=15)
        # HTTP hata kodları için (404, 500 vb.) otomatik olarak hata fırlat.
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tabloyu bulmaya çalışıyoruz. Eğer bulunamazsa 'None' döner.
        table = soup.find('table')
        if not table:
            raise ScraperError("HTML içeriğinde beklenen '<table>' etiketi bulunamadı.")

        headers = [header.text.strip() for header in table.find_all('th')]
        # Eğer başlıklar boşsa veya yoksa, jenerik başlıklar kullanabiliriz.
        # Ancak şimdilik bu yapının var olduğunu varsayıyoruz.

        data = []
        rows = table.find_all('tr')
        for row in rows[1:]:  # Başlık satırını atla
            cells = row.find_all('td')
            if not cells:
                continue

            # Hücre sayısına göre kırılgan normalizasyon yerine daha esnek bir yapı
            record = {}
            for i, header in enumerate(headers):
                if i < len(cells):
                    record[header] = cells[i].text.strip()
                else:
                    record[header] = "" # Eksik hücreler için boş değer ata
            data.append(record)
        
        print(f"Başarıyla {len(data)} kayıt çekildi.")
        return data

    except requests.exceptions.Timeout as e:
        raise ScraperError(f"Web sitesine bağlanırken zaman aşımı yaşandı: {e}")
    
    except requests.exceptions.RequestException as e:
        # Bu, DNS hatası, bağlantı reddi gibi tüm ağ sorunlarını yakalar.
        raise ScraperError(f"Web sitesine bağlanırken bir ağ hatası oluştu: {e}")

    except Exception as e:
        # BeautifulSoup'tan gelebilecek beklenmedik hatalar veya diğer sorunlar için.
        # Bu, bizim son kalemiz olmalı ve hatayı gizlememeli.
        raise ScraperError(f"Veri ayrıştırılırken beklenmedik bir hata oluştu: {e}")
