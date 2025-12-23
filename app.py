#!/usr/bin/env python3
"""
WEST MONEY OS v8.0 - GODMODE ULTIMATE ENTERPRISE EDITION
Enterprise Universe GmbH - Complete Business Suite
15+ API Integrations | Webhooks | Full Automation
(c) 2025 Ömer Hüseyin Coşkun - GOD MODE ACTIVATED
"""

from flask import Flask, jsonify, request, Response, session, redirect
from flask_cors import CORS
import requests
import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta
import re
import csv
import io

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

PORT = int(os.getenv('PORT', 5000))
OPENCORPORATES_API_KEY = os.getenv('OPENCORPORATES_API_KEY', '')
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')
WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID', '')
HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY', '')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'westmoney_webhook_2025')

PLANS = {
    'free': {'name': 'Free', 'price': 0, 'price_yearly': 0, 'features': ['3 Kontakte', '2 Leads', 'Basic Dashboard']},
    'starter': {'name': 'Starter', 'price': 29, 'price_yearly': 290, 'features': ['50 Kontakte', '25 Leads', 'Handelsregister', 'Export']},
    'professional': {'name': 'Professional', 'price': 99, 'price_yearly': 990, 'popular': True, 'features': ['Unlimited', 'WhatsApp', 'HubSpot', 'API', 'Team']},
    'enterprise': {'name': 'Enterprise', 'price': 299, 'price_yearly': 2990, 'features': ['Alles', 'White Label', 'Custom', 'SLA 99.9%']}
}

USERS = {
    'admin': {'password': hashlib.sha256('663724'.encode()).hexdigest(), 'name': 'Ömer Coşkun', 'email': 'info@west-money.com', 'role': 'GOD MODE', 'company': 'Enterprise Universe GmbH', 'avatar': 'ÖC', 'plan': 'enterprise'},
    'demo': {'password': hashlib.sha256('demo123'.encode()).hexdigest(), 'name': 'Demo User', 'email': 'demo@west-money.com', 'role': 'Demo', 'company': 'Demo Company', 'avatar': 'DM', 'plan': 'professional'},
}

ADMIN_DB = {
    'contacts': [
        {'id': 1, 'name': 'Max Mustermann', 'email': 'max@techgmbh.de', 'company': 'Tech GmbH', 'phone': '+49 221 12345678', 'position': 'CEO', 'status': 'active', 'source': 'Website', 'created': '2025-12-01', 'whatsapp_consent': True, 'score': 85, 'tags': ['VIP']},
        {'id': 2, 'name': 'Anna Schmidt', 'email': 'anna@startup.de', 'company': 'StartUp AG', 'phone': '+49 89 98765432', 'position': 'CTO', 'status': 'active', 'source': 'Handelsregister', 'created': '2025-12-05', 'whatsapp_consent': True, 'score': 92, 'tags': ['Tech']},
        {'id': 3, 'name': 'Thomas Weber', 'email': 'weber@industrie.de', 'company': 'Industrie KG', 'phone': '+49 211 55555555', 'position': 'GF', 'status': 'lead', 'source': 'Explorium', 'created': '2025-12-10', 'whatsapp_consent': False, 'score': 68, 'tags': ['B2B']},
        {'id': 4, 'name': 'Julia Becker', 'email': 'j.becker@finance.de', 'company': 'Finance Plus GmbH', 'phone': '+49 69 44444444', 'position': 'CFO', 'status': 'active', 'source': 'Messe', 'created': '2025-12-12', 'whatsapp_consent': True, 'score': 78, 'tags': ['Finance']},
        {'id': 5, 'name': 'Michael Braun', 'email': 'braun@loxone.de', 'company': 'LOXONE Partner', 'phone': '+49 711 6666666', 'position': 'Partner', 'status': 'active', 'source': 'Partner', 'created': '2025-11-01', 'whatsapp_consent': True, 'score': 95, 'tags': ['Partner', 'VIP']},
    ],
    'leads': [
        {'id': 1, 'name': 'Smart Home Villa', 'company': 'Private Investor', 'contact': 'Dr. Hans Meier', 'email': 'meier@gmail.com', 'phone': '+49 170 1234567', 'value': 185000, 'stage': 'proposal', 'probability': 75, 'created': '2025-12-01', 'source': 'Website'},
        {'id': 2, 'name': 'Bürogebäude Automation', 'company': 'Corporate RE AG', 'contact': 'Maria Corp', 'email': 'maria@corporate.de', 'phone': '+49 171 9876543', 'value': 450000, 'stage': 'negotiation', 'probability': 85, 'created': '2025-12-05', 'source': 'Referral'},
        {'id': 3, 'name': 'Hotel Automation', 'company': 'Luxus Hotels AG', 'contact': 'Peter Luxus', 'email': 'peter@luxus.de', 'phone': '+49 172 5555555', 'value': 890000, 'stage': 'qualified', 'probability': 60, 'created': '2025-12-10', 'source': 'Messe'},
        {'id': 4, 'name': 'Restaurant Beleuchtung', 'company': 'Gastro Excellence', 'contact': 'Tom Gastro', 'email': 'tom@gastro.de', 'phone': '+49 173 4444444', 'value': 45000, 'stage': 'won', 'probability': 100, 'created': '2025-11-20', 'source': 'Google'},
        {'id': 5, 'name': 'Arztpraxis Modern', 'company': 'Dr. Wellness', 'contact': 'Dr. Sarah', 'email': 'praxis@wellness.de', 'phone': '+49 175 7777777', 'value': 28000, 'stage': 'discovery', 'probability': 20, 'created': '2025-12-18', 'source': 'Empfehlung'},
    ],
    'tasks': [
        {'id': 1, 'title': 'Angebot Villa nachfassen', 'description': 'Dr. Meier anrufen', 'status': 'pending', 'priority': 'high', 'due_date': '2025-12-27', 'created': '2025-12-20'},
        {'id': 2, 'title': 'Vertrag vorbereiten', 'description': 'Bürogebäude Automation', 'status': 'in_progress', 'priority': 'high', 'due_date': '2025-12-26', 'created': '2025-12-18'},
        {'id': 3, 'title': 'Präsentation Hotel', 'description': 'Technische Details', 'status': 'pending', 'priority': 'medium', 'due_date': '2026-01-08', 'created': '2025-12-15'},
    ],
    'campaigns': [
        {'id': 1, 'name': 'Q4 Newsletter', 'type': 'email', 'status': 'active', 'sent': 2500, 'delivered': 2450, 'opened': 1125, 'clicked': 340, 'converted': 28, 'created': '2025-10-01'},
        {'id': 2, 'name': 'Smart Home Launch', 'type': 'email', 'status': 'completed', 'sent': 5000, 'delivered': 4920, 'opened': 2750, 'clicked': 890, 'converted': 67, 'created': '2025-09-15'},
        {'id': 3, 'name': 'WhatsApp Weihnachten', 'type': 'whatsapp', 'status': 'active', 'sent': 850, 'delivered': 840, 'opened': 780, 'clicked': 320, 'converted': 45, 'created': '2025-12-01'},
    ],
    'invoices': [
        {'id': 'INV-2025-001', 'customer': 'Tech GmbH', 'email': 'billing@techgmbh.de', 'amount': 1188, 'tax': 225.72, 'total': 1413.72, 'status': 'paid', 'date': '2025-12-01', 'due': '2025-12-15'},
        {'id': 'INV-2025-002', 'customer': 'StartUp AG', 'email': 'finance@startup.de', 'amount': 3588, 'tax': 681.72, 'total': 4269.72, 'status': 'paid', 'date': '2025-12-01', 'due': '2025-12-15'},
        {'id': 'INV-2025-003', 'customer': 'Dr. Hans Meier', 'email': 'meier@gmail.com', 'amount': 45000, 'tax': 8550, 'total': 53550, 'status': 'pending', 'date': '2025-12-15', 'due': '2025-12-30'},
        {'id': 'INV-2025-004', 'customer': 'Gastro Excellence', 'email': 'tom@gastro.de', 'amount': 45000, 'tax': 8550, 'total': 53550, 'status': 'paid', 'date': '2025-12-16', 'due': '2025-12-30'},
    ],
    'notifications': [
        {'id': 1, 'type': 'deal', 'title': 'Deal gewonnen! 🎉', 'message': 'Restaurant Beleuchtung - €45.000', 'read': False, 'created': '2025-12-21 16:30', 'icon': '🎯'},
        {'id': 2, 'type': 'payment', 'title': 'Zahlung erhalten', 'message': 'Gastro Excellence - €53.550', 'read': False, 'created': '2025-12-20 14:22', 'icon': '💰'},
        {'id': 3, 'type': 'task', 'title': 'Aufgabe fällig', 'message': 'Vertrag vorbereiten', 'read': False, 'created': '2025-12-22 09:00', 'icon': '📋'},
        {'id': 4, 'type': 'whatsapp', 'title': 'WhatsApp Nachricht', 'message': 'Neue Anfrage +49 170...', 'read': False, 'created': '2025-12-23 14:22', 'icon': '📱'},
    ],
    'stats': {
        'revenue': 1247000, 'revenue_growth': 28.5,
        'leads': 67, 'leads_growth': 22,
        'customers': 234, 'customers_growth': 18,
        'mrr': 18750, 'mrr_growth': 12.4,
        'pipeline_value': 1598000, 'weighted_pipeline': 987500,
        'whatsapp_sent': 1250, 'whatsapp_delivered': 1180, 'whatsapp_read': 980,
        'email_sent': 8500, 'email_opened': 3825
    },
    'chart_data': {
        'labels': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
        'revenue': [62000, 78000, 81000, 97000, 102000, 99000, 118000, 132000, 149000, 165000, 182000, 247000],
        'leads': [28, 35, 32, 41, 38, 45, 52, 48, 56, 62, 58, 67],
        'mrr': [9200, 10800, 11100, 12600, 13200, 14500, 15000, 16400, 16900, 17200, 17850, 18750]
    }
}

DEMO_DB = {
    'contacts': [
        {'id': 1, 'name': 'Demo Kontakt 1', 'email': 'demo1@example.com', 'company': 'Demo GmbH', 'phone': '+49 123 456789', 'position': 'Manager', 'status': 'active', 'source': 'Demo', 'created': '2025-12-01', 'whatsapp_consent': True, 'score': 50, 'tags': ['Demo']},
        {'id': 2, 'name': 'Demo Kontakt 2', 'email': 'demo2@example.com', 'company': 'Test AG', 'phone': '+49 987 654321', 'position': 'CEO', 'status': 'lead', 'source': 'Website', 'created': '2025-12-10', 'whatsapp_consent': False, 'score': 35, 'tags': ['Test']},
        {'id': 3, 'name': 'Demo Kontakt 3', 'email': 'demo3@example.com', 'company': 'Sample Corp', 'phone': '+49 555 123456', 'position': 'CTO', 'status': 'active', 'source': 'Referral', 'created': '2025-12-15', 'whatsapp_consent': True, 'score': 60, 'tags': ['Sample']},
    ],
    'leads': [
        {'id': 1, 'name': 'Demo Projekt A', 'company': 'Demo Kunde', 'contact': 'Max Demo', 'email': 'max@demo.de', 'phone': '+49 170 0000001', 'value': 25000, 'stage': 'proposal', 'probability': 60, 'created': '2025-12-01', 'source': 'Demo'},
        {'id': 2, 'name': 'Demo Projekt B', 'company': 'Test Firma', 'contact': 'Lisa Test', 'email': 'lisa@test.de', 'phone': '+49 170 0000002', 'value': 45000, 'stage': 'qualified', 'probability': 40, 'created': '2025-12-10', 'source': 'Demo'},
    ],
    'tasks': [
        {'id': 1, 'title': 'Demo Task', 'description': 'Demo Aufgabe', 'status': 'pending', 'priority': 'medium', 'due_date': '2025-12-30', 'created': '2025-12-20'},
    ],
    'campaigns': [
        {'id': 1, 'name': 'Demo Newsletter', 'type': 'email', 'status': 'active', 'sent': 100, 'delivered': 98, 'opened': 45, 'clicked': 12, 'converted': 2, 'created': '2025-12-01'},
    ],
    'invoices': [
        {'id': 'DEMO-001', 'customer': 'Demo Kunde', 'email': 'demo@example.com', 'amount': 990, 'tax': 188.10, 'total': 1178.10, 'status': 'paid', 'date': '2025-12-01', 'due': '2025-12-15'},
    ],
    'notifications': [
        {'id': 1, 'type': 'info', 'title': 'Willkommen! 👋', 'message': 'Erkunden Sie alle Features', 'read': False, 'created': '2025-12-23 12:00', 'icon': '👋'},
    ],
    'stats': {
        'revenue': 125000, 'revenue_growth': 15.2,
        'leads': 12, 'leads_growth': 8,
        'customers': 24, 'customers_growth': 12,
        'mrr': 2450, 'mrr_growth': 5.4,
        'pipeline_value': 70000, 'weighted_pipeline': 35000,
        'whatsapp_sent': 50, 'whatsapp_delivered': 48, 'whatsapp_read': 40,
        'email_sent': 200, 'email_opened': 90
    },
    'chart_data': {
        'labels': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
        'revenue': [8000, 9500, 11000, 12500, 14000, 15500, 17000, 19000, 21000, 23000, 25000, 28000],
        'leads': [3, 4, 5, 6, 5, 7, 8, 7, 9, 10, 11, 12],
        'mrr': [1200, 1400, 1550, 1700, 1850, 1950, 2100, 2200, 2300, 2350, 2400, 2450]
    }
}

def get_db():
    return DEMO_DB if session.get('user') == 'demo' else ADMIN_DB

# AUTH
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '').lower().strip()
    password = data.get('password', '')
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    if username in USERS and USERS[username]['password'] == pw_hash:
        session['user'] = username
        user = USERS[username]
        return jsonify({'success': True, 'user': {'name': user['name'], 'email': user['email'], 'role': user['role'], 'company': user['company'], 'avatar': user['avatar'], 'plan': user['plan']}})
    return jsonify({'success': False, 'error': 'Ungültige Anmeldedaten'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json or {}
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    name = data.get('name', '')
    company = data.get('company', '')
    if not email or not password or not name:
        return jsonify({'success': False, 'error': 'Alle Pflichtfelder ausfüllen'}), 400
    if len(password) < 8:
        return jsonify({'success': False, 'error': 'Passwort mind. 8 Zeichen'}), 400
    username = email.split('@')[0].lower()
    if username in USERS:
        return jsonify({'success': False, 'error': 'Benutzer existiert'}), 400
    USERS[username] = {'password': hashlib.sha256(password.encode()).hexdigest(), 'name': name, 'email': email, 'role': 'User', 'company': company, 'avatar': name[:2].upper(), 'plan': 'free'}
    session['user'] = username
    return jsonify({'success': True, 'user': USERS[username]})

@app.route('/api/auth/demo', methods=['POST'])
def demo_login():
    session['user'] = 'demo'
    user = USERS['demo']
    return jsonify({'success': True, 'user': {'name': user['name'], 'email': user['email'], 'role': user['role'], 'company': user['company'], 'avatar': user['avatar'], 'plan': user['plan']}})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/status')
def auth_status():
    if 'user' in session:
        user = USERS.get(session['user'], {})
        return jsonify({'authenticated': True, 'user': {'name': user.get('name'), 'email': user.get('email'), 'role': user.get('role'), 'company': user.get('company'), 'avatar': user.get('avatar'), 'plan': user.get('plan')}})
    return jsonify({'authenticated': False})

# DASHBOARD
@app.route('/api/dashboard/stats')
def dashboard_stats():
    return jsonify(get_db()['stats'])

@app.route('/api/dashboard/charts')
def dashboard_charts():
    return jsonify(get_db()['chart_data'])

# CONTACTS
@app.route('/api/contacts')
def get_contacts():
    return jsonify(get_db()['contacts'])

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    db = get_db()
    data = request.json
    new_id = max([c['id'] for c in db['contacts']], default=0) + 1
    contact = {'id': new_id, 'name': data.get('name', ''), 'email': data.get('email', ''), 'company': data.get('company', ''), 'phone': data.get('phone', ''), 'position': data.get('position', ''), 'status': 'lead', 'source': data.get('source', 'Manual'), 'created': datetime.now().strftime('%Y-%m-%d'), 'whatsapp_consent': False, 'score': 50, 'tags': []}
    db['contacts'].append(contact)
    return jsonify(contact)

@app.route('/api/contacts/bulk-consent', methods=['POST'])
def bulk_consent():
    db = get_db()
    data = request.json
    ids = data.get('contact_ids', [])
    consent = data.get('consent', False)
    updated = 0
    for c in db['contacts']:
        if c['id'] in ids:
            c['whatsapp_consent'] = consent
            updated += 1
    return jsonify({'success': True, 'updated': updated})

# LEADS
@app.route('/api/leads')
def get_leads():
    return jsonify(get_db()['leads'])

@app.route('/api/leads', methods=['POST'])
def create_lead():
    db = get_db()
    data = request.json
    new_id = max([l['id'] for l in db['leads']], default=0) + 1
    lead = {'id': new_id, 'name': data.get('name', ''), 'company': data.get('company', ''), 'contact': data.get('contact', ''), 'email': data.get('email', ''), 'phone': data.get('phone', ''), 'value': int(data.get('value', 0)), 'stage': 'discovery', 'probability': 10, 'created': datetime.now().strftime('%Y-%m-%d'), 'source': data.get('source', 'Manual')}
    db['leads'].append(lead)
    return jsonify(lead)

@app.route('/api/leads/<int:id>/stage', methods=['POST'])
def update_lead_stage(id):
    db = get_db()
    data = request.json
    stages = {'discovery': 10, 'qualified': 30, 'proposal': 50, 'negotiation': 75, 'won': 100, 'lost': 0}
    for l in db['leads']:
        if l['id'] == id:
            l['stage'] = data.get('stage', l['stage'])
            l['probability'] = stages.get(l['stage'], l['probability'])
            return jsonify({'success': True, 'lead': l})
    return jsonify({'success': False}), 404

# TASKS
@app.route('/api/tasks')
def get_tasks():
    return jsonify(get_db()['tasks'])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    db = get_db()
    data = request.json
    new_id = max([t['id'] for t in db['tasks']], default=0) + 1
    task = {'id': new_id, 'title': data.get('title', ''), 'description': data.get('description', ''), 'status': 'pending', 'priority': data.get('priority', 'medium'), 'due_date': data.get('due_date', ''), 'created': datetime.now().strftime('%Y-%m-%d')}
    db['tasks'].append(task)
    return jsonify(task)

@app.route('/api/tasks/<int:id>/complete', methods=['POST'])
def complete_task(id):
    db = get_db()
    for t in db['tasks']:
        if t['id'] == id:
            t['status'] = 'completed'
            return jsonify({'success': True})
    return jsonify({'success': False}), 404

# CAMPAIGNS
@app.route('/api/campaigns')
def get_campaigns():
    return jsonify(get_db()['campaigns'])

# INVOICES
@app.route('/api/invoices')
def get_invoices():
    return jsonify(get_db()['invoices'])

# NOTIFICATIONS
@app.route('/api/notifications')
def get_notifications():
    return jsonify(get_db()['notifications'])

@app.route('/api/notifications/unread-count')
def unread_count():
    return jsonify({'count': len([n for n in get_db()['notifications'] if not n['read']])})

@app.route('/api/notifications/<int:id>/read', methods=['POST'])
def mark_read(id):
    for n in get_db()['notifications']:
        if n['id'] == id:
            n['read'] = True
    return jsonify({'success': True})

@app.route('/api/notifications/mark-all-read', methods=['POST'])
def mark_all_read():
    for n in get_db()['notifications']:
        n['read'] = True
    return jsonify({'success': True})

# WHATSAPP
@app.route('/api/whatsapp/send', methods=['POST'])
def whatsapp_send():
    if session.get('user') == 'demo':
        return jsonify({'success': True, 'message': 'Demo: WhatsApp simuliert', 'demo': True})
    data = request.json
    phone = data.get('phone', '').replace(' ', '').replace('+', '')
    message = data.get('message', '')
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        return jsonify({'success': False, 'error': 'WhatsApp nicht konfiguriert'})
    try:
        url = f'https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages'
        headers = {'Authorization': f'Bearer {WHATSAPP_TOKEN}', 'Content-Type': 'application/json'}
        payload = {'messaging_product': 'whatsapp', 'to': phone, 'type': 'text', 'text': {'body': message}}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return jsonify({'success': r.status_code == 200, 'response': r.json()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == WEBHOOK_SECRET:
            return request.args.get('hub.challenge', '')
        return 'Invalid', 403
    return jsonify({'success': True})

@app.route('/api/whatsapp/templates')
def whatsapp_templates():
    return jsonify([
        {'id': 'welcome', 'name': 'Willkommen', 'text': 'Willkommen bei West Money! Wie können wir helfen?'},
        {'id': 'appointment', 'name': 'Termin', 'text': 'Ihr Termin: {{1}} um {{2}} Uhr'},
        {'id': 'quote', 'name': 'Angebot', 'text': 'Ihr Angebot: {{1}}'},
        {'id': 'followup', 'name': 'Nachfassen', 'text': 'Haben Sie noch Fragen?'},
        {'id': 'invoice', 'name': 'Rechnung', 'text': 'Rechnung {{1}} über {{2}} verfügbar'},
    ])

# HUBSPOT
@app.route('/api/hubspot/status')
def hubspot_status():
    return jsonify({'connected': bool(HUBSPOT_API_KEY)})

@app.route('/api/hubspot/sync', methods=['POST'])
def hubspot_sync():
    if session.get('user') == 'demo':
        return jsonify({'success': True, 'synced': 5, 'demo': True})
    if not HUBSPOT_API_KEY:
        return jsonify({'success': False, 'error': 'HubSpot nicht konfiguriert'})
    try:
        db = get_db()
        synced = 0
        for contact in db['contacts']:
            url = 'https://api.hubapi.com/crm/v3/objects/contacts'
            headers = {'Authorization': f'Bearer {HUBSPOT_API_KEY}', 'Content-Type': 'application/json'}
            name_parts = contact['name'].split(' ', 1)
            payload = {'properties': {'email': contact['email'], 'firstname': name_parts[0] if name_parts else '', 'lastname': name_parts[1] if len(name_parts) > 1 else '', 'company': contact.get('company', ''), 'phone': contact.get('phone', '')}}
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            if r.status_code in [200, 201, 409]:
                synced += 1
        return jsonify({'success': True, 'synced': synced})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# HANDELSREGISTER
@app.route('/api/hr/search')
def hr_search():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'results': [], 'total': 0})
    try:
        url = 'https://api.opencorporates.com/v0.4/companies/search'
        params = {'q': q, 'jurisdiction_code': 'de', 'per_page': 30}
        if OPENCORPORATES_API_KEY:
            params['api_token'] = OPENCORPORATES_API_KEY
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        results = []
        for item in data.get('results', {}).get('companies', []):
            c = item.get('company', {})
            addr = c.get('registered_address', {}) or {}
            cn = (c.get('company_number') or '').upper()
            reg_type = next((rt for rt in ['HRB', 'HRA', 'GNR', 'PR', 'VR'] if rt in cn), '')
            results.append({'id': c.get('company_number', ''), 'name': c.get('name', ''), 'register_type': reg_type, 'register_number': cn, 'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv', 'type': c.get('company_type', ''), 'city': addr.get('locality', ''), 'address': ', '.join(filter(None, [addr.get('street_address'), addr.get('postal_code'), addr.get('locality')])), 'founded': c.get('incorporation_date', ''), 'url': c.get('opencorporates_url', '')})
        return jsonify({'success': True, 'results': results, 'total': data.get('results', {}).get('total_count', 0)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'results': []})

@app.route('/api/hr/import', methods=['POST'])
def hr_import():
    db = get_db()
    data = request.json
    new_id = max([c['id'] for c in db['contacts']], default=0) + 1
    contact = {'id': new_id, 'name': data.get('name', ''), 'email': '', 'company': data.get('name', ''), 'phone': '', 'position': '', 'status': 'lead', 'source': 'Handelsregister', 'created': datetime.now().strftime('%Y-%m-%d'), 'whatsapp_consent': False, 'score': 40, 'tags': ['HR', data.get('register_type', '')]}
    db['contacts'].append(contact)
    return jsonify({'success': True, 'contact': contact})

# CRYPTO API (CoinGecko - FREE)
@app.route('/api/crypto/prices')
def crypto_prices():
    try:
        r = requests.get('https://api.coingecko.com/api/v3/simple/price', params={'ids': 'bitcoin,ethereum,solana', 'vs_currencies': 'eur,usd', 'include_24hr_change': 'true'}, timeout=10)
        return jsonify(r.json())
    except:
        return jsonify({'bitcoin': {'eur': 42500}, 'ethereum': {'eur': 2250}, 'solana': {'eur': 95}})

# EXCHANGE RATES (FREE)
@app.route('/api/exchange-rates')
def exchange_rates():
    try:
        r = requests.get('https://api.exchangerate-api.com/v4/latest/EUR', timeout=10)
        return jsonify(r.json())
    except:
        return jsonify({'rates': {'USD': 1.09, 'GBP': 0.86, 'CHF': 0.95, 'JPY': 162.5}})

# WEATHER (FREE)
@app.route('/api/weather')
def weather():
    city = request.args.get('city', 'Cologne')
    return jsonify({'city': city, 'temp': 8, 'description': 'Bewölkt', 'humidity': 75})

# ADDITIONAL STATS
@app.route('/api/gaming/stats')
def gaming_stats():
    return jsonify({'twitch_followers': 15420, 'youtube_subs': 8750, 'discord_members': 3240, 'peak_viewers': 12500})

@app.route('/api/automations/stats')
def automations_stats():
    return jsonify({'active_systems': 47, 'devices_connected': 2840, 'energy_saved_kwh': 45200, 'co2_reduced_kg': 18900})

@app.route('/api/security/stats')
def security_stats():
    return jsonify({'threats_blocked': 1247, 'systems_protected': 58, 'uptime_percent': 99.97, 'security_score': 94})

# EXPORT
@app.route('/api/export/contacts')
def export_contacts():
    db = get_db()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['id', 'name', 'email', 'company', 'phone', 'status', 'source', 'created', 'score'])
    writer.writeheader()
    for c in db['contacts']:
        writer.writerow({k: c.get(k, '') for k in ['id', 'name', 'email', 'company', 'phone', 'status', 'source', 'created', 'score']})
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=contacts.csv'})

@app.route('/api/export/leads')
def export_leads():
    db = get_db()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['id', 'name', 'company', 'contact', 'email', 'value', 'stage', 'probability'])
    writer.writeheader()
    for l in db['leads']:
        writer.writerow({k: l.get(k, '') for k in ['id', 'name', 'company', 'contact', 'email', 'value', 'stage', 'probability']})
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=leads.csv'})

# PLANS
@app.route('/api/plans')
def get_plans():
    return jsonify(PLANS)

# HEALTH
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'version': '8.0.0', 'codename': 'GODMODE', 'timestamp': datetime.now().isoformat()})

# WEBHOOKS
@app.route('/api/webhooks/incoming/<webhook_id>', methods=['POST'])
def incoming_webhook(webhook_id):
    return jsonify({'success': True, 'received': webhook_id})

# HTML TEMPLATES
LANDING_HTML = '''<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>West Money OS | All-in-One Business Platform</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>:root{--bg:#09090b;--bg2:#111114;--text:#fafafa;--text2:#a1a1aa;--text3:#71717a;--gold:#fbbf24;--orange:#f97316;--emerald:#10b981;--border:rgba(255,255,255,.06)}*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}.nav{position:fixed;top:0;left:0;right:0;background:rgba(9,9,11,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);z-index:100;padding:0 24px}.nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:72px}.nav-logo{display:flex;align-items:center;gap:12px;font-size:20px;font-weight:700;text-decoration:none;color:var(--text)}.nav-logo span{background:linear-gradient(135deg,var(--gold),var(--orange));width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center}.btn{padding:10px 20px;border-radius:8px;font-size:14px;font-weight:500;text-decoration:none;transition:all .2s;cursor:pointer;border:none;display:inline-flex;align-items:center;gap:6px}.btn-ghost{background:transparent;color:var(--text);border:1px solid var(--border)}.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;font-weight:600}.btn-gold:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(251,191,36,.25)}.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:120px 24px 80px;background:radial-gradient(ellipse at top,rgba(251,191,36,.05) 0%,transparent 60%)}.hero-content{max-width:900px}.badges{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-bottom:24px}.badge{display:inline-flex;align-items:center;gap:6px;background:var(--bg2);border:1px solid var(--border);padding:6px 14px;border-radius:20px;font-size:12px;color:var(--text2)}.badge .dot{width:6px;height:6px;background:var(--emerald);border-radius:50%;animation:pulse 2s infinite}.badge .new{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}h1{font-size:64px;font-weight:800;line-height:1.05;margin-bottom:24px;background:linear-gradient(135deg,var(--text) 0%,var(--text) 60%,var(--gold) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.hero p{font-size:18px;color:var(--text2);margin-bottom:36px;max-width:600px;margin-left:auto;margin-right:auto}.hero-btns{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}.hero-btns .btn{padding:14px 28px;font-size:15px}.integrations{display:flex;justify-content:center;gap:16px;margin-top:48px;flex-wrap:wrap}.int-badge{background:var(--bg2);border:1px solid var(--border);padding:8px 14px;border-radius:8px;font-size:12px;color:var(--text2)}.stats{display:flex;justify-content:center;gap:48px;margin-top:64px;flex-wrap:wrap}.stat{text-align:center}.stat-value{font-size:42px;font-weight:800;background:linear-gradient(135deg,var(--gold),var(--orange));-webkit-background-clip:text;-webkit-text-fill-color:transparent}.stat-label{font-size:13px;color:var(--text3)}.features{padding:100px 24px;background:var(--bg2)}.section-header{text-align:center;margin-bottom:48px}.section-header h2{font-size:40px;font-weight:700;margin-bottom:12px}.section-header p{color:var(--text2);font-size:16px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;max-width:1200px;margin:0 auto}.card{background:var(--bg);border:1px solid var(--border);border-radius:12px;padding:24px;transition:all .3s}.card:hover{border-color:rgba(251,191,36,.2);transform:translateY(-2px)}.card-icon{width:44px;height:44px;background:linear-gradient(135deg,rgba(251,191,36,.12),rgba(251,191,36,.04));border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:14px}.card h3{font-size:16px;font-weight:600;margin-bottom:8px}.card p{color:var(--text2);font-size:13px;line-height:1.6}.tag{display:inline-block;background:rgba(16,185,129,.12);color:var(--emerald);padding:3px 8px;border-radius:5px;font-size:10px;font-weight:600;margin-top:10px}.cta{padding:100px 24px;text-align:center;background:linear-gradient(180deg,var(--bg) 0%,rgba(251,191,36,.03) 100%)}.cta h2{font-size:40px;font-weight:700;margin-bottom:12px}.cta p{color:var(--text2);font-size:16px;margin-bottom:32px}.footer{padding:40px 24px;border-top:1px solid var(--border)}.footer-inner{max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}.footer p{color:var(--text3);font-size:12px}.footer a{color:var(--gold);text-decoration:none}@media(max-width:900px){h1{font-size:36px}.grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:600px){.grid{grid-template-columns:1fr}.stats{gap:24px}}</style></head>
<body>
<nav class="nav"><div class="nav-inner"><a href="/" class="nav-logo"><span>⚡</span>West Money OS</a><div style="display:flex;gap:12px"><a href="/app" class="btn btn-ghost">Login</a><a href="/register" class="btn btn-gold">Kostenlos</a></div></div></nav>
<section class="hero"><div class="hero-content"><div class="badges"><div class="badge"><span class="dot"></span><span class="new">NEU</span>v8.0 GODMODE</div><div class="badge">🔗 15+ APIs</div><div class="badge">🔄 Webhooks</div></div><h1>Die ultimative Business Platform</h1><p>CRM, WhatsApp Business, HubSpot, Handelsregister, Crypto und 15+ weitere Integrationen - alles in einer Plattform.</p><div class="hero-btns"><a href="/demo" class="btn btn-gold">🚀 Kostenlos testen</a><a href="/pricing" class="btn btn-ghost">💳 Pläne ab €0</a></div><div class="integrations"><div class="int-badge">📱 WhatsApp</div><div class="int-badge">🔗 HubSpot</div><div class="int-badge">💳 Stripe</div><div class="int-badge">🏛️ Handelsregister</div><div class="int-badge">₿ Crypto</div><div class="int-badge">⚡ Zapier</div></div><div class="stats"><div class="stat"><div class="stat-value">234+</div><div class="stat-label">Kunden</div></div><div class="stat"><div class="stat-value">€1.5M</div><div class="stat-label">Pipeline</div></div><div class="stat"><div class="stat-value">99.97%</div><div class="stat-label">Uptime</div></div><div class="stat"><div class="stat-value">15+</div><div class="stat-label">APIs</div></div></div></div></section>
<section class="features"><div class="section-header"><h2>Alles was Sie brauchen</h2><p>Enterprise-Features für jeden</p></div><div class="grid"><div class="card"><div class="card-icon">📱</div><h3>WhatsApp Business</h3><p>Nachrichten, Templates, Consent-Management direkt aus dem CRM.</p><span class="tag">API</span></div><div class="card"><div class="card-icon">🔗</div><h3>HubSpot Sync</h3><p>Bidirektionale Synchronisation aller Kontakte.</p><span class="tag">API</span></div><div class="card"><div class="card-icon">🏛️</div><h3>Handelsregister</h3><p>LIVE Suche im deutschen Handelsregister.</p><span class="tag">LIVE</span></div><div class="card"><div class="card-icon">₿</div><h3>Crypto & Exchange</h3><p>Live Preise und Wechselkurse.</p><span class="tag">API</span></div><div class="card"><div class="card-icon">👥</div><h3>CRM & Pipeline</h3><p>Kontakte, Leads, Deals, Tasks.</p></div><div class="card"><div class="card-icon">📊</div><h3>Analytics</h3><p>KPIs, Charts, Reports, Export.</p></div><div class="card"><div class="card-icon">🤖</div><h3>Automations</h3><p>Smart Home, Building Automation.</p></div><div class="card"><div class="card-icon">🛡️</div><h3>Security</h3><p>Enterprise-grade Security.</p></div></div></section>
<section class="cta"><h2>Bereit für GODMODE?</h2><p>Starten Sie kostenlos.</p><div class="hero-btns"><a href="/demo" class="btn btn-gold">🚀 Demo</a><a href="/register" class="btn btn-ghost">Account →</a></div></section>
<footer class="footer"><div class="footer-inner"><p>© 2025 <a href="https://enterprise-universe.de">Enterprise Universe GmbH</a> | West Money OS v8.0</p></div></footer>
</body></html>'''

PRICING_HTML = '''<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pricing | West Money OS</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>:root{--bg:#09090b;--bg2:#111114;--bg3:#18181b;--text:#fafafa;--text2:#a1a1aa;--gold:#fbbf24;--orange:#f97316;--emerald:#10b981;--border:rgba(255,255,255,.06)}*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}.nav{position:fixed;top:0;left:0;right:0;background:rgba(9,9,11,.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);z-index:100;padding:0 24px}.nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:72px}.nav-logo{display:flex;align-items:center;gap:12px;font-size:20px;font-weight:700;text-decoration:none;color:var(--text)}.nav-logo span{background:linear-gradient(135deg,var(--gold),var(--orange));width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center}.btn{padding:10px 20px;border-radius:8px;font-size:14px;font-weight:500;text-decoration:none;cursor:pointer;border:none}.btn-ghost{background:transparent;color:var(--text);border:1px solid var(--border)}.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;font-weight:600}.pricing{padding:130px 24px 80px;max-width:1200px;margin:0 auto}.pricing-header{text-align:center;margin-bottom:48px}.pricing-header h1{font-size:40px;font-weight:700;margin-bottom:12px}.pricing-header p{color:var(--text2);font-size:16px}.toggle-wrap{display:flex;justify-content:center;gap:12px;margin-top:24px;align-items:center}.toggle-wrap span{color:var(--text3);font-size:14px;cursor:pointer}.toggle-wrap span.active{color:var(--gold)}.toggle{width:48px;height:24px;background:var(--bg3);border-radius:12px;position:relative;cursor:pointer;border:1px solid var(--border)}.toggle::after{content:'';position:absolute;width:18px;height:18px;background:var(--gold);border-radius:50%;top:2px;left:3px;transition:transform .2s}.toggle.yearly::after{transform:translateX(22px)}.pricing-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:40px}.plan-card{background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:28px;position:relative}.plan-card.popular{border-color:var(--gold);background:linear-gradient(180deg,rgba(251,191,36,.03) 0%,var(--bg2) 100%)}.popular-badge{position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;padding:4px 14px;border-radius:14px;font-size:10px;font-weight:700}.plan-name{font-size:20px;font-weight:700;margin-bottom:4px}.plan-price{font-size:44px;font-weight:800;margin-bottom:4px}.plan-price span{font-size:14px;color:var(--text2);font-weight:400}.plan-desc{color:var(--text3);font-size:12px;margin-bottom:20px}.plan-features{list-style:none;margin-bottom:24px}.plan-features li{padding:8px 0;font-size:12px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--border)}.plan-features li:last-child{border-bottom:none}.plan-features li::before{content:'✓';color:var(--emerald);font-weight:700}.plan-features li.disabled{color:var(--text3)}.plan-features li.disabled::before{content:'—';color:var(--text3)}.plan-btn{width:100%;padding:12px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;border:none}.plan-btn.primary{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}.plan-btn.secondary{background:var(--bg3);color:var(--text);border:1px solid var(--border)}@media(max-width:900px){.pricing-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:600px){.pricing-grid{grid-template-columns:1fr}}</style></head>
<body>
<nav class="nav"><div class="nav-inner"><a href="/" class="nav-logo"><span>⚡</span>West Money OS</a><div style="display:flex;gap:12px"><a href="/demo" class="btn btn-ghost">Demo</a><a href="/app" class="btn btn-gold">Login</a></div></div></nav>
<section class="pricing"><div class="pricing-header"><h1>Transparent & Fair</h1><p>Starten Sie kostenlos. Upgraden Sie wenn Sie wachsen.</p><div class="toggle-wrap"><span class="active" id="mL" onclick="setB(0)">Monatlich</span><div class="toggle" id="tog" onclick="togB()"></div><span id="yL" onclick="setB(1)">Jährlich <span style="color:var(--emerald)">-17%</span></span></div></div>
<div class="pricing-grid">
<div class="plan-card"><div class="plan-name">Free</div><div class="plan-price" id="p0">€0<span>/Monat</span></div><div class="plan-desc">Zum Ausprobieren</div><ul class="plan-features"><li>3 Kontakte</li><li>2 Leads</li><li>Basic Dashboard</li><li class="disabled">Handelsregister</li><li class="disabled">WhatsApp</li></ul><button class="plan-btn secondary" onclick="location.href='/register'">Kostenlos</button></div>
<div class="plan-card"><div class="plan-name">Starter</div><div class="plan-price" id="p1">€29<span>/Monat</span></div><div class="plan-desc">Einzelunternehmer</div><ul class="plan-features"><li>50 Kontakte</li><li>25 Leads</li><li>Handelsregister</li><li>CSV Export</li><li class="disabled">WhatsApp</li></ul><button class="plan-btn secondary">Starten</button></div>
<div class="plan-card popular"><div class="popular-badge">⭐ BELIEBT</div><div class="plan-name">Professional</div><div class="plan-price" id="p2">€99<span>/Monat</span></div><div class="plan-desc">Für Teams</div><ul class="plan-features"><li>Unlimited</li><li>WhatsApp</li><li>HubSpot</li><li>API Access</li><li>Team (3)</li></ul><button class="plan-btn primary">Jetzt starten</button></div>
<div class="plan-card"><div class="plan-name">Enterprise</div><div class="plan-price" id="p3">€299<span>/Monat</span></div><div class="plan-desc">Unternehmen</div><ul class="plan-features"><li>Alles Unlimited</li><li>White Label</li><li>Custom Domain</li><li>SLA 99.9%</li><li>Dedicated</li></ul><button class="plan-btn secondary" onclick="location.href='mailto:info@west-money.com'">Kontakt</button></div>
</div></section>
<script>let y=0;const pr=[[0,0],[29,290],[99,990],[299,2990]];function togB(){y=1-y;upd()}function setB(v){y=v;upd()}function upd(){document.getElementById('tog').classList.toggle('yearly',y);document.getElementById('mL').classList.toggle('active',!y);document.getElementById('yL').classList.toggle('active',y);const s=y?'/Jahr':'/Monat';for(let i=0;i<4;i++)document.getElementById('p'+i).innerHTML='€'+pr[i][y]+'<span>'+s+'</span>'}</script>
</body></html>'''

DEMO_HTML = '''<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Demo | West Money OS</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>:root{--bg:#09090b;--bg2:#111114;--text:#fafafa;--text2:#a1a1aa;--gold:#fbbf24;--orange:#f97316;--emerald:#10b981;--border:rgba(255,255,255,.06)}*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}.box{background:var(--bg2);border:1px solid var(--border);border-radius:20px;padding:44px;max-width:440px;width:100%;text-align:center}.icon{width:80px;height:80px;background:linear-gradient(135deg,var(--gold),var(--orange));border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:36px;margin:0 auto 20px;box-shadow:0 16px 48px rgba(251,191,36,.2)}h1{font-size:28px;margin-bottom:8px}p{color:var(--text2);margin-bottom:24px;font-size:14px}.features{text-align:left;background:var(--bg);border:1px solid var(--border);border-radius:12px;padding:18px;margin-bottom:24px}.features h3{font-size:11px;color:var(--text2);margin-bottom:12px;text-transform:uppercase;letter-spacing:.5px}.features ul{list-style:none}.features li{padding:7px 0;font-size:12px;display:flex;align-items:center;gap:7px}.features li::before{content:'✓';color:var(--emerald);font-weight:700}.btn{width:100%;padding:14px;border-radius:10px;font-size:14px;font-weight:600;cursor:pointer;border:none;margin-bottom:8px}.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}.btn-ghost{background:transparent;color:var(--text);border:1px solid var(--border)}.note{font-size:10px;color:var(--text2);margin-top:14px}</style></head>
<body><div class="box"><div class="icon">🚀</div><h1>Demo starten</h1><p>Testen Sie alle Features kostenlos.</p><div class="features"><h3>Enthalten:</h3><ul><li>CRM Dashboard</li><li>Kontakte & Leads</li><li>Handelsregister LIVE</li><li>WhatsApp Templates</li><li>Crypto & Exchange</li><li>Alle 15+ APIs</li></ul></div><button class="btn btn-gold" onclick="go()">⚡ Demo starten</button><button class="btn btn-ghost" onclick="location.href='/app'">Ich habe einen Account</button><p class="note">Keine Registrierung. Demo-Daten.</p></div>
<script>async function go(){const r=await fetch('/api/auth/demo',{method:'POST'});const d=await r.json();if(d.success)location.href='/app'}</script>
</body></html>'''

REGISTER_HTML = '''<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Registrieren | West Money OS</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>:root{--bg:#09090b;--bg2:#111114;--bg3:#18181b;--text:#fafafa;--text2:#a1a1aa;--gold:#fbbf24;--orange:#f97316;--rose:#f43f5e;--border:rgba(255,255,255,.06)}*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}.box{background:var(--bg2);border:1px solid var(--border);border-radius:20px;padding:40px;max-width:400px;width:100%}.logo{text-align:center;margin-bottom:24px}.logo-icon{width:56px;height:56px;background:linear-gradient(135deg,var(--gold),var(--orange));border-radius:14px;display:inline-flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:12px}.logo h1{font-size:20px;margin-bottom:4px}.logo p{color:var(--text2);font-size:12px}.form-group{margin-bottom:14px}.form-group label{display:block;font-size:11px;margin-bottom:5px;color:var(--text2)}.form-input{width:100%;padding:11px 13px;background:var(--bg3);border:1px solid var(--border);border-radius:7px;color:var(--text);font-size:13px}.form-input:focus{outline:none;border-color:var(--gold)}.btn{width:100%;padding:13px;border-radius:9px;font-size:13px;font-weight:600;cursor:pointer;border:none;margin-top:5px}.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}.error{background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.2);color:var(--rose);padding:9px;border-radius:7px;margin-bottom:14px;font-size:11px;display:none}.error.show{display:block}.divider{text-align:center;margin:18px 0;color:var(--text2);font-size:11px}.links{text-align:center;margin-top:18px;font-size:11px}.links a{color:var(--gold);text-decoration:none}</style></head>
<body><div class="box"><div class="logo"><div class="logo-icon">⚡</div><h1>Account erstellen</h1><p>Kostenlos starten</p></div><div class="error" id="err"></div><div class="form-group"><label>Name *</label><input class="form-input" id="name" placeholder="Ihr Name"></div><div class="form-group"><label>E-Mail *</label><input class="form-input" id="email" type="email" placeholder="ihre@email.de"></div><div class="form-group"><label>Unternehmen</label><input class="form-input" id="company" placeholder="Firma GmbH"></div><div class="form-group"><label>Passwort * (min. 8)</label><input class="form-input" id="pass" type="password" placeholder="••••••••"></div><button class="btn btn-gold" onclick="reg()">🚀 Registrieren</button><div class="divider">oder</div><button class="btn" style="background:var(--bg3);color:var(--text)" onclick="location.href='/demo'">Demo starten</button><div class="links">Account? <a href="/app">Anmelden</a></div></div>
<script>async function reg(){const n=document.getElementById('name').value,e=document.getElementById('email').value,c=document.getElementById('company').value,p=document.getElementById('pass').value,err=document.getElementById('err');if(!n||!e||!p){err.textContent='Pflichtfelder ausfüllen';err.classList.add('show');return}if(p.length<8){err.textContent='Passwort mind. 8 Zeichen';err.classList.add('show');return}const r=await fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,email:e,company:c,password:p})});const d=await r.json();if(d.success)location.href='/app';else{err.textContent=d.error||'Fehler';err.classList.add('show')}}</script>
</body></html>'''

APP_HTML = '''<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>West Money OS v8.0</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>:root{--bg0:#09090b;--bg1:#0e0e11;--bg2:#141417;--bg3:#1a1a1e;--text0:#fafafa;--text1:#e4e4e7;--text2:#a1a1aa;--text3:#71717a;--primary:#6366f1;--emerald:#10b981;--amber:#f59e0b;--rose:#f43f5e;--cyan:#06b6d4;--violet:#8b5cf6;--gold:#fbbf24;--orange:#f97316;--border:rgba(255,255,255,.05);--r:7px}*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg0);color:var(--text0);font-size:13px}.login{min-height:100vh;display:flex;align-items:center;justify-content:center}.login-box{background:var(--bg2);border:1px solid var(--border);border-radius:18px;padding:40px;width:100%;max-width:360px}.login-logo{text-align:center;margin-bottom:24px}.login-logo-icon{width:56px;height:56px;background:linear-gradient(135deg,var(--gold),var(--orange));border-radius:14px;display:inline-flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:10px}.login-logo h1{font-size:18px;margin-bottom:3px}.login-logo p{color:var(--text3);font-size:11px}.form-group{margin-bottom:12px}.form-group label{display:block;font-size:11px;margin-bottom:4px;color:var(--text2)}.form-input{width:100%;padding:11px 12px;background:var(--bg3);border:1px solid var(--border);border-radius:var(--r);color:var(--text0);font-size:12px}.form-input:focus{outline:none;border-color:var(--gold)}.login-btn{width:100%;padding:12px;background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;border:none;border-radius:var(--r);font-size:13px;font-weight:600;cursor:pointer;margin-top:5px}.demo-link{text-align:center;margin-top:18px}.demo-link a{color:var(--gold);text-decoration:none;font-size:11px}.login-error{background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.2);color:var(--rose);padding:9px;border-radius:var(--r);margin-bottom:12px;text-align:center;display:none;font-size:11px}.login-error.show{display:block}.app{display:none;min-height:100vh}.app.active{display:flex}.sidebar{width:220px;background:var(--bg1);border-right:1px solid var(--border);position:fixed;height:100vh;display:flex;flex-direction:column;overflow-y:auto}.sidebar-header{padding:14px;border-bottom:1px solid var(--border)}.logo{display:flex;align-items:center;gap:9px}.logo-icon{width:32px;height:32px;background:linear-gradient(135deg,var(--gold),var(--orange));border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:14px}.logo-text h1{font-size:13px;font-weight:700}.logo-text span{font-size:9px;color:var(--text3)}.sidebar-nav{flex:1;padding:8px}.nav-section{margin-bottom:2px}.nav-section-title{font-size:9px;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:.5px;padding:9px 9px 5px}.nav-item{display:flex;align-items:center;gap:7px;padding:8px 9px;border-radius:var(--r);cursor:pointer;color:var(--text2);font-size:11px;margin-bottom:1px}.nav-item:hover{background:var(--bg3);color:var(--text0)}.nav-item.active{background:rgba(251,191,36,.08);color:var(--gold);border:1px solid rgba(251,191,36,.1)}.nav-item .badge{font-size:8px;padding:2px 5px;border-radius:5px;font-weight:600;margin-left:auto}.nav-item .badge.live{background:var(--rose);color:white}.nav-item .badge.api{background:var(--cyan);color:white}.nav-item .badge.new{background:var(--emerald);color:white}.sidebar-footer{padding:9px;border-top:1px solid var(--border)}.user-card{display:flex;align-items:center;gap:7px;padding:9px;background:var(--bg2);border-radius:var(--r)}.user-avatar{width:28px;height:28px;border-radius:7px;background:linear-gradient(135deg,var(--gold),var(--orange));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:10px;color:#000}.user-info{flex:1}.user-info .name{font-size:11px;font-weight:600}.user-info .role{font-size:9px;color:var(--gold)}.logout-btn{background:none;border:none;color:var(--text3);cursor:pointer;font-size:12px}.main{flex:1;margin-left:220px;min-height:100vh}.topbar{height:48px;background:var(--bg1);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 18px;position:sticky;top:0;z-index:50}.breadcrumb{font-size:11px;color:var(--text2)}.breadcrumb strong{color:var(--gold)}.topbar-right{display:flex;align-items:center;gap:9px}.notif-btn{background:var(--bg2);border:1px solid var(--border);padding:5px 9px;border-radius:var(--r);cursor:pointer;position:relative;font-size:11px}.notif-btn .count{position:absolute;top:-3px;right:-3px;background:var(--rose);color:white;font-size:8px;padding:2px 4px;border-radius:6px}.demo-badge{background:linear-gradient(135deg,var(--emerald),var(--cyan));color:#fff;padding:4px 10px;border-radius:10px;font-size:9px;font-weight:600}.content{padding:18px}.page{display:none}.page.active{display:block}.page-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px;flex-wrap:wrap;gap:10px}.page-header h1{font-size:18px;font-weight:700;display:flex;align-items:center;gap:7px}.page-header p{color:var(--text2);font-size:11px;margin-top:2px}.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:18px}.stat-card{background:var(--bg2);border:1px solid var(--border);border-radius:9px;padding:14px}.stat-card.gold{border-left:3px solid var(--gold)}.stat-card.emerald{border-left:3px solid var(--emerald)}.stat-card.amber{border-left:3px solid var(--amber)}.stat-card.violet{border-left:3px solid var(--violet)}.stat-card.cyan{border-left:3px solid var(--cyan)}.stat-card .label{font-size:10px;color:var(--text3);margin-bottom:3px}.stat-card .value{font-size:22px;font-weight:700}.stat-card .change{font-size:9px;margin-top:3px;color:var(--emerald)}.card{background:var(--bg2);border:1px solid var(--border);border-radius:9px;margin-bottom:14px}.card-header{padding:12px 14px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}.card-header h3{font-size:12px;font-weight:600;display:flex;align-items:center;gap:5px}.card-body{padding:14px}.card-body.no-padding{padding:0}.grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.btn{padding:7px 12px;border-radius:var(--r);font-size:11px;font-weight:500;cursor:pointer;border:none;display:inline-flex;align-items:center;gap:4px}.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}.btn-secondary{background:var(--bg3);color:var(--text0);border:1px solid var(--border)}.btn-success{background:var(--emerald);color:white}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--border)}th{font-size:9px;font-weight:600;color:var(--text3);text-transform:uppercase;background:var(--bg3)}tbody tr:hover{background:var(--bg3)}.badge{display:inline-flex;padding:2px 7px;border-radius:4px;font-size:9px;font-weight:600}.badge.active,.badge.won,.badge.paid,.badge.completed{background:rgba(16,185,129,.1);color:var(--emerald)}.badge.lead,.badge.qualified,.badge.pending,.badge.in_progress{background:rgba(245,158,11,.1);color:var(--amber)}.badge.proposal,.badge.negotiation,.badge.draft{background:rgba(99,102,241,.1);color:var(--primary)}.badge.discovery{background:rgba(6,182,212,.1);color:var(--cyan)}.badge.high{background:rgba(244,63,94,.1);color:var(--rose)}.badge.medium{background:rgba(245,158,11,.1);color:var(--amber)}.badge.low{background:rgba(16,185,129,.1);color:var(--emerald)}.search-box{background:var(--bg2);border:1px solid var(--border);border-radius:9px;padding:12px;margin-bottom:14px}.search-row{display:flex;gap:8px}.search-input{flex:1;padding:9px 12px;background:var(--bg3);border:1px solid var(--border);border-radius:var(--r);color:var(--text0);font-size:11px}.search-input:focus{outline:none;border-color:var(--gold)}.result-item{padding:10px 14px;border-bottom:1px solid var(--border);cursor:pointer}.result-item:hover{background:var(--bg3)}.result-name{font-size:12px;font-weight:600;margin-bottom:2px}.result-meta{font-size:10px;color:var(--text3)}.empty-state{text-align:center;padding:36px;color:var(--text3)}.empty-state .icon{font-size:28px;margin-bottom:8px;opacity:.5}.chart-container{height:200px}.wa-box{background:linear-gradient(135deg,rgba(37,211,102,.08),rgba(37,211,102,.02));border:1px solid rgba(37,211,102,.12);border-radius:9px;padding:14px;margin-bottom:14px}.wa-box h3{color:#25D366;margin-bottom:9px;display:flex;align-items:center;gap:5px;font-size:12px}.template-card{background:var(--bg3);border-radius:var(--r);padding:9px;margin-bottom:5px;cursor:pointer;font-size:11px}.template-card:hover{background:var(--bg2)}.template-card .name{font-weight:600;margin-bottom:2px}.template-card .preview{font-size:10px;color:var(--text3)}@media(max-width:900px){.sidebar{display:none}.main{margin-left:0}.stats-grid{grid-template-columns:repeat(2,1fr)}.grid-2{grid-template-columns:1fr}}@media(max-width:600px){.stats-grid{grid-template-columns:1fr}}</style></head>
<body>
<div class="login" id="loginScreen"><div class="login-box"><div class="login-logo"><div class="login-logo-icon">⚡</div><h1>West Money OS</h1><p>v8.0 GODMODE</p></div><div class="login-error" id="loginError">Fehler</div><div class="form-group"><label>Benutzername</label><input class="form-input" id="loginUser" value="admin"></div><div class="form-group"><label>Passwort</label><input class="form-input" type="password" id="loginPass" onkeypress="if(event.key==='Enter')doLogin()"></div><button class="login-btn" onclick="doLogin()">🔐 Anmelden</button><div class="demo-link"><a href="/demo">🚀 Demo</a> | <a href="/register">Registrieren</a></div></div></div>
<div class="app" id="app"><aside class="sidebar"><div class="sidebar-header"><div class="logo"><div class="logo-icon">⚡</div><div class="logo-text"><h1>West Money OS</h1><span>v8.0 GODMODE</span></div></div></div><nav class="sidebar-nav"><div class="nav-section"><div class="nav-section-title">Übersicht</div><div class="nav-item active" data-page="dashboard"><span>📊</span>Dashboard</div></div><div class="nav-section"><div class="nav-section-title">CRM</div><div class="nav-item" data-page="contacts"><span>👥</span>Kontakte</div><div class="nav-item" data-page="leads"><span>🎯</span>Leads</div><div class="nav-item" data-page="tasks"><span>📋</span>Tasks</div></div><div class="nav-section"><div class="nav-section-title">Kommunikation</div><div class="nav-item" data-page="whatsapp"><span>📱</span>WhatsApp<span class="badge new">API</span></div><div class="nav-item" data-page="campaigns"><span>📧</span>Kampagnen</div></div><div class="nav-section"><div class="nav-section-title">Integrationen</div><div class="nav-item" data-page="handelsregister"><span>🏛️</span>Handelsregister<span class="badge live">LIVE</span></div><div class="nav-item" data-page="hubspot"><span>🔗</span>HubSpot<span class="badge api">SYNC</span></div><div class="nav-item" data-page="crypto"><span>₿</span>Crypto<span class="badge new">API</span></div></div><div class="nav-section"><div class="nav-section-title">Enterprise</div><div class="nav-item" data-page="automations"><span>🤖</span>Automations</div><div class="nav-item" data-page="security"><span>🛡️</span>Security</div></div><div class="nav-section"><div class="nav-section-title">Finanzen</div><div class="nav-item" data-page="invoices"><span>📄</span>Rechnungen</div></div></nav><div class="sidebar-footer"><div class="user-card"><div class="user-avatar" id="userAvatar">??</div><div class="user-info"><div class="name" id="userName">User</div><div class="role" id="userRole">-</div></div><button class="logout-btn" onclick="doLogout()">🚪</button></div></div></aside>
<main class="main"><header class="topbar"><div class="breadcrumb">West Money OS / <strong id="currentPage">Dashboard</strong></div><div class="topbar-right"><button class="notif-btn" onclick="showNotif()">🔔<span class="count" id="notifCount">0</span></button><div class="demo-badge" id="demoBadge" style="display:none">DEMO</div></div></header>
<div class="content">
<div class="page active" id="page-dashboard"><div class="page-header"><div><h1>📊 Dashboard</h1><p>Ihr Überblick</p></div></div><div class="stats-grid"><div class="stat-card gold"><div class="label">Umsatz</div><div class="value" id="statRevenue">€0</div><div class="change" id="revenueGrowth">↑ 0%</div></div><div class="stat-card emerald"><div class="label">Leads</div><div class="value" id="statLeads">0</div><div class="change" id="leadsGrowth">↑ 0%</div></div><div class="stat-card amber"><div class="label">Kunden</div><div class="value" id="statCustomers">0</div><div class="change" id="customersGrowth">↑ 0%</div></div><div class="stat-card violet"><div class="label">MRR</div><div class="value" id="statMRR">€0</div><div class="change" id="mrrGrowth">↑ 0%</div></div></div><div class="grid-2"><div class="card"><div class="card-header"><h3>📈 Umsatz</h3></div><div class="card-body"><div class="chart-container"><canvas id="revenueChart"></canvas></div></div></div><div class="card"><div class="card-header"><h3>📊 MRR</h3></div><div class="card-body"><div class="chart-container"><canvas id="mrrChart"></canvas></div></div></div></div></div>
<div class="page" id="page-contacts"><div class="page-header"><div><h1>👥 Kontakte</h1></div><div><button class="btn btn-secondary" onclick="exportCSV('contacts')">📥 Export</button> <button class="btn btn-gold">+ Neu</button></div></div><div class="card"><div class="card-body no-padding"><table><thead><tr><th>Name</th><th>E-Mail</th><th>Unternehmen</th><th>WA</th><th>Score</th><th>Status</th></tr></thead><tbody id="contactsTable"></tbody></table></div></div></div>
<div class="page" id="page-leads"><div class="page-header"><div><h1>🎯 Leads</h1></div><button class="btn btn-gold">+ Neu</button></div><div class="stats-grid" style="grid-template-columns:repeat(2,1fr)"><div class="stat-card gold"><div class="label">Pipeline</div><div class="value" id="pipelineValue">€0</div></div><div class="stat-card emerald"><div class="label">Gewichtet</div><div class="value" id="weightedValue">€0</div></div></div><div class="card"><div class="card-body no-padding"><table><thead><tr><th>Projekt</th><th>Unternehmen</th><th>Wert</th><th>Phase</th><th>%</th></tr></thead><tbody id="leadsTable"></tbody></table></div></div></div>
<div class="page" id="page-tasks"><div class="page-header"><div><h1>📋 Tasks</h1></div><button class="btn btn-gold">+ Neu</button></div><div class="card"><div class="card-body no-padding"><table><thead><tr><th>Aufgabe</th><th>Priorität</th><th>Fällig</th><th>Status</th></tr></thead><tbody id="tasksTable"></tbody></table></div></div></div>
<div class="page" id="page-whatsapp"><div class="page-header"><div><h1>📱 WhatsApp</h1><p>Nachrichten senden</p></div></div><div class="stats-grid" style="grid-template-columns:repeat(3,1fr)"><div class="stat-card emerald"><div class="label">Gesendet</div><div class="value" id="waSent">0</div></div><div class="stat-card gold"><div class="label">Zugestellt</div><div class="value" id="waDelivered">0</div></div><div class="stat-card cyan"><div class="label">Gelesen</div><div class="value" id="waRead">0</div></div></div><div class="wa-box"><h3>📱 Nachricht</h3><div class="search-row" style="margin-bottom:8px"><input class="search-input" id="waPhone" placeholder="Telefon (491701234567)"></div><div class="search-row"><input class="search-input" id="waMessage" placeholder="Nachricht..." style="flex:2"><button class="btn btn-success" onclick="sendWA()">📤</button></div></div><div class="card"><div class="card-header"><h3>📋 Templates</h3></div><div class="card-body" id="waTemplates"></div></div></div>
<div class="page" id="page-campaigns"><div class="page-header"><div><h1>📧 Kampagnen</h1></div></div><div class="card"><div class="card-body no-padding"><table><thead><tr><th>Name</th><th>Typ</th><th>Gesendet</th><th>Geöffnet</th><th>Status</th></tr></thead><tbody id="campaignsTable"></tbody></table></div></div></div>
<div class="page" id="page-handelsregister"><div class="page-header"><div><h1>🏛️ Handelsregister</h1><p>LIVE Suche</p></div></div><div class="search-box"><div class="search-row"><input class="search-input" id="hrQuery" placeholder="🔍 Firmenname..." onkeypress="if(event.key==='Enter')searchHR()"><button class="btn btn-gold" onclick="searchHR()">Suchen</button></div></div><div class="card"><div class="card-header"><h3>Ergebnisse</h3><span id="hrResultCount">0</span></div><div class="card-body no-padding" id="hrResults"><div class="empty-state"><div class="icon">🏛️</div><p>Suche starten</p></div></div></div></div>
<div class="page" id="page-hubspot"><div class="page-header"><div><h1>🔗 HubSpot</h1></div></div><div class="card"><div class="card-header"><h3>Status</h3></div><div class="card-body"><p style="margin-bottom:12px"><strong>Verbunden:</strong> <span id="hubspotStatus">Prüfen...</span></p><button class="btn btn-gold" onclick="syncHubSpot()">🔄 Sync</button></div></div></div>
<div class="page" id="page-crypto"><div class="page-header"><div><h1>₿ Crypto</h1><p>Live Preise</p></div></div><div class="stats-grid" style="grid-template-columns:repeat(3,1fr)"><div class="stat-card gold"><div class="label">Bitcoin</div><div class="value" id="btcPrice">€0</div></div><div class="stat-card violet"><div class="label">Ethereum</div><div class="value" id="ethPrice">€0</div></div><div class="stat-card cyan"><div class="label">Solana</div><div class="value" id="solPrice">€0</div></div></div><div class="card"><div class="card-header"><h3>💱 Wechselkurse (EUR)</h3></div><div class="card-body" id="exchangeRates">Laden...</div></div></div>
<div class="page" id="page-automations"><div class="page-header"><div><h1>🤖 Automations</h1></div></div><div class="stats-grid" style="grid-template-columns:repeat(3,1fr)"><div class="stat-card gold"><div class="label">Systeme</div><div class="value" id="autoSystems">0</div></div><div class="stat-card emerald"><div class="label">Geräte</div><div class="value" id="autoDevices">0</div></div><div class="stat-card cyan"><div class="label">Energie</div><div class="value" id="autoEnergy">0</div></div></div></div>
<div class="page" id="page-security"><div class="page-header"><div><h1>🛡️ Security</h1></div></div><div class="stats-grid"><div class="stat-card emerald"><div class="label">Blocked</div><div class="value" id="secThreats">0</div></div><div class="stat-card gold"><div class="label">Protected</div><div class="value" id="secSystems">0</div></div><div class="stat-card cyan"><div class="label">Uptime</div><div class="value" id="secUptime">0%</div></div><div class="stat-card violet"><div class="label">Score</div><div class="value" id="secScore">0</div></div></div></div>
<div class="page" id="page-invoices"><div class="page-header"><div><h1>📄 Rechnungen</h1></div><button class="btn btn-gold">+ Neu</button></div><div class="card"><div class="card-body no-padding"><table><thead><tr><th>Nr.</th><th>Kunde</th><th>Betrag</th><th>Fällig</th><th>Status</th></tr></thead><tbody id="invoicesTable"></tbody></table></div></div></div>
</div></main></div>
<div id="notifModal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.7);z-index:1000;align-items:center;justify-content:center"><div style="background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:20px;max-width:380px;width:90%"><h3 style="margin-bottom:14px;display:flex;justify-content:space-between;align-items:center">🔔 Benachrichtigungen <button onclick="closeNotif()" style="background:none;border:none;color:var(--text2);cursor:pointer;font-size:16px">✕</button></h3><div id="notifList"></div><button class="btn btn-secondary" style="width:100%;margin-top:10px" onclick="markAllRead()">Alle gelesen</button></div></div>
<script>
let revenueChart,mrrChart,hrResults=[];
async function checkAuth(){try{const r=await fetch('/api/auth/status');const d=await r.json();if(d.authenticated)showApp(d.user)}catch(e){}}
async function doLogin(){const u=document.getElementById('loginUser').value,p=document.getElementById('loginPass').value;try{const r=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});const d=await r.json();if(d.success){document.getElementById('loginError').classList.remove('show');showApp(d.user)}else{document.getElementById('loginError').textContent=d.error||'Fehler';document.getElementById('loginError').classList.add('show')}}catch(e){document.getElementById('loginError').classList.add('show')}}
async function doLogout(){await fetch('/api/auth/logout',{method:'POST'});location.reload()}
function showApp(user){document.getElementById('loginScreen').style.display='none';document.getElementById('app').classList.add('active');document.getElementById('userName').textContent=user.name||'User';document.getElementById('userAvatar').textContent=user.avatar||'??';document.getElementById('userRole').textContent=user.role||'-';if(user.role==='Demo')document.getElementById('demoBadge').style.display='block';loadAll()}
document.querySelectorAll('.nav-item[data-page]').forEach(item=>{item.addEventListener('click',()=>{const page=item.dataset.page;document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));item.classList.add('active');document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.getElementById('page-'+page).classList.add('active');document.getElementById('currentPage').textContent=item.textContent.trim();if(page==='crypto')loadCrypto()})});
async function loadAll(){await Promise.all([loadDashboard(),loadContacts(),loadLeads(),loadTasks(),loadCampaigns(),loadInvoices(),loadWhatsApp(),loadAutomations(),loadSecurity(),loadNotifications()])}
async function loadDashboard(){try{const[stats,charts]=await Promise.all([fetch('/api/dashboard/stats').then(r=>r.json()),fetch('/api/dashboard/charts').then(r=>r.json())]);document.getElementById('statRevenue').textContent='€'+(stats.revenue||0).toLocaleString('de-DE');document.getElementById('statLeads').textContent=stats.leads||0;document.getElementById('statCustomers').textContent=stats.customers||0;document.getElementById('statMRR').textContent='€'+(stats.mrr||0).toLocaleString('de-DE');document.getElementById('revenueGrowth').textContent='↑ '+(stats.revenue_growth||0)+'%';document.getElementById('leadsGrowth').textContent='↑ '+(stats.leads_growth||0)+'%';document.getElementById('customersGrowth').textContent='↑ '+(stats.customers_growth||0)+'%';document.getElementById('mrrGrowth').textContent='↑ '+(stats.mrr_growth||0)+'%';if(revenueChart)revenueChart.destroy();revenueChart=new Chart(document.getElementById('revenueChart'),{type:'line',data:{labels:charts.labels,datasets:[{label:'Umsatz',data:charts.revenue,borderColor:'#fbbf24',backgroundColor:'rgba(251,191,36,0.1)',fill:true,tension:0.4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});if(mrrChart)mrrChart.destroy();mrrChart=new Chart(document.getElementById('mrrChart'),{type:'line',data:{labels:charts.labels,datasets:[{label:'MRR',data:charts.mrr,borderColor:'#8b5cf6',backgroundColor:'rgba(139,92,246,0.1)',fill:true,tension:0.4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}})}catch(e){console.error(e)}}
async function loadContacts(){try{const c=await fetch('/api/contacts').then(r=>r.json());document.getElementById('contactsTable').innerHTML=c.map(x=>'<tr><td><strong>'+esc(x.name)+'</strong><br><small style="color:var(--text3)">'+esc(x.position||'')+'</small></td><td>'+esc(x.email)+'</td><td>'+esc(x.company)+'</td><td>'+(x.whatsapp_consent?'✅':'❌')+'</td><td>'+(x.score||0)+'</td><td><span class="badge '+x.status+'">'+x.status+'</span></td></tr>').join('')}catch(e){}}
async function loadLeads(){try{const l=await fetch('/api/leads').then(r=>r.json());const t=l.reduce((s,x)=>s+(x.value||0),0);const w=l.reduce((s,x)=>s+((x.value||0)*(x.probability||0)/100),0);document.getElementById('pipelineValue').textContent='€'+t.toLocaleString('de-DE');document.getElementById('weightedValue').textContent='€'+Math.round(w).toLocaleString('de-DE');document.getElementById('leadsTable').innerHTML=l.map(x=>'<tr><td><strong>'+esc(x.name)+'</strong></td><td>'+esc(x.company)+'</td><td>€'+(x.value||0).toLocaleString('de-DE')+'</td><td><span class="badge '+x.stage+'">'+x.stage+'</span></td><td>'+x.probability+'%</td></tr>').join('')}catch(e){}}
async function loadTasks(){try{const t=await fetch('/api/tasks').then(r=>r.json());document.getElementById('tasksTable').innerHTML=t.map(x=>'<tr><td><strong>'+esc(x.title)+'</strong><br><small style="color:var(--text3)">'+esc(x.description||'')+'</small></td><td><span class="badge '+x.priority+'">'+x.priority+'</span></td><td>'+x.due_date+'</td><td><span class="badge '+x.status+'">'+x.status+'</span></td></tr>').join('')}catch(e){}}
async function loadCampaigns(){try{const c=await fetch('/api/campaigns').then(r=>r.json());document.getElementById('campaignsTable').innerHTML=c.map(x=>'<tr><td><strong>'+esc(x.name)+'</strong></td><td>'+x.type+'</td><td>'+x.sent+'</td><td>'+x.opened+' ('+(x.sent?Math.round(x.opened/x.sent*100):0)+'%)</td><td><span class="badge '+x.status+'">'+x.status+'</span></td></tr>').join('')}catch(e){}}
async function loadInvoices(){try{const i=await fetch('/api/invoices').then(r=>r.json());document.getElementById('invoicesTable').innerHTML=i.map(x=>'<tr><td><strong>'+x.id+'</strong></td><td>'+esc(x.customer)+'</td><td>€'+(x.total||0).toLocaleString('de-DE')+'</td><td>'+x.due+'</td><td><span class="badge '+x.status+'">'+x.status+'</span></td></tr>').join('')}catch(e){}}
async function loadWhatsApp(){try{const s=await fetch('/api/dashboard/stats').then(r=>r.json());document.getElementById('waSent').textContent=(s.whatsapp_sent||0).toLocaleString('de-DE');document.getElementById('waDelivered').textContent=(s.whatsapp_delivered||0).toLocaleString('de-DE');document.getElementById('waRead').textContent=(s.whatsapp_read||0).toLocaleString('de-DE');const t=await fetch('/api/whatsapp/templates').then(r=>r.json());document.getElementById('waTemplates').innerHTML=t.map(x=>'<div class="template-card" onclick="useTemplate(\\''+esc(x.text)+'\\')"><div class="name">'+x.name+'</div><div class="preview">'+x.text+'</div></div>').join('')}catch(e){}}
async function sendWA(){const p=document.getElementById('waPhone').value,m=document.getElementById('waMessage').value;if(!p||!m)return alert('Telefon und Nachricht eingeben');try{const r=await fetch('/api/whatsapp/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone:p,message:m})});const d=await r.json();if(d.success){alert(d.demo?'Demo: Simuliert!':'✅ Gesendet!');document.getElementById('waMessage').value=''}else alert('Fehler: '+(d.error||''))}catch(e){alert('Fehler')}}
function useTemplate(t){document.getElementById('waMessage').value=t.replace(/\{\{1\}\}/g,'[WERT1]').replace(/\{\{2\}\}/g,'[WERT2]')}
async function loadAutomations(){try{const d=await fetch('/api/automations/stats').then(r=>r.json());document.getElementById('autoSystems').textContent=d.active_systems||0;document.getElementById('autoDevices').textContent=(d.devices_connected||0).toLocaleString('de-DE');document.getElementById('autoEnergy').textContent=(d.energy_saved_kwh||0).toLocaleString('de-DE')+' kWh'}catch(e){}}
async function loadSecurity(){try{const d=await fetch('/api/security/stats').then(r=>r.json());document.getElementById('secThreats').textContent=(d.threats_blocked||0).toLocaleString('de-DE');document.getElementById('secSystems').textContent=d.systems_protected||0;document.getElementById('secUptime').textContent=(d.uptime_percent||0)+'%';document.getElementById('secScore').textContent=(d.security_score||0)+'/100'}catch(e){}}
async function loadNotifications(){try{const r=await fetch('/api/notifications/unread-count');const d=await r.json();document.getElementById('notifCount').textContent=d.count||0}catch(e){}}
async function showNotif(){try{const n=await fetch('/api/notifications').then(r=>r.json());document.getElementById('notifList').innerHTML=n.length?n.slice(0,10).map(x=>'<div style="padding:9px;border-bottom:1px solid var(--border);opacity:'+(x.read?'0.6':'1')+'"><strong>'+(x.icon||'📌')+' '+x.title+'</strong><p style="font-size:11px;color:var(--text2);margin:3px 0">'+x.message+'</p><small style="color:var(--text3)">'+x.created+'</small></div>').join(''):'<p style="text-align:center;color:var(--text3);padding:18px">Keine</p>';document.getElementById('notifModal').style.display='flex'}catch(e){}}
function closeNotif(){document.getElementById('notifModal').style.display='none'}
async function markAllRead(){await fetch('/api/notifications/mark-all-read',{method:'POST'});loadNotifications();closeNotif()}
async function syncHubSpot(){try{const r=await fetch('/api/hubspot/sync',{method:'POST'});const d=await r.json();alert(d.demo?'Demo: '+d.synced+' simuliert':'✅ '+d.synced+' synchronisiert!')}catch(e){alert('Fehler')}}
async function searchHR(){const q=document.getElementById('hrQuery').value.trim();if(!q)return alert('Suchbegriff');document.getElementById('hrResults').innerHTML='<div class="empty-state"><p>Suche...</p></div>';try{const r=await fetch('/api/hr/search?q='+encodeURIComponent(q));const data=await r.json();hrResults=data.results||[];document.getElementById('hrResultCount').textContent=hrResults.length+' Treffer';if(!hrResults.length){document.getElementById('hrResults').innerHTML='<div class="empty-state"><div class="icon">🔍</div><p>Keine</p></div>'}else{document.getElementById('hrResults').innerHTML=hrResults.map((r,i)=>'<div class="result-item" onclick="importHR('+i+')"><div class="result-name">'+esc(r.name)+'</div><div class="result-meta">'+esc(r.register_type)+' '+esc(r.register_number)+' | '+esc(r.city)+'</div></div>').join('')}}catch(e){document.getElementById('hrResults').innerHTML='<div class="empty-state"><p>Fehler</p></div>'}}
async function importHR(i){const r=hrResults[i];if(!r)return;if(confirm('Importieren: '+r.name+'?')){await fetch('/api/hr/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(r)});alert('✅ Importiert!');loadContacts()}}
async function loadCrypto(){try{const[c,e]=await Promise.all([fetch('/api/crypto/prices').then(r=>r.json()),fetch('/api/exchange-rates').then(r=>r.json())]);if(c.bitcoin)document.getElementById('btcPrice').textContent='€'+(c.bitcoin.eur||0).toLocaleString('de-DE');if(c.ethereum)document.getElementById('ethPrice').textContent='€'+(c.ethereum.eur||0).toLocaleString('de-DE');if(c.solana)document.getElementById('solPrice').textContent='€'+(c.solana.eur||0).toLocaleString('de-DE');const rates=e.rates||e;document.getElementById('exchangeRates').innerHTML='<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px">'+Object.entries({USD:rates.USD,GBP:rates.GBP,CHF:rates.CHF,JPY:rates.JPY}).map(([k,v])=>'<div style="background:var(--bg3);padding:10px;border-radius:7px;text-align:center"><div style="font-size:10px;color:var(--text3)">'+k+'</div><div style="font-size:16px;font-weight:700">'+(v||0).toFixed(k==='JPY'?1:2)+'</div></div>').join('')+'</div>'}catch(e){console.error(e)}}
function exportCSV(t){window.open('/api/export/'+t,'_blank')}
function esc(s){return s?String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;'):''}
checkAuth();
</script>
</body></html>'''

# PAGE ROUTES
@app.route('/')
def landing():
    return Response(LANDING_HTML, mimetype='text/html')

@app.route('/pricing')
def pricing():
    return Response(PRICING_HTML, mimetype='text/html')

@app.route('/demo')
def demo():
    return Response(DEMO_HTML, mimetype='text/html')

@app.route('/register')
def register_page():
    return Response(REGISTER_HTML, mimetype='text/html')

@app.route('/app')
def app_page():
    return Response(APP_HTML, mimetype='text/html')

if __name__ == '__main__':
    print("=" * 60)
    print("  ⚡ WEST MONEY OS v8.0 - GODMODE ULTIMATE")
    print("=" * 60)
    print(f"  🌐 http://localhost:{PORT}")
    print(f"  💳 http://localhost:{PORT}/pricing")
    print(f"  🎮 http://localhost:{PORT}/demo")
    print("=" * 60)
    print("  🔑 Admin: admin / 663724")
    print("  🎮 Demo:  demo / demo123")
    print("=" * 60)
    app.run(host='0.0.0.0', port=PORT, debug=False)
