from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from src.persistence import save_animals, load_animals
import uuid
from src.sync_manager import SyncManager
import asyncio

class AddAnimalScreen(MDScreen):
    isletme_kupesi_field = ObjectProperty(None)
    devlet_kupesi_field = ObjectProperty(None)
    tasma_no_field = ObjectProperty(None)
    irk_field = ObjectProperty(None)
    dialog = None
    sync_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sync_manager = SyncManager()

    def save_animal(self):
        isletme_kupesi = self.isletme_kupesi_field.text
        devlet_kupesi = self.devlet_kupesi_field.text
        tasma_no = self.tasma_no_field.text
        irk = self.irk_field.text

        if not isletme_kupesi:
            self.show_error_dialog("İşletme küpesi alanı boş bırakılamaz.")
            return

        new_animal = {
            'uuid': str(uuid.uuid4()),
            'isletme_kupesi': isletme_kupesi,
            'devlet_kupesi': devlet_kupesi,
            'tasma_no': tasma_no,
            'irk': irk,
            'tohumlamalar': []
        }

        asyncio.run(self._save_animal(new_animal))

    async def _save_animal(self, new_animal):
        try:
            await self.sync_manager.create_animal(new_animal)
            self.show_success_dialog("Hayvan başarıyla kaydedildi.")
            self.reset_fields()
        except Exception as e:
            self.show_error_dialog(f"Hayvan kaydedilirken hata oluştu: {e}")

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

    def show_success_dialog(self, message):
        self.show_dialog("Başarılı", message)

    def reset_fields(self):
        self.isletme_kupesi_field.text = ""
        self.devlet_kupesi_field.text = ""
        self.tasma_no_field.text = ""
        self.irk_field.text = ""

