from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty
from kivymd.uix.list import OneLineListItem
from src.statistics import calculate_statistics, get_animal_specific_stats
from src.persistence import load_animals


class StatisticsScreen(MDScreen):
    statistics_list = ObjectProperty(None)

    def on_enter(self):
        self.update_statistics()

    def update_statistics(self):
        try:
            all_animals = load_animals()
            general_stats = calculate_statistics(all_animals)
            self.populate_general_stats(general_stats)
        except Exception as e:
            print(f"İstatistikler yüklenirken hata oluştu: {e}")
            # Hata durumunda kullanıcıya bildirim gösterilebilir.

    def populate_general_stats(self, stats):
        if self.statistics_list:
            self.statistics_list.clear_widgets()
            for key, value in stats.items():
                self.statistics_list.add_widget(OneLineListItem(text=f"{key}: {value}"))

