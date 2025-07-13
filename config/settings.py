import os
from dotenv import load_dotenv
load_dotenv() # .env dosyasındaki değişkenleri yükler
# config/settings.py

DATA_SOURCE_URL = 'http://vethek.org/t_2_7867_NDcyNQ.htm'
LOCAL_DATA_FILE = 'data/animal_records.json'
SYNC_QUEUE_FILE = 'data/sync_queue.json' # New: File to store pending sync actions
GESTATATION_PERIOD_DAYS = 285

# Sütun başlıkları ve indeksleri (scrape edilen tablonun yapısına göre ayarlandı)
# Bu sıralama ve isimler, scraperdan gelen 'texts' listesindeki pozisyona göre olmalı
COLUMN_HEADERS = [
    'id', 'Sperma_Belgeno', 'belgeno_dummy', 'kupeno', 'irki', 'Not', 'tarih', 'Gebe_mi'
]
# Not: Sizin kodunuzda index 1 ve 2 birleştirilip index 2 silindiği için
# 'Sperma | Belgeno' şeklinde tek bir sütun olarak işliyoruz.
# 'belgeno_dummy' buradaki boşluk veya birleşmiş alanın orijinal belgeno karşılığıdır.
# Bu durumda, scrape edilen veriden sonra 'Sperma' ve 'belgeno'yu ayırmamız gerekecek.
