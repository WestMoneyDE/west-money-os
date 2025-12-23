#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ⚡ WEST MONEY OS v7.0 - ULTIMATE ENTERPRISE PLATFORM ⚡               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  🏢 Enterprise Universe GmbH - Complete Business Suite                       ║
║  📱 WhatsApp Business API Integration                                        ║
║  💳 Stripe Payments & Subscriptions                                          ║
║  🔗 HubSpot CRM Sync                                                         ║
║  🤖 Automation & Workflows                                                   ║
║  © 2025 Ömer Hüseyin Coşkun - All Rights Reserved                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, jsonify, request, Response, session, redirect
from flask_cors import CORS
import requests
import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
import re

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# =============================================================================
# CONFIGURATION
# =============================================================================
PORT = int(os.getenv('PORT', 5000))
OPENCORPORATES_API_KEY = os.getenv('OPENCORPORATES_API_KEY', '')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', 'pk_live_xxx')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_live_xxx')
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')
WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID', '')
HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY', '')

# =============================================================================
# PRICING PLANS
# =============================================================================
PLANS = {
    'starter': {'name': 'Starter', 'price': 29, 'price_yearly': 290, 'stripe_price_monthly': 'price_starter_monthly', 'stripe_price_yearly': 'price_starter_yearly',
        'features': ['5 Kontakte', '3 Leads', 'Basic Dashboard', 'E-Mail Support', 'Handelsregister (10/Monat)'],
        'limits': {'contacts': 5, 'leads': 3, 'hr_searches': 10, 'whatsapp': False, 'hubspot': False}},
    'professional': {'name': 'Professional', 'price': 99, 'price_yearly': 990, 'stripe_price_monthly': 'price_pro_monthly', 'stripe_price_yearly': 'price_pro_yearly', 'popular': True,
        'features': ['Unbegrenzte Kontakte', 'Unbegrenzte Leads', 'Voller Dashboard', 'Priority Support', 'Handelsregister (100/Monat)', 'Explorium Integration', 'Kampagnen', 'WhatsApp Integration'],
        'limits': {'contacts': -1, 'leads': -1, 'hr_searches': 100, 'whatsapp': True, 'hubspot': False}},
    'enterprise': {'name': 'Enterprise', 'price': 299, 'price_yearly': 2990, 'stripe_price_monthly': 'price_ent_monthly', 'stripe_price_yearly': 'price_ent_yearly',
        'features': ['Alles aus Professional', 'Broly Automations', 'Einstein Agency', 'GTzMeta Gaming', 'FinTech & Crypto', 'DedSec Security', 'White Label', 'HubSpot Sync', 'API Access', 'Dedicated Support'],
        'limits': {'contacts': -1, 'leads': -1, 'hr_searches': -1, 'whatsapp': True, 'hubspot': True}}
}

# =============================================================================
# USERS DATABASE
# =============================================================================
USERS = {
    'admin': {'password': hashlib.sha256('663724'.encode()).hexdigest(), 'name': 'Ömer Coşkun', 'email': 'info@west-money.com', 'role': 'GOD MODE', 'company': 'Enterprise Universe GmbH', 'avatar': 'ÖC', 'plan': 'enterprise', 'created': '2025-01-01'},
    'demo': {'password': hashlib.sha256('demo123'.encode()).hexdigest(), 'name': 'Demo User', 'email': 'demo@west-money.com', 'role': 'Demo', 'company': 'Demo Company', 'avatar': 'DM', 'plan': 'professional', 'created': '2025-12-01'},
}

# =============================================================================
# ADMIN DATABASE (Real Data)
# =============================================================================
ADMIN_DB = {
    'contacts': [
        {'id': 1, 'name': 'Max Mustermann', 'email': 'max@techgmbh.de', 'company': 'Tech GmbH', 'phone': '+49 221 12345678', 'status': 'active', 'source': 'Website', 'created': '2025-12-01', 'whatsapp_consent': True},
        {'id': 2, 'name': 'Anna Schmidt', 'email': 'anna@startup.de', 'company': 'StartUp AG', 'phone': '+49 89 98765432', 'status': 'active', 'source': 'Handelsregister', 'created': '2025-12-05', 'whatsapp_consent': True},
        {'id': 3, 'name': 'Thomas Weber', 'email': 'weber@industrie.de', 'company': 'Industrie KG', 'phone': '+49 211 55555555', 'status': 'lead', 'source': 'Explorium', 'created': '2025-12-10', 'whatsapp_consent': False},
        {'id': 4, 'name': 'Julia Becker', 'email': 'j.becker@finance.de', 'company': 'Finance Plus GmbH', 'phone': '+49 69 44444444', 'status': 'active', 'source': 'Messe', 'created': '2025-12-12', 'whatsapp_consent': True},
        {'id': 5, 'name': 'LOXONE Partner', 'email': 'partner@loxone.com', 'company': 'LOXONE', 'phone': '+43 7612 90901', 'status': 'active', 'source': 'Partner', 'created': '2025-11-01', 'whatsapp_consent': True},
    ],
    'leads': [
        {'id': 1, 'name': 'Smart Home Villa', 'company': 'Private Investor', 'contact': 'Dr. Hans Meier', 'email': 'meier@gmail.com', 'phone': '+49 170 1234567', 'value': 185000, 'stage': 'proposal', 'probability': 75, 'created': '2025-12-01', 'source': 'Website'},
        {'id': 2, 'name': 'Bürogebäude Automation', 'company': 'Corporate Real Estate', 'contact': 'Maria Corporate', 'email': 'maria@corporate.de', 'phone': '+49 171 9876543', 'value': 450000, 'stage': 'negotiation', 'probability': 85, 'created': '2025-12-05', 'source': 'Referral'},
        {'id': 3, 'name': 'Hotel Automation', 'company': 'Luxus Hotels AG', 'contact': 'Peter Luxus', 'email': 'peter@luxushotels.de', 'phone': '+49 172 5555555', 'value': 890000, 'stage': 'qualified', 'probability': 60, 'created': '2025-12-10', 'source': 'Messe'},
        {'id': 4, 'name': 'Restaurant Beleuchtung', 'company': 'Gastro Excellence', 'contact': 'Tom Gastro', 'email': 'tom@gastro.de', 'phone': '+49 173 4444444', 'value': 45000, 'stage': 'won', 'probability': 100, 'created': '2025-11-20', 'source': 'Google'},
    ],
    'campaigns': [
        {'id': 1, 'name': 'Q4 Newsletter', 'type': 'email', 'status': 'active', 'sent': 2500, 'opened': 1125, 'clicked': 340, 'converted': 28, 'created': '2025-10-01'},
        {'id': 2, 'name': 'Smart Home Launch', 'type': 'email', 'status': 'completed', 'sent': 5000, 'opened': 2750, 'clicked': 890, 'converted': 67, 'created': '2025-09-15'},
        {'id': 3, 'name': 'WhatsApp Promo', 'type': 'whatsapp', 'status': 'active', 'sent': 850, 'opened': 780, 'clicked': 320, 'converted': 45, 'created': '2025-12-01'},
    ],
    'invoices': [
        {'id': 'INV-2025-001', 'customer': 'Tech GmbH', 'email': 'billing@techgmbh.de', 'amount': 1188, 'status': 'paid', 'date': '2025-12-01', 'due': '2025-12-15', 'items': 'Professional Plan (12 Monate)'},
        {'id': 'INV-2025-002', 'customer': 'StartUp AG', 'email': 'finance@startup.de', 'amount': 3588, 'status': 'paid', 'date': '2025-12-01', 'due': '2025-12-15', 'items': 'Enterprise Plan (12 Monate)'},
        {'id': 'INV-2025-003', 'customer': 'Smart Home Villa', 'email': 'meier@gmail.com', 'amount': 45000, 'status': 'pending', 'date': '2025-12-15', 'due': '2025-12-30', 'items': 'LOXONE Installation Anzahlung'},
        {'id': 'INV-2025-004', 'customer': 'Bürogebäude Corp', 'email': 'maria@corporate.de', 'amount': 112500, 'status': 'pending', 'date': '2025-12-20', 'due': '2026-01-05', 'items': 'Building Automation Phase 1'},
    ],
    'notifications': [
        {'id': 1, 'type': 'deal', 'title': 'Neuer Deal gewonnen!', 'message': 'Restaurant Beleuchtung - €45.000', 'read': False, 'created': '2025-12-21 16:30'},
        {'id': 2, 'type': 'lead', 'title': 'Neuer Lead', 'message': 'Hotel Automation - Luxus Hotels AG', 'read': True, 'created': '2025-12-20 10:15'},
        {'id': 3, 'type': 'payment', 'title': 'Zahlung erhalten', 'message': 'Tech GmbH - €1.188', 'read': True, 'created': '2025-12-15 09:00'},
        {'id': 4, 'type': 'whatsapp', 'title': 'WhatsApp Nachricht', 'message': 'Neue Anfrage von +49 170 1234567', 'read': False, 'created': '2025-12-23 14:22'},
    ],
    'stats': {
        'revenue': 1247000, 'revenue_growth': 28.5, 'leads': 67, 'leads_growth': 22,
        'customers': 234, 'customers_growth': 18, 'mrr': 18750, 'mrr_growth': 12.4,
        'churn': 1.8, 'ltv': 4250, 'cac': 380, 'nps': 78,
        'whatsapp_sent': 1250, 'whatsapp_delivered': 1180, 'email_sent': 8500
    },
    'chart_data': {
        'labels': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
        'revenue': [62000, 78000, 81000, 97000, 102000, 99000, 118000, 132000, 149000, 165000, 182000, 247000],
        'leads': [28, 35, 32, 41, 38, 45, 52, 48, 56, 62, 58, 67],
        'mrr': [9200, 10800, 11100, 12600, 13200, 14500, 15000, 16400, 16900, 17200, 17850, 18750]
    }
}

# =============================================================================
# DEMO DATABASE (Fake Data for Demo Users)
# =============================================================================
DEMO_DB = {
    'contacts': [
        {'id': 1, 'name': 'Demo Kontakt 1', 'email': 'demo1@example.com', 'company': 'Demo GmbH', 'phone': '+49 123 456789', 'status': 'active', 'source': 'Demo', 'created': '2025-12-01', 'whatsapp_consent': True},
        {'id': 2, 'name': 'Demo Kontakt 2', 'email': 'demo2@example.com', 'company': 'Test AG', 'phone': '+49 987 654321', 'status': 'lead', 'source': 'Website', 'created': '2025-12-10', 'whatsapp_consent': False},
        {'id': 3, 'name': 'Demo Kontakt 3', 'email': 'demo3@example.com', 'company': 'Sample Corp', 'phone': '+49 555 123456', 'status': 'active', 'source': 'Referral', 'created': '2025-12-15', 'whatsapp_consent': True},
    ],
    'leads': [
        {'id': 1, 'name': 'Demo Projekt A', 'company': 'Demo Kunde', 'contact': 'Max Demo', 'email': 'max@demo.de', 'phone': '+49 170 0000001', 'value': 25000, 'stage': 'proposal', 'probability': 60, 'created': '2025-12-01', 'source': 'Demo'},
        {'id': 2, 'name': 'Demo Projekt B', 'company': 'Test Firma', 'contact': 'Lisa Test', 'email': 'lisa@test.de', 'phone': '+49 170 0000002', 'value': 45000, 'stage': 'qualified', 'probability': 40, 'created': '2025-12-10', 'source': 'Demo'},
    ],
    'campaigns': [
        {'id': 1, 'name': 'Demo Newsletter', 'type': 'email', 'status': 'active', 'sent': 100, 'opened': 45, 'clicked': 12, 'converted': 2, 'created': '2025-12-01'},
    ],
    'invoices': [
        {'id': 'DEMO-001', 'customer': 'Demo Kunde', 'email': 'demo@example.com', 'amount': 990, 'status': 'paid', 'date': '2025-12-01', 'due': '2025-12-15', 'items': 'Demo Plan'},
    ],
    'notifications': [
        {'id': 1, 'type': 'info', 'title': 'Willkommen zur Demo!', 'message': 'Erkunden Sie alle Features', 'read': False, 'created': '2025-12-23'},
    ],
    'stats': {
        'revenue': 125000, 'revenue_growth': 15.2, 'leads': 12, 'leads_growth': 8,
        'customers': 24, 'customers_growth': 12, 'mrr': 2450, 'mrr_growth': 5.4,
        'churn': 2.1, 'ltv': 1200, 'cac': 180, 'nps': 65,
        'whatsapp_sent': 50, 'whatsapp_delivered': 48, 'email_sent': 200
    },
    'chart_data': {
        'labels': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
        'revenue': [8000, 9500, 11000, 12500, 14000, 15500, 17000, 19000, 21000, 23000, 25000, 28000],
        'leads': [3, 4, 5, 6, 5, 7, 8, 7, 9, 10, 11, 12],
        'mrr': [1200, 1400, 1550, 1700, 1850, 1950, 2100, 2200, 2300, 2350, 2400, 2450]
    }
}

def get_db():
    """Get database based on current user"""
    if session.get('user') == 'demo':
        return DEMO_DB
    return ADMIN_DB

# =============================================================================
# AUTH ROUTES
# =============================================================================
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
        return jsonify({'success': False, 'error': 'Alle Felder ausfüllen'}), 400
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'success': False, 'error': 'Ungültige E-Mail'}), 400
    username = email.split('@')[0]
    if username in USERS:
        return jsonify({'success': False, 'error': 'Benutzer existiert bereits'}), 400
    USERS[username] = {
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'name': name, 'email': email, 'role': 'User', 'company': company,
        'avatar': name[:2].upper(), 'plan': 'starter', 'created': datetime.now().strftime('%Y-%m-%d')
    }
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

# =============================================================================
# DASHBOARD
# =============================================================================
@app.route('/api/dashboard/stats')
def dashboard_stats():
    return jsonify(get_db()['stats'])

@app.route('/api/dashboard/charts')
def dashboard_charts():
    return jsonify(get_db()['chart_data'])

@app.route('/api/notifications')
def get_notifications():
    return jsonify(get_db()['notifications'])

@app.route('/api/notifications/<int:id>/read', methods=['POST'])
def mark_notification_read(id):
    db = get_db()
    for n in db['notifications']:
        if n['id'] == id:
            n['read'] = True
    return jsonify({'success': True})

# =============================================================================
# CONTACTS
# =============================================================================
@app.route('/api/contacts')
def get_contacts():
    return jsonify(get_db()['contacts'])

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    db = get_db()
    data = request.json
    new_id = max([c['id'] for c in db['contacts']], default=0) + 1
    contact = {
        'id': new_id, 'name': data.get('name', ''), 'email': data.get('email', ''),
        'company': data.get('company', ''), 'phone': data.get('phone', ''),
        'status': 'lead', 'source': data.get('source', 'Manual'),
        'created': datetime.now().strftime('%Y-%m-%d'), 'whatsapp_consent': False
    }
    db['contacts'].append(contact)
    return jsonify(contact)

@app.route('/api/contacts/<int:id>/whatsapp-consent', methods=['POST'])
def update_whatsapp_consent(id):
    db = get_db()
    data = request.json
    for c in db['contacts']:
        if c['id'] == id:
            c['whatsapp_consent'] = data.get('consent', False)
            return jsonify({'success': True})
    return jsonify({'success': False}), 404

# =============================================================================
# LEADS
# =============================================================================
@app.route('/api/leads')
def get_leads():
    return jsonify(get_db()['leads'])

@app.route('/api/leads', methods=['POST'])
def create_lead():
    db = get_db()
    data = request.json
    new_id = max([l['id'] for l in db['leads']], default=0) + 1
    lead = {
        'id': new_id, 'name': data.get('name', ''), 'company': data.get('company', ''),
        'contact': data.get('contact', ''), 'email': data.get('email', ''),
        'phone': data.get('phone', ''), 'value': int(data.get('value', 0)),
        'stage': 'discovery', 'probability': 10,
        'created': datetime.now().strftime('%Y-%m-%d'), 'source': data.get('source', 'Manual')
    }
    db['leads'].append(lead)
    return jsonify(lead)

@app.route('/api/leads/<int:id>/stage', methods=['POST'])
def update_lead_stage(id):
    db = get_db()
    data = request.json
    stages_prob = {'discovery': 10, 'qualified': 30, 'proposal': 50, 'negotiation': 75, 'won': 100, 'lost': 0}
    for l in db['leads']:
        if l['id'] == id:
            l['stage'] = data.get('stage', l['stage'])
            l['probability'] = stages_prob.get(l['stage'], l['probability'])
            return jsonify({'success': True, 'lead': l})
    return jsonify({'success': False}), 404

# =============================================================================
# CAMPAIGNS
# =============================================================================
@app.route('/api/campaigns')
def get_campaigns():
    return jsonify(get_db()['campaigns'])

# =============================================================================
# INVOICES
# =============================================================================
@app.route('/api/invoices')
def get_invoices():
    return jsonify(get_db()['invoices'])

# =============================================================================
# WHATSAPP INTEGRATION
# =============================================================================
@app.route('/api/whatsapp/send', methods=['POST'])
def whatsapp_send():
    if session.get('user') == 'demo':
        return jsonify({'success': True, 'message': 'Demo: WhatsApp Nachricht simuliert', 'demo': True})
    data = request.json
    phone = data.get('phone', '').replace(' ', '').replace('+', '')
    message = data.get('message', '')
    template = data.get('template')
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        return jsonify({'success': False, 'error': 'WhatsApp nicht konfiguriert'})
    try:
        url = f'https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages'
        headers = {'Authorization': f'Bearer {WHATSAPP_TOKEN}', 'Content-Type': 'application/json'}
        payload = {'messaging_product': 'whatsapp', 'to': phone}
        if template:
            payload['type'] = 'template'
            payload['template'] = {'name': template, 'language': {'code': 'de'}}
        else:
            payload['type'] = 'text'
            payload['text'] = {'body': message}
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return jsonify({'success': r.status_code == 200, 'response': r.json()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token')
        if verify_token == 'westmoney_verify_token':
            return request.args.get('hub.challenge', '')
        return 'Invalid token', 403
    data = request.json
    # Process incoming WhatsApp messages here
    return jsonify({'success': True})

@app.route('/api/whatsapp/templates')
def whatsapp_templates():
    return jsonify([
        {'name': 'welcome', 'text': 'Willkommen bei West Money! Wie können wir Ihnen helfen?'},
        {'name': 'appointment', 'text': 'Ihr Termin wurde bestätigt für {{1}} um {{2}} Uhr.'},
        {'name': 'quote', 'text': 'Vielen Dank für Ihre Anfrage. Ihr Angebot: {{1}}'},
        {'name': 'followup', 'text': 'Haben Sie noch Fragen zu unserem Angebot?'},
    ])

# =============================================================================
# HUBSPOT INTEGRATION
# =============================================================================
@app.route('/api/hubspot/sync', methods=['POST'])
def hubspot_sync():
    if session.get('user') == 'demo':
        return jsonify({'success': True, 'message': 'Demo: HubSpot Sync simuliert', 'synced': 5, 'demo': True})
    if not HUBSPOT_API_KEY:
        return jsonify({'success': False, 'error': 'HubSpot nicht konfiguriert'})
    try:
        db = get_db()
        synced = 0
        for contact in db['contacts']:
            url = 'https://api.hubapi.com/crm/v3/objects/contacts'
            headers = {'Authorization': f'Bearer {HUBSPOT_API_KEY}', 'Content-Type': 'application/json'}
            payload = {'properties': {'email': contact['email'], 'firstname': contact['name'].split()[0] if contact['name'] else '', 'lastname': ' '.join(contact['name'].split()[1:]) if contact['name'] else '', 'company': contact['company'], 'phone': contact['phone']}}
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            if r.status_code in [200, 201]:
                synced += 1
        return jsonify({'success': True, 'synced': synced})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/hubspot/status')
def hubspot_status():
    return jsonify({'connected': bool(HUBSPOT_API_KEY), 'api_key_set': bool(HUBSPOT_API_KEY)})

# =============================================================================
# STRIPE INTEGRATION
# =============================================================================
@app.route('/api/stripe/create-checkout', methods=['POST'])
def stripe_create_checkout():
    data = request.json or {}
    plan = data.get('plan', 'starter')
    billing = data.get('billing', 'monthly')
    if plan not in PLANS:
        return jsonify({'success': False, 'error': 'Invalid plan'}), 400
    price_key = 'stripe_price_yearly' if billing == 'yearly' else 'stripe_price_monthly'
    price_id = PLANS[plan].get(price_key)
    # In production, create actual Stripe checkout session
    # For now, return demo checkout URL
    return jsonify({
        'success': True,
        'checkout_url': f'https://checkout.stripe.com/c/pay/demo_{plan}_{billing}',
        'plan': plan,
        'billing': billing,
        'price': PLANS[plan]['price'] if billing == 'monthly' else PLANS[plan]['price_yearly']
    })

@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    # Verify webhook signature and process events
    return jsonify({'received': True})

@app.route('/api/stripe/portal', methods=['POST'])
def stripe_portal():
    # Create Stripe customer portal session
    return jsonify({'url': 'https://billing.stripe.com/p/demo_portal'})

# =============================================================================
# HANDELSREGISTER
# =============================================================================
@app.route('/api/hr/search')
def hr_search():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'results': [], 'total': 0})
    try:
        url = 'https://api.opencorporates.com/v0.4/companies/search'
        params = {'q': q, 'jurisdiction_code': 'de', 'per_page': 20}
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
            results.append({
                'id': c.get('company_number', ''), 'name': c.get('name', ''),
                'register_type': reg_type, 'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv',
                'type': c.get('company_type', ''), 'city': addr.get('locality', ''),
                'address': ', '.join(filter(None, [addr.get('street_address'), addr.get('postal_code'), addr.get('locality')])),
                'founded': c.get('incorporation_date', ''), 'url': c.get('opencorporates_url', '')
            })
        return jsonify({'success': True, 'results': results, 'total': data.get('results', {}).get('total_count', 0)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'results': []})

@app.route('/api/hr/import', methods=['POST'])
def hr_import():
    db = get_db()
    data = request.json
    new_id = max([c['id'] for c in db['contacts']], default=0) + 1
    contact = {
        'id': new_id, 'name': data.get('name', ''), 'email': '',
        'company': data.get('name', ''), 'phone': '',
        'status': 'lead', 'source': 'Handelsregister',
        'created': datetime.now().strftime('%Y-%m-%d'), 'whatsapp_consent': False
    }
    db['contacts'].append(contact)
    return jsonify({'success': True, 'contact': contact})

# =============================================================================
# EXPLORIUM / ADDITIONAL APIs
# =============================================================================
@app.route('/api/explorium/stats')
def explorium_stats():
    return jsonify({'credits': 4873, 'plan': 'Professional', 'searches': 89, 'enrichments': 156})

@app.route('/api/gaming/stats')
def gaming_stats():
    return jsonify({'twitch_followers': 15420, 'youtube_subs': 8750, 'discord_members': 3240, 'peak_viewers': 12500, 'total_streams': 287})

@app.route('/api/automations/stats')
def automations_stats():
    return jsonify({'active_systems': 47, 'devices_connected': 2840, 'energy_saved_kwh': 45200, 'co2_reduced_kg': 18900})

@app.route('/api/security/stats')
def security_stats():
    return jsonify({'threats_blocked': 1247, 'systems_protected': 58, 'uptime_percent': 99.97, 'security_score': 94})

# =============================================================================
# PLANS & PRICING
# =============================================================================
@app.route('/api/plans')
def get_plans():
    return jsonify(PLANS)

# =============================================================================
# HEALTH & STATUS
# =============================================================================
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy', 'version': '7.0.0', 'service': 'West Money OS Ultimate',
        'timestamp': datetime.now().isoformat(),
        'integrations': {
            'whatsapp': bool(WHATSAPP_TOKEN),
            'hubspot': bool(HUBSPOT_API_KEY),
            'stripe': bool(STRIPE_SECRET_KEY),
            'handelsregister': True
        }
    })

# =============================================================================
# ROUTES
# =============================================================================
@app.route('/')
def landing():
    return Response(LANDING_HTML, mimetype='text/html')

@app.route('/pricing')
def pricing():
    return Response(PRICING_HTML, mimetype='text/html')

@app.route('/demo')
def demo():
    return Response(DEMO_HTML, mimetype='text/html')

@app.route('/app')
def app_page():
    return Response(APP_HTML, mimetype='text/html')

@app.route('/register')
def register_page():
    return Response(REGISTER_HTML, mimetype='text/html')

# =============================================================================
# HTML TEMPLATES
# =============================================================================
LANDING_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>West Money OS | Die All-in-One Business Platform</title>
<meta name="description" content="CRM, Smart Home Automation, WhatsApp Business, FinTech - alles in einer Plattform. Jetzt kostenlos testen!">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
:root{--bg:#09090b;--bg-2:#131316;--bg-3:#1a1a1f;--text:#fafafa;--text-2:#a1a1aa;--text-3:#71717a;--gold:#fbbf24;--orange:#f97316;--emerald:#10b981;--primary:#6366f1;--border:rgba(255,255,255,.06)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
.nav{position:fixed;top:0;left:0;right:0;background:rgba(9,9,11,.9);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);z-index:100;padding:0 24px}
.nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:72px}
.nav-logo{display:flex;align-items:center;gap:12px;font-size:20px;font-weight:700;text-decoration:none;color:var(--text)}
.nav-logo span{background:linear-gradient(135deg,var(--gold),var(--orange));width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center}
.nav-links{display:flex;gap:32px}
.nav-links a{color:var(--text-2);text-decoration:none;font-size:14px;transition:color .2s}
.nav-links a:hover{color:var(--text)}
.nav-btns{display:flex;gap:12px}
.btn{padding:10px 20px;border-radius:8px;font-size:14px;font-weight:500;text-decoration:none;transition:all .2s;cursor:pointer;border:none;display:inline-flex;align-items:center;gap:6px}
.btn-ghost{background:transparent;color:var(--text);border:1px solid var(--border)}
.btn-ghost:hover{background:var(--bg-2);border-color:rgba(255,255,255,.1)}
.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;font-weight:600}
.btn-gold:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(251,191,36,.25)}
.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:120px 24px 80px;background:radial-gradient(ellipse at top,rgba(251,191,36,.06) 0%,transparent 60%)}
.hero-content{max-width:900px}
.hero-badge{display:inline-flex;align-items:center;gap:8px;background:var(--bg-2);border:1px solid var(--border);padding:8px 16px;border-radius:24px;font-size:13px;color:var(--text-2);margin-bottom:28px}
.hero-badge .dot{width:8px;height:8px;background:var(--emerald);border-radius:50%;animation:pulse 2s infinite}
.hero-badge .new{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;padding:2px 8px;border-radius:12px;font-size:10px;font-weight:700}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
h1{font-size:72px;font-weight:800;line-height:1.05;margin-bottom:24px;background:linear-gradient(135deg,var(--text) 0%,var(--text) 50%,var(--gold) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{font-size:20px;color:var(--text-2);margin-bottom:40px;max-width:640px;margin-left:auto;margin-right:auto}
.hero-btns{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.hero-btns .btn{padding:16px 32px;font-size:16px}
.integrations{display:flex;justify-content:center;gap:32px;margin-top:64px;flex-wrap:wrap;opacity:.7}
.integrations span{font-size:13px;color:var(--text-3);display:flex;align-items:center;gap:8px}
.stats-row{display:flex;justify-content:center;gap:64px;margin-top:80px;flex-wrap:wrap}
.stat{text-align:center}
.stat-value{font-size:48px;font-weight:800;background:linear-gradient(135deg,var(--gold),var(--orange));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat-label{font-size:14px;color:var(--text-3);margin-top:4px}
.features{padding:120px 24px;background:var(--bg-2)}
.section-header{text-align:center;margin-bottom:64px}
.section-header h2{font-size:48px;font-weight:700;margin-bottom:16px}
.section-header p{color:var(--text-2);font-size:18px;max-width:600px;margin:0 auto}
.features-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;max-width:1200px;margin:0 auto}
.feature-card{background:var(--bg);border:1px solid var(--border);border-radius:16px;padding:32px;transition:all .3s}
.feature-card:hover{border-color:rgba(251,191,36,.2);transform:translateY(-4px)}
.feature-icon{width:56px;height:56px;background:linear-gradient(135deg,rgba(251,191,36,.15),rgba(251,191,36,.05));border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:20px}
.feature-card h3{font-size:20px;font-weight:600;margin-bottom:12px}
.feature-card p{color:var(--text-2);font-size:14px;line-height:1.7}
.feature-card .tag{display:inline-block;background:rgba(16,185,129,.15);color:var(--emerald);padding:4px 10px;border-radius:6px;font-size:11px;font-weight:600;margin-top:16px}
.integrations-section{padding:100px 24px;text-align:center}
.integrations-section h2{font-size:36px;font-weight:700;margin-bottom:48px}
.integration-logos{display:flex;justify-content:center;gap:48px;flex-wrap:wrap;opacity:.8}
.integration-logos div{background:var(--bg-2);border:1px solid var(--border);padding:20px 32px;border-radius:12px;font-size:14px;font-weight:500}
.cta{padding:120px 24px;text-align:center;background:linear-gradient(180deg,var(--bg) 0%,rgba(251,191,36,.03) 100%)}
.cta h2{font-size:48px;font-weight:700;margin-bottom:16px}
.cta p{color:var(--text-2);font-size:18px;margin-bottom:40px;max-width:500px;margin-left:auto;margin-right:auto}
.footer{padding:48px 24px;border-top:1px solid var(--border)}
.footer-inner{max-width:1200px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:24px}
.footer p{color:var(--text-3);font-size:13px}
.footer a{color:var(--gold);text-decoration:none}
.footer-links{display:flex;gap:24px}
.footer-links a{color:var(--text-3);text-decoration:none;font-size:13px}
.footer-links a:hover{color:var(--text)}
@media(max-width:900px){h1{font-size:42px}.features-grid{grid-template-columns:1fr}.nav-links{display:none}.stats-row{gap:32px}}
</style>
</head>
<body>
<nav class="nav">
<div class="nav-inner">
<a href="/" class="nav-logo"><span>⚡</span>West Money OS</a>
<div class="nav-links">
<a href="#features">Features</a>
<a href="/pricing">Pricing</a>
<a href="/demo">Demo</a>
<a href="#integrations">Integrationen</a>
</div>
<div class="nav-btns">
<a href="/app" class="btn btn-ghost">Login</a>
<a href="/register" class="btn btn-gold">Kostenlos starten</a>
</div>
</div>
</nav>

<section class="hero">
<div class="hero-content">
<div class="hero-badge"><span class="dot"></span><span class="new">NEU</span>WhatsApp Business & HubSpot Integration</div>
<h1>Die Business Platform der Zukunft</h1>
<p>CRM, Smart Home Automation, WhatsApp Business, Handelsregister, FinTech und mehr - alles in einer Plattform. Steigern Sie Ihre Produktivität um 300%.</p>
<div class="hero-btns">
<a href="/demo" class="btn btn-gold">🚀 Kostenlos testen</a>
<a href="/pricing" class="btn btn-ghost">💳 Pläne ansehen</a>
</div>
<div class="integrations">
<span>📱 WhatsApp Business</span>
<span>🔗 HubSpot CRM</span>
<span>💳 Stripe Payments</span>
<span>🏛️ Handelsregister</span>
<span>🏠 LOXONE</span>
</div>
<div class="stats-row">
<div class="stat"><div class="stat-value">234+</div><div class="stat-label">Aktive Kunden</div></div>
<div class="stat"><div class="stat-value">€1.2M</div><div class="stat-label">Pipeline verwaltet</div></div>
<div class="stat"><div class="stat-value">99.9%</div><div class="stat-label">Uptime</div></div>
<div class="stat"><div class="stat-value">47</div><div class="stat-label">Smart Homes</div></div>
</div>
</div>
</section>

<section class="features" id="features">
<div class="section-header">
<h2>Alles was Sie brauchen</h2>
<p>Eine Plattform - unendliche Möglichkeiten für Ihr Business</p>
</div>
<div class="features-grid">
<div class="feature-card">
<div class="feature-icon">📱</div>
<h3>WhatsApp Business</h3>
<p>Erreichen Sie Ihre Kunden dort, wo sie sind. Automatisierte Nachrichten, Templates und Kampagnen direkt aus dem CRM.</p>
<span class="tag">NEU</span>
</div>
<div class="feature-card">
<div class="feature-icon">👥</div>
<h3>CRM & Pipeline</h3>
<p>Verwalten Sie Kontakte, Leads und Deals in einer übersichtlichen Pipeline. Automatische Follow-ups und Erinnerungen.</p>
</div>
<div class="feature-card">
<div class="feature-icon">🔗</div>
<h3>HubSpot Sync</h3>
<p>Nahtlose Integration mit HubSpot CRM. Automatische Synchronisation Ihrer Kontakte und Deals.</p>
<span class="tag">NEU</span>
</div>
<div class="feature-card">
<div class="feature-icon">🏛️</div>
<h3>Handelsregister</h3>
<p>Direkter Zugriff auf das deutsche Handelsregister. Suchen Sie Firmen und importieren Sie diese direkt.</p>
</div>
<div class="feature-card">
<div class="feature-icon">🤖</div>
<h3>Smart Home</h3>
<p>LOXONE und ComfortClick Integration. Building Automation für Wohn- und Gewerbeimmobilien.</p>
</div>
<div class="feature-card">
<div class="feature-icon">💳</div>
<h3>Stripe Payments</h3>
<p>Integrierte Zahlungsabwicklung. Abonnements, Rechnungen und Kundenportal.</p>
</div>
</div>
</section>

<section class="integrations-section" id="integrations">
<h2>Verbunden mit den besten Tools</h2>
<div class="integration-logos">
<div>📱 WhatsApp Business API</div>
<div>🔗 HubSpot CRM</div>
<div>💳 Stripe</div>
<div>🏛️ Handelsregister</div>
<div>🏠 LOXONE</div>
<div>⚡ Zapier</div>
</div>
</section>

<section class="cta">
<h2>Bereit durchzustarten?</h2>
<p>Starten Sie noch heute kostenlos und erleben Sie die Zukunft des Business Managements.</p>
<div class="hero-btns">
<a href="/demo" class="btn btn-gold">🚀 Demo starten</a>
<a href="/register" class="btn btn-ghost">Account erstellen →</a>
</div>
</section>

<footer class="footer">
<div class="footer-inner">
<p>© 2025 <a href="https://enterprise-universe.de">Enterprise Universe GmbH</a> | West Money OS v7.0</p>
<div class="footer-links">
<a href="/pricing">Pricing</a>
<a href="/demo">Demo</a>
<a href="mailto:info@west-money.com">Kontakt</a>
<a href="#">Datenschutz</a>
<a href="#">Impressum</a>
</div>
</div>
</footer>
</body>
</html>'''

PRICING_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pricing | West Money OS</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
:root{--bg:#09090b;--bg-2:#131316;--bg-3:#1a1a1f;--text:#fafafa;--text-2:#a1a1aa;--text-3:#71717a;--gold:#fbbf24;--orange:#f97316;--emerald:#10b981;--border:rgba(255,255,255,.06)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.nav{position:fixed;top:0;left:0;right:0;background:rgba(9,9,11,.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);z-index:100;padding:0 24px}
.nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:72px}
.nav-logo{display:flex;align-items:center;gap:12px;font-size:20px;font-weight:700;text-decoration:none;color:var(--text)}
.nav-logo span{background:linear-gradient(135deg,var(--gold),var(--orange));width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center}
.btn{padding:10px 20px;border-radius:8px;font-size:14px;font-weight:500;text-decoration:none;transition:all .2s;cursor:pointer;border:none}
.btn-ghost{background:transparent;color:var(--text);border:1px solid var(--border)}
.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;font-weight:600}
.pricing{padding:140px 24px 80px;max-width:1200px;margin:0 auto}
.pricing-header{text-align:center;margin-bottom:64px}
.pricing-header h1{font-size:48px;font-weight:700;margin-bottom:16px}
.pricing-header p{color:var(--text-2);font-size:18px}
.billing-toggle{display:flex;justify-content:center;gap:12px;margin-top:32px;align-items:center}
.billing-toggle span{color:var(--text-3);font-size:14px;cursor:pointer}
.billing-toggle span.active{color:var(--gold)}
.toggle{width:56px;height:28px;background:var(--bg-3);border-radius:14px;position:relative;cursor:pointer;border:1px solid var(--border)}
.toggle::after{content:'';position:absolute;width:22px;height:22px;background:var(--gold);border-radius:50%;top:2px;left:3px;transition:transform .2s}
.toggle.yearly::after{transform:translateX(26px)}
.pricing-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:48px}
.plan-card{background:var(--bg-2);border:1px solid var(--border);border-radius:20px;padding:36px;position:relative;transition:all .3s}
.plan-card:hover{border-color:rgba(255,255,255,.1)}
.plan-card.popular{border-color:var(--gold);background:linear-gradient(180deg,rgba(251,191,36,.03) 0%,var(--bg-2) 100%)}
.popular-badge{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;padding:6px 20px;border-radius:20px;font-size:12px;font-weight:700}
.plan-name{font-size:24px;font-weight:700;margin-bottom:8px}
.plan-price{font-size:56px;font-weight:800;margin-bottom:4px;line-height:1}
.plan-price span{font-size:18px;color:var(--text-2);font-weight:400}
.plan-desc{color:var(--text-3);font-size:14px;margin-bottom:28px}
.plan-features{list-style:none;margin-bottom:32px}
.plan-features li{padding:10px 0;font-size:14px;display:flex;align-items:center;gap:12px;border-bottom:1px solid var(--border)}
.plan-features li:last-child{border-bottom:none}
.plan-features li::before{content:'✓';color:var(--emerald);font-weight:700;font-size:16px}
.plan-features li.disabled{color:var(--text-3)}
.plan-features li.disabled::before{content:'—';color:var(--text-3)}
.plan-btn{width:100%;padding:16px;border-radius:12px;font-size:15px;font-weight:600;cursor:pointer;border:none;transition:all .2s}
.plan-btn.primary{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}
.plan-btn.primary:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(251,191,36,.25)}
.plan-btn.secondary{background:var(--bg-3);color:var(--text);border:1px solid var(--border)}
.plan-btn.secondary:hover{background:var(--bg);border-color:rgba(255,255,255,.15)}
.guarantee{text-align:center;margin-top:64px;padding:32px;background:var(--bg-2);border-radius:16px;border:1px solid var(--border)}
.guarantee h3{font-size:18px;margin-bottom:12px}
.guarantee p{color:var(--text-2);font-size:14px}
.faq{margin-top:80px}
.faq h2{text-align:center;font-size:32px;margin-bottom:40px}
.faq-item{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:12px}
.faq-item h4{font-size:16px;margin-bottom:8px}
.faq-item p{color:var(--text-2);font-size:14px}
@media(max-width:900px){.pricing-grid{grid-template-columns:1fr}.pricing-header h1{font-size:36px}}
</style>
</head>
<body>
<nav class="nav">
<div class="nav-inner">
<a href="/" class="nav-logo"><span>⚡</span>West Money OS</a>
<div style="display:flex;gap:12px">
<a href="/demo" class="btn btn-ghost">Demo</a>
<a href="/app" class="btn btn-gold">Login</a>
</div>
</div>
</nav>

<section class="pricing">
<div class="pricing-header">
<h1>Einfache, transparente Preise</h1>
<p>Wählen Sie den Plan, der zu Ihrem Business passt. Jederzeit kündbar.</p>
<div class="billing-toggle">
<span class="active" id="monthlyLabel" onclick="setBilling(false)">Monatlich</span>
<div class="toggle" id="billingToggle" onclick="toggleBilling()"></div>
<span id="yearlyLabel" onclick="setBilling(true)">Jährlich <span style="color:var(--emerald)">spare 17%</span></span>
</div>
</div>

<div class="pricing-grid">
<div class="plan-card">
<div class="plan-name">Starter</div>
<div class="plan-price" id="starterPrice">€29<span>/Monat</span></div>
<div class="plan-desc">Perfekt für Einzelunternehmer</div>
<ul class="plan-features">
<li>5 Kontakte</li>
<li>3 Leads</li>
<li>Basic Dashboard</li>
<li>E-Mail Support</li>
<li>Handelsregister (10/Monat)</li>
<li class="disabled">WhatsApp Integration</li>
<li class="disabled">HubSpot Sync</li>
</ul>
<button class="plan-btn secondary" onclick="checkout('starter')">Starten</button>
</div>

<div class="plan-card popular">
<div class="popular-badge">⭐ BELIEBT</div>
<div class="plan-name">Professional</div>
<div class="plan-price" id="proPrice">€99<span>/Monat</span></div>
<div class="plan-desc">Für wachsende Unternehmen</div>
<ul class="plan-features">
<li>Unbegrenzte Kontakte</li>
<li>Unbegrenzte Leads</li>
<li>Voller Dashboard</li>
<li>Priority Support</li>
<li>Handelsregister (100/Monat)</li>
<li>WhatsApp Integration</li>
<li class="disabled">HubSpot Sync</li>
</ul>
<button class="plan-btn primary" onclick="checkout('professional')">Jetzt starten</button>
</div>

<div class="plan-card">
<div class="plan-name">Enterprise</div>
<div class="plan-price" id="entPrice">€299<span>/Monat</span></div>
<div class="plan-desc">Für große Teams & Agenturen</div>
<ul class="plan-features">
<li>Alles aus Professional</li>
<li>Broly Automations</li>
<li>Einstein Agency</li>
<li>HubSpot Sync</li>
<li>API Access</li>
<li>White Label Option</li>
<li>Dedicated Support</li>
</ul>
<button class="plan-btn secondary" onclick="checkout('enterprise')">Kontakt aufnehmen</button>
</div>
</div>

<div class="guarantee">
<h3>💳 Sichere Zahlung | 🔒 SSL | 🔄 30 Tage Geld-zurück</h3>
<p>Keine versteckten Kosten. Jederzeit kündbar. Zahlung über Stripe.</p>
</div>

<div class="faq">
<h2>Häufige Fragen</h2>
<div class="faq-item">
<h4>Kann ich den Plan jederzeit wechseln?</h4>
<p>Ja, Sie können jederzeit up- oder downgraden. Die Differenz wird anteilig berechnet.</p>
</div>
<div class="faq-item">
<h4>Gibt es eine kostenlose Testphase?</h4>
<p>Ja! Testen Sie alle Features 14 Tage kostenlos. Keine Kreditkarte erforderlich.</p>
</div>
<div class="faq-item">
<h4>Was passiert nach der Kündigung?</h4>
<p>Sie behalten Lesezugriff auf Ihre Daten. Export ist jederzeit möglich.</p>
</div>
</div>
</section>

<script>
let yearly = false;
const prices = {starter: [29, 290], professional: [99, 990], enterprise: [299, 2990]};

function toggleBilling() {
    yearly = !yearly;
    updatePrices();
}

function setBilling(isYearly) {
    yearly = isYearly;
    updatePrices();
}

function updatePrices() {
    document.getElementById('billingToggle').classList.toggle('yearly', yearly);
    document.getElementById('monthlyLabel').classList.toggle('active', !yearly);
    document.getElementById('yearlyLabel').classList.toggle('active', yearly);
    const period = yearly ? '/Jahr' : '/Monat';
    document.getElementById('starterPrice').innerHTML = '€' + prices.starter[yearly?1:0] + '<span>' + period + '</span>';
    document.getElementById('proPrice').innerHTML = '€' + prices.professional[yearly?1:0] + '<span>' + period + '</span>';
    document.getElementById('entPrice').innerHTML = '€' + prices.enterprise[yearly?1:0] + '<span>' + period + '</span>';
}

async function checkout(plan) {
    if (plan === 'enterprise') {
        window.location.href = 'mailto:info@west-money.com?subject=Enterprise Plan Anfrage';
        return;
    }
    try {
        const r = await fetch('/api/stripe/create-checkout', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({plan: plan, billing: yearly ? 'yearly' : 'monthly'})
        });
        const data = await r.json();
        if (data.success) {
            alert('Demo: Stripe Checkout würde öffnen\\n\\nPlan: ' + plan.toUpperCase() + '\\nPreis: €' + data.price + '/' + (yearly ? 'Jahr' : 'Monat'));
        }
    } catch(e) {
        console.error(e);
    }
}
</script>
</body>
</html>'''

DEMO_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Demo starten | West Money OS</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
:root{--bg:#09090b;--bg-2:#131316;--text:#fafafa;--text-2:#a1a1aa;--gold:#fbbf24;--orange:#f97316;--emerald:#10b981;--border:rgba(255,255,255,.06)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
.demo-box{background:var(--bg-2);border:1px solid var(--border);border-radius:24px;padding:48px;max-width:480px;width:100%;text-align:center}
.demo-icon{width:88px;height:88px;background:linear-gradient(135deg,var(--gold),var(--orange));border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:40px;margin:0 auto 28px;box-shadow:0 16px 48px rgba(251,191,36,.25)}
h1{font-size:32px;margin-bottom:12px}
p{color:var(--text-2);margin-bottom:32px;font-size:15px}
.features{text-align:left;background:var(--bg);border:1px solid var(--border);border-radius:14px;padding:24px;margin-bottom:32px}
.features h3{font-size:13px;color:var(--text-2);margin-bottom:16px;text-transform:uppercase;letter-spacing:.5px}
.features ul{list-style:none}
.features li{padding:10px 0;font-size:14px;display:flex;align-items:center;gap:10px;border-bottom:1px solid var(--border)}
.features li:last-child{border-bottom:none}
.features li::before{content:'✓';color:var(--emerald);font-weight:700}
.btn{width:100%;padding:16px;border-radius:12px;font-size:16px;font-weight:600;cursor:pointer;border:none;margin-bottom:12px;transition:all .2s}
.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}
.btn-gold:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(251,191,36,.3)}
.btn-ghost{background:transparent;color:var(--text);border:1px solid var(--border)}
.btn-ghost:hover{background:var(--bg)}
.note{font-size:12px;color:var(--text-2);margin-top:20px}
</style>
</head>
<body>
<div class="demo-box">
<div class="demo-icon">🚀</div>
<h1>Demo starten</h1>
<p>Testen Sie West Money OS kostenlos und unverbindlich mit allen Features.</p>
<div class="features">
<h3>In der Demo enthalten:</h3>
<ul>
<li>Vollständiges CRM Dashboard</li>
<li>Kontakte & Leads Management</li>
<li>Handelsregister Suche (LIVE)</li>
<li>WhatsApp Templates</li>
<li>Broly Automations</li>
<li>Einstein Agency</li>
<li>FinTech & DedSec Security</li>
</ul>
</div>
<button class="btn btn-gold" onclick="startDemo()">⚡ Demo starten</button>
<button class="btn btn-ghost" onclick="window.location.href='/app'">Ich habe einen Account</button>
<p class="note">Keine Registrierung erforderlich. Demo-Daten werden verwendet.</p>
</div>
<script>
async function startDemo() {
    try {
        const r = await fetch('/api/auth/demo', {method: 'POST'});
        const d = await r.json();
        if (d.success) window.location.href = '/app';
    } catch(e) { alert('Fehler beim Starten der Demo'); }
}
</script>
</body>
</html>'''

REGISTER_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Registrieren | West Money OS</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
:root{--bg:#09090b;--bg-2:#131316;--bg-3:#1a1a1f;--text:#fafafa;--text-2:#a1a1aa;--gold:#fbbf24;--orange:#f97316;--emerald:#10b981;--rose:#f43f5e;--border:rgba(255,255,255,.06)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
.register-box{background:var(--bg-2);border:1px solid var(--border);border-radius:24px;padding:48px;max-width:440px;width:100%}
.logo{text-align:center;margin-bottom:32px}
.logo-icon{width:72px;height:72px;background:linear-gradient(135deg,var(--gold),var(--orange));border-radius:18px;display:inline-flex;align-items:center;justify-content:center;font-size:32px;margin-bottom:16px}
.logo h1{font-size:24px;margin-bottom:4px}
.logo p{color:var(--text-2);font-size:13px}
.form-group{margin-bottom:20px}
.form-group label{display:block;font-size:13px;margin-bottom:8px;color:var(--text-2)}
.form-input{width:100%;padding:14px 16px;background:var(--bg-3);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:14px}
.form-input:focus{outline:none;border-color:var(--gold)}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.btn{width:100%;padding:16px;border-radius:12px;font-size:15px;font-weight:600;cursor:pointer;border:none;margin-top:8px}
.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}
.btn-gold:hover{transform:translateY(-2px)}
.error{background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.2);color:var(--rose);padding:12px;border-radius:8px;margin-bottom:20px;font-size:13px;display:none}
.error.show{display:block}
.divider{text-align:center;margin:24px 0;color:var(--text-2);font-size:13px}
.links{text-align:center;margin-top:24px;font-size:13px}
.links a{color:var(--gold);text-decoration:none}
</style>
</head>
<body>
<div class="register-box">
<div class="logo">
<div class="logo-icon">⚡</div>
<h1>Account erstellen</h1>
<p>Starten Sie kostenlos mit West Money OS</p>
</div>
<div class="error" id="error"></div>
<div class="form-group"><label>Name *</label><input type="text" class="form-input" id="name" placeholder="Ihr vollständiger Name"></div>
<div class="form-group"><label>E-Mail *</label><input type="email" class="form-input" id="email" placeholder="ihre@email.de"></div>
<div class="form-group"><label>Unternehmen</label><input type="text" class="form-input" id="company" placeholder="Firma GmbH"></div>
<div class="form-group"><label>Passwort *</label><input type="password" class="form-input" id="password" placeholder="Mind. 8 Zeichen"></div>
<button class="btn btn-gold" onclick="register()">🚀 Kostenlos registrieren</button>
<div class="divider">oder</div>
<button class="btn" style="background:var(--bg-3);color:var(--text)" onclick="window.location.href='/demo'">Demo ohne Registrierung →</button>
<div class="links">Bereits registriert? <a href="/app">Jetzt anmelden</a></div>
</div>
<script>
async function register() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const company = document.getElementById('company').value;
    const password = document.getElementById('password').value;
    if (!name || !email || !password) {
        document.getElementById('error').textContent = 'Bitte alle Pflichtfelder ausfüllen';
        document.getElementById('error').classList.add('show');
        return;
    }
    if (password.length < 8) {
        document.getElementById('error').textContent = 'Passwort muss mind. 8 Zeichen haben';
        document.getElementById('error').classList.add('show');
        return;
    }
    try {
        const r = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, email, company, password})
        });
        const d = await r.json();
        if (d.success) {
            window.location.href = '/app';
        } else {
            document.getElementById('error').textContent = d.error || 'Registrierung fehlgeschlagen';
            document.getElementById('error').classList.add('show');
        }
    } catch(e) {
        document.getElementById('error').textContent = 'Verbindungsfehler';
        document.getElementById('error').classList.add('show');
    }
}
</script>
</body>
</html>'''

APP_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>West Money OS v7.0</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{--bg-0:#09090b;--bg-1:#0f0f12;--bg-2:#151518;--bg-3:#1c1c20;--text-0:#fafafa;--text-1:#e4e4e7;--text-2:#a1a1aa;--text-3:#71717a;--primary:#6366f1;--emerald:#10b981;--amber:#f59e0b;--rose:#f43f5e;--cyan:#06b6d4;--violet:#8b5cf6;--gold:#fbbf24;--orange:#f97316;--border:rgba(255,255,255,.06);--radius:8px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg-0);color:var(--text-0);font-size:14px}
.login-screen{min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg-0)}
.login-box{background:var(--bg-2);border:1px solid var(--border);border-radius:24px;padding:48px;width:100%;max-width:400px}
.login-logo{text-align:center;margin-bottom:32px}
.login-logo-icon{width:72px;height:72px;background:linear-gradient(135deg,var(--gold),var(--orange));border-radius:18px;display:inline-flex;align-items:center;justify-content:center;font-size:32px;margin-bottom:16px}
.login-logo h1{font-size:24px;margin-bottom:4px}
.login-logo p{color:var(--text-3);font-size:13px}
.form-group{margin-bottom:16px}
.form-group label{display:block;font-size:13px;margin-bottom:6px;color:var(--text-2)}
.form-input{width:100%;padding:14px 16px;background:var(--bg-3);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-0);font-size:14px}
.form-input:focus{outline:none;border-color:var(--gold)}
.login-btn{width:100%;padding:16px;background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;border:none;border-radius:var(--radius);font-size:15px;font-weight:600;cursor:pointer;margin-top:8px}
.login-btn:hover{transform:translateY(-2px)}
.demo-link{text-align:center;margin-top:24px}
.demo-link a{color:var(--gold);text-decoration:none;font-size:13px}
.login-error{background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.2);color:var(--rose);padding:12px;border-radius:var(--radius);margin-bottom:16px;text-align:center;display:none;font-size:13px}
.login-error.show{display:block}
.app{display:none;min-height:100vh}
.app.active{display:flex}
.sidebar{width:260px;background:var(--bg-1);border-right:1px solid var(--border);position:fixed;height:100vh;display:flex;flex-direction:column;overflow-y:auto}
.sidebar-header{padding:20px;border-bottom:1px solid var(--border)}
.logo{display:flex;align-items:center;gap:12px}
.logo-icon{width:42px;height:42px;background:linear-gradient(135deg,var(--gold),var(--orange));border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px}
.logo-text h1{font-size:15px;font-weight:700}
.logo-text span{font-size:10px;color:var(--text-3)}
.sidebar-nav{flex:1;padding:12px}
.nav-section{margin-bottom:4px}
.nav-section-title{font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.5px;padding:12px 12px 8px}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:var(--radius);cursor:pointer;color:var(--text-2);font-size:13px;margin-bottom:2px;transition:all .15s}
.nav-item:hover{background:var(--bg-3);color:var(--text-0)}
.nav-item.active{background:rgba(251,191,36,.1);color:var(--gold);border:1px solid rgba(251,191,36,.15)}
.nav-item .badge{font-size:9px;padding:2px 6px;border-radius:8px;font-weight:600;margin-left:auto}
.nav-item .badge.live{background:var(--rose);color:white}
.nav-item .badge.api{background:var(--cyan);color:white}
.nav-item .badge.new{background:var(--emerald);color:white}
.nav-item .badge.gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}
.sidebar-footer{padding:12px;border-top:1px solid var(--border)}
.user-card{display:flex;align-items:center;gap:10px;padding:12px;background:var(--bg-2);border-radius:var(--radius)}
.user-avatar{width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,var(--gold),var(--orange));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;color:#000}
.user-info{flex:1}
.user-info .name{font-size:13px;font-weight:600}
.user-info .role{font-size:10px;color:var(--gold)}
.logout-btn{background:none;border:none;color:var(--text-3);cursor:pointer;font-size:16px}
.main{flex:1;margin-left:260px;min-height:100vh}
.topbar{height:60px;background:var(--bg-1);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 24px;position:sticky;top:0;z-index:50}
.breadcrumb{font-size:13px;color:var(--text-2)}
.breadcrumb strong{color:var(--gold)}
.topbar-right{display:flex;align-items:center;gap:12px}
.notifications-btn{background:var(--bg-2);border:1px solid var(--border);padding:8px 12px;border-radius:var(--radius);cursor:pointer;position:relative}
.notifications-btn .count{position:absolute;top:-4px;right:-4px;background:var(--rose);color:white;font-size:10px;padding:2px 6px;border-radius:10px}
.demo-badge{background:linear-gradient(135deg,var(--emerald),var(--cyan));color:#fff;padding:6px 14px;border-radius:16px;font-size:11px;font-weight:600}
.content{padding:24px}
.page{display:none}
.page.active{display:block}
.page-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px;flex-wrap:wrap;gap:16px}
.page-header h1{font-size:24px;font-weight:700;display:flex;align-items:center;gap:10px}
.page-header p{color:var(--text-2);font-size:13px;margin-top:4px}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.stat-card{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:20px;transition:all .2s}
.stat-card:hover{border-color:rgba(255,255,255,.1)}
.stat-card.gold{border-left:3px solid var(--gold)}
.stat-card.emerald{border-left:3px solid var(--emerald)}
.stat-card.amber{border-left:3px solid var(--amber)}
.stat-card.violet{border-left:3px solid var(--violet)}
.stat-card.cyan{border-left:3px solid var(--cyan)}
.stat-card.rose{border-left:3px solid var(--rose)}
.stat-card .label{font-size:12px;color:var(--text-3);margin-bottom:6px}
.stat-card .value{font-size:28px;font-weight:700}
.stat-card .change{font-size:11px;margin-top:6px;color:var(--emerald)}
.card{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;margin-bottom:20px}
.card-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.card-header h3{font-size:14px;font-weight:600;display:flex;align-items:center;gap:8px}
.card-body{padding:20px}
.card-body.no-padding{padding:0}
.grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.btn{padding:10px 16px;border-radius:var(--radius);font-size:13px;font-weight:500;cursor:pointer;border:none;transition:all .15s;display:inline-flex;align-items:center;gap:6px}
.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}
.btn-gold:hover{transform:translateY(-1px)}
.btn-secondary{background:var(--bg-3);color:var(--text-0);border:1px solid var(--border)}
.btn-success{background:var(--emerald);color:white}
table{width:100%;border-collapse:collapse}
th,td{text-align:left;padding:12px 16px;border-bottom:1px solid var(--border)}
th{font-size:11px;font-weight:600;color:var(--text-3);text-transform:uppercase;background:var(--bg-3)}
tbody tr:hover{background:var(--bg-3)}
.badge{display:inline-flex;padding:4px 10px;border-radius:6px;font-size:10px;font-weight:600}
.badge.active,.badge.won,.badge.paid{background:rgba(16,185,129,.15);color:var(--emerald)}
.badge.lead,.badge.qualified,.badge.pending{background:rgba(245,158,11,.15);color:var(--amber)}
.badge.proposal,.badge.negotiation{background:rgba(99,102,241,.15);color:var(--primary)}
.search-box{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:20px}
.search-row{display:flex;gap:12px}
.search-input{flex:1;padding:12px 16px;background:var(--bg-3);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-0);font-size:13px}
.search-input:focus{outline:none;border-color:var(--gold)}
.result-item{padding:14px 20px;border-bottom:1px solid var(--border);cursor:pointer;transition:background .15s}
.result-item:hover{background:var(--bg-3)}
.result-name{font-size:14px;font-weight:600;margin-bottom:4px}
.result-meta{font-size:12px;color:var(--text-3)}
.empty-state{text-align:center;padding:48px;color:var(--text-3)}
.empty-state .icon{font-size:40px;margin-bottom:12px;opacity:.5}
.chart-container{height:260px}
.whatsapp-box{background:linear-gradient(135deg,rgba(37,211,102,.1),rgba(37,211,102,.02));border:1px solid rgba(37,211,102,.2);border-radius:12px;padding:20px;margin-bottom:20px}
.whatsapp-box h3{color:#25D366;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.template-card{background:var(--bg-3);border-radius:var(--radius);padding:12px;margin-bottom:8px;cursor:pointer}
.template-card:hover{background:var(--bg-2)}
.template-card .name{font-weight:600;margin-bottom:4px}
.template-card .preview{font-size:12px;color:var(--text-3)}
@media(max-width:900px){.sidebar{display:none}.main{margin-left:0}.stats-grid{grid-template-columns:repeat(2,1fr)}.grid-2{grid-template-columns:1fr}}
@media(max-width:600px){.stats-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="login-screen" id="loginScreen">
<div class="login-box">
<div class="login-logo">
<div class="login-logo-icon">⚡</div>
<h1>West Money OS</h1>
<p>Ultimate Business Platform</p>
</div>
<div class="login-error" id="loginError">Ungültige Anmeldedaten</div>
<div class="form-group"><label>Benutzername oder E-Mail</label><input type="text" class="form-input" id="loginUser" value="admin"></div>
<div class="form-group"><label>Passwort</label><input type="password" class="form-input" id="loginPass" onkeypress="if(event.key==='Enter')doLogin()"></div>
<button class="login-btn" onclick="doLogin()">🔐 Anmelden</button>
<div class="demo-link">
<a href="/demo">🚀 Demo ohne Login starten</a><br>
<a href="/register" style="color:var(--text-2)">Noch kein Account? Registrieren</a>
</div>
</div>
</div>

<div class="app" id="app">
<aside class="sidebar">
<div class="sidebar-header">
<div class="logo">
<div class="logo-icon">⚡</div>
<div class="logo-text"><h1>West Money OS</h1><span>v7.0 Ultimate</span></div>
</div>
</div>
<nav class="sidebar-nav">
<div class="nav-section">
<div class="nav-section-title">Übersicht</div>
<div class="nav-item active" data-page="dashboard"><span>📊</span>Dashboard</div>
</div>
<div class="nav-section">
<div class="nav-section-title">CRM</div>
<div class="nav-item" data-page="contacts"><span>👥</span>Kontakte</div>
<div class="nav-item" data-page="leads"><span>🎯</span>Leads</div>
<div class="nav-item" data-page="campaigns"><span>📧</span>Kampagnen</div>
</div>
<div class="nav-section">
<div class="nav-section-title">Kommunikation</div>
<div class="nav-item" data-page="whatsapp"><span>📱</span>WhatsApp<span class="badge new">NEU</span></div>
</div>
<div class="nav-section">
<div class="nav-section-title">Daten & APIs</div>
<div class="nav-item" data-page="handelsregister"><span>🏛️</span>Handelsregister<span class="badge live">LIVE</span></div>
<div class="nav-item" data-page="hubspot"><span>🔗</span>HubSpot<span class="badge api">SYNC</span></div>
</div>
<div class="nav-section">
<div class="nav-section-title">Enterprise</div>
<div class="nav-item" data-page="automations"><span>🤖</span>Broly Automations</div>
<div class="nav-item" data-page="gaming"><span>🎮</span>GTzMeta Gaming</div>
<div class="nav-item" data-page="security"><span>🛡️</span>DedSec Security</div>
</div>
<div class="nav-section">
<div class="nav-section-title">Finanzen</div>
<div class="nav-item" data-page="invoices"><span>📄</span>Rechnungen</div>
</div>
</nav>
<div class="sidebar-footer">
<div class="user-card">
<div class="user-avatar" id="userAvatar">??</div>
<div class="user-info"><div class="name" id="userName">User</div><div class="role" id="userRole">-</div></div>
<button class="logout-btn" onclick="doLogout()">🚪</button>
</div>
</div>
</aside>

<main class="main">
<header class="topbar">
<div class="breadcrumb">West Money OS / <strong id="currentPage">Dashboard</strong></div>
<div class="topbar-right">
<button class="notifications-btn" onclick="showNotifications()">🔔<span class="count" id="notifCount">0</span></button>
<div class="demo-badge" id="demoBadge" style="display:none">🎮 DEMO</div>
</div>
</header>

<div class="content">
<!-- DASHBOARD -->
<div class="page active" id="page-dashboard">
<div class="page-header"><div><h1>📊 Dashboard</h1><p>Willkommen zurück! Hier ist Ihr Überblick.</p></div></div>
<div class="stats-grid">
<div class="stat-card gold"><div class="label">Umsatz</div><div class="value" id="statRevenue">€0</div><div class="change" id="revenueGrowth">↑ 0%</div></div>
<div class="stat-card emerald"><div class="label">Leads</div><div class="value" id="statLeads">0</div><div class="change" id="leadsGrowth">↑ 0%</div></div>
<div class="stat-card amber"><div class="label">Kunden</div><div class="value" id="statCustomers">0</div><div class="change" id="customersGrowth">↑ 0%</div></div>
<div class="stat-card violet"><div class="label">MRR</div><div class="value" id="statMRR">€0</div><div class="change" id="mrrGrowth">↑ 0%</div></div>
</div>
<div class="grid-2">
<div class="card"><div class="card-header"><h3>📈 Umsatzentwicklung</h3></div><div class="card-body"><div class="chart-container"><canvas id="revenueChart"></canvas></div></div></div>
<div class="card"><div class="card-header"><h3>📊 MRR</h3></div><div class="card-body"><div class="chart-container"><canvas id="mrrChart"></canvas></div></div></div>
</div>
</div>

<!-- CONTACTS -->
<div class="page" id="page-contacts">
<div class="page-header"><div><h1>👥 Kontakte</h1></div><button class="btn btn-gold" onclick="showModal('contact')">+ Neuer Kontakt</button></div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Name</th><th>E-Mail</th><th>Unternehmen</th><th>WhatsApp</th><th>Status</th></tr></thead><tbody id="contactsTable"></tbody></table></div></div>
</div>

<!-- LEADS -->
<div class="page" id="page-leads">
<div class="page-header"><div><h1>🎯 Leads</h1></div><button class="btn btn-gold" onclick="showModal('lead')">+ Neuer Lead</button></div>
<div class="stats-grid" style="grid-template-columns:repeat(2,1fr)">
<div class="stat-card gold"><div class="label">Pipeline Wert</div><div class="value" id="pipelineValue">€0</div></div>
<div class="stat-card emerald"><div class="label">Gewichteter Wert</div><div class="value" id="weightedValue">€0</div></div>
</div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Projekt</th><th>Unternehmen</th><th>Wert</th><th>Phase</th></tr></thead><tbody id="leadsTable"></tbody></table></div></div>
</div>

<!-- CAMPAIGNS -->
<div class="page" id="page-campaigns">
<div class="page-header"><div><h1>📧 Kampagnen</h1></div></div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Name</th><th>Typ</th><th>Versendet</th><th>Geöffnet</th><th>Status</th></tr></thead><tbody id="campaignsTable"></tbody></table></div></div>
</div>

<!-- WHATSAPP -->
<div class="page" id="page-whatsapp">
<div class="page-header"><div><h1>📱 WhatsApp Business</h1><p>Nachrichten senden und Kampagnen verwalten</p></div></div>
<div class="stats-grid" style="grid-template-columns:repeat(3,1fr)">
<div class="stat-card emerald"><div class="label">Gesendet</div><div class="value" id="waSent">0</div></div>
<div class="stat-card gold"><div class="label">Zugestellt</div><div class="value" id="waDelivered">0</div></div>
<div class="stat-card cyan"><div class="label">E-Mails</div><div class="value" id="emailSent">0</div></div>
</div>
<div class="whatsapp-box">
<h3>📱 Schnellnachricht senden</h3>
<div class="search-row" style="margin-bottom:12px">
<input type="text" class="search-input" id="waPhone" placeholder="Telefonnummer (z.B. 491701234567)">
</div>
<div class="search-row">
<input type="text" class="search-input" id="waMessage" placeholder="Nachricht eingeben..." style="flex:2">
<button class="btn btn-success" onclick="sendWhatsApp()">📤 Senden</button>
</div>
</div>
<div class="card"><div class="card-header"><h3>📋 Vorlagen</h3></div><div class="card-body" id="waTemplates"></div></div>
</div>

<!-- HANDELSREGISTER -->
<div class="page" id="page-handelsregister">
<div class="page-header"><div><h1>🏛️ Handelsregister</h1><p>LIVE Firmendaten aus dem deutschen Handelsregister</p></div></div>
<div class="search-box"><div class="search-row"><input type="text" class="search-input" id="hrQuery" placeholder="🔍 Firmenname eingeben..." onkeypress="if(event.key==='Enter')searchHR()"><button class="btn btn-gold" onclick="searchHR()">Suchen</button></div></div>
<div class="card"><div class="card-header"><h3>Ergebnisse</h3><span id="hrResultCount">0</span></div><div class="card-body no-padding" id="hrResults"><div class="empty-state"><div class="icon">🏛️</div><p>Suche starten</p></div></div></div>
</div>

<!-- HUBSPOT -->
<div class="page" id="page-hubspot">
<div class="page-header"><div><h1>🔗 HubSpot CRM</h1><p>Synchronisation mit HubSpot</p></div></div>
<div class="card"><div class="card-header"><h3>Status</h3></div><div class="card-body">
<p style="margin-bottom:16px"><strong>Status:</strong> <span class="badge" id="hubspotStatus">Prüfen...</span></p>
<button class="btn btn-gold" onclick="syncHubSpot()">🔄 Jetzt synchronisieren</button>
</div></div>
</div>

<!-- AUTOMATIONS -->
<div class="page" id="page-automations">
<div class="page-header"><div><h1>🤖 Broly Automations</h1></div></div>
<div class="stats-grid" style="grid-template-columns:repeat(3,1fr)">
<div class="stat-card gold"><div class="label">Systeme</div><div class="value" id="autoSystems">0</div></div>
<div class="stat-card emerald"><div class="label">Geräte</div><div class="value" id="autoDevices">0</div></div>
<div class="stat-card cyan"><div class="label">Energie gespart</div><div class="value" id="autoEnergy">0</div></div>
</div>
</div>

<!-- GAMING -->
<div class="page" id="page-gaming">
<div class="page-header"><div><h1>🎮 GTzMeta Gaming</h1></div></div>
<div class="stats-grid">
<div class="stat-card violet"><div class="label">Twitch</div><div class="value" id="gamingTwitch">0</div></div>
<div class="stat-card rose"><div class="label">YouTube</div><div class="value" id="gamingYoutube">0</div></div>
<div class="stat-card cyan"><div class="label">Discord</div><div class="value" id="gamingDiscord">0</div></div>
<div class="stat-card gold"><div class="label">Peak</div><div class="value" id="gamingPeak">0</div></div>
</div>
</div>

<!-- SECURITY -->
<div class="page" id="page-security">
<div class="page-header"><div><h1>🛡️ DedSec Security</h1></div></div>
<div class="stats-grid">
<div class="stat-card emerald"><div class="label">Blocked</div><div class="value" id="secThreats">0</div></div>
<div class="stat-card gold"><div class="label">Protected</div><div class="value" id="secSystems">0</div></div>
<div class="stat-card cyan"><div class="label">Uptime</div><div class="value" id="secUptime">0%</div></div>
<div class="stat-card violet"><div class="label">Score</div><div class="value" id="secScore">0</div></div>
</div>
</div>

<!-- INVOICES -->
<div class="page" id="page-invoices">
<div class="page-header"><div><h1>📄 Rechnungen</h1></div></div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Nr.</th><th>Kunde</th><th>Betrag</th><th>Fällig</th><th>Status</th></tr></thead><tbody id="invoicesTable"></tbody></table></div></div>
</div>
</div>
</main>
</div>

<script>
let revenueChart, mrrChart, hrResults = [];

async function checkAuth() {
    try {
        const r = await fetch('/api/auth/status');
        const d = await r.json();
        if (d.authenticated) showApp(d.user);
    } catch(e) {}
}

async function doLogin() {
    const user = document.getElementById('loginUser').value;
    const pass = document.getElementById('loginPass').value;
    try {
        const r = await fetch('/api/auth/login', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username:user, password:pass})});
        const d = await r.json();
        if (d.success) { document.getElementById('loginError').classList.remove('show'); showApp(d.user); }
        else { document.getElementById('loginError').textContent = d.error || 'Ungültige Anmeldedaten'; document.getElementById('loginError').classList.add('show'); }
    } catch(e) { document.getElementById('loginError').classList.add('show'); }
}

async function doLogout() { await fetch('/api/auth/logout', {method:'POST'}); location.reload(); }

function showApp(user) {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('app').classList.add('active');
    document.getElementById('userName').textContent = user.name || 'User';
    document.getElementById('userAvatar').textContent = user.avatar || '??';
    document.getElementById('userRole').textContent = user.role || '-';
    if (user.role === 'Demo') document.getElementById('demoBadge').style.display = 'block';
    loadAllData();
}

document.querySelectorAll('.nav-item[data-page]').forEach(item => {
    item.addEventListener('click', () => {
        const page = item.dataset.page;
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        item.classList.add('active');
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById('page-' + page).classList.add('active');
        document.getElementById('currentPage').textContent = item.textContent.trim();
    });
});

async function loadAllData() {
    await Promise.all([loadDashboard(), loadContacts(), loadLeads(), loadCampaigns(), loadInvoices(), loadWhatsApp(), loadGaming(), loadAutomations(), loadSecurity(), loadNotifications()]);
}

async function loadDashboard() {
    try {
        const [stats, charts] = await Promise.all([fetch('/api/dashboard/stats').then(r=>r.json()), fetch('/api/dashboard/charts').then(r=>r.json())]);
        document.getElementById('statRevenue').textContent = '€' + (stats.revenue || 0).toLocaleString('de-DE');
        document.getElementById('statLeads').textContent = stats.leads || 0;
        document.getElementById('statCustomers').textContent = stats.customers || 0;
        document.getElementById('statMRR').textContent = '€' + (stats.mrr || 0).toLocaleString('de-DE');
        document.getElementById('revenueGrowth').textContent = '↑ ' + (stats.revenue_growth || 0) + '% vs. Vorjahr';
        document.getElementById('leadsGrowth').textContent = '↑ ' + (stats.leads_growth || 0) + '% diesen Monat';
        document.getElementById('customersGrowth').textContent = '↑ ' + (stats.customers_growth || 0) + '% dieses Jahr';
        document.getElementById('mrrGrowth').textContent = '↑ ' + (stats.mrr_growth || 0) + '%';
        if (revenueChart) revenueChart.destroy();
        revenueChart = new Chart(document.getElementById('revenueChart'), {type:'line', data:{labels:charts.labels, datasets:[{label:'Umsatz', data:charts.revenue, borderColor:'#fbbf24', backgroundColor:'rgba(251,191,36,0.1)', fill:true, tension:0.4}]}, options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}}});
        if (mrrChart) mrrChart.destroy();
        mrrChart = new Chart(document.getElementById('mrrChart'), {type:'line', data:{labels:charts.labels, datasets:[{label:'MRR', data:charts.mrr, borderColor:'#8b5cf6', backgroundColor:'rgba(139,92,246,0.1)', fill:true, tension:0.4}]}, options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}}});
    } catch(e) { console.error(e); }
}

async function loadContacts() {
    try {
        const contacts = await fetch('/api/contacts').then(r=>r.json());
        document.getElementById('contactsTable').innerHTML = contacts.map(c => '<tr><td><strong>'+esc(c.name)+'</strong></td><td>'+esc(c.email)+'</td><td>'+esc(c.company)+'</td><td>'+(c.whatsapp_consent ? '✅' : '❌')+'</td><td><span class="badge '+c.status+'">'+c.status+'</span></td></tr>').join('');
    } catch(e) {}
}

async function loadLeads() {
    try {
        const leads = await fetch('/api/leads').then(r=>r.json());
        const total = leads.reduce((s,l)=>s+(l.value||0), 0);
        const weighted = leads.reduce((s,l)=>s+((l.value||0)*(l.probability||0)/100), 0);
        document.getElementById('pipelineValue').textContent = '€' + total.toLocaleString('de-DE');
        document.getElementById('weightedValue').textContent = '€' + Math.round(weighted).toLocaleString('de-DE');
        document.getElementById('leadsTable').innerHTML = leads.map(l => '<tr><td><strong>'+esc(l.name)+'</strong></td><td>'+esc(l.company)+'</td><td>€'+(l.value||0).toLocaleString('de-DE')+'</td><td><span class="badge '+l.stage+'">'+l.stage+'</span></td></tr>').join('');
    } catch(e) {}
}

async function loadCampaigns() {
    try {
        const campaigns = await fetch('/api/campaigns').then(r=>r.json());
        document.getElementById('campaignsTable').innerHTML = campaigns.map(c => '<tr><td><strong>'+esc(c.name)+'</strong></td><td>'+c.type+'</td><td>'+c.sent+'</td><td>'+c.opened+'</td><td><span class="badge '+c.status+'">'+c.status+'</span></td></tr>').join('');
    } catch(e) {}
}

async function loadInvoices() {
    try {
        const invoices = await fetch('/api/invoices').then(r=>r.json());
        document.getElementById('invoicesTable').innerHTML = invoices.map(i => '<tr><td><strong>'+i.id+'</strong></td><td>'+esc(i.customer)+'</td><td>€'+(i.amount||0).toLocaleString('de-DE')+'</td><td>'+i.due+'</td><td><span class="badge '+i.status+'">'+i.status+'</span></td></tr>').join('');
    } catch(e) {}
}

async function loadWhatsApp() {
    try {
        const stats = await fetch('/api/dashboard/stats').then(r=>r.json());
        document.getElementById('waSent').textContent = (stats.whatsapp_sent || 0).toLocaleString('de-DE');
        document.getElementById('waDelivered').textContent = (stats.whatsapp_delivered || 0).toLocaleString('de-DE');
        document.getElementById('emailSent').textContent = (stats.email_sent || 0).toLocaleString('de-DE');
        const templates = await fetch('/api/whatsapp/templates').then(r=>r.json());
        document.getElementById('waTemplates').innerHTML = templates.map(t => '<div class="template-card" onclick="useTemplate(\\''+t.name+'\\')"><div class="name">'+t.name+'</div><div class="preview">'+t.text+'</div></div>').join('');
    } catch(e) {}
}

async function sendWhatsApp() {
    const phone = document.getElementById('waPhone').value;
    const message = document.getElementById('waMessage').value;
    if (!phone || !message) return alert('Telefon und Nachricht eingeben');
    try {
        const r = await fetch('/api/whatsapp/send', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({phone, message})});
        const d = await r.json();
        if (d.success) { alert(d.demo ? 'Demo: Nachricht simuliert!' : 'Nachricht gesendet!'); document.getElementById('waMessage').value = ''; }
        else alert('Fehler: ' + (d.error || 'Unbekannt'));
    } catch(e) { alert('Fehler'); }
}

function useTemplate(name) { document.getElementById('waMessage').value = 'Template: ' + name; }

async function loadGaming() {
    try {
        const data = await fetch('/api/gaming/stats').then(r=>r.json());
        document.getElementById('gamingTwitch').textContent = (data.twitch_followers || 0).toLocaleString('de-DE');
        document.getElementById('gamingYoutube').textContent = (data.youtube_subs || 0).toLocaleString('de-DE');
        document.getElementById('gamingDiscord').textContent = (data.discord_members || 0).toLocaleString('de-DE');
        document.getElementById('gamingPeak').textContent = (data.peak_viewers || 0).toLocaleString('de-DE');
    } catch(e) {}
}

async function loadAutomations() {
    try {
        const data = await fetch('/api/automations/stats').then(r=>r.json());
        document.getElementById('autoSystems').textContent = data.active_systems || 0;
        document.getElementById('autoDevices').textContent = (data.devices_connected || 0).toLocaleString('de-DE');
        document.getElementById('autoEnergy').textContent = (data.energy_saved_kwh || 0).toLocaleString('de-DE') + ' kWh';
    } catch(e) {}
}

async function loadSecurity() {
    try {
        const data = await fetch('/api/security/stats').then(r=>r.json());
        document.getElementById('secThreats').textContent = (data.threats_blocked || 0).toLocaleString('de-DE');
        document.getElementById('secSystems').textContent = data.systems_protected || 0;
        document.getElementById('secUptime').textContent = (data.uptime_percent || 0) + '%';
        document.getElementById('secScore').textContent = (data.security_score || 0) + '/100';
    } catch(e) {}
}

async function loadNotifications() {
    try {
        const notifs = await fetch('/api/notifications').then(r=>r.json());
        const unread = notifs.filter(n => !n.read).length;
        document.getElementById('notifCount').textContent = unread;
    } catch(e) {}
}

function showNotifications() { alert('Benachrichtigungen - Feature kommt bald!'); }

async function syncHubSpot() {
    try {
        const r = await fetch('/api/hubspot/sync', {method:'POST'});
        const d = await r.json();
        if (d.success) alert(d.demo ? 'Demo: ' + d.synced + ' Kontakte simuliert synchronisiert' : d.synced + ' Kontakte synchronisiert!');
        else alert('Fehler: ' + (d.error || 'Unbekannt'));
    } catch(e) { alert('Fehler'); }
}

async function searchHR() {
    const q = document.getElementById('hrQuery').value.trim();
    if (!q) return alert('Suchbegriff eingeben');
    document.getElementById('hrResults').innerHTML = '<div class="empty-state"><p>Suche...</p></div>';
    try {
        const r = await fetch('/api/hr/search?q=' + encodeURIComponent(q));
        const data = await r.json();
        hrResults = data.results || [];
        document.getElementById('hrResultCount').textContent = hrResults.length + ' Treffer';
        if (!hrResults.length) {
            document.getElementById('hrResults').innerHTML = '<div class="empty-state"><div class="icon">🔍</div><p>Keine Ergebnisse</p></div>';
        } else {
            document.getElementById('hrResults').innerHTML = hrResults.map((r,i) => '<div class="result-item" onclick="importHR('+i+')"><div class="result-name">'+esc(r.name)+'</div><div class="result-meta">'+esc(r.register_type)+' | '+esc(r.city)+' | '+esc(r.type)+'</div></div>').join('');
        }
    } catch(e) {
        document.getElementById('hrResults').innerHTML = '<div class="empty-state"><p>Fehler</p></div>';
    }
}

async function importHR(idx) {
    const r = hrResults[idx];
    if (!r) return;
    if (confirm('Importieren: ' + r.name + '?')) {
        await fetch('/api/hr/import', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(r)});
        alert('✅ Importiert!');
        loadContacts();
    }
}

function showModal(type) { alert('Modal: ' + type + ' - Feature kommt!'); }
function esc(s) { return s ? String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') : ''; }
checkAuth();
</script>
</body>
</html>'''

if __name__ == '__main__':
    print("=" * 70)
    print("  ⚡ WEST MONEY OS v7.0 - ULTIMATE ENTERPRISE PLATFORM")
    print("=" * 70)
    print(f"  🌐 Landing:  http://localhost:{PORT}")
    print(f"  💳 Pricing:  http://localhost:{PORT}/pricing")
    print(f"  🎮 Demo:     http://localhost:{PORT}/demo")
    print(f"  📝 Register: http://localhost:{PORT}/register")
    print(f"  📊 App:      http://localhost:{PORT}/app")
    print("=" * 70)
    print("  🔑 Admin: admin / 663724")
    print("  🎮 Demo:  demo / demo123")
    print("=" * 70)
    print("  Integrations: WhatsApp | HubSpot | Stripe | Handelsregister")
    print("=" * 70)
    app.run(host='0.0.0.0', port=PORT, debug=False)
