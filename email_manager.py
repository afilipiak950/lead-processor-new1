from typing import Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
from config import *
from logger import logger

class EmailManager:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.username = EMAIL_USERNAME
        self.password = EMAIL_PASSWORD
        
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Sendet eine E-Mail"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                
            logger.info(f"E-Mail erfolgreich gesendet an {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Senden der E-Mail an {to_email}: {str(e)}")
            return False
            
    def send_initial_email(self, lead_data: Dict, personalization: Dict) -> bool:
        """Sendet die initiale E-Mail"""
        subject = f"Personalisiertes Angebot für {lead_data.get('name', '')}"
        
        # Hole die E-Mail-Vorlage
        from email_templates import EmailTemplates
        template = EmailTemplates.get_initial_email_template(lead_data, "")
        
        # Fülle die Vorlage
        body = template.format(
            name=lead_data.get('name', ''),
            company=lead_data.get('company', ''),
            position=lead_data.get('position', ''),
            positive_observation=personalization.get('positive_observation', ''),
            personalized_value_proposition=personalization.get('value_proposition', ''),
            Ihr Name="Ihr Name",  # Diese Werte sollten aus der Konfiguration kommen
            Position="Position",
            Unternehmen="Unternehmen"
        )
        
        return self.send_email(lead_data.get('email', ''), subject, body)
        
    def send_follow_up(self, lead_data: Dict, personalization: Dict, days: int) -> bool:
        """Sendet eine Follow-Up E-Mail"""
        subject = f"Nachfrage: Personalisiertes Angebot für {lead_data.get('name', '')}"
        
        # Hole die E-Mail-Vorlage
        from email_templates import EmailTemplates
        template = EmailTemplates.get_follow_up_template(lead_data, "", days)
        
        # Fülle die Vorlage
        body = template.format(
            name=lead_data.get('name', ''),
            days=days,
            personalized_reminder=personalization.get('follow_up', ''),
            Ihr Name="Ihr Name",
            Position="Position",
            Unternehmen="Unternehmen"
        )
        
        return self.send_email(lead_data.get('email', ''), subject, body)
        
    def send_final_email(self, lead_data: Dict, personalization: Dict) -> bool:
        """Sendet die finale E-Mail"""
        subject = f"Letzte Nachricht: Personalisiertes Angebot für {lead_data.get('name', '')}"
        
        # Hole die E-Mail-Vorlage
        from email_templates import EmailTemplates
        template = EmailTemplates.get_final_template(lead_data, "")
        
        # Fülle die Vorlage
        body = template.format(
            name=lead_data.get('name', ''),
            final_offer=personalization.get('final_offer', ''),
            Ihr Name="Ihr Name",
            Position="Position",
            Unternehmen="Unternehmen"
        )
        
        return self.send_email(lead_data.get('email', ''), subject, body)
        
    def schedule_follow_ups(self, lead_data: Dict, personalization: Dict) -> Dict:
        """Plant Follow-Up E-Mails"""
        follow_up_days = [3, 7, 14]  # Tage nach der initialen E-Mail
        scheduled_emails = {}
        
        for days in follow_up_days:
            scheduled_date = datetime.now() + timedelta(days=days)
            scheduled_emails[scheduled_date.strftime("%Y-%m-%d")] = {
                "type": "follow_up",
                "days": days,
                "personalization": personalization
            }
            
        # Füge finale E-Mail hinzu
        final_date = datetime.now() + timedelta(days=30)
        scheduled_emails[final_date.strftime("%Y-%m-%d")] = {
            "type": "final",
            "personalization": personalization
        }
        
        return scheduled_emails 