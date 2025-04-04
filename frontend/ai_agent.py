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
        website_url = lead.get('website', '')
        website_content = self.scrape_website(website_url) if website_url else "Keine Website verfügbar"
        
        # Scrape LinkedIn (vereinfacht)
        linkedin_url = lead.get('linkedin', '')
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
                'website': lead.get('website', ''),
                'linkedin': lead.get('linkedin', ''),
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
                'website': lead.get('website', ''),
                'linkedin': lead.get('linkedin', ''),
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
def get_leads_from_apify(api_key: Optional[str] = None, actor_id: Optional[str] = None) -> List[Dict]:
    """Ruft Leads von Apify ab."""
    apify_key = api_key or os.getenv("APIFY_API_KEY")
    apify_actor_id = actor_id or os.getenv("APIFY_ACTOR_ID")
    
    if not apify_key or not apify_actor_id:
        st.error("Apify API-Key oder Actor-ID nicht gefunden. Bitte als Umgebungsvariablen setzen.")
        return []
    
    try:
        # Apify API-Endpunkt für Actor
        url = f"https://api.apify.com/v2/actor-tasks/{apify_actor_id}/runs?token={apify_key}"
        
        # Starte einen neuen Run
        response = requests.post(url, json={
            "memory": 4096,
            "timeout": 300
        })
        response.raise_for_status()
        run_id = response.json()["data"]["id"]
        
        # Warte auf Abschluss und hole die Ergebnisse
        while True:
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={apify_key}"
            status_response = requests.get(status_url)
            status_response.raise_for_status()
            status = status_response.json()["data"]["status"]
            
            if status == "SUCCEEDED":
                # Hole die Ergebnisse
                results_url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={apify_key}"
                results_response = requests.get(results_url)
                results_response.raise_for_status()
                return results_response.json()
            elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                st.error(f"Apify Run fehlgeschlagen mit Status: {status}")
                return []
            
            time.sleep(5)  # Warte 5 Sekunden vor dem nächsten Check
            
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