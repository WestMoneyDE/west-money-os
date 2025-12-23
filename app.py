#!/usr/bin/env python3
"""
West Money OS v5.0 - MEGA FINAL EDITION
Enterprise Business Platform
© 2025 Enterprise Universe GmbH
"""

from flask import Flask, jsonify, request, Response, session
from flask_cors import CORS
import requests
import json
import os
import hashlib
import secrets
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

PORT = int(os.getenv('PORT', 5000))
OPENCORPORATES_API_KEY = os.getenv('OPENCORPORATES_API_KEY', '')

USERS = {
    'admin': {
        'password': hashlib.sha256('663724'.encode()).hexdigest(),
        'name': 'Ömer Coşkun',
        'email': 'info@west-money.com',
        'role': 'admin',
        'company': 'Enterprise Universe GmbH'
    }
}

DB = {
    'contacts': [
        {'id': 1, 'name': 'Max Mustermann', 'email': 'max@techgmbh.de', 'company': 'Tech GmbH', 'phone': '+49 221 12345678', 'status': 'active', 'source': 'Website', 'created': '2025-12-01'},
        {'id': 2, 'name': 'Anna Schmidt', 'email': 'anna@startup.de', 'company': 'StartUp AG', 'phone': '+49 89 98765432', 'status': 'active', 'source': 'Handelsregister', 'created': '2025-12-05'},
        {'id': 3, 'name': 'Thomas Weber', 'email': 'weber@industrie.de', 'company': 'Industrie KG', 'phone': '+49 211 55555555', 'status': 'lead', 'source': 'Explorium', 'created': '2025-12-10'},
        {'id': 4, 'name': 'Julia Becker', 'email': 'j.becker@finance.de', 'company': 'Finance Plus GmbH', 'phone': '+49 69 44444444', 'status': 'active', 'source': 'Messe', 'created': '2025-12-12'},
        {'id': 5, 'name': 'Michael Schulz', 'email': 'schulz@consulting.de', 'company': 'Consulting Pro', 'phone': '+49 40 33333333', 'status': 'inactive', 'source': 'Referral', 'created': '2025-12-15'},
    ],
    'leads': [
        {'id': 1, 'name': 'ERP System Implementation', 'company': 'Digital GmbH', 'contact': 'Klaus Digital', 'email': 'klaus@digital.de', 'value': 45000, 'stage': 'qualified', 'probability': 60, 'created': '2025-12-01', 'next_action': '2025-12-28'},
        {'id': 2, 'name': 'Cloud Migration Project', 'company': 'Cloud Solutions AG', 'contact': 'Maria Cloud', 'email': 'maria@cloudsolutions.de', 'value': 75000, 'stage': 'proposal', 'probability': 75, 'created': '2025-12-05', 'next_action': '2025-12-26'},
        {'id': 3, 'name': 'Security Audit', 'company': 'SecureTech', 'contact': 'Peter Secure', 'email': 'peter@securetech.de', 'value': 25000, 'stage': 'negotiation', 'probability': 85, 'created': '2025-12-10', 'next_action': '2025-12-24'},
        {'id': 4, 'name': 'AI Integration', 'company': 'Future Corp', 'contact': 'Lisa Future', 'email': 'lisa@futurecorp.de', 'value': 120000, 'stage': 'discovery', 'probability': 30, 'created': '2025-12-15', 'next_action': '2026-01-05'},
        {'id': 5, 'name': 'Website Redesign', 'company': 'Brand Masters', 'contact': 'Tom Brand', 'email': 'tom@brandmasters.de', 'value': 18000, 'stage': 'won', 'probability': 100, 'created': '2025-11-20', 'next_action': None},
    ],
    'campaigns': [
        {'id': 1, 'name': 'Q4 Newsletter', 'type': 'email', 'status': 'active', 'sent': 2500, 'opened': 1125, 'clicked': 340, 'converted': 28, 'created': '2025-12-01'},
        {'id': 2, 'name': 'Product Launch 2025', 'type': 'email', 'status': 'completed', 'sent': 5000, 'opened': 2750, 'clicked': 890, 'converted': 67, 'created': '2025-11-15'},
        {'id': 3, 'name': 'Holiday Special', 'type': 'email', 'status': 'draft', 'sent': 0, 'opened': 0, 'clicked': 0, 'converted': 0, 'created': '2025-12-20'},
    ],
    'subscriptions': [
        {'id': 1, 'customer': 'Tech GmbH', 'email': 'billing@techgmbh.de', 'plan': 'Professional', 'price': 99, 'status': 'active', 'next_billing': '2026-01-01', 'mrr': 99},
        {'id': 2, 'customer': 'StartUp AG', 'email': 'finance@startup.de', 'plan': 'Enterprise', 'price': 299, 'status': 'active', 'next_billing': '2026-01-15', 'mrr': 299},
        {'id': 3, 'customer': 'Digital Solutions', 'email': 'admin@digital.de', 'plan': 'Starter', 'price': 29, 'status': 'active', 'next_billing': '2026-01-01', 'mrr': 29},
        {'id': 4, 'customer': 'AI Innovations', 'email': 'finance@ai-innovations.de', 'plan': 'Enterprise', 'price': 299, 'status': 'active', 'next_billing': '2026-01-01', 'mrr': 299},
    ],
    'invoices': [
        {'id': 'INV-2025-001', 'customer': 'Tech GmbH', 'amount': 1188, 'status': 'paid', 'date': '2025-12-01', 'due': '2025-12-15', 'items': 'Professional Plan (12 months)'},
        {'id': 'INV-2025-002', 'customer': 'StartUp AG', 'amount': 3588, 'status': 'paid', 'date': '2025-12-01', 'due': '2025-12-15', 'items': 'Enterprise Plan (12 months)'},
        {'id': 'INV-2025-003', 'customer': 'Digital Solutions', 'amount': 348, 'status': 'pending', 'date': '2025-12-15', 'due': '2025-12-30', 'items': 'Starter Plan (12 months)'},
    ],
    'activities': [
        {'id': 1, 'type': 'call', 'contact': 'Max Mustermann', 'description': 'Follow-up call regarding proposal', 'date': '2025-12-23 14:30'},
        {'id': 2, 'type': 'email', 'contact': 'Anna Schmidt', 'description': 'Sent product documentation', 'date': '2025-12-23 11:00'},
        {'id': 3, 'type': 'meeting', 'contact': 'Thomas Weber', 'description': 'Demo presentation scheduled', 'date': '2025-12-22 15:00'},
    ],
    'stats': {
        'revenue': 847000, 'revenue_growth': 23.5, 'leads': 47, 'leads_growth': 15,
        'customers': 156, 'customers_growth': 12, 'mrr': 12850, 'mrr_growth': 8.2,
        'churn': 2.1, 'ltv': 2850, 'cac': 450, 'nps': 72
    },
    'chart_data': {
        'labels': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
        'revenue': [52000, 58000, 61000, 67000, 72000, 69000, 78000, 82000, 89000, 95000, 102000, 125000],
        'leads': [28, 35, 32, 41, 38, 45, 52, 48, 56, 62, 58, 47],
        'customers': [98, 105, 112, 118, 125, 128, 134, 139, 145, 149, 153, 156],
        'mrr': [8200, 8800, 9100, 9600, 10200, 10500, 11000, 11400, 11900, 12200, 12500, 12850]
    }
}

# AUTH
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '')
    password = data.get('password', '')
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    if username in USERS and USERS[username]['password'] == pw_hash:
        session['user'] = username
        user = USERS[username]
        return jsonify({'success': True, 'user': {'name': user['name'], 'email': user['email'], 'role': user['role'], 'company': user['company']}})
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/status')
def auth_status():
    if 'user' in session:
        user = USERS.get(session['user'], {})
        return jsonify({'authenticated': True, 'user': {'name': user.get('name'), 'email': user.get('email'), 'role': user.get('role'), 'company': user.get('company')}})
    return jsonify({'authenticated': False})

# DASHBOARD
@app.route('/api/dashboard/stats')
def dashboard_stats():
    return jsonify(DB['stats'])

@app.route('/api/dashboard/charts')
def dashboard_charts():
    return jsonify(DB['chart_data'])

@app.route('/api/dashboard/activities')
def dashboard_activities():
    return jsonify(DB['activities'][:10])

@app.route('/api/dashboard/pipeline')
def dashboard_pipeline():
    stages = {'discovery': 0, 'qualified': 0, 'proposal': 0, 'negotiation': 0, 'won': 0, 'lost': 0}
    for lead in DB['leads']:
        if lead['stage'] in stages:
            stages[lead['stage']] += lead['value']
    return jsonify(stages)

# CONTACTS
@app.route('/api/contacts')
def get_contacts():
    return jsonify(DB['contacts'])

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    data = request.json
    new_id = max([c['id'] for c in DB['contacts']], default=0) + 1
    contact = {'id': new_id, 'name': data.get('name', ''), 'email': data.get('email', ''), 'company': data.get('company', ''), 'phone': data.get('phone', ''), 'status': data.get('status', 'lead'), 'source': data.get('source', 'Manual'), 'created': datetime.now().strftime('%Y-%m-%d')}
    DB['contacts'].append(contact)
    return jsonify(contact)

@app.route('/api/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    DB['contacts'] = [c for c in DB['contacts'] if c['id'] != id]
    return jsonify({'success': True})

# LEADS
@app.route('/api/leads')
def get_leads():
    return jsonify(DB['leads'])

@app.route('/api/leads', methods=['POST'])
def create_lead():
    data = request.json
    new_id = max([l['id'] for l in DB['leads']], default=0) + 1
    lead = {'id': new_id, 'name': data.get('name', ''), 'company': data.get('company', ''), 'contact': data.get('contact', ''), 'email': data.get('email', ''), 'value': int(data.get('value', 0)), 'stage': data.get('stage', 'discovery'), 'probability': int(data.get('probability', 10)), 'created': datetime.now().strftime('%Y-%m-%d'), 'next_action': data.get('next_action')}
    DB['leads'].append(lead)
    return jsonify(lead)

# CAMPAIGNS
@app.route('/api/campaigns')
def get_campaigns():
    return jsonify(DB['campaigns'])

# SUBSCRIPTIONS
@app.route('/api/subscriptions')
def get_subscriptions():
    return jsonify(DB['subscriptions'])

@app.route('/api/invoices')
def get_invoices():
    return jsonify(DB['invoices'])

@app.route('/api/billing/stats')
def billing_stats():
    active = [s for s in DB['subscriptions'] if s['status'] == 'active']
    return jsonify({'mrr': sum(s['mrr'] for s in active), 'active_subscriptions': len(active), 'total_revenue': sum(i['amount'] for i in DB['invoices'] if i['status'] == 'paid'), 'pending_invoices': sum(1 for i in DB['invoices'] if i['status'] == 'pending'), 'pending_amount': sum(i['amount'] for i in DB['invoices'] if i['status'] == 'pending')})

# HANDELSREGISTER
@app.route('/api/hr/search')
def hr_search():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'results': [], 'total': 0})
    try:
        url = 'https://api.opencorporates.com/v0.4/companies/search'
        params = {'q': q, 'jurisdiction_code': 'de', 'per_page': 30, 'order': 'score'}
        if OPENCORPORATES_API_KEY:
            params['api_token'] = OPENCORPORATES_API_KEY
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        results = []
        for item in data.get('results', {}).get('companies', []):
            c = item.get('company', {})
            addr = c.get('registered_address', {}) or {}
            cn = (c.get('company_number') or '').upper()
            reg_type = ''
            for rt in ['HRB', 'HRA', 'GNR', 'PR', 'VR']:
                if rt in cn:
                    reg_type = rt
                    break
            results.append({'id': c.get('company_number', ''), 'name': c.get('name', ''), 'register_type': reg_type, 'register_number': c.get('company_number', ''), 'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv', 'type': c.get('company_type', ''), 'city': addr.get('locality', '') or addr.get('region', '') or '', 'address': ', '.join(filter(None, [addr.get('street_address'), addr.get('postal_code'), addr.get('locality')])), 'founded': c.get('incorporation_date', ''), 'url': c.get('opencorporates_url', '')})
        return jsonify({'success': True, 'query': q, 'total': data.get('results', {}).get('total_count', 0), 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'results': [], 'total': 0})

@app.route('/api/hr/company/<path:id>')
def hr_company(id):
    try:
        url = f'https://api.opencorporates.com/v0.4/companies/de/{id}'
        params = {}
        if OPENCORPORATES_API_KEY:
            params['api_token'] = OPENCORPORATES_API_KEY
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        c = data.get('results', {}).get('company', {})
        addr = c.get('registered_address', {}) or {}
        officers = []
        for o in c.get('officers', []):
            off = o.get('officer', {})
            officers.append({'name': off.get('name', ''), 'position': off.get('position', ''), 'start_date': off.get('start_date', ''), 'end_date': off.get('end_date', '')})
        return jsonify({'success': True, 'id': c.get('company_number', ''), 'name': c.get('name', ''), 'type': c.get('company_type', ''), 'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv', 'founded': c.get('incorporation_date', ''), 'address': ', '.join(filter(None, [addr.get('street_address'), addr.get('postal_code'), addr.get('locality')])), 'officers': officers, 'filings': len(c.get('filings', [])), 'url': c.get('opencorporates_url', ''), 'source': c.get('registry_url', '')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/hr/import', methods=['POST'])
def hr_import():
    data = request.json
    new_id = max([c['id'] for c in DB['contacts']], default=0) + 1
    contact = {'id': new_id, 'name': data.get('name', ''), 'email': '', 'company': data.get('name', ''), 'phone': '', 'status': 'lead', 'source': 'Handelsregister', 'created': datetime.now().strftime('%Y-%m-%d')}
    DB['contacts'].append(contact)
    return jsonify({'success': True, 'contact': contact})

# EXPLORIUM
@app.route('/api/explorium/stats')
def explorium_stats():
    return jsonify({'credits': 4873, 'used_this_month': 127, 'plan': 'Professional', 'searches': 89, 'enrichments': 156, 'exports': 23})

# HEALTH
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'version': '5.0.0', 'service': 'West Money OS - Mega Final Edition', 'timestamp': datetime.now().isoformat()})

# FRONTEND - Using Response to avoid Jinja2 template issues
@app.route('/')
def index():
    return Response(FRONTEND_HTML, mimetype='text/html')

FRONTEND_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>West Money OS v5.0 | Enterprise Business Platform</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{--bg-0:#09090b;--bg-1:#0f0f12;--bg-2:#161619;--bg-3:#1c1c20;--bg-4:#252529;--text-0:#fafafa;--text-1:#e4e4e7;--text-2:#a1a1aa;--text-3:#71717a;--primary:#6366f1;--primary-h:#818cf8;--primary-glow:rgba(99,102,241,.15);--emerald:#10b981;--amber:#f59e0b;--rose:#f43f5e;--cyan:#06b6d4;--violet:#8b5cf6;--border:rgba(255,255,255,.08);--radius:8px;--radius-lg:12px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg-0);color:var(--text-0);font-size:14px;line-height:1.5;min-height:100vh}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:var(--bg-1)}::-webkit-scrollbar-thumb{background:var(--bg-4);border-radius:3px}
.login-screen{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--bg-0) 0%,#0a0a15 50%,#12061f 100%)}
.login-box{background:var(--bg-2);border:1px solid var(--border);border-radius:20px;padding:48px;width:100%;max-width:420px}
.login-logo{text-align:center;margin-bottom:32px}
.login-logo-icon{width:72px;height:72px;background:linear-gradient(135deg,var(--primary),var(--violet));border-radius:18px;display:inline-flex;align-items:center;justify-content:center;font-size:32px;margin-bottom:16px;box-shadow:0 8px 32px rgba(99,102,241,.4)}
.login-logo h1{font-size:26px;font-weight:700;margin-bottom:4px}
.login-logo p{color:var(--text-3);font-size:14px}
.login-logo .version{display:inline-block;background:linear-gradient(135deg,var(--emerald),var(--cyan));color:white;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600;margin-top:8px}
.form-group{margin-bottom:20px}
.form-group label{display:block;font-size:13px;font-weight:500;margin-bottom:8px;color:var(--text-1)}
.form-input{width:100%;padding:14px 16px;background:var(--bg-3);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-0);font-size:14px}
.form-input:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-glow)}
.login-btn{width:100%;padding:14px;background:linear-gradient(135deg,var(--primary),var(--violet));color:white;border:none;border-radius:var(--radius);font-size:14px;font-weight:600;cursor:pointer;margin-top:8px}
.login-btn:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(99,102,241,.4)}
.login-error{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);color:#ef4444;padding:12px;border-radius:var(--radius);margin-bottom:20px;text-align:center;display:none}
.login-error.show{display:block}
.app{display:none;min-height:100vh}
.app.active{display:flex}
.sidebar{width:260px;background:var(--bg-1);border-right:1px solid var(--border);position:fixed;height:100vh;display:flex;flex-direction:column;z-index:100}
.sidebar-header{padding:20px;border-bottom:1px solid var(--border)}
.logo{display:flex;align-items:center;gap:12px}
.logo-icon{width:42px;height:42px;background:linear-gradient(135deg,var(--primary),var(--violet));border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px}
.logo-text h1{font-size:16px;font-weight:700}
.logo-text span{font-size:10px;color:var(--text-3)}
.sidebar-nav{flex:1;padding:12px;overflow-y:auto}
.nav-section{margin-bottom:8px}
.nav-section-title{font-size:10px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.5px;padding:12px 12px 8px}
.nav-item{display:flex;align-items:center;gap:12px;padding:11px 12px;border-radius:var(--radius);cursor:pointer;color:var(--text-2);font-size:13px;transition:all .15s;margin-bottom:2px}
.nav-item:hover{background:var(--bg-3);color:var(--text-0)}
.nav-item.active{background:var(--primary-glow);color:var(--primary-h);border:1px solid rgba(99,102,241,.2)}
.nav-item .icon{width:20px;text-align:center;font-size:15px}
.nav-item .text{flex:1}
.nav-item .badge{font-size:10px;padding:3px 8px;border-radius:10px;font-weight:600}
.nav-item .badge.count{background:var(--primary);color:white}
.nav-item .badge.live{background:var(--rose);color:white}
.nav-item .badge.api{background:var(--cyan);color:white}
.nav-item .badge.stripe{background:#635bff;color:white}
.sidebar-footer{padding:12px;border-top:1px solid var(--border)}
.user-card{display:flex;align-items:center;gap:12px;padding:12px;background:var(--bg-2);border-radius:var(--radius)}
.user-avatar{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,var(--emerald),var(--cyan));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
.user-info{flex:1}
.user-info .name{font-size:13px;font-weight:600}
.user-info .role{font-size:11px;color:var(--text-3)}
.logout-btn{background:none;border:none;color:var(--text-3);cursor:pointer;padding:8px;font-size:16px}
.logout-btn:hover{color:var(--rose)}
.main{flex:1;margin-left:260px;display:flex;flex-direction:column;min-height:100vh}
.topbar{height:64px;background:var(--bg-1);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 24px;position:sticky;top:0;z-index:50}
.breadcrumb{font-size:14px;color:var(--text-2)}
.breadcrumb strong{color:var(--text-0)}
.api-status{display:flex;align-items:center;gap:8px;padding:8px 16px;background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.2);border-radius:20px;font-size:12px;font-weight:600;color:var(--emerald)}
.api-status .dot{width:8px;height:8px;border-radius:50%;background:var(--emerald);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.content{padding:24px;flex:1}
.page{display:none}
.page.active{display:block;animation:fadeIn .3s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.page-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px;flex-wrap:wrap;gap:16px}
.page-header h1{font-size:28px;font-weight:700;display:flex;align-items:center;gap:12px}
.page-header p{color:var(--text-2);font-size:14px;margin-top:4px}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.stat-card{background:var(--bg-2);border:1px solid var(--border);border-radius:var(--radius-lg);padding:20px}
.stat-card:hover{border-color:rgba(255,255,255,.15);transform:translateY(-2px)}
.stat-card.primary{border-left:3px solid var(--primary)}
.stat-card.emerald{border-left:3px solid var(--emerald)}
.stat-card.amber{border-left:3px solid var(--amber)}
.stat-card.violet{border-left:3px solid var(--violet)}
.stat-card.rose{border-left:3px solid var(--rose)}
.stat-card.cyan{border-left:3px solid var(--cyan)}
.stat-card .label{font-size:12px;color:var(--text-3);margin-bottom:8px;font-weight:500}
.stat-card .value{font-size:28px;font-weight:700;line-height:1}
.stat-card .change{font-size:12px;margin-top:8px}
.stat-card .change.up{color:var(--emerald)}
.stat-card .change.down{color:var(--rose)}
.card{background:var(--bg-2);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;margin-bottom:20px}
.card-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.card-header h3{font-size:15px;font-weight:600;display:flex;align-items:center;gap:8px}
.card-body{padding:20px}
.card-body.no-padding{padding:0}
.grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:10px 18px;border-radius:var(--radius);font-size:13px;font-weight:500;cursor:pointer;border:none;transition:all .15s}
.btn-primary{background:var(--primary);color:white}
.btn-primary:hover{background:var(--primary-h)}
.btn-secondary{background:var(--bg-3);color:var(--text-0);border:1px solid var(--border)}
.btn-success{background:var(--emerald);color:white}
table{width:100%;border-collapse:collapse}
th,td{text-align:left;padding:14px 16px;border-bottom:1px solid var(--border)}
th{font-size:11px;font-weight:600;color:var(--text-3);text-transform:uppercase;letter-spacing:.5px;background:var(--bg-3)}
tbody tr:hover{background:var(--bg-3)}
.badge{display:inline-flex;padding:4px 10px;border-radius:6px;font-size:11px;font-weight:600}
.badge.active,.badge.paid,.badge.aktiv,.badge.won{background:rgba(16,185,129,.15);color:var(--emerald)}
.badge.pending,.badge.lead,.badge.qualified,.badge.discovery{background:rgba(245,158,11,.15);color:var(--amber)}
.badge.inactive,.badge.inaktiv,.badge.cancelled,.badge.lost{background:rgba(244,63,94,.15);color:var(--rose)}
.badge.proposal,.badge.negotiation{background:rgba(99,102,241,.15);color:var(--primary)}
.badge.hrb{background:rgba(99,102,241,.15);color:var(--primary)}
.badge.hra{background:rgba(16,185,129,.15);color:var(--emerald)}
.search-box{background:var(--bg-2);border:1px solid var(--border);border-radius:var(--radius-lg);padding:20px;margin-bottom:20px}
.search-row{display:flex;gap:12px}
.search-input{flex:1;padding:12px 16px;background:var(--bg-3);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-0);font-size:14px}
.search-input:focus{outline:none;border-color:var(--primary)}
.result-item{padding:16px 20px;border-bottom:1px solid var(--border);cursor:pointer}
.result-item:hover{background:var(--bg-3)}
.result-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.result-name{font-size:15px;font-weight:600}
.result-meta{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;font-size:12px}
.result-meta span{color:var(--text-3)}
.result-meta strong{color:var(--text-0);display:block;margin-top:2px}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.8);display:none;align-items:center;justify-content:center;z-index:1000;padding:24px}
.modal-overlay.active{display:flex}
.modal{background:var(--bg-2);border:1px solid var(--border);border-radius:16px;width:100%;max-width:640px;max-height:90vh;overflow:hidden}
.modal-header{padding:20px 24px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.modal-header h2{font-size:18px;font-weight:600}
.modal-close{background:none;border:none;color:var(--text-2);font-size:24px;cursor:pointer}
.modal-body{padding:24px;overflow-y:auto;max-height:60vh}
.modal-footer{padding:16px 24px;border-top:1px solid var(--border);display:flex;justify-content:flex-end;gap:12px}
.detail-section{background:var(--bg-3);border-radius:var(--radius);padding:16px;margin-bottom:16px}
.detail-section h4{font-size:13px;font-weight:600;color:var(--text-2);margin-bottom:12px}
.detail-section p{font-size:14px;margin-bottom:8px}
.empty-state{text-align:center;padding:60px 20px;color:var(--text-3)}
.empty-state .icon{font-size:48px;margin-bottom:16px;opacity:.5}
.chart-container{position:relative;height:280px}
.activity-item{display:flex;gap:12px;padding:12px 0;border-bottom:1px solid var(--border)}
.activity-icon{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px}
.activity-icon.call{background:rgba(16,185,129,.15);color:var(--emerald)}
.activity-icon.email{background:rgba(99,102,241,.15);color:var(--primary)}
.activity-icon.meeting{background:rgba(245,158,11,.15);color:var(--amber)}
.activity-content{flex:1}
.activity-content .title{font-size:13px;font-weight:500;margin-bottom:2px}
.activity-content .desc{font-size:12px;color:var(--text-3)}
.activity-time{font-size:11px;color:var(--text-3)}
@media(max-width:1200px){.stats-grid{grid-template-columns:repeat(2,1fr)}.result-meta{grid-template-columns:repeat(2,1fr)}}
@media(max-width:900px){.sidebar{display:none}.main{margin-left:0}.grid-2{grid-template-columns:1fr}}
@media(max-width:600px){.stats-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="login-screen" id="loginScreen">
<div class="login-box">
<div class="login-logo">
<div class="login-logo-icon">⚡</div>
<h1>West Money OS</h1>
<p>Enterprise Business Platform</p>
<span class="version">v5.0 Mega Final Edition</span>
</div>
<div class="login-error" id="loginError">Ungültige Anmeldedaten</div>
<div class="form-group">
<label>Benutzername</label>
<input type="text" class="form-input" id="loginUser" value="admin" placeholder="admin">
</div>
<div class="form-group">
<label>Passwort</label>
<input type="password" class="form-input" id="loginPass" placeholder="••••••" onkeypress="if(event.key==='Enter')doLogin()">
</div>
<button class="login-btn" onclick="doLogin()">🔐 Anmelden</button>
</div>
</div>

<div class="app" id="app">
<aside class="sidebar">
<div class="sidebar-header">
<div class="logo">
<div class="logo-icon">⚡</div>
<div class="logo-text"><h1>West Money OS</h1><span>v5.0 Mega Final</span></div>
</div>
</div>
<nav class="sidebar-nav">
<div class="nav-section">
<div class="nav-section-title">Übersicht</div>
<div class="nav-item active" data-page="dashboard"><span class="icon">📊</span><span class="text">Dashboard</span></div>
<div class="nav-item" data-page="analytics"><span class="icon">📈</span><span class="text">Analytics</span></div>
</div>
<div class="nav-section">
<div class="nav-section-title">CRM</div>
<div class="nav-item" data-page="contacts"><span class="icon">👥</span><span class="text">Kontakte</span><span class="badge count" id="contactCount">5</span></div>
<div class="nav-item" data-page="leads"><span class="icon">🎯</span><span class="text">Leads</span><span class="badge count">5</span></div>
</div>
<div class="nav-section">
<div class="nav-section-title">Marketing</div>
<div class="nav-item" data-page="campaigns"><span class="icon">📧</span><span class="text">Kampagnen</span></div>
</div>
<div class="nav-section">
<div class="nav-section-title">Daten & APIs</div>
<div class="nav-item" data-page="handelsregister"><span class="icon">🏛️</span><span class="text">Handelsregister</span><span class="badge live">LIVE</span></div>
<div class="nav-item" data-page="explorium"><span class="icon">🔍</span><span class="text">Explorium</span><span class="badge api">API</span></div>
</div>
<div class="nav-section">
<div class="nav-section-title">Finanzen</div>
<div class="nav-item" data-page="subscriptions"><span class="icon">💳</span><span class="text">Abonnements</span><span class="badge stripe">Stripe</span></div>
<div class="nav-item" data-page="invoices"><span class="icon">📄</span><span class="text">Rechnungen</span></div>
</div>
<div class="nav-section">
<div class="nav-section-title">System</div>
<div class="nav-item" data-page="settings"><span class="icon">⚙️</span><span class="text">Einstellungen</span></div>
</div>
</nav>
<div class="sidebar-footer">
<div class="user-card">
<div class="user-avatar" id="userAvatar">ÖC</div>
<div class="user-info"><div class="name" id="userName">Ömer Coşkun</div><div class="role">Administrator</div></div>
<button class="logout-btn" onclick="doLogout()" title="Logout">🚪</button>
</div>
</div>
</aside>

<main class="main">
<header class="topbar">
<div class="breadcrumb">West Money OS / <strong id="currentPage">Dashboard</strong></div>
<div class="api-status"><span class="dot"></span>All Systems Online</div>
</header>

<div class="content">
<!-- DASHBOARD -->
<div class="page active" id="page-dashboard">
<div class="page-header"><div><h1>📊 Dashboard</h1><p>Willkommen zurück! Hier ist dein Business-Überblick.</p></div></div>
<div class="stats-grid">
<div class="stat-card primary"><div class="label">Gesamtumsatz</div><div class="value" id="statRevenue">€0</div><div class="change up" id="statRevenueGrowth">↑ 0%</div></div>
<div class="stat-card emerald"><div class="label">Aktive Leads</div><div class="value" id="statLeads">0</div><div class="change up">↑ diese Woche</div></div>
<div class="stat-card amber"><div class="label">Kunden</div><div class="value" id="statCustomers">0</div><div class="change up">↑ 0%</div></div>
<div class="stat-card violet"><div class="label">MRR</div><div class="value" id="statMRR">€0</div><div class="change up">↑ 0%</div></div>
</div>
<div class="grid-2">
<div class="card"><div class="card-header"><h3>📈 Umsatzentwicklung</h3></div><div class="card-body"><div class="chart-container"><canvas id="revenueChart"></canvas></div></div></div>
<div class="card"><div class="card-header"><h3>🎯 Lead Pipeline</h3></div><div class="card-body"><div class="chart-container"><canvas id="pipelineChart"></canvas></div></div></div>
</div>
<div class="grid-2">
<div class="card"><div class="card-header"><h3>📅 Letzte Aktivitäten</h3></div><div class="card-body" id="activitiesList"></div></div>
<div class="card"><div class="card-header"><h3>📊 MRR Entwicklung</h3></div><div class="card-body"><div class="chart-container"><canvas id="mrrChart"></canvas></div></div></div>
</div>
</div>

<!-- ANALYTICS -->
<div class="page" id="page-analytics">
<div class="page-header"><div><h1>📈 Analytics</h1><p>Detaillierte Auswertungen und KPIs</p></div></div>
<div class="stats-grid">
<div class="stat-card cyan"><div class="label">LTV</div><div class="value" id="statLTV">€0</div><div class="change">Lifetime Value</div></div>
<div class="stat-card amber"><div class="label">CAC</div><div class="value" id="statCAC">€0</div><div class="change">Acquisition Cost</div></div>
<div class="stat-card rose"><div class="label">Churn Rate</div><div class="value" id="statChurn">0%</div><div class="change">Monatlich</div></div>
<div class="stat-card emerald"><div class="label">NPS</div><div class="value" id="statNPS">0</div><div class="change">Net Promoter Score</div></div>
</div>
<div class="card"><div class="card-header"><h3>📊 Kundenentwicklung</h3></div><div class="card-body"><div class="chart-container"><canvas id="customersChart"></canvas></div></div></div>
</div>

<!-- CONTACTS -->
<div class="page" id="page-contacts">
<div class="page-header"><div><h1>👥 Kontakte</h1><p>Alle deine Kontakte verwalten</p></div><div><button class="btn btn-primary" onclick="showModal('newContact')">+ Neuer Kontakt</button></div></div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Name</th><th>E-Mail</th><th>Unternehmen</th><th>Telefon</th><th>Quelle</th><th>Status</th></tr></thead><tbody id="contactsTable"></tbody></table></div></div>
</div>

<!-- LEADS -->
<div class="page" id="page-leads">
<div class="page-header"><div><h1>🎯 Leads</h1><p>Deine Verkaufschancen im Überblick</p></div><div><button class="btn btn-primary" onclick="showModal('newLead')">+ Neuer Lead</button></div></div>
<div class="stats-grid">
<div class="stat-card"><div class="label">Pipeline Wert</div><div class="value" id="pipelineValue">€0</div></div>
<div class="stat-card emerald"><div class="label">Gewichteter Wert</div><div class="value" id="weightedValue">€0</div></div>
<div class="stat-card amber"><div class="label">Offene Leads</div><div class="value" id="openLeads">0</div></div>
<div class="stat-card primary"><div class="label">Ø Deal Size</div><div class="value" id="avgDeal">€0</div></div>
</div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Projekt</th><th>Unternehmen</th><th>Kontakt</th><th>Wert</th><th>Phase</th><th>Wahrsch.</th></tr></thead><tbody id="leadsTable"></tbody></table></div></div>
</div>

<!-- CAMPAIGNS -->
<div class="page" id="page-campaigns">
<div class="page-header"><div><h1>📧 Kampagnen</h1><p>E-Mail Marketing Kampagnen</p></div></div>
<div class="stats-grid">
<div class="stat-card primary"><div class="label">Gesamt versendet</div><div class="value" id="totalSent">0</div></div>
<div class="stat-card emerald"><div class="label">Öffnungsrate</div><div class="value" id="openRate">0%</div></div>
<div class="stat-card amber"><div class="label">Klickrate</div><div class="value" id="clickRate">0%</div></div>
<div class="stat-card violet"><div class="label">Conversions</div><div class="value" id="conversions">0</div></div>
</div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Kampagne</th><th>Versendet</th><th>Geöffnet</th><th>Geklickt</th><th>Conversions</th><th>Status</th></tr></thead><tbody id="campaignsTable"></tbody></table></div></div>
</div>

<!-- HANDELSREGISTER -->
<div class="page" id="page-handelsregister">
<div class="page-header"><div><h1>🏛️ Handelsregister</h1><p>Echte Firmendaten aus dem deutschen Handelsregister</p></div></div>
<div class="stats-grid">
<div class="stat-card primary"><div class="label">Suchen heute</div><div class="value" id="hrSearches">0</div></div>
<div class="stat-card emerald"><div class="label">Importiert</div><div class="value" id="hrImported">0</div></div>
<div class="stat-card amber"><div class="label">HRB</div><div class="value" id="hrHRB">-</div></div>
<div class="stat-card cyan"><div class="label">HRA</div><div class="value" id="hrHRA">-</div></div>
</div>
<div class="search-box">
<div class="search-row">
<input type="text" class="search-input" id="hrQuery" placeholder="🔍 Firmenname eingeben (z.B. Siemens, BMW...)" onkeypress="if(event.key==='Enter')searchHR()">
<button class="btn btn-primary" onclick="searchHR()">🏛️ Suchen</button>
</div>
</div>
<div class="card"><div class="card-header"><h3>🔍 Suchergebnisse</h3><span class="badge" id="hrResultCount">0 Treffer</span></div><div class="card-body no-padding" id="hrResults"><div class="empty-state"><div class="icon">🏛️</div><p>Suche starten um echte Handelsregister-Daten abzurufen</p></div></div></div>
</div>

<!-- EXPLORIUM -->
<div class="page" id="page-explorium">
<div class="page-header"><div><h1>🔍 Explorium</h1><p>B2B Daten & Lead Enrichment</p></div></div>
<div class="stats-grid">
<div class="stat-card primary"><div class="label">API Credits</div><div class="value" id="expCredits">0</div></div>
<div class="stat-card emerald"><div class="label">Enrichments</div><div class="value" id="expEnrichments">0</div></div>
<div class="stat-card amber"><div class="label">Suchen</div><div class="value" id="expSearches">0</div></div>
<div class="stat-card cyan"><div class="label">Exports</div><div class="value" id="expExports">0</div></div>
</div>
<div class="card"><div class="card-header"><h3>🔗 API Status</h3></div><div class="card-body"><p><strong>Status:</strong> <span class="badge active">✅ Verbunden</span></p><p><strong>Plan:</strong> Professional</p></div></div>
</div>

<!-- SUBSCRIPTIONS -->
<div class="page" id="page-subscriptions">
<div class="page-header"><div><h1>💳 Abonnements</h1><p>Stripe Subscription Management</p></div></div>
<div class="stats-grid">
<div class="stat-card primary"><div class="label">MRR</div><div class="value" id="subMRR">€0</div></div>
<div class="stat-card emerald"><div class="label">Aktive Abos</div><div class="value" id="subActive">0</div></div>
<div class="stat-card amber"><div class="label">Offene Rechnungen</div><div class="value" id="subPending">0</div></div>
<div class="stat-card violet"><div class="label">Offener Betrag</div><div class="value" id="subPendingAmount">€0</div></div>
</div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Kunde</th><th>E-Mail</th><th>Plan</th><th>Preis</th><th>Nächste Zahlung</th><th>Status</th></tr></thead><tbody id="subscriptionsTable"></tbody></table></div></div>
</div>

<!-- INVOICES -->
<div class="page" id="page-invoices">
<div class="page-header"><div><h1>📄 Rechnungen</h1><p>Alle Rechnungen im Überblick</p></div></div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Nummer</th><th>Kunde</th><th>Beschreibung</th><th>Betrag</th><th>Fällig</th><th>Status</th></tr></thead><tbody id="invoicesTable"></tbody></table></div></div>
</div>

<!-- SETTINGS -->
<div class="page" id="page-settings">
<div class="page-header"><div><h1>⚙️ Einstellungen</h1><p>System-Konfiguration</p></div></div>
<div class="grid-2">
<div class="card"><div class="card-header"><h3>🏢 Unternehmen</h3></div><div class="card-body"><p><strong>Firma:</strong> Enterprise Universe GmbH</p><p><strong>Domain:</strong> west-money.com</p><p><strong>Zeitzone:</strong> Europe/Berlin</p></div></div>
<div class="card"><div class="card-header"><h3>🔗 Integrationen</h3></div><div class="card-body"><p>✅ Handelsregister (OpenCorporates)</p><p>✅ Explorium B2B Data</p><p>✅ Stripe Payments</p><p>⬜ WhatsApp Business</p></div></div>
</div>
<div class="card"><div class="card-header"><h3>📊 System Status</h3></div><div class="card-body"><p><strong>Version:</strong> West Money OS v5.0 Mega Final Edition</p><p><strong>SSL:</strong> <span class="badge active">✅ Aktiv</span></p><p><strong>API:</strong> <span class="badge active">✅ Online</span></p></div></div>
</div>
</div>
</main>
</div>

<div class="modal-overlay" id="modal" onclick="if(event.target===this)closeModal()">
<div class="modal">
<div class="modal-header"><h2 id="modalTitle">Modal</h2><button class="modal-close" onclick="closeModal()">&times;</button></div>
<div class="modal-body" id="modalBody"></div>
<div class="modal-footer" id="modalFooter"></div>
</div>
</div>

<script>
let hrSearchCount=0,hrImportCount=0,lastHRResults=[],revenueChart,pipelineChart,mrrChart,customersChart;

async function checkAuth(){try{const r=await fetch('/api/auth/status');const d=await r.json();if(d.authenticated)showApp(d.user)}catch(e){}}
async function doLogin(){const user=document.getElementById('loginUser').value,pass=document.getElementById('loginPass').value;try{const r=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:user,password:pass})});const d=await r.json();if(d.success){document.getElementById('loginError').classList.remove('show');showApp(d.user)}else{document.getElementById('loginError').classList.add('show')}}catch(e){document.getElementById('loginError').classList.add('show')}}
async function doLogout(){await fetch('/api/auth/logout',{method:'POST'});location.reload()}
function showApp(user){document.getElementById('loginScreen').style.display='none';document.getElementById('app').classList.add('active');if(user){document.getElementById('userName').textContent=user.name||'User';document.getElementById('userAvatar').textContent=(user.name||'U').split(' ').map(n=>n[0]).join('').substring(0,2)}loadAllData()}

document.querySelectorAll('.nav-item[data-page]').forEach(item=>{item.addEventListener('click',()=>{const page=item.dataset.page;document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));item.classList.add('active');document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));document.getElementById('page-'+page).classList.add('active');document.getElementById('currentPage').textContent=item.querySelector('.text').textContent})})

async function loadAllData(){await Promise.all([loadDashboard(),loadContacts(),loadLeads(),loadCampaigns(),loadSubscriptions(),loadInvoices(),loadExplorium()])}

async function loadDashboard(){try{const[stats,charts,activities]=await Promise.all([fetch('/api/dashboard/stats').then(r=>r.json()),fetch('/api/dashboard/charts').then(r=>r.json()),fetch('/api/dashboard/activities').then(r=>r.json())]);
document.getElementById('statRevenue').textContent='€'+stats.revenue.toLocaleString('de-DE');
document.getElementById('statRevenueGrowth').innerHTML='↑ '+stats.revenue_growth+'% vs. Vorjahr';
document.getElementById('statLeads').textContent=stats.leads;
document.getElementById('statCustomers').textContent=stats.customers;
document.getElementById('statMRR').textContent='€'+stats.mrr.toLocaleString('de-DE');
document.getElementById('statLTV').textContent='€'+stats.ltv.toLocaleString('de-DE');
document.getElementById('statCAC').textContent='€'+stats.cac.toLocaleString('de-DE');
document.getElementById('statChurn').textContent=stats.churn+'%';
document.getElementById('statNPS').textContent=stats.nps;

if(revenueChart)revenueChart.destroy();
revenueChart=new Chart(document.getElementById('revenueChart'),{type:'line',data:{labels:charts.labels,datasets:[{label:'Umsatz €',data:charts.revenue,borderColor:'#6366f1',backgroundColor:'rgba(99,102,241,0.1)',fill:true,tension:0.4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});

if(pipelineChart)pipelineChart.destroy();
pipelineChart=new Chart(document.getElementById('pipelineChart'),{type:'bar',data:{labels:charts.labels,datasets:[{label:'Leads',data:charts.leads,backgroundColor:'#10b981'}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});

if(mrrChart)mrrChart.destroy();
mrrChart=new Chart(document.getElementById('mrrChart'),{type:'line',data:{labels:charts.labels,datasets:[{label:'MRR €',data:charts.mrr,borderColor:'#8b5cf6',backgroundColor:'rgba(139,92,246,0.1)',fill:true,tension:0.4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});

if(customersChart)customersChart.destroy();
customersChart=new Chart(document.getElementById('customersChart'),{type:'line',data:{labels:charts.labels,datasets:[{label:'Kunden',data:charts.customers,borderColor:'#06b6d4',backgroundColor:'rgba(6,182,212,0.1)',fill:true,tension:0.4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});

const actIcons={call:'📞',email:'📧',meeting:'📅',note:'📝'};
document.getElementById('activitiesList').innerHTML=activities.map(a=>'<div class="activity-item"><div class="activity-icon '+a.type+'">'+(actIcons[a.type]||'📌')+'</div><div class="activity-content"><div class="title">'+esc(a.contact)+'</div><div class="desc">'+esc(a.description)+'</div></div><div class="activity-time">'+a.date+'</div></div>').join('')}catch(e){console.error(e)}}

async function loadContacts(){try{const contacts=await fetch('/api/contacts').then(r=>r.json());document.getElementById('contactCount').textContent=contacts.length;document.getElementById('contactsTable').innerHTML=contacts.map(c=>'<tr><td><strong>'+esc(c.name)+'</strong></td><td>'+esc(c.email)+'</td><td>'+esc(c.company)+'</td><td>'+esc(c.phone)+'</td><td>'+esc(c.source)+'</td><td><span class="badge '+c.status+'">'+c.status+'</span></td></tr>').join('')}catch(e){}}

async function loadLeads(){try{const leads=await fetch('/api/leads').then(r=>r.json());const open=leads.filter(l=>l.stage!=='won'&&l.stage!=='lost');const total=leads.reduce((s,l)=>s+l.value,0);const weighted=leads.reduce((s,l)=>s+(l.value*l.probability/100),0);document.getElementById('pipelineValue').textContent='€'+total.toLocaleString('de-DE');document.getElementById('weightedValue').textContent='€'+Math.round(weighted).toLocaleString('de-DE');document.getElementById('openLeads').textContent=open.length;document.getElementById('avgDeal').textContent='€'+Math.round(total/leads.length).toLocaleString('de-DE');document.getElementById('leadsTable').innerHTML=leads.map(l=>'<tr><td><strong>'+esc(l.name)+'</strong></td><td>'+esc(l.company)+'</td><td>'+esc(l.contact)+'</td><td>€'+l.value.toLocaleString('de-DE')+'</td><td><span class="badge '+l.stage+'">'+l.stage+'</span></td><td>'+l.probability+'%</td></tr>').join('')}catch(e){}}

async function loadCampaigns(){try{const campaigns=await fetch('/api/campaigns').then(r=>r.json());const totalSent=campaigns.reduce((s,c)=>s+c.sent,0);const totalOpened=campaigns.reduce((s,c)=>s+c.opened,0);const totalClicked=campaigns.reduce((s,c)=>s+c.clicked,0);const totalConverted=campaigns.reduce((s,c)=>s+c.converted,0);document.getElementById('totalSent').textContent=totalSent.toLocaleString('de-DE');document.getElementById('openRate').textContent=totalSent?Math.round(totalOpened/totalSent*100)+'%':'0%';document.getElementById('clickRate').textContent=totalOpened?Math.round(totalClicked/totalOpened*100)+'%':'0%';document.getElementById('conversions').textContent=totalConverted;document.getElementById('campaignsTable').innerHTML=campaigns.map(c=>'<tr><td><strong>'+esc(c.name)+'</strong></td><td>'+c.sent.toLocaleString('de-DE')+'</td><td>'+c.opened.toLocaleString('de-DE')+'</td><td>'+c.clicked.toLocaleString('de-DE')+'</td><td>'+c.converted+'</td><td><span class="badge '+c.status+'">'+c.status+'</span></td></tr>').join('')}catch(e){}}

async function loadSubscriptions(){try{const[subs,billing]=await Promise.all([fetch('/api/subscriptions').then(r=>r.json()),fetch('/api/billing/stats').then(r=>r.json())]);document.getElementById('subMRR').textContent='€'+billing.mrr.toLocaleString('de-DE');document.getElementById('subActive').textContent=billing.active_subscriptions;document.getElementById('subPending').textContent=billing.pending_invoices;document.getElementById('subPendingAmount').textContent='€'+billing.pending_amount.toLocaleString('de-DE');document.getElementById('subscriptionsTable').innerHTML=subs.map(s=>'<tr><td><strong>'+esc(s.customer)+'</strong></td><td>'+esc(s.email)+'</td><td>'+s.plan+'</td><td>€'+s.price+'/mo</td><td>'+(s.next_billing||'-')+'</td><td><span class="badge '+s.status+'">'+s.status+'</span></td></tr>').join('')}catch(e){}}

async function loadInvoices(){try{const invoices=await fetch('/api/invoices').then(r=>r.json());document.getElementById('invoicesTable').innerHTML=invoices.map(i=>'<tr><td><strong>'+i.id+'</strong></td><td>'+esc(i.customer)+'</td><td>'+esc(i.items)+'</td><td>€'+i.amount.toLocaleString('de-DE')+'</td><td>'+i.due+'</td><td><span class="badge '+i.status+'">'+i.status+'</span></td></tr>').join('')}catch(e){}}

async function loadExplorium(){try{const data=await fetch('/api/explorium/stats').then(r=>r.json());document.getElementById('expCredits').textContent=data.credits.toLocaleString('de-DE');document.getElementById('expEnrichments').textContent=data.enrichments;document.getElementById('expSearches').textContent=data.searches;document.getElementById('expExports').textContent=data.exports}catch(e){}}

async function searchHR(){const q=document.getElementById('hrQuery').value.trim();if(!q)return alert('Bitte Suchbegriff eingeben');document.getElementById('hrResults').innerHTML='<div class="empty-state"><div class="icon">⏳</div><p>Suche im Handelsregister...</p></div>';try{const r=await fetch('/api/hr/search?q='+encodeURIComponent(q));const data=await r.json();hrSearchCount++;document.getElementById('hrSearches').textContent=hrSearchCount;document.getElementById('hrResultCount').textContent=(data.results?.length||0)+' Treffer';const hrb=data.results?.filter(r=>r.register_type==='HRB').length||0;const hra=data.results?.filter(r=>r.register_type==='HRA').length||0;document.getElementById('hrHRB').textContent=hrb;document.getElementById('hrHRA').textContent=hra;lastHRResults=data.results||[];if(!data.results?.length){document.getElementById('hrResults').innerHTML='<div class="empty-state"><div class="icon">🔍</div><p>Keine Ergebnisse gefunden</p></div>'}else{document.getElementById('hrResults').innerHTML=data.results.map((r,i)=>'<div class="result-item" onclick="showHRDetails('+i+')"><div class="result-header"><span class="result-name">'+esc(r.name)+'</span><div>'+(r.register_type?'<span class="badge '+r.register_type.toLowerCase()+'">'+r.register_type+'</span>':'')+' <span class="badge '+r.status+'">'+r.status+'</span></div></div><div class="result-meta"><div><span>Register</span><strong>'+(esc(r.register_number)||'-')+'</strong></div><div><span>Sitz</span><strong>'+(esc(r.city)||'-')+'</strong></div><div><span>Rechtsform</span><strong>'+(esc(r.type)||'-')+'</strong></div><div><span>Gründung</span><strong>'+(r.founded||'-')+'</strong></div></div></div>').join('')}}catch(e){document.getElementById('hrResults').innerHTML='<div class="empty-state"><div class="icon">❌</div><p>Fehler: '+e.message+'</p></div>'}}

async function showHRDetails(idx){const r=lastHRResults[idx];if(!r)return;document.getElementById('modalTitle').textContent=r.name;document.getElementById('modalBody').innerHTML='<div class="empty-state"><p>Lade Details...</p></div>';document.getElementById('modalFooter').innerHTML='<button class="btn btn-success" onclick="importHR('+idx+')">📥 In CRM importieren</button><button class="btn btn-secondary" onclick="closeModal()">Schließen</button>';document.getElementById('modal').classList.add('active');try{const data=await fetch('/api/hr/company/'+encodeURIComponent(r.id)).then(res=>res.json());document.getElementById('modalBody').innerHTML='<div class="detail-section"><h4>📋 Registerdaten</h4><p><strong>Register:</strong> '+(r.register_type||'-')+' '+(data.id||'')+'</p><p><strong>Status:</strong> <span class="badge '+data.status+'">'+data.status+'</span></p><p><strong>Gründung:</strong> '+(data.founded||'-')+'</p></div><div class="detail-section"><h4>🏢 Unternehmen</h4><p><strong>Rechtsform:</strong> '+(data.type||'-')+'</p><p><strong>Adresse:</strong> '+(data.address||'-')+'</p></div>'+(data.officers?.length?'<div class="detail-section"><h4>👥 Vertretungsberechtigte ('+data.officers.length+')</h4>'+data.officers.slice(0,8).map(o=>'<p><strong>'+esc(o.name)+'</strong> - '+esc(o.position)+'</p>').join('')+'</div>':'')}catch(e){document.getElementById('modalBody').innerHTML='<div class="empty-state"><p>Fehler beim Laden der Details</p></div>'}}

async function importHR(idx){const r=lastHRResults[idx];if(!r)return;try{await fetch('/api/hr/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(r)});hrImportCount++;document.getElementById('hrImported').textContent=hrImportCount;closeModal();loadContacts();alert('✅ '+r.name+' wurde in CRM importiert!')}catch(e){alert('Fehler beim Import')}}

function showModal(type){if(type==='newContact'){document.getElementById('modalTitle').textContent='Neuer Kontakt';document.getElementById('modalBody').innerHTML='<div class="form-group"><label>Name *</label><input type="text" class="form-input" id="ncName"></div><div class="form-group"><label>E-Mail *</label><input type="email" class="form-input" id="ncEmail"></div><div class="form-group"><label>Unternehmen</label><input type="text" class="form-input" id="ncCompany"></div><div class="form-group"><label>Telefon</label><input type="text" class="form-input" id="ncPhone"></div>';document.getElementById('modalFooter').innerHTML='<button class="btn btn-primary" onclick="saveContact()">Speichern</button><button class="btn btn-secondary" onclick="closeModal()">Abbrechen</button>'}else if(type==='newLead'){document.getElementById('modalTitle').textContent='Neuer Lead';document.getElementById('modalBody').innerHTML='<div class="form-group"><label>Projektname *</label><input type="text" class="form-input" id="nlName"></div><div class="form-group"><label>Unternehmen *</label><input type="text" class="form-input" id="nlCompany"></div><div class="form-group"><label>Kontaktperson</label><input type="text" class="form-input" id="nlContact"></div><div class="form-group"><label>Wert (€)</label><input type="number" class="form-input" id="nlValue" value="10000"></div>';document.getElementById('modalFooter').innerHTML='<button class="btn btn-primary" onclick="saveLead()">Speichern</button><button class="btn btn-secondary" onclick="closeModal()">Abbrechen</button>'}document.getElementById('modal').classList.add('active')}

function closeModal(){document.getElementById('modal').classList.remove('active')}
async function saveContact(){const data={name:document.getElementById('ncName').value,email:document.getElementById('ncEmail').value,company:document.getElementById('ncCompany').value,phone:document.getElementById('ncPhone').value};if(!data.name||!data.email)return alert('Name und E-Mail sind Pflichtfelder');await fetch('/api/contacts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});closeModal();loadContacts()}
async function saveLead(){const data={name:document.getElementById('nlName').value,company:document.getElementById('nlCompany').value,contact:document.getElementById('nlContact').value,value:parseInt(document.getElementById('nlValue').value)||0};if(!data.name||!data.company)return alert('Projektname und Unternehmen sind Pflichtfelder');await fetch('/api/leads',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});closeModal();loadLeads()}

function esc(s){return s?String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'):''}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});
checkAuth();
</script>
</body>
</html>'''

if __name__ == '__main__':
    print("=" * 60)
    print("  ⚡ WEST MONEY OS v5.0 - MEGA FINAL EDITION")
    print("=" * 60)
    print(f"  🌐 Server: http://localhost:{PORT}")
    print(f"  🔑 Login: admin / 663724")
    print("=" * 60)
    app.run(host='0.0.0.0', port=PORT, debug=False)
