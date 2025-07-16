# Hayvan Takip ve Gebelik Bildirim Sistemi

Bu proje, büyükbaş hayvanların takibini, yönetimini ve gebelik süreçlerinin izlenmesini kolaylaştırmak amacıyla geliştirilmiş bir mobil uygulamadır. KivyMD kullanıcı arayüzü çerçevesini kullanarak kullanıcı dostu bir deneyim sunar ve Supabase ile bulut senkronizasyonu ile çevrimdışı çalışma yeteneklerini birleştirir.

## Ana Özellikler

*   **Esnek Veri Girişi:** Yerel CSV/Excel dosyalarından veya belirlenen web sayfalarından (HTML tablo içeren) hayvan kayıtlarını kolayca içe aktarma.
*   **Hayvan Yönetimi:** Hayvan kayıtlarını ekleme, listeleme, detaylarını görüntüleme ve düzenleme.
*   **Gebelik Takibi:** Tohumlama bilgilerinin girilmesi ve otomatik gebelik durumu takibi (285 gün üzerinden).
*   **İstatistiksel Analiz:** Hayvan ırk dağılımı ve aylık doğum sayıları gibi önemli istatistiklerin görselleştirilmesi.
*   **Çevrimdışı Uyumlu Senkronizasyon:** Lokal ve uzaktaki (Supabase) veriler arasında otomatik senkronizasyon, çevrimdışı öncelikli çalışma.
*   **Gelişmiş Kullanıcı Deneyimi:** Tarih girişi için kolay tarih seçiciler (`MDDatePicker`) ve işlem sonuçları için bilgilendirici `Snackbar` bildirimleri.

## Kurulum

Bu proje özellikle ARM64 mimarisi için GitHub Actions (CI/CD) üzerinde derlenmek üzere tasarlanmıştır. Lokal geliştirme ortamınızı kurmak ve bağımlılıkları yönetmek için aşağıdaki adımları izleyebilirsiniz:

1.  **Projeyi Klonlayın:**
    Proje GitHub üzerinde barındırıldığından, öncelikle depoyu klonlayarak başlayın:
    ```bash
    git clone https://github.com/Meliksahtokur/stt.git
    cd stt # veya projenizin ana dizini
    ```

2.  **Lokal Geliştirme Ortamını Kurun (Opsiyonel):**
    Eğer lokalde geliştirme veya test yapmak isterseniz, Python bağımlılıklarını kurmak için aşağıdaki adımları izleyin. (Bu adım, ARM64 için GitHub Actions derlemesini etkilemez.)

    a) **Otomatik Kurulum (Önerilen):**
    Ana dizinde (bu README dosyasının bulunduğu yer) aşağıdaki tek komutu çalıştırabilirsiniz:
    ```bash
    bash setup.sh
    ```
    Bu komut, gerekli klasörleri oluşturacak, Python sanal ortamını hazırlayacak ve tüm bağımlılıkları yükleyecektir.

    b) **Manuel Bağımlılık Yükleme:**
    Eğer `setup.sh` kullanmazsanız veya bir sorun yaşarsanız, proje ana dizininde bir sanal ortam oluşturup (örn: `python3 -m venv myenv`) aktifleştirdikten sonra aşağıdaki komutu çalıştırın:
    ```bash
    pip install -r requirements.txt
    ```
    Android/iOS için **GitHub Actions dışında** derleme yapacaksanız, `buildozer`'ı da kurmanız ve yapılandırmanız gerekebilir. Ancak projenin birincil derleme yöntemi GitHub Actions üzerindendir.

## Kullanım

1.  **Supabase Ayarları:**
    `config/secrets.py` dosyasında Supabase URL'nizi ve Anahtarınızı (`SUPABASE_URL`, `SUPABASE_KEY`) doğru şekilde yapılandırdığınızdan emin olun.

2.  **Uygulamayı Çalıştırın:**
    Proje ana dizininde terminali açın ve aşağıdaki komutu çalıştırın:
    ```bash
    python main.py
    ```
    Uygulama başlayacak ve giriş ekranını gösterecektir.

3.  **Veri Girişi:**
    *   **Manuel Giriş:** Uygulama içindeki "Ekle" (+) butonu aracılığıyla tek tek hayvan kaydı girebilirsiniz. Tarih alanları için `MDDatePicker` kullanılmaktadır.
    *   **Toplu Veri İçe Aktarımı:** Ana ekrandaki "Yükle" (upload icon) butonu ile "Veri Yükle / Web Kazı" ekranına gidin.
        *   **Yerel Dosyadan:** Bilgisayarınızdan CSV veya Excel dosyası seçerek toplu veri yükleyebilirsiniz.
        *   **Web Sayfasından:** HTML tablo içeren bir web sitesi URL'si girerek verileri doğrudan web'den kazıyabilirsiniz.
        Yükleme/kazıma işlemi tamamlandıktan sonra veriler otomatik olarak işlenir ve Supabase ile senkronize edilmek üzere kuyruğa eklenir.

4.  **Hayvan Listeleme ve Detayları:**
    Ana ekranda tüm hayvanları listeleyebilir, arama çubuğunu kullanarak filtreleyebilirsiniz. Bir hayvana dokunarak detay ekranına gidebilir, bilgileri düzenleyebilir ve kaydedebilirsiniz.

5.  **İstatistikler:**
    İstatistikler ekranı, hayvan ırk dağılımı ve aylık doğum sayıları gibi genel istatistikleri grafiklerle görselleştirir.

## Klasör Yapısı

*   `main.py`: Kivy uygulamasının ana giriş noktası. Uygulama yaşam döngüsünü ve ekran yönetimini kontrol eder.
*   `src/`: Uygulamanın çekirdek mantığını içeren Python modülleri:
    *   `auth_manager.py`: Supabase ile kullanıcı kimlik doğrulama işlemlerini yönetir.
    *   `sync_manager.py`: Lokal ve uzaktaki (Supabase) hayvan verileri arasındaki senkronizasyonu sağlar.
    *   `permissions_manager.py`: Kullanıcı yetkilerini ve denetim kaydı işlemlerini yönetir (şu anda yer tutucu).
    *   `data_processor.py`: Ham hayvan verilerini işler, zenginleştirir (örn: sınıflandırma, görünen ad, tarih dönüşümleri).
    *   `persistence.py`: Hayvan verilerini ve senkronizasyon kuyruğunu yerel JSON dosyalarına kaydetme ve yükleme işlemlerini yürütür.
    *   `scraper.py`: Harici bir web sitesinden tablo verilerini çeker ve ayrıştırır.
    *   `data_loader.py`: Yerel dosyalardan (CSV/Excel) veri yükleme mantığını içerir.
    *   `statistics.py`: Hayvan istatistiklerini hesaplar ve Matplotlib kullanarak grafikler oluşturur.
    *   `utils.py`: Yardımcı fonksiyonları (örn: tarih ayrıştırma, güvenli dönüşüm) içerir.
    *   `data_service.py`: `get_all_animal_data` gibi veri çekme/senkronizasyon mantığını barındıran modül.
*   `ui/`: KivyMD kullanıcı arayüzü ile ilgili dosyaları içerir:
    *   `screens/`: Uygulamanın farklı ekranları için Python (.py) ve Kivy (.kv) dosyaları bulunur. (örn: `login_screen`, `home_screen`, `add_animal`, `animal_details`, `statistics_screen`, `file_upload_screen`).
    *   `utils/`: UI'ya özgü yardımcı araçlar (örn: `dialogs.py` - Snackbar bildirimleri için).
*   `config/`: Uygulama yapılandırma dosyaları (örn: `settings.py`, `secrets.py`).
*   `tests/`: Proje için yazılmış birim testleri.
*   `requirements.txt`: Projenin tüm Python bağımlılıklarını listeler.
*   `buildozer.spec`: Buildozer aracının Android ve iOS paketlemesi için kullandığı yapılandırma dosyası.
*   `apply_fixes.py`: Projede belirli dosyaları güncellemek için kullanılan yardımcı bir Python betiği (sadece geliştirme ortamı için).
