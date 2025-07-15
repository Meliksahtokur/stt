from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.button import MDRaisedButton # Add this import
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivymd.uix.textfield import MDTextField
import asyncio
from kivymd.app import MDApp # Import MDApp to access global app properties
from ui.utils.dialogs import show_error, show_success # Import the centralized dialog utility

class AnimalDetailsScreen(MDScreen):
    animal_data = ObjectProperty(None)
    animal_uuid = StringProperty("")
    edit_mode = BooleanProperty(False)

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
        app = MDApp.get_running_app()
        # Check for permission before proceeding
        if app.permissions_manager and not app.permissions_manager.can_edit_animal(self.animal_uuid):
            show_error("You do not have permission to edit this animal.")
            return

        if self.edit_mode:
            updated_animal = self.animal_data.copy()
            for i in range(0, self.ids.animal_details_list.children.__len__()):
                if isinstance(self.ids.animal_details_list.children[i], BoxLayout):
                    # Ensure child widgets exist and are accessible
                    if len(self.ids.animal_details_list.children[i].children) >= 2:
                        key_label = self.ids.animal_details_list.children[i].children[0]
                        value_input = self.ids.animal_details_list.children[i].children[1]

                        # Extract key from label (e.g., "key:")
                        key = key_label.text.replace(":", "").strip()
                        value = value_input.text
                        updated_animal[key] = value
            try:
                # Use the app's sync_manager
                if app.sync_manager:
                    await app.sync_manager.update_animal(self.animal_uuid, updated_animal)
                    show_success("Değişiklikler kaydedildi.")
                    self.edit_mode = False
                    self.ids.edit_button.text = "Düzenle"
                    self.populate_list()
                else:
                    show_error("Sync manager not initialized. Please log in.")
            except Exception as e:
                show_error(f"Değişiklikler kaydedilirken hata oluştu: {e}")
        else:
            self.toggle_edit_mode()

    def on_kv_post(self, base_widget):
        self.ids.edit_button = MDRaisedButton(text="Düzenle", on_press=self.save_changes, size_hint_y=None, height=40)
        self.ids.animal_details_list.add_widget(self.ids.edit_button)

