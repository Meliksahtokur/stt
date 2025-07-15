from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class AnimalTrackerApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(
            text='Hayvan Takip Sistemi',
            size_hint_y=None,
            height=50,
            font_size='20sp'
        )
        
        start_button = Button(
            text='Sistemi Başlat',
            size_hint_y=None,
            height=50
        )
        start_button.bind(on_press=self.start_system)
        
        layout.add_widget(title)
        layout.add_widget(start_button)
        
        return layout
    
    def start_system(self, instance):
        print("Sistem başlatıldı!")

if __name__ == '__main__':
    AnimalTrackerApp().run()
