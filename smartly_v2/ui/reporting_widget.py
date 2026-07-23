"""
SMARTLY Enterprise - Phase 3: Raporlama Arayüzü
PDF, Excel, Email Raporları
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QDateEdit, QLabel, QCheckBox, QProgressBar, QMessageBox,
    QFileDialog, QTextEdit, QTabWidget, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from pathlib import Path
from datetime import datetime, timedelta
import os


class ReportingWidget(QWidget):
    """
    Raporlama ve Export Sistemi
    """
    
    def __init__(self, db, logger, reporting_manager):
        super().__init__()
        self.db = db
        self.logger = logger
        self.reporting = reporting_manager
        self.init_ui()
        
    def init_ui(self):
        """
        Raporlama arayüzünü oluştur
        """
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("📊 Raporlama Sistemi")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Tab Widget
        tabs = QTabWidget()
        
        # 1. Hızlı Raporlar
        quick_tab = QWidget()
        quick_layout = QVBoxLayout(quick_tab)
        
        report_buttons_layout = QHBoxLayout()
        
        daily_btn = QPushButton("📅 Günlük Rapor")
        daily_btn.clicked.connect(self.generate_daily_report)
        report_buttons_layout.addWidget(daily_btn)
        
        weekly_btn = QPushButton("📈 Haftalık Rapor")
        weekly_btn.clicked.connect(self.generate_weekly_report)
        report_buttons_layout.addWidget(weekly_btn)
        
        monthly_btn = QPushButton("📊 Aylık Rapor")
        monthly_btn.clicked.connect(self.generate_monthly_report)
        report_buttons_layout.addWidget(monthly_btn)
        
        performance_btn = QPushButton("👥 Ekip Performansı")
        performance_btn.clicked.connect(self.generate_performance_report)
        report_buttons_layout.addWidget(performance_btn)
        
        quick_layout.addLayout(report_buttons_layout)
        
        # Rapor Listesi
        self.report_list = QListWidget()
        quick_layout.addWidget(QLabel("📁 Oluşturulan Raporlar:"))
        quick_layout.addWidget(self.report_list)
        
        # Download Butonları
        download_layout = QHBoxLayout()
        
        download_pdf_btn = QPushButton("💾 PDF İndir")
        download_pdf_btn.clicked.connect(self.download_pdf)
        download_layout.addWidget(download_pdf_btn)
        
        download_excel_btn = QPushButton("📥 Excel İndir")
        download_excel_btn.clicked.connect(self.download_excel)
        download_layout.addWidget(download_excel_btn)
        
        open_btn = QPushButton("👁️ Aç")
        open_btn.clicked.connect(self.open_report)
        download_layout.addWidget(open_btn)
        
        quick_layout.addLayout(download_layout)
        
        tabs.addTab(quick_tab, "⚡ Hızlı Raporlar")
        
        # 2. Özel Raporlar
        custom_tab = QWidget()
        custom_layout = QVBoxLayout(custom_tab)
        
        # Tarih Aralığı
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel("Başlangıç Tarihi:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("Bitiş Tarihi:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        
        custom_layout.addLayout(date_layout)
        
        # Rapor Türü
        type_layout = QHBoxLayout()
        
        type_layout.addWidget(QLabel("Rapor Türü:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "İş Özeti",
            "Ekip Performansı",
            "Bölge Yoğunluğu",
            "Depo Stok",
            "Sayaç Takibi",
            "Mali Rapor",
            "Anomali Analizi"
        ])
        type_layout.addWidget(self.report_type_combo)
        
        type_layout.addStretch()
        
        custom_layout.addLayout(type_layout)
        
        # Filtreler
        filter_layout = QHBoxLayout()
        
        self.include_closed = QCheckBox("Kapalı İşleri İnclude Et")
        self.include_closed.setChecked(True)
        filter_layout.addWidget(self.include_closed)
        
        self.include_pending = QCheckBox("Bekleyen İşleri İnclude Et")
        self.include_pending.setChecked(True)
        filter_layout.addWidget(self.include_pending)
        
        custom_layout.addLayout(filter_layout)
        
        # Oluştur Butonu
        create_btn = QPushButton("✨ Rapor Oluştur")
        create_btn.clicked.connect(self.create_custom_report)
        custom_layout.addWidget(create_btn)
        
        # İlerleme Çubuğu
        self.progress_bar = QProgressBar()
        custom_layout.addWidget(self.progress_bar)
        
        tabs.addTab(custom_tab, "⚙️ Özel Raporlar")
        
        # 3. Zamanlanmış Raporlar
        schedule_tab = QWidget()
        schedule_layout = QVBoxLayout(schedule_tab)
        
        schedule_layout.addWidget(QLabel("⏰ Zamanlanmış Raporlar (Gelecek Sürümde)"))
        schedule_layout.addStretch()
        
        tabs.addTab(schedule_tab, "⏰ Zamanlanmış")
        
        layout.addWidget(tabs)
        
        self.load_reports()
        
    def load_reports(self):
        """
        Önceki raporları yükle
        """
        try:
            reports_dir = Path("exports")
            reports_dir.mkdir(exist_ok=True)
            
            self.report_list.clear()
            
            for report_file in sorted(reports_dir.glob("*.pdf")):
                item = QListWidgetItem(f"📄 {report_file.name}")
                item.setData(Qt.UserRole, str(report_file))
                self.report_list.addItem(item)
                
            self.logger.info(f"{self.report_list.count()} rapor bulundu")
            
        except Exception as e:
            self.logger.error(f"Rapor yükleme hatası: {e}")
            
    def generate_daily_report(self):
        """
        Günlük rapor oluştur
        """
        try:
            self.logger.info("Günlük rapor oluşturuluyor...")
            
            data = {
                "Rapor Türü": "Günlük İş Özeti",
                "Tarih": datetime.now().strftime("%d.%m.%Y"),
                "Yeni İşler": "5",
                "Devam Eden": "8",
                "Tamamlanan": "12",
                "Ortalama Süre": "2.5 saat"
            }
            
            filename = f"Günlük_Rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            self.reporting.generate_pdf_report("Günlük Rapor", data, f"exports/{filename}")
            
            QMessageBox.information(self, "Başarılı", f"Rapor oluşturuldu: {filename}")
            self.load_reports()
            
        except Exception as e:
            self.logger.error(f"Günlük rapor hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Hata: {e}")
            
    def generate_weekly_report(self):
        """Haftalık rapor oluştur"""
        self.logger.info("Haftalık rapor oluşturuluyor...")
        QMessageBox.information(self, "Bilgi", "Haftalık rapor oluşturuluyor...")
        
    def generate_monthly_report(self):
        """Aylık rapor oluştur"""
        self.logger.info("Aylık rapor oluşturuluyor...")
        QMessageBox.information(self, "Bilgi", "Aylık rapor oluşturuluyor...")
        
    def generate_performance_report(self):
        """Ekip performans raporu oluştur"""
        self.logger.info("Performans raporu oluşturuluyor...")
        QMessageBox.information(self, "Bilgi", "Performans raporu oluşturuluyor...")
        
    def create_custom_report(self):
        """Özel rapor oluştur"""
        self.logger.info(f"Özel rapor oluşturuluyor: {self.report_type_combo.currentText()}")
        QMessageBox.information(self, "Bilgi", "Özel rapor oluşturuluyor...")
        
    def download_pdf(self):
        """PDF indir"""
        current_item = self.report_list.currentItem()
        if current_item:
            file_path = current_item.data(Qt.UserRole)
            self.logger.info(f"PDF indirildi: {file_path}")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir rapor seçin")
            
    def download_excel(self):
        """Excel indir"""
        self.logger.info("Excel indirildi")
        QMessageBox.information(self, "Bilgi", "Excel raporu oluşturuluyor...")
        
    def open_report(self):
        """Raporu aç"""
        current_item = self.report_list.currentItem()
        if current_item:
            file_path = current_item.data(Qt.UserRole)
            import webbrowser
            webbrowser.open(f"file:///{file_path}")
            self.logger.info(f"Rapor açıldı: {file_path}")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir rapor seçin")
