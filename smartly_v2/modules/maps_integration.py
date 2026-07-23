"""
SMARTLY v2.0 - Google Maps Entegrasyonu Modülü
Harita görüntüleme ve konum işlemleri
"""

import folium
from folium.plugins import MarkerCluster
from pathlib import Path
import json
from datetime import datetime


class MapsIntegration:
    """
    Google Maps ve Folium Entegrasyonu
    """
    
    def __init__(self, db, logger, default_lat=41.0082, default_lon=28.9784):
        self.db = db
        self.logger = logger
        self.default_lat = default_lat  # Istanbul
        self.default_lon = default_lon
        self.map = None
        
    def create_map(self, output_path="map.html"):
        """
        Harita oluştur
        """
        try:
            self.logger.info("Harita oluşturuluyor...")
            
            # Folium haritası oluştur
            self.map = folium.Map(
                location=[self.default_lat, self.default_lon],
                zoom_start=10,
                tiles="OpenStreetMap"
            )
            
            # Veritabanından konumları al
            konumlar = self.db.fetch_all("""
                SELECT hk.*, i.baslik, p.ad, p.soyad
                FROM harita_konumlari hk
                LEFT JOIN isler i ON hk.is_id = i.id
                LEFT JOIN personeller p ON i.atanan_personel_id = p.id
                WHERE hk.enlem IS NOT NULL AND hk.boylam IS NOT NULL
            """)
            
            # İşaretçi ekle
            marker_cluster = MarkerCluster().add_to(self.map)
            
            for konum in konumlar:
                popup_text = f"""
                <b>{konum[8] if konum[8] else 'İş'}</b><br>
                Kişi: {konum[9] or 'Atanmadı'} {konum[10] or ''}<br>
                Adres: {konum[4] or 'Belirsiz'}<br>
                Not: {konum[5] or 'Yok'}
                """
                
                folium.Marker(
                    location=[konum[2], konum[3]],
                    popup=popup_text,
                    tooltip=f"İş #{konum[1]}"
                ).add_to(marker_cluster)
                
            # Haritayı kaydet
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.map.save(str(output_path))
            
            self.logger.success(f"Harita oluşturuldu: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Harita oluşturma hatası: {e}")
            return False
            
    def add_location(self, job_id, latitude, longitude, address, notes=""):
        """
        Yeni konum ekle
        """
        try:
            query = """
                INSERT INTO harita_konumlari (is_id, enlem, boylam, adres, notlar)
                VALUES (?, ?, ?, ?, ?)
            """
            
            self.db.execute_query(query, (job_id, latitude, longitude, address, notes))
            self.logger.success(f"Konum eklendi: {address}")
            return True
            
        except Exception as e:
            self.logger.error(f"Konum ekleme hatası: {e}")
            return False
            
    def filter_by_area(self, center_lat, center_lon, radius_km=5):
        """
        Alan içinde filtreleme yap
        """
        try:
            # Basit mesafe hesabı (km)
            query = """
                SELECT *, 
                (6371 * acos(cos(radians(?)) * cos(radians(enlem)) * 
                cos(radians(boylam) - radians(?)) + sin(radians(?)) * 
                sin(radians(enlem)))) AS mesafe
                FROM harita_konumlari
                HAVING mesafe < ?
                ORDER BY mesafe
            """
            
            results = self.db.fetch_all(query, (center_lat, center_lon, center_lat, radius_km))
            self.logger.info(f"Alan filtresi: {len(results)} konum bulundu")
            return results
            
        except Exception as e:
            self.logger.error(f"Alan filtreleme hatası: {e}")
            return []
            
    def export_kml(self, output_path="locations.kml"):
        """
        KML formatında dışa aktar
        """
        try:
            self.logger.info("KML dosyası oluşturuluyor...")
            
            konumlar = self.db.fetch_all("""
                SELECT * FROM harita_konumlari
                WHERE enlem IS NOT NULL AND boylam IS NOT NULL
            """)
            
            kml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
            kml_content += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
            kml_content += '  <Document>\n'
            kml_content += '    <name>SMARTLY Konumlar</name>\n'
            
            for konum in konumlar:
                kml_content += '    <Placemark>\n'
                kml_content += f'      <name>İş #{konum[1]}</name>\n'
                kml_content += f'      <description>{konum[5]}</description>\n'
                kml_content += '      <Point>\n'
                kml_content += f'        <coordinates>{konum[3]},{konum[2]},0</coordinates>\n'
                kml_content += '      </Point>\n'
                kml_content += '    </Placemark>\n'
                
            kml_content += '  </Document>\n'
            kml_content += '</kml>\n'
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(kml_content, encoding='utf-8')
            
            self.logger.success(f"KML dosyası oluşturuldu: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"KML dışa aktarma hatası: {e}")
            return False
