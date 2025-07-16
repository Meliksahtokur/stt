import uuid
import asyncio
from kivymd.app import MDApp # Import MDApp to access global app properties
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty
from ui.utils.dialogs import show_error, show_success # <- ADD

class AddAnimalScreen(MDScreen):
    isletme_kupesi_field = ObjectProperty(None)
    devlet_kupesi_field = ObjectProperty(None)
    tasma_no_field = ObjectProperty(None)
    irk_field = ObjectProperty(None)
    dogum_tarihi_field = ObjectProperty(None) # New ObjectProperty for birth date

    def save_animal(self):
        isletme_kupesi = self.isletme_kupesi_field.text
        devlet_kupesi = self.devlet_kupesi_field.text
        tasma_no = self.tasma_no_field.text
        irk = self.irk_field.text
        dogum_tarihi = self.dogum_tarihi_field.text # Get birth date text

        if not isletme_kupesi:
            show_error("İşletme küpesi alanı boş bırakılamaz.")
            return

        new_animal = {
            'uuid': str(uuid.uuid4()),
            'isletme_kupesi': isletme_kupesi,
            'devlet_kupesi': devlet_kupesi,
            'tasma_no': tasma_no,
            'irk': irk,
            'dogum_tarihi': dogum_tarihi if dogum_tarihi else None, # Add birth date
            'tohumlamalar': []
        }

        # Use app's sync_manager to handle the async call
        app = MDApp.get_running_app()
        if app.sync_manager:
            asyncio.create_task(self._save_animal(app.sync_manager, new_animal))
        else:
            show_error("Sync manager not initialized. Please log in.")


    async def _save_animal(self, sync_manager, new_animal):
        try:
            await sync_manager.create_animal(new_animal)
            show_success("Hayvan başarıyla kaydedildi.")
            self.reset_fields()
        except Exception as e:
            show_error(f"Hayvan kaydedilirken hata oluştu: {e}")

    def reset_fields(self):
        self.isletme_kupesi_field.text = ""
        self.devlet_kupesi_field.text = ""
        self.tasma_no_field.text = ""
        self.irk_field.text = ""
        self.dogum_tarihi_field.text = "" # Reset birth date field
        self.dogum_tarihi_field.text = "" # Reset birth date field

