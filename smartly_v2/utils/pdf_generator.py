"""
SMARTLY v2.0 - PDF Rapor Generatörü
Detaylı PDF raporları oluştur
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from datetime import datetime
from pathlib import Path


class PDFReportGenerator:
    """
    PDF Rapor Üretimi
    """
    
    def __init__(self, logger):
        self.logger = logger
        self.styles = getSampleStyleSheet()
        
    def create_title_page(self, title, subtitle=""):
        """
        Kapak sayfası oluştur
        """
        story = []
        
        # Boş alan
        story.append(Spacer(1, 2 * inch))
        
        # Başlık
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1  # Ortala
        )
        
        story.append(Paragraph(f"📈 {title}", title_style))
        
        if subtitle:
            story.append(Paragraph(subtitle, self.styles['Heading3']))
            
        # Boş alan
        story.append(Spacer(1, 1 * inch))
        
        # Tarih
        story.append(Paragraph(
            f"<b>Oluşturma Tarihi:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            self.styles['Normal']
        ))
        
        story.append(Paragraph(
            f"<b>Sistem:</b> SMARTLY v2.0",
            self.styles['Normal']
        ))
        
        return story
