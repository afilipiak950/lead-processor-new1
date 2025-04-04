from typing import Dict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import *

class LinkedInAnalyzer:
    def __init__(self):
        self.setup_selenium()
        
    def setup_selenium(self):
        """Richtet Selenium für das LinkedIn-Scraping ein"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"user-agent={USER_AGENT}")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
    def analyze_profile(self, linkedin_url: str) -> Dict:
        """Analysiert ein LinkedIn-Profil"""
        try:
            self.driver.get(linkedin_url)
            
            # Warte auf das Laden der wichtigsten Elemente
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "text-heading-xlarge"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extrahiere grundlegende Informationen
            name = self._get_name(soup)
            headline = self._get_headline(soup)
            about = self._get_about(soup)
            experience = self._get_experience(soup)
            education = self._get_education(soup)
            skills = self._get_skills(soup)
            
            return {
                "name": name,
                "headline": headline,
                "about": about,
                "experience": experience,
                "education": education,
                "skills": skills,
                "url": linkedin_url
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "url": linkedin_url
            }
            
    def _get_name(self, soup: BeautifulSoup) -> str:
        """Extrahiert den Namen"""
        name_element = soup.find("h1", {"class": "text-heading-xlarge"})
        return name_element.text.strip() if name_element else ""
        
    def _get_headline(self, soup: BeautifulSoup) -> str:
        """Extrahiert die Headline"""
        headline_element = soup.find("div", {"class": "text-body-medium"})
        return headline_element.text.strip() if headline_element else ""
        
    def _get_about(self, soup: BeautifulSoup) -> str:
        """Extrahiert den About-Text"""
        about_element = soup.find("div", {"id": "about"})
        return about_element.text.strip() if about_element else ""
        
    def _get_experience(self, soup: BeautifulSoup) -> list:
        """Extrahiert die Berufserfahrung"""
        experience = []
        experience_section = soup.find("section", {"id": "experience"})
        
        if experience_section:
            for exp in experience_section.find_all("li", {"class": "experience-item"}):
                title = exp.find("h3", {"class": "title"})
                company = exp.find("p", {"class": "company"})
                duration = exp.find("p", {"class": "duration"})
                
                if title and company:
                    experience.append({
                        "title": title.text.strip(),
                        "company": company.text.strip(),
                        "duration": duration.text.strip() if duration else ""
                    })
                    
        return experience
        
    def _get_education(self, soup: BeautifulSoup) -> list:
        """Extrahiert die Ausbildung"""
        education = []
        education_section = soup.find("section", {"id": "education"})
        
        if education_section:
            for edu in education_section.find_all("li", {"class": "education-item"}):
                school = edu.find("h3", {"class": "school"})
                degree = edu.find("p", {"class": "degree"})
                field = edu.find("p", {"class": "field"})
                
                if school:
                    education.append({
                        "school": school.text.strip(),
                        "degree": degree.text.strip() if degree else "",
                        "field": field.text.strip() if field else ""
                    })
                    
        return education
        
    def _get_skills(self, soup: BeautifulSoup) -> list:
        """Extrahiert die Skills"""
        skills = []
        skills_section = soup.find("section", {"id": "skills"})
        
        if skills_section:
            for skill in skills_section.find_all("li", {"class": "skill-item"}):
                skills.append(skill.text.strip())
                
        return skills
        
    def __del__(self):
        """Cleanup beim Beenden"""
        if hasattr(self, 'driver'):
            self.driver.quit() 