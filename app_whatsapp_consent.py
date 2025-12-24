"""
West Money OS v12.0 - WHATSAPP CONSENT & HUBSPOT SYNC
======================================================
WhatsApp Business API Integration mit HubSpot Consent Sync
Basierend auf: https://knowledge.hubspot.com/de/inbox/edit-the-whatsapp-consent-status-of-your-contacts-in-bulk
Enterprise Universe GmbH - 2025
"""

from flask import Blueprint, render_template_string, jsonify, request, session
import requests
import json
import os
from datetime import datetime
from functools import wraps

# ============================================================================
# BLUEPRINT
# ============================================================================
whatsapp_consent_bp = Blueprint('whatsapp_consent', __name__, url_prefix='/whatsapp-consent')

# ============================================================================
# CONFIGURATION
# ============================================================================
WHATSAPP_CONFIG = {
    "phone_number_id": os.environ.get("WHATSAPP_PHONE_ID", ""),
    "access_token": os.environ.get("WHATSAPP_TOKEN", ""),
    "business_account_id": os.environ.get("WHATSAPP_BUSINESS_ID", ""),
    "api_version": "v18.0",
    "webhook_verify_token": os.environ.get("WHATSAPP_VERIFY_TOKEN", "westmoney_verify_2025"),
}

HUBSPOT_CONFIG = {
    "api_key": os.environ.get("HUBSPOT_API_KEY", ""),
    "portal_id": os.environ.get("HUBSPOT_PORTAL_ID", ""),
    "base_url": "https://api.hubapi.com",
}

# WhatsApp Consent Status nach HubSpot Standard
CONSENT_STATUS = {
    "OPT_IN": "opted_in",           # Explizite Zustimmung
    "OPT_OUT": "opted_out",         # Explizite Ablehnung
    "NOT_SET": "not_set",           # Noch nicht festgelegt
    "PENDING": "pending",           # Warten auf Bestätigung
    "IMPLICIT": "implicit_consent"  # Implizite Zustimmung (z.B. durch Nachricht)
}

# ============================================================================
# WHATSAPP CLOUD API CLIENT
# ============================================================================
class WhatsAppClient:
    """WhatsApp Cloud API Client"""
    
    def __init__(self):
        self.phone_id = WHATSAPP_CONFIG["phone_number_id"]
        self.token = WHATSAPP_CONFIG["access_token"]
        self.version = WHATSAPP_CONFIG["api_version"]
        self.base_url = f"https://graph.facebook.com/{self.version}"
        
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def send_message(self, to, message_type="text", **kwargs):
        """Send WhatsApp message"""
        url = f"{self.base_url}/{self.phone_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": message_type
        }
        
        if message_type == "text":
            payload["text"] = {"body": kwargs.get("text", "")}
        elif message_type == "template":
            payload["template"] = {
                "name": kwargs.get("template_name"),
                "language": {"code": kwargs.get("language", "de")},
                "components": kwargs.get("components", [])
            }
        elif message_type == "interactive":
            payload["interactive"] = kwargs.get("interactive", {})
            
        try:
            response = requests.post(url, headers=self._headers(), json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def send_consent_request(self, to, contact_name=""):
        """Send WhatsApp consent/opt-in request"""
        interactive = {
            "type": "button",
            "header": {
                "type": "text",
                "text": "📱 WhatsApp Kommunikation"
            },
            "body": {
                "text": f"Hallo{' ' + contact_name if contact_name else ''}! 👋\n\nWir von West Money Bau möchten Sie gerne über WhatsApp kontaktieren, um Sie über:\n\n✅ Projektfortschritte\n✅ Termine & Angebote\n✅ Smart Home Updates\n\nzu informieren.\n\nMöchten Sie WhatsApp-Nachrichten von uns erhalten?"
            },
            "footer": {
                "text": "Sie können Ihre Einwilligung jederzeit widerrufen."
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "consent_yes",
                            "title": "✅ Ja, gerne!"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "consent_no",
                            "title": "❌ Nein, danke"
                        }
                    }
                ]
            }
        }
        
        return self.send_message(to, message_type="interactive", interactive=interactive)
    
    def get_phone_number_info(self):
        """Get registered phone number info"""
        url = f"{self.base_url}/{self.phone_id}"
        try:
            response = requests.get(url, headers=self._headers())
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_message_templates(self):
        """Get approved message templates"""
        url = f"{self.base_url}/{WHATSAPP_CONFIG['business_account_id']}/message_templates"
        try:
            response = requests.get(url, headers=self._headers())
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# ============================================================================
# HUBSPOT API CLIENT
# ============================================================================
class HubSpotClient:
    """HubSpot API Client für Contact & Consent Management"""
    
    def __init__(self):
        self.api_key = HUBSPOT_CONFIG["api_key"]
        self.base_url = HUBSPOT_CONFIG["base_url"]
        
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_contact(self, contact_id=None, email=None, phone=None):
        """Get contact by ID, email or phone"""
        if contact_id:
            url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
        elif email:
            url = f"{self.base_url}/crm/v3/objects/contacts/{email}?idProperty=email"
        elif phone:
            # Search by phone
            return self.search_contacts(f"phone:{phone}")
        else:
            return {"error": "contact_id, email or phone required"}
            
        try:
            response = requests.get(url, headers=self._headers())
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def search_contacts(self, query=None, filters=None, properties=None):
        """Search contacts with filters"""
        url = f"{self.base_url}/crm/v3/objects/contacts/search"
        
        payload = {
            "properties": properties or [
                "firstname", "lastname", "email", "phone", "mobilephone",
                "hs_whatsapp_phone_number", "hs_whatsapp_consent_status",
                "hs_whatsapp_consent_date", "company", "lifecyclestage"
            ],
            "limit": 100
        }
        
        if filters:
            payload["filterGroups"] = [{"filters": filters}]
        elif query:
            payload["query"] = query
            
        try:
            response = requests.post(url, headers=self._headers(), json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def update_contact(self, contact_id, properties):
        """Update contact properties"""
        url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
        
        try:
            response = requests.patch(url, headers=self._headers(), json={"properties": properties})
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def update_whatsapp_consent(self, contact_id, status, phone_number=None):
        """Update WhatsApp consent status for a contact"""
        properties = {
            "hs_whatsapp_consent_status": status,
            "hs_whatsapp_consent_date": datetime.now().isoformat()
        }
        
        if phone_number:
            # Format: +49XXXXXXXXXX
            formatted = phone_number.replace(" ", "").replace("-", "")
            if not formatted.startswith("+"):
                formatted = "+49" + formatted.lstrip("0")
            properties["hs_whatsapp_phone_number"] = formatted
            
        return self.update_contact(contact_id, properties)
    
    def bulk_update_consent(self, contact_updates):
        """Bulk update WhatsApp consent for multiple contacts
        
        Args:
            contact_updates: List of dicts with 'id', 'status', and optional 'phone'
        """
        url = f"{self.base_url}/crm/v3/objects/contacts/batch/update"
        
        inputs = []
        for update in contact_updates:
            properties = {
                "hs_whatsapp_consent_status": update["status"],
                "hs_whatsapp_consent_date": datetime.now().isoformat()
            }
            if update.get("phone"):
                properties["hs_whatsapp_phone_number"] = update["phone"]
                
            inputs.append({
                "id": update["id"],
                "properties": properties
            })
        
        try:
            response = requests.post(url, headers=self._headers(), json={"inputs": inputs})
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_contacts_by_consent_status(self, status):
        """Get all contacts with specific WhatsApp consent status"""
        filters = [{
            "propertyName": "hs_whatsapp_consent_status",
            "operator": "EQ",
            "value": status
        }]
        return self.search_contacts(filters=filters)
    
    def get_contacts_without_consent(self):
        """Get contacts without WhatsApp consent status set"""
        filters = [{
            "propertyName": "hs_whatsapp_consent_status",
            "operator": "NOT_HAS_PROPERTY"
        }]
        return self.search_contacts(filters=filters)
    
    def create_contact(self, properties):
        """Create new contact"""
        url = f"{self.base_url}/crm/v3/objects/contacts"
        
        try:
            response = requests.post(url, headers=self._headers(), json={"properties": properties})
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# ============================================================================
# CONSENT MANAGEMENT SERVICE
# ============================================================================
class ConsentManager:
    """Manages WhatsApp consent flow between WhatsApp and HubSpot"""
    
    def __init__(self):
        self.whatsapp = WhatsAppClient()
        self.hubspot = HubSpotClient()
        
    def request_consent(self, contact_id):
        """Send consent request to contact and update status to pending"""
        # Get contact from HubSpot
        contact = self.hubspot.get_contact(contact_id=contact_id)
        if "error" in contact:
            return contact
            
        props = contact.get("properties", {})
        phone = props.get("hs_whatsapp_phone_number") or props.get("mobilephone") or props.get("phone")
        name = props.get("firstname", "")
        
        if not phone:
            return {"error": "No phone number found for contact"}
            
        # Format phone number
        formatted_phone = phone.replace(" ", "").replace("-", "")
        if not formatted_phone.startswith("+"):
            formatted_phone = "+49" + formatted_phone.lstrip("0")
        
        # Send WhatsApp consent request
        wa_result = self.whatsapp.send_consent_request(formatted_phone.replace("+", ""), name)
        
        if "error" not in wa_result:
            # Update HubSpot to pending
            self.hubspot.update_whatsapp_consent(contact_id, CONSENT_STATUS["PENDING"], formatted_phone)
            
        return {
            "success": "error" not in wa_result,
            "whatsapp_result": wa_result,
            "contact_id": contact_id,
            "phone": formatted_phone
        }
    
    def process_consent_response(self, phone, response_id):
        """Process consent response from WhatsApp webhook"""
        # Find contact by phone
        search_result = self.hubspot.search_contacts(query=phone)
        
        if not search_result.get("results"):
            return {"error": "Contact not found"}
            
        contact = search_result["results"][0]
        contact_id = contact["id"]
        
        # Determine consent status based on response
        if response_id == "consent_yes":
            status = CONSENT_STATUS["OPT_IN"]
            # Send confirmation
            self.whatsapp.send_message(
                phone.replace("+", ""),
                text="✅ Vielen Dank! Sie erhalten ab jetzt WhatsApp-Nachrichten von West Money Bau. Sie können jederzeit 'STOP' schreiben, um sich abzumelden."
            )
        elif response_id == "consent_no":
            status = CONSENT_STATUS["OPT_OUT"]
            self.whatsapp.send_message(
                phone.replace("+", ""),
                text="👍 Verstanden! Wir werden Sie nicht über WhatsApp kontaktieren. Sie können Ihre Meinung jederzeit ändern."
            )
        else:
            return {"error": f"Unknown response: {response_id}"}
            
        # Update HubSpot
        result = self.hubspot.update_whatsapp_consent(contact_id, status)
        
        return {
            "success": True,
            "contact_id": contact_id,
            "status": status,
            "hubspot_result": result
        }
    
    def bulk_request_consent(self, contact_ids):
        """Send consent requests to multiple contacts"""
        results = []
        for contact_id in contact_ids:
            result = self.request_consent(contact_id)
            results.append(result)
        return results
    
    def sync_consent_from_hubspot(self):
        """Get all contacts with their consent status from HubSpot"""
        all_contacts = []
        
        for status_name, status_value in CONSENT_STATUS.items():
            contacts = self.hubspot.get_contacts_by_consent_status(status_value)
            if contacts.get("results"):
                for contact in contacts["results"]:
                    contact["consent_status"] = status_name
                    all_contacts.append(contact)
                    
        # Also get contacts without consent
        no_consent = self.hubspot.get_contacts_without_consent()
        if no_consent.get("results"):
            for contact in no_consent["results"]:
                contact["consent_status"] = "NOT_SET"
                all_contacts.append(contact)
                
        return all_contacts

# ============================================================================
# HTML TEMPLATE - CONSENT MANAGEMENT DASHBOARD
# ============================================================================
CONSENT_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 WhatsApp Consent Manager - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Rajdhani', sans-serif;
            background: linear-gradient(135deg, #0a0a15 0%, #1a0a2e 50%, #0a1628 100%);
            min-height: 100vh;
            color: #ffffff;
        }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid rgba(37, 211, 102, 0.3);
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.5rem;
            background: linear-gradient(90deg, #25d366, #128c7e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(145deg, rgba(37, 211, 102, 0.1), rgba(18, 140, 126, 0.05));
            border: 1px solid rgba(37, 211, 102, 0.3);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
        }
        
        .stat-card .icon { font-size: 2rem; margin-bottom: 10px; }
        .stat-card .number {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.5rem;
            color: #25d366;
        }
        .stat-card .label { color: #888; font-size: 0.9rem; }
        
        .action-bar {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1rem;
        }
        
        .btn-primary {
            background: linear-gradient(90deg, #25d366, #128c7e);
            color: #fff;
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn:hover { transform: scale(1.05); }
        
        .contacts-table {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            overflow: hidden;
        }
        
        .table-header {
            display: grid;
            grid-template-columns: 50px 1fr 1fr 150px 150px 150px;
            background: rgba(37, 211, 102, 0.1);
            padding: 15px 20px;
            font-weight: 700;
            color: #25d366;
        }
        
        .table-row {
            display: grid;
            grid-template-columns: 50px 1fr 1fr 150px 150px 150px;
            padding: 15px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            align-items: center;
            transition: background 0.3s ease;
        }
        
        .table-row:hover { background: rgba(37, 211, 102, 0.05); }
        
        .checkbox {
            width: 20px;
            height: 20px;
            accent-color: #25d366;
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
        
        .status-opted_in { background: rgba(37, 211, 102, 0.2); color: #25d366; }
        .status-opted_out { background: rgba(255, 68, 68, 0.2); color: #ff4444; }
        .status-pending { background: rgba(255, 170, 0, 0.2); color: #ffaa00; }
        .status-not_set { background: rgba(150, 150, 150, 0.2); color: #999; }
        
        .action-btn {
            padding: 8px 15px;
            border: none;
            border-radius: 15px;
            font-size: 0.85rem;
            cursor: pointer;
            background: rgba(37, 211, 102, 0.2);
            color: #25d366;
            transition: all 0.3s ease;
        }
        
        .action-btn:hover {
            background: #25d366;
            color: #000;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active { display: flex; }
        
        .modal-content {
            background: linear-gradient(145deg, #1a1a2e, #16213e);
            border: 1px solid rgba(37, 211, 102, 0.3);
            border-radius: 20px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
        }
        
        .modal h3 {
            font-family: 'Orbitron', sans-serif;
            color: #25d366;
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            color: #888;
            margin-bottom: 8px;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(37, 211, 102, 0.3);
            border-radius: 10px;
            color: #fff;
            font-size: 1rem;
        }
        
        .nav-back {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(37, 211, 102, 0.2);
            border: 1px solid #25d366;
            padding: 10px 20px;
            border-radius: 25px;
            color: #fff;
            text-decoration: none;
            font-weight: 600;
        }
        
        .nav-back:hover { background: #25d366; color: #000; }
        
        .config-section {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }
        
        .config-section h3 {
            color: #25d366;
            margin-bottom: 15px;
            font-family: 'Orbitron', sans-serif;
        }
        
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .config-item {
            background: rgba(37, 211, 102, 0.05);
            border: 1px solid rgba(37, 211, 102, 0.2);
            border-radius: 10px;
            padding: 15px;
        }
        
        .config-item label {
            display: block;
            color: #888;
            font-size: 0.85rem;
            margin-bottom: 5px;
        }
        
        .config-item input {
            width: 100%;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(37, 211, 102, 0.3);
            border-radius: 8px;
            padding: 10px;
            color: #fff;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        .status-connected {
            background: rgba(37, 211, 102, 0.2);
            color: #25d366;
        }
        
        .status-disconnected {
            background: rgba(255, 68, 68, 0.2);
            color: #ff4444;
        }
    </style>
</head>
<body>
    <a href="/dashboard" class="nav-back">← Dashboard</a>
    
    <div class="container">
        <div class="header">
            <h1>📱 WhatsApp Consent Manager</h1>
            <p style="color: #888; margin-top: 10px;">DSGVO-konformes Consent Management mit HubSpot Sync</p>
        </div>
        
        <!-- Connection Status -->
        <div class="config-section">
            <h3>🔗 Verbindungsstatus</h3>
            <div class="config-grid">
                <div class="config-item">
                    <label>WhatsApp Business API</label>
                    <div>
                        {% if whatsapp_connected %}
                        <span class="status-indicator status-connected">✅ Verbunden</span>
                        {% else %}
                        <span class="status-indicator status-disconnected">❌ Nicht konfiguriert</span>
                        {% endif %}
                    </div>
                </div>
                <div class="config-item">
                    <label>HubSpot CRM</label>
                    <div>
                        {% if hubspot_connected %}
                        <span class="status-indicator status-connected">✅ Verbunden</span>
                        {% else %}
                        <span class="status-indicator status-disconnected">❌ Nicht konfiguriert</span>
                        {% endif %}
                    </div>
                </div>
                <div class="config-item">
                    <label>Webhook Status</label>
                    <div>
                        <span class="status-indicator status-connected">✅ Aktiv</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">✅</div>
                <div class="number" id="stat-optin">{{ stats.opted_in }}</div>
                <div class="label">Opt-In</div>
            </div>
            <div class="stat-card">
                <div class="icon">❌</div>
                <div class="number" id="stat-optout">{{ stats.opted_out }}</div>
                <div class="label">Opt-Out</div>
            </div>
            <div class="stat-card">
                <div class="icon">⏳</div>
                <div class="number" id="stat-pending">{{ stats.pending }}</div>
                <div class="label">Ausstehend</div>
            </div>
            <div class="stat-card">
                <div class="icon">❓</div>
                <div class="number" id="stat-notset">{{ stats.not_set }}</div>
                <div class="label">Nicht gesetzt</div>
            </div>
        </div>
        
        <!-- Actions -->
        <div class="action-bar">
            <button class="btn btn-primary" onclick="openBulkModal()">
                📨 Bulk Consent-Anfrage senden
            </button>
            <button class="btn btn-secondary" onclick="syncFromHubSpot()">
                🔄 Mit HubSpot synchronisieren
            </button>
            <button class="btn btn-secondary" onclick="exportConsent()">
                📥 Export CSV
            </button>
            <button class="btn btn-secondary" onclick="openConfigModal()">
                ⚙️ API Konfiguration
            </button>
        </div>
        
        <!-- Contacts Table -->
        <div class="contacts-table">
            <div class="table-header">
                <div><input type="checkbox" class="checkbox" id="selectAll" onchange="toggleAll()"></div>
                <div>Name</div>
                <div>Telefon</div>
                <div>Status</div>
                <div>Datum</div>
                <div>Aktion</div>
            </div>
            <div id="contactsList">
                {% for contact in contacts %}
                <div class="table-row">
                    <div><input type="checkbox" class="checkbox contact-check" data-id="{{ contact.id }}"></div>
                    <div>{{ contact.properties.firstname }} {{ contact.properties.lastname }}</div>
                    <div>{{ contact.properties.hs_whatsapp_phone_number or contact.properties.phone or '-' }}</div>
                    <div>
                        <span class="status-badge status-{{ contact.consent_status|lower }}">
                            {{ contact.consent_status }}
                        </span>
                    </div>
                    <div>{{ contact.properties.hs_whatsapp_consent_date or '-' }}</div>
                    <div>
                        <button class="action-btn" onclick="sendConsentRequest('{{ contact.id }}')">
                            📨 Anfrage
                        </button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <!-- Bulk Modal -->
    <div class="modal" id="bulkModal">
        <div class="modal-content">
            <h3>📨 Bulk Consent-Anfrage</h3>
            <p style="color: #888; margin-bottom: 20px;">
                Senden Sie Consent-Anfragen an alle ausgewählten Kontakte.
            </p>
            <div class="form-group">
                <label>Zielgruppe</label>
                <select id="bulkTarget">
                    <option value="selected">Ausgewählte Kontakte</option>
                    <option value="not_set">Alle ohne Consent-Status</option>
                    <option value="pending">Alle mit Status "Pending"</option>
                </select>
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="btn btn-secondary" onclick="closeBulkModal()">Abbrechen</button>
                <button class="btn btn-primary" onclick="sendBulkConsent()">Senden</button>
            </div>
        </div>
    </div>
    
    <!-- Config Modal -->
    <div class="modal" id="configModal">
        <div class="modal-content">
            <h3>⚙️ API Konfiguration</h3>
            <div class="form-group">
                <label>WhatsApp Phone Number ID</label>
                <input type="text" id="waPhoneId" placeholder="Ihre Phone Number ID">
            </div>
            <div class="form-group">
                <label>WhatsApp Access Token</label>
                <input type="password" id="waToken" placeholder="Ihr Access Token">
            </div>
            <div class="form-group">
                <label>HubSpot API Key</label>
                <input type="password" id="hsApiKey" placeholder="Ihr HubSpot API Key">
            </div>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="btn btn-secondary" onclick="closeConfigModal()">Abbrechen</button>
                <button class="btn btn-primary" onclick="saveConfig()">Speichern</button>
            </div>
        </div>
    </div>
    
    <script>
        function openBulkModal() {
            document.getElementById('bulkModal').classList.add('active');
        }
        
        function closeBulkModal() {
            document.getElementById('bulkModal').classList.remove('active');
        }
        
        function openConfigModal() {
            document.getElementById('configModal').classList.add('active');
        }
        
        function closeConfigModal() {
            document.getElementById('configModal').classList.remove('active');
        }
        
        function toggleAll() {
            const selectAll = document.getElementById('selectAll');
            document.querySelectorAll('.contact-check').forEach(cb => {
                cb.checked = selectAll.checked;
            });
        }
        
        async function sendConsentRequest(contactId) {
            try {
                const response = await fetch('/whatsapp-consent/request', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({contact_id: contactId})
                });
                const data = await response.json();
                
                if (data.success) {
                    alert('✅ Consent-Anfrage gesendet!');
                    location.reload();
                } else {
                    alert('❌ Fehler: ' + (data.error || 'Unbekannter Fehler'));
                }
            } catch (error) {
                alert('❌ Fehler: ' + error.message);
            }
        }
        
        async function sendBulkConsent() {
            const target = document.getElementById('bulkTarget').value;
            let contactIds = [];
            
            if (target === 'selected') {
                document.querySelectorAll('.contact-check:checked').forEach(cb => {
                    contactIds.push(cb.dataset.id);
                });
            }
            
            if (contactIds.length === 0 && target === 'selected') {
                alert('Bitte wählen Sie mindestens einen Kontakt aus.');
                return;
            }
            
            try {
                const response = await fetch('/whatsapp-consent/bulk-request', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({contact_ids: contactIds, target: target})
                });
                const data = await response.json();
                
                alert(`✅ ${data.sent || 0} Anfragen gesendet!`);
                closeBulkModal();
                location.reload();
            } catch (error) {
                alert('❌ Fehler: ' + error.message);
            }
        }
        
        async function syncFromHubSpot() {
            try {
                const response = await fetch('/whatsapp-consent/sync');
                const data = await response.json();
                alert(`✅ ${data.contacts || 0} Kontakte synchronisiert!`);
                location.reload();
            } catch (error) {
                alert('❌ Fehler: ' + error.message);
            }
        }
        
        function exportConsent() {
            window.location.href = '/whatsapp-consent/export';
        }
        
        async function saveConfig() {
            const config = {
                whatsapp_phone_id: document.getElementById('waPhoneId').value,
                whatsapp_token: document.getElementById('waToken').value,
                hubspot_api_key: document.getElementById('hsApiKey').value
            };
            
            try {
                const response = await fetch('/whatsapp-consent/config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(config)
                });
                const data = await response.json();
                
                if (data.success) {
                    alert('✅ Konfiguration gespeichert!');
                    closeConfigModal();
                    location.reload();
                }
            } catch (error) {
                alert('❌ Fehler: ' + error.message);
            }
        }
    </script>
</body>
</html>
"""

# ============================================================================
# ROUTES
# ============================================================================

@whatsapp_consent_bp.route('/')
def consent_dashboard():
    """WhatsApp Consent Management Dashboard"""
    manager = ConsentManager()
    
    # Get contacts with consent info
    try:
        contacts = manager.sync_consent_from_hubspot()
    except:
        contacts = []
    
    # Calculate stats
    stats = {
        "opted_in": len([c for c in contacts if c.get("consent_status") == "OPT_IN"]),
        "opted_out": len([c for c in contacts if c.get("consent_status") == "OPT_OUT"]),
        "pending": len([c for c in contacts if c.get("consent_status") == "PENDING"]),
        "not_set": len([c for c in contacts if c.get("consent_status") == "NOT_SET"])
    }
    
    return render_template_string(
        CONSENT_DASHBOARD_HTML,
        contacts=contacts[:100],  # Limit for display
        stats=stats,
        whatsapp_connected=bool(WHATSAPP_CONFIG["access_token"]),
        hubspot_connected=bool(HUBSPOT_CONFIG["api_key"])
    )

@whatsapp_consent_bp.route('/request', methods=['POST'])
def request_consent():
    """Send consent request to single contact"""
    data = request.json
    contact_id = data.get('contact_id')
    
    if not contact_id:
        return jsonify({"error": "contact_id required"}), 400
        
    manager = ConsentManager()
    result = manager.request_consent(contact_id)
    
    return jsonify(result)

@whatsapp_consent_bp.route('/bulk-request', methods=['POST'])
def bulk_request_consent():
    """Send consent requests to multiple contacts"""
    data = request.json
    contact_ids = data.get('contact_ids', [])
    target = data.get('target', 'selected')
    
    manager = ConsentManager()
    
    if target == 'not_set':
        # Get all contacts without consent
        contacts = manager.hubspot.get_contacts_without_consent()
        contact_ids = [c["id"] for c in contacts.get("results", [])]
    elif target == 'pending':
        contacts = manager.hubspot.get_contacts_by_consent_status(CONSENT_STATUS["PENDING"])
        contact_ids = [c["id"] for c in contacts.get("results", [])]
    
    results = manager.bulk_request_consent(contact_ids)
    sent = len([r for r in results if r.get("success")])
    
    return jsonify({"sent": sent, "total": len(contact_ids), "results": results})

@whatsapp_consent_bp.route('/sync')
def sync_contacts():
    """Sync contacts from HubSpot"""
    manager = ConsentManager()
    contacts = manager.sync_consent_from_hubspot()
    
    return jsonify({"contacts": len(contacts), "data": contacts[:20]})

@whatsapp_consent_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """WhatsApp Webhook for receiving messages and consent responses"""
    if request.method == 'GET':
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == WHATSAPP_CONFIG["webhook_verify_token"]:
            return challenge, 200
        return 'Forbidden', 403
    
    # Handle incoming messages
    data = request.json
    
    if data.get('object') == 'whatsapp_business_account':
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # Handle interactive button responses
                for message in value.get('messages', []):
                    if message.get('type') == 'interactive':
                        interactive = message.get('interactive', {})
                        if interactive.get('type') == 'button_reply':
                            button_id = interactive.get('button_reply', {}).get('id')
                            phone = message.get('from')
                            
                            # Process consent response
                            manager = ConsentManager()
                            manager.process_consent_response(f"+{phone}", button_id)
    
    return jsonify({"status": "ok"})

@whatsapp_consent_bp.route('/update-status', methods=['POST'])
def update_status():
    """Manually update consent status"""
    data = request.json
    contact_id = data.get('contact_id')
    status = data.get('status')
    
    if not contact_id or not status:
        return jsonify({"error": "contact_id and status required"}), 400
        
    if status not in CONSENT_STATUS.values():
        return jsonify({"error": f"Invalid status. Must be one of: {list(CONSENT_STATUS.values())}"}), 400
    
    hubspot = HubSpotClient()
    result = hubspot.update_whatsapp_consent(contact_id, status)
    
    return jsonify(result)

@whatsapp_consent_bp.route('/bulk-update', methods=['POST'])
def bulk_update():
    """Bulk update consent status"""
    data = request.json
    updates = data.get('updates', [])  # List of {id, status}
    
    if not updates:
        return jsonify({"error": "updates array required"}), 400
    
    hubspot = HubSpotClient()
    result = hubspot.bulk_update_consent(updates)
    
    return jsonify(result)

@whatsapp_consent_bp.route('/export')
def export_consent():
    """Export consent data as CSV"""
    manager = ConsentManager()
    contacts = manager.sync_consent_from_hubspot()
    
    # Build CSV
    csv_lines = ["ID,Vorname,Nachname,Telefon,Status,Datum"]
    for c in contacts:
        props = c.get("properties", {})
        csv_lines.append(f"{c.get('id')},{props.get('firstname','')},{props.get('lastname','')},{props.get('hs_whatsapp_phone_number','')},{c.get('consent_status','')},{props.get('hs_whatsapp_consent_date','')}")
    
    csv_content = "\n".join(csv_lines)
    
    return csv_content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=whatsapp_consent_{datetime.now().strftime("%Y%m%d")}.csv'
    }

@whatsapp_consent_bp.route('/config', methods=['GET', 'POST'])
def api_config():
    """Get or update API configuration"""
    if request.method == 'GET':
        return jsonify({
            "whatsapp_configured": bool(WHATSAPP_CONFIG["access_token"]),
            "hubspot_configured": bool(HUBSPOT_CONFIG["api_key"]),
            "webhook_url": f"{request.host_url}whatsapp-consent/webhook"
        })
    
    # POST - Update config (in real app, save to secure storage)
    data = request.json
    
    if data.get('whatsapp_phone_id'):
        WHATSAPP_CONFIG["phone_number_id"] = data['whatsapp_phone_id']
    if data.get('whatsapp_token'):
        WHATSAPP_CONFIG["access_token"] = data['whatsapp_token']
    if data.get('hubspot_api_key'):
        HUBSPOT_CONFIG["api_key"] = data['hubspot_api_key']
    
    return jsonify({"success": True})

# ============================================================================
# EXPORT
# ============================================================================
__all__ = [
    'whatsapp_consent_bp',
    'WhatsAppClient',
    'HubSpotClient',
    'ConsentManager',
    'CONSENT_STATUS'
]
