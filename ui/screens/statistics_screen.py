import asyncio # Import asyncio
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.scrollview import ScrollView # Added for explicit import
from kivymd.uix.list import OneLineListItem
from src.statistics import (
    calculate_statistics, # Şimdi API çağrısı
    generate_pie_chart_base64, # Şimdi API çağrısı
    generate_bar_chart_base64, # Şimdi API çağrısı
    get_animal_specific_stats, # Şimdi API çağrısı
    StatisticsAPIError # Yeni hata sınıfı
)
from src.persistence import load_animals # Hala lokal veri için kullanılıyor
from ui.utils.dialogs import show_error # Import centralized dialogs
from src.data_processor import process_animal_records # Hayvanları API'ye göndermeden önce işlemek için

class StatisticsScreen(MDScreen):
    statistics_list = ObjectProperty(None)
    # Properties to hold chart images as base64 strings
    breed_pie_chart_src = StringProperty("data:image/png;base64,") # Default empty
    births_bar_chart_src = StringProperty("data:image/png;base64,") # Default empty

    def on_enter(self):
        asyncio.create_task(self._update_statistics_async())

    async def _update_statistics_async(self):
        try:
            # It's better to fetch animals from sync_manager or get_all_animal_data
            # for consistency with offline-first approach, but for now using load_animals
            # as it was previously done and doesn't require complex app/sync_manager access.
            all_animals = load_animals()
            all_animals = load_animals()
            if not all_animals:
                show_error("Henüz hiç hayvan verisi yok. Lütfen hayvan ekleyin.")
                self.populate_general_stats({}) # Clear existing stats
                self.breed_pie_chart_src = ""
                self.births_bar_chart_src = ""
                return

            # Hayvan verilerini API'ye göndermeden önce işlemeliyiz (datetime'ları ISO formatına çevirmek gibi)
            # Normalde load_animals'tan gelen veri zaten API'ye uygun olmalı veya API tarafında işlenmeli.
            # Ancak process_animal_records fonksiyonu datetime objelerine çevirdiği için,
            # API'ye göndermeden önce tekrar string'e çevirmek veya API'de bu dönüşümleri yönetmek gerekir.
            # src/statistics.py içindeki _call_deta_api zaten datetime objelerini JSON'a çeviriyor.
            # Bu nedenle doğrudan 'all_animals' gönderebiliriz. Ancak emin olmak için processed formunu kullanmak daha güvenli.
            processed_animals = process_animal_records(all_animals) # Bu, lokalde zaten yapılıyor
            
            # Tüm istatistikleri ve grafik bilgilerini tek API çağrısıyla alalım
            api_response = await calculate_statistics(processed_animals) # Bu artık tek bir API çağrısı

            if "hata" in api_response:
                show_error(f"İstatistik API hatası: {api_response['hata']}")
                self.populate_general_stats({})
                self.breed_pie_chart_src = ""
                self.births_bar_chart_src = ""
                return

            general_stats = api_response.get("statistics", {})
            self.populate_general_stats(general_stats)

            # Grafik kaynaklarını API yanıtından doğrudan al
            pie_chart_base64 = api_response.get("pie_chart_base64")
            if pie_chart_base64:
                self.breed_pie_chart_src = f"data:image/png;base64,{pie_chart_base64}"
            else:
                self.breed_pie_chart_src = ""

            bar_chart_base64 = api_response.get("bar_chart_base64")
            if bar_chart_base64:
                self.births_bar_chart_src = f"data:image/png;base64,{bar_chart_base64}"
            else:
                self.births_bar_chart_src = ""

        except StatisticsAPIError as e:
            print(f"İstatistik API hatası (ekran): {e}")
            show_error(f"İstatistikler yüklenirken API hatası: {e}")
            self.populate_general_stats({})
            self.breed_pie_chart_src = ""
            self.births_bar_chart_src = ""
        except Exception as e:
            print(f"İstatistikler yüklenirken beklenmedik hata (ekran): {e}")
            show_error(f"İstatistikler yüklenirken beklenmedik bir hata oluştu: {e}")
            self.populate_general_stats({})
            self.breed_pie_chart_src = ""
            self.births_bar_chart_src = ""

    def populate_general_stats(self, stats):
        # Clear previous items
        self.ids.statistics_list.clear_widgets()
        # Add a header for general statistics
        self.ids.statistics_list.add_widget(OneLineListItem(text="Genel İstatistikler", font_style="H6", text_color=[0, 0.5, 0.5, 1]))
        
        # Populate with general stats
        for key, value in stats.items():
            display_text = ""
            if key == "toplam_hayvan_sayisi": display_text = f"Toplam Hayvan Sayısı: {value}"
            elif key == "inek_sayisi": display_text = f"İnek Sayısı: {value}"
            elif key == "duve_sayisi": display_text = f"Düve Sayısı: {value}"
            elif key == "ortalama_tohumlama_sayisi": display_text = f"Ortalama Tohumlama Sayısı: {value}"
            elif key == "ortalama_yas_gun": display_text = f"Ortalama Yaş (Gün): {value}"
            elif key == "ortalama_yas_yil": display_text = f"Ortalama Yaş (Yıl): {value}"
            else: display_text = f"{key}: {value}" # Fallback for unknown keys
            
            self.ids.statistics_list.add_widget(OneLineListItem(text=display_text))

