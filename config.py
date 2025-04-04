import os
from dotenv import load_dotenv
import logging

# Lade Umgebungsvariablen
load_dotenv()

# API Keys und Credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APIFY_API_KEY = os.getenv("APIFY_API_KEY")
APIFY_ACTOR_ID = os.getenv("APIFY_ACTOR_ID")
APIFY_DATASET_URL = os.getenv("APIFY_DATASET_URL")
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# Google Sheets Konfiguration
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
LEADS_SHEET_NAME = "Leads"

# E-Mail Konfiguration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Scraping Konfiguration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Timeout Konfiguration
SELENIUM_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT", "30"))
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "60"))

# Retry Konfiguration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))

def validate_config():
    """Überprüft die Konfiguration auf Vollständigkeit"""
    required_vars = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "APIFY_API_KEY": APIFY_API_KEY,
        "APIFY_ACTOR_ID": APIFY_ACTOR_ID,
        "APIFY_DATASET_URL": APIFY_DATASET_URL,
        "SPREADSHEET_ID": SPREADSHEET_ID,
        "EMAIL_USERNAME": EMAIL_USERNAME,
        "EMAIL_PASSWORD": EMAIL_PASSWORD
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        error_msg = f"Fehlende Umgebungsvariablen: {', '.join(missing_vars)}"
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    # Überprüfe Google Credentials
    if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
        error_msg = f"Google Credentials Datei nicht gefunden: {GOOGLE_CREDENTIALS_FILE}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)

# Führe die Konfigurationsvalidierung beim Import aus
validate_config() 