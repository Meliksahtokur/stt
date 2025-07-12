from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from src.persistence import save_animals, load_animals
import uuid

class AddAnimalScreen(MDScreen):
    isletme_kupesi_field = ObjectProperty(None)
    devlet_kupesi_field = ObjectProperty(None)
    tasma_no_field = ObjectProperty(None)
    irk_field = ObjectProperty(None)
    dialog = None

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

        try:
            animals = load_animals() or []
            animals.append(new_animal)
            save_animals(animals)
            self.show_success_dialog("Hayvan başarıyla kaydedildi.")
            self.reset_fields()
        except Exception as e:
            self.show_error_dialog(f"Hayvan kaydedilirken hata oluştu: {e}")
            print(f"An unexpected error occurred: {e}") #For debugging purposes

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

