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
        from kivymd.app import MDApp # Import MDApp locally for open_date_picker
        app = MDApp.get_running_app()

        layout = BoxLayout(orientation='horizontal', size_hint_y=None, height="40dp", padding="5dp")
        label = Label(text=f"{key}:", size_hint_x=0.4, halign="left", valign="middle")
        label.bind(size=label.setter('text_size')) # Ensure text wraps if needed

        text_input = MDTextField(
            text=str(value),
            size_hint_x=0.6,
            mode="rectangle"
        )

        # Apply date picker for specific date fields
        if key in ['dogum_tarihi', 'son_tohumlama']: # Add other date fields as needed
            text_input.bind(focus=lambda instance, focus: app.open_date_picker(instance) if focus else None)
        
        # Assign a unique ID to each text_input for retrieval
        text_input.id = f"editable_field_{key}" 
        
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
            for child in self.ids.animal_details_list.children:
                if isinstance(child, BoxLayout):
                    # Find the MDTextField within the BoxLayout
                    for grand_child in child.children:
                        if isinstance(grand_child, MDTextField):
                            # Extract key from its ID (e.g., "editable_field_dogum_tarihi")
                            key = grand_child.id.replace("editable_field_", "")
                            value = grand_child.text
                            updated_animal[key] = value
                            break # Found the text field, move to next BoxLayout
            try:
                # Use the app's sync_manager
                if app.sync_manager:
                    await app.sync_manager.update_animal(self.animal_uuid, updated_animal)
                    show_success("Değişiklikler kaydedildi.")
                    self.edit_mode = False
                    self.ids.edit_button.text = "Düzenle"
                    # Refresh animal data and repopulate list to reflect changes
                    # This implies re-fetching from local/synced data
                    await app.root.get_screen('home')._load_animal_data() # Reload all animals
                    self.set_animal_data(next((a for a in app.root.get_screen('home')._all_animals if a.get('uuid') == self.animal_uuid), updated_animal))
                else:
                    show_error("Sync manager not initialized. Please log in.")
            except Exception as e:
                show_error(f"Değişiklikler kaydedilirken hata oluştu: {e}")
        else:
            self.toggle_edit_mode()

    # on_kv_post method removed, button is defined in KV now

