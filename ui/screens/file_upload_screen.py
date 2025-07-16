import asyncio
import os
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty
from plyer import filechooser
from src.data_loader import load_data_from_file
from src.scraper import fetch_and_parse_table, ScraperError
from src.data_processor import process_animal_records
from ui.utils.dialogs import show_error, show_success

class FileUploadScreen(MDScreen):
    file_path_input = ObjectProperty(None)
    web_url_input = ObjectProperty(None)
    status_label = ObjectProperty(None)

    def on_enter(self):
        # Clear previous status and inputs when entering the screen
        self.status_label.text = ""
        self.file_path_input.text = ""
        self.web_url_input.text = ""

    def select_local_file(self):
        try:
            # Open file chooser for CSV or Excel files
            path = filechooser.open_file(filters=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xls", "*.xlsx")
            ])
            if path:
                self.file_path_input.text = path[0] # plyer returns a list
                self.status_label.text = f"Seçilen dosya: {os.path.basename(path[0])}"
            else:
                self.status_label.text = "Dosya seçimi iptal edildi."
        except Exception as e:
            show_error(f"Dosya seçicide hata: {e}")
            self.status_label.text = f"Dosya seçicide hata: {e}"

    def process_data_input(self):
        file_path = self.file_path_input.text
        web_url = self.web_url_input.text

        if file_path and web_url:
            show_error("Lütfen sadece bir kaynak seçin (yerel dosya veya web URL'si).")
            self.status_label.text = "Sadece bir kaynak seçin."
            return
        elif file_path:
            asyncio.create_task(self._process_local_file(file_path))
        elif web_url:
            asyncio.create_task(self._process_web_url(web_url))
        else:
            show_error("Lütfen bir dosya seçin veya bir web URL'si girin.")
            self.status_label.text = "Kaynak seçilmedi."

    async def _process_local_file(self, file_path):
        self.status_label.text = "Yerel dosya yükleniyor..."
        try:
            raw_data = load_data_from_file(file_path)
            await self._process_and_sync_data(raw_data, "yerel dosya")
        except Exception as e:
            show_error(f"Yerel dosya işlenirken hata oluştu: {e}")
            self.status_label.text = f"Hata: {e}"

    async def _process_web_url(self, url):
        self.status_label.text = "Web sayfasından veri kazınıyor..."
        try:
            raw_data = fetch_and_parse_table(url)
            await self._process_and_sync_data(raw_data, "web kazıma")
        except ScraperError as e:
            show_error(f"Web kazıma hatası: {e}")
            self.status_label.text = f"Web kazıma hatası: {e}"
        except Exception as e:
            show_error(f"Web verileri işlenirken beklenmedik hata: {e}")
            self.status_label.text = f"Hata: {e}"

    async def _process_and_sync_data(self, raw_data, source_type):
        app = MDApp.get_running_app()
        if not app.sync_manager:
            show_error("Senkronizasyon yöneticisi başlatılamadı. Lütfen giriş yapın.")
            self.status_label.text = "Senkronizasyon yöneticisi yok."
            return

        if not raw_data:
            show_success(f"{source_type} kaynağından yüklenecek veri bulunamadı.")
            self.status_label.text = "Veri bulunamadı."
            return

        self.status_label.text = f"{len(raw_data)} kayıt işleniyor ve senkronize ediliyor..."
        try:
            # Process data (e.g., classify, format dates)
            processed_data = process_animal_records(raw_data)
            
            # Send each processed record to sync_manager
            successful_uploads = 0
            for animal in processed_data:
                try:
                    await app.sync_manager.create_animal(animal)
                    successful_uploads += 1
                except Exception as e:
                    print(f"Bireysel hayvan kaydı senkronizasyonunda hata ({animal.get('isletme_kupesi', 'N/A')}): {e}")
                    # Log individual failures but try to continue

            if successful_uploads > 0:
                show_success(f"{successful_uploads} hayvan kaydı başarıyla yüklendi ve senkronizasyon kuyruğuna eklendi.")
                self.status_label.text = f"Başarıyla yüklendi: {successful_uploads} kayıt."
            else:
                show_error(f"Hiçbir hayvan kaydı yüklenemedi. Detaylar için konsolu kontrol edin.")
                self.status_label.text = "Yükleme başarısız oldu."
            self.reset_inputs()
            # Optionally refresh home screen data after upload
            app.root.get_screen('home').load_animal_data()

        except Exception as e:
            show_error(f"Veri işleme veya senkronizasyon sırasında hata oluştu: {e}")
            self.status_label.text = f"Hata: {e}"

    def reset_inputs(self):
        self.file_path_input.text = ""
        self.web_url_input.text = ""
        self.status_label.text = ""
import asyncio
import os
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty
from plyer import filechooser
from src.data_loader import load_data_from_file
from src.scraper import fetch_and_parse_table, ScraperError
from src.data_processor import process_animal_records
from ui.utils.dialogs import show_error, show_success

class FileUploadScreen(MDScreen):
    file_path_input = ObjectProperty(None)
    web_url_input = ObjectProperty(None)
    status_label = ObjectProperty(None)

    def on_enter(self):
        # Clear previous status and inputs when entering the screen
        self.status_label.text = ""
        self.file_path_input.text = ""
        self.web_url_input.text = ""

    def select_local_file(self):
        try:
            # Open file chooser for CSV or Excel files
            path = filechooser.open_file(filters=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xls", "*.xlsx")
            ])
            if path:
                self.file_path_input.text = path[0] # plyer returns a list
                self.status_label.text = f"Seçilen dosya: {os.path.basename(path[0])}"
            else:
                self.status_label.text = "Dosya seçimi iptal edildi."
        except Exception as e:
            show_error(f"Dosya seçicide hata: {e}")
            self.status_label.text = f"Dosya seçicide hata: {e}"

    def process_data_input(self):
        file_path = self.file_path_input.text
        web_url = self.web_url_input.text

        if file_path and web_url:
            show_error("Lütfen sadece bir kaynak seçin (yerel dosya veya web URL'si).")
            self.status_label.text = "Sadece bir kaynak seçin."
            return
        elif file_path:
            asyncio.create_task(self._process_local_file(file_path))
        elif web_url:
            asyncio.create_task(self._process_web_url(web_url))
        else:
            show_error("Lütfen bir dosya seçin veya bir web URL'si girin.")
            self.status_label.text = "Kaynak seçilmedi."

    async def _process_local_file(self, file_path):
        self.status_label.text = "Yerel dosya yükleniyor..."
        try:
            raw_data = load_data_from_file(file_path)
            await self._process_and_sync_data(raw_data, "yerel dosya")
        except Exception as e:
            show_error(f"Yerel dosya işlenirken hata oluştu: {e}")
            self.status_label.text = f"Hata: {e}"

    async def _process_web_url(self, url):
        self.status_label.text = "Web sayfasından veri kazınıyor..."
        try:
            raw_data = fetch_and_parse_table(url)
            await self._process_and_sync_data(raw_data, "web kazıma")
        except ScraperError as e:
            show_error(f"Web kazıma hatası: {e}")
            self.status_label.text = f"Web kazıma hatası: {e}"
        except Exception as e:
            show_error(f"Web verileri işlenirken beklenmedik hata: {e}")
            self.status_label.text = f"Hata: {e}"

    async def _process_and_sync_data(self, raw_data, source_type):
        app = MDApp.get_running_app()
        if not app.sync_manager:
            show_error("Senkronizasyon yöneticisi başlatılamadı. Lütfen giriş yapın.")
            self.status_label.text = "Senkronizasyon yöneticisi yok."
            return

        if not raw_data:
            show_success(f"{source_type} kaynağından yüklenecek veri bulunamadı.")
            self.status_label.text = "Veri bulunamadı."
            return

        self.status_label.text = f"{len(raw_data)} kayıt işleniyor ve senkronize ediliyor..."
        try:
            # Process data (e.g., classify, format dates)
            processed_data = process_animal_records(raw_data)
            
            # Send each processed record to sync_manager
            successful_uploads = 0
            for animal in processed_data:
                try:
                    await app.sync_manager.create_animal(animal)
                    successful_uploads += 1
                except Exception as e:
                    print(f"Bireysel hayvan kaydı senkronizasyonunda hata ({animal.get('isletme_kupesi', 'N/A')}): {e}")
                    # Log individual failures but try to continue

            if successful_uploads > 0:
                show_success(f"{successful_uploads} hayvan kaydı başarıyla yüklendi ve senkronizasyon kuyruğuna eklendi.")
                self.status_label.text = f"Başarıyla yüklendi: {successful_uploads} kayıt."
            else:
                show_error(f"Hiçbir hayvan kaydı yüklenemedi. Detaylar için konsolu kontrol edin.")
                self.status_label.text = "Yükleme başarısız oldu."
            self.reset_inputs()
            # Optionally refresh home screen data after upload
            app.root.get_screen('home').load_animal_data()

        except Exception as e:
            show_error(f"Veri işleme veya senkronizasyon sırasında hata oluştu: {e}")
            self.status_label.text = f"Hata: {e}"

    def reset_inputs(self):
        self.file_path_input.text = ""
        self.web_url_input.text = ""
        self.status_label.text = ""
