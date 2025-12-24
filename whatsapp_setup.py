#!/usr/bin/env python3
"""
WhatsApp Business API Setup Script
Enterprise Universe GmbH - West Money OS
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

class WhatsAppSetup:
    """WhatsApp Business API Configuration"""
    
    def __init__(self):
        self.token = os.getenv('WHATSAPP_TOKEN', '')
        self.phone_id = os.getenv('WHATSAPP_PHONE_ID', '423598467493680')
        self.business_id = os.getenv('WHATSAPP_BUSINESS_ID', '412877065246901')
        self.api_version = 'v21.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
    
    def check_connection(self):
        """Test API connection"""
        if not self.token or self.token.startswith('EAAG...'):
            return {'success': False, 'error': 'WHATSAPP_TOKEN nicht konfiguriert'}
        
        url = f'{self.base_url}/{self.phone_id}'
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'phone_number': data.get('display_phone_number'),
                    'verified_name': data.get('verified_name'),
                    'quality_rating': data.get('quality_rating')
                }
            else:
                return {'success': False, 'error': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_message_templates(self):
        """Get available message templates"""
        if not self.token or self.token.startswith('EAAG...'):
            return []
        
        url = f'{self.base_url}/{self.business_id}/message_templates'
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except:
            return []
    
    def create_template(self, name, category, language, body):
        """Create a new message template"""
        url = f'{self.base_url}/{self.business_id}/message_templates'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'name': name,
            'category': category,  # MARKETING, UTILITY, AUTHENTICATION
            'language': language,
            'components': [
                {
                    'type': 'BODY',
                    'text': body
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def send_test_message(self, to_number, message):
        """Send a test message"""
        url = f'{self.base_url}/{self.phone_id}/messages'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to_number,
            'type': 'text',
            'text': {'body': message}
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()
        except Exception as e:
            return {'error': str(e)}


# Recommended Templates
RECOMMENDED_TEMPLATES = [
    {
        'name': 'welcome_message',
        'category': 'MARKETING',
        'language': 'de',
        'body': 'Willkommen bei West Money OS! 👋\n\nVielen Dank für Ihr Interesse an unseren Smart Home und Business-Lösungen.\n\nWie können wir Ihnen helfen?\n\n1️⃣ Smart Home Beratung\n2️⃣ Automation Anfrage\n3️⃣ Preise & Angebote\n4️⃣ Support'
    },
    {
        'name': 'appointment_confirmation',
        'category': 'UTILITY',
        'language': 'de',
        'body': 'Terminbestätigung ✅\n\nIhr Termin wurde bestätigt:\n📅 Datum: {{1}}\n⏰ Uhrzeit: {{2}}\n📍 Ort: {{3}}\n\nBei Fragen erreichen Sie uns unter +49 69 XXX XXX.\n\nIhr West Money Team'
    },
    {
        'name': 'invoice_reminder',
        'category': 'UTILITY',
        'language': 'de',
        'body': 'Zahlungserinnerung 📄\n\nSehr geehrte/r {{1}},\n\ndie Rechnung {{2}} über {{3}}€ ist noch offen.\n\nBitte überweisen Sie den Betrag bis {{4}}.\n\nFragen? Kontaktieren Sie uns gerne.\n\nEnterprise Universe GmbH'
    },
    {
        'name': 'lead_followup',
        'category': 'MARKETING',
        'language': 'de',
        'body': 'Hallo {{1}}! 👋\n\nVielen Dank für Ihr Interesse an {{2}}.\n\nHaben Sie noch Fragen zu unserem Angebot?\n\nIch stehe Ihnen gerne für ein kurzes Gespräch zur Verfügung.\n\nMit freundlichen Grüßen,\nIhr West Money Team'
    },
    {
        'name': 'auth_otp',
        'category': 'AUTHENTICATION',
        'language': 'de',
        'body': '🔐 Ihr Verifizierungscode: {{1}}\n\nDieser Code ist 10 Minuten gültig.\n\nTeilen Sie diesen Code niemals mit anderen.'
    }
]


if __name__ == '__main__':
    print("=" * 60)
    print("  WhatsApp Business API Setup")
    print("=" * 60)
    print()
    
    wa = WhatsAppSetup()
    
    # Check connection
    print("🔍 Prüfe Verbindung...")
    result = wa.check_connection()
    
    if result['success']:
        print(f"✅ Verbunden!")
        print(f"   Nummer: {result.get('phone_number')}")
        print(f"   Name: {result.get('verified_name')}")
        print(f"   Qualität: {result.get('quality_rating')}")
        
        print()
        print("📋 Vorhandene Templates:")
        templates = wa.get_message_templates()
        for t in templates[:5]:
            print(f"   • {t.get('name')} ({t.get('status')})")
    else:
        print(f"⚠️ Nicht verbunden: {result.get('error')}")
        print()
        print("📝 So richtest du WhatsApp Business API ein:")
        print()
        print("1. Gehe zu: https://business.facebook.com/")
        print("2. Erstelle eine App (Business Type)")
        print("3. Füge WhatsApp Produkt hinzu")
        print("4. Registriere eine Telefonnummer")
        print("5. Kopiere den Access Token")
        print("6. Trage ihn in .env ein als WHATSAPP_TOKEN")
        print()
        print("📋 Empfohlene Templates:")
        for t in RECOMMENDED_TEMPLATES:
            print(f"   • {t['name']} ({t['category']})")
