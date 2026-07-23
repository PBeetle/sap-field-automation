"""
SMARTLY v2.0 - Ekip Yönetimi Modülü
Personel ve iş atama yönetimi
"""

from datetime import datetime, timedelta


class TeamManager:
    """
    Ekip Yönetimi
    """
    
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        
    def add_staff(self, name, surname, email, phone, role, department):
        """
        Personel ekle
        """
        try:
            query = """
                INSERT INTO personeller (ad, soyad, email, telefon, rol, departman, durum)
                VALUES (?, ?, ?, ?, ?, ?, 'aktif')
            """
            
            self.db.execute_query(query, (name, surname, email, phone, role, department))
            self.logger.success(f"Personel eklendi: {name} {surname}")
            return True
            
        except Exception as e:
            self.logger.error(f"Personel ekleme hatası: {e}")
            return False
            
    def assign_job(self, job_id, staff_id):
        """
        İş personele ata
        """
        try:
            query = "UPDATE isler SET atanan_personel_id = ?, status = 'devam_ediyor' WHERE id = ?"
            
            self.db.execute_query(query, (staff_id, job_id))
            self.logger.success(f"İş #{job_id} personel #{staff_id} ye atandı")
            return True
            
        except Exception as e:
            self.logger.error(f"İş atama hatası: {e}")
            return False
            
    def get_staff_workload(self, staff_id):
        """
        Personelin iş yükünü getir
        """
        try:
            result = self.db.fetch_one("""
                SELECT COUNT(*) as aktif_is_sayisi, SUM(saatler_yukleme) as toplam_saat
                FROM isler
                WHERE atanan_personel_id = ? AND status != 'tamamlandi'
            """, (staff_id,))
            
            if result:
                return {
                    'active_jobs': result[0] or 0,
                    'total_hours': result[1] or 0
                }
            return None
            
        except Exception as e:
            self.logger.error(f"İş yükü hesaplama hatası: {e}")
            return None
            
    def suggest_assignment(self, job_hours, job_priority="orta"):
        """
        Otomatik iş dağıtım önerisi
        """
        try:
            # En az yüklü personeli bul
            query = """
                SELECT p.id, p.ad, p.soyad, 
                       COUNT(i.id) as aktif_is_sayisi,
                       COALESCE(SUM(i.saatler_yukleme), 0) as toplam_saat
                FROM personeller p
                LEFT JOIN isler i ON p.id = i.atanan_personel_id AND i.status != 'tamamlandi'
                WHERE p.durum = 'aktif'
                GROUP BY p.id
                ORDER BY toplam_saat ASC
                LIMIT 1
            """
            
            result = self.db.fetch_one(query)
            
            if result:
                suggestion = {
                    'staff_id': result[0],
                    'name': f"{result[1]} {result[2]}",
                    'current_jobs': result[3],
                    'current_hours': result[4],
                    'recommended': True
                }
                
                self.logger.success(f"Atanım önerisi: {suggestion['name']}")
                return suggestion
                
            return None
            
        except Exception as e:
            self.logger.error(f"Atanım önerisi hatası: {e}")
            return None
            
    def get_team_performance(self, start_date=None, end_date=None):
        """
        Ekip performans raporu
        """
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
                
            query = """
                SELECT p.id, p.ad, p.soyad,
                       COUNT(i.id) as tamamlanan_is,
                       AVG(i.saatler_yukleme) as ortalama_saat,
                       MAX(i.guncelleme_tarihi) as son_aktivite
                FROM personeller p
                LEFT JOIN isler i ON p.id = i.atanan_personel_id 
                    AND i.status = 'tamamlandi'
                    AND i.guncelleme_tarihi BETWEEN ? AND ?
                WHERE p.durum = 'aktif'
                GROUP BY p.id
                ORDER BY tamamlanan_is DESC
            """
            
            results = self.db.fetch_all(query, (start_date, end_date))
            self.logger.info(f"Ekip performans raporu: {len(results)} personel")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Performans raporu hatası: {e}")
            return []
