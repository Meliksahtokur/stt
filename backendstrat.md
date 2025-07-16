backend stratejileri buraya not alinacak
### **AWS Entegrasyon Stratejisi: Mobil Uygulama (Kivy) + Supabase (Veritabanı/Auth) + AWS Lambda (İşlem Gücü)**

Bu strateji, mobil uygulamanızın "elleri ve gözleri" (Kivy UI, veri girişi) olmaya devam etmesini, Supabase'in "hafızası" (veritabanı, kimlik doğrulama) olmasını, ve AWS Lambda'nın "beyni" (ağır hesaplama ve analiz) olmasını sağlayacaktır.

---

**Faz 1: AWS Ortamı ve Temel Fonksiyonların Hazırlanması**

**Hedef:** AWS hesabını yapılandırmak ve bilimsel kütüphaneleri kullanabilen ilk Lambda fonksiyonlarını dağıtmak.

*   **Adım 1.1: AWS Hesabı Oluşturma ve Kredi Kartı Onayı**
    *   AWS Free Tier'dan yararlanarak bir AWS hesabı oluşturun. (Kredi kartı bilgisi girmeniz gerekecektir.)
    *   Hesabınızı etkinleştirin ve ödeme bilgilerinizin doğru olduğundan emin olun.

*   **Adım 1.2: IAM Kullanıcısı ve İzinleri Oluşturma**
    *   AWS konsolunda, Lambda fonksiyonlarını dağıtmak ve yönetmek için bir IAM (Identity and Access Management) kullanıcısı oluşturun.
    *   Bu kullanıcıya minimum yetki prensibiyle, sadece Lambda'ya dağıtım, CloudWatch'a log yazma ve S3'e erişim (eğer fonksiyon paketi S3'te depolanacaksa) gibi gerekli izinleri verin.

*   **Adım 1.3: AWS CLI Kurulumu ve Yapılandırması (Geliştirme Ortamınızda)**
    *   Yerel geliştirme ortamınıza AWS CLI'ı kurun.
    *   `aws configure` komutu ile IAM kullanıcınızın erişim anahtarlarını ve varsayılan bölgesini (örneğin `eu-central-1` - Frankfurt) yapılandırın. Bu, Lambda fonksiyonlarınızı CLI üzerinden kolayca dağıtmanızı sağlayacaktır.

*   **Adım 1.4: Lambda Layer Oluşturma (`numpy`, `pandas`, `matplotlib` için)**
    *   `numpy`, `pandas`, `matplotlib` gibi büyük kütüphaneler, Lambda fonksiyonlarının dağıtım paketini (zip dosyası) çok büyütebilir. Bunu aşmak için bu kütüphaneleri bir **Lambda Layer** olarak paketleyeceğiz.
    *   Lambda Layer, birden fazla fonksiyonda yeniden kullanılabilen bağımlılıkları veya özel kodları içerir. Bu, her fonksiyon paketinizi küçük tutar.
    *   Doğru mimariye (ARM64) ve Python sürümüne (Python 3.9 veya 3.10) uygun bir Linux ortamında bu kütüphaneleri yükleyip zipleyerek bir Layer oluşturacağız.

*   **Adım 1.5: İlk AWS Lambda Fonksiyonunu Oluşturma (`get_statistics_lambda`)**
    *   `src/statistics.py` içindeki `calculate_statistics`, `calculate_breed_distribution`, `calculate_births_per_month` gibi istatistik hesaplama fonksiyonlarını bu Lambda fonksiyonuna taşıyacağız.
    *   Bu fonksiyon, Supabase'den hayvan verilerini çekecek (Supabase Python istemcisini Lambda ortamında kurarak) ve istatistikleri hesaplayıp JSON olarak dönecek.
    *   `matplotlib` ile grafik oluşturma fonksiyonları ayrı bir fonksiyonda ele alınacaktır (bkz. Adım 1.6).
    *   Fonksiyonu AWS konsolundan veya AWS CLI kullanarak dağıtın ve Adım 1.4'te oluşturulan Layer'ı bu fonksiyona ekleyin.

*   **Adım 1.6: İkinci AWS Lambda Fonksiyonunu Oluşturma (`generate_charts_lambda`)**
    *   `src/statistics.py` içindeki `generate_pie_chart_base64` ve `generate_bar_chart_base64` gibi grafik oluşturma fonksiyonlarını bu ayrı Lambda fonksiyonuna taşıyacağız.
    *   Bu fonksiyon, istatistik verilerini (veya doğrudan hayvan verilerini) girdi olarak alacak, `matplotlib` kullanarak grafikleri oluşturacak ve base64 kodlu PNG/SVG formatında geri dönecek.
    *   Bu fonksiyonu da dağıtın ve Adım 1.4'teki Layer'ı ekleyin.

*   **Adım 1.7: Lambda Fonksiyonlarının Supabase'e Erişimi**
    *   AWS Lambda fonksiyonlarınızın Supabase veritabanına erişebilmesi için `config/secrets.py`'deki `SUPABASE_URL` ve `SUPABASE_KEY` bilgilerini Lambda ortam değişkenleri (environment variables) olarak güvenli bir şekilde saklayın ve bu fonksiyonlar içinde kullanın.

---

**Faz 2: API Gateway ile Lambda Fonksiyonlarını Çağırılabilir Hale Getirme**

**Hedef:** Mobil uygulamanın AWS Lambda fonksiyonlarını HTTPS üzerinden güvenli bir şekilde çağırabilmesini sağlamak.

*   **Adım 2.1: API Gateway REST API Oluşturma**
    *   AWS API Gateway konsolunda yeni bir REST API oluşturun.
    *   Her Lambda fonksiyonu (`get_statistics_lambda`, `generate_charts_lambda`) için birer kaynak (resource) ve metod (örneğin `/statistics` için `GET`, `/charts` için `POST`) tanımlayın.
    *   Bu metodları ilgili Lambda fonksiyonlarına entegre edin.

*   **Adım 2.2: API Güvenliği (API Key veya IAM Yetkilendirme)**
    *   **Basit Başlangıç (API Key):** API Gateway için bir API Key oluşturun ve bu anahtarı API metodlarınıza bağlayın. Mobil uygulama, istek yaparken bu API Key'i HTTP başlığına ekleyecektir.
    *   **Daha Gelişmiş (IAM Yetkilendirme):** Eğer daha yüksek güvenlik gereksinimleriniz olursa, AWS IAM yetkilendirmeyi düşünebilirsiniz, ancak bu mobil uygulamada AWS SDK kullanımını gerektirebilir ve ilk aşama için daha karmaşıktır. API Key başlangıç için yeterlidir.

*   **Adım 2.3: CORS Yapılandırması**
    *   API Gateway'iniz ile mobil uygulamanız arasındaki çapraz kaynak isteklerini (CORS) etkinleştirmek için uygun başlıkları yapılandırın.

---

**Faz 3: Mobil Uygulama (Kivy) Entegrasyonu**

**Hedef:** Mobil uygulamayı, ağır iş yükleri için AWS Lambda API'lerini çağıracak şekilde güncellemek.

*   **Adım 3.1: `config/secrets.py` Güncelleme**
    *   AWS API Gateway endpoint URL'sini ve API Key'i `secrets.py` dosyasına ekleyin. Bu bilgileri `.env` dosyasında saklayın.

*   **Adım 3.2: `src/statistics.py` Güncelleme**
    *   Bu modüldeki `calculate_statistics`, `generate_pie_chart_base64`, `generate_bar_chart_base64` gibi fonksiyonların iç mantığını değiştirin. Artık bu fonksiyonlar, yerel olarak hesaplama ve grafik oluşturmak yerine, `requests` kütüphanesini kullanarak AWS API Gateway endpoint'lerini çağıracak ve dönen JSON/base64 verisini işleyecek.

*   **Adım 3.3: `ui/screens/statistics_screen.py` Güncelleme**
    *   `_update_statistics_async` metodunu, güncellenmiş `src/statistics.py` modülünü çağıracak şekilde uyarlayın. Bu metod artık ağ isteklerini (Lambda çağrıları) yönetecek ve dönen grafikleri ve istatistikleri UI'da gösterecek.

*   **Adım 3.4: Hata Yönetimi Geliştirme**
    *   Ağ isteklerinde (API çağrıları) zaman aşımı, bağlantı hatası, yetkilendirme hatası gibi durumlar için sağlam `try-except` blokları ekleyin ve kullanıcıya uygun geri bildirimler verin (`Snackbar` kullanarak).

---

**Faz 4: Test ve "0 Maliyet" Kontrolü**

**Hedef:** Entegre sistemin düzgün çalıştığından ve maliyetin kontrol altında olduğundan emin olmak.

*   **Adım 4.1: Uçtan Uca Test**
    *   Mobil uygulamayı derleyin ve gerçek bir cihazda (veya emülatörde) çalıştırın.
    *   Giriş yapın, hayvan verisi girin/yükleyin ve istatistikler ekranına giderek Lambda fonksiyonlarının doğru tetiklendiğini, veriyi işlediğini ve grafikleri döndürdüğünü doğrulayın.
    *   AWS CloudWatch loglarını ve Lambda/API Gateway metriklerini izleyerek fonksiyonların beklendiği gibi çalıştığını kontrol edin.

*   **Adım 4.2: Maliyet Takibi**
    *   AWS Billing Dashboard'u düzenli olarak kontrol edin. Özellikle Lambda çağrıları, çalışma süresi ve API Gateway istekleri için ücretsiz katman limitlerinizi takip edin.
    *   Limitlere yaklaştığınızda veya beklenmedik bir maliyet gördüğünüzde, uygulamanın kullanımını ayarlayın veya fonksiyonları daha optimize hale getirin.
