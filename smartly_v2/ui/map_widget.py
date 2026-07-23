"""
SMARTLY Enterprise - Phase 3: Harita Arayüzü
OpenStreetMap Entegrasyonu
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QLineEdit, QLabel, QSpinBox, QDoubleSpinBox, QMessageBox,
    QProgressBar, QFileDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from pathlib import Path
import folium
from folium.plugins import MarkerCluster, HeatMap
import os


class MapWidget(QWidget):
    """
    Harita Görüntüleme ve İşlemler
    """
    
    def __init__(self, db, logger, maps_integration):
        super().__init__()
        self.db = db
        self.logger = logger
        self.maps = maps_integration
        self.map_file = "maps/smartly_map.html"
        self.init_ui()
        
    def init_ui(self):
        """
        Harita arayüzünü oluştur
        """
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("🗺️ Harita - Konumlar ve Takip")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Kontrol Paneli
        control_layout = QHBoxLayout()
        
        # Merkez Koordinatları
        control_layout.addWidget(QLabel("Merkez Enlem:"))
        self.center_lat = QDoubleSpinBox()
        self.center_lat.setRange(36.0, 42.0)
        self.center_lat.setValue(41.0082)
        control_layout.addWidget(self.center_lat)
        
        control_layout.addWidget(QLabel("Merkez Boylam:"))
        self.center_lon = QDoubleSpinBox()
        self.center_lon.setRange(26.0, 45.0)
        self.center_lon.setValue(28.9784)
        control_layout.addWidget(self.center_lon)
        
        # Zoom Seviyesi
        control_layout.addWidget(QLabel("Zoom:"))
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(1, 18)
        self.zoom_spin.setValue(10)
        control_layout.addWidget(self.zoom_spin)
        
        # Filtreler
        control_layout.addWidget(QLabel("Filtre:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tüm İşler", "Yeni İşler", "Devam Edenler", "Tamamlananlar"])
        control_layout.addWidget(self.filter_combo)
        
        layout.addLayout(control_layout)
        
        # Harita Butonu Satırı
        map_button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Haritayı Yenile")
        refresh_btn.clicked.connect(self.refresh_map)
        map_button_layout.addWidget(refresh_btn)
        
        heatmap_btn = QPushButton("🔥 Isı Haritası")
        heatmap_btn.clicked.connect(self.show_heatmap)
        map_button_layout.addWidget(heatmap_btn)
        
        cluster_btn = QPushButton("📍 Cluster")
        cluster_btn.clicked.connect(self.show_clusters)
        map_button_layout.addWidget(cluster_btn)
        
        export_kml_btn = QPushButton("💾 KML İndir")
        export_kml_btn.clicked.connect(self.export_kml)
        map_button_layout.addWidget(export_kml_btn)
        
        export_csv_btn = QPushButton("📊 CSV İndir")
        export_csv_btn.clicked.connect(self.export_csv)
        map_button_layout.addWidget(export_csv_btn)
        
        open_browser_btn = QPushButton("🌐 Tarayıcıda Aç")
        open_browser_btn.clicked.connect(self.open_in_browser)
        map_button_layout.addWidget(open_browser_btn)
        
        map_button_layout.addStretch()
        layout.addLayout(map_button_layout)
        
        # Harita Bilgi Paneli
        info_layout = QHBoxLayout()
        
        self.info_label = QLabel("⏳ Harita yükleniyor...")
        info_layout.addWidget(self.info_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(0)  # İlerleme göster
        info_layout.addWidget(self.progress_bar)
        
        layout.addLayout(info_layout)
        
        # Haritayı İlk Yükle
        self.refresh_map()
        
    def refresh_map(self):
        """
        Haritayı yenile ve güncelle
        """
        try:
            self.logger.info("Harita yenileniyor...")
            self.info_label.setText("⏳ Harita oluşturuluyor...")
            
            # Harita oluştur
            map_obj = folium.Map(
                location=[self.center_lat.value(), self.center_lon.value()],
                zoom_start=self.zoom_spin.value(),
                tiles="OpenStreetMap"
            )
            
            # Veritabanından konumları al
            locations = self.db.fetch_all("""
                SELECT enlem, boylam, adres, is_id FROM harita_konumlari
                WHERE enlem IS NOT NULL AND boylam IS NOT NULL
                LIMIT 100
            """)
            
            # İşaretçileri ekle
            for loc in locations:
                enlem, boylam, adres, is_id = loc
                folium.Marker(
                    location=[enlem, boylam],
                    popup=f"İş #{is_id}",
                    tooltip=adres or "Adres Yok",
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(map_obj)
            
            # Haritayı kaydet
            Path("maps").mkdir(exist_ok=True)
            map_obj.save(self.map_file)
            
            self.logger.success(f"Harita oluşturuldu: {len(locations)} konum")
            self.info_label.setText(f"✓ Harita hazır ({len(locations)} konum)")
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(100)
            
        except Exception as e:
            self.logger.error(f"Harita oluşturma hatası: {e}")
            self.info_label.setText(f"✗ Hata: {e}")
            
    def show_heatmap(self):
        """
        Isı haritası göster (Hotspot Analizi)
        """
        try:
            self.logger.info("Isı haritası oluşturuluyor...")
            
            map_obj = folium.Map(
                location=[self.center_lat.value(), self.center_lon.value()],
                zoom_start=self.zoom_spin.value()
            )
            
            # Koordinatları al
            locations = self.db.fetch_all("""
                SELECT enlem, boylam FROM harita_konumlari
                WHERE enlem IS NOT NULL AND boylam IS NOT NULL
            """)
            
            if locations:
                heat_data = [[loc[0], loc[1]] for loc in locations]
                HeatMap(heat_data).add_to(map_obj)
                
            Path("maps").mkdir(exist_ok=True)
            map_obj.save("maps/smartly_heatmap.html")
            
            self.logger.success("Isı haritası oluşturuldu")
            QMessageBox.information(self, "Başarılı", "Isı haritası oluşturuldu: maps/smartly_heatmap.html")
            
        except Exception as e:
            self.logger.error(f"Isı haritası hatası: {e}")
            
    def show_clusters(self):
        """
        Cluster haritası göster
        """
        try:
            self.logger.info("Cluster haritası oluşturuluyor...")
            
            map_obj = folium.Map(
                location=[self.center_lat.value(), self.center_lon.value()],
                zoom_start=self.zoom_spin.value()
            )
            
            marker_cluster = MarkerCluster().add_to(map_obj)
            
            locations = self.db.fetch_all("""
                SELECT enlem, boylam, adres FROM harita_konumlari
                WHERE enlem IS NOT NULL AND boylam IS NOT NULL
            """)
            
            for loc in locations:
                folium.Marker(
                    location=[loc[0], loc[1]],
                    popup=loc[2] or "Adres Yok"
                ).add_to(marker_cluster)
                
            Path("maps").mkdir(exist_ok=True)
            map_obj.save("maps/smartly_clusters.html")
            
            self.logger.success("Cluster haritası oluşturuldu")
            QMessageBox.information(self, "Başarılı", "Cluster haritası oluşturuldu: maps/smartly_clusters.html")
            
        except Exception as e:
            self.logger.error(f"Cluster hatası: {e}")
            
    def export_kml(self):
        """
        KML dosyası olarak dışa aktar
        """
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "KML Dosyasını Kaydet",
                "exports/",
                "KML Files (*.kml)"
            )
            
            if file_path:
                self.maps.export_kml(file_path)
                self.logger.success(f"KML dışa aktarıldı: {file_path}")
                QMessageBox.information(self, "Başarılı", f"KML dosyası kaydedildi: {file_path}")
                
        except Exception as e:
            self.logger.error(f"KML export hatası: {e}")
            
    def export_csv(self):
        """
        CSV dosyası olarak dışa aktar
        """
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "CSV Dosyasını Kaydet",
                "exports/",
                "CSV Files (*.csv)"
            )
            
            if file_path:
                locations = self.db.fetch_all("""
                    SELECT enlem, boylam, adres FROM harita_konumlari
                    WHERE enlem IS NOT NULL AND boylam IS NOT NULL
                """)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Enlem,Boylam,Adres\n")
                    for loc in locations:
                        f.write(f"{loc[0]},{loc[1]},\"{loc[2] or ''}\"\n")
                        
                self.logger.success(f"CSV dışa aktarıldı: {file_path}")
                QMessageBox.information(self, "Başarılı", f"CSV dosyası kaydedildi: {file_path}")
                
        except Exception as e:
            self.logger.error(f"CSV export hatası: {e}")
            
    def open_in_browser(self):
        """
        Haritayı tarayıcıda aç
        """
        try:
            import webbrowser
            map_path = Path(self.map_file).absolute()
            webbrowser.open(f"file:///{map_path}")
            self.logger.success("Harita tarayıcıda açıldı")
        except Exception as e:
            self.logger.error(f"Tarayıcı açma hatası: {e}")
