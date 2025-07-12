#!/bin/bash

# Gün sonu veya görev sonu rapor ve senkronizasyon betiği.
echo "--- Operasyon Raporu ve Merkezi Üs Senkronizasyonu ---"

# 1. Mevcut durumu göster
echo "Mevcut durum kontrol ediliyor:"
git status
echo "---------------------------------"

# 2. Aider'ın commit'leri dışında kalan tüm dosyaları hazırla
echo "Tüm yerel değişiklikler hazırlanıyor..."
git add .

# 3. Eğer hazırlanacak yeni bir şey varsa, ek bir commit yap
# Bu, Aider'ın unuttuğu veya bizim manuel eklediğimiz dosyaları güvence altına alır.
if ! git diff --quiet --cached; then
    echo "Aider dışı değişiklikler için ek bir commit oluşturuluyor..."
    git commit -m "chore: Sync local changes and untracked files"
else
    echo "Aider'ın commit'leri dışında ek bir değişiklik bulunamadı."
fi

# 4. Tüm yerel kayıtları merkezi üsse gönder
echo -e "\nTüm yerel kayıtlar GitHub'a gönderiliyor..."
git push origin main  # Eğer ana dalınız master ise burayı 'master' olarak değiştirin

echo -e "\n✔ Senkronizasyon tamamlandı. Karargah güncel."
