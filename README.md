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
    *   `statistics.py`: Hayvan istatistiklerini hesaplar ve Matplotlib kullanarak grafikler oluşturur. **NOT:** Bu modüldeki ağır hesaplamalar ve grafik oluşturma (`numpy`, `pandas`, `matplotlib` gerektiren) mobil uygulamanın dışına taşınmıştır (bkz: "Mimari Kararlar ve Zorluklar" bölümü).
    *   `utils.py`: Yardımcı fonksiyonları (örn: tarih ayrıştırma, güvenli dönüşüm) içerir.
    *   `data_service.py`: `get_all_animal_data` gibi veri çekme/senkronizasyon mantığını barındıran modül.
*   `ui/`: KivyMD kullanıcı arayüzü ile ilgili dosyaları içerir:
    *   `screens/`: Uygulamanın farklı ekranları için Python (.py) ve Kivy (.kv) dosyaları bulunur. (örn: `login_screen`, `home_screen`, `add_animal`, `animal_details`, `statistics_screen`, `file_upload_screen`).
    *   `utils/`: UI'ya özgü yardımcı araçlar (örn: `dialogs.py` - Snackbar bildirimleri için).
*   `config/`: Uygulama yapılandırma dosyaları (örn: `settings.py`, `secrets.py`).
*   `tests/`: Proje için yazılmış birim testleri.
*   `requirements.txt`: Projenin tüm Python bağımlılıklarını listeler. **NOT:** Mobil derleme zorlukları nedeniyle `numpy`, `pandas`, `matplotlib` gibi kütüphaneler buradan kaldırılmış veya GitHub Actions'da özel olarak ele alınmıştır (bkz: "Mimari Kararlar ve Zorluklar" bölümü).
*   `buildozer.spec`: Buildozer aracının Android ve iOS paketlemesi için kullandığı yapılandırma dosyası.
*   `.github/workflows/`: GitHub Actions CI/CD iş akışlarını (`android-build.yml` gibi) içerir. Bu, projenin ARM64 mobil APK'sını otomatik olarak derlemek için kullanılır.
*   `apply_fixes.py`: Projede belirli dosyaları güncellemek için kullanılan yardımcı bir Python betiği (sadece geliştirme ortamı için).

## Mimari Kararlar ve Zorluklar

Bu projenin geliştirme sürecinde, özellikle mobil platform (ARM64) için derleme sırasında önemli mimari kararlar alınmış ve zorluklarla karşılaşılmıştır.

### 1. Bilimsel Kütüphaneler ve Mobil Derleme Zorlukları

*   **Problem:** Uygulamanın istatistik ve veri işleme (örneğin grafik oluşturma, karmaşık analizler) işlevleri `numpy`, `pandas` ve `matplotlib` gibi güçlü Python bilimsel kütüphanelerine bağımlıdır. Ancak bu kütüphaneler, C/Fortran tabanlı native uzantılara sahip oldukları için Python-for-Android (p4a) kullanılarak mobil (ARM64) uygulamalara doğrudan derlenmeleri **son derece zordur ve genellikle build hatalarına yol açar.** Bu, uygulamanın çalışması için bu kütüphanelerin "şart" olduğu ancak mobil ortamda doğrudan paketlenemediği bir çelişki oluşturmuştur.
*   **Çözüm:** Bu derleme engellerini aşmak ve mobil uygulamanın boyutunu/performansını optimize etmek amacıyla, `numpy`, `pandas`, `matplotlib` kullanan **tüm ağır hesaplama ve grafik oluşturma mantığı mobil uygulamadan ayrılmış ve bir Bulut Fonksiyonuna taşınmıştır.**
*   **Seçilen Servis:** Bu Bulut Fonksiyonları için **AWS Lambda** servisi tercih edilmiştir. AWS Lambda, mevcut Python kodunun en az değişiklikle taşınmasına izin vermesi ve bireysel kullanım için oldukça cömert bir ücretsiz katman sunması nedeniyle "0 maliyet" hedefimizle uyumludur.

### 2. Uygulama Mimarisi (Mobil + Bulut Entegrasyonu)

Bu mimari kararının bir sonucu olarak, uygulamanın yapısı aşağıdaki gibi evrilmiştir:

*   **Mobil Uygulama (Frontend):**
    *   `numpy`, `pandas`, `matplotlib` kütüphanelerini doğrudan içermez.
    *   Kullanıcı arayüzünü (KivyMD), temel hayvan kayıtlarını (CRUD işlemleri), Supabase ile kimlik doğrulama ve veri senkronizasyonunu yönetir.
    *   Ağır istatistik ve grafik analizleri gerektiğinde, verileri Supabase üzerinden veya doğrudan **AWS Lambda fonksiyonlarına gönderir ve işlenmiş sonuçları (örneğin base64 kodlu grafik görüntüleri) geri alır.**
    *   `requirements.txt` ve `buildozer.spec` artık bu ağır bilimsel kütüphaneleri doğrudan `requirements` listesinde içermez (gerektiğinde, Lambda ortamında bulunurlar), bu da derleme sürecini çok daha kararlı hale getirir.
*   **AWS Lambda Fonksiyonları (Backend/Compute):**
    *   `numpy`, `pandas`, `matplotlib` gibi kütüphanelerin yüklü olduğu ayrı Python ortamlarında çalışır.
    *   Mobil uygulamadan gelen analiz isteklerini işler, Supabase veritabanından ilgili veriyi çeker, gerekli hesaplamaları ve grafik oluşturmayı yapar.
    *   Sonuçları (görsel veya ham veri) mobil uygulamaya bir API yanıtı olarak geri döner.
    *   AWS Lambda'nın ücretsiz katmanı sayesinde, bireysel veya düşük hacimli kullanımda bu hesaplamaların maliyeti sıfırda kalır.

### 3. "0 Maliyet" Hedefi

*   Bu mimari, `numpy`, `pandas`, `matplotlib` gibi kütüphanelerin maliyetli veya imkansız mobil derlemesini önleyerek projenin "0 maliyet" hedefini destekler.
*   Hem Supabase'in (veritabanı, kimlik doğrulama, temel depolama) hem de AWS Lambda'nın (ağır hesaplama gücü) ücretsiz katmanları birleştirilerek, projenin bireysel kullanımda uzun süre maliyetsiz kalması (kullanım hacmi arttıkça küçük maliyetler oluşabileceği unutulmamalıdır) hedeflenmiştir.

Bu değişiklikler, uygulamanın performansını artırırken, mobil derleme sorunlarını çözmek ve projenin uzun vadeli sürdürülebilirliğini sağlamak için stratejik öneme sahiptir.
