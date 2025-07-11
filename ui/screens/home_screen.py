import asyncio
from kivymd.uix.screen import MDScreen
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from src.main import get_all_animal_data
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock


class AnimalItem(RecycleDataViewBehavior, BoxLayout):
    # ... (rest of AnimalItem class remains the same) ...


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    pass


class HomeScreen(MDScreen):
    animal_list = ObjectProperty(None)
    dialog = None

    def on_enter(self):
        Clock.schedule_once(self.load_animal_data)

    async def load_animal_data(self, dt=None):
        try:
            animals = await get_all_animal_data()
            self.update_animal_list(animals)
        except Exception as e:
            self.show_error_dialog(f"Hayvan verileri yüklenirken hata oluştu: {e}")

    def update_animal_list(self, animals):
        if self.animal_list:
            self.animal_list.data = [{
                'isletme_kupesi': animal.get('isletme_kupesi', 'N/A'),
                'sinif': animal.get('sinif', 'N/A'),
                'devlet_kupesi': animal.get('devlet_kupesi', 'N/A'),
                'selectable': True
            } for animal in animals]

    def show_error_dialog(self, message):
        # ... (rest of show_error_dialog remains the same) ...

