import os
import json
import time
import schedule
import threading
from datetime import datetime
import streamlit as st
from ai_agent import AIAgent, get_leads_from_apify, save_analyses, load_analyses

class LeadScheduler:
    def __init__(self, max_leads_per_day=50):
        """Initialisiert den Scheduler für die tägliche Lead-Verarbeitung."""
        self.max_leads_per_day = max_leads_per_day
        self.ai_agent = None
        self.is_running = False
        self.last_run = None
        self.analyses_file = "lead_analyses.json"
        self.processed_leads_file = "processed_leads.json"
        
        # Lade bereits verarbeitete Leads
        self.processed_leads = self._load_processed_leads()
    
    def _load_processed_leads(self):
        """Lädt die bereits verarbeiteten Leads."""
        try:
            if os.path.exists(self.processed_leads_file):
                with open(self.processed_leads_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            st.error(f"Fehler beim Laden der verarbeiteten Leads: {str(e)}")
            return []
    
    def _save_processed_leads(self):
        """Speichert die verarbeiteten Leads."""
        try:
            with open(self.processed_leads_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_leads, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Fehler beim Speichern der verarbeiteten Leads: {str(e)}")
            return False
    
    def process_daily_leads(self):
        """Verarbeitet die täglichen Leads."""
        if self.is_running:
            st.warning("Ein Prozess läuft bereits.")
            return
        
        self.is_running = True
        st.info("Starte die tägliche Lead-Verarbeitung...")
        
        try:
            # Initialisiere den AI-Agenten
            self.ai_agent = AIAgent()
            
            # Hole Leads von Apify
            leads = get_leads_from_apify()
            
            if not leads:
                st.warning("Keine Leads von Apify gefunden.")
                self.is_running = False
                return
            
            # Filtere bereits verarbeitete Leads
            new_leads = []
            for lead in leads:
                lead_id = f"{lead.get('name', '')}_{lead.get('company', '')}_{lead.get('email', '')}"
                if lead_id not in self.processed_leads:
                    new_leads.append(lead)
            
            if not new_leads:
                st.info("Keine neuen Leads zum Verarbeiten.")
                self.is_running = False
                return
            
            # Begrenze die Anzahl der Leads
            leads_to_process = new_leads[:self.max_leads_per_day]
            
            # Verarbeite die Leads
            analyses = self.ai_agent.process_leads(leads_to_process)
            
            # Lade bestehende Analysen
            existing_analyses = load_analyses(self.analyses_file)
            
            # Füge neue Analysen hinzu
            all_analyses = existing_analyses + analyses
            
            # Speichere alle Analysen
            save_analyses(all_analyses, self.analyses_file)
            
            # Aktualisiere die verarbeiteten Leads
            for lead in leads_to_process:
                lead_id = f"{lead.get('name', '')}_{lead.get('company', '')}_{lead.get('email', '')}"
                self.processed_leads.append(lead_id)
            
            # Speichere die verarbeiteten Leads
            self._save_processed_leads()
            
            # Aktualisiere den Zeitstempel der letzten Ausführung
            self.last_run = datetime.now()
            
            st.success(f"{len(leads_to_process)} Leads erfolgreich verarbeitet.")
        except Exception as e:
            st.error(f"Fehler bei der Lead-Verarbeitung: {str(e)}")
        finally:
            self.is_running = False
    
    def schedule_daily_run(self, time="09:00"):
        """Plant die tägliche Ausführung."""
        schedule.every().day.at(time).do(self.process_daily_leads)
        
        # Starte den Scheduler in einem separaten Thread
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        st.success(f"Tägliche Ausführung um {time} Uhr geplant.")
    
    def run_immediately(self):
        """Führt die Lead-Verarbeitung sofort aus."""
        self.process_daily_leads()
    
    def get_last_run(self):
        """Gibt den Zeitstempel der letzten Ausführung zurück."""
        return self.last_run
    
    def get_analyses(self):
        """Gibt alle Analysen zurück."""
        return load_analyses(self.analyses_file)
    
    def get_analysis_by_email(self, email):
        """Gibt die Analyse für eine bestimmte E-Mail-Adresse zurück."""
        analyses = self.get_analyses()
        for analysis in analyses:
            if analysis.get('email') == email:
                return analysis
        return None

# Singleton-Instanz
_scheduler = None

def get_scheduler(max_leads_per_day=50):
    """Gibt die Singleton-Instanz des Schedulers zurück."""
    global _scheduler
    if _scheduler is None:
        _scheduler = LeadScheduler(max_leads_per_day)
    return _scheduler 