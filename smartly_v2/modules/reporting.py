"""
SMARTLY v2.0 - Raporlama Modülü
PDF ve Excel rapor oluşturma
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from pathlib import Path
from datetime import datetime
import pandas as pd


class ReportingManager:
    """
    Raporlama ve PDF/Excel oluşturma
    """
    
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        
    def generate_pdf_report(self, report_title, data, output_path="report.pdf"):
        """
        PDF rapor oluştur
        """
        try:
            self.logger.info(f"PDF rapor oluşturuluyor: {report_title}")
            
            # Dosya yolu oluştur
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # PDF oluştur
            doc = SimpleDocTemplate(str(output_path), pagesize=A4)
            story = []
            
            # Başlık
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30
            )
            
            story.append(Paragraph(f"📊 {report_title}", title_style))
            story.append(Paragraph(f"Oluşturma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 0.3 * inch))
            
            # Veri tablosu
            if isinstance(data, list) and len(data) > 0:
                # Başlıklar
                if isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    table_data = [headers]
                    
                    for row in data:
                        table_data.append([str(row.get(h, '')) for h in headers])
                else:
                    table_data = data
                    
                # Tablo oluştur
                table = Table(table_data, colWidths=[1.5*inch]*len(table_data[0]) if table_data else [])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
                ]))
                
                story.append(table)
                
            # Raporu oluştur
            doc.build(story)
            
            self.logger.success(f"PDF rapor oluşturuldu: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"PDF rapor oluşturma hatası: {e}")
            return False
            
    def generate_excel_report(self, report_title, data, output_path="report.xlsx"):
        """
        Excel rapor oluştur
        """
        try:
            self.logger.info(f"Excel rapor oluşturuluyor: {report_title}")
            
            # DataFrame oluştur
            df = pd.DataFrame(data)
            
            # Dosya yolu oluştur
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Excel dosyasına yazı
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Rapor', index=False)
                
                # Format ayarla
                workbook = writer.book
                worksheet = writer.sheets['Rapor']
                
                # Kolon genişliğini ayarla
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                    
            self.logger.success(f"Excel rapor oluşturuldu: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Excel rapor oluşturma hatası: {e}")
            return False
            
    def get_job_summary(self):
        """
        İş özet raporu
        """
        try:
            query = """
                SELECT 
                    status,
                    COUNT(*) as is_sayisi,
                    AVG(saatler_yukleme) as ortalama_saat,
                    MAX(tarih_bitis) as son_bitis_tarihi
                FROM isler
                GROUP BY status
            """
            
            results = self.db.fetch_all(query)
            self.logger.info(f"İş özet raporu: {len(results)} kategori")
            
            return results
            
        except Exception as e:
            self.logger.error(f"İş özet raporu hatası: {e}")
            return []
