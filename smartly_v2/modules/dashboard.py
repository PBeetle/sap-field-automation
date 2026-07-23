"""
SMARTLY v2.0 - Dashboard Modülü
Grafikler, İstatistikler ve Analiz
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QDateEdit, QPushButton, QComboBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from PySide6.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PySide6.QtCore import Qt as QtCore
import random


class DashboardWidget(QWidget):
    """
    Dashboard Modülü - İstatistikler ve Grafikler
    """
    
    def __init__(self, db, logger):
        super().__init__()
        self.db = db
        self.logger = logger
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """
        Dashboard arayüzünü oluştur
        """
        main_layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("📊 Dashboard - İstatistikler ve Analiz")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        main_layout.addWidget(title)
        
        # Filtreler
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Tarih Aralığı:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.start_date)
        
        filter_layout.addWidget(QLabel("-"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)
        
        filter_layout.addWidget(QLabel("Kategori:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Tümü", "SAP", "Harita", "Ekip"])
        filter_layout.addWidget(self.category_combo)
        
        filter_btn = QPushButton("🔄 Yenile")
        filter_btn.clicked.connect(self.load_data)
        filter_layout.addWidget(filter_btn)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        # İstatistik Kartları
        stats_layout = QGridLayout()
        
        self.stat_cards = {
            "Toplam İş": self.create_stat_card("📋 Toplam İş", "0", "#3498db"),
            "Tamamlanan": self.create_stat_card("✅ Tamamlanan", "0", "#27ae60"),
            "Devam Eden": self.create_stat_card("⏳ Devam Eden", "0", "#f39c12"),
            "Personel Sayı": self.create_stat_card("👥 Personel Sayı", "0", "#9b59b6"),
        }
        
        col = 0
        for stat_name, stat_card in self.stat_cards.items():
            stats_layout.addWidget(stat_card, 0, col)
            col += 1
            
        main_layout.addLayout(stats_layout)
        
        # Grafikler
        charts_layout = QGridLayout()
        
        # Pasta Grafik - İş Durumu
        self.pie_chart = self.create_pie_chart()
        pie_view = QChartView(self.pie_chart)
        pie_view.setRenderHint(pie_view.Antialiasing)
        charts_layout.addWidget(pie_view, 0, 0)
        
        # Bar Grafik - Haftaya Göre
        self.bar_chart = self.create_bar_chart()
        bar_view = QChartView(self.bar_chart)
        bar_view.setRenderHint(bar_view.Antialiasing)
        charts_layout.addWidget(bar_view, 0, 1)
        
        main_layout.addLayout(charts_layout)
        
    def create_stat_card(self, label, value, color):
        """
        İstatistik kartı oluştur
        """
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        card.setMinimumHeight(100)
        
        layout = QVBoxLayout(card)
        
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Arial", 12, QFont.Bold))
        label_widget.setStyleSheet("color: white;")
        layout.addWidget(label_widget)
        
        value_widget = QLabel(value)
        value_widget.setFont(QFont("Arial", 24, QFont.Bold))
        value_widget.setStyleSheet("color: white;")
        value_widget.setObjectName(f"value_{label}")
        layout.addWidget(value_widget)
        
        return card
        
    def create_pie_chart(self):
        """
        Pasta grafik oluştur
        """
        chart = QChart()
        chart.setTitle("📊 İş Durumu Dağılımı")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        series = QPieSeries()
        
        # Örnek veriler
        slices_data = [
            ("Yeni", 5, "#3498db"),
            ("Devam Eden", 8, "#f39c12"),
            ("Tamamlanan", 12, "#27ae60"),
            ("Gecikmiş", 2, "#e74c3c"),
        ]
        
        for label, value, color in slices_data:
            slice_obj = series.append(label, value)
            slice_obj.setColor(QColor(color))
            
        chart.addSeries(series)
        chart.legend().setVisible(True)
        
        return chart
        
    def create_bar_chart(self):
        """
        Bar grafik oluştur
        """
        chart = QChart()
        chart.setTitle("📈 Haftaya Göre İş Sayısı")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Veri seti
        bar_set = QBarSet("İşler")
        bar_set.setColor(QColor("#3498db"))
        
        bar_set.append(5)
        bar_set.append(8)
        bar_set.append(6)
        bar_set.append(9)
        bar_set.append(7)
        bar_set.append(11)
        bar_set.append(4)
        
        series = QBarSeries()
        series.append(bar_set)
        
        chart.addSeries(series)
        
        # Kategoriler
        categories = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, QtCore.Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Y Ekseni
        axis_y = QValueAxis()
        axis_y.setRange(0, 15)
        chart.addAxis(axis_y, QtCore.Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        chart.legend().setVisible(True)
        
        return chart
        
    def load_data(self):
        """
        Veritabanından veri yükle
        """
        self.logger.info("Dashboard verileri yükleniyor...")
        
        try:
            # Toplam iş
            total_jobs = self.db.fetch_one("SELECT COUNT(*) as count FROM isler")
            total = total_jobs[0] if total_jobs else 0
            
            # Tamamlanan iş
            completed = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM isler WHERE status = 'tamamlandi'"
            )
            completed_count = completed[0] if completed else 0
            
            # Devam eden
            ongoing = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM isler WHERE status = 'devam_ediyor'"
            )
            ongoing_count = ongoing[0] if ongoing else 0
            
            # Personel sayı
            staff = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM personeller WHERE durum = 'aktif'"
            )
            staff_count = staff[0] if staff else 0
            
            # İstatistik kartlarını güncelle
            self.stat_cards["Toplam İş"].findChild(QLabel, "value_📋 Toplam İş").setText(str(total))
            self.stat_cards["Tamamlanan"].findChild(QLabel, "value_✅ Tamamlanan").setText(str(completed_count))
            self.stat_cards["Devam Eden"].findChild(QLabel, "value_⏳ Devam Eden").setText(str(ongoing_count))
            self.stat_cards["Personel Sayı"].findChild(QLabel, "value_👥 Personel Sayı").setText(str(staff_count))
            
            self.logger.success(f"Dashboard verileri yüklendi: {total} iş, {staff_count} personel")
            
        except Exception as e:
            self.logger.error(f"Dashboard veri yükleme hatası: {e}")
