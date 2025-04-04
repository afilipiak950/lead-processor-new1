import argparse
import schedule
import time
from datetime import datetime
from logger import logger
from lead_processor import LeadProcessor
from sheets_manager import SheetsManager
from scheduler import Scheduler
from init_sheets import init_sheets

def process_leads():
    """Verarbeitet neue Leads und plant Follow-Ups"""
    try:
        # Initialisiere Komponenten
        lead_processor = LeadProcessor()
        sheets_manager = SheetsManager()
        scheduler = Scheduler()
        
        # Hole neue Leads von Apify
        logger.info("Hole neue Leads von Apify...")
        leads = lead_processor.fetch_leads_from_apify()
        
        if not leads:
            logger.info("Keine neuen Leads gefunden")
            return
            
        logger.info(f"{len(leads)} neue Leads gefunden")
        
        # Verarbeite jeden Lead
        for lead in leads:
            try:
                # Verarbeite den Lead
                logger.info(f"Verarbeite Lead: {lead.get('email', '')}")
                processed_lead = lead_processor.process_lead(lead)
                
                # Speichere in Google Sheets
                sheets_manager.append_lead(processed_lead)
                
                # Plane Follow-Ups
                scheduled_emails = scheduler.add_to_schedule(
                    processed_lead,
                    processed_lead.get('personalization', {})
                )
                
                logger.info(f"Lead erfolgreich verarbeitet: {lead.get('email', '')}")
                
            except Exception as e:
                logger.error(f"Fehler bei der Verarbeitung des Leads {lead.get('email', '')}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Fehler bei der Lead-Verarbeitung: {str(e)}")
        
def process_scheduled_emails():
    """Verarbeitet geplante E-Mails"""
    try:
        scheduler = Scheduler()
        scheduler.process_scheduled_emails()
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung der geplanten E-Mails: {str(e)}")
        
def main():
    parser = argparse.ArgumentParser(description="KI-gestützter Lead-Prozessor")
    parser.add_argument('--init', action='store_true', help="Initialisiere Google Sheets")
    parser.add_argument('--test', action='store_true', help="Führe einen Testlauf durch")
    args = parser.parse_args()
    
    if args.init:
        logger.info("Initialisiere Google Sheets...")
        init_sheets()
        return
        
    if args.test:
        from test_lead import test_lead_processing
        logger.info("Führe Testlauf durch...")
        test_lead_processing()
        return
        
    # Plane regelmäßige Ausführung
    schedule.every(1).hours.do(process_leads)
    schedule.every(15).minutes.do(process_scheduled_emails)
    
    logger.info("Starte Lead-Prozessor...")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Beende Lead-Prozessor...")
            break
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {str(e)}")
            time.sleep(300)  # Warte 5 Minuten bei Fehler
            
if __name__ == "__main__":
    main() 