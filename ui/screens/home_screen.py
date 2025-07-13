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
from kivymd.uix.list import OneLineAvatarIconListItem # Changed to OneLineAvatarIconListItem for consistency
# from kivymd.uix.dialog import MDDialog # Removed, using centralized dialogs
# from kivymd.uix.button import MDFlatButton # Removed, using centralized dialogs
from kivy.clock import Clock
from src.main import get_all_animal_data
from src.data_processor import get_display_name
from ui.utils.dialogs import show_error, show_success # Import centralized dialogs


# Changed AnimalItem to inherit from OneLineAvatarIconListItem as used in KV
class AnimalItem(RecycleDataViewBehavior, OneLineAvatarIconListItem):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    data = ObjectProperty(None) # Holds the full animal data dictionary

    # Properties to be set from data for display in KV
    isletme_kupesi = StringProperty("")
    sinif = StringProperty("")
    devlet_kupesi = StringProperty("") # Explicitly define if used in KV
    gebelik_durumu_metin = StringProperty("") # Explicitly define
    display_name = StringProperty("") # Explicitly define

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.data = data['data'] # Store the full animal data
        # Set individual properties for display
        self.isletme_kupesi = data.get('isletme_kupesi', 'N/A')
        self.sinif = data.get('sinif', 'N/A')
        self.devlet_kupesi = data.get('devlet_kupesi', 'N/A')
        self.gebelik_durumu_metin = data.get('gebelik_durumu_metin', 'Bilinmiyor')
        self.display_name = data.get('display_name', 'Bilinmeyen Hayvan')
        self.text = f"{self.display_name} - {self.sinif}" # Update text based on display_name and sinif
        self.secondary_text = f"Küpe: {self.isletme_kupesi}" if self.isletme_kupesi else "" # Secondary info

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
        # KivyMD list items handle their own selection background colors,
        # but you can override if needed. For now, removing direct color change.
        # if value:
        #     self.background_color = (0.5, 0.5, 0.5, 1)
        # else:
        #     self.background_color = (1, 1, 1, 1)
        pass # KivyMD handles selection visuals


class HomeScreen(MDScreen):
    _all_animals = [] # Cache the full list of animals for filtering
    # dialog = None # Removed, using centralized dialogs

    def on_enter(self):
        Clock.schedule_once(self.load_animal_data)

    def load_animal_data(self, dt=0): # Added dt=0 for Clock.schedule_once
        asyncio.create_task(self._load_animal_data())

    async def _load_animal_data(self):
        try:
            animals = await get_all_animal_data()
            self._all_animals = animals # Cache the full list
            self.populate_list(self._all_animals) # Populate initially with all data
        except Exception as e:
            print(f"Error loading animal data: {e}")  # Log the error for debugging
            show_error("Veri çekilemedi, lütfen internet bağlantınızı kontrol edin.")

    def populate_list(self, animals):
        if self.ids.animal_list:
            # Ensure 'devlet_kupesi' and 'gebelik_durumu_metin' are handled
            self.ids.animal_list.data = [{
                'isletme_kupesi': animal.get('isletme_kupesi', 'N/A'),
                'sinif': animal.get('sinif', 'N/A'),
                'devlet_kupesi': animal.get('devlet_kupesi', 'N/A'), # Ensure this key is passed
                'gebelik_durumu_metin': animal.get('gebelik_durumu_metin', 'Bilinmiyor'),
                'display_name': get_display_name(animal),
                'data': animal, # Pass the full animal data
            } for animal in animals]

    def filter_list(self, search_text=""):
        search_text = search_text.lower()
        if not search_text:
            filtered_animals = self._all_animals
        else:
            filtered_animals = [
                animal for animal in self._all_animals
                if search_text in get_display_name(animal).lower() or \
                   search_text in animal.get('isletme_kupesi', '').lower() or \
                   search_text in animal.get('devlet_kupesi', '').lower()
            ]
        self.populate_list(filtered_animals)

    # Removed show_dialog and show_error_dialog as they are centralized in ui/utils/dialogs.py

