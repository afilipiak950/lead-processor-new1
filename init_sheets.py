from sheets_manager import SheetsManager
import json

def init_sheets():
    """Initialisiert die Google Sheet mit den notwendigen Spalten"""
    sheets_manager = SheetsManager()
    
    # Definiere die Spaltenüberschriften
    headers = [
        "Email",
        "Name",
        "Company",
        "Domain",
        "LinkedIn URL",
        "Domain Info",
        "LinkedIn Info",
        "Communication Style",
        "Status"
    ]
    
    # Erstelle die Sheet mit den Überschriften
    values = [headers]
    body = {
        'values': values
    }
    
    try:
        result = sheets_manager.service.spreadsheets().values().update(
            spreadsheetId=sheets_manager.SPREADSHEET_ID,
            range=f'{sheets_manager.LEADS_SHEET_NAME}!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        print(f"Sheet erfolgreich initialisiert: {result.get('updatedCells')} Zellen aktualisiert")
    except Exception as e:
        print(f"Fehler bei der Initialisierung: {str(e)}")

if __name__ == "__main__":
    init_sheets() 