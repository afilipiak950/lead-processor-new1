from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langgraph.graph import Graph, StateGraph
from apify_client import ApifyClient
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from config import *
import logging
from time import sleep
from typing import Optional

class ApifyError(Exception):
    pass

class LeadProcessor:
    def __init__(self):
        self._validate_config()
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY)
        self.apify_client = ApifyClient(APIFY_API_KEY)
        self.setup_selenium()
        self.setup_logging()
        
    def _validate_config(self):
        """Überprüft, ob alle erforderlichen Konfigurationen vorhanden sind"""
        required_configs = {
            'OPENAI_API_KEY': OPENAI_API_KEY,
            'APIFY_API_KEY': APIFY_API_KEY,
            'APIFY_ACTOR_ID': APIFY_ACTOR_ID,
            'APIFY_DATASET_URL': APIFY_DATASET_URL
        }
        
        missing_configs = [key for key, value in required_configs.items() if not value]
        if missing_configs:
            raise ValueError(f"Fehlende Konfigurationen: {', '.join(missing_configs)}")
    
    def setup_logging(self):
        """Richtet das Logging ein"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_selenium(self):
        """Richtet Selenium mit verbesserten Optionen ein"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={USER_AGENT}")
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
        except Exception as e:
            self.logger.error(f"Fehler beim Einrichten von Selenium: {str(e)}")
            raise
        
    def fetch_leads_from_apify(self, max_retries: int = 3) -> List[Dict]:
        """Holt Leads von Apify mit Retry-Logik"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Versuche Leads von Apify zu holen (Versuch {attempt + 1}/{max_retries})")
                
                run_input = {
                    "startUrls": [{"url": "https://www.apollo.io"}],  # Beispiel-URL, wird durch den Actor überschrieben
                    "maxItems": 10
                }
                
                # Starte den Actor-Run
                run = self.apify_client.actor(APIFY_ACTOR_ID).call(run_input=run_input)
                self.logger.info(f"Apify Run gestartet mit ID: {run['id']}")
                
                # Warte auf die Fertigstellung des Runs
                while True:
                    run_info = self.apify_client.run(run["id"]).get()
                    if run_info["status"] == "SUCCEEDED":
                        break
                    elif run_info["status"] in ["FAILED", "ABORTED", "TIMED-OUT"]:
                        raise ApifyError(f"Apify Run fehlgeschlagen: {run_info['status']}")
                    self.logger.info(f"Warte auf Apify Run... Status: {run_info['status']}")
                    sleep(5)
                
                # Hole die Dataset-ID aus dem Run
                dataset_id = run_info["defaultDatasetId"]
                self.logger.info(f"Dataset ID gefunden: {dataset_id}")
                
                # Hole die Daten aus dem Dataset
                dataset = self.apify_client.dataset(dataset_id).list_items().items
                self.logger.info(f"Erfolgreich {len(dataset)} Leads von Apify geholt")
                return dataset
                
            except Exception as e:
                self.logger.error(f"Fehler beim Holen der Leads: {str(e)}")
                if attempt == max_retries - 1:
                    raise ApifyError(f"Konnte Leads nach {max_retries} Versuchen nicht holen: {str(e)}")
                sleep(2 ** attempt)  # Exponentielles Backoff
                
    def get_domain_info(self, domain: str, max_retries: int = 3) -> Dict:
        """Extrahiert Informationen von der Unternehmenswebsite mit Retry-Logik"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Versuche Domain-Info zu holen für {domain} (Versuch {attempt + 1}/{max_retries})")
                
                self.driver.get(f"https://{domain}")
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                title = soup.title.string if soup.title else ""
                meta_description = soup.find("meta", {"name": "description"})
                description = meta_description["content"] if meta_description else ""
                
                return {
                    "title": title,
                    "description": description,
                    "url": domain
                }
            except Exception as e:
                self.logger.error(f"Fehler beim Holen der Domain-Info: {str(e)}")
                if attempt == max_retries - 1:
                    return {"error": str(e)}
                sleep(2 ** attempt)
                
    def get_linkedin_info(self, linkedin_url: str, max_retries: int = 3) -> Dict:
        """Extrahiert Informationen vom LinkedIn-Profil mit Retry-Logik"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Versuche LinkedIn-Info zu holen für {linkedin_url} (Versuch {attempt + 1}/{max_retries})")
                
                self.driver.get(linkedin_url)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                name = soup.find("h1", {"class": "text-heading-xlarge"})
                name = name.text.strip() if name else ""
                
                headline = soup.find("div", {"class": "text-body-medium"})
                headline = headline.text.strip() if headline else ""
                
                return {
                    "name": name,
                    "headline": headline,
                    "url": linkedin_url
                }
            except Exception as e:
                self.logger.error(f"Fehler beim Holen der LinkedIn-Info: {str(e)}")
                if attempt == max_retries - 1:
                    return {"error": str(e)}
                sleep(2 ** attempt)
            
    def analyze_communication_style(self, lead_data: Dict) -> str:
        """Analysiert den Kommunikationsstil basierend auf den gesammelten Daten"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Du bist ein Experte für Kommunikationsanalyse. Analysiere die folgenden Informationen und bestimme den wahrscheinlichen Kommunikationsstil der Person."),
            ("user", "{lead_data}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"lead_data": json.dumps(lead_data, indent=2)})
        
    def generate_personalized_email(self, lead_data: Dict, communication_style: str) -> str:
        """Generiert eine personalisierte E-Mail basierend auf den Lead-Daten"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Du bist ein erfahrener Sales Copywriter. Schreibe eine hochpersonalisierte E-Mail basierend auf den Lead-Daten und dem Kommunikationsstil."),
            ("user", "Lead-Daten: {lead_data}\nKommunikationsstil: {communication_style}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({
            "lead_data": json.dumps(lead_data, indent=2),
            "communication_style": communication_style
        })
        
    def send_email(self, to_email: str, subject: str, body: str):
        """Sendet die generierte E-Mail"""
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
            
    def process_lead(self, lead: Dict) -> Dict:
        """Verarbeitet einen einzelnen Lead durch den gesamten Workflow"""
        # Hole Domain-Informationen
        domain_info = self.get_domain_info(lead.get("domain", ""))
        
        # Hole LinkedIn-Informationen
        linkedin_info = self.get_linkedin_info(lead.get("linkedin_url", ""))
        
        # Kombiniere alle Informationen
        lead_data = {
            **lead,
            "domain_info": domain_info,
            "linkedin_info": linkedin_info
        }
        
        # Analysiere Kommunikationsstil
        communication_style = self.analyze_communication_style(lead_data)
        
        # Generiere E-Mail
        email_content = self.generate_personalized_email(lead_data, communication_style)
        
        # Sende E-Mail
        self.send_email(
            lead.get("email", ""),
            "Personalisiertes Angebot für Sie",
            email_content
        )
        
        return {
            "lead_data": lead_data,
            "communication_style": communication_style,
            "email_sent": True
        }
        
    def __del__(self):
        """Cleanup beim Beenden"""
        if hasattr(self, 'driver'):
            self.driver.quit() 