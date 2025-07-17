# Deta Space üzerinde çalışacak FastAPI uygulaması

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import io
import base64
from datetime import datetime, date
from collections import defaultdict
import logging

# Bilimsel kütüphaneleri burada import ediyoruz
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Supabase istemcisi için gerekli importlar
from supabase import create_client, Client

# Ortam değişkenlerinden Supabase bilgilerini al
# Deta Micro ortamında bunlar otomatik yüklenecektir
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
DETA_API_KEY_AUTH = os.environ.get("DETA_API_KEY_AUTH") # API anahtarı doğrulaması için

# Logger ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Supabase istemcisini başlat
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

app = FastAPI(
    title="Animal Tracker Statistics API",
    description="Hayvan takip uygulaması için istatistik ve grafik oluşturma servisi",
    version="0.1.0",
)

# API Anahtarı doğrulama Middleware'i
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
        return await call_next(request) # Swagger/OpenAPI dokümanlarına izin ver

    api_key = request.headers.get("X-API-Key")
    if not DETA_API_KEY_AUTH or api_key == DETA_API_KEY_AUTH:
        response = await call_next(request)
        return response
    raise HTTPException(status_code=401, detail="Yetkilendirme başarısız: Geçersiz API Anahtarı")

# Veri modelleri
class InseminationData(BaseModel):
    tohumlama_tarihi: Optional[str] # Frontend'den ISO format string olarak gelecek

class AnimalData(BaseModel):
    uuid: str
    isletme_kupesi: Optional[str]
    devlet_kupesi: Optional[str]
    tasma_no: Optional[str]
    irk: Optional[str]
    sinif: Optional[str]
    dogum_tarihi: Optional[str] # Frontend'den ISO format string olarak gelecek
    tohumlamalar: List[InseminationData] # Frontend'den ISO format string olarak gelecek
    son_tohumlama: Optional[str] # Frontend'den ISO format string olarak gelecek
    gebelik_durumu_metin: Optional[str]

class AnimalsPayload(BaseModel):
    animals: List[AnimalData]

class ChartDataPayload(BaseModel):
    data: Dict[str, Any]
    title: str
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None

# --- Yardımcı Fonksiyonlar (src/statistics.py'den taşındı) ---
# DİKKAT: datetime objeleri API'den string olarak geleceği için işleme mantığı güncellendi

def _parse_date_from_str(date_str: Optional[str]) -> Optional[datetime]:
    if isinstance(date_str, str):
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')) # Zulu time handling
        except ValueError:
            return None
    return None

def _classify_animal(insemination_dates_str: List[str]) -> str:
    """Tohumlama geçmişine göre hayvanı 'İnek' veya 'Düve' olarak sınıflandırır."""
    insem_dates_dt = [_parse_date_from_str(d) for d in insemination_dates_str if d]
    insem_dates_dt = [d for d in insem_dates_dt if d is not None] # Sadece geçerli tarihleri al

    if not insem_dates_dt:
        return "Bilinmiyor"
    if len(insem_dates_dt) <= 1:
        return "Düve"
    sorted_dates = sorted(insem_dates_dt)
    for i in range(len(sorted_dates) - 1):
        if (sorted_dates[i + 1] - sorted_dates[i]).days > 180:
            return "İnek"
    return "Düve"

def _calculate_statistics_internal(animals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Hayvanlar hakkında çeşitli istatistikleri hesaplar."""
    if not animals:
        return {}

    total_animals = len(animals)
    cow_count = sum(1 for animal in animals if animal.get('sinif') == 'İnek')
    heifer_count = sum(1 for animal in animals if animal.get('sinif') == 'Düve')
    
    total_inseminations = sum(len(animal.get('tohumlamalar', [])) for animal in animals)
    average_inseminations = total_inseminations / total_animals if total_animals else 0

    valid_ages_days = []
    for animal in animals:
        birth_date_str = animal.get('dogum_tarihi')
        birth_date_dt = _parse_date_from_str(birth_date_str)
        if birth_date_dt:
            valid_ages_days.append((date.today() - birth_date_dt.date()).days)
    
    average_age_days = np.mean(valid_ages_days) if valid_ages_days else 0
    average_age_years = round(average_age_days / 365.25, 1)

    return {
        "toplam_hayvan_sayisi": total_animals,
        "inek_sayisi": cow_count,
        "duve_sayisi": heifer_count,
        "ortalama_tohumlama_sayisi": round(average_inseminations, 1),
        "ortalama_yas_gun": round(average_age_days, 1),
        "ortalama_yas_yil": average_age_years,
    }

def _calculate_breed_distribution_internal(animals: List[Dict[str, Any]]) -> Dict[str, int]:
    """Irk dağılımını hesaplar."""
    breed_counts = defaultdict(int)
    for animal in animals:
        breed = animal.get('irk', 'Bilinmiyor')
        breed_counts[breed] += 1
    return dict(breed_counts)

def _generate_pie_chart_base64_internal(data: Dict[str, int], title: str) -> Optional[str]:
    """Pasta grafiği oluşturur ve base64 string olarak döndürür."""
    if not data or not any(data.values()): # Check if data is empty or all values are zero
        logging.warning(f"No valid data to generate pie chart for {title}.")
        return None

    labels = data.keys()
    sizes = data.values()

    fig1, ax1 = plt.subplots(figsize=(6, 6))
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
    ax1.axis('equal')
    ax1.set_title(title)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig1)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def _calculate_births_per_month_internal(animals: List[Dict[str, Any]]) -> Dict[str, int]:
    """Hayvanların doğum tarihlerine göre aylık doğum sayılarını hesaplar."""
    births_per_month = defaultdict(int)
    for animal in animals:
        birth_date_str = animal.get('dogum_tarihi')
        birth_date_dt = _parse_date_from_str(birth_date_str)
        if birth_date_dt:
            month_year_key = birth_date_dt.strftime('%Y-%m')
            births_per_month[month_year_key] += 1
    
    sorted_births = dict(sorted(births_per_month.items()))
    return sorted_births

def _generate_bar_chart_base64_internal(data: Dict[str, int], title: str, xlabel: str, ylabel: str) -> Optional[str]:
    """Çubuk grafiği oluşturur ve base64 string olarak döndürür."""
    if not data or not any(data.values()): # Check if data is empty or all values are zero
        logging.warning(f"No valid data to generate bar chart for {title}.")
        return None

    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color='skyblue')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def _get_animal_specific_stats_internal(animal_uuid: str, all_processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Belirli bir hayvan için özel istatistikleri döndürür."""
    animal_record = next((animal for animal in all_processed_data if animal.get('uuid') == animal_uuid), None)

    if not animal_record:
        return {"hata": "Hayvan bulunamadı."}

    total_inseminations = len(animal_record.get('tohumlamalar', []))
    
    # son_tohumlama'nın string formatında geldiğini ve gerekirse parse edilmesi gerektiğini unutmayın
    last_insemination_str = animal_record.get('son_tohumlama')
    last_insemination_dt = _parse_date_from_str(last_insemination_str)
    
    pregnancy_status = animal_record.get('gebelik_durumu_metin', 'Bilinmiyor')

    birth_date_str = animal_record.get('dogum_tarihi')
    birth_date_formatted = birth_date_str if birth_date_str and _parse_date_from_str(birth_date_str) else "Bilgi Yok"

    animal_stats = {
        "toplam_tohumlama_sayisi": total_inseminations,
        "sinif_tahmini": animal_record.get('sinif', 'Bilgi Yok'),
        "son_tohumlama": last_insemination_dt.isoformat() if last_insemination_dt else "Bilgi Yok",
        "mevcut_gebelik_durumu": pregnancy_status,
        "dogum_tarihi": birth_date_formatted
    }
    return animal_stats

# --- API Endpoints ---

@app.post("/statistics")
async def get_statistics_api(payload: AnimalsPayload):
    logging.info(f"Received request for /statistics with {len(payload.animals)} animals.")
    # pydantic modeli doğrudan dict'e çevir
    animals_as_dict = [animal.dict() for animal in payload.animals]
    
    # Backend'de Supabase'den çekme, bu API'nin görevi istatistikleri hesaplamak.
    # Eğer mobil uygulama zaten tüm hayvan verisini gönderiyorsa, tekrar Supabase'den çekmeye gerek yok.
    # Ancak Supabase entegrasyonu, eğer veriyi doğrudan API'den çekeceksek burada olmalı.
    
    # Şu anki akış: Mobil uygulama işlenmiş veriyi gönderiyor.
    # Eğer bu veriyi direkt Supabase'den çekeceksek:
    # try:
    #     response = supabase.table('animals').select('*').eq('user_id', <user_id>).execute()
    #     animals_from_db = response.data
    #     # Burada animals_from_db'yi data_processor'dan geçirmemiz gerekebilir
    #     # veya data_processor mantığını da API'ye taşımamız gerekebilir.
    # except Exception as e:
    #     logging.error(f"Supabase'den hayvan verisi çekilemedi: {e}")
    #     raise HTTPException(status_code=500, detail="Hayvan verisi çekilemedi.")

    general_stats = _calculate_statistics_internal(animals_as_dict)
    breed_dist = _calculate_breed_distribution_internal(animals_as_dict)
    births_data = _calculate_births_per_month_internal(animals_as_dict)

    pie_chart_base64 = _generate_pie_chart_base64_internal(breed_dist, "Hayvan Irk Dağılımı")
    bar_chart_base64 = _generate_bar_chart_base64_internal(births_data, "Aylara Göre Doğum Sayısı", "Ay-Yıl", "Doğum Sayısı")

    return {
        "statistics": general_stats,
        "breed_distribution": breed_dist,
        "births_per_month": births_data,
        "pie_chart_base64": pie_chart_base64,
        "bar_chart_base64": bar_chart_base64
    }

@app.post("/animal_stats/{animal_uuid}")
async def get_animal_statistics_api(animal_uuid: str, payload: AnimalsPayload):
    logging.info(f"Received request for /animal_stats/{animal_uuid} with {len(payload.animals)} animals.")
    animals_as_dict = [animal.dict() for animal in payload.animals]
    animal_stats = _get_animal_specific_stats_internal(animal_uuid, animals_as_dict)
    return {"animal_stats": animal_stats}

@app.post("/charts/pie")
async def generate_pie_chart_api(payload: ChartDataPayload):
    logging.info(f"Received request for /charts/pie with title: {payload.title}")
    chart_base64 = _generate_pie_chart_base64_internal(payload.data, payload.title)
    if chart_base64:
        return {"chart_base64": chart_base64}
    raise HTTPException(status_code=400, detail="Pasta grafiği oluşturulamadı, veri geçersiz olabilir.")

@app.post("/charts/bar")
async def generate_bar_chart_api(payload: ChartDataPayload):
    logging.info(f"Received request for /charts/bar with title: {payload.title}")
    chart_base64 = _generate_bar_chart_base64_internal(payload.data, payload.title, payload.xlabel, payload.ylabel)
    if chart_base64:
        return {"chart_base64": chart_base64}
    raise HTTPException(status_code=400, detail="Çubuk grafiği oluşturulamadı, veri geçersiz olabilir.")

@app.get("/")
def read_root():
    return {"message": "Animal Tracker Statistics API is running!"}
