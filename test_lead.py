from lead_processor import LeadProcessor
from sheets_manager import SheetsManager
import json

def test_lead_processing():
    """Testet die Lead-Verarbeitung mit einem Beispiel-Lead"""
    # Erstelle einen Beispiel-Lead
    test_lead = {
        "email": "test@example.com",
        "name": "Test Person",
        "company": "Test Company",
        "domain": "example.com",
        "linkedin_url": "https://linkedin.com/in/testperson",
        "position": "CEO"
    }
    
    try:
        # Initialisiere die Komponenten
        lead_processor = LeadProcessor()
        sheets_manager = SheetsManager()
        
        # Verarbeite den Lead
        print("Verarbeite Test-Lead...")
        processed_lead = lead_processor.process_lead(test_lead)
        
        # Speichere in Google Sheets
        print("Speichere in Google Sheets...")
        sheets_manager.append_lead(processed_lead)
        
        print("Test erfolgreich abgeschlossen!")
        print("\nVerarbeiteter Lead:")
        print(json.dumps(processed_lead, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Fehler beim Test: {str(e)}")

if __name__ == "__main__":
    test_lead_processing() 