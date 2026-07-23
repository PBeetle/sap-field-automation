"""
SMARTLY v2.0 - SAP Excel İçe Aktarma Modülü
Excel dosyalarından veri okuma ve işleme
"""

import openpyxl
from openpyxl import load_workbook
from pathlib import Path
from datetime import datetime
import pandas as pd


class ExcelImporter:
    """
    SAP Excel İçe Aktarma
    """
    
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        
    def import_excel(self, file_path):
        """
        Excel dosyasını içe aktar
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.logger.error(f"Dosya bulunamadı: {file_path}")
            return False
            
        try:
            self.logger.info(f"Excel dosyası okunuyor: {file_path.name}")
            
            # Pandas ile oku
            df = pd.read_excel(file_path)
            
            self.logger.info(f"Satır sayısı: {len(df)}")
            
            # Veriyi işle
            imported_count = 0
            for index, row in df.iterrows():
                if self.process_row(row):
                    imported_count += 1
                    
            self.logger.success(f"{imported_count} satır başarıyla içe aktarıldı")
            return True
            
        except Exception as e:
            self.logger.error(f"Excel içe aktarma hatası: {e}")
            return False
            
    def process_row(self, row):
        """
        Excel satırını işle
        """
        try:
            # Gerekli alanları al
            malzeme_kodu = str(row.get('Malzeme Kodu', '')).strip()
            malzeme_adi = str(row.get('Malzeme Adı', '')).strip()
            miktar = float(row.get('Miktar', 0))
            birim = str(row.get('Birim', 'EA')).strip()
            sap_belgesi = str(row.get('Belge No', '')).strip()
            
            if not malzeme_kodu:
                return False
                
            # Veritabanına ekle
            query = """
                INSERT INTO sap_veriler 
                (malzeme_kodu, malzeme_adi, miktar, birim, sap_belgesi_no, durum, olusturma_tarihi)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute_query(query, (
                malzeme_kodu,
                malzeme_adi,
                miktar,
                birim,
                sap_belgesi,
                'imported',
                datetime.now()
            ))
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Satır işleme hatası: {e}")
            return False
            
    def export_to_excel(self, data, output_file):
        """
        Verileri Excel dosyasına dışa aktar
        """
        try:
            self.logger.info(f"Excel dosyası oluşturuluyor: {output_file}")
            
            # Pandas DataFrame oluştur
            df = pd.DataFrame(data)
            
            # Excel dosyasına yazı
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_excel(output_path, index=False)
            
            self.logger.success(f"Excel dosyası başarıyla oluşturuldu: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Excel dışa aktarma hatası: {e}")
            return False
            
    def get_excel_columns(self, file_path):
        """
        Excel dosyasının kolon adlarını al
        """
        try:
            df = pd.read_excel(file_path, nrows=0)
            return list(df.columns)
        except Exception as e:
            self.logger.error(f"Excel kolon okuma hatası: {e}")
            return []
