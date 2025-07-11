from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from ui.screens.home_screen import HomeScreen # Import the home screen
from src.main import get_all_animal_data

class WindowManager(ScreenManager):
    pass

class AnimalTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"
        Builder.load_file('ui/screens/home_screen.kv') # Load only the home screen for now
        return WindowManager()

if __name__ == '__main__':
    AnimalTrackerApp().run()
