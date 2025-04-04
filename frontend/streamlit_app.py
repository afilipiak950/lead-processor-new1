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