Harika! Deta entegrasyonu için detaylı stratejimizi ve iş planımızı olası sorunları belirleyerek çıkaralım.
                                                                                                                                    ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
### **Deta Entegrasyon Stratejisi: İstatistik ve Grafik İş yükünü Deta Space'e Taşıma**

Bu strateji, mobil uygulamanızın (`Kivy`) Supabase'i (veritabanı ve kimlik doğrulama) kullanmaya devam ederken, `numpy`, `pandas`, `matplotlib` gibi ağır bilimsel kütüphanelerin işlem yükünü AWS Lambda yerine **geçici olarak Deta Space'e taşımasını** sağlayacaktır. Bu sayede mobil uygulama derleme sorunlarından kurtulacak ve "0 maliyet" hedefimizle uyumlu kalacaktır.

---

**Faz 1: Deta Space Backend'i Hazırlama**

**Hedef:** İstatistik hesaplama ve grafik oluşturma API'sini Deta Space'te oluşturmak ve dağıtmak.

*   **Adım 1.1: Deta CLI Kurulumu ve Deta Projesi Oluşturma**
    *   Yerel geliştirme ortamınıza Deta CLI'ı kurun (`curl -fsSL https://get.deta.dev/cli.sh | sh`).
    *   Deta CLI'yı yetkilendirin (`deta login`).
    *   Yeni bir Deta Space projesi başlatın (`deta new`). Bu, bir proje klasörü ve `Micro` hizmeti için varsayılan bir yapı oluşturacaktır.

*   **Adım 1.2: İstatistik ve Grafik API'sinin Tasarımı ve Kodlanması**
    *   Deta projenizin ana dizininde (örneğin `deta_backend/`) bir Python web çerçevesi (FastAPI veya Flask önerilir) kullanarak bir API uygulaması oluşturacağız. FastAPI, modern ve hızlı olduğu için tercih edilecektir.
    *   `src/statistics.py` içindeki **`calculate_statistics`, `calculate_breed_distribution`, `generate_pie_chart_base64`, `calculate_births_per_month`, `generate_bar_chart_base64`, `get_animal_specific_stats`** fonksiyonlarını bu yeni API'ye taşıyacağız.
    *   Bu API endpoint'leri, mobil uygulamadan gelen istekleri alacak, Supabase'den veriyi çekecek ve işlenmiş istatistikleri veya base64 kodlu grafik görüntülerini JSON yanıtı olarak dönecektir.

*   **Adım 1.3: Supabase Entegrasyonu (Deta API'den Supabase'e Erişim)**
    *   Deta API'si içinden Supabase veritabanına erişim sağlamak için `supabase-py` kütüphanesini kullanacağız.
    *   `config/secrets.py`'deki `SUPABASE_URL` ve `SUPABASE_KEY` bilgilerini Deta Micro ortam değişkenleri (Environment Variables) olarak güvenli bir şekilde saklayacağız ve API kodumuz içinde kullanacağız.

*   **Adım 1.4: Deta Micro Servisini Dağıtma**
    *   API kodunu ve bağımlılıklarını (`fastapi`, `uvicorn`, `supabase-py`, `numpy`, `pandas`, `matplotlib`) içeren bir `requirements.txt` dosyasını Deta projesinin içine yerleştireceğiz.
    *   Deta CLI kullanarak (`deta deploy`) API'yi Deta Space'e dağıtacağız. Dağıtım sonrası Deta, herkese açık bir endpoint URL'si sağlayacaktır.

**Faz 2: Mobil Uygulama (Kivy) Entegrasyonu**

**Hedef:** Kivy uygulamasını, istatistik ve grafikler için Deta API'sini çağıracak şekilde güncellemek.

*   **Adım 2.1: `config/secrets.py` Güncelleme**
    *   Deta API'sinin endpoint URL'sini `secrets.py` dosyasına ekleyeceğiz. Bu bilgiyi `.env` dosyasında saklayacağız.

*   **Adım 2.2: `src/statistics.py` Güncelleme**
    *   Bu modüldeki tüm istatistik hesaplama ve grafik oluşturma fonksiyonlarını kaldıracağız.
    *   Bunun yerine, `requests` kütüphanesini kullanarak Deta API'sine HTTP istekleri (GET/POST) gönderecek ve dönen JSON/base64 verisini işleyecek yeni fonksiyonlar yazacağız.

*   **Adım 2.3: `ui/screens/statistics_screen.py` Güncelleme**
    *   `_update_statistics_async` metodunu, güncellenmiş `src/statistics.py` modülündeki yeni API çağrılarını kullanacak şekilde uyarlayacağız. UI'da dönen grafikleri ve istatistikleri göstereceğiz.

*   **Adım 2.4: Bağımlılık Temizliği (`requirements.txt` ve `buildozer.spec`)**
    *   `requirements.txt` dosyasından `numpy`, `pandas`, `matplotlib` paketlerini tamamen çıkaracağız. `requests` kütüphanesinin ise mobil tarafta kalmasını sağlayacağız.
    *   `buildozer.spec` dosyasındaki `requirements` listesinden de aynı paketleri kaldıracağız. Bu, mobil uygulama derleme süresini ve boyutunu azaltacak, build hatalarını çözecektir.

**Faz 3: Test ve Optimizasyon**

**Hedif:** Entegre sistemin düzgün çalıştığından ve "0 maliyet" hedefine uyduğundan emin olmak.

*   **Adım 3.1: Uçtan Uca Test**
    *   Deta API'sini (`deta run` veya doğrudan URL ile) test edin.
    *   Mobil uygulamayı tekrar derleyin ve gerçek bir cihazda (veya emülatörde) çalıştırın.
    *   İstatistikler ekranına giderek Deta API'sinin doğru tetiklendiğini, veriyi işlediğini ve grafikleri döndürdüğünü doğrulayın.
    *   Deta Space'in proje loglarını ve metriklerini izleyerek API'nin beklendiği gibi çalıştığını kontrol edin.

*   **Adım 3.2: Maliyet ve Performans Gözetimi**
    *   Deta Space kontrol panelindeki kullanım metriklerini düzenli olarak kontrol ederek "0 maliyet" limitlerinin aşılmadığından emin olun.
    *   "Cold Start" gecikmelerini gözlemleyin ve kullanıcı deneyimi için kabul edilebilir olup olmadığını değerlendirin.

---

### **Olası Sorunlar ve Çözümleri:**

*   **Python Paket Boyutları/Çalışma Süresi (Deta Limitleri):**
    *   **Sorun:** `numpy`, `pandas`, `matplotlib` paketleri Deta'nın ücretsiz Micro hizmetinin bellek veya çalışma süresi limitlerini zorlayabilir (özellikle büyük veri setleri veya karmaşık grafikler). `matplotlib` özellikle büyük bir pakettir.
    *   **Çözüm:** Fonksiyonları daha küçük parçalara bölmek. Eğer `matplotlib` tek başına problem çıkarırsa, grafikleri oluşturmak için `plotly.js` gibi bir JavaScript kütüphanesi kullanıp JSON istatistik verisini direkt mobil uygulamaya gönderip, client (Kivy webview veya custom widget) tarafında çizdirmeyi düşünebiliriz (ancak bu ek frontend geliştirme gerektirir). Deta limitlerini aşarsak, küçük bir ücret ödemeyi kabul etmeli veya daha hafif bir bulut alternatifine geçişi hızlandırmalıyız.
*   **Supabase Bağlantısı (Deta Ortamından):**
    *   **Sorun:** Deta Micro'dan Supabase'e ağ isteği yaparken güvenlik veya bağlantı sorunları yaşanabilir.
    *   **Çözüm:** Deta Micro ortam değişkenlerinin doğru ayarlandığından emin olmak. Supabase güvenlik kurallarını (Row Level Security - RLS) ve CORS ayarlarını Deta Micro'dan gelen isteklere izin verecek şekilde kontrol etmek.
*   **"Cold Start" Gecikmeleri:**
    *   **Sorun:** Deta Micro (ücretsiz katman) belirli bir süre inaktif kaldığında uyku moduna girebilir. İlk istekte fonksiyonun "uyanması" birkaç saniye sürebilir.
    *   **Çözüm:** Küçük bir web istek zamanlayıcısı (cron job) ile Deta API'nizi düzenli aralıklarla pinglemek (`uptime robot` veya benzeri bir servisle) fonksiyonu "sıcak" tutabilir. Deta'nın "Always On" özelliği varsa onu kullanmak (limitlere uygun olarak).
*   **API Güvenliği:**
    *   **Sorun:** Deta API'sinin herkesin erişimine açık olması ve Supabase anahtarlarının sızdırılma riski (ortam değişkenlerinde saklanacakları için bu risk düşüktür).
    *   **Çözüm:** API anahtarı (API Key) kullanarak erişimi kısıtlamak. Mobil uygulama isteklere bu API anahtarını ekleyecek, Deta API'si bu anahtarı doğrulayacaktır. Bu, doğrudan Supabase anahtarlarını mobil uygulamada taşımaktan çok daha güvenlidir.

---

**İş Planı (Faz 1 ve Faz 2'nin ilk adımları):**

Şimdi, bu stratejiyi hayata geçirmek için ilk adımları atacağız. Mobil uygulamadan `numpy`, `pandas`, `matplotlib` gibi bağımlılıkları çıkaracağız ve backend için Deta'da yeni bir proje yapısı oluşturacağız.

**Değişiklikler:**

1.  **Yeni Deta Backend Proje Yapısı Oluşturma (FastAPI ile):**
    *   `deta_backend/main.py`
    *   `deta_backend/requirements.txt`
2.  **`src/statistics.py` Güncelleme:** İstatistik hesaplama ve grafik oluşturma mantığını bu dosyadan kaldıracağız (Deta backend'e taşınacak).
3.  **`requirements.txt` Güncelleme:** `numpy`, `pandas`, `matplotlib` bağımlılıklarını kaldıracağız.
4.  **`buildozer.spec` Güncelleme:** `numpy`, `pandas`, `matplotlib` bağımlılıklarını kaldıracağız.

---
