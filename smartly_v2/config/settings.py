"""
SMARTLY v2.0 - Ayarlar Yönetimi
Uygulama Konfigürasyonu
"""

import json
from pathlib import Path
from datetime import datetime


class Settings:
    """
    Uygulama Ayarları
    """
    
    def __init__(self, config_file="smartly_config.json"):
        self.config_file = Path(config_file)
        self.config = self.get_default_config()
        
    def get_default_config(self):
        """
        Varsayılan ayarları döndür
        """
        return {
            "app_name": "SMARTLY v2.0",
            "version": "2.0.0",
            "db_path": "smartly.db",
            "log_dir": "logs",
            "export_dir": "exports",
            "backup_dir": "backups",
            
            # Arayüz Ayarları
            "theme": "dark",
            "language": "tr",
            "window_width": 1400,
            "window_height": 900,
            
            # SAP Ayarları
            "sap_excel_encoding": "utf-8",
            
            # Google Maps
            "maps_default_zoom": 10,
            "maps_default_lat": 41.0082,
            "maps_default_lon": 28.9784,
            
            # Veritabanı Ayarları
            "auto_backup": True,
            "backup_interval_days": 7,
            
            # Log Ayarları
            "log_level": "INFO",
            "log_file_retention_days": 30,
        }
        
    def load(self):
        """
        Ayarları dosyadan yükle
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                    print(f"✓ Ayarlar yüklendi: {self.config_file}")
            except Exception as e:
                print(f"Ayarlar yükleme hatası: {e}")
                self.save()  # Hata durumunda kaydet
        else:
            self.save()  # İlk çalışmada kaydet
            
    def save(self):
        """
        Ayarları dosyaya kaydet
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                print(f"✓ Ayarlar kaydedildi: {self.config_file}")
        except Exception as e:
            print(f"Ayarlar kaydetme hatası: {e}")
            
    def get(self, key, default=None):
        """
        Ayar değeri al
        """
        return self.config.get(key, default)
        
    def set(self, key, value):
        """
        Ayar değeri belirle
        """
        self.config[key] = value
        self.save()
        
    def __getattr__(self, name):
        """
        Nokta gösterimi ile ayarlara eriş
        """
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return self.config.get(name)
