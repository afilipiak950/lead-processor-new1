from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import json
from config import *

class SheetsManager:
    def __init__(self):
        self.creds = None
        self.service = None
        self.setup_credentials()
        
    def setup_credentials(self):
        """Richtet die Google Sheets API Credentials ein"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_CREDENTIALS_FILE, SCOPES)
                self.creds = flow.run_local_server(port=0)
                
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
                
        self.service = build('sheets', 'v4', credentials=self.creds)
        
    def append_lead(self, lead_data: dict):
        """Fügt einen neuen Lead zur Google Sheet hinzu"""
        values = [
            [
                lead_data.get('email', ''),
                lead_data.get('name', ''),
                lead_data.get('company', ''),
                lead_data.get('domain', ''),
                lead_data.get('linkedin_url', ''),
                json.dumps(lead_data.get('domain_info', {})),
                json.dumps(lead_data.get('linkedin_info', {})),
                lead_data.get('communication_style', ''),
                'Sent' if lead_data.get('email_sent', False) else 'Pending'
            ]
        ]
        
        body = {
            'values': values
        }
        
        result = self.service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{LEADS_SHEET_NAME}!A:I',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return result
        
    def get_all_leads(self):
        """Holt alle Leads aus der Google Sheet"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{LEADS_SHEET_NAME}!A:I'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
            
        headers = values[0]
        leads = []
        
        for row in values[1:]:
            lead = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    if headers[i] in ['domain_info', 'linkedin_info']:
                        try:
                            lead[headers[i]] = json.loads(value)
                        except:
                            lead[headers[i]] = {}
                    else:
                        lead[headers[i]] = value
            leads.append(lead)
            
        return leads 