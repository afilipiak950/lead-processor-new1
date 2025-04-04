import logging
import os
from datetime import datetime

def setup_logger():
    """Richtet den Logger für die Anwendung ein"""
    # Erstelle logs Verzeichnis falls nicht vorhanden
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Erstelle Logger
    logger = logging.getLogger('lead_processor')
    logger.setLevel(logging.INFO)
    
    # Erstelle File Handler
    log_file = f'logs/lead_processor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Erstelle Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Erstelle Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Füge Handler zum Logger hinzu
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Erstelle globalen Logger
logger = setup_logger() 