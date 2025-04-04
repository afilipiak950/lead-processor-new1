from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
import json
from config import *

class CommunicationAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY)
        
    def analyze_style(self, lead_data: Dict) -> Dict:
        """Analysiert den Kommunikationsstil basierend auf den Lead-Daten"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Du bist ein Experte für Kommunikationsanalyse. 
            Analysiere die folgenden Informationen und bestimme:
            1. Den Kommunikationsstil (formell/informell, direkt/indirekt, etc.)
            2. Die bevorzugte Kommunikationsweise
            3. Mögliche Interessengebiete
            4. Potenzielle Schmerzpunkte
            5. Passende Ansprache
            
            Formatiere die Antwort als JSON mit den folgenden Schlüsseln:
            - style: Hauptkommunikationsstil
            - tone: Tonfall
            - interests: Liste von Interessengebieten
            - pain_points: Liste von möglichen Schmerzpunkten
            - approach: Empfohlene Ansprache
            """),
            ("user", "{lead_data}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"lead_data": json.dumps(lead_data, indent=2)})
        
        try:
            return json.loads(result)
        except:
            return {
                "style": "unbekannt",
                "tone": "neutral",
                "interests": [],
                "pain_points": [],
                "approach": "standard"
            }
            
    def generate_personalization(self, lead_data: Dict, analysis: Dict) -> Dict:
        """Generiert personalisierte Inhalte basierend auf der Analyse"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generiere personalisierte Inhalte für die E-Mail basierend auf:
            1. Lead-Daten
            2. Kommunikationsanalyse
            3. Unternehmen und Position
            
            Formatiere die Antwort als JSON mit den folgenden Schlüsseln:
            - positive_observation: Positive Beobachtung über das Unternehmen/Profil
            - value_proposition: Personalisierter Wertversprechen
            - follow_up: Personalisierter Follow-Up Text
            - final_offer: Personalisiertes finales Angebot
            """),
            ("user", "Lead-Daten: {lead_data}\nAnalyse: {analysis}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({
            "lead_data": json.dumps(lead_data, indent=2),
            "analysis": json.dumps(analysis, indent=2)
        })
        
        try:
            return json.loads(result)
        except:
            return {
                "positive_observation": "Ihrem Unternehmen und Ihrem Profil",
                "value_proposition": "unserer Lösung",
                "follow_up": "unserem Angebot",
                "final_offer": "unserem Service"
            } 