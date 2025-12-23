#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    WEST MONEY OS v5.0 - FINAL EDITION                       ║
║══════════════════════════════════════════════════════════════════════════════║
║  Complete Business Platform with:                                            ║
║  • Dashboard & Analytics                                                     ║
║  • CRM (Contacts, Leads, Pipeline)                                          ║
║  • Campaigns & Email Templates                                               ║
║  • Stripe Payments & Subscriptions                                          ║
║  • Explorium B2B Data Integration                                           ║
║  • Handelsregister LIVE Data                                                ║
║  • Authentication System                                                     ║
║                                                                              ║
║  © 2025 Enterprise Universe GmbH - Ömer Hüseyin Coşkun                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Flask, jsonify, request, render_template_string, redirect, session
from flask_cors import CORS
from functools import wraps
import requests
import json
import os
from datetime import datetime, timedelta
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

# =============================================================================
# CONFIGURATION
# =============================================================================

PORT = int(os.getenv('PORT', 5000))

# API Keys
EXPLORIUM_API_KEY = os.getenv('EXPLORIUM_API_KEY', '1121ab737ecf41edaea2570899a8f90b')
OPENCORPORATES_API_KEY = os.getenv('OPENCORPORATES_API_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_51ShUrH2KgRKMdiU0xxxxxx')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', 'pk_test_51ShUrH2KgRKMdiU0xxxxxx')

# Users Database (in production use real DB)
USERS = {
    'admin': {'password': hashlib.sha256('663724'.encode()).hexdigest(), 'name': 'Ömer Coşkun', 'role': 'admin', 'company': 'Enterprise Universe GmbH'},
    'demo': {'password': hashlib.sha256('demo'.encode()).hexdigest(), 'name': 'Demo User', 'role': 'user', 'company': 'Demo GmbH'}
}

# In-Memory Data Store
DATA = {
    'contacts': [
        {'id': 1, 'name': 'Max Mustermann', 'email': 'max@example.de', 'company': 'Tech GmbH', 'phone': '+49 221 12345', 'status': 'active', 'source': 'Website', 'created': '2025-12-01'},
        {'id': 2, 'name': 'Anna Schmidt', 'email': 'anna@startup.de', 'company': 'StartUp AG', 'phone': '+49 89 98765', 'status': 'active', 'source': 'Handelsregister', 'created': '2025-12-05'},
        {'id': 3, 'name': 'Thomas Weber', 'email': 'weber@industrie.de', 'company': 'Industrie KG', 'phone': '+49 211 55555', 'status': 'lead', 'source': 'Explorium', 'created': '2025-12-10'},
    ],
    'leads': [
        {'id': 1, 'name': 'Software Projekt', 'company': 'Digital GmbH', 'value': 25000, 'stage': 'qualified', 'probability': 60, 'contact': 'Klaus Digital'},
        {'id': 2, 'name': 'Beratungsauftrag', 'company': 'Consulting AG', 'value': 15000, 'stage': 'proposal', 'probability': 80, 'contact': 'Maria Berater'},
        {'id': 3, 'name': 'Enterprise License', 'company': 'Big Corp', 'value': 75000, 'stage': 'negotiation', 'probability': 40, 'contact': 'Peter Enterprise'},
    ],
    'campaigns': [
        {'id': 1, 'name': 'Q1 Newsletter', 'type': 'email', 'status': 'active', 'sent': 1250, 'opened': 487, 'clicked': 156},
        {'id': 2, 'name': 'Product Launch', 'type': 'email', 'status': 'completed', 'sent': 3500, 'opened': 1820, 'clicked': 643},
    ],
    'subscriptions': [
        {'id': 1, 'customer': 'Tech GmbH', 'plan': 'Professional', 'amount': 99, 'status': 'active', 'next_billing': '2026-01-15'},
        {'id': 2, 'customer': 'StartUp AG', 'plan': 'Enterprise', 'amount': 299, 'status': 'active', 'next_billing': '2026-01-20'},
    ],
    'invoices': [
        {'id': 'INV-001', 'customer': 'Tech GmbH', 'amount': 2500, 'status': 'paid', 'date': '2025-12-01'},
        {'id': 'INV-002', 'customer': 'StartUp AG', 'amount': 5000, 'status': 'pending', 'date': '2025-12-15'},
    ],
    'stats': {
        'revenue': 125000,
        'leads': 47,
        'customers': 23,
        'mrr': 4850,
        'growth': 23.5
    }
}

# =============================================================================
# AUTHENTICATION
# =============================================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            if request.is_json:
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if username in USERS and USERS[username]['password'] == password_hash:
        session['user'] = username
        session['name'] = USERS[username]['name']
        session['role'] = USERS[username]['role']
        return jsonify({'success': True, 'user': USERS[username]['name']})
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/status')
def api_auth_status():
    if 'user' in session:
        return jsonify({'authenticated': True, 'user': session.get('name'), 'role': session.get('role')})
    return jsonify({'authenticated': False})

# =============================================================================
# DASHBOARD API
# =============================================================================

@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    return jsonify({
        'revenue': DATA['stats']['revenue'],
        'leads': DATA['stats']['leads'],
        'customers': DATA['stats']['customers'],
        'mrr': DATA['stats']['mrr'],
        'growth': DATA['stats']['growth'],
        'contacts': len(DATA['contacts']),
        'campaigns': len(DATA['campaigns']),
        'subscriptions': len(DATA['subscriptions'])
    })

@app.route('/api/dashboard/chart')
def api_dashboard_chart():
    return jsonify({
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
        'revenue': [12000, 15000, 18000, 22000, 19000, 25000, 28000, 32000, 35000, 38000, 42000, 45000],
        'leads': [15, 22, 18, 25, 30, 28, 35, 40, 38, 45, 50, 47]
    })

# =============================================================================
# CONTACTS API
# =============================================================================

@app.route('/api/contacts')
def api_contacts():
    return jsonify(DATA['contacts'])

@app.route('/api/contacts', methods=['POST'])
def api_contacts_create():
    data = request.json
    new_id = max([c['id'] for c in DATA['contacts']], default=0) + 1
    contact = {
        'id': new_id,
        'name': data.get('name', ''),
        'email': data.get('email', ''),
        'company': data.get('company', ''),
        'phone': data.get('phone', ''),
        'status': data.get('status', 'lead'),
        'source': data.get('source', 'Manual'),
        'created': datetime.now().strftime('%Y-%m-%d')
    }
    DATA['contacts'].append(contact)
    return jsonify(contact)

@app.route('/api/contacts/<int:id>', methods=['DELETE'])
def api_contacts_delete(id):
    DATA['contacts'] = [c for c in DATA['contacts'] if c['id'] != id]
    return jsonify({'success': True})

# =============================================================================
# LEADS API
# =============================================================================

@app.route('/api/leads')
def api_leads():
    return jsonify(DATA['leads'])

@app.route('/api/leads', methods=['POST'])
def api_leads_create():
    data = request.json
    new_id = max([l['id'] for l in DATA['leads']], default=0) + 1
    lead = {
        'id': new_id,
        'name': data.get('name', ''),
        'company': data.get('company', ''),
        'value': data.get('value', 0),
        'stage': data.get('stage', 'new'),
        'probability': data.get('probability', 10),
        'contact': data.get('contact', '')
    }
    DATA['leads'].append(lead)
    DATA['stats']['leads'] += 1
    return jsonify(lead)

# =============================================================================
# CAMPAIGNS API
# =============================================================================

@app.route('/api/campaigns')
def api_campaigns():
    return jsonify(DATA['campaigns'])

@app.route('/api/campaigns', methods=['POST'])
def api_campaigns_create():
    data = request.json
    new_id = max([c['id'] for c in DATA['campaigns']], default=0) + 1
    campaign = {
        'id': new_id,
        'name': data.get('name', ''),
        'type': data.get('type', 'email'),
        'status': 'draft',
        'sent': 0, 'opened': 0, 'clicked': 0
    }
    DATA['campaigns'].append(campaign)
    return jsonify(campaign)

# =============================================================================
# SUBSCRIPTIONS & PAYMENTS API
# =============================================================================

@app.route('/api/subscriptions')
def api_subscriptions():
    return jsonify(DATA['subscriptions'])

@app.route('/api/invoices')
def api_invoices():
    return jsonify(DATA['invoices'])

@app.route('/api/stripe/plans')
def api_stripe_plans():
    return jsonify([
        {'id': 'starter', 'name': 'Starter', 'price': 29, 'features': ['5 Users', '1.000 Contacts', 'Email Support']},
        {'id': 'professional', 'name': 'Professional', 'price': 99, 'features': ['25 Users', '10.000 Contacts', 'Priority Support', 'API Access']},
        {'id': 'enterprise', 'name': 'Enterprise', 'price': 299, 'features': ['Unlimited Users', 'Unlimited Contacts', '24/7 Support', 'Custom Integration', 'Dedicated Manager']}
    ])

# =============================================================================
# HANDELSREGISTER API - LIVE DATA
# =============================================================================

@app.route('/api/hr/search')
def hr_search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Suchbegriff fehlt', 'results': [], 'total': 0})
    
    try:
        url = 'https://api.opencorporates.com/v0.4/companies/search'
        params = {'q': query, 'jurisdiction_code': 'de', 'per_page': 30, 'order': 'score'}
        if OPENCORPORATES_API_KEY:
            params['api_token'] = OPENCORPORATES_API_KEY
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for item in data.get('results', {}).get('companies', []):
            c = item.get('company', {})
            addr = c.get('registered_address', {}) or {}
            reg_type = ''
            cn = (c.get('company_number') or '').upper()
            for rt in ['HRB', 'HRA', 'GNR', 'PR', 'VR']:
                if rt in cn:
                    reg_type = rt
                    break
            results.append({
                'id': c.get('company_number', ''),
                'name': c.get('name', ''),
                'registerArt': reg_type,
                'registerNummer': c.get('company_number', ''),
                'sitz': addr.get('locality', '') or addr.get('region', '') or '',
                'rechtsform': c.get('company_type', ''),
                'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv',
                'gruendung': c.get('incorporation_date', ''),
                'adresse': ', '.join(filter(None, [addr.get('street_address', ''), addr.get('postal_code', ''), addr.get('locality', '')])),
                'url': c.get('opencorporates_url', '')
            })
        
        return jsonify({
            'success': True, 'query': query,
            'total': data.get('results', {}).get('total_count', 0),
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e), 'results': [], 'total': 0})

@app.route('/api/hr/company/<path:company_id>')
def hr_company_details(company_id):
    try:
        url = f'https://api.opencorporates.com/v0.4/companies/de/{company_id}'
        params = {}
        if OPENCORPORATES_API_KEY:
            params['api_token'] = OPENCORPORATES_API_KEY
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        c = data.get('results', {}).get('company', {})
        addr = c.get('registered_address', {}) or {}
        
        officers = []
        for o in c.get('officers', []):
            off = o.get('officer', {})
            officers.append({
                'name': off.get('name', ''),
                'position': off.get('position', ''),
                'start_date': off.get('start_date', ''),
                'end_date': off.get('end_date', '')
            })
        
        return jsonify({
            'success': True,
            'id': c.get('company_number', ''),
            'name': c.get('name', ''),
            'rechtsform': c.get('company_type', ''),
            'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv',
            'gruendung': c.get('incorporation_date', ''),
            'adresse': ', '.join(filter(None, [addr.get('street_address', ''), addr.get('postal_code', ''), addr.get('locality', '')])),
            'officers': officers,
            'filings_count': len(c.get('filings', [])),
            'url': c.get('opencorporates_url', ''),
            'registry_url': c.get('registry_url', '')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/hr/officers/search')
def hr_officers_search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Suchbegriff fehlt', 'results': [], 'total': 0})
    
    try:
        url = 'https://api.opencorporates.com/v0.4/officers/search'
        params = {'q': query, 'jurisdiction_code': 'de'}
        if OPENCORPORATES_API_KEY:
            params['api_token'] = OPENCORPORATES_API_KEY
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for item in data.get('results', {}).get('officers', []):
            o = item.get('officer', {})
            comp = o.get('company', {})
            results.append({
                'name': o.get('name', ''),
                'position': o.get('position', ''),
                'company_name': comp.get('name', ''),
                'company_number': comp.get('company_number', ''),
                'start_date': o.get('start_date', ''),
                'end_date': o.get('end_date', ''),
                'url': o.get('opencorporates_url', '')
            })
        
        return jsonify({
            'success': True, 'query': query,
            'total': data.get('results', {}).get('total_count', 0),
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e), 'results': [], 'total': 0})

@app.route('/api/hr/import', methods=['POST'])
def hr_import_to_crm():
    data = request.json
    new_id = max([c['id'] for c in DATA['contacts']], default=0) + 1
    contact = {
        'id': new_id,
        'name': data.get('name', ''),
        'email': '',
        'company': data.get('name', ''),
        'phone': '',
        'status': 'lead',
        'source': 'Handelsregister',
        'created': datetime.now().strftime('%Y-%m-%d'),
        'hr_verified': True,
        'hr_data': data
    }
    DATA['contacts'].append(contact)
    return jsonify({'success': True, 'contact': contact})

# =============================================================================
# EXPLORIUM API
# =============================================================================

@app.route('/api/explorium/search', methods=['POST'])
def explorium_search():
    data = request.json
    # Simulated response - in production connect to real Explorium API
    return jsonify({
        'success': True,
        'credits_used': 10,
        'credits_remaining': 4863,
        'results': [
            {'company': 'Tech Solutions GmbH', 'industry': 'Software', 'employees': 50, 'revenue': '5M-10M'},
            {'company': 'Digital Services AG', 'industry': 'IT Services', 'employees': 120, 'revenue': '10M-25M'},
        ]
    })

@app.route('/api/explorium/credits')
def explorium_credits():
    return jsonify({'credits': 4873, 'plan': 'Professional'})

# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'West Money OS v5.0 Final Edition',
        'timestamp': datetime.now().isoformat()
    })

# =============================================================================
# MAIN FRONTEND
# =============================================================================

@app.route('/')
@app.route('/login')
@app.route('/dashboard')
@app.route('/contacts')
@app.route('/leads')
@app.route('/pipeline')
@app.route('/campaigns')
@app.route('/handelsregister')
@app.route('/explorium')
@app.route('/subscriptions')
@app.route('/invoices')
@app.route('/settings')
def index():
    return render_template_string(FRONTEND_HTML)

# =============================================================================
# COMPLETE FRONTEND HTML/CSS/JS
# =============================================================================

FRONTEND_HTML = r'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>West Money OS | Enterprise Business Platform</title>
    <meta name="description" content="West Money OS - All-in-One Business Platform mit CRM, Handelsregister & Stripe">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
:root{--bg:#09090b;--bg2:#111113;--bg3:#18181b;--bg4:#27272a;--text:#fafafa;--text2:#a1a1aa;--text3:#71717a;--primary:#6366f1;--primary-hover:#818cf8;--emerald:#10b981;--amber:#f59e0b;--rose:#f43f5e;--cyan:#06b6d4;--violet:#8b5cf6;--stripe:#635bff;--hr:#1e3a8a;--border:rgba(255,255,255,0.08);--radius:8px;--radius-lg:12px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;font-size:14px;line-height:1.6}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:var(--bg2)}::-webkit-scrollbar-thumb{background:var(--bg4);border-radius:3px}

/* Login */
.login-screen{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,var(--bg) 0%,#0f0f1a 50%,#1a0a2e 100%)}
.login-container{width:100%;max-width:400px;padding:20px}
.login-logo{text-align:center;margin-bottom:32px}
.login-logo-icon{width:80px;height:80px;background:linear-gradient(135deg,var(--primary),var(--violet));border-radius:20px;display:inline-flex;align-items:center;justify-content:center;font-size:36px;margin-bottom:16px;box-shadow:0 8px 32px rgba(99,102,241,0.4)}
.login-logo h1{font-size:28px;font-weight:700}
.login-logo p{color:var(--text3);margin-top:4px}
.login-box{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-lg);padding:32px}
.login-box h2{font-size:20px;margin-bottom:24px;text-align:center}
.form-group{margin-bottom:20px}
.form-group label{display:block;font-size:13px;font-weight:500;margin-bottom:8px}
.form-input{width:100%;padding:12px 14px;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);color:var(--text);font-size:14px}
.form-input:focus{outline:none;border-color:var(--primary)}
.login-btn{width:100%;padding:14px;background:linear-gradient(135deg,var(--primary),var(--violet));color:white;border:none;border-radius:var(--radius);font-size:14px;font-weight:600;cursor:pointer}
.login-btn:hover{opacity:0.9}
.login-error{background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);color:#ef4444;padding:12px;border-radius:var(--radius);margin-bottom:20px;text-align:center;display:none}
.login-error.show{display:block}

/* App Layout */
.app{display:none;min-height:100vh}
.app.active{display:flex}
.sidebar{width:260px;background:var(--bg2);border-right:1px solid var(--border);position:fixed;height:100vh;display:flex;flex-direction:column;z-index:100}
.sidebar-header{padding:16px;border-bottom:1px solid var(--border)}
.logo{display:flex;align-items:center;gap:10px}
.logo-icon{width:40px;height:40px;background:linear-gradient(135deg,var(--primary),var(--violet));border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px}
.logo h1{font-size:16px;font-weight:600}
.logo span{font-size:10px;color:var(--text3);display:block}
.sidebar-nav{flex:1;padding:8px;overflow-y:auto}
.nav-group{margin-bottom:8px}
.nav-label{font-size:10px;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:0.5px;padding:12px 12px 6px}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:var(--radius);cursor:pointer;color:var(--text2);font-size:13px;transition:all 0.15s;margin-bottom:2px}
.nav-item:hover{background:var(--bg3);color:var(--text)}
.nav-item.active{background:rgba(99,102,241,0.15);color:var(--primary-hover);border:1px solid rgba(99,102,241,0.3)}
.nav-item .icon{width:20px;text-align:center}
.nav-item .label{flex:1}
.nav-item .badge{background:var(--primary);color:white;font-size:10px;padding:2px 6px;border-radius:4px}
.nav-item .badge.new{background:var(--emerald)}
.nav-item .badge.hr{background:var(--hr)}
.nav-item .badge.stripe{background:var(--stripe)}
.sidebar-footer{padding:12px;border-top:1px solid var(--border)}
.user-box{display:flex;align-items:center;gap:10px;padding:10px;background:var(--bg3);border-radius:var(--radius)}
.user-avatar{width:36px;height:36px;border-radius:8px;background:linear-gradient(135deg,var(--emerald),var(--cyan));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
.user-info{flex:1}
.user-info div{font-size:13px;font-weight:500}
.user-info span{color:var(--text3);font-size:11px}
.logout-btn{background:none;border:none;color:var(--text3);cursor:pointer;padding:8px;font-size:14px}
.logout-btn:hover{color:var(--rose)}

/* Main Content */
.main{flex:1;margin-left:260px;display:flex;flex-direction:column;min-height:100vh}
.topbar{height:60px;background:var(--bg2);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 24px;position:sticky;top:0;z-index:50}
.topbar-left{display:flex;align-items:center;gap:16px}
.breadcrumb{font-size:13px;color:var(--text2)}
.breadcrumb strong{color:var(--text)}
.topbar-right{display:flex;align-items:center;gap:10px}
.api-status{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:600;background:rgba(16,185,129,0.15);color:var(--emerald)}
.api-status .dot{width:8px;height:8px;border-radius:50%;background:var(--emerald);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
.content{padding:24px;flex:1}
.page{display:none}
.page.active{display:block;animation:fadeIn 0.3s}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.page-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px;flex-wrap:wrap;gap:16px}
.page-header h1{font-size:26px;font-weight:700;display:flex;align-items:center;gap:12px}
.page-header p{color:var(--text2);font-size:13px;margin-top:4px}

/* Cards & Stats */
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.stat-card{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-lg);padding:20px}
.stat-card.primary{border-left:3px solid var(--primary)}
.stat-card.emerald{border-left:3px solid var(--emerald)}
.stat-card.amber{border-left:3px solid var(--amber)}
.stat-card.rose{border-left:3px solid var(--rose)}
.stat-card.hr{border-left:3px solid var(--hr)}
.stat-card .label{font-size:12px;color:var(--text3);margin-bottom:4px}
.stat-card .value{font-size:28px;font-weight:700}
.stat-card .change{font-size:12px;margin-top:4px}
.stat-card .change.up{color:var(--emerald)}
.stat-card .change.down{color:var(--rose)}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden}
.card-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.card-header h3{font-size:15px;font-weight:600}
.card-body{padding:20px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:20px}

/* Buttons */
.btn{display:inline-flex;align-items:center;gap:6px;padding:10px 16px;border-radius:var(--radius);font-size:13px;font-weight:500;cursor:pointer;border:none;transition:all 0.15s}
.btn-primary{background:var(--primary);color:white}
.btn-primary:hover{background:var(--primary-hover)}
.btn-secondary{background:var(--bg3);color:var(--text);border:1px solid var(--border)}
.btn-secondary:hover{border-color:var(--primary)}
.btn-success{background:var(--emerald);color:white}
.btn-hr{background:var(--hr);color:white}
.btn-stripe{background:var(--stripe);color:white}

/* Tables */
.table-container{overflow-x:auto}
table{width:100%;border-collapse:collapse}
th,td{text-align:left;padding:12px 16px;border-bottom:1px solid var(--border)}
th{font-size:11px;font-weight:600;color:var(--text3);text-transform:uppercase;background:var(--bg3)}
tr:hover{background:var(--bg3)}
.badge{display:inline-flex;align-items:center;padding:4px 10px;border-radius:6px;font-size:11px;font-weight:600}
.badge.active,.badge.paid,.badge.aktiv{background:rgba(16,185,129,0.15);color:var(--emerald)}
.badge.pending,.badge.lead{background:rgba(245,158,11,0.15);color:var(--amber)}
.badge.inactive,.badge.inaktiv{background:rgba(244,63,94,0.15);color:var(--rose)}
.badge.hrb{background:rgba(99,102,241,0.15);color:var(--primary)}
.badge.hra{background:rgba(16,185,129,0.15);color:var(--emerald)}

/* Search */
.search-box{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius-lg);padding:20px;margin-bottom:24px}
.search-row{display:flex;gap:12px}
.search-input{flex:1;padding:12px 16px;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);color:var(--text);font-size:14px}
.search-input:focus{outline:none;border-color:var(--primary)}

/* Modal */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.8);display:none;align-items:center;justify-content:center;z-index:1000;padding:20px}
.modal-overlay.active{display:flex}
.modal{background:var(--bg2);border:1px solid var(--border);border-radius:16px;width:100%;max-width:600px;max-height:90vh;overflow:hidden}
.modal-header{padding:20px 24px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.modal-header h2{font-size:18px}
.modal-close{background:none;border:none;color:var(--text2);font-size:24px;cursor:pointer}
.modal-body{padding:24px;overflow-y:auto;max-height:60vh}
.modal-footer{padding:16px 24px;border-top:1px solid var(--border);display:flex;justify-content:flex-end;gap:12px}

/* Results */
.result-item{padding:16px;border-bottom:1px solid var(--border);cursor:pointer;transition:background 0.2s}
.result-item:hover{background:var(--bg3)}
.result-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.result-name{font-weight:600;font-size:15px}
.result-meta{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;font-size:12px;color:var(--text2)}
.result-meta strong{color:var(--text);display:block}

/* Responsive */
@media(max-width:1200px){.stats-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:900px){.sidebar{transform:translateX(-100%)}.main{margin-left:0}.grid-2{grid-template-columns:1fr}}
@media(max-width:600px){.stats-grid{grid-template-columns:1fr}.search-row{flex-direction:column}.result-meta{grid-template-columns:1fr}}
    </style>
</head>
<body>
<!-- LOGIN SCREEN -->
<div class="login-screen" id="loginScreen">
    <div class="login-container">
        <div class="login-logo">
            <div class="login-logo-icon">⚡</div>
            <h1>West Money OS</h1>
            <p>Enterprise Business Platform</p>
        </div>
        <div class="login-box">
            <h2>Anmelden</h2>
            <div class="login-error" id="loginError">Ungültige Anmeldedaten</div>
            <div class="form-group">
                <label>Benutzername</label>
                <input type="text" class="form-input" id="loginUser" placeholder="admin" value="admin">
            </div>
            <div class="form-group">
                <label>Passwort</label>
                <input type="password" class="form-input" id="loginPass" placeholder="••••••">
            </div>
            <button class="login-btn" onclick="doLogin()">Anmelden</button>
        </div>
    </div>
</div>

<!-- APP -->
<div class="app" id="app">
    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="sidebar-header">
            <div class="logo">
                <div class="logo-icon">⚡</div>
                <div><h1>West Money OS</h1><span>v5.0 Final Edition</span></div>
            </div>
        </div>
        <nav class="sidebar-nav">
            <div class="nav-group">
                <div class="nav-label">Übersicht</div>
                <div class="nav-item active" data-page="dashboard"><span class="icon">📊</span><span class="label">Dashboard</span></div>
                <div class="nav-item" data-page="analytics"><span class="icon">📈</span><span class="label">Analytics</span></div>
            </div>
            <div class="nav-group">
                <div class="nav-label">CRM</div>
                <div class="nav-item" data-page="contacts"><span class="icon">👥</span><span class="label">Kontakte</span><span class="badge">3</span></div>
                <div class="nav-item" data-page="leads"><span class="icon">🎯</span><span class="label">Leads</span><span class="badge new">3</span></div>
                <div class="nav-item" data-page="pipeline"><span class="icon">📋</span><span class="label">Pipeline</span></div>
            </div>
            <div class="nav-group">
                <div class="nav-label">Marketing</div>
                <div class="nav-item" data-page="campaigns"><span class="icon">📧</span><span class="label">Kampagnen</span></div>
                <div class="nav-item" data-page="templates"><span class="icon">📝</span><span class="label">Templates</span></div>
            </div>
            <div class="nav-group">
                <div class="nav-label">Daten APIs</div>
                <div class="nav-item" data-page="handelsregister"><span class="icon">🏛️</span><span class="label">Handelsregister</span><span class="badge hr">LIVE</span></div>
                <div class="nav-item" data-page="explorium"><span class="icon">🔍</span><span class="label">Explorium</span><span class="badge">API</span></div>
            </div>
            <div class="nav-group">
                <div class="nav-label">Finanzen</div>
                <div class="nav-item" data-page="subscriptions"><span class="icon">💳</span><span class="label">Abonnements</span><span class="badge stripe">Stripe</span></div>
                <div class="nav-item" data-page="invoices"><span class="icon">📄</span><span class="label">Rechnungen</span></div>
            </div>
            <div class="nav-group">
                <div class="nav-label">System</div>
                <div class="nav-item" data-page="settings"><span class="icon">⚙️</span><span class="label">Einstellungen</span></div>
            </div>
        </nav>
        <div class="sidebar-footer">
            <div class="user-box">
                <div class="user-avatar" id="userAvatar">ÖC</div>
                <div class="user-info">
                    <div id="userName">Ömer Coşkun</div>
                    <span>Administrator</span>
                </div>
                <button class="logout-btn" onclick="doLogout()">🚪</button>
            </div>
        </div>
    </aside>

    <!-- Main -->
    <main class="main">
        <header class="topbar">
            <div class="topbar-left">
                <div class="breadcrumb">West Money OS / <strong id="currentPage">Dashboard</strong></div>
            </div>
            <div class="topbar-right">
                <div class="api-status"><span class="dot"></span>APIs Online</div>
            </div>
        </header>
        <div class="content">
            <!-- Dashboard -->
            <div class="page active" id="page-dashboard">
                <div class="page-header">
                    <div><h1>📊 Dashboard</h1><p>Willkommen bei West Money OS</p></div>
                </div>
                <div class="stats-grid">
                    <div class="stat-card primary"><div class="label">Umsatz</div><div class="value" id="statRevenue">€0</div><div class="change up">+23.5% vs. Vormonat</div></div>
                    <div class="stat-card emerald"><div class="label">Leads</div><div class="value" id="statLeads">0</div><div class="change up">+12 diese Woche</div></div>
                    <div class="stat-card amber"><div class="label">Kunden</div><div class="value" id="statCustomers">0</div><div class="change up">+3 neu</div></div>
                    <div class="stat-card rose"><div class="label">MRR</div><div class="value" id="statMRR">€0</div><div class="change up">+8.2%</div></div>
                </div>
                <div class="grid-2">
                    <div class="card"><div class="card-header"><h3>📈 Umsatzentwicklung</h3></div><div class="card-body"><canvas id="revenueChart" height="200"></canvas></div></div>
                    <div class="card"><div class="card-header"><h3>🎯 Lead Pipeline</h3></div><div class="card-body"><canvas id="leadsChart" height="200"></canvas></div></div>
                </div>
            </div>

            <!-- Analytics -->
            <div class="page" id="page-analytics">
                <div class="page-header"><div><h1>📈 Analytics</h1><p>Detaillierte Auswertungen</p></div></div>
                <div class="stats-grid">
                    <div class="stat-card primary"><div class="label">Kontakte</div><div class="value" id="statContacts2">0</div></div>
                    <div class="stat-card emerald"><div class="label">Kampagnen</div><div class="value" id="statCampaigns2">0</div></div>
                    <div class="stat-card amber"><div class="label">Öffnungsrate</div><div class="value">52%</div></div>
                    <div class="stat-card hr"><div class="label">HR Verifiziert</div><div class="value">12</div></div>
                </div>
            </div>

            <!-- Contacts -->
            <div class="page" id="page-contacts">
                <div class="page-header">
                    <div><h1>👥 Kontakte</h1><p>Alle deine Kontakte verwalten</p></div>
                    <button class="btn btn-primary" onclick="showModal('newContact')">+ Kontakt</button>
                </div>
                <div class="card">
                    <div class="table-container">
                        <table>
                            <thead><tr><th>Name</th><th>E-Mail</th><th>Firma</th><th>Quelle</th><th>Status</th></tr></thead>
                            <tbody id="contactsTable"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Leads -->
            <div class="page" id="page-leads">
                <div class="page-header">
                    <div><h1>🎯 Leads</h1><p>Deine Verkaufschancen</p></div>
                    <button class="btn btn-primary" onclick="showModal('newLead')">+ Lead</button>
                </div>
                <div class="card">
                    <div class="table-container">
                        <table>
                            <thead><tr><th>Name</th><th>Firma</th><th>Wert</th><th>Phase</th><th>Wahrscheinlichkeit</th></tr></thead>
                            <tbody id="leadsTable"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Pipeline -->
            <div class="page" id="page-pipeline">
                <div class="page-header"><div><h1>📋 Pipeline</h1><p>Visualisierung deiner Sales Pipeline</p></div></div>
                <div class="stats-grid">
                    <div class="stat-card"><div class="label">Qualifiziert</div><div class="value">€25.000</div></div>
                    <div class="stat-card"><div class="label">Angebot</div><div class="value">€15.000</div></div>
                    <div class="stat-card"><div class="label">Verhandlung</div><div class="value">€75.000</div></div>
                    <div class="stat-card emerald"><div class="label">Gewonnen</div><div class="value">€45.000</div></div>
                </div>
            </div>

            <!-- Campaigns -->
            <div class="page" id="page-campaigns">
                <div class="page-header">
                    <div><h1>📧 Kampagnen</h1><p>E-Mail Marketing Kampagnen</p></div>
                    <button class="btn btn-primary">+ Kampagne</button>
                </div>
                <div class="card">
                    <div class="table-container">
                        <table>
                            <thead><tr><th>Name</th><th>Typ</th><th>Gesendet</th><th>Geöffnet</th><th>Geklickt</th><th>Status</th></tr></thead>
                            <tbody id="campaignsTable"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Templates -->
            <div class="page" id="page-templates">
                <div class="page-header"><div><h1>📝 Templates</h1><p>E-Mail Vorlagen</p></div><button class="btn btn-primary">+ Template</button></div>
                <div class="card"><div class="card-body"><p style="color:var(--text2);text-align:center;padding:40px">6 Templates verfügbar</p></div></div>
            </div>

            <!-- Handelsregister -->
            <div class="page" id="page-handelsregister">
                <div class="page-header">
                    <div><h1>🏛️ Handelsregister</h1><p>Echte Firmendaten aus dem deutschen Handelsregister</p></div>
                </div>
                <div class="stats-grid">
                    <div class="stat-card hr"><div class="label">Suchen heute</div><div class="value" id="hrSearches">0</div></div>
                    <div class="stat-card emerald"><div class="label">Importiert</div><div class="value" id="hrImported">0</div></div>
                    <div class="stat-card primary"><div class="label">HRB Einträge</div><div class="value" id="hrHRB">-</div></div>
                    <div class="stat-card amber"><div class="label">HRA Einträge</div><div class="value" id="hrHRA">-</div></div>
                </div>
                <div class="search-box">
                    <div class="search-row">
                        <input type="text" class="search-input" id="hrQuery" placeholder="Firmenname eingeben (z.B. Siemens, BMW, Deutsche Bahn...)" onkeypress="if(event.key==='Enter')searchHR()">
                        <button class="btn btn-hr" onclick="searchHR()">🔍 Suchen</button>
                    </div>
                    <div class="search-row" style="margin-top:12px">
                        <input type="text" class="search-input" id="hrOfficer" placeholder="Person suchen (Geschäftsführer, Vorstand...)" onkeypress="if(event.key==='Enter')searchHROfficers()">
                        <button class="btn btn-secondary" onclick="searchHROfficers()">👤 Personen</button>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><h3>Suchergebnisse</h3><span class="badge" id="hrResultCount">0 Treffer</span></div>
                    <div id="hrResults"><div style="padding:40px;text-align:center;color:var(--text3)">Suche starten um echte Handelsregister-Daten abzurufen</div></div>
                </div>
            </div>

            <!-- Explorium -->
            <div class="page" id="page-explorium">
                <div class="page-header"><div><h1>🔍 Explorium</h1><p>B2B Daten & Lead Enrichment</p></div></div>
                <div class="stats-grid">
                    <div class="stat-card primary"><div class="label">API Credits</div><div class="value">4.873</div></div>
                    <div class="stat-card emerald"><div class="label">Enrichments</div><div class="value">156</div></div>
                    <div class="stat-card amber"><div class="label">Matches</div><div class="value">89%</div></div>
                    <div class="stat-card"><div class="label">Plan</div><div class="value">Pro</div></div>
                </div>
                <div class="card"><div class="card-body"><p style="color:var(--text2)">API Key: 1121ab73...f90b • Status: ✅ Aktiv</p></div></div>
            </div>

            <!-- Subscriptions -->
            <div class="page" id="page-subscriptions">
                <div class="page-header"><div><h1>💳 Abonnements</h1><p>Stripe Subscription Management</p></div></div>
                <div class="stats-grid">
                    <div class="stat-card stripe"><div class="label">Aktive Abos</div><div class="value">2</div></div>
                    <div class="stat-card emerald"><div class="label">MRR</div><div class="value">€398</div></div>
                    <div class="stat-card amber"><div class="label">Churn Rate</div><div class="value">2.1%</div></div>
                    <div class="stat-card"><div class="label">LTV</div><div class="value">€1.850</div></div>
                </div>
                <div class="card">
                    <div class="table-container">
                        <table>
                            <thead><tr><th>Kunde</th><th>Plan</th><th>Betrag</th><th>Nächste Zahlung</th><th>Status</th></tr></thead>
                            <tbody id="subscriptionsTable"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Invoices -->
            <div class="page" id="page-invoices">
                <div class="page-header"><div><h1>📄 Rechnungen</h1><p>Alle Rechnungen</p></div></div>
                <div class="card">
                    <div class="table-container">
                        <table>
                            <thead><tr><th>Nummer</th><th>Kunde</th><th>Betrag</th><th>Datum</th><th>Status</th></tr></thead>
                            <tbody id="invoicesTable"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Settings -->
            <div class="page" id="page-settings">
                <div class="page-header"><div><h1>⚙️ Einstellungen</h1><p>System Konfiguration</p></div></div>
                <div class="grid-2">
                    <div class="card"><div class="card-header"><h3>API Verbindungen</h3></div><div class="card-body">
                        <p>✅ Handelsregister (OpenCorporates)</p>
                        <p>✅ Explorium B2B Data</p>
                        <p>✅ Stripe Payments</p>
                    </div></div>
                    <div class="card"><div class="card-header"><h3>Account</h3></div><div class="card-body">
                        <p><strong>Firma:</strong> Enterprise Universe GmbH</p>
                        <p><strong>Plan:</strong> Enterprise</p>
                        <p><strong>Domain:</strong> west-money.com</p>
                    </div></div>
                </div>
            </div>
        </div>
    </main>
</div>

<!-- Modal -->
<div class="modal-overlay" id="modal">
    <div class="modal">
        <div class="modal-header"><h2 id="modalTitle">Modal</h2><button class="modal-close" onclick="closeModal()">&times;</button></div>
        <div class="modal-body" id="modalBody"></div>
        <div class="modal-footer" id="modalFooter"></div>
    </div>
</div>

<script>
// State
let currentPage = 'dashboard';
let hrSearchCount = 0;
let hrImportCount = 0;
let lastHRResults = [];

// Auth
async function checkAuth() {
    try {
        const resp = await fetch('/api/auth/status');
        const data = await resp.json();
        if (data.authenticated) {
            showApp(data.user);
        }
    } catch (e) {}
}

async function doLogin() {
    const user = document.getElementById('loginUser').value;
    const pass = document.getElementById('loginPass').value;
    
    try {
        const resp = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: user, password: pass})
        });
        const data = await resp.json();
        
        if (data.success) {
            showApp(data.user);
        } else {
            document.getElementById('loginError').classList.add('show');
        }
    } catch (e) {
        document.getElementById('loginError').classList.add('show');
    }
}

async function doLogout() {
    await fetch('/api/auth/logout', {method: 'POST'});
    document.getElementById('loginScreen').style.display = 'flex';
    document.getElementById('app').classList.remove('active');
}

function showApp(userName) {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('app').classList.add('active');
    document.getElementById('userName').textContent = userName || 'User';
    document.getElementById('userAvatar').textContent = (userName || 'U').substring(0,2).toUpperCase();
    loadDashboard();
    loadData();
}

// Navigation
document.querySelectorAll('.nav-item[data-page]').forEach(item => {
    item.addEventListener('click', () => {
        const page = item.dataset.page;
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        item.classList.add('active');
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById('page-' + page).classList.add('active');
        document.getElementById('currentPage').textContent = item.querySelector('.label').textContent;
        currentPage = page;
    });
});

// Dashboard
async function loadDashboard() {
    try {
        const resp = await fetch('/api/dashboard/stats');
        const data = await resp.json();
        document.getElementById('statRevenue').textContent = '€' + data.revenue.toLocaleString();
        document.getElementById('statLeads').textContent = data.leads;
        document.getElementById('statCustomers').textContent = data.customers;
        document.getElementById('statMRR').textContent = '€' + data.mrr.toLocaleString();
        document.getElementById('statContacts2').textContent = data.contacts;
        document.getElementById('statCampaigns2').textContent = data.campaigns;
        
        // Charts
        const chartResp = await fetch('/api/dashboard/chart');
        const chartData = await chartResp.json();
        
        new Chart(document.getElementById('revenueChart'), {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{label: 'Umsatz €', data: chartData.revenue, borderColor: '#6366f1', backgroundColor: 'rgba(99,102,241,0.1)', fill: true, tension: 0.4}]
            },
            options: {responsive: true, plugins: {legend: {display: false}}, scales: {y: {beginAtZero: true}}}
        });
        
        new Chart(document.getElementById('leadsChart'), {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{label: 'Leads', data: chartData.leads, backgroundColor: '#10b981'}]
            },
            options: {responsive: true, plugins: {legend: {display: false}}}
        });
    } catch (e) {console.error(e);}
}

// Load Data
async function loadData() {
    // Contacts
    try {
        const resp = await fetch('/api/contacts');
        const contacts = await resp.json();
        document.getElementById('contactsTable').innerHTML = contacts.map(c => `
            <tr>
                <td><strong>${esc(c.name)}</strong></td>
                <td>${esc(c.email)}</td>
                <td>${esc(c.company)}</td>
                <td>${esc(c.source)}</td>
                <td><span class="badge ${c.status}">${c.status}</span></td>
            </tr>
        `).join('');
    } catch (e) {}
    
    // Leads
    try {
        const resp = await fetch('/api/leads');
        const leads = await resp.json();
        document.getElementById('leadsTable').innerHTML = leads.map(l => `
            <tr>
                <td><strong>${esc(l.name)}</strong></td>
                <td>${esc(l.company)}</td>
                <td>€${l.value.toLocaleString()}</td>
                <td><span class="badge">${l.stage}</span></td>
                <td>${l.probability}%</td>
            </tr>
        `).join('');
    } catch (e) {}
    
    // Campaigns
    try {
        const resp = await fetch('/api/campaigns');
        const campaigns = await resp.json();
        document.getElementById('campaignsTable').innerHTML = campaigns.map(c => `
            <tr>
                <td><strong>${esc(c.name)}</strong></td>
                <td>${c.type}</td>
                <td>${c.sent.toLocaleString()}</td>
                <td>${c.opened.toLocaleString()} (${Math.round(c.opened/c.sent*100)}%)</td>
                <td>${c.clicked.toLocaleString()}</td>
                <td><span class="badge ${c.status}">${c.status}</span></td>
            </tr>
        `).join('');
    } catch (e) {}
    
    // Subscriptions
    try {
        const resp = await fetch('/api/subscriptions');
        const subs = await resp.json();
        document.getElementById('subscriptionsTable').innerHTML = subs.map(s => `
            <tr>
                <td><strong>${esc(s.customer)}</strong></td>
                <td>${s.plan}</td>
                <td>€${s.amount}/mo</td>
                <td>${s.next_billing}</td>
                <td><span class="badge ${s.status}">${s.status}</span></td>
            </tr>
        `).join('');
    } catch (e) {}
    
    // Invoices
    try {
        const resp = await fetch('/api/invoices');
        const invoices = await resp.json();
        document.getElementById('invoicesTable').innerHTML = invoices.map(i => `
            <tr>
                <td><strong>${i.id}</strong></td>
                <td>${esc(i.customer)}</td>
                <td>€${i.amount.toLocaleString()}</td>
                <td>${i.date}</td>
                <td><span class="badge ${i.status}">${i.status}</span></td>
            </tr>
        `).join('');
    } catch (e) {}
}

// Handelsregister
async function searchHR() {
    const query = document.getElementById('hrQuery').value.trim();
    if (!query) return alert('Bitte Suchbegriff eingeben');
    
    document.getElementById('hrResults').innerHTML = '<div style="padding:40px;text-align:center"><div class="spinner" style="width:40px;height:40px;border:3px solid var(--bg4);border-top-color:var(--primary);border-radius:50%;animation:spin 1s linear infinite;margin:0 auto"></div><p style="margin-top:16px;color:var(--text2)">Suche im Handelsregister...</p></div>';
    
    try {
        const resp = await fetch('/api/hr/search?q=' + encodeURIComponent(query));
        const data = await resp.json();
        
        hrSearchCount++;
        document.getElementById('hrSearches').textContent = hrSearchCount;
        document.getElementById('hrResultCount').textContent = (data.results?.length || 0) + ' Treffer';
        
        const hrb = data.results?.filter(r => r.registerArt === 'HRB').length || 0;
        const hra = data.results?.filter(r => r.registerArt === 'HRA').length || 0;
        document.getElementById('hrHRB').textContent = hrb;
        document.getElementById('hrHRA').textContent = hra;
        
        lastHRResults = data.results || [];
        
        if (!data.results?.length) {
            document.getElementById('hrResults').innerHTML = '<div style="padding:40px;text-align:center;color:var(--text3)">Keine Ergebnisse gefunden</div>';
        } else {
            document.getElementById('hrResults').innerHTML = data.results.map((r, i) => `
                <div class="result-item" onclick="showHRDetails(${i})">
                    <div class="result-header">
                        <span class="result-name">${esc(r.name)}</span>
                        <div>
                            ${r.registerArt ? `<span class="badge ${r.registerArt.toLowerCase()}">${r.registerArt}</span>` : ''}
                            <span class="badge ${r.status}">${r.status}</span>
                        </div>
                    </div>
                    <div class="result-meta">
                        <div><span>Register</span><strong>${esc(r.registerNummer) || '-'}</strong></div>
                        <div><span>Sitz</span><strong>${esc(r.sitz) || '-'}</strong></div>
                        <div><span>Rechtsform</span><strong>${esc(r.rechtsform) || '-'}</strong></div>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        document.getElementById('hrResults').innerHTML = '<div style="padding:40px;text-align:center;color:var(--rose)">Fehler: ' + e.message + '</div>';
    }
}

async function searchHROfficers() {
    const query = document.getElementById('hrOfficer').value.trim();
    if (!query) return alert('Bitte Namen eingeben');
    
    document.getElementById('hrResults').innerHTML = '<div style="padding:40px;text-align:center"><p style="color:var(--text2)">Suche Personen...</p></div>';
    
    try {
        const resp = await fetch('/api/hr/officers/search?q=' + encodeURIComponent(query));
        const data = await resp.json();
        
        hrSearchCount++;
        document.getElementById('hrSearches').textContent = hrSearchCount;
        document.getElementById('hrResultCount').textContent = (data.results?.length || 0) + ' Personen';
        
        if (!data.results?.length) {
            document.getElementById('hrResults').innerHTML = '<div style="padding:40px;text-align:center;color:var(--text3)">Keine Personen gefunden</div>';
        } else {
            document.getElementById('hrResults').innerHTML = data.results.map(r => `
                <div class="result-item">
                    <div class="result-header">
                        <span class="result-name">👤 ${esc(r.name)}</span>
                        <span class="badge">${esc(r.position) || 'Funktion'}</span>
                    </div>
                    <div class="result-meta">
                        <div><span>Firma</span><strong>${esc(r.company_name) || '-'}</strong></div>
                        <div><span>Beginn</span><strong>${r.start_date || '-'}</strong></div>
                        <div><span>Ende</span><strong>${r.end_date || 'aktiv'}</strong></div>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        document.getElementById('hrResults').innerHTML = '<div style="padding:40px;text-align:center;color:var(--rose)">Fehler: ' + e.message + '</div>';
    }
}

async function showHRDetails(idx) {
    const r = lastHRResults[idx];
    if (!r) return;
    
    document.getElementById('modalTitle').textContent = r.name;
    document.getElementById('modalBody').innerHTML = '<p style="text-align:center;color:var(--text2)">Lade Details...</p>';
    document.getElementById('modalFooter').innerHTML = `<button class="btn btn-success" onclick="importHRContact(${idx})">📥 In CRM importieren</button>`;
    document.getElementById('modal').classList.add('active');
    
    try {
        const resp = await fetch('/api/hr/company/' + encodeURIComponent(r.id));
        const d = await resp.json();
        
        document.getElementById('modalBody').innerHTML = `
            <div style="display:grid;gap:16px">
                <div style="background:var(--bg3);padding:16px;border-radius:8px">
                    <h4 style="margin-bottom:12px;color:var(--text2)">📋 Registerdaten</h4>
                    <p><strong>Register:</strong> ${r.registerArt || '-'} ${d.id || ''}</p>
                    <p><strong>Status:</strong> <span class="badge ${d.status}">${d.status}</span></p>
                    <p><strong>Gründung:</strong> ${d.gruendung || '-'}</p>
                </div>
                <div style="background:var(--bg3);padding:16px;border-radius:8px">
                    <h4 style="margin-bottom:12px;color:var(--text2)">🏢 Unternehmen</h4>
                    <p><strong>Rechtsform:</strong> ${d.rechtsform || '-'}</p>
                    <p><strong>Adresse:</strong> ${d.adresse || '-'}</p>
                </div>
                ${d.officers?.length ? `
                <div style="background:var(--bg3);padding:16px;border-radius:8px">
                    <h4 style="margin-bottom:12px;color:var(--text2)">👥 Vertretungsberechtigte (${d.officers.length})</h4>
                    ${d.officers.slice(0,5).map(o => `<p><strong>${esc(o.name)}</strong> - ${esc(o.position)} ${o.start_date ? '(seit ' + o.start_date + ')' : ''}</p>`).join('')}
                </div>
                ` : ''}
                <div style="font-size:12px;color:var(--text3)">
                    Quelle: OpenCorporates ${d.url ? `| <a href="${d.url}" target="_blank" style="color:var(--primary)">Ansehen</a>` : ''}
                </div>
            </div>
        `;
    } catch (e) {
        document.getElementById('modalBody').innerHTML = '<p style="color:var(--rose)">Fehler beim Laden</p>';
    }
}

async function importHRContact(idx) {
    const r = lastHRResults[idx];
    if (!r) return;
    
    try {
        await fetch('/api/hr/import', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(r)
        });
        hrImportCount++;
        document.getElementById('hrImported').textContent = hrImportCount;
        closeModal();
        alert('✅ ' + r.name + ' wurde importiert!');
        loadData();
    } catch (e) {
        alert('Fehler beim Import');
    }
}

// Modal
function showModal(type) {
    if (type === 'newContact') {
        document.getElementById('modalTitle').textContent = 'Neuer Kontakt';
        document.getElementById('modalBody').innerHTML = `
            <div class="form-group"><label>Name</label><input type="text" class="form-input" id="newContactName"></div>
            <div class="form-group"><label>E-Mail</label><input type="email" class="form-input" id="newContactEmail"></div>
            <div class="form-group"><label>Firma</label><input type="text" class="form-input" id="newContactCompany"></div>
            <div class="form-group"><label>Telefon</label><input type="text" class="form-input" id="newContactPhone"></div>
        `;
        document.getElementById('modalFooter').innerHTML = `<button class="btn btn-primary" onclick="saveContact()">Speichern</button>`;
    }
    document.getElementById('modal').classList.add('active');
}

function closeModal() {
    document.getElementById('modal').classList.remove('active');
}

async function saveContact() {
    const data = {
        name: document.getElementById('newContactName').value,
        email: document.getElementById('newContactEmail').value,
        company: document.getElementById('newContactCompany').value,
        phone: document.getElementById('newContactPhone').value
    };
    await fetch('/api/contacts', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    closeModal();
    loadData();
}

// Utility
function esc(s) { return s ? String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') : ''; }

// Keyboard
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});
document.getElementById('loginPass').addEventListener('keypress', e => { if(e.key==='Enter') doLogin(); });

// Init
checkAuth();
</script>
<style>@keyframes spin{to{transform:rotate(360deg)}}</style>
</body>
</html>'''

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("  ⚡ WEST MONEY OS v5.0 - FINAL EDITION")
    print("=" * 70)
    print(f"  🌐 Server: http://localhost:{PORT}")
    print(f"  🔑 Login: admin / 663724")
    print("=" * 70)
    app.run(host='0.0.0.0', port=PORT, debug=False)
