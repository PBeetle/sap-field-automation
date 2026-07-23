"""
SAP SAHA PERSONELİ İŞ ATAMA OTOMASYONu
PC Operatörü için - Saha Personeline Otomatik İş Atama
"""

import pyautogui
import time
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
import logging
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import threading

# Loglama ayarı
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/sap_otomasyonu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VeriTabani:
    """Veritabanı işlemleri"""
    
    def __init__(self, db_adi="saha_personeli.db"):
        self.db_adi = db_adi
        self.baglanti_kur()
    
    def baglanti_kur(self):
        """Veritabanı bağlantısı kur"""
        try:
            self.baglanti = sqlite3.connect(self.db_adi)
            self.imleç = self.baglanti.cursor()
            self.tablolari_olustur()
            logger.info("Veritabanı bağlantısı başarılı!")
        except Exception as e:
            logger.error(f"Veritabanı hatası: {e}")
    
    def tablolari_olustur(self):
        """Veritabanı tablolarını oluştur"""
        try:
            # Saha Personeli Tablosu
            self.imleç.execute('''
                CREATE TABLE IF NOT EXISTS saha_personeli (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personel_adi TEXT NOT NULL,
                    personel_no TEXT UNIQUE NOT NULL,
                    sap_kullanici TEXT,
                    telefon TEXT,
                    bolum TEXT,
                    aktif INTEGER DEFAULT 1,
                    olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # İş Atama Tablosu
            self.imleç.execute('''
                CREATE TABLE IF NOT EXISTS is_atama (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personel_no TEXT NOT NULL,
                    is_no TEXT NOT NULL,
                    is_adi TEXT,
                    is_tipi TEXT,
                    malzeme_kodu TEXT,
                    miktar REAL,
                    musteri_kodu TEXT,
                    durumu TEXT DEFAULT 'Yeni',
                    atama_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tamamlama_tarihi TIMESTAMP,
                    notlar TEXT,
                    sap_belgesi_no TEXT,
                    FOREIGN KEY(personel_no) REFERENCES saha_personeli(personel_no)
                )
            ''')
            
            # İş Geçmişi Tablosu
            self.imleç.execute('''
                CREATE TABLE IF NOT EXISTS is_gecmisi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personel_no TEXT NOT NULL,
                    is_no TEXT,
                    islem_tipi TEXT,
                    islem_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    aciklama TEXT,
                    FOREIGN KEY(personel_no) REFERENCES saha_personeli(personel_no)
                )
            ''')
            
            # SAP Ayarları Tablosu
            self.imleç.execute('''
                CREATE TABLE IF NOT EXISTS sap_ayarlari (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sap_sunucu TEXT,
                    sap_sistemi TEXT,
                    sap_istemci TEXT,
                    sap_kullanici TEXT,
                    sap_sifre TEXT,
                    sap_dili TEXT DEFAULT 'TR'
                )
            ''')
            
            self.baglanti.commit()
            logger.info("Veritabanı tabloları oluşturuldu!")
        except Exception as e:
            logger.error(f"Tablo oluşturma hatası: {e}")
    
    def personel_ekle(self, personel_adi, personel_no, sap_kullanici, telefon, bolum):
        """Saha personeli ekle"""
        try:
            self.imleç.execute('''
                INSERT INTO saha_personeli 
                (personel_adi, personel_no, sap_kullanici, telefon, bolum)
                VALUES (?, ?, ?, ?, ?)
            ''', (personel_adi, personel_no, sap_kullanici, telefon, bolum))
            self.baglanti.commit()
            logger.info(f"Personel {personel_adi} eklendi!")
            return True
        except Exception as e:
            logger.error(f"Personel ekleme hatası: {e}")
            return False
    
    def personelleri_getir(self):
        """Tüm personelleri getir"""
        try:
            self.imleç.execute('SELECT * FROM saha_personeli WHERE aktif = 1')
            return self.imleç.fetchall()
        except Exception as e:
            logger.error(f"Personel getirme hatası: {e}")
            return []
    
    def is_ata(self, personel_no, is_no, is_adi, is_tipi, malzeme_kodu, miktar, musteri_kodu, notlar=""):
        """İş personele ata"""
        try:
            self.imleç.execute('''
                INSERT INTO is_atama 
                (personel_no, is_no, is_adi, is_tipi, malzeme_kodu, miktar, musteri_kodu, notlar)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (personel_no, is_no, is_adi, is_tipi, malzeme_kodu, miktar, musteri_kodu, notlar))
            self.baglanti.commit()
            
            # Geçmiş kayıt
            self.imleç.execute('''
                INSERT INTO is_gecmisi (personel_no, is_no, islem_tipi, aciklama)
                VALUES (?, ?, ?, ?)
            ''', (personel_no, is_no, 'İş Atama', f"{is_adi} işi atandı"))
            self.baglanti.commit()
            
            logger.info(f"İş {is_no} personele {personel_no} atandı!")
            return True
        except Exception as e:
            logger.error(f"İş atama hatası: {e}")
            return False
    
    def beklemede_olan_isleri_getir(self):
        """Beklemede olan işleri getir"""
        try:
            self.imleç.execute('''
                SELECT * FROM is_atama WHERE durumu = 'Yeni' 
                ORDER BY atama_tarihi ASC
            ''')
            return self.imleç.fetchall()
        except Exception as e:
            logger.error(f"İş getirme hatası: {e}")
            return []
    
    def is_durusunu_guncelle(self, is_id, yeni_durum, sap_belgesi_no=""):
        """İş durumunu güncelle"""
        try:
            self.imleç.execute('''
                UPDATE is_atama 
                SET durumu = ?, tamamlama_tarihi = CURRENT_TIMESTAMP, sap_belgesi_no = ?
                WHERE id = ?
            ''', (yeni_durum, sap_belgesi_no, is_id))
            self.baglanti.commit()
            logger.info(f"İş {is_id} durumu {yeni_durum} olarak güncellendi!")
            return True
        except Exception as e:
            logger.error(f"İş güncelleme hatası: {e}")
            return False
    
    def kapat(self):
        """Veritabanı bağlantısını kapat"""
        try:
            self.baglanti.close()
            logger.info("Veritabanı bağlantısı kapatıldı!")
        except Exception as e:
            logger.error(f"Bağlantı kapama hatası: {e}")


class SAPOtomasyonu:
    """SAP Otomasyonu"""
    
    def __init__(self, db):
        self.db = db
        self.sap_acik = False
    
    def giris_yap(self, kullanici, sifre, istemci='100'):
        """SAP'a giriş yap"""
        try:
            logger.info(f"SAP'a giriş yapılıyor: {kullanici}")
            
            time.sleep(2)
            
            # Kullanıcı adı alanını temizle ve doldur
            pyautogui.click(500, 380)
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.typewrite(kullanici, interval=0.05)
            
            # Şifre alanı
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.typewrite(sifre, interval=0.05)
            
            # İstemci alanı
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.typewrite(istemci, interval=0.05)
            
            # Giriş
            pyautogui.press('enter')
            time.sleep(5)
            
            self.sap_acik = True
            logger.info("SAP'a giriş başarılı!")
            return True
            
        except Exception as e:
            logger.error(f"Giriş hatası: {e}")
            return False
    
    def transaksiyon_ac(self, kod):
        """SAP Transaksiyon kodunu aç"""
        try:
            logger.info(f"Transaksiyon {kod} açılıyor...")
            
            pyautogui.hotkey('ctrl', 'g')
            time.sleep(1)
            
            pyautogui.typewrite(kod, interval=0.1)
            pyautogui.press('enter')
            time.sleep(3)
            
            logger.info(f"Transaksiyon {kod} açıldı!")
            return True
            
        except Exception as e:
            logger.error(f"Transaksiyon açma hatası: {e}")
            return False
    
    def malzeme_sorgusu(self, malzeme_kodu):
        """Malzeme sorgusu (MM03)"""
        try:
            logger.info(f"Malzeme {malzeme_kodu} sorgulanıyor...")
            
            self.transaksiyon_ac('MM03')
            time.sleep(1)
            
            pyautogui.typewrite(malzeme_kodu, interval=0.1)
            pyautogui.press('enter')
            time.sleep(2)
            
            logger.info(f"Malzeme {malzeme_kodu} bulundu!")
            return True
            
        except Exception as e:
            logger.error(f"Malzeme sorgusu hatası: {e}")
            return False
    
    def malzeme_hareket_girisi(self, malzeme_kodu, miktar, depo='0001'):
        """Malzeme hareketi girişi (MIGO)"""
        try:
            logger.info(f"Malzeme hareketi: {malzeme_kodu}, Miktar: {miktar}")
            
            self.transaksiyon_ac('MIGO')
            time.sleep(2)
            
            # Malzeme kodu
            pyautogui.typewrite(malzeme_kodu, interval=0.1)
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # Miktar
            pyautogui.typewrite(str(miktar), interval=0.1)
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # Depo
            pyautogui.typewrite(depo, interval=0.1)
            pyautogui.press('enter')
            time.sleep(2)
            
            # Kaydet
            pyautogui.hotkey('ctrl', 's')
            time.sleep(2)
            
            logger.info("Malzeme hareketi kaydedildi!")
            return True
            
        except Exception as e:
            logger.error(f"Malzeme hareketi hatası: {e}")
            return False
    
    def satis_emri_olustur(self, musteri_kodu, malzeme_kodu, miktar):
        """Satış emri oluştur (VA01)"""
        try:
            logger.info(f"Satış emri: Müşteri={musteri_kodu}, Malzeme={malzeme_kodu}, Miktar={miktar}")
            
            self.transaksiyon_ac('VA01')
            time.sleep(2)
            
            # Müşteri
            pyautogui.typewrite(musteri_kodu, interval=0.1)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Malzeme
            pyautogui.typewrite(malzeme_kodu, interval=0.1)
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # Miktar
            pyautogui.typewrite(str(miktar), interval=0.1)
            pyautogui.press('enter')
            time.sleep(2)
            
            # Kaydet
            pyautogui.hotkey('ctrl', 's')
            time.sleep(2)
            
            logger.info("Satış emri oluşturuldu!")
            return True
            
        except Exception as e:
            logger.error(f"Satış emri hatası: {e}")
            return False
    
    def sevkiyat_olustur(self, satış_emri_no):
        """Sevkiyat oluştur (VL01N)"""
        try:
            logger.info(f"Sevkiyat oluşturuluyor: {satış_emri_no}")
            
            self.transaksiyon_ac('VL01N')
            time.sleep(2)
            
            # Satış emri
            pyautogui.typewrite(satış_emri_no, interval=0.1)
            pyautogui.press('enter')
            time.sleep(3)
            
            # Kaydet
            pyautogui.hotkey('ctrl', 's')
            time.sleep(2)
            
            logger.info("Sevkiyat oluşturuldu!")
            return True
            
        except Exception as e:
            logger.error(f"Sevkiyat oluşturma hatası: {e}")
            return False
    
    def cikis_yap(self):
        """SAP'tan çık"""
        try:
            logger.info("SAP'tan çıkılıyor...")
            pyautogui.hotkey('alt', 'f4')
            time.sleep(2)
            self.sap_acik = False
            logger.info("SAP kapatıldı!")
            return True
        except Exception as e:
            logger.error(f"Çıkış hatası: {e}")
            return False


class SahaOtomasyonuGUI:
    """GUI Arayüzü"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SAP SAHA PERSONELİ OTOMASYONu - PC Operatörü")
        self.root.geometry("1200x700")
        self.root.config(bg="#f0f0f0")
        
        self.db = VeriTabani()
        self.sap = SAPOtomasyonu(self.db)
        
        self.arayuzu_olustur()
    
    def arayuzu_olustur(self):
        """GUI arayüzünü oluştur"""
        
        # Başlık
        baslik_frame = Frame(self.root, bg="#2c3e50", height=60)
        baslik_frame.pack(fill=X)
        baslik_frame.pack_propagate(False)
        
        baslik_label = Label(
            baslik_frame,
            text="🔧 SAP SAHA PERSONELİ OTOMASYONu - PC OPERATÖRÜ PANELI",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        baslik_label.pack(pady=10)
        
        # Ana kontrol paneli
        kontrol_frame = LabelFrame(self.root, text="KONTROL PANELİ", font=("Arial", 12, "bold"), padx=10, pady=10)
        kontrol_frame.pack(fill=X, padx=10, pady=10)
        
        # SAP Giriş Bölümü
        sap_frame = LabelFrame(kontrol_frame, text="SAP Giriş Bilgileri", font=("Arial", 10, "bold"), padx=5, pady=5)
        sap_frame.pack(fill=X, pady=5)
        
        Label(sap_frame, text="Kullanıcı Adı:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.sap_kullanici_entry = Entry(sap_frame, width=20)
        self.sap_kullanici_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(sap_frame, text="Şifre:").grid(row=0, column=2, sticky=W, padx=5, pady=5)
        self.sap_sifre_entry = Entry(sap_frame, width=20, show="*")
        self.sap_sifre_entry.grid(row=0, column=3, padx=5, pady=5)
        
        Label(sap_frame, text="İstemci:").grid(row=0, column=4, sticky=W, padx=5, pady=5)
        self.sap_istemci_entry = Entry(sap_frame, width=10)
        self.sap_istemci_entry.insert(0, "100")
        self.sap_istemci_entry.grid(row=0, column=5, padx=5, pady=5)
        
        self.sap_giris_btn = Button(sap_frame, text="SAP'a Giriş Yap", command=self.sap_giris, bg="#27ae60", fg="white", font=("Arial", 10, "bold"))
        self.sap_giris_btn.grid(row=0, column=6, padx=5, pady=5)
        
        # Personel Yönetimi Bölümü
        personel_frame = LabelFrame(kontrol_frame, text="Saha Personeli Yönetimi", font=("Arial", 10, "bold"), padx=5, pady=5)
        personel_frame.pack(fill=X, pady=5)
        
        Label(personel_frame, text="Personel Adı:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.personel_adi_entry = Entry(personel_frame, width=20)
        self.personel_adi_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(personel_frame, text="Personel No:").grid(row=0, column=2, sticky=W, padx=5, pady=5)
        self.personel_no_entry = Entry(personel_frame, width=15)
        self.personel_no_entry.grid(row=0, column=3, padx=5, pady=5)
        
        Label(personel_frame, text="SAP Kullanıcı:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.personel_sap_entry = Entry(personel_frame, width=20)
        self.personel_sap_entry.grid(row=1, column=1, padx=5, pady=5)
        
        Label(personel_frame, text="Telefon:").grid(row=1, column=2, sticky=W, padx=5, pady=5)
        self.personel_telefon_entry = Entry(personel_frame, width=15)
        self.personel_telefon_entry.grid(row=1, column=3, padx=5, pady=5)
        
        self.personel_ekle_btn = Button(personel_frame, text="Personel Ekle", command=self.personel_ekle, bg="#3498db", fg="white", font=("Arial", 10, "bold"))
        self.personel_ekle_btn.grid(row=0, column=4, rowspan=2, padx=5, pady=5, sticky=NS)
        
        # İş Atama Bölümü
        is_atama_frame = LabelFrame(kontrol_frame, text="İş Atama", font=("Arial", 10, "bold"), padx=5, pady=5)
        is_atama_frame.pack(fill=X, pady=5)
        
        Label(is_atama_frame, text="Personel:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.personel_combo = ttk.Combobox(is_atama_frame, width=20, state="readonly")
        self.personel_combo.grid(row=0, column=1, padx=5, pady=5)
        
        Label(is_atama_frame, text="İş No:").grid(row=0, column=2, sticky=W, padx=5, pady=5)
        self.is_no_entry = Entry(is_atama_frame, width=15)
        self.is_no_entry.grid(row=0, column=3, padx=5, pady=5)
        
        Label(is_atama_frame, text="İş Adı:").grid(row=0, column=4, sticky=W, padx=5, pady=5)
        self.is_adi_entry = Entry(is_atama_frame, width=20)
        self.is_adi_entry.grid(row=0, column=5, padx=5, pady=5)
        
        Label(is_atama_frame, text="İş Tipi:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.is_tipi_combo = ttk.Combobox(is_atama_frame, width=20, state="readonly")
        self.is_tipi_combo['values'] = ('Malzeme Sorgusu', 'Malzeme Hareketi', 'Satış Emri', 'Sevkiyat')
        self.is_tipi_combo.grid(row=1, column=1, padx=5, pady=5)
        
        Label(is_atama_frame, text="Malzeme:").grid(row=1, column=2, sticky=W, padx=5, pady=5)
        self.malzeme_entry = Entry(is_atama_frame, width=15)
        self.malzeme_entry.grid(row=1, column=3, padx=5, pady=5)
        
        Label(is_atama_frame, text="Miktar:").grid(row=1, column=4, sticky=W, padx=5, pady=5)
        self.miktar_entry = Entry(is_atama_frame, width=10)
        self.miktar_entry.grid(row=1, column=5, padx=5, pady=5)
        
        Label(is_atama_frame, text="Müşteri:").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.musteri_entry = Entry(is_atama_frame, width=15)
        self.musteri_entry.grid(row=2, column=1, padx=5, pady=5)
        
        Label(is_atama_frame, text="Notlar:").grid(row=2, column=2, sticky=W, padx=5, pady=5)
        self.notlar_entry = Entry(is_atama_frame, width=40)
        self.notlar_entry.grid(row=2, column=3, columnspan=2, padx=5, pady=5)
        
        self.is_ata_btn = Button(is_atama_frame, text="İŞ ATA", command=self.is_ata, bg="#e74c3c", fg="white", font=("Arial", 10, "bold"))
        self.is_ata_btn.grid(row=1, column=5, rowspan=2, padx=5, pady=5, sticky=NS)
        
        # İş Listesi Bölümü
        liste_frame = LabelFrame(self.root, text="BEKLEMEDE OLAN İŞLER", font=("Arial", 12, "bold"), padx=10, pady=10)
        liste_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar ile Treeview
        scroll_y = Scrollbar(liste_frame)
        scroll_y.pack(side=RIGHT, fill=Y)
        
        self.isler_tree = ttk.Treeview(
            liste_frame,
            columns=('ID', 'Personel No', 'İş No', 'İş Adı', 'Tipi', 'Malzeme', 'Miktar', 'Müşteri', 'Durumu', 'Atama Tarihi'),
            height=15,
            yscrollcommand=scroll_y.set
        )
        scroll_y.config(command=self.isler_tree.yview)
        
        # Kolon başlıkları
        self.isler_tree.column('#0', width=0, stretch=NO)
        self.isler_tree.column('ID', anchor=W, width=40)
        self.isler_tree.column('Personel No', anchor=W, width=80)
        self.isler_tree.column('İş No', anchor=W, width=70)
        self.isler_tree.column('İş Adı', anchor=W, width=120)
        self.isler_tree.column('Tipi', anchor=W, width=100)
        self.isler_tree.column('Malzeme', anchor=W, width=80)
        self.isler_tree.column('Miktar', anchor=W, width=60)
        self.isler_tree.column('Müşteri', anchor=W, width=80)
        self.isler_tree.column('Durumu', anchor=W, width=80)
        self.isler_tree.column('Atama Tarihi', anchor=W, width=150)
        
        self.isler_tree.heading('#0', text='', anchor=W)
        self.isler_tree.heading('ID', text='ID', anchor=W)
        self.isler_tree.heading('Personel No', text='Personel No', anchor=W)
        self.isler_tree.heading('İş No', text='İş No', anchor=W)
        self.isler_tree.heading('İş Adı', text='İş Adı', anchor=W)
        self.isler_tree.heading('Tipi', text='Tipi', anchor=W)
        self.isler_tree.heading('Malzeme', text='Malzeme', anchor=W)
        self.isler_tree.heading('Miktar', text='Miktar', anchor=W)
        self.isler_tree.heading('Müşteri', text='Müşteri', anchor=W)
        self.isler_tree.heading('Durumu', text='Durumu', anchor=W)
        self.isler_tree.heading('Atama Tarihi', text='Atama Tarihi', anchor=W)
        
        self.isler_tree.pack(fill=BOTH, expand=True)
        
        # Alt Butonlar
        alt_frame = Frame(self.root, bg="#f0f0f0")
        alt_frame.pack(fill=X, padx=10, pady=10)
        
        self.yenile_btn = Button(alt_frame, text="LİSTEYİ YENILE", command=self.isleri_listele, bg="#9b59b6", fg="white", font=("Arial", 10, "bold"))
        self.yenile_btn.pack(side=LEFT, padx=5)
        
        self.otomasyonu_baslat_btn = Button(alt_frame, text="OTOMASYONu BAŞLAT", command=self.otomasyonu_baslat, bg="#e67e22", fg="white", font=("Arial", 10, "bold"))
        self.otomasyonu_baslat_btn.pack(side=LEFT, padx=5)
        
        self.cikis_btn = Button(alt_frame, text="ÇIKIŞ", command=self.cikis, bg="#c0392b", fg="white", font=("Arial", 10, "bold"))
        self.cikis_btn.pack(side=RIGHT, padx=5)
        
        # Durum çubuğu
        self.durum_label = Label(self.root, text="Hazır...", bg="#ecf0f1", fg="#2c3e50", font=("Arial", 9))
        self.durum_label.pack(fill=X, padx=10, pady=5)
        
        self.isleri_listele()
    
    def durum_guncelle(self, mesaj):
        """Durum çubuğunu güncelle"""
        self.durum_label.config(text=mesaj)
        self.root.update()
    
    def sap_giris(self):
        """SAP'a giriş yap"""
        try:
            kullanici = self.sap_kullanici_entry.get()
            sifre = self.sap_sifre_entry.get()
            istemci = self.sap_istemci_entry.get()
            
            if not kullanici or not sifre:
                messagebox.showerror("Hata", "Kullanıcı adı ve şifre giriniz!")
                return
            
            self.durum_guncelle("SAP'a giriş yapılıyor...")
            
            # SAP giriş işlemini ayrı thread'te yap
            thread = threading.Thread(target=self._sap_giris_thread, args=(kullanici, sifre, istemci))
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Hata", f"SAP giriş hatası: {e}")
            logger.error(f"SAP giriş hatası: {e}")
    
    def _sap_giris_thread(self, kullanici, sifre, istemci):
        """SAP giriş thread'i"""
        try:
            if self.sap.giris_yap(kullanici, sifre, istemci):
                self.durum_guncelle("✓ SAP'a başarıyla giriş yapıldı!")
                messagebox.showinfo("Başarılı", "SAP'a başarıyla giriş yapıldı!")
            else:
                self.durum_guncelle("✗ SAP giriş başarısız!")
                messagebox.showerror("Hata", "SAP giriş başarısız!")
        except Exception as e:
            messagebox.showerror("Hata", f"Hata: {e}")
            logger.error(f"SAP giriş thread hatası: {e}")
    
    def personel_ekle(self):
        """Personel ekle"""
        try:
            ad = self.personel_adi_entry.get()
            no = self.personel_no_entry.get()
            sap_user = self.personel_sap_entry.get()
            telefon = self.personel_telefon_entry.get()
            
            if not ad or not no:
                messagebox.showerror("Hata", "Personel adı ve numarası zorunludur!")
                return
            
            if self.db.personel_ekle(ad, no, sap_user, telefon, ""):
                messagebox.showinfo("Başarılı", f"{ad} başarıyla eklendi!")
                self.personel_adi_entry.delete(0, END)
                self.personel_no_entry.delete(0, END)
                self.personel_sap_entry.delete(0, END)
                self.personel_telefon_entry.delete(0, END)
                self.personel_combo_guncelle()
                self.durum_guncelle(f"✓ Personel {ad} eklendi!")
            else:
                messagebox.showerror("Hata", "Personel eklenirken hata oluştu!")
        except Exception as e:
            messagebox.showerror("Hata", f"Hata: {e}")
            logger.error(f"Personel ekleme hatası: {e}")
    
    def personel_combo_guncelle(self):
        """Personel combobox'ını güncelle"""
        try:
            personeller = self.db.personelleri_getir()
            personel_listesi = [f"{p[2]} - {p[1]}" for p in personeller]
            self.personel_combo['values'] = personel_listesi
        except Exception as e:
            logger.error(f"Personel combo güncelleme hatası: {e}")
    
    def is_ata(self):
        """İş personele ata"""
        try:
            if not self.personel_combo.get():
                messagebox.showerror("Hata", "Personel seçiniz!")
                return
            
            if not self.is_no_entry.get():
                messagebox.showerror("Hata", "İş No giriniz!")
                return
            
            personel_bilgisi = self.personel_combo.get()
            personel_no = personel_bilgisi.split(" - ")[1]
            
            is_no = self.is_no_entry.get()
            is_adi = self.is_adi_entry.get()
            is_tipi = self.is_tipi_combo.get()
            malzeme = self.malzeme_entry.get()
            miktar = self.miktar_entry.get()
            musteri = self.musteri_entry.get()
            notlar = self.notlar_entry.get()
            
            if self.db.is_ata(personel_no, is_no, is_adi, is_tipi, malzeme, miktar, musteri, notlar):
                messagebox.showinfo("Başarılı", f"İş {is_no} personele atandı!")
                
                # Alanları temizle
                self.is_no_entry.delete(0, END)
                self.is_adi_entry.delete(0, END)
                self.is_tipi_combo.set("")
                self.malzeme_entry.delete(0, END)
                self.miktar_entry.delete(0, END)
                self.musteri_entry.delete(0, END)
                self.notlar_entry.delete(0, END)
                
                self.isleri_listele()
                self.durum_guncelle(f"✓ İş {is_no} personele {personel_no} atandı!")
            else:
                messagebox.showerror("Hata", "İş atanırken hata oluştu!")
        except Exception as e:
            messagebox.showerror("Hata", f"Hata: {e}")
            logger.error(f"İş atama hatası: {e}")
    
    def isleri_listele(self):
        """Beklemede olan işleri listele"""
        try:
            # Önceki verileri temizle
            for item in self.isler_tree.get_children():
                self.isler_tree.delete(item)
            
            # Yeni verileri ekle
            isleri = self.db.beklemede_olan_isleri_getir()
            for is_ in isleri:
                self.isler_tree.insert('', 'end', values=(
                    is_[0], is_[1], is_[2], is_[3], is_[4], is_[5], is_[6], is_[7], is_[8], is_[9]
                ))
            
            self.durum_guncelle(f"✓ {len(isleri)} adet beklemede iş listelendi!")
        except Exception as e:
            logger.error(f"İş listeleme hatası: {e}")
    
    def otomasyonu_baslat(self):
        """Otomasyonu başlat"""
        try:
            if not self.sap.sap_acik:
                messagebox.showerror("Hata", "Lütfen önce SAP'a giriş yapınız!")
                return
            
            isleri = self.db.beklemede_olan_isleri_getir()
            
            if not isleri:
                messagebox.showinfo("Bilgi", "Beklemede olan iş yok!")
                return
            
            self.durum_guncelle("🔄 Otomasyonu başlatılıyor...")
            
            # Otomasyonu ayrı thread'te yap
            thread = threading.Thread(target=self._otomasyonu_calistir, args=(isleri,))
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Hata: {e}")
            logger.error(f"Otomasyon başlatma hatası: {e}")
    
    def _otomasyonu_calistir(self, isleri):
        """Otomasyonu çalıştır"""
        try:
            for is_ in isleri:
                is_id = is_[0]
                is_tipi = is_[4]
                malzeme = is_[5]
                miktar = is_[6]
                musteri = is_[7]
                is_no = is_[2]
                
                self.durum_guncelle(f"🔄 İşleniyor: {is_no} ({is_tipi})")
                
                sap_belgesi_no = ""
                
                if is_tipi == "Malzeme Sorgusu":
                    if self.sap.malzeme_sorgusu(malzeme):
                        sap_belgesi_no = malzeme
                        durum = "Tamamlandı"
                    else:
                        durum = "Hata"
                
                elif is_tipi == "Malzeme Hareketi":
                    if self.sap.malzeme_hareket_girisi(malzeme, float(miktar) if miktar else 1):
                        sap_belgesi_no = f"{malzeme}-{int(time.time())}"
                        durum = "Tamamlandı"
                    else:
                        durum = "Hata"
                
                elif is_tipi == "Satış Emri":
                    if self.sap.satis_emri_olustur(musteri, malzeme, float(miktar) if miktar else 1):
                        sap_belgesi_no = f"SO-{int(time.time())}"
                        durum = "Tamamlandı"
                    else:
                        durum = "Hata"
                
                elif is_tipi == "Sevkiyat":
                    if self.sap.sevkiyat_olustur(is_no):
                        sap_belgesi_no = f"SH-{int(time.time())}"
                        durum = "Tamamlandı"
                    else:
                        durum = "Hata"
                
                # İş durumunu güncelle
                self.db.is_durusunu_guncelle(is_id, durum, sap_belgesi_no)
                time.sleep(1)
            
            self.isleri_listele()
            self.durum_guncelle("✓ Tüm işler başarıyla tamamlandı!")
            messagebox.showinfo("Başarılı", "Tüm işler başarıyla tamamlandı!")
            
        except Exception as e:
            self.durum_guncelle(f"✗ Hata: {e}")
            messagebox.showerror("Hata", f"Otomasyon hatası: {e}")
            logger.error(f"Otomasyon çalıştırma hatası: {e}")
    
    def cikis(self):
        """Programdan çık"""
        try:
            if self.sap.sap_acik:
                self.sap.cikis_yap()
            self.db.kapat()
            self.root.quit()
        except Exception as e:
            logger.error(f"Çıkış hatası: {e}")


def main():
    """Ana program"""
    root = Tk()
    app = SahaOtomasyonuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
