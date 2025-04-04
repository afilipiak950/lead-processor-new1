# Lead Processor Deployment

Dieses Verzeichnis enthält alle notwendigen Dateien für das Deployment des Lead Processors auf lovable.dev.

## Verzeichnisstruktur

```
deployment/
├── frontend/
│   ├── app.py                 # Streamlit Frontend-Anwendung
│   ├── requirements.txt       # Python-Abhängigkeiten
│   ├── Dockerfile            # Docker-Konfiguration für Frontend
│   ├── .dockerignore         # Docker-Ignore-Datei
│   └── .env.production       # Produktions-Umgebungsvariablen
└── docker-compose.yml        # Docker Compose Konfiguration
```

## Deployment auf lovable.dev

1. Erstellen Sie ein neues Repository auf GitHub
2. Pushen Sie den Inhalt dieses Verzeichnisses in das Repository
3. Gehen Sie zu [lovable.dev](https://lovable.dev)
4. Verbinden Sie Ihr GitHub-Repository
5. Wählen Sie die `docker-compose.yml` als Deployment-Konfiguration
6. Setzen Sie die folgenden Umgebungsvariablen in den lovable.dev Einstellungen:

### Erforderliche Umgebungsvariablen

- `OPENAI_API_KEY`: Ihr OpenAI API-Schlüssel
- `APIFY_API_KEY`: Ihr Apify API-Schlüssel
- `APIFY_ACTOR_ID`: Die ID Ihres Apify Actors
- `SPREADSHEET_ID`: Die ID Ihres Google Sheets
- `EMAIL_USERNAME`: Ihre Gmail-Adresse
- `EMAIL_PASSWORD`: Ihr Gmail App-Passwort

### Optionale Umgebungsvariablen

- `SMTP_SERVER`: SMTP-Server (Standard: smtp.gmail.com)
- `SMTP_PORT`: SMTP-Port (Standard: 587)
- `SELENIUM_TIMEOUT`: Timeout für Selenium (Standard: 30)
- `API_TIMEOUT`: Timeout für API-Aufrufe (Standard: 60)
- `MAX_RETRIES`: Maximale Anzahl von Wiederholungsversuchen (Standard: 3)
- `RETRY_DELAY`: Verzögerung zwischen Wiederholungsversuchen (Standard: 5)

## Wichtige Hinweise

1. Stellen Sie sicher, dass die `credentials.json` für Google Sheets im Hauptverzeichnis vorhanden ist
2. Die Anwendung läuft auf Port 8501
3. Healthchecks sind alle 30 Sekunden konfiguriert
4. Automatische Neustarts sind bei Fehlern aktiviert

## Fehlerbehebung

1. Überprüfen Sie die Logs in lovable.dev
2. Stellen Sie sicher, dass alle Umgebungsvariablen korrekt gesetzt sind
3. Überprüfen Sie die Google Sheets-Berechtigungen
4. Testen Sie die E-Mail-Konfiguration lokal vor dem Deployment 