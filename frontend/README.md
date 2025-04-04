# Lead Processor Dashboard

Ein Streamlit-Dashboard zur Verwaltung und Analyse von Leads mit KI-Unterstützung.

## Funktionen

- **Dashboard**: Übersicht über alle Leads mit Metriken und Diagrammen
- **Lead-Übersicht**: Detaillierte Ansicht und Filterung aller Leads
- **AI-Aktivitäten**: Anzeige der KI-Analysen und personalisierten Nachrichten
- **Einstellungen**: Konfiguration des AI-Agenten und Schedulers

## Installation

1. Klonen Sie das Repository:
   ```
   git clone https://github.com/yourusername/lead-processor.git
   cd lead-processor/frontend
   ```

2. Installieren Sie die Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```

3. Konfigurieren Sie die Umgebungsvariablen:
   - Kopieren Sie `.env.example` zu `.env`
   - Tragen Sie Ihre API-Schlüssel ein:
     - `OPENAI_API_KEY`: Ihr OpenAI API-Schlüssel
     - `APIFY_API_KEY`: Ihr Apify API-Schlüssel
     - `APIFY_DATASET_ID`: Ihre Apify Dataset-ID

## Verwendung

1. Starten Sie die App:
   ```
   streamlit run streamlit_app.py
   ```

2. Öffnen Sie die App in Ihrem Browser:
   ```
   http://localhost:8501
   ```

## Deployment auf Streamlit Cloud

1. Erstellen Sie ein Konto auf [Streamlit Cloud](https://streamlit.io/cloud)
2. Verbinden Sie Ihr GitHub-Repository
3. Konfigurieren Sie die Umgebungsvariablen in den Streamlit Cloud-Einstellungen
4. Deployen Sie die App mit der Hauptdatei `streamlit_app.py`

## AI-Agent

Der AI-Agent analysiert Leads automatisch:
- Scrapt Websites und LinkedIn-Profile
- Erstellt Zusammenfassungen der Inhalte
- Bestimmt den optimalen Kommunikationsstil
- Generiert personalisierte Nachrichten

## Scheduler

Der Scheduler führt täglich folgende Aufgaben aus:
- Ruft neue Leads von Apify ab
- Verarbeitet bis zu 50 Leads pro Tag
- Speichert die Analysen für spätere Verwendung

## Lizenz

MIT 