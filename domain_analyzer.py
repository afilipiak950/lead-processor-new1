from typing import Dict
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import *

class DomainAnalyzer:
    def __init__(self):
        self.setup_selenium()
        
    def setup_selenium(self):
        """Richtet Selenium für das Web-Scraping ein"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"user-agent={USER_AGENT}")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
    def analyze_domain(self, domain: str) -> Dict:
        """Analysiert eine Unternehmenswebsite"""
        try:
            # Versuche zuerst mit requests
            response = requests.get(f"https://{domain}", headers={"User-Agent": USER_AGENT})
            soup = BeautifulSoup(response.text, 'html.parser')
        except:
            # Fallback auf Selenium
            self.driver.get(f"https://{domain}")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
        # Extrahiere grundlegende Informationen
        title = soup.title.string if soup.title else ""
        meta_description = soup.find("meta", {"name": "description"})
        description = meta_description["content"] if meta_description else ""
        
        # Extrahiere weitere relevante Informationen
        about_section = self._find_about_section(soup)
        services = self._find_services(soup)
        contact_info = self._find_contact_info(soup)
        
        return {
            "title": title,
            "description": description,
            "about": about_section,
            "services": services,
            "contact": contact_info,
            "url": domain
        }
        
    def _find_about_section(self, soup: BeautifulSoup) -> str:
        """Findet den About/Über uns Abschnitt"""
        # Suche nach typischen About-Sektionen
        about_selectors = [
            "about", "über-uns", "about-us", "company", "unternehmen",
            "who-we-are", "our-story", "geschichte"
        ]
        
        for selector in about_selectors:
            element = soup.find(id=selector) or soup.find(class_=selector)
            if element:
                return element.get_text(strip=True)
                
        return ""
        
    def _find_services(self, soup: BeautifulSoup) -> list:
        """Findet die angebotenen Services/Leistungen"""
        services = []
        service_selectors = [
            "services", "leistungen", "products", "produkte",
            "solutions", "lösungen", "portfolio"
        ]
        
        for selector in service_selectors:
            elements = soup.find_all(class_=selector)
            for element in elements:
                services.extend([li.get_text(strip=True) for li in element.find_all("li")])
                
        return list(set(services))  # Entferne Duplikate
        
    def _find_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Findet Kontaktinformationen"""
        contact_info = {
            "email": "",
            "phone": "",
            "address": ""
        }
        
        # Suche nach E-Mail
        email_elements = soup.find_all("a", href=lambda x: x and "mailto:" in x)
        if email_elements:
            contact_info["email"] = email_elements[0].get("href").replace("mailto:", "")
            
        # Suche nach Telefon
        phone_elements = soup.find_all("a", href=lambda x: x and "tel:" in x)
        if phone_elements:
            contact_info["phone"] = phone_elements[0].get("href").replace("tel:", "")
            
        # Suche nach Adresse
        address_elements = soup.find_all(class_=["address", "contact-address"])
        if address_elements:
            contact_info["address"] = address_elements[0].get_text(strip=True)
            
        return contact_info
        
    def __del__(self):
        """Cleanup beim Beenden"""
        if hasattr(self, 'driver'):
            self.driver.quit() 