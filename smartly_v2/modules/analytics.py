"""
SMARTLY v2.0 - Yapay Zeka Analiz Modülü
Veri analizi ve tahminler
"""

from datetime import datetime, timedelta
import statistics


class AIAnalytics:
    """
    Yapay Zeka destekli Analiz
    """
    
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        
    def analyze_hotspots(self):
        """
        En yoğun bölgeleri analiz et
        """
        try:
            self.logger.info("Yoğun bölgeler analiz ediliyor...")
            
            # Konum bazlı clustering
            query = """
                SELECT 
                    COUNT(*) as is_sayisi,
                    AVG(enlem) as ort_enlem,
                    AVG(boylam) as ort_boylam,
                    adres
                FROM harita_konumlari
                WHERE enlem IS NOT NULL AND boylam IS NOT NULL
                GROUP BY adres
                ORDER BY is_sayisi DESC
                LIMIT 10
            """
            
            hotspots = self.db.fetch_all(query)
            self.logger.success(f"Yoğun bölgeler bulundu: {len(hotspots)}")
            
            return hotspots
            
        except Exception as e:
            self.logger.error(f"Hotspot analiz hatası: {e}")
            return []
            
    def predict_performance(self, staff_id):
        """
        Personel performans tahmini
        """
        try:
            # Geçmiş verileri al
            query = """
                SELECT saatler_yukleme, guncelleme_tarihi
                FROM isler
                WHERE atanan_personel_id = ? AND status = 'tamamlandi'
                ORDER BY guncelleme_tarihi DESC
                LIMIT 30
            """
            
            results = self.db.fetch_all(query, (staff_id,))
            
            if not results:
                return None
                
            # Basit tahmin: ortalama ve trend
            hours = [r[0] for r in results if r[0]]
            
            if not hours:
                return None
                
            avg_hours = statistics.mean(hours)
            
            # Trend hesapla (son 10 vs önceki 10)
            if len(hours) >= 10:
                recent_avg = statistics.mean(hours[:10])
                older_avg = statistics.mean(hours[10:])
                trend = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
            else:
                trend = 0
                
            prediction = {
                'staff_id': staff_id,
                'average_hours': round(avg_hours, 2),
                'trend_percent': round(trend, 2),
                'status': 'artiş' if trend > 0 else 'azalış' if trend < 0 else 'sabit'
            }
            
            self.logger.success(f"Performans tahmini: {prediction}")
            return prediction
            
        except Exception as e:
            self.logger.error(f"Performans tahmini hatası: {e}")
            return None
            
    def get_daily_performance(self, days=7):
        """
        Günlük performans raporu
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            query = """
                SELECT 
                    DATE(guncelleme_tarihi) as gun,
                    COUNT(*) as tamamlanan_is,
                    SUM(saatler_yukleme) as toplam_saat,
                    AVG(saatler_yukleme) as ortalama_saat
                FROM isler
                WHERE status = 'tamamlandi' AND guncelleme_tarihi > ?
                GROUP BY DATE(guncelleme_tarihi)
                ORDER BY gun DESC
            """
            
            results = self.db.fetch_all(query, (start_date,))
            self.logger.info(f"Günlük performans: {len(results)} gün")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Günlük performans hatası: {e}")
            return []
            
    def recommend_optimization(self):
        """
        İş akışı optimizasyon önerileri
        """
        try:
            recommendations = []
            
            # 1. Fazla yüklü personeller
            overloaded = self.db.fetch_all("""
                SELECT p.id, p.ad, COUNT(i.id) as is_sayisi
                FROM personeller p
                LEFT JOIN isler i ON p.id = i.atanan_personel_id AND i.status != 'tamamlandi'
                WHERE p.durum = 'aktif'
                GROUP BY p.id
                HAVING is_sayisi > 10
            """)
            
            if overloaded:
                recommendations.append({
                    'type': 'overload',
                    'message': f'{len(overloaded)} personel fazla yüklü',
                    'data': overloaded
                })
                
            # 2. Gecikmiş işler
            delayed = self.db.fetch_all("""
                SELECT COUNT(*) as gecikme_sayisi
                FROM isler
                WHERE status != 'tamamlandi' AND tarih_bitis < ?
            """, (datetime.now(),))
            
            if delayed and delayed[0]:
                recommendations.append({
                    'type': 'delay',
                    'message': f'{delayed[0][0]} işin süresi dolmuş',
                    'count': delayed[0][0]
                })
                
            self.logger.info(f"Optimizasyon önerileri: {len(recommendations)} öneri")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Optimizasyon önerisi hatası: {e}")
            return []
