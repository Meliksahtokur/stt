# src/data_loader.py

"""
Bu modül, çeşitli dosya formatlarından (CSV, Excel, JSON) hayvan verilerini
yüklemekten sorumludur. Dosya tipini otomatik olarak tanır ve veriyi
projenin geri kalanının anlayacağı standart bir formata (sözlük listesi) dönüştürür.
"""

import os
import json
from typing import List, Dict, Any

try:
    import pandas as pd
except ImportError:
    pd = None # Pandas yüklü değilse None olarak ayarla

class DataLoaderError(Exception):
    """Dosya yükleme işlemleri sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

def _load_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """Bir Excel dosyasından veri yükler."""
    if not pd:
        raise DataLoaderError("Excel dosyalarını işlemek için 'pandas' kütüphanesi gereklidir. Lütfen 'pip install pandas openpyxl' ile kurun.")
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        # Sütun adlarını küçük harfe çevirip boşlukları alt çizgi ile değiştirelim
        df.columns = [str(col).lower().replace(' ', '_') for col in df.columns]
        return df.to_dict('records')
    except Exception as e:
        raise DataLoaderError(f"Excel dosyası okunurken hata oluştu: {e}") from e

def _load_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """Bir CSV dosyasından veri yükler."""
    if not pd:
        raise DataLoaderError("CSV dosyalarını işlemek için 'pandas' kütüphanesi gereklidir. Lütfen 'pip install pandas' ile kurun.")
    try:
        df = pd.read_csv(file_path)
        df.columns = [str(col).lower().replace(' ', '_') for col in df.columns]
        return df.to_dict('records')
    except Exception as e:
        raise DataLoaderError(f"CSV dosyası okunurken hata oluştu: {e}") from e

def _load_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Bir JSON dosyasından veri yükler."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise DataLoaderError("JSON dosyası bir liste içermelidir.")
        return data
    except json.JSONDecodeError as e:
        raise DataLoaderError(f"JSON dosyası bozuk veya geçersiz formatta: {e}") from e
    except Exception as e:
        raise DataLoaderError(f"JSON dosyası okunurken hata oluştu: {e}") from e

def load_data_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Dosya uzantısına göre uygun yükleyiciyi seçer ve veriyi yükler.

    Args:
        file_path: Yüklenecek dosyanın yolu.

    Returns:
        Dosyadan okunan ve standart formata getirilmiş veri.
    
    Raises:
        DataLoaderError: Dosya tipi desteklenmiyorsa veya okuma sırasında hata oluşursa.
    """
    if not os.path.exists(file_path):
        raise DataLoaderError(f"Dosya bulunamadı: {file_path}")

    _, file_extension = os.path.splitext(file_path.lower())

    if file_extension in ['.xlsx', '.xls']:
        return _load_from_excel(file_path)
    elif file_extension == '.csv':
        return _load_from_csv(file_path)
    elif file_extension == '.json':
        return _load_from_json(file_path)
    elif file_extension == '.txt':
        # TXT dosyaları için CSV okuyucuyu deneyebiliriz, genellikle çalışır.
        print("UYARI: TXT dosyası CSV olarak okunmaya çalışılıyor.")
        return _load_from_csv(file_path)
    else:
        raise DataLoaderError(f"Desteklenmeyen dosya tipi: {file_extension}")
