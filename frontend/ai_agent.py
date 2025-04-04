import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import streamlit as st

# Lade Umgebungsvariablen
load_dotenv()

# Definiere die Ausgabestruktur für den AI-Agenten
class LeadAnalysis(BaseModel):
    name: str = Field(description="Name des Leads")
    company: str = Field(description="Unternehmen des Leads")
    website_summary: str = Field(description="Zusammenfassung der Website-Inhalte")
    linkedin_summary: Optional[str] = Field(description="Zusammenfassung des LinkedIn-Profils, falls verfügbar")
    communication_style: str = Field(description="Empfohlener Kommunikationsstil (formal/informal)")
    personalized_message: str = Field(description="Personalisierte Nachricht für den Lead")
    status: str = Field(description="Status des Leads (aktiv/inaktiv/abgeschlossen)")

class AIAgent:
    def __init__(self, api_key: Optional[str] = None):
        """Initialisiert den AI-Agenten mit OpenAI API-Key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API-Key nicht gefunden. Bitte als Umgebungsvariable OPENAI_API_KEY setzen.")
        
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=self.api_key
        )
        
        self.parser = PydanticOutputParser(pydantic_object=LeadAnalysis)
        
        # Cache für Analysen
        self.analysis_cache = {}
    
    def scrape_website(self, url: str) -> str:
        """Scrapt eine Website und extrahiert den Text."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Entferne Skripte, Styles und andere nicht-relevante Elemente
            for script in soup(["script", "style", "meta", "link"]):
                script.decompose()
            
            # Extrahiere Text
            text = soup.get_text(separator=' ', strip=True)
            
            # Bereinige Text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:4000]  # Begrenze auf 4000 Zeichen
        except Exception as e:
            return f"Fehler beim Scrapen der Website: {str(e)}"
    
    def analyze_lead(self, lead: Dict) -> Dict:
        """Analysiert einen Lead mit LangChain und OpenAI."""
        # Prüfe Cache
        cache_key = f"{lead.get('name', '')}_{lead.get('company', '')}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        # Scrape Website
        website_url = lead.get('organization_website_url', '')
        website_content = self.scrape_website(website_url) if website_url else "Keine Website verfügbar"
        
        # Scrape LinkedIn
        linkedin_url = lead.get('linkedin_url', '')
        linkedin_content = self.scrape_website(linkedin_url) if linkedin_url else "Kein LinkedIn-Profil verfügbar"
        
        # Erstelle Prompt für den LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Du bist ein erfahrener Sales- und Marketing-Experte, der Leads analysiert und personalisierte Nachrichten erstellt.
            
            Analysiere die folgenden Informationen über einen Lead und erstelle eine personalisierte Nachricht.
            
            {format_instructions}
            """),
            ("human", """
            Name: {name}
            Unternehmen: {company}
            E-Mail: {email}
            Website-Inhalt: {website_content}
            LinkedIn-Inhalt: {linkedin_content}
            
            Bitte analysiere diese Informationen und erstelle eine personalisierte Nachricht.
            """)
        ])
        
        # Formatiere den Prompt
        formatted_prompt = prompt.format_messages(
            name=lead.get('name', 'Unbekannt'),
            company=lead.get('company', 'Unbekannt'),
            email=lead.get('email', 'Unbekannt'),
            website_content=website_content,
            linkedin_content=linkedin_content,
            format_instructions=self.parser.get_format_instructions()
        )
        
        # Rufe das LLM auf
        response = self.llm.invoke(formatted_prompt)
        
        # Parse die Antwort
        try:
            analysis = self.parser.parse(response.content)
            result = analysis.dict()
            
            # Füge Original-Lead-Daten hinzu
            result.update({
                'email': lead.get('email', ''),
                'website': lead.get('organization_website_url', ''),
                'linkedin': lead.get('linkedin_url', ''),
                'timestamp': datetime.now().isoformat()
            })
            
            # Speichere im Cache
            self.analysis_cache[cache_key] = result
            
            return result
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {str(e)}")
            return {
                'name': lead.get('name', 'Unbekannt'),
                'company': lead.get('company', 'Unbekannt'),
                'website_summary': "Fehler bei der Analyse",
                'linkedin_summary': "Fehler bei der Analyse",
                'communication_style': "formal",
                'personalized_message': "Fehler bei der Analyse",
                'status': "inaktiv",
                'email': lead.get('email', ''),
                'website': lead.get('organization_website_url', ''),
                'linkedin': lead.get('linkedin_url', ''),
                'timestamp': datetime.now().isoformat()
            }
    
    def process_leads(self, leads: List[Dict], max_leads: int = 50) -> List[Dict]:
        """Verarbeitet eine Liste von Leads und gibt Analysen zurück."""
        # Begrenze die Anzahl der Leads
        leads_to_process = leads[:max_leads]
        
        results = []
        for lead in leads_to_process:
            analysis = self.analyze_lead(lead)
            results.append(analysis)
            # Kurze Pause zwischen Anfragen
            time.sleep(1)
        
        return results

# Funktion zum Abrufen von Leads von Apify
def get_leads_from_apify(api_key: Optional[str] = None, dataset_id: Optional[str] = None) -> List[Dict]:
    """Ruft Leads von Apify ab."""
    try:
        # Verwende die direkte Dataset-URL
        url = "https://api.apify.com/v2/datasets/AGXiSRbH72qL6OFGs/items?token=apify_api_NOVzYHdbHojPZaa8HlulffsrqBE7Ka1M3y8G"
        
        response = requests.get(url)
        response.raise_for_status()
        leads = response.json()
        
        if not leads:
            st.warning("Keine Leads im Dataset gefunden.")
            return []
            
        st.success(f"{len(leads)} Leads erfolgreich abgerufen!")
        return leads
            
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Leads von Apify: {str(e)}")
        return []

# Funktion zum Speichern der Analysen
def save_analyses(analyses: List[Dict], filename: str = "lead_analyses.json"):
    """Speichert die Analysen in einer JSON-Datei."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analyses, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern der Analysen: {str(e)}")
        return False

# Funktion zum Laden der Analysen
def load_analyses(filename: str = "lead_analyses.json") -> List[Dict]:
    """Lädt die Analysen aus einer JSON-Datei."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Fehler beim Laden der Analysen: {str(e)}")
        return [] 