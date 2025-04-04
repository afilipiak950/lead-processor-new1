import os
from openai import OpenAI
from config.prompts import (
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    WEBSITE_ANALYSIS_PROMPT,
    LINKEDIN_ANALYSIS_PROMPT,
    MESSAGE_GENERATION_PROMPT,
    SYSTEM_CONTEXT
)
import logging

logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = OPENAI_MODEL
        self.temperature = OPENAI_TEMPERATURE
    
    def analyze_website(self, website_content):
        """Analysiert den Website-Content mit dem konfigurierten Prompt."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_CONTEXT},
                    {"role": "user", "content": WEBSITE_ANALYSIS_PROMPT + "\n\n" + website_content}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Fehler bei der Website-Analyse: {str(e)}")
            return "Keine Website-Analyse verfügbar"
    
    def analyze_linkedin(self, linkedin_content):
        """Analysiert den LinkedIn-Content mit dem konfigurierten Prompt."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_CONTEXT},
                    {"role": "user", "content": LINKEDIN_ANALYSIS_PROMPT + "\n\n" + linkedin_content}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Fehler bei der LinkedIn-Analyse: {str(e)}")
            return "Keine LinkedIn-Analyse verfügbar"
    
    def generate_message(self, website_summary, linkedin_summary, communication_style):
        """Generiert eine personalisierte Nachricht basierend auf den Analysen."""
        try:
            prompt = MESSAGE_GENERATION_PROMPT.format(
                website_summary=website_summary,
                linkedin_summary=linkedin_summary,
                communication_style=communication_style
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_CONTEXT},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Fehler bei der Nachrichtengenerierung: {str(e)}")
            return "Keine personalisierte Nachricht verfügbar"

# Funktionen für die Streamlit-App
def get_leads_from_apify():
    """Holt die Leads von Apify."""
    # Implementierung des Apify-Abrufs hier
    pass

def load_analyses():
    """Lädt die gespeicherten Analysen."""
    # Implementierung des Ladens der Analysen hier
    pass 