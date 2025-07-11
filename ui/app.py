from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from ui.screens.home_screen import HomeScreen
from ui.screens.animal_details import AnimalDetailsScreen
from ui.screens.add_animal import AddAnimalScreen
from ui.screens.statistics_screen import StatisticsScreen # Import statistics screen
from src.main import get_all_animal_data

class WindowManager(ScreenManager):
    pass

class AnimalTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"
        Builder.load_file('ui/screens/home_screen.kv')
        Builder.load_file('ui/screens/animal_details.kv')
        Builder.load_file('ui/screens/add_animal.kv')
        Builder.load_file('ui/screens/statistics_screen.kv') # Load statistics screen kv file
        return WindowManager()

if __name__ == '__main__':
    AnimalTrackerApp().run()
