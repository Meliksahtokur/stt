from kivymd.uix.screen import MDScreen
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import ObjectProperty, BooleanProperty # Added import
from kivy.uix.recycleview.layout import LayoutSelectionBehavior # Added import
from src.main import get_all_animal_data


class AnimalItem(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the selection changes '''
        self.index = index
        return super(AnimalItem, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(AnimalItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Add selection support to the RecycleBoxLayout '''
    pass


class HomeScreen(MDScreen):
    animal_list = ObjectProperty(None)

    def on_enter(self):
        animals = get_all_animal_data()
        self.update_animal_list(animals)

    def update_animal_list(self, animals):
        if self.animal_list:
            self.animal_list.data = [{'text': f"{animal.get('isletme_kupesi', 'N/A')} - {animal.get('sinif', 'N/A')}", 'selectable': True} for animal in animals]

