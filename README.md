# Hayvan Takip ve Gebelik Bildirim Sistemi

Bu proje, belirlenen bir web sayfasından hayvan kayıtlarını çekmeyi, çekilen verileri işlemeyi, özellikle tohumlama tarihlerine göre beklenen doğum tarihlerini hesaplamayı ve gebelik sürecindeki hayvanlar için kritik dönemlerde bildirimler sağlamayı amaçlayan bir Python uygulamasıdır.

## Kurulum

1.  **Projeyi Klonlayın veya Dosyaları Oluşturun:**
    Bu projenin tamamını otomatik olarak kurmak için, bu README dosyasının bulunduğu ana dizinde aşağıdaki tek komutu çalıştırabilirsiniz:
    ```bash
    bash setup.sh
    ```
    Bu komut, tüm klasörleri ve dosyaları oluşturacak, içlerini dolduracak ve Python bağımlılıklarını yükleyecektir.

2.  **Bağımlılıkları Manuel Yükleme (Eğer setup.sh kullanmazsanız):**
    Proje ana dizininde (`animal_tracker_project/`) terminali açın ve aşağıdaki komutu çalıştırın:
    ```bash
    pip install -r requirements.txt
    ```

## Kullanım

1.  **URL Ayarı:**
    `config/settings.py` dosyasını açın ve `DATA_SOURCE_URL` değişkenini, hayvan kayıtlarınızın bulunduğu web sayfasının doğru URL'si ile güncelleyin.

2.  **Uygulamayı Çalıştırın:**
    Proje ana dizininde (`animal_tracker_project/`) terminali açın ve aşağıdaki komutu çalıştırın:
    ```bash
    python src/main.py
    ```
    Uygulama, web sayfasından verileri çekecek, işleyecek, lokal bir JSON dosyasına kaydedecek ve konsolda gebelik durumlarını ve bildirimleri gösterecektir.

## Klasör Yapısı
