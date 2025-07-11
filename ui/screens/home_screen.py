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


class AnimalItem(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    isletme_kupesi = StringProperty("")
    sinif = StringProperty("")
    devlet_kupesi = StringProperty("")
    # Add other properties as needed

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.isletme_kupesi = data.get('isletme_kupesi', 'N/A')
        self.sinif = data.get('sinif', 'N/A')
        self.devlet_kupesi = data.get('devlet_kupesi', 'N/A')
        # Update other properties
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    pass


class HomeScreen(MDScreen):
    animal_list = ObjectProperty(None)
    dialog = None

    def on_enter(self):
        self.load_animal_data()

    def load_animal_data(self):
        try:
            animals = get_all_animal_data()
            self.update_animal_list(animals)
        except Exception as e:
            self.show_error_dialog(f"Hayvan verileri yüklenirken hata oluştu: {e}")

    def update_animal_list(self, animals):
        if self.animal_list:
            self.animal_list.data = [{
                'isletme_kupesi': animal.get('isletme_kupesi', 'N/A'),
                'sinif': animal.get('sinif', 'N/A'),
                'devlet_kupesi': animal.get('devlet_kupesi', 'N/A'),
                # Add other data fields here
                'selectable': True
            } for animal in animals]

    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Hata",
                text=message,
                buttons=[
                    MDFlatButton(text="Tamam", on_release=lambda x: self.dialog.dismiss())
                ],
            )
        self.dialog.text = message
        self.dialog.open()

