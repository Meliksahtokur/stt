# src/scraper.py

import requests
from bs4 import BeautifulSoup
from config.settings import COLUMN_HEADERS

def fetch_and_parse_table(url, expected_cols_after_normalization=8):
    """
    Fetches an HTML table from the given URL and parses its content.
    Applies normalization rules to handle varying column counts as per user's code.
    Returns a list of dictionaries, where each dictionary represents a row.
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        response.encoding = response.apparent_encoding # Use apparent encoding for better character handling
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            raise ValueError(f"Tablo bulunamadı: {url}")

        rows = table.find_all('tr')
        # İlk satır başlık olsa bile, biz kendi başlıklarımızı kullanacağız.
        # Bu yüzden ilk satırı atlamıyoruz, çünkü içinde veri olabilir.
        # Sizin verdiğiniz tabloda id, Sperma, belgeno... şeklinde başlık satırı yok, doğrudan veri başlıyor gibi.
        
        parsed_data = []

        for i, row in enumerate(rows):
            cells = row.find_all(['td', 'th']) # Hem td hem th'leri al
            texts = [cell.get_text(strip=True) for cell in cells]

            # --- Kullanıcının orijinal kodundaki kolon normalizasyon mantığı ---
            if len(texts) == 9:
                texts[1] = texts[1] + " | " + texts[2]
                del texts[2]
            elif len(texts) == 7:
                texts.insert(2, '') # belgeno_dummy için boş ekle
            elif len(texts) < expected_cols_after_normalization:
                texts += [''] * (expected_cols_after_normalization - len(texts))
            elif len(texts) > expected_cols_after_normalization:
                texts = texts[:expected_cols_after_normalization]
            # --- Normalizasyon sonu ---

            # Dictionary'e dönüştürme
            # COLUMN_HEADERS listesindeki her bir başlık için corresponding text value'yu al
            # Eğer texts ve COLUMN_HEADERS boyutları uyuşmuyorsa IndexError almamak için min(len(texts), len(COLUMN_HEADERS))
            row_dict = {}
            for j in range(min(len(texts), len(COLUMN_HEADERS))):
                row_dict[COLUMN_HEADERS[j]] = texts[j]
            
            # Sperma_Belgeno sütununu ayırma (eğer format buysa)
            # Eğer 'Sperma | Belgeno' şeklinde geliyorsa ayır.
            if 'Sperma_Belgeno' in row_dict:
                sperma_belgeno_combined = row_dict['Sperma_Belgeno']
                if ' | ' in sperma_belgeno_combined:
                    parts = sperma_belgeno_combined.split(' | ', 1) # Sadece ilk ' | ' kısmından ayır
                    row_dict['Sperma'] = parts[0].strip()
                    row_dict['belgeno'] = parts[1].strip() # Bu, aslında belgeno_dummy'nin yerine geçiyor olabilir.
                else:
                    row_dict['Sperma'] = sperma_belgeno_combined.strip()
                    row_dict['belgeno'] = '' # Boş bırak
                del row_dict['Sperma_Belgeno'] # Birleşmiş olanı sil
                
            # Eğer COLUMN_HEADERS'da olmayan bir 'belgeno_dummy' varsa onu da sil
            if 'belgeno_dummy' in row_dict:
                del row_dict['belgeno_dummy']


            parsed_data.append(row_dict)
            
        # İlk satırın başlıklar olup olmadığını kontrol edip atlayabiliriz
        # Sizin verinizde ilk satır doğrudan data olduğu için atlamadık.
        # Eğer tablonun ilk satırı gerçekten başlık ise:
        # if parsed_data and parsed_data[0]['id'].lower() == 'id': # Basit bir kontrol
        #     parsed_data = parsed_data[1:]

        return parsed_data

    except requests.exceptions.RequestException as e:
        print(f"Web sayfasından veri çekerken bağlantı/istek hatası oluştu: {e}")
        return []
    except ValueError as e:
        print(f"Scraping sırasında değer hatası: {e}")
        return []
    except Exception as e:
        print(f"Scraping sırasında beklenmeyen bir hata oluştu: {e}")
        return []
