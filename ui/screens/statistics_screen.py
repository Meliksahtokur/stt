import asyncio # Import asyncio
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.scrollview import ScrollView # Added for explicit import
from kivymd.uix.list import OneLineListItem
from src.statistics import calculate_statistics, get_animal_specific_stats, \
                           calculate_breed_distribution, generate_pie_chart_base64, \
                           calculate_births_per_month, generate_bar_chart_base64
from src.persistence import load_animals
from ui.utils.dialogs import show_error # Import centralized dialogs

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
            if not all_animals:
                show_error("Henüz hiç hayvan verisi yok. Lütfen hayvan ekleyin.")
                self.populate_general_stats({}) # Clear existing stats
                self.breed_pie_chart_src = ""
                self.births_bar_chart_src = ""
                return

            # General Statistics
            general_stats = calculate_statistics(all_animals)
            self.populate_general_stats(general_stats)

            # Breed Distribution Chart
            breed_dist = calculate_breed_distribution(all_animals)
            pie_chart_base64 = generate_pie_chart_base64(breed_dist, "Hayvan Irk Dağılımı")
            if pie_chart_base64:
                self.breed_pie_chart_src = f"data:image/png;base64,{pie_chart_base64}"
            else:
                self.breed_pie_chart_src = "" # Clear if no data

            # Births per Month Chart
            births_data = calculate_births_per_month(all_animals)
            bar_chart_base64 = generate_bar_chart_base64(births_data, "Aylara Göre Doğum Sayısı", "Ay-Yıl", "Doğum Sayısı")
            if bar_chart_base64:
                self.births_bar_chart_src = f"data:image/png;base64,{bar_chart_base64}"
            else:
                self.births_bar_chart_src = "" # Clear if no data

        except Exception as e:
            print(f"İstatistikler yüklenirken hata oluştu: {e}")
            show_error(f"İstatistikler yüklenirken bir hata oluştu: {e}")
            self.populate_general_stats({}) # Clear existing stats on error
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

