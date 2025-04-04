"""
Konfigurationsdatei für alle AI-Prompts und Modelleinstellungen
"""

# OpenAI Modell-Konfiguration
OPENAI_MODEL = "gpt-4-turbo-preview"  # Kann zu anderen Modellen geändert werden, z.B. "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.7

# Prompts für Website-Scraping
WEBSITE_ANALYSIS_PROMPT = """
Analysiere die folgende Website und extrahiere die wichtigsten Informationen:
- Hauptgeschäftsfeld und Branche
- Produkte oder Dienstleistungen
- Unternehmensgröße und Standort (falls verfügbar)
- Besondere Merkmale oder USPs
- Aktuelle Herausforderungen oder Wachstumsbereiche

Fasse die Informationen in 2-3 prägnanten Sätzen zusammen.
"""

# Prompts für LinkedIn-Scraping
LINKEDIN_ANALYSIS_PROMPT = """
Analysiere das LinkedIn-Profil und extrahiere die wichtigsten Informationen:
- Aktuelle Position und Verantwortlichkeiten
- Beruflicher Werdegang
- Ausbildung und Qualifikationen
- Interessen und Aktivitäten
- Gemeinsame Verbindungen oder Interessen

Fasse die Informationen in 2-3 prägnanten Sätzen zusammen.
"""

# Prompt für die Nachrichtengenerierung
MESSAGE_GENERATION_PROMPT = """
Erstelle eine personalisierte Nachricht basierend auf den folgenden Informationen:
- Website-Analyse: {website_summary}
- LinkedIn-Analyse: {linkedin_summary}
- Kommunikationsstil: {communication_style}

Die Nachricht sollte:
1. Persönlich und authentisch sein
2. Sich auf spezifische Details aus der Analyse beziehen
3. Einen klaren Mehrwert für den Empfänger bieten
4. Eine konkrete nächste Aktion vorschlagen
5. Im angegebenen Kommunikationsstil (formal/informal) verfasst sein

Maximale Länge: 150 Wörter
"""

# Systemkontext für das AI-Modell
SYSTEM_CONTEXT = """
Du bist ein erfahrener Business Development Manager bei Amplifa, 
einem führenden Unternehmen für digitales Marketing und Lead-Generierung. 
Deine Aufgabe ist es, potenzielle Kunden zu analysieren und 
personalisierte Nachrichten zu erstellen, die authentisch und 
wertvoll für den Empfänger sind.
""" 