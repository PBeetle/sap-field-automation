"""
SMARTLY v2.0 - Ana Program
SAP Ekip Yönetimi ve Harita Entegrasyonu Sistemi
"""

import sys
import os
from pathlib import Path

# Proje kökünü ekle
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication
from smartly_v2.ui.main_window import MainWindow
from smartly_v2.database.db_manager import DatabaseManager
from smartly_v2.config.settings import Settings
from smartly_v2.utils.logger import Logger


def main():
    """
    Ana program başlangıcı
    """
    # Logger başlat
    logger = Logger()
    logger.info("="*80)
    logger.info("SMARTLY v2.0 Başlatılıyor...")
    logger.info("="*80)
    
    # Ayarları yükle
    try:
        settings = Settings()
        settings.load()
        logger.info("✓ Ayarlar yüklendi")
    except Exception as e:
        logger.error(f"Ayarlar yüklenirken hata: {e}")
        settings = Settings()
    
    # Veritabanını başlat
    try:
        db = DatabaseManager(settings.db_path)
        db.init_database()
        logger.info("✓ Veritabanı başlatıldı")
    except Exception as e:
        logger.error(f"Veritabanı başlatılırken hata: {e}")
        return 1
    
    # PySide6 Uygulaması
    try:
        app = QApplication(sys.argv)
        
        # Ana pencereyi oluştur
        window = MainWindow(db, settings, logger)
        window.show()
        
        logger.info("✓ Ana pencere gösterildi")
        logger.info("SMARTLY v2.0 Çalışıyor...")
        
        # Uygulamayı çalıştır
        exit_code = app.exec()
        
        logger.info("="*80)
        logger.info("SMARTLY v2.0 Kapatılıyor...")
        logger.info("="*80)
        
        return exit_code
        
    except Exception as e:
        logger.error(f"Uygulama başlatılırken kritik hata: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
