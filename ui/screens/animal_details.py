from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.list import OneLineListItem


class AnimalDetailsScreen(MDScreen):
    animal_data = ObjectProperty(None)
    animal_uuid = StringProperty("")

    def set_animal_data(self, animal_data):
        self.animal_data = animal_data
        self.animal_uuid = animal_data.get('uuid', '')
        self.ids.animal_details_list.clear_widgets()
        for key, value in animal_data.items():
            if key != 'uuid' and key != 'tohumlamalar':
                self.ids.animal_details_list.add_widget(OneLineListItem(text=f"{key}: {value}"))
        # Handle inseminations separately
        if animal_data.get('tohumlamalar'):
            for insemination in animal_data['tohumlamalar']:
                self.ids.animal_details_list.add_widget(OneLineListItem(text=f"Tohumlama Tarihi: {insemination.get('tohumlama_tarihi', 'N/A')}"))

