# src/statistics.py

"""
Bu modül, işlenmiş hayvan verilerinden kapsamlı istatistikler üretir.
Sürü genelindeki verimlilik, bireysel hayvan performansı ve boğa (sperma)
başarı oranları gibi kritik metrikleri hesaplar.
"""

from collections import defaultdict
from typing import List, Dict, Any, Tuple

def calculate_statistics(processed_animals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tüm istatistikleri hesaplayan ana fonksiyondur.

    Args:
        processed_animals: Data processor'dan gelen, zenginleştirilmiş hayvan listesi.

    Returns:
        Tüm istatistikleri içeren kapsamlı bir sözlük.
    """
    if not processed_animals:
        return {} # Veri yoksa boş sözlük döndür

    # --- Genel Sürü İstatistikleri ---
    total_animals = len(processed_animals)
    cow_count = sum(1 for animal in processed_animals if animal.get('sinif') == 'İnek')
    heifer_count = sum(1 for animal in processed_animals if animal.get('sinif') == 'Düve')
    pregnant_count = sum(1 for animal in processed_animals if "GEBE" in animal.get('gebelik_durumu_metin', ''))

    # --- Boğa (Sperma) Başarı Oranları ---
    bull_stats = defaultdict(lambda: {'success': 0, 'total': 0})
    for animal in processed_animals:
        # Not: Bu hesaplama, her bir hayvanın en son kaydını baz alır.
        # Daha detaylı bir analiz için tüm tohumlama geçmişi gerekebilir.
        # Şimdilik en son tohumlamanın gebelikle sonuçlanıp sonuçlanmadığına bakıyoruz.
        sperma = animal.get('Sperma')
        if sperma:
            bull_stats[sperma]['total'] += 1
            if "GEBE" in animal.get('gebelik_durumu_metin', ''):
                bull_stats[sperma]['success'] += 1
    
    bull_success_rates = {
        sperma: {
            **stats,
            'rate': (stats['success'] / stats['total']) * 100 if stats['total'] > 0 else 0
        }
        for sperma, stats in bull_stats.items()
    }
    # Başarı oranına göre sırala
    sorted_bulls = sorted(bull_success_rates.items(), key=lambda item: item[1]['rate'], reverse=True)

    # --- Gebelik İçin Ortalama Tohumlama Sayısı ---
    # Not: Bu metrik, her hayvanın tüm geçmişini gerektirir.
    # `data_processor` artık en son kaydı döndürdüğü için bu mantığı
    # gelecekte `persistence` modülünden tüm geçmişi okuyarak yapmalıyız.
    # Şimdilik bu alanı geçici olarak dolduruyoruz.
    avg_inseminations_for_pregnancy = "Hesaplanmadı (Tüm geçmiş verisi gerekli)"

    # Tüm istatistikleri tek bir raporda topla
    statistics_report = {
        "general_stats": {
            "toplam_hayvan_sayisi": total_animals,
            "inek_sayisi": cow_count,
            "duve_sayisi": heifer_count,
            "gebe_sayisi": pregnant_count,
            "gebelik_orani": (pregnant_count / total_animals) * 100 if total_animals > 0 else 0,
        },
        "bull_success_stats": {
            "raw_data": bull_success_rates,
            "sorted_by_rate": sorted_bulls
        },
        "efficiency_stats": {
            "avg_inseminations_for_pregnancy": avg_inseminations_for_pregnancy
        }
    }

    return statistics_report

def get_animal_specific_stats(animal_id: int, all_processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Belirli bir hayvana ait özel istatistikleri döndürür.

    Args:
        animal_id: İstatistikleri istenen hayvanın ID'si.
        all_processed_data: İşlenmiş tüm hayvanların listesi.

    Returns:
        O hayvana ait istatistikleri içeren bir sözlük.
    """
    animal_record = next((animal for animal in all_processed_data if animal.get('id') == animal_id), None)

    if not animal_record:
        return {"hata": "Hayvan bulunamadı."}

    # Bu veriler `data_processor` tarafından zaten hesaplanmıştı.
    total_inseminations = animal_record.get('tohumlama_gecmisi_sayisi', 'Bilgi Yok')

    # Gelecekte eklenecek diğer istatistikler için yer tutucu
    animal_stats = {
        "toplam_tohumlama_sayisi": total_inseminations,
        "sinif_tahmini": animal_record.get('sinif', 'Bilgi Yok'),
        "son_gebelik_durumu": animal_record.get('gebelik_durumu_metin', 'Bilgi Yok')
    }
    return animal_stats
