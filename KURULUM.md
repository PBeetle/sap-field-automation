# 📥 SAP SAHA OTOMASYONu - KURULUM KILAVUZU

## Windows'ta Kurulum

### 1. Adım: Python Yükle

1. https://www.python.org/downloads/ adresine git
2. "Download Python 3.11" (veya daha yeni) butonuna tıkla
3. İndirilen dosyayı çalıştır
4. **ÖNEMLİ:** "Add Python to PATH" checkbox'ını işaretle
5. "Install Now" butonuna tıkla
6. Kurulum bitene kadar bekle

### 2. Adım: Kod İndir

1. https://github.com/PBeetle/sap-field-automation adresine git
2. Yeşil "Code" butonuna tıkla
3. "Download ZIP" seç
4. ZIP dosyasını extract et (örn: C:\SAP_Otomasyonu)

### 3. Adım: Kütüphaneleri Yükle

1. Command Prompt (Komut İstemci) aç
   - Windows+R tuşuna bas
   - "cmd" yaz ve Enter tuşuna bas

2. Klasöre git:
   ```cmd
   cd C:\SAP_Otomasyonu
   ```

3. Kütüphaneleri yükle:
   ```cmd
   pip install -r requirements.txt
   ```

### 4. Adım: EXE Dosyası Oluştur (Opsiyonel)

Eğer EXE dosyası istersen:

1. Command Prompt'ta:
   ```cmd
   pip install pyinstaller
   pyinstaller --onefile --windowed sap_saha_otomasyonu.py
   ```

2. EXE dosyası burada olacak:
   ```
   C:\SAP_Otomasyonu\dist\sap_saha_otomasyonu.exe
   ```

### 5. Adım: Programı Çalıştır

#### Python ile:
```cmd
python sap_saha_otomasyonu.py
```

#### EXE ile:
```
C:\SAP_Otomasyonu\dist\sap_saha_otomasyonu.exe
```

## 🎯 İlk Çalıştırma

1. Program açıldığında ana pencere görünecek
2. SAP GUI'yi açık tut
3. SAP giriş bilgilerini gir
4. "SAP'a Giriş Yap" butonuna tıkla
5. Başarılı mesaj aldıktan sonra personel ve işleri ekle

## 📁 Dosya Yapısı

```
C:\SAP_Otomasyonu
├── sap_saha_otomasyonu.py     # Ana program
├── requirements.txt            # Kütüphaneler listesi
├── README.md                   # Açıklama dosyası
├── KURULUM.md                  # Bu dosya
├── dist/                       # EXE dosyası
│   └── sap_saha_otomasyonu.exe
├── logs/                       # Log dosyaları (otomatik oluşturulur)
└── saha_personeli.db          # Veritabanı (otomatik oluşturulur)
```

## ⚠️ Sorun Giderme

### "Python bulunamadı" hatası
- Python'u doğru kurduğundan emin ol
- Bilgisayarı yeniden başlat
- Python PATH'e eklendiğini kontrol et

### Kütüphaneler yüklenmiyorsa
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### SAP'a bağlanılamıyor
- SAP GUI açık olduğundan emin ol
- Kullanıcı adı/şifreyi kontrol et
- Ağ bağlantısını kontrol et

## 📞 Yardım

Probleminiz varsa:
1. Log dosyalarını kontrol et (logs/ klasörü)
2. GitHub Issues açarak bildir
3. Tam hata mesajını yapıştır

---

**Başarılı kurulum dilerim! 🚀**
