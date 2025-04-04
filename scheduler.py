from typing import Dict, List
import json
from datetime import datetime
import os
from logger import logger
from email_manager import EmailManager
from sheets_manager import SheetsManager

class Scheduler:
    def __init__(self):
        self.email_manager = EmailManager()
        self.sheets_manager = SheetsManager()
        self.schedule_file = "scheduled_emails.json"
        self.load_schedule()
        
    def load_schedule(self):
        """Lädt den E-Mail-Zeitplan"""
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                self.schedule = json.load(f)
        else:
            self.schedule = {}
            
    def save_schedule(self):
        """Speichert den E-Mail-Zeitplan"""
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(self.schedule, f, indent=2, ensure_ascii=False)
            
    def add_to_schedule(self, lead_data: Dict, scheduled_emails: Dict):
        """Fügt geplante E-Mails zum Zeitplan hinzu"""
        lead_id = lead_data.get('email', '')
        if lead_id not in self.schedule:
            self.schedule[lead_id] = {
                'lead_data': lead_data,
                'scheduled_emails': scheduled_emails,
                'status': 'active'
            }
            self.save_schedule()
            logger.info(f"Neue E-Mails für {lead_id} geplant")
            
    def process_scheduled_emails(self):
        """Verarbeitet fällige E-Mails"""
        today = datetime.now().strftime("%Y-%m-%d")
        processed_leads = []
        
        for lead_id, data in self.schedule.items():
            if data['status'] != 'active':
                continue
                
            scheduled_emails = data['scheduled_emails']
            lead_data = data['lead_data']
            
            for date, email_data in scheduled_emails.items():
                if date == today:
                    success = self._send_scheduled_email(lead_data, email_data)
                    if success:
                        processed_leads.append(lead_id)
                        
        # Aktualisiere den Status der verarbeiteten Leads
        for lead_id in processed_leads:
            if lead_id in self.schedule:
                self.schedule[lead_id]['status'] = 'processed'
                
        self.save_schedule()
        
    def _send_scheduled_email(self, lead_data: Dict, email_data: Dict) -> bool:
        """Sendet eine geplante E-Mail"""
        try:
            if email_data['type'] == 'follow_up':
                success = self.email_manager.send_follow_up(
                    lead_data,
                    email_data['personalization'],
                    email_data['days']
                )
            elif email_data['type'] == 'final':
                success = self.email_manager.send_final_email(
                    lead_data,
                    email_data['personalization']
                )
            else:
                success = False
                
            if success:
                # Aktualisiere den Status in Google Sheets
                self.sheets_manager.update_lead_status(
                    lead_data.get('email', ''),
                    f"Follow-up gesendet: {email_data['type']}"
                )
                
            return success
            
        except Exception as e:
            logger.error(f"Fehler beim Senden der geplanten E-Mail: {str(e)}")
            return False
            
    def get_active_schedules(self) -> List[Dict]:
        """Gibt alle aktiven Zeitpläne zurück"""
        return [
            {
                'lead_id': lead_id,
                'lead_data': data['lead_data'],
                'scheduled_emails': data['scheduled_emails']
            }
            for lead_id, data in self.schedule.items()
            if data['status'] == 'active'
        ]
        
    def cancel_schedule(self, lead_id: str):
        """Storniert den Zeitplan für einen Lead"""
        if lead_id in self.schedule:
            self.schedule[lead_id]['status'] = 'cancelled'
            self.save_schedule()
            logger.info(f"Zeitplan für {lead_id} storniert") 