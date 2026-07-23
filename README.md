# 🔧 SAP SAHA PERSONELİ OTOMASYONu

**PC Operatörü için Saha Personeline Otomatik İş Atama Sistemi**

## 📋 Özellikler

### ✅ Ana Fonksiyonlar
- **Saha Personeli Yönetimi** - Personel bilgilerini ekle, düzenle ve yönet
- **İş Atama Sistemi** - Personellere otomatik olarak iş ata
- **SAP Otomasyonu** - 4 türde SAP işlemini otomatik gerçekleştir
- **Veritabanı Yönetimi** - SQLite ile tüm verileri kaydet
- **İş Geçmişi** - Tüm işlemlerin kaydını tut
- **Detaylı Loglama** - Her işlemi log dosyasında kaydet

### 🎯 Desteklenen SAP İşleri
1. **Malzeme Sorgusu (MM03)** - Ürün bilgilerini sorgula
2. **Malzeme Hareketi (MIGO)** - Stok hareketini kayıt et
3. **Satış Emri (VA01)** - Yeni satış emri oluştur
4. **Sevkiyat (VL01N)** - Gemi hazırla

## 🚀 Kurulum

### 1. Python Yükleme
Python 3.7+ gereklidir. [python.org](https://www.python.org) adresinden indir.

### 2. Kütüphaneleri Yükle
```bash
pip install -r requirements.txt
```

### 3. Programı Çalıştır
```bash
python sap_saha_otomasyonu.py
```

## 📦 EXE Dosyası Oluşturma

Windows'ta tek tıkla çalıştırmak için EXE dosyası oluştur:

```bash
# PyInstaller yükle
pip install pyinstaller

# EXE dosyası oluştur
pyinstaller --onefile --windowed sap_saha_otomasyonu.py
```

EXE dosyası şuraya kaydedilecek:
```
dist/sap_saha_otomasyonu.exe
```

## 📖 Kullanım Kılavuzu

### Adım 1: SAP'a Giriş Yap
1. Program başlat
2. SAP Giriş Bilgileri bölümüne kullanıcı adı ve şifre gir
3. "SAP'a Giriş Yap" butonuna tıkla

### Adım 2: Personel Ekle
1. "Saha Personeli Yönetimi" bölümüne personel bilgilerini gir:
   - Personel Adı
   - Personel No
   - SAP Kullanıcı (opsiyonel)
   - Telefon
2. "Personel Ekle" butonuna tıkla

### Adım 3: İş Ata
1. "İş Atama" bölümüne iş detaylarını gir:
   - Personel seç
   - İş No
   - İş Adı
   - İş Tipi (Malzeme Sorgusu, Malzeme Hareketi, Satış Emri, Sevkiyat)
   - Malzeme Kodu
   - Miktar
   - Müşteri Kodu
   - Notlar (opsiyonel)
2. "İŞ ATA" butonuna tıkla

### Adım 4: Otomasyonu Başlat
1. "BEKLEMEDE OLAN İŞLER" listesinde işleri gözle
2. "OTOMASYONu BAŞLAT" butonuna tıkla
3. Sistem otomatik olarak SAP'ta işleri gerçekleştir

## 📁 Veri Yapısı

### Veritabanı Tabloları

**saha_personeli** - Saha personel bilgileri
- id (PRIMARY KEY)
- personel_adi
- personel_no (UNIQUE)
- sap_kullanici
- telefon
- bolum
- aktif
- olusturma_tarihi

**is_atama** - Atanan işler
- id (PRIMARY KEY)
- personel_no (FOREIGN KEY)
- is_no
- is_adi
- is_tipi
- malzeme_kodu
- miktar
- musteri_kodu
- durumu (Yeni, Tamamlandı, Hata)
- atama_tarihi
- tamamlama_tarihi
- notlar
- sap_belgesi_no

**is_gecmisi** - İş işlem geçmişi
- id (PRIMARY KEY)
- personel_no (FOREIGN KEY)
- is_no
- islem_tipi
- islem_tarihi
- aciklama

**sap_ayarlari** - SAP bağlantı ayarları
- id (PRIMARY KEY)
- sap_sunucu
- sap_sistemi
- sap_istemci
- sap_kullanici
- sap_sifre
- sap_dili

## 📊 Dosya Yapısı

```
sap-field-automation/
├── sap_saha_otomasyonu.py     # Ana program
├── requirements.txt            # Python kütüphaneleri
├── README.md                   # Bu dosya
├── logs/                       # Log dosyaları (otomatik oluşturulur)
└── saha_personeli.db          # Veritabanı (otomatik oluşturulur)
```

## 🔐 Güvenlik Notları

⚠️ **ÖNEMLİ:**
- SAP şifrenizi güvenli bir yerde saklayın
- Veritabanı dosyasını yedekleyin
- Program sadece SAP GUI açıkken çalışır
- Otomasyonu başlatmadan SAP'a giriş yapın

## 🐛 Hata Giderme

### SAP'a Bağlanılamıyor
- SAP GUI'nin açık olduğunu kontrol et
- Kullanıcı adı ve şifrenin doğru olduğunu kontrol et
- SAP sunucusunun erişilebilir olduğunu kontrol et

### İşler Otomatik Olarak Yapılmıyor
- SAP giriş yapıldıktan sonra otomasyon başlat
- İş listesinde en az bir iş olduğundan emin ol
- Log dosyalarını kontrol et

### Ekran Koordinatları Yanlış
- Farklı ekran çözünürlükleri için koordinatları ayarla
- `sap_saha_otomasyonu.py` dosyasında koordinatları güncelle

## 📝 Log Dosyaları

Her çalıştırma için otomatik log dosyası oluşturulur:
```
logs/sap_otomasyonu_YYYYMMDD_HHMMSS.log
```

## 🤝 Katkı

Bu proje PC Operatörleri için SAP iş otomasyonunu kolaylaştırmak amacıyla geliştirilmiştir.

## 📄 Lisans

MIT Lisansı - Açıkça kullanın, değiştirin ve dağıtın

## 👨‍💻 Geliştirici

**Copilot** - GitHub

## 📞 Destek

Sorularınız veya sorunlarınız için GitHub Issues açın.

---

**Başarılı otomasyonlar dilerim! 🚀**
