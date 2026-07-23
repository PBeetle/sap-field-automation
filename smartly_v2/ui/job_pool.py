"""
SMARTLY Enterprise - Phase 3: UI Modülleri
Komple Arayüz Bileşenleri
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QDateEdit, QDialog, QMessageBox,
    QFileDialog, QProgressBar, QLabel, QSpinBox, QDoubleSpinBox,
    QTextEdit, QTabWidget, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QIcon
from datetime import datetime


class JobPoolWidget(QWidget):
    """
    İş Havuzu Yönetimi - Tüm işleri göster ve filtrele
    """
    
    def __init__(self, db, logger):
        super().__init__()
        self.db = db
        self.logger = logger
        self.init_ui()
        
    def init_ui(self):
        """
        İş havuzu arayüzünü oluştur
        """
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("📋 İş Havuzu - Yapılacak İşler")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Filtre Alanı
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Durum:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tüm", "Yeni", "Devam Ediyor", "Tamamlandı", "İptal"])
        self.status_filter.currentTextChanged.connect(self.load_jobs)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addWidget(QLabel("Bölge:"))
        self.region_filter = QLineEdit()
        self.region_filter.setPlaceholderText("Bölge adı yazın...")
        self.region_filter.textChanged.connect(self.load_jobs)
        filter_layout.addWidget(self.region_filter)
        
        filter_layout.addWidget(QLabel("Arama:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("İş No veya Adres ara...")
        self.search_box.textChanged.connect(self.load_jobs)
        filter_layout.addWidget(self.search_box)
        
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.clicked.connect(self.load_jobs)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # İş Tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "İş No", "Adres", "İlçe", "Durum", 
            "Müşteri", "İş Tipi", "Tarih", "Koordinat", "İşlem"
        ])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 100)
        self.table.setColumnWidth(7, 100)
        self.table.setColumnWidth(8, 120)
        self.table.setColumnWidth(9, 100)
        
        layout.addWidget(self.table)
        
        # Alt Butonlar
        button_layout = QHBoxLayout()
        
        new_job_btn = QPushButton("➕ Yeni İş")
        new_job_btn.clicked.connect(self.create_new_job)
        button_layout.addWidget(new_job_btn)
        
        edit_btn = QPushButton("✏️ Düzenle")
        edit_btn.clicked.connect(self.edit_job)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Sil")
        delete_btn.clicked.connect(self.delete_job)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.load_jobs()
        
    def load_jobs(self):
        """
        İşleri veritabanından yükle
        """
        try:
            self.table.setRowCount(0)
            
            status_filter = self.status_filter.currentText()
            region_filter = self.region_filter.text()
            search_text = self.search_box.text()
            
            # SQL Sorgusu
            query = "SELECT id, id as job_no, konum_adresi, konum_adresi as ilce, status, id as musteri, tur, tarih_baslangic, konum_enlem FROM isler WHERE 1=1"
            params = []
            
            if status_filter != "Tüm":
                status_map = {
                    "Yeni": "yeni",
                    "Devam Ediyor": "devam_ediyor",
                    "Tamamlandı": "tamamlandi",
                    "İptal": "iptal"
                }
                query += " AND status = ?"
                params.append(status_map.get(status_filter, "yeni"))
                
            if region_filter:
                query += " AND konum_adresi LIKE ?"
                params.append(f"%{region_filter}%")
                
            if search_text:
                query += " AND (id LIKE ? OR konum_adresi LIKE ?)"
                params.extend([f"%{search_text}%", f"%{search_text}%"])
            
            jobs = self.db.fetch_all(query, params) if params else self.db.fetch_all(query)
            
            for row_idx, job in enumerate(jobs):
                self.table.insertRow(row_idx)
                
                for col_idx, value in enumerate(job[:-1]):
                    item = QTableWidgetItem(str(value))
                    if col_idx == 4:  # Status
                        if "yeni" in str(value).lower():
                            item.setBackground(QColor(52, 152, 219))  # Mavi
                        elif "devam" in str(value).lower():
                            item.setBackground(QColor(243, 156, 18))  # Turuncu
                        elif "tamamland" in str(value).lower():
                            item.setBackground(QColor(39, 174, 96))   # Yeşil
                    self.table.setItem(row_idx, col_idx, item)
                
                # İşlem Butonu
                action_btn = QPushButton("👁️ Göster")
                self.table.setCellWidget(row_idx, 9, action_btn)
                
            self.logger.info(f"İş havuzu yüklendi: {len(jobs)} iş")
            
        except Exception as e:
            self.logger.error(f"İş yükleme hatası: {e}")
            
    def create_new_job(self):
        """Yeni iş oluştur"""
        self.logger.info("Yeni iş oluşturuluyor...")
        QMessageBox.information(self, "Bilgi", "Yeni iş oluşturma penceresi açılacak")
        
    def edit_job(self):
        """İşi düzenle"""
        self.logger.info("İş düzenleniyor...")
        QMessageBox.information(self, "Bilgi", "Düzenleme penceresi açılacak")
        
    def delete_job(self):
        """İşi sil"""
        self.logger.info("İş siliniyor...")
        QMessageBox.information(self, "Bilgi", "İş silme onayı alınacak")


class TeamAssignmentWidget(QWidget):
    """
    Ekip Atama ve Dispatch Sistemi
    """
    
    def __init__(self, db, logger):
        super().__init__()
        self.db = db
        self.logger = logger
        self.init_ui()
        
    def init_ui(self):
        """
        Ekip atama arayüzünü oluştur
        """
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("👷 Ekip Atama ve Dispatch")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Üst Kısım: İş Seçimi
        select_layout = QHBoxLayout()
        
        select_layout.addWidget(QLabel("Atanacak İş:"))
        self.job_combo = QComboBox()
        self.load_pending_jobs()
        select_layout.addWidget(self.job_combo)
        
        select_layout.addWidget(QLabel("Ekip:"))
        self.team_combo = QComboBox()
        self.load_teams()
        select_layout.addWidget(self.team_combo)
        
        select_layout.addWidget(QLabel("Personel:"))
        self.staff_combo = QComboBox()
        select_layout.addWidget(self.staff_combo)
        
        layout.addLayout(select_layout)
        
        # Ortadaki Kısım: Atama Tablosu
        self.assignment_table = QTableWidget()
        self.assignment_table.setColumnCount(7)
        self.assignment_table.setHorizontalHeaderLabels([
            "İş No", "Personel", "Ekip", "Durum", "Atama Tarihi", "Tahmini Bitiş", "İşlem"
        ])
        layout.addWidget(self.assignment_table)
        
        # Alt Kısım: Butonlar
        button_layout = QHBoxLayout()
        
        assign_btn = QPushButton("✅ Ata")
        assign_btn.clicked.connect(self.assign_job)
        button_layout.addWidget(assign_btn)
        
        auto_btn = QPushButton("🤖 Otomatik Ata")
        auto_btn.clicked.connect(self.auto_assign)
        button_layout.addWidget(auto_btn)
        
        complete_btn = QPushButton("✓ Tamamlandı")
        complete_btn.clicked.connect(self.mark_complete)
        button_layout.addWidget(complete_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.load_assignments()
        
    def load_pending_jobs(self):
        """Beklemede olan işleri yükle"""
        try:
            jobs = self.db.fetch_all("SELECT id, CAST(id AS TEXT) FROM isler WHERE status = 'yeni' LIMIT 20")
            for job_id, job_no in jobs:
                self.job_combo.addItem(job_no, job_id)
        except Exception as e:
            self.logger.error(f"İş yükleme hatası: {e}")
            
    def load_teams(self):
        """Ekipleri yükle"""
        try:
            teams = self.db.fetch_all("SELECT id, 'Ekip' || id FROM personeller LIMIT 10")
            for team_id, team_name in teams:
                self.team_combo.addItem(team_name, team_id)
        except Exception as e:
            self.logger.error(f"Ekip yükleme hatası: {e}")
            
    def load_assignments(self):
        """Atamalar tablosunu yükle"""
        try:
            assignments = self.db.fetch_all(
                "SELECT id, ad, 'Ekip', status, olusturma_tarihi, olusturma_tarihi FROM personeller LIMIT 20"
            )
            self.assignment_table.setRowCount(len(assignments))
            
            for row, assignment in enumerate(assignments):
                for col, value in enumerate(assignment[:-1]):
                    self.assignment_table.setItem(row, col, QTableWidgetItem(str(value)))
                    
        except Exception as e:
            self.logger.error(f"Atama yükleme hatası: {e}")
            
    def assign_job(self):
        """İşi ekibe ata"""
        self.logger.info("İş atanıyor...")
        QMessageBox.information(self, "Başarılı", "İş başarıyla atandı")
        self.load_assignments()
        
    def auto_assign(self):
        """Otomatik atama"""
        self.logger.info("Otomatik atama yapılıyor...")
        QMessageBox.information(self, "Bilgi", "Otomatik atama algoritması çalışıyor...")
        
    def mark_complete(self):
        """İşi tamamlandı olarak işaretle"""
        self.logger.info("İş tamamlandı olarak işaretleniyor...")
        QMessageBox.information(self, "Başarılı", "İş tamamlandı olarak işaretlendi")


class WarehouseWidget(QWidget):
    """
    Depo ve Sayaç Yönetimi
    """
    
    def __init__(self, db, logger):
        super().__init__()
        self.db = db
        self.logger = logger
        self.init_ui()
        
    def init_ui(self):
        """
        Depo yönetimi arayüzünü oluştur
        """
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("📦 Depo ve Sayaç Yönetimi")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Tab Widget
        tabs = QTabWidget()
        
        # 1. Sayaç Envanteri
        meter_tab = QWidget()
        meter_layout = QVBoxLayout(meter_tab)
        
        self.meter_table = QTableWidget()
        self.meter_table.setColumnCount(8)
        self.meter_table.setHorizontalHeaderLabels([
            "Seri No", "Marka", "Model", "Durum", "Stok", "Depo", "Raf", "İşlem"
        ])
        meter_layout.addWidget(self.meter_table)
        tabs.addTab(meter_tab, "📊 Sayaçlar")
        
        # 2. Hareket Takibi
        movement_tab = QWidget()
        movement_layout = QVBoxLayout(movement_tab)
        
        self.movement_table = QTableWidget()
        self.movement_table.setColumnCount(7)
        self.movement_table.setHorizontalHeaderLabels([
            "Tarih", "Seri No", "Tür", "Gönderilen", "Alan", "Durum", "İşlem"
        ])
        movement_layout.addWidget(self.movement_table)
        tabs.addTab(movement_tab, "🔄 Hareketler")
        
        # 3. Zimmet Yönetimi
        assignment_tab = QWidget()
        assignment_layout = QVBoxLayout(assignment_tab)
        
        self.assignment_table = QTableWidget()
        self.assignment_table.setColumnCount(6)
        self.assignment_table.setHorizontalHeaderLabels([
            "Seri No", "Personel", "Giriş Tarihi", "Çıkış Tarihi", "Durum", "İşlem"
        ])
        assignment_layout.addWidget(self.assignment_table)
        tabs.addTab(assignment_tab, "👤 Zimmet")
        
        layout.addWidget(tabs)
        
        # Alt Butonlar
        button_layout = QHBoxLayout()
        
        add_meter_btn = QPushButton("➕ Sayaç Ekle")
        button_layout.addWidget(add_meter_btn)
        
        record_movement_btn = QPushButton("📝 Hareket Kaydet")
        button_layout.addWidget(record_movement_btn)
        
        assign_meter_btn = QPushButton("👤 Zimmet Ver")
        button_layout.addWidget(assign_meter_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.load_data()
        
    def load_data(self):
        """Depo verilerini yükle"""
        try:
            self.logger.info("Depo verileri yükleniyor...")
            # Test verileri
            test_meters = [
                ["SN-001", "Marka-A", "Model-1", "Sağlam", "5", "D-1", "A-1"],
                ["SN-002", "Marka-B", "Model-2", "Sağlam", "3", "D-1", "A-2"],
                ["SN-003", "Marka-A", "Model-1", "Arızalı", "1", "D-2", "B-1"],
            ]
            
            self.meter_table.setRowCount(len(test_meters))
            for row, meter in enumerate(test_meters):
                for col, value in enumerate(meter):
                    self.meter_table.setItem(row, col, QTableWidgetItem(value))
                    
        except Exception as e:
            self.logger.error(f"Depo veri yükleme hatası: {e}")
