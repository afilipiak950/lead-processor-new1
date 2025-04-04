# KI-gestützter Lead-Prozessor

Dieses Projekt implementiert einen KI-gestützten Lead-Prozessor, der:
- Leads von Apify abruft
- Unternehmens- und LinkedIn-Informationen extrahiert
- Den Kommunikationsstil analysiert
- Personalisierte E-Mails generiert und versendet
- Alle Informationen in Google Sheets speichert

## Installation

1. Klonen Sie das Repository
2. Installieren Sie die Abhängigkeiten:
```bash
pip install -r requirements.txt
```

## Konfiguration

Erstellen Sie eine `.env` Datei im Hauptverzeichnis mit folgenden Variablen:

```env
OPENAI_API_KEY=your_openai_api_key
APIFY_API_KEY=your_apify_api_key
SPREADSHEET_ID=your_google_spreadsheet_id
EMAIL_USERNAME=your_email
EMAIL_PASSWORD=your_email_password
```

### Google Sheets Setup

1. Gehen Sie zur [Google Cloud Console](https://console.cloud.google.com)
2. Erstellen Sie ein neues Projekt
3. Aktivieren Sie die Google Sheets API
4. Erstellen Sie OAuth 2.0 Credentials
5. Laden Sie die Credentials als `credentials.json` herunter und platzieren Sie sie im Projektverzeichnis

### Apify Setup

1. Erstellen Sie einen [Apify](https://apify.com) Account
2. Erstellen Sie einen Actor für das Lead-Scraping
3. Notieren Sie sich die Actor-ID und API-Key

## Verwendung

Starten Sie den Lead-Prozessor mit:

```bash
python main.py
```

Der Prozessor wird:
1. Leads von Apify abrufen
2. Für jeden Lead:
   - Unternehmenswebsite analysieren
   - LinkedIn-Profil extrahieren
   - Kommunikationsstil analysieren
   - Personalisierte E-Mail generieren
   - E-Mail versenden
   - Daten in Google Sheets speichern

## Projektstruktur

- `main.py`: Hauptanwendung mit LangGraph-Workflow
- `lead_processor.py`: Lead-Verarbeitung und E-Mail-Generierung
- `sheets_manager.py`: Google Sheets Integration
- `config.py`: Konfigurationsdatei

## Fehlerbehebung

- Stellen Sie sicher, dass alle API-Keys korrekt konfiguriert sind
- Überprüfen Sie die Google Sheets Berechtigungen
- Stellen Sie sicher, dass der Apify Actor korrekt konfiguriert ist
- Überprüfen Sie die E-Mail-Server-Einstellungen 