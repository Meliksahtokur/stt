from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from ui.screens.home_screen import HomeScreen
from ui.screens.animal_details import AnimalDetailsScreen # Import the new screen
from src.main import get_all_animal_data

class WindowManager(ScreenManager):
    pass

class AnimalTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"
        Builder.load_file('ui/screens/home_screen.kv')
        Builder.load_file('ui/screens/animal_details.kv') # Load the new screen's kv file
        return WindowManager()

if __name__ == '__main__':
    AnimalTrackerApp().run()
