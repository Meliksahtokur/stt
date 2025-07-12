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
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from src.main import get_all_animal_data
from src.data_processor import get_display_name


class AnimalItem(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    data = ObjectProperty(None)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(AnimalItem, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(AnimalItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def on_touch_up(self, touch):
        ''' Remove selection on touch up '''
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.deselect_node(self.index)
        return super(AnimalItem, self).on_touch_up(touch)

    def on_selected(self, widget, value):
        ''' Change the background color of the selected item '''
        if value:
            self.background_color = (0.5, 0.5, 0.5, 1)
        else:
            self.background_color = (1, 1, 1, 1)


class HomeScreen(MDScreen):
    animal_list = ObjectProperty(None)
    dialog = None

    def on_enter(self):
        Clock.schedule_once(self.load_animal_data)

    def load_animal_data(self, dt):
        asyncio.create_task(self._load_animal_data())

    async def _load_animal_data(self):
        try:
            animals = await get_all_animal_data()
            self.populate_list(animals)
        except Exception as e:
            print(f"Error loading animal data: {e}")  # Log the error for debugging
            self.show_error_dialog("Veri çekilemedi, lütfen internet bağlantınızı kontrol edin.")

    def populate_list(self, animals):
        if self.animal_list:
            self.animal_list.data = [{
                'isletme_kupesi': animal['isletme_kupesi'],
                'sinif': animal['sinif'],
                'gebelik_durumu_metin': animal.get('gebelik_durumu_metin', 'Bilinmiyor'),
                'display_name': get_display_name(animal),
                'data': animal,
            } for animal in animals]

    def show_dialog(self, title, message, button_text="Tamam"):
        if not self.dialog:
            self.dialog = MDDialog(
                title=title,
                text=message,
                buttons=[MDFlatButton(text=button_text, on_release=lambda x: self.dialog.dismiss())],
            )
        else:
            self.dialog.title = title
            self.dialog.text = message
        self.dialog.open()

    def show_error_dialog(self, message):
        self.show_dialog("Hata", message)

