"""
SMARTLY v2.0 - Veritabanı Yönetimi
SQLite Veritabanı İşlemleri
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json


class DatabaseManager:
    """
    SQLite Veritabanı Yönetimi
    """
    
    def __init__(self, db_path="smartly.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self.cursor = None
        self.connect()
        
    def connect(self):
        """
        Veritabanına bağlan
        """
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.cursor = self.connection.cursor()
            self.cursor.row_factory = sqlite3.Row
            print(f"✓ Veritabanına bağlanıldı: {self.db_path}")
        except sqlite3.Error as e:
            print(f"✗ Veritabanı bağlantı hatası: {e}")
            raise
            
    def init_database(self):
        """
        Veritabanı tablolarını oluştur
        """
        tables = [
            # Personel Tablosu
            """
            CREATE TABLE IF NOT EXISTS personeller (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                email TEXT UNIQUE,
                telefon TEXT,
                rol TEXT,
                departman TEXT,
                durum TEXT DEFAULT 'aktif',
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # İş Tablosu
            """
            CREATE TABLE IF NOT EXISTS isler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                baslik TEXT NOT NULL,
                aciklama TEXT,
                kategori TEXT,
                status TEXT DEFAULT 'yeni',
                oncelik TEXT DEFAULT 'orta',
                konum_enlem REAL,
                konum_boylam REAL,
                konum_adresi TEXT,
                tarih_baslangic DATE,
                tarih_bitis DATE,
                saatler_yukleme REAL DEFAULT 0,
                atanan_personel_id INTEGER,
                olusturan_personel_id INTEGER,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (atanan_personel_id) REFERENCES personeller(id),
                FOREIGN KEY (olusturan_personel_id) REFERENCES personeller(id)
            )
            """,
            
            # SAP Veri Tablosu
            """
            CREATE TABLE IF NOT EXISTS sap_veriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dosya_adi TEXT,
                malzeme_kodu TEXT,
                malzeme_adi TEXT,
                miktar REAL,
                birim TEXT,
                sap_belgesi_no TEXT,
                durum TEXT,
                personel_id INTEGER,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (personel_id) REFERENCES personeller(id)
            )
            """,
            
            # Harita Konumları
            """
            CREATE TABLE IF NOT EXISTS harita_konumlari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_id INTEGER,
                enlem REAL NOT NULL,
                boylam REAL NOT NULL,
                adres TEXT,
                notlar TEXT,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (is_id) REFERENCES isler(id)
            )
            """,
            
            # Raporlar
            """
            CREATE TABLE IF NOT EXISTS raporlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                tip TEXT,
                icerik TEXT,
                olusturan_personel_id INTEGER,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (olusturan_personel_id) REFERENCES personeller(id)
            )
            """,
            
            # Log Sistemi
            """
            CREATE TABLE IF NOT EXISTS loglar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                islem_tipi TEXT,
                aciklama TEXT,
                personel_id INTEGER,
                olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (personel_id) REFERENCES personeller(id)
            )
            """,
            
            # Ayarlar
            """
            CREATE TABLE IF NOT EXISTS ayarlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anahtar TEXT UNIQUE NOT NULL,
                deger TEXT,
                aciklama TEXT,
                guncelleme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table_sql in tables:
            try:
                self.cursor.execute(table_sql)
            except sqlite3.OperationalError as e:
                print(f"Tablo oluşturma hatası: {e}")
                
        self.connection.commit()
        print("✓ Veritabanı tabloları oluşturuldu")
        
    def execute_query(self, query, params=None):
        """
        SQL sorgusu çalıştır
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Sorgu hatası: {e}")
            return False
            
    def fetch_one(self, query, params=None):
        """
        Tek sonuç getir
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Sorgu hatası: {e}")
            return None
            
    def fetch_all(self, query, params=None):
        """
        Tüm sonuçları getir
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Sorgu hatası: {e}")
            return []
            
    def close(self):
        """
        Veritabanı bağlantısını kapat
        """
        if self.connection:
            self.connection.close()
            print("✓ Veritabanı bağlantısı kapatıldı")
            
    def __del__(self):
        self.close()
