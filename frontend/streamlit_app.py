import streamlit as st
import os
import sys

# Füge das übergeordnete Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Stelle sicher, dass die Umgebungsvariablen geladen werden
from dotenv import load_dotenv
load_dotenv()

# Importiere die Hauptapp
from app import *

# Die App wird automatisch ausgeführt, wenn sie importiert wird

# Umgebungsvariablen für Google Sheets (Beispiel - in der Praxis sollten diese in .env gespeichert werden)
# GOOGLE_SHEETS_CREDENTIALS = {"type": "service_account", "project_id": "example", "private_key_id": "key", "private_key": "key", "client_email": "email", "client_id": "id", "auth_uri": "uri", "token_uri": "uri", "auth_provider_x509_cert_url": "url", "client_x509_cert_url": "url"}
# SPREADSHEET_ID = "your_spreadsheet_id"
# WORKSHEET_NAME = "your_worksheet_name" 