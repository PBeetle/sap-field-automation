"""
SMARTLY v2.0 - Log Sistemi
Detaylı Loglama ve İzleme
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


class Logger:
    """
    Merkezi Log Yöneticisi
    """
    
    def __init__(self, log_dir="logs", log_name=None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        if log_name is None:
            log_name = f"smartly_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
        self.log_file = self.log_dir / log_name
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """
        Logger'ı yapılandır
        """
        logger = logging.getLogger("SMARTLY")
        logger.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File Handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
        
    def debug(self, message):
        """Debug log"""
        self.logger.debug(f"🔍 {message}")
        
    def info(self, message):
        """Info log"""
        self.logger.info(f"ℹ️  {message}")
        
    def warning(self, message):
        """Warning log"""
        self.logger.warning(f"⚠️  {message}")
        
    def error(self, message, exc_info=False):
        """Error log"""
        self.logger.error(f"❌ {message}", exc_info=exc_info)
        
    def critical(self, message):
        """Critical log"""
        self.logger.critical(f"🚨 {message}")
        
    def success(self, message):
        """Success log"""
        self.logger.info(f"✓ {message}")
