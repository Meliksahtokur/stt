# src/statistics.py
import requests
import json
from datetime import datetime # Import datetime
from typing import List, Dict, Any, Optional
import os
from config.secrets import DETA_API_BASE_URL, DETA_API_KEY # Yeni Deta API bilgileri

# NOT: Bu dosyadaki orijinal istatistik hesaplama ve grafik oluşturma mantığı
# artık Deta Space backend'inde yer almaktadır. Mobil uygulama sadece bu API'leri çağıracaktır.

class StatisticsAPIError(Exception):
    """İstatistik API çağrısı sırasında oluşan hatalar için özel istisna sınıfı."""
    pass

def _call_deta_api(endpoint: str, method: str = 'GET', data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Deta Space'teki istatistik API'lerini çağırır."""
    url = f"{DETA_API_BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": DETA_API_KEY # Deta API anahtarı
    }
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            raise StatisticsAPIError(f"Desteklenmeyen HTTP metodu: {method}")

        response.raise_for_status() # HTTP hata kodları için hata fırlat
        return response.json()
    except requests.exceptions.Timeout:
        raise StatisticsAPIError(f"API isteği zaman aşımına uğradı: {url}")
    except requests.exceptions.ConnectionError:
        raise StatisticsAPIError(f"API'ye bağlanırken ağ hatası oluştu: {url}. İnternet bağlantınızı veya Deta API durumunu kontrol edin.")
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_detail = e.response.text
        raise StatisticsAPIError(f"API hatası ({status_code}): {error_detail}")
    except json.JSONDecodeError:
        raise StatisticsAPIError("API'den geçersiz JSON yanıtı alındı.")
    except Exception as e:
        raise StatisticsAPIError(f"API çağrısı sırasında beklenmedik hata: {e}")

def calculate_statistics(processed_animals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """İstatistikleri hesaplamak için Deta API'yi çağırır."""
    try:
        # Deta API'ye işlenmiş hayvan verilerini göndererek istatistikleri al
        # Not: processed_animals içindeki datetime objeleri JSON'a çevrilmeli.
        # Bu işlem burada veya API'de yapılabilir. Basitlik için burada yapalım.
        serializable_animals = []
        for animal in processed_animals:
            serializable_animal = animal.copy()
            for key, value in serializable_animal.items():
                if isinstance(value, datetime):
                    serializable_animal[key] = value.isoformat()
                elif isinstance(value, list): # Tohumlamalar gibi listelerdeki datetime'ları da çevir
                    processed_list_items = []
                    for item in value:
                        if isinstance(item, dict):
                            processed_item = item.copy()
                            for k, v in processed_item.items():
                                if isinstance(v, datetime):
                                    processed_item[k] = v.isoformat()
                            processed_list_items.append(processed_item)
                        else:
                            processed_list_items.append(item)
                    serializable_animal[key] = processed_list_items
            serializable_animals.append(serializable_animal)


        response_data = _call_deta_api("/statistics", method='POST', data={"animals": serializable_animals})
        return response_data.get("statistics", {})
    except StatisticsAPIError as e:
        print(f"İstatistik API hatası: {e}")
        return {"hata": str(e)}
    except Exception as e:
        print(f"Beklenmedik istatistik hesaplama hatası: {e}")
        return {"hata": str(e)}

def calculate_breed_distribution(animals: List[Dict[str, Any]]) -> Dict[str, int]:
    # Bu fonksiyon hala lokalde kullanılabilir veya API'ye taşınabilir.
    # Şimdilik, sadece API'ye taşıma kararını istatistik ve grafik için uyguluyoruz.
    # Ancak istatistik hesaplama API'si bunu da kapsadığı için, bu fonksiyonu API'den alacağız.
    raise NotImplementedError("Irk dağılımı hesaplaması artık Deta API üzerinden yapılmaktadır.")

def generate_pie_chart_base64(data: Dict[str, int], title: str) -> Optional[str]:
    """Pasta grafiğini oluşturmak için Deta API'yi çağırır."""
    try:
        response_data = _call_deta_api("/charts/pie", method='POST', data={"data": data, "title": title})
        return response_data.get("chart_base64")
    except StatisticsAPIError as e:
        print(f"Pasta grafiği API hatası: {e}")
        return None
    except Exception as e:
        print(f"Beklenmedik pasta grafiği hatası: {e}")
        return None

def calculate_births_per_month(animals: List[Dict[str, Any]]) -> Dict[str, int]:
    # Bu fonksiyon da artık API'den gelecek istatistiklerin bir parçasıdır.
    raise NotImplementedError("Aylık doğum sayısı hesaplaması artık Deta API üzerinden yapılmaktadır.")

def generate_bar_chart_base64(data: Dict[str, int], title: str, xlabel: str, ylabel: str) -> Optional[str]:
    """Çubuk grafiği oluşturmak için Deta API'yi çağırır."""
    try:
        response_data = _call_deta_api("/charts/bar", method='POST', data={"data": data, "title": title, "xlabel": xlabel, "ylabel": ylabel})
        return response_data.get("chart_base64")
    except StatisticsAPIError as e:
        print(f"Çubuk grafiği API hatası: {e}")
        return None
    except Exception as e:
        print(f"Beklenmedik çubuk grafiği hatası: {e}")
        return None

def get_animal_specific_stats(animal_uuid: str, all_processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Hayvan özel istatistiklerini almak için Deta API'yi çağırır."""
    try:
        serializable_animals = []
        for animal in all_processed_data:
            serializable_animal = animal.copy()
            for key, value in serializable_animal.items():
                if isinstance(value, datetime):
                    serializable_animal[key] = value.isoformat()
                elif isinstance(value, list): # Tohumlamalar gibi listelerdeki datetime'ları da çevir
                    processed_list_items = []
                    for item in value:
                        if isinstance(item, dict):
                            processed_item = item.copy()
                            for k, v in processed_item.items():
                                if isinstance(v, datetime):
                                    processed_item[k] = v.isoformat()
                            processed_list_items.append(processed_item)
                        else:
                            processed_list_items.append(item)
                    serializable_animal[key] = processed_list_items
            serializable_animals.append(serializable_animal)
            
        response_data = _call_deta_api(f"/animal_stats/{animal_uuid}", method='POST', data={"animals": serializable_animals})
        return response_data.get("animal_stats", {"hata": "Hayvan bulunamadı."})
    except StatisticsAPIError as e:
        print(f"Hayvan özel istatistikleri API hatası: {e}")
        return {"hata": str(e)}
    except Exception as e:
        print(f"Beklenmedik hayvan özel istatistik hatası: {e}")
        return {"hata": str(e)}

