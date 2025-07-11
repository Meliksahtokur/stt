from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from src.main import get_all_animal_data # Example backend API call

# Load your .kv files here (one for each screen)
Builder.load_file("kivy_app/screens/login.kv")
Builder.load_file("kivy_app/screens/animal_list.kv")


class LoginScreen(Screen):
    pass

class AnimalListScreen(Screen):
    def on_enter(self):
        animals = get_all_animal_data() # Call your backend API
        # Update the RecycleView with the animal data
        pass


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AnimalListScreen(name='animal_list'))
        return sm

if __name__ == '__main__':
    MyApp().run()
