from dotenv import load_dotenv
import os
from ai_agent import get_leads_from_apify

# Lade Umgebungsvariablen
load_dotenv()

def test_apify_connection():
    print("Teste Apify-Verbindung...")
    print(f"API-Key vorhanden: {'APIFY_API_KEY' in os.environ}")
    print(f"Dataset-ID vorhanden: {'APIFY_DATASET_ID' in os.environ}")
    
    try:
        leads = get_leads_from_apify()
        if leads:
            print(f"\nErfolgreich {len(leads)} Leads abgerufen!")
            print("\nBeispiel-Lead:")
            print(leads[0] if leads else "Keine Leads gefunden")
        else:
            print("\nKeine Leads gefunden.")
    except Exception as e:
        print(f"\nFehler beim Abrufen der Leads: {str(e)}")

if __name__ == "__main__":
    test_apify_connection() 