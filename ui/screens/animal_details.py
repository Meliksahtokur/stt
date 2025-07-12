from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label # Import Label
from kivymd.uix.textfield import MDTextField # Import MDTextField
from src.persistence import save_animals, load_animals
from src.sync_manager import SyncManager
import asyncio

class AnimalDetailsScreen(MDScreen):
    animal_data = ObjectProperty(None)
    animal_uuid = StringProperty("")
    edit_mode = BooleanProperty(False)
    dialog = ObjectProperty(None)
    sync_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sync_manager = SyncManager()

    def set_animal_data(self, animal_data):
        self.animal_data = animal_data
        self.animal_uuid = animal_data.get('uuid', '')
        self.ids.animal_details_list.clear_widgets()
        self.populate_list()

    def populate_list(self):
        for key, value in self.animal_data.items():
            if key != 'uuid' and key != 'tohumlamalar':
                if self.edit_mode:
                    item = self.create_editable_item(key, value)
                else:
                    item = OneLineListItem(text=f"{key}: {value}")
                self.ids.animal_details_list.add_widget(item)
        # Handle inseminations separately
        if self.animal_data.get('tohumlamalar'):
            for insemination in self.animal_data['tohumlamalar']:
                self.ids.animal_details_list.add_widget(OneLineListItem(text=f"Tohumlama Tarihi: {insemination.get('tohumlama_tarihi', 'N/A')}"))

    def create_editable_item(self, key, value):
        layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        label = Label(text=f"{key}:", size_hint_x=0.3)
        text_input = MDTextField(text=str(value), size_hint_x=0.7)
        layout.add_widget(label)
        layout.add_widget(text_input)
        return layout

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.ids.edit_button.text = "Kaydet" if self.edit_mode else "Düzenle"
        self.populate_list()

    async def save_changes(self):
        if self.edit_mode:
            updated_animal = self.animal_data.copy()
            for i in range(0, self.ids.animal_details_list.children.__len__()):
                if isinstance(self.ids.animal_details_list.children[i], BoxLayout):
                    key = self.ids.animal_details_list.children[i].children[0].text.replace(":", "")
                    value = self.ids.animal_details_list.children[i].children[1].text
                    updated_animal[key] = value
            try:
                await self.sync_manager.update_animal(self.animal_uuid, updated_animal)
                self.show_success_dialog("Değişiklikler kaydedildi.")
                self.edit_mode = False
                self.ids.edit_button.text = "Düzenle"
                self.populate_list()
            except Exception as e:
                self.show_error_dialog(f"Değişiklikler kaydedilirken hata oluştu: {e}")
        else:
            self.toggle_edit_mode()

    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Hata",
                text=message,
                buttons=[MDFlatButton(text="Tamam", on_release=lambda x: self.dialog.dismiss())],
            )
        self.dialog.text = message
        self.dialog.open()

    def show_success_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Başarılı",
                text=message,
                buttons=[MDFlatButton(text="Tamam", on_release=lambda x: self.dialog.dismiss())],
            )
        self.dialog.text = message
        self.dialog.open()

    def on_kv_post(self, base_widget):
        self.ids.edit_button = MDRaisedButton(text="Düzenle", on_press=lambda x: asyncio.run(self.save_changes()), size_hint_y=None, height=40)
        self.ids.animal_details_list.add_widget(self.ids.edit_button)

