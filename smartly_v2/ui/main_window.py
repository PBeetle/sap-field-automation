"""
SMARTLY v2.0 - Ana Pencere (PySide6)
Kullanıcı Arayüzü ve Menü Yönetimi
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QMenuBar, QMenu, QLabel,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QColor
from pathlib import Path


class MainWindow(QMainWindow):
    """
    Uygulamanın ana penceresi
    """
    
    def __init__(self, db, settings, logger):
        super().__init__()
        self.db = db
        self.settings = settings
        self.logger = logger
        
        self.init_ui()
        self.setup_menus()
        self.setup_status_bar()
        
    def init_ui(self):
        """
        Arayüz bileşenlerini başlat
        """
        self.setWindowTitle("SMARTLY v2.0 - SAP Ekip Yönetimi ve Harita Sistemi")
        self.setGeometry(100, 100, 1400, 900)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        
        # Tab Widget oluştur
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Sekmeler
        self.create_tabs()
        
        central_widget.setLayout(main_layout)
        
    def create_tabs(self):
        """
        Uygulama sekmelerini oluştur
        """
        # 1. Dashboard Sekmesi
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_label = QLabel("📊 Dashboard - Yakında Başlatılacak")
        dashboard_label.setFont(QFont("Arial", 14, QFont.Bold))
        dashboard_layout.addWidget(dashboard_label)
        self.tabs.addTab(dashboard_widget, "📊 Dashboard")
        
        # 2. SAP Excel İçe Aktarma
        import_widget = QWidget()
        import_layout = QVBoxLayout(import_widget)
        import_label = QLabel("📁 SAP Excel İçe Aktarma - Yakında Başlatılacak")
        import_label.setFont(QFont("Arial", 14, QFont.Bold))
        import_layout.addWidget(import_label)
        self.tabs.addTab(import_widget, "📁 İçe Aktarma")
        
        # 3. Harita Sekmesi
        map_widget = QWidget()
        map_layout = QVBoxLayout(map_widget)
        map_label = QLabel("🗺️ Google Maps Entegrasyonu - Yakında Başlatılacak")
        map_label.setFont(QFont("Arial", 14, QFont.Bold))
        map_layout.addWidget(map_label)
        self.tabs.addTab(map_widget, "🗺️ Harita")
        
        # 4. Ekip Yönetimi
        team_widget = QWidget()
        team_layout = QVBoxLayout(team_widget)
        team_label = QLabel("👷 Ekip Yönetimi - Yakında Başlatılacak")
        team_label.setFont(QFont("Arial", 14, QFont.Bold))
        team_layout.addWidget(team_label)
        self.tabs.addTab(team_widget, "👷 Ekip")
        
        # 5. Raporlama
        report_widget = QWidget()
        report_layout = QVBoxLayout(report_widget)
        report_label = QLabel("📈 Raporlama - Yakında Başlatılacak")
        report_label.setFont(QFont("Arial", 14, QFont.Bold))
        report_layout.addWidget(report_label)
        self.tabs.addTab(report_widget, "📈 Raporlar")
        
        # 6. Ayarlar
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_label = QLabel("⚙️ Ayarlar - Yakında Başlatılacak")
        settings_label.setFont(QFont("Arial", 14, QFont.Bold))
        settings_layout.addWidget(settings_label)
        self.tabs.addTab(settings_widget, "⚙️ Ayarlar")
        
    def setup_menus(self):
        """
        Menü çubuğunu ayarla
        """
        menubar = self.menuBar()
        
        # Dosya Menüsü
        file_menu = menubar.addMenu("📁 Dosya")
        
        new_action = file_menu.addAction("Yeni Proje")
        new_action.triggered.connect(self.new_project)
        
        open_action = file_menu.addAction("Proje Aç")
        open_action.triggered.connect(self.open_project)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Çıkış")
        exit_action.triggered.connect(self.close_app)
        
        # İçe Aktarma Menüsü
        import_menu = menubar.addMenu("📥 İçe Aktarma")
        
        excel_action = import_menu.addAction("SAP Excel Dosyası")
        excel_action.triggered.connect(self.import_excel)
        
        csv_action = import_menu.addAction("CSV Dosyası")
        csv_action.triggered.connect(self.import_csv)
        
        # Dışa Aktarma Menüsü
        export_menu = menubar.addMenu("📤 Dışa Aktarma")
        
        pdf_action = export_menu.addAction("PDF Raporu")
        pdf_action.triggered.connect(self.export_pdf)
        
        excel_export_action = export_menu.addAction("Excel Raporu")
        excel_export_action.triggered.connect(self.export_excel)
        
        # Yardım Menüsü
        help_menu = menubar.addMenu("❓ Yardım")
        
        about_action = help_menu.addAction("Hakkında")
        about_action.triggered.connect(self.show_about)
        
    def setup_status_bar(self):
        """
        Durum çubuğunu ayarla
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        status_label = QLabel("✓ SMARTLY v2.0 Hazır")
        self.status_bar.addWidget(status_label)
        
    # Menü İşlemleri
    def new_project(self):
        """Yeni proje oluştur"""
        self.logger.info("Yeni proje oluşturma...")
        QMessageBox.information(self, "Bilgi", "Yeni proje oluşturma özelliği yakında gelecek.")
        
    def open_project(self):
        """Proje aç"""
        self.logger.info("Proje açma...")
        QMessageBox.information(self, "Bilgi", "Proje açma özelliği yakında gelecek.")
        
    def import_excel(self):
        """Excel dosyası içe aktarma"""
        self.logger.info("Excel içe aktarma...")
        QMessageBox.information(self, "Bilgi", "Excel içe aktarma özelliği yakında gelecek.")
        
    def import_csv(self):
        """CSV dosyası içe aktarma"""
        self.logger.info("CSV içe aktarma...")
        QMessageBox.information(self, "Bilgi", "CSV içe aktarma özelliği yakında gelecek.")
        
    def export_pdf(self):
        """PDF raporu dışa aktarma"""
        self.logger.info("PDF dışa aktarma...")
        QMessageBox.information(self, "Bilgi", "PDF dışa aktarma özelliği yakında gelecek.")
        
    def export_excel(self):
        """Excel raporu dışa aktarma"""
        self.logger.info("Excel dışa aktarma...")
        QMessageBox.information(self, "Bilgi", "Excel dışa aktarma özelliği yakında gelecek.")
        
    def show_about(self):
        """Hakkında sayfasını göster"""
        about_text = """
        SMARTLY v2.0
        
        SAP Ekip Yönetimi ve Harita Entegrasyonu Sistemi
        
        Versiyon: 2.0.0
        Geliştirici: Copilot
        
        🚀 Özellikler:
        ✓ SAP Excel İçe Aktarma
        ✓ Google Maps Entegrasyonu
        ✓ Dashboard ve Analiz
        ✓ Ekip Yönetimi
        ✓ PDF/Excel Raporları
        ✓ Log Sistemi
        """
        QMessageBox.about(self, "SMARTLY v2.0 Hakkında", about_text)
        
    def close_app(self):
        """Uygulamayı kapat"""
        self.logger.info("Uygulama kapatılıyor...")
        self.close()
