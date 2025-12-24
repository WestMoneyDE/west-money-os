#!/usr/bin/env python3
"""
WhatsApp Webhook Handler
Verarbeitet eingehende Nachrichten
"""

from flask import Blueprint, request, jsonify
import os
import hmac
import hashlib
import json
from datetime import datetime

whatsapp_webhook_bp = Blueprint('whatsapp_webhook', __name__)

VERIFY_TOKEN = os.getenv('WEBHOOK_SECRET', 'westmoney_webhook_2025')
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')

# Message Handlers
MESSAGE_HANDLERS = {
    '1': 'smart_home_info',
    '2': 'automation_inquiry',
    '3': 'pricing_info',
    '4': 'support_request',
    'hallo': 'welcome',
    'hi': 'welcome',
    'hilfe': 'help_menu',
    'help': 'help_menu',
    'termin': 'appointment',
    'preis': 'pricing_info',
    'angebot': 'quote_request',
}

RESPONSES = {
    'welcome': '''Willkommen bei West Money OS! 👋

Ich bin Ihr digitaler Assistent. Wie kann ich Ihnen helfen?

1️⃣ Smart Home Beratung
2️⃣ Automation Anfrage  
3️⃣ Preise & Angebote
4️⃣ Support

Antworten Sie einfach mit der Nummer oder schreiben Sie Ihre Frage.''',
    
    'help_menu': '''📋 *Hilfe-Menü*

Hier sind die verfügbaren Optionen:

• "termin" - Termin vereinbaren
• "preis" - Preisanfrage
• "angebot" - Angebot anfordern
• "support" - Technischer Support
• "mensch" - Mit einem Mitarbeiter sprechen

Oder beschreiben Sie einfach Ihr Anliegen!''',
    
    'smart_home_info': '''🏠 *Smart Home Lösungen*

Wir bieten professionelle Smart Home Integration:

• LOXONE Miniserver
• KNX Systeme
• ComfortClick Visualisierung
• Sprachsteuerung (Alexa, Google, Siri)
• Barrierefrei nach DIN 18040

💰 Preise ab €15.000 (Einfamilienhaus)

Möchten Sie eine kostenlose Beratung? Antworten Sie mit "termin"''',
    
    'pricing_info': '''💰 *Preisübersicht West Money Bau*

🏠 Smart Home Paket Basic: ab €15.000
🏠 Smart Home Paket Premium: ab €25.000
🏠 Komplett barrierefrei: ab €35.000

📱 West Money OS Software:
• Free: €0/Monat
• Starter: €29/Monat
• Professional: €99/Monat
• Enterprise: €299/Monat

Für ein individuelles Angebot antworten Sie mit "angebot"''',
    
    'appointment': '''📅 *Terminvereinbarung*

Wann passt es Ihnen am besten?

Mo-Fr: 09:00 - 17:00 Uhr
Sa: Nach Vereinbarung

Bitte nennen Sie mir:
1. Ihren Wunschtermin
2. Ihr Anliegen
3. Ihre Kontaktdaten

Ein Mitarbeiter wird sich umgehend bei Ihnen melden.''',
    
    'human_handoff': '''👤 *Weiterleitung an Mitarbeiter*

Ich verbinde Sie mit einem unserer Experten.

Geschäftszeiten: Mo-Fr 09:00-17:00 Uhr

Außerhalb der Geschäftszeiten hinterlassen Sie bitte eine Nachricht und wir melden uns schnellstmöglich.''',
    
    'default': '''Vielen Dank für Ihre Nachricht! 

Ich habe Ihre Anfrage erhalten und leite sie an einen Mitarbeiter weiter.

In der Zwischenzeit können Sie:
• "hilfe" eingeben für alle Optionen
• "termin" für eine Terminvereinbarung
• "preis" für Preisinformationen'''
}


@whatsapp_webhook_bp.route('/api/whatsapp/webhook', methods=['GET'])
def verify_webhook():
    """Webhook verification for Meta"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print(f"✅ Webhook verified!")
        return challenge, 200
    
    return 'Forbidden', 403


@whatsapp_webhook_bp.route('/api/whatsapp/webhook', methods=['POST'])
def receive_webhook():
    """Handle incoming WhatsApp messages"""
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'no data'}), 400
    
    # Process messages
    try:
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages', [])
                
                for message in messages:
                    process_message(message, value.get('contacts', []))
    except Exception as e:
        print(f"Error processing webhook: {e}")
    
    return jsonify({'status': 'ok'}), 200


def process_message(message, contacts):
    """Process a single incoming message"""
    msg_type = message.get('type')
    from_number = message.get('from')
    msg_id = message.get('id')
    timestamp = message.get('timestamp')
    
    # Get contact name
    contact_name = 'Unknown'
    if contacts:
        contact_name = contacts[0].get('profile', {}).get('name', 'Unknown')
    
    print(f"📩 Message from {contact_name} ({from_number})")
    
    # Handle text messages
    if msg_type == 'text':
        text = message.get('text', {}).get('body', '').lower().strip()
        response = get_response(text)
        send_reply(from_number, response)
    
    # Handle interactive (button) responses
    elif msg_type == 'interactive':
        interactive = message.get('interactive', {})
        if interactive.get('type') == 'button_reply':
            button_id = interactive.get('button_reply', {}).get('id')
            response = get_response(button_id)
            send_reply(from_number, response)
    
    # Handle other message types
    else:
        send_reply(from_number, RESPONSES['default'])


def get_response(text):
    """Get appropriate response for message"""
    text = text.lower().strip()
    
    # Check for exact matches
    if text in MESSAGE_HANDLERS:
        handler = MESSAGE_HANDLERS[text]
        return RESPONSES.get(handler, RESPONSES['default'])
    
    # Check for partial matches
    for keyword, handler in MESSAGE_HANDLERS.items():
        if keyword in text:
            return RESPONSES.get(handler, RESPONSES['default'])
    
    # Check for human handoff requests
    if any(word in text for word in ['mensch', 'mitarbeiter', 'agent', 'person']):
        return RESPONSES['human_handoff']
    
    return RESPONSES['default']


def send_reply(to_number, message):
    """Send reply via WhatsApp API"""
    import requests
    
    if not WHATSAPP_TOKEN or WHATSAPP_TOKEN.startswith('EAAG...'):
        print(f"⚠️ WhatsApp Token nicht konfiguriert")
        return
    
    phone_id = os.getenv('WHATSAPP_PHONE_ID', '')
    url = f'https://graph.facebook.com/v21.0/{phone_id}/messages'
    
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
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
        if response.status_code == 200:
            print(f"✅ Reply sent to {to_number}")
        else:
            print(f"❌ Failed to send: {response.text}")
    except Exception as e:
        print(f"❌ Error sending message: {e}")
