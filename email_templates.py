from typing import Dict
import json

class EmailTemplates:
    @staticmethod
    def get_initial_email_template(lead_data: Dict, communication_style: str) -> str:
        """Generiert die initiale E-Mail basierend auf dem Lead und Kommunikationsstil"""
        template = """
Sehr geehrte(r) {name},

ich habe Ihr LinkedIn-Profil und die Website von {company} besucht und war beeindruckt von {positive_observation}.

Als {position} bei {company} verstehe ich die Herausforderungen, vor denen Sie stehen. Basierend auf Ihrem Kommunikationsstil und den Informationen, die ich gefunden habe, dachte ich, dass Sie an unserer Lösung interessiert sein könnten.

{personalized_value_proposition}

Ich würde gerne einen kurzen Anruf mit Ihnen vereinbaren, um zu besprechen, wie wir Ihnen helfen können.

Beste Grüße,
{Ihr Name}
{Position}
{Unternehmen}
"""
        return template

    @staticmethod
    def get_follow_up_template(lead_data: Dict, communication_style: str, days: int) -> str:
        """Generiert eine Follow-Up E-Mail"""
        template = """
Sehr geehrte(r) {name},

ich habe mich vor {days} Tagen bei Ihnen gemeldet und wollte nachfragen, ob Sie Interesse an einem kurzen Gespräch haben.

{personalized_reminder}

Ich stehe Ihnen gerne für weitere Informationen zur Verfügung.

Beste Grüße,
{Ihr Name}
{Position}
{Unternehmen}
"""
        return template

    @staticmethod
    def get_final_template(lead_data: Dict, communication_style: str) -> str:
        """Generiert eine finale E-Mail"""
        template = """
Sehr geehrte(r) {name},

da ich bisher keine Rückmeldung von Ihnen erhalten habe, möchte ich Ihnen eine letzte Nachricht senden.

{final_offer}

Falls Sie in Zukunft Interesse haben, können Sie sich jederzeit bei mir melden.

Beste Grüße,
{Ihr Name}
{Position}
{Unternehmen}
"""
        return template 