#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ⚡ WEST MONEY OS v6.1 - ULTIMATE ENTERPRISE EDITION ⚡                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  🏢 Enterprise Universe GmbH - Full Business Platform                        ║
║  💳 Subscription & Pricing System                                            ║
║  🎮 Demo Mode Available                                                      ║
║  © 2025 Ömer Hüseyin Coşkun                                                  ║
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

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
CORS(app)

PORT = int(os.getenv('PORT', 5000))
OPENCORPORATES_API_KEY = os.getenv('OPENCORPORATES_API_KEY', '')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', 'pk_test_demo')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_demo')

# =============================================================================
# PRICING PLANS
# =============================================================================
PLANS = {
    'starter': {
        'name': 'Starter',
        'price': 29,
        'price_yearly': 290,
        'features': ['5 Kontakte', '3 Leads', 'Basic Dashboard', 'E-Mail Support', 'Handelsregister (10/Monat)'],
        'limits': {'contacts': 5, 'leads': 3, 'hr_searches': 10},
        'stripe_price_id': 'price_starter_monthly'
    },
    'professional': {
        'name': 'Professional',
        'price': 99,
        'price_yearly': 990,
        'features': ['Unbegrenzte Kontakte', 'Unbegrenzte Leads', 'Voller Dashboard', 'Priority Support', 'Handelsregister (100/Monat)', 'Explorium Integration', 'Kampagnen'],
        'limits': {'contacts': -1, 'leads': -1, 'hr_searches': 100},
        'stripe_price_id': 'price_professional_monthly',
        'popular': True
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 299,
        'price_yearly': 2990,
        'features': ['Alles aus Professional', 'Broly Automations', 'Einstein Agency', 'GTzMeta Gaming', 'FinTech & Crypto', 'DedSec Security', 'White Label Option', 'Dedicated Support', 'Custom Integrationen'],
        'limits': {'contacts': -1, 'leads': -1, 'hr_searches': -1},
        'stripe_price_id': 'price_enterprise_monthly'
    }
}

# =============================================================================
# USERS & AUTH
# =============================================================================
USERS = {
    'admin': {'password': hashlib.sha256('663724'.encode()).hexdigest(), 'name': 'Ömer Coşkun', 'email': 'info@west-money.com', 'role': 'GOD MODE', 'company': 'Enterprise Universe GmbH', 'avatar': 'ÖC', 'plan': 'enterprise'},
    'demo': {'password': hashlib.sha256('demo123'.encode()).hexdigest(), 'name': 'Demo User', 'email': 'demo@west-money.com', 'role': 'Demo', 'company': 'Demo Company', 'avatar': 'DM', 'plan': 'professional'},
}

# =============================================================================
# DEMO DATABASE
# =============================================================================
DB = {
    'contacts': [
        {'id': 1, 'name': 'Max Mustermann', 'email': 'max@techgmbh.de', 'company': 'Tech GmbH', 'phone': '+49 221 12345678', 'status': 'active', 'source': 'Website', 'created': '2025-12-01'},
        {'id': 2, 'name': 'Anna Schmidt', 'email': 'anna@startup.de', 'company': 'StartUp AG', 'phone': '+49 89 98765432', 'status': 'active', 'source': 'Handelsregister', 'created': '2025-12-05'},
        {'id': 3, 'name': 'Thomas Weber', 'email': 'weber@industrie.de', 'company': 'Industrie KG', 'phone': '+49 211 55555555', 'status': 'lead', 'source': 'Explorium', 'created': '2025-12-10'},
        {'id': 4, 'name': 'Julia Becker', 'email': 'j.becker@finance.de', 'company': 'Finance Plus GmbH', 'phone': '+49 69 44444444', 'status': 'active', 'source': 'Messe', 'created': '2025-12-12'},
        {'id': 5, 'name': 'LOXONE Partner', 'email': 'partner@loxone.com', 'company': 'LOXONE', 'phone': '+43 7612 90901', 'status': 'active', 'source': 'Partner', 'created': '2025-11-01'},
    ],
    'leads': [
        {'id': 1, 'name': 'Smart Home Villa', 'company': 'Private Investor', 'contact': 'Dr. Hans Meier', 'email': 'meier@gmail.com', 'value': 185000, 'stage': 'proposal', 'probability': 75},
        {'id': 2, 'name': 'Bürogebäude Automation', 'company': 'Corporate Real Estate', 'contact': 'Maria Corporate', 'email': 'maria@corporate.de', 'value': 450000, 'stage': 'negotiation', 'probability': 85},
        {'id': 3, 'name': 'Hotel Automation', 'company': 'Luxus Hotels AG', 'contact': 'Peter Luxus', 'email': 'peter@luxushotels.de', 'value': 890000, 'stage': 'qualified', 'probability': 60},
        {'id': 4, 'name': 'Restaurant Beleuchtung', 'company': 'Gastro Excellence', 'contact': 'Tom Gastro', 'email': 'tom@gastro.de', 'value': 45000, 'stage': 'won', 'probability': 100},
    ],
    'campaigns': [
        {'id': 1, 'name': 'Q4 Newsletter', 'type': 'email', 'status': 'active', 'sent': 2500, 'opened': 1125, 'clicked': 340, 'converted': 28},
        {'id': 2, 'name': 'Smart Home Launch', 'type': 'email', 'status': 'completed', 'sent': 5000, 'opened': 2750, 'clicked': 890, 'converted': 67},
    ],
    'stats': {
        'revenue': 1247000, 'revenue_growth': 28.5, 'leads': 67, 'leads_growth': 22,
        'customers': 234, 'customers_growth': 18, 'mrr': 18750, 'mrr_growth': 12.4,
        'churn': 1.8, 'ltv': 4250, 'cac': 380, 'nps': 78
    },
    'chart_data': {
        'labels': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
        'revenue': [62000, 78000, 81000, 97000, 102000, 99000, 118000, 132000, 149000, 165000, 182000, 247000],
        'leads': [28, 35, 32, 41, 38, 45, 52, 48, 56, 62, 58, 67],
        'mrr': [9200, 10800, 11100, 12600, 13200, 14500, 15000, 16400, 16900, 17200, 17850, 18750]
    },
    'gaming': {'twitch_followers': 15420, 'youtube_subs': 8750, 'discord_members': 3240, 'peak_viewers': 12500},
    'automations': {'active_systems': 47, 'devices_connected': 2840, 'energy_saved_kwh': 45200},
    'security': {'threats_blocked': 1247, 'systems_protected': 58, 'uptime_percent': 99.97, 'security_score': 94}
}

# =============================================================================
# AUTH ROUTES
# =============================================================================
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '')
    password = data.get('password', '')
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    if username in USERS and USERS[username]['password'] == pw_hash:
        session['user'] = username
        user = USERS[username]
        return jsonify({'success': True, 'user': {'name': user['name'], 'email': user['email'], 'role': user['role'], 'company': user['company'], 'avatar': user['avatar'], 'plan': user['plan']}})
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

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
# PRICING & SUBSCRIPTION
# =============================================================================
@app.route('/api/plans')
def get_plans():
    return jsonify(PLANS)

@app.route('/api/checkout', methods=['POST'])
def create_checkout():
    data = request.json or {}
    plan = data.get('plan', 'starter')
    billing = data.get('billing', 'monthly')
    # In production, create Stripe checkout session here
    return jsonify({
        'success': True,
        'checkout_url': f'https://checkout.stripe.com/demo?plan={plan}&billing={billing}',
        'message': 'Demo Mode - In Produktion wird hier zu Stripe weitergeleitet'
    })

# =============================================================================
# DASHBOARD & DATA
# =============================================================================
@app.route('/api/dashboard/stats')
def dashboard_stats():
    # SECURITY: Demo users see demo data, not real data
    if session.get('user') == 'demo':
        return jsonify({
            'revenue': 125000, 'revenue_growth': 15.2, 'leads': 12, 'leads_growth': 8,
            'customers': 24, 'customers_growth': 12, 'mrr': 2450, 'mrr_growth': 5.4,
            'churn': 2.1, 'ltv': 1200, 'cac': 180, 'nps': 65
        })
    return jsonify(DB['stats'])

@app.route('/api/dashboard/charts')
def dashboard_charts():
    # SECURITY: Demo users see demo charts
    if session.get('user') == 'demo':
        return jsonify({
            'labels': ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
            'revenue': [8000, 9500, 11000, 12500, 14000, 15500, 17000, 19000, 21000, 23000, 25000, 28000],
            'leads': [3, 4, 5, 6, 5, 7, 8, 7, 9, 10, 11, 12],
            'mrr': [1200, 1400, 1550, 1700, 1850, 1950, 2100, 2200, 2300, 2350, 2400, 2450]
        })
    return jsonify(DB['chart_data'])

@app.route('/api/contacts')
def get_contacts():
    # SECURITY: Demo users see demo contacts
    if session.get('user') == 'demo':
        return jsonify([
            {'id': 1, 'name': 'Demo Kontakt 1', 'email': 'demo1@example.com', 'company': 'Demo GmbH', 'phone': '+49 123 456789', 'status': 'active', 'source': 'Demo', 'created': '2025-12-01'},
            {'id': 2, 'name': 'Demo Kontakt 2', 'email': 'demo2@example.com', 'company': 'Test AG', 'phone': '+49 987 654321', 'status': 'lead', 'source': 'Website', 'created': '2025-12-10'},
            {'id': 3, 'name': 'Demo Kontakt 3', 'email': 'demo3@example.com', 'company': 'Sample Corp', 'phone': '+49 555 123456', 'status': 'active', 'source': 'Referral', 'created': '2025-12-15'},
        ])
    return jsonify(DB['contacts'])

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    data = request.json
    new_id = max([c['id'] for c in DB['contacts']], default=0) + 1
    contact = {'id': new_id, 'name': data.get('name', ''), 'email': data.get('email', ''), 'company': data.get('company', ''), 'phone': data.get('phone', ''), 'status': 'lead', 'source': 'Manual', 'created': datetime.now().strftime('%Y-%m-%d')}
    DB['contacts'].append(contact)
    return jsonify(contact)

@app.route('/api/leads')
def get_leads():
    # SECURITY: Demo users see demo leads
    if session.get('user') == 'demo':
        return jsonify([
            {'id': 1, 'name': 'Demo Projekt A', 'company': 'Demo Kunde', 'contact': 'Max Demo', 'email': 'max@demo.de', 'value': 25000, 'stage': 'proposal', 'probability': 60},
            {'id': 2, 'name': 'Demo Projekt B', 'company': 'Test Firma', 'contact': 'Lisa Test', 'email': 'lisa@test.de', 'value': 45000, 'stage': 'qualified', 'probability': 40},
        ])
    return jsonify(DB['leads'])

@app.route('/api/leads', methods=['POST'])
def create_lead():
    data = request.json
    new_id = max([l['id'] for l in DB['leads']], default=0) + 1
    lead = {'id': new_id, 'name': data.get('name', ''), 'company': data.get('company', ''), 'contact': data.get('contact', ''), 'email': data.get('email', ''), 'value': int(data.get('value', 0)), 'stage': 'discovery', 'probability': 10}
    DB['leads'].append(lead)
    return jsonify(lead)

@app.route('/api/campaigns')
def get_campaigns():
    return jsonify(DB['campaigns'])

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
            results.append({'id': c.get('company_number', ''), 'name': c.get('name', ''), 'register_type': reg_type, 'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv', 'type': c.get('company_type', ''), 'city': addr.get('locality', ''), 'founded': c.get('incorporation_date', '')})
        return jsonify({'success': True, 'results': results, 'total': data.get('results', {}).get('total_count', 0)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'results': []})

@app.route('/api/hr/import', methods=['POST'])
def hr_import():
    data = request.json
    new_id = max([c['id'] for c in DB['contacts']], default=0) + 1
    contact = {'id': new_id, 'name': data.get('name', ''), 'email': '', 'company': data.get('name', ''), 'phone': '', 'status': 'lead', 'source': 'Handelsregister', 'created': datetime.now().strftime('%Y-%m-%d')}
    DB['contacts'].append(contact)
    return jsonify({'success': True, 'contact': contact})

# =============================================================================
# ADDITIONAL MODULES
# =============================================================================
@app.route('/api/gaming/stats')
def gaming_stats():
    return jsonify(DB['gaming'])

@app.route('/api/automations/stats')
def automations_stats():
    return jsonify(DB['automations'])

@app.route('/api/security/stats')
def security_stats():
    return jsonify(DB['security'])

@app.route('/api/explorium/stats')
def explorium_stats():
    return jsonify({'credits': 4873, 'plan': 'Professional', 'searches': 89})

# =============================================================================
# HEALTH
# =============================================================================
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'version': '6.1.0'})

# =============================================================================
# ROUTES
# =============================================================================
@app.route('/')
def landing():
    return Response(LANDING_HTML, mimetype='text/html')

@app.route('/pricing')
def pricing():
    return Response(PRICING_HTML, mimetype='text/html')

@app.route('/app')
def app_page():
    return Response(APP_HTML, mimetype='text/html')

@app.route('/demo')
def demo():
    return Response(DEMO_HTML, mimetype='text/html')

# =============================================================================
# LANDING PAGE HTML
# =============================================================================
LANDING_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>West Money OS | Enterprise Business Platform</title>
<meta name="description" content="Die All-in-One Business Platform für Smart Home, CRM, FinTech und mehr. Starten Sie jetzt kostenlos!">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
:root{--bg:#09090b;--bg-2:#161619;--bg-3:#1c1c20;--text:#fafafa;--text-2:#a1a1aa;--gold:#fbbf24;--orange:#f97316;--primary:#6366f1;--emerald:#10b981;--border:rgba(255,255,255,.08)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
.nav{position:fixed;top:0;left:0;right:0;background:rgba(9,9,11,.9);backdrop-filter:blur(10px);border-bottom:1px solid var(--border);z-index:100;padding:0 24px}
.nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:72px}
.nav-logo{display:flex;align-items:center;gap:12px;font-size:20px;font-weight:700;text-decoration:none;color:var(--text)}
.nav-logo span{background:linear-gradient(135deg,var(--gold),var(--orange));width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center}
.nav-links{display:flex;gap:32px}
.nav-links a{color:var(--text-2);text-decoration:none;font-size:14px;transition:color .2s}
.nav-links a:hover{color:var(--text)}
.nav-btns{display:flex;gap:12px}
.btn{padding:10px 20px;border-radius:8px;font-size:14px;font-weight:500;text-decoration:none;transition:all .2s;cursor:pointer;border:none}
.btn-ghost{background:transparent;color:var(--text);border:1px solid var(--border)}
.btn-ghost:hover{background:var(--bg-2)}
.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;font-weight:600}
.btn-gold:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(251,191,36,.3)}
.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:120px 24px 80px;background:radial-gradient(ellipse at top,rgba(251,191,36,.08) 0%,transparent 50%)}
.hero-content{max-width:800px}
.hero-badge{display:inline-flex;align-items:center;gap:8px;background:var(--bg-2);border:1px solid var(--border);padding:6px 16px;border-radius:20px;font-size:12px;color:var(--text-2);margin-bottom:24px}
.hero-badge .dot{width:8px;height:8px;background:var(--emerald);border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.hero h1{font-size:64px;font-weight:700;line-height:1.1;margin-bottom:24px;background:linear-gradient(135deg,var(--text) 0%,var(--gold) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{font-size:20px;color:var(--text-2);margin-bottom:40px;max-width:600px;margin-left:auto;margin-right:auto}
.hero-btns{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.hero-btns .btn{padding:14px 28px;font-size:16px}
.stats-row{display:flex;justify-content:center;gap:48px;margin-top:64px;flex-wrap:wrap}
.stat{text-align:center}
.stat-value{font-size:36px;font-weight:700;color:var(--gold)}
.stat-label{font-size:14px;color:var(--text-2)}
.features{padding:120px 24px;background:var(--bg-2)}
.section-title{text-align:center;margin-bottom:64px}
.section-title h2{font-size:42px;font-weight:700;margin-bottom:16px}
.section-title p{color:var(--text-2);font-size:18px}
.features-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;max-width:1200px;margin:0 auto}
.feature-card{background:var(--bg);border:1px solid var(--border);border-radius:16px;padding:32px;transition:all .3s}
.feature-card:hover{border-color:rgba(251,191,36,.3);transform:translateY(-4px)}
.feature-icon{width:56px;height:56px;background:linear-gradient(135deg,rgba(251,191,36,.2),rgba(251,191,36,.05));border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:20px}
.feature-card h3{font-size:20px;font-weight:600;margin-bottom:12px}
.feature-card p{color:var(--text-2);font-size:14px;line-height:1.7}
.cta{padding:120px 24px;text-align:center;background:linear-gradient(180deg,var(--bg) 0%,rgba(251,191,36,.05) 100%)}
.cta h2{font-size:42px;font-weight:700;margin-bottom:16px}
.cta p{color:var(--text-2);font-size:18px;margin-bottom:40px}
.footer{padding:48px 24px;border-top:1px solid var(--border);text-align:center}
.footer p{color:var(--text-2);font-size:14px}
.footer a{color:var(--gold);text-decoration:none}
@media(max-width:900px){.hero h1{font-size:42px}.features-grid{grid-template-columns:1fr}.nav-links{display:none}}
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
<a href="https://docs.west-money.com">Docs</a>
</div>
<div class="nav-btns">
<a href="/app" class="btn btn-ghost">Login</a>
<a href="/pricing" class="btn btn-gold">Kostenlos starten</a>
</div>
</div>
</nav>

<section class="hero">
<div class="hero-content">
<div class="hero-badge"><span class="dot"></span>v6.1 - Ultimate Enterprise Edition</div>
<h1>Die All-in-One Business Platform</h1>
<p>CRM, Smart Home Automation, Handelsregister, FinTech, und mehr - alles in einer Plattform. Steigern Sie Ihre Produktivität um 300%.</p>
<div class="hero-btns">
<a href="/demo" class="btn btn-gold">🎮 Demo testen</a>
<a href="/pricing" class="btn btn-ghost">💳 Pläne ansehen</a>
</div>
<div class="stats-row">
<div class="stat"><div class="stat-value">234+</div><div class="stat-label">Aktive Kunden</div></div>
<div class="stat"><div class="stat-value">€1.2M+</div><div class="stat-label">Pipeline verwaltet</div></div>
<div class="stat"><div class="stat-value">99.9%</div><div class="stat-label">Uptime</div></div>
<div class="stat"><div class="stat-value">47</div><div class="stat-label">Smart Home Systeme</div></div>
</div>
</div>
</section>

<section class="features" id="features">
<div class="section-title">
<h2>Alles was Sie brauchen</h2>
<p>Eine Platform - unendliche Möglichkeiten</p>
</div>
<div class="features-grid">
<div class="feature-card">
<div class="feature-icon">👥</div>
<h3>CRM & Kontakte</h3>
<p>Verwalten Sie Ihre Kontakte, Leads und Deals in einer übersichtlichen Pipeline. Automatische Follow-ups und Erinnerungen.</p>
</div>
<div class="feature-card">
<div class="feature-icon">🏛️</div>
<h3>Handelsregister</h3>
<p>Direkter Zugriff auf das deutsche Handelsregister. Suchen Sie Firmen und importieren Sie diese direkt in Ihr CRM.</p>
</div>
<div class="feature-card">
<div class="feature-icon">🤖</div>
<h3>Broly Automations</h3>
<p>Smart Home & Building Automation mit LOXONE und ComfortClick Integration. Energie sparen und Komfort steigern.</p>
</div>
<div class="feature-card">
<div class="feature-icon">🏗️</div>
<h3>Einstein Agency</h3>
<p>Architektur und Smart Home Planung. Barrierefreies Bauen und nachhaltige Gebäudekonzepte.</p>
</div>
<div class="feature-card">
<div class="feature-icon">💳</div>
<h3>FinTech & Crypto</h3>
<p>Wallet Management, Crypto Holdings und Stripe Integration. Behalten Sie Ihre Finanzen im Blick.</p>
</div>
<div class="feature-card">
<div class="feature-icon">🛡️</div>
<h3>DedSec Security</h3>
<p>Enterprise-grade Security. SSL, Firewall, VPN und 24/7 Monitoring für maximale Sicherheit.</p>
</div>
</div>
</section>

<section class="cta">
<h2>Bereit durchzustarten?</h2>
<p>Starten Sie noch heute kostenlos und erleben Sie die Zukunft des Business Managements.</p>
<div class="hero-btns">
<a href="/demo" class="btn btn-gold">🚀 Jetzt Demo starten</a>
<a href="/pricing" class="btn btn-ghost">Alle Pläne ansehen →</a>
</div>
</section>

<footer class="footer">
<p>© 2025 <a href="https://enterprise-universe.de">Enterprise Universe GmbH</a> | West Money OS v6.1</p>
<p style="margin-top:8px">Made with ⚡ by Ömer Hüseyin Coşkun</p>
</footer>
</body>
</html>'''

# =============================================================================
# PRICING PAGE HTML
# =============================================================================
PRICING_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pricing | West Money OS</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
:root{--bg:#09090b;--bg-2:#161619;--bg-3:#1c1c20;--text:#fafafa;--text-2:#a1a1aa;--gold:#fbbf24;--orange:#f97316;--primary:#6366f1;--emerald:#10b981;--border:rgba(255,255,255,.08)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;min-height:100vh}
.nav{position:fixed;top:0;left:0;right:0;background:rgba(9,9,11,.9);backdrop-filter:blur(10px);border-bottom:1px solid var(--border);z-index:100;padding:0 24px}
.nav-inner{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:72px}
.nav-logo{display:flex;align-items:center;gap:12px;font-size:20px;font-weight:700;text-decoration:none;color:var(--text)}
.nav-logo span{background:linear-gradient(135deg,var(--gold),var(--orange));width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center}
.btn{padding:10px 20px;border-radius:8px;font-size:14px;font-weight:500;text-decoration:none;transition:all .2s;cursor:pointer;border:none}
.btn-ghost{background:transparent;color:var(--text);border:1px solid var(--border)}
.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;font-weight:600}
.btn-gold:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(251,191,36,.3)}
.pricing{padding:140px 24px 80px;max-width:1200px;margin:0 auto}
.pricing-header{text-align:center;margin-bottom:64px}
.pricing-header h1{font-size:48px;font-weight:700;margin-bottom:16px}
.pricing-header p{color:var(--text-2);font-size:18px}
.billing-toggle{display:flex;justify-content:center;gap:12px;margin-top:32px;align-items:center}
.billing-toggle span{color:var(--text-2);font-size:14px}
.billing-toggle .active{color:var(--gold)}
.toggle{width:56px;height:28px;background:var(--bg-3);border-radius:14px;position:relative;cursor:pointer}
.toggle::after{content:'';position:absolute;width:24px;height:24px;background:var(--gold);border-radius:50%;top:2px;left:2px;transition:transform .2s}
.toggle.yearly::after{transform:translateX(28px)}
.pricing-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:48px}
.plan-card{background:var(--bg-2);border:1px solid var(--border);border-radius:20px;padding:32px;position:relative;transition:all .3s}
.plan-card:hover{border-color:rgba(255,255,255,.15)}
.plan-card.popular{border-color:var(--gold);background:linear-gradient(180deg,rgba(251,191,36,.05) 0%,var(--bg-2) 100%)}
.popular-badge{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;padding:4px 16px;border-radius:20px;font-size:12px;font-weight:600}
.plan-name{font-size:24px;font-weight:700;margin-bottom:8px}
.plan-price{font-size:48px;font-weight:700;margin-bottom:8px}
.plan-price span{font-size:18px;color:var(--text-2);font-weight:400}
.plan-desc{color:var(--text-2);font-size:14px;margin-bottom:24px}
.plan-features{list-style:none;margin-bottom:32px}
.plan-features li{padding:8px 0;font-size:14px;display:flex;align-items:center;gap:12px}
.plan-features li::before{content:'✓';color:var(--emerald);font-weight:700}
.plan-btn{width:100%;padding:14px;border-radius:10px;font-size:14px;font-weight:600;cursor:pointer;border:none;transition:all .2s}
.plan-btn.primary{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}
.plan-btn.primary:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(251,191,36,.3)}
.plan-btn.secondary{background:var(--bg-3);color:var(--text);border:1px solid var(--border)}
.guarantee{text-align:center;margin-top:48px;padding:24px;background:var(--bg-2);border-radius:12px}
.guarantee p{color:var(--text-2);font-size:14px}
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
<p>Wählen Sie den Plan der zu Ihnen passt. Jederzeit kündbar.</p>
<div class="billing-toggle">
<span class="active" id="monthlyLabel">Monatlich</span>
<div class="toggle" id="billingToggle" onclick="toggleBilling()"></div>
<span id="yearlyLabel">Jährlich <span style="color:var(--emerald)">-17%</span></span>
</div>
</div>

<div class="pricing-grid">
<div class="plan-card">
<div class="plan-name">Starter</div>
<div class="plan-price" id="starterPrice">€29<span>/Monat</span></div>
<div class="plan-desc">Perfekt für Einzelunternehmer und kleine Teams</div>
<ul class="plan-features">
<li>5 Kontakte</li>
<li>3 Leads</li>
<li>Basic Dashboard</li>
<li>E-Mail Support</li>
<li>Handelsregister (10/Monat)</li>
</ul>
<button class="plan-btn secondary" onclick="checkout('starter')">Starten</button>
</div>

<div class="plan-card popular">
<div class="popular-badge">⭐ Beliebt</div>
<div class="plan-name">Professional</div>
<div class="plan-price" id="proPrice">€99<span>/Monat</span></div>
<div class="plan-desc">Für wachsende Unternehmen</div>
<ul class="plan-features">
<li>Unbegrenzte Kontakte</li>
<li>Unbegrenzte Leads</li>
<li>Voller Dashboard</li>
<li>Priority Support</li>
<li>Handelsregister (100/Monat)</li>
<li>Explorium Integration</li>
<li>Kampagnen</li>
</ul>
<button class="plan-btn primary" onclick="checkout('professional')">Jetzt starten</button>
</div>

<div class="plan-card">
<div class="plan-name">Enterprise</div>
<div class="plan-price" id="entPrice">€299<span>/Monat</span></div>
<div class="plan-desc">Für Unternehmen mit hohen Ansprüchen</div>
<ul class="plan-features">
<li>Alles aus Professional</li>
<li>Broly Automations</li>
<li>Einstein Agency</li>
<li>GTzMeta Gaming</li>
<li>FinTech & Crypto</li>
<li>DedSec Security</li>
<li>White Label Option</li>
<li>Dedicated Support</li>
<li>Custom Integrationen</li>
</ul>
<button class="plan-btn secondary" onclick="checkout('enterprise')">Kontakt</button>
</div>
</div>

<div class="guarantee">
<p>💳 Sichere Zahlung über Stripe | 🔒 SSL verschlüsselt | 🔄 30 Tage Geld-zurück-Garantie</p>
</div>
</section>

<script>
let yearly = false;
const prices = {starter: [29, 290], professional: [99, 990], enterprise: [299, 2990]};

function toggleBilling() {
    yearly = !yearly;
    document.getElementById('billingToggle').classList.toggle('yearly', yearly);
    document.getElementById('monthlyLabel').classList.toggle('active', !yearly);
    document.getElementById('yearlyLabel').classList.toggle('active', yearly);
    const period = yearly ? '/Jahr' : '/Monat';
    document.getElementById('starterPrice').innerHTML = '€' + prices.starter[yearly?1:0] + '<span>' + period + '</span>';
    document.getElementById('proPrice').innerHTML = '€' + prices.professional[yearly?1:0] + '<span>' + period + '</span>';
    document.getElementById('entPrice').innerHTML = '€' + prices.enterprise[yearly?1:0] + '<span>' + period + '</span>';
}

function checkout(plan) {
    const billing = yearly ? 'yearly' : 'monthly';
    if (plan === 'enterprise') {
        window.location.href = 'mailto:info@west-money.com?subject=Enterprise Plan Anfrage';
    } else {
        alert('Demo Mode: In Produktion werden Sie zu Stripe weitergeleitet.\\n\\nPlan: ' + plan.toUpperCase() + '\\nAbrechnungszeitraum: ' + (yearly ? 'Jährlich' : 'Monatlich'));
    }
}
</script>
</body>
</html>'''

# =============================================================================
# DEMO PAGE HTML
# =============================================================================
DEMO_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Demo | West Money OS</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
:root{--bg:#09090b;--bg-2:#161619;--text:#fafafa;--text-2:#a1a1aa;--gold:#fbbf24;--orange:#f97316;--emerald:#10b981;--border:rgba(255,255,255,.08)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
.demo-box{background:var(--bg-2);border:1px solid var(--border);border-radius:24px;padding:48px;max-width:480px;width:100%;text-align:center}
.demo-icon{width:80px;height:80px;background:linear-gradient(135deg,var(--gold),var(--orange));border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:36px;margin:0 auto 24px;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(251,191,36,.4)}50%{box-shadow:0 0 0 20px rgba(251,191,36,0)}}
h1{font-size:32px;margin-bottom:12px}
p{color:var(--text-2);margin-bottom:32px}
.features{text-align:left;background:var(--bg);border-radius:12px;padding:20px;margin-bottom:32px}
.features h3{font-size:14px;color:var(--text-2);margin-bottom:12px}
.features ul{list-style:none}
.features li{padding:8px 0;font-size:14px;display:flex;align-items:center;gap:8px}
.features li::before{content:'✓';color:var(--emerald)}
.btn{width:100%;padding:16px;border-radius:12px;font-size:16px;font-weight:600;cursor:pointer;border:none;margin-bottom:12px}
.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}
.btn-gold:hover{transform:translateY(-2px)}
.btn-ghost{background:transparent;color:var(--text);border:1px solid var(--border)}
.note{font-size:12px;color:var(--text-2);margin-top:16px}
</style>
</head>
<body>
<div class="demo-box">
<div class="demo-icon">🎮</div>
<h1>Demo starten</h1>
<p>Testen Sie West Money OS kostenlos und unverbindlich mit allen Features.</p>
<div class="features">
<h3>In der Demo enthalten:</h3>
<ul>
<li>Vollständiges CRM Dashboard</li>
<li>Kontakte & Leads Management</li>
<li>Handelsregister Suche (LIVE)</li>
<li>Explorium B2B Data</li>
<li>Broly Automations</li>
<li>Einstein Agency</li>
<li>FinTech & Security</li>
</ul>
</div>
<button class="btn btn-gold" onclick="startDemo()">🚀 Demo starten</button>
<button class="btn btn-ghost" onclick="window.location.href='/app'">Ich habe einen Account</button>
<p class="note">Keine Registrierung erforderlich. Demo läuft 30 Minuten.</p>
</div>
<script>
async function startDemo() {
    try {
        const r = await fetch('/api/auth/demo', {method: 'POST'});
        const d = await r.json();
        if (d.success) {
            window.location.href = '/app';
        }
    } catch(e) {
        alert('Fehler beim Starten der Demo');
    }
}
</script>
</body>
</html>'''

# =============================================================================
# APP HTML (Full Dashboard)
# =============================================================================
APP_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>West Money OS v6.1 | Dashboard</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{--bg-0:#09090b;--bg-1:#0f0f12;--bg-2:#161619;--bg-3:#1c1c20;--text-0:#fafafa;--text-1:#e4e4e7;--text-2:#a1a1aa;--text-3:#71717a;--primary:#6366f1;--emerald:#10b981;--amber:#f59e0b;--rose:#f43f5e;--cyan:#06b6d4;--violet:#8b5cf6;--gold:#fbbf24;--orange:#f97316;--border:rgba(255,255,255,.08);--radius:8px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg-0);color:var(--text-0);font-size:14px}
.login-screen{min-height:100vh;display:flex;align-items:center;justify-content:center;background:var(--bg-0)}
.login-box{background:var(--bg-2);border:1px solid var(--border);border-radius:20px;padding:48px;width:100%;max-width:400px}
.login-logo{text-align:center;margin-bottom:32px}
.login-logo-icon{width:72px;height:72px;background:linear-gradient(135deg,var(--gold),var(--orange));border-radius:18px;display:inline-flex;align-items:center;justify-content:center;font-size:32px;margin-bottom:16px}
.login-logo h1{font-size:24px;margin-bottom:4px}
.login-logo p{color:var(--text-3);font-size:13px}
.form-group{margin-bottom:16px}
.form-group label{display:block;font-size:13px;margin-bottom:6px;color:var(--text-2)}
.form-input{width:100%;padding:12px;background:var(--bg-3);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-0);font-size:14px}
.form-input:focus{outline:none;border-color:var(--gold)}
.login-btn{width:100%;padding:14px;background:linear-gradient(135deg,var(--gold),var(--orange));color:#000;border:none;border-radius:var(--radius);font-size:14px;font-weight:600;cursor:pointer;margin-top:8px}
.login-btn:hover{transform:translateY(-2px)}
.demo-link{text-align:center;margin-top:20px}
.demo-link a{color:var(--gold);text-decoration:none;font-size:13px}
.login-error{background:rgba(244,63,94,.1);border:1px solid rgba(244,63,94,.3);color:var(--rose);padding:10px;border-radius:var(--radius);margin-bottom:16px;text-align:center;display:none;font-size:13px}
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
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:var(--radius);cursor:pointer;color:var(--text-2);font-size:13px;margin-bottom:2px}
.nav-item:hover{background:var(--bg-3);color:var(--text-0)}
.nav-item.active{background:rgba(251,191,36,.1);color:var(--gold);border:1px solid rgba(251,191,36,.2)}
.nav-item .badge{font-size:9px;padding:2px 6px;border-radius:8px;font-weight:600;margin-left:auto}
.nav-item .badge.live{background:var(--rose);color:white}
.nav-item .badge.api{background:var(--cyan);color:white}
.nav-item .badge.gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}
.sidebar-footer{padding:12px;border-top:1px solid var(--border)}
.user-card{display:flex;align-items:center;gap:10px;padding:10px;background:var(--bg-2);border-radius:var(--radius)}
.user-avatar{width:36px;height:36px;border-radius:8px;background:linear-gradient(135deg,var(--gold),var(--orange));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;color:#000}
.user-info{flex:1}
.user-info .name{font-size:13px;font-weight:600}
.user-info .role{font-size:10px;color:var(--gold)}
.logout-btn{background:none;border:none;color:var(--text-3);cursor:pointer;font-size:14px}
.main{flex:1;margin-left:260px;min-height:100vh}
.topbar{height:60px;background:var(--bg-1);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 24px;position:sticky;top:0;z-index:50}
.breadcrumb{font-size:13px;color:var(--text-2)}
.breadcrumb strong{color:var(--gold)}
.demo-badge{background:linear-gradient(135deg,var(--emerald),var(--cyan));color:#fff;padding:6px 12px;border-radius:16px;font-size:11px;font-weight:600}
.content{padding:24px}
.page{display:none}
.page.active{display:block}
.page-header{margin-bottom:24px}
.page-header h1{font-size:24px;font-weight:700;display:flex;align-items:center;gap:10px}
.page-header p{color:var(--text-2);font-size:13px;margin-top:4px}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.stat-card{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:20px}
.stat-card.gold{border-left:3px solid var(--gold)}
.stat-card.emerald{border-left:3px solid var(--emerald)}
.stat-card.amber{border-left:3px solid var(--amber)}
.stat-card.violet{border-left:3px solid var(--violet)}
.stat-card .label{font-size:12px;color:var(--text-3);margin-bottom:6px}
.stat-card .value{font-size:26px;font-weight:700}
.stat-card .change{font-size:11px;margin-top:6px;color:var(--emerald)}
.card{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;margin-bottom:20px}
.card-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.card-header h3{font-size:14px;font-weight:600}
.card-body{padding:20px}
.card-body.no-padding{padding:0}
.grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.btn{padding:10px 16px;border-radius:var(--radius);font-size:13px;font-weight:500;cursor:pointer;border:none}
.btn-gold{background:linear-gradient(135deg,var(--gold),var(--orange));color:#000}
.btn-secondary{background:var(--bg-3);color:var(--text-0);border:1px solid var(--border)}
table{width:100%;border-collapse:collapse}
th,td{text-align:left;padding:12px 16px;border-bottom:1px solid var(--border)}
th{font-size:11px;font-weight:600;color:var(--text-3);text-transform:uppercase;background:var(--bg-3)}
tbody tr:hover{background:var(--bg-3)}
.badge{display:inline-flex;padding:4px 8px;border-radius:6px;font-size:10px;font-weight:600}
.badge.active,.badge.won{background:rgba(16,185,129,.15);color:var(--emerald)}
.badge.lead,.badge.qualified{background:rgba(245,158,11,.15);color:var(--amber)}
.badge.proposal,.badge.negotiation{background:rgba(99,102,241,.15);color:var(--primary)}
.search-box{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:20px}
.search-row{display:flex;gap:12px}
.search-input{flex:1;padding:10px 14px;background:var(--bg-3);border:1px solid var(--border);border-radius:var(--radius);color:var(--text-0);font-size:13px}
.result-item{padding:14px 20px;border-bottom:1px solid var(--border);cursor:pointer}
.result-item:hover{background:var(--bg-3)}
.result-name{font-size:14px;font-weight:600;margin-bottom:4px}
.result-meta{font-size:12px;color:var(--text-3)}
.empty-state{text-align:center;padding:48px;color:var(--text-3)}
.empty-state .icon{font-size:40px;margin-bottom:12px;opacity:.5}
.chart-container{height:260px}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.8);display:none;align-items:center;justify-content:center;z-index:1000}
.modal-overlay.active{display:flex}
.modal{background:var(--bg-2);border:1px solid var(--border);border-radius:16px;width:100%;max-width:500px;max-height:90vh;overflow:hidden}
.modal-header{padding:20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.modal-header h2{font-size:16px}
.modal-close{background:none;border:none;color:var(--text-2);font-size:20px;cursor:pointer}
.modal-body{padding:20px;max-height:60vh;overflow-y:auto}
.modal-footer{padding:16px 20px;border-top:1px solid var(--border);display:flex;justify-content:flex-end;gap:12px}
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
<p>Enterprise Business Platform</p>
</div>
<div class="login-error" id="loginError">Ungültige Anmeldedaten</div>
<div class="form-group"><label>Benutzername</label><input type="text" class="form-input" id="loginUser" value="admin"></div>
<div class="form-group"><label>Passwort</label><input type="password" class="form-input" id="loginPass" onkeypress="if(event.key==='Enter')doLogin()"></div>
<button class="login-btn" onclick="doLogin()">🔐 Anmelden</button>
<div class="demo-link"><a href="/demo">🎮 Oder Demo starten →</a></div>
</div>
</div>

<div class="app" id="app">
<aside class="sidebar">
<div class="sidebar-header">
<div class="logo">
<div class="logo-icon">⚡</div>
<div class="logo-text"><h1>West Money OS</h1><span>v6.1 Ultimate</span></div>
</div>
</div>
<nav class="sidebar-nav">
<div class="nav-section">
<div class="nav-section-title">Übersicht</div>
<div class="nav-item active" data-page="dashboard"><span>📊</span>Dashboard<span class="badge gold">PRO</span></div>
</div>
<div class="nav-section">
<div class="nav-section-title">CRM</div>
<div class="nav-item" data-page="contacts"><span>👥</span>Kontakte</div>
<div class="nav-item" data-page="leads"><span>🎯</span>Leads</div>
<div class="nav-item" data-page="campaigns"><span>📧</span>Kampagnen</div>
</div>
<div class="nav-section">
<div class="nav-section-title">Daten & APIs</div>
<div class="nav-item" data-page="handelsregister"><span>🏛️</span>Handelsregister<span class="badge live">LIVE</span></div>
<div class="nav-item" data-page="explorium"><span>🔍</span>Explorium<span class="badge api">API</span></div>
</div>
<div class="nav-section">
<div class="nav-section-title">Enterprise</div>
<div class="nav-item" data-page="automations"><span>🤖</span>Broly Automations</div>
<div class="nav-item" data-page="einstein"><span>🏗️</span>Einstein Agency</div>
<div class="nav-item" data-page="gaming"><span>🎮</span>GTzMeta Gaming</div>
</div>
<div class="nav-section">
<div class="nav-section-title">FinTech</div>
<div class="nav-item" data-page="fintech"><span>💳</span>Wallet & Crypto</div>
<div class="nav-item" data-page="security"><span>🛡️</span>DedSec Security</div>
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
<div class="demo-badge" id="demoBadge" style="display:none">🎮 DEMO MODE</div>
</header>

<div class="content">
<!-- DASHBOARD -->
<div class="page active" id="page-dashboard">
<div class="page-header"><h1>📊 Dashboard</h1><p>Willkommen zurück!</p></div>
<div class="stats-grid">
<div class="stat-card gold"><div class="label">Umsatz</div><div class="value" id="statRevenue">€0</div><div class="change">↑ 28.5% vs. Vorjahr</div></div>
<div class="stat-card emerald"><div class="label">Leads</div><div class="value" id="statLeads">0</div><div class="change">↑ 22% diesen Monat</div></div>
<div class="stat-card amber"><div class="label">Kunden</div><div class="value" id="statCustomers">0</div><div class="change">↑ 18% dieses Jahr</div></div>
<div class="stat-card violet"><div class="label">MRR</div><div class="value" id="statMRR">€0</div><div class="change">↑ 12.4%</div></div>
</div>
<div class="grid-2">
<div class="card"><div class="card-header"><h3>📈 Umsatzentwicklung</h3></div><div class="card-body"><div class="chart-container"><canvas id="revenueChart"></canvas></div></div></div>
<div class="card"><div class="card-header"><h3>📊 MRR</h3></div><div class="card-body"><div class="chart-container"><canvas id="mrrChart"></canvas></div></div></div>
</div>
</div>

<!-- CONTACTS -->
<div class="page" id="page-contacts">
<div class="page-header"><h1>👥 Kontakte</h1><p>Alle Kontakte verwalten</p></div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Name</th><th>E-Mail</th><th>Unternehmen</th><th>Quelle</th><th>Status</th></tr></thead><tbody id="contactsTable"></tbody></table></div></div>
</div>

<!-- LEADS -->
<div class="page" id="page-leads">
<div class="page-header"><h1>🎯 Leads</h1><p>Pipeline Management</p></div>
<div class="stats-grid">
<div class="stat-card gold"><div class="label">Pipeline Wert</div><div class="value" id="pipelineValue">€0</div></div>
<div class="stat-card emerald"><div class="label">Gewichteter Wert</div><div class="value" id="weightedValue">€0</div></div>
</div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Projekt</th><th>Unternehmen</th><th>Wert</th><th>Phase</th><th>%</th></tr></thead><tbody id="leadsTable"></tbody></table></div></div>
</div>

<!-- CAMPAIGNS -->
<div class="page" id="page-campaigns">
<div class="page-header"><h1>📧 Kampagnen</h1></div>
<div class="card"><div class="card-body no-padding"><table><thead><tr><th>Kampagne</th><th>Versendet</th><th>Geöffnet</th><th>Geklickt</th><th>Status</th></tr></thead><tbody id="campaignsTable"></tbody></table></div></div>
</div>

<!-- HANDELSREGISTER -->
<div class="page" id="page-handelsregister">
<div class="page-header"><h1>🏛️ Handelsregister</h1><p>LIVE Firmendaten aus dem deutschen Handelsregister</p></div>
<div class="search-box"><div class="search-row"><input type="text" class="search-input" id="hrQuery" placeholder="🔍 Firmenname eingeben..." onkeypress="if(event.key==='Enter')searchHR()"><button class="btn btn-gold" onclick="searchHR()">Suchen</button></div></div>
<div class="card"><div class="card-header"><h3>Suchergebnisse</h3><span id="hrResultCount">0 Treffer</span></div><div class="card-body no-padding" id="hrResults"><div class="empty-state"><div class="icon">🏛️</div><p>Suche starten</p></div></div></div>
</div>

<!-- EXPLORIUM -->
<div class="page" id="page-explorium">
<div class="page-header"><h1>🔍 Explorium</h1><p>B2B Data Enrichment</p></div>
<div class="stats-grid">
<div class="stat-card gold"><div class="label">Credits</div><div class="value" id="expCredits">0</div></div>
<div class="stat-card emerald"><div class="label">Plan</div><div class="value" id="expPlan">-</div></div>
</div>
</div>

<!-- AUTOMATIONS -->
<div class="page" id="page-automations">
<div class="page-header"><h1>🤖 Broly Automations</h1><p>Building Automation & Smart Home</p></div>
<div class="stats-grid">
<div class="stat-card gold"><div class="label">Aktive Systeme</div><div class="value" id="autoSystems">0</div></div>
<div class="stat-card emerald"><div class="label">Geräte</div><div class="value" id="autoDevices">0</div></div>
<div class="stat-card amber"><div class="label">Energie gespart</div><div class="value" id="autoEnergy">0 kWh</div></div>
</div>
</div>

<!-- EINSTEIN -->
<div class="page" id="page-einstein">
<div class="page-header"><h1>🏗️ Einstein Agency</h1><p>Architektur & Smart Home Planung</p></div>
<div class="card"><div class="card-body"><p>Projekte, Designs und Planungen - alles in einer Übersicht.</p></div></div>
</div>

<!-- GAMING -->
<div class="page" id="page-gaming">
<div class="page-header"><h1>🎮 GTzMeta Gaming</h1><p>Streaming & Content</p></div>
<div class="stats-grid">
<div class="stat-card violet"><div class="label">Twitch Followers</div><div class="value" id="gamingTwitch">0</div></div>
<div class="stat-card rose"><div class="label">YouTube Subs</div><div class="value" id="gamingYoutube">0</div></div>
<div class="stat-card cyan"><div class="label">Discord</div><div class="value" id="gamingDiscord">0</div></div>
<div class="stat-card gold"><div class="label">Peak Viewers</div><div class="value" id="gamingPeak">0</div></div>
</div>
</div>

<!-- FINTECH -->
<div class="page" id="page-fintech">
<div class="page-header"><h1>💳 Wallet & Crypto</h1></div>
<div class="card"><div class="card-body"><p>Wallet Balance, Crypto Holdings und Transaktionen.</p></div></div>
</div>

<!-- SECURITY -->
<div class="page" id="page-security">
<div class="page-header"><h1>🛡️ DedSec Security</h1></div>
<div class="stats-grid">
<div class="stat-card emerald"><div class="label">Threats Blocked</div><div class="value" id="secThreats">0</div></div>
<div class="stat-card gold"><div class="label">Systems</div><div class="value" id="secSystems">0</div></div>
<div class="stat-card cyan"><div class="label">Uptime</div><div class="value" id="secUptime">0%</div></div>
<div class="stat-card violet"><div class="label">Score</div><div class="value" id="secScore">0</div></div>
</div>
</div>
</div>
</main>
</div>

<div class="modal-overlay" id="modal"><div class="modal"><div class="modal-header"><h2 id="modalTitle">Modal</h2><button class="modal-close" onclick="closeModal()">&times;</button></div><div class="modal-body" id="modalBody"></div><div class="modal-footer" id="modalFooter"></div></div></div>

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
        else { document.getElementById('loginError').classList.add('show'); }
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
        document.getElementById('currentPage').textContent = item.textContent.trim().split(' ')[0];
    });
});

async function loadAllData() {
    await Promise.all([loadDashboard(), loadContacts(), loadLeads(), loadCampaigns(), loadExplorium(), loadGaming(), loadAutomations(), loadSecurity()]);
}

async function loadDashboard() {
    try {
        const [stats, charts] = await Promise.all([fetch('/api/dashboard/stats').then(r=>r.json()), fetch('/api/dashboard/charts').then(r=>r.json())]);
        document.getElementById('statRevenue').textContent = '€' + stats.revenue.toLocaleString('de-DE');
        document.getElementById('statLeads').textContent = stats.leads;
        document.getElementById('statCustomers').textContent = stats.customers;
        document.getElementById('statMRR').textContent = '€' + stats.mrr.toLocaleString('de-DE');
        if (revenueChart) revenueChart.destroy();
        revenueChart = new Chart(document.getElementById('revenueChart'), {type:'line', data:{labels:charts.labels, datasets:[{label:'Umsatz', data:charts.revenue, borderColor:'#fbbf24', backgroundColor:'rgba(251,191,36,0.1)', fill:true, tension:0.4}]}, options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}}});
        if (mrrChart) mrrChart.destroy();
        mrrChart = new Chart(document.getElementById('mrrChart'), {type:'line', data:{labels:charts.labels, datasets:[{label:'MRR', data:charts.mrr, borderColor:'#8b5cf6', backgroundColor:'rgba(139,92,246,0.1)', fill:true, tension:0.4}]}, options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}}});
    } catch(e) {}
}

async function loadContacts() {
    try {
        const contacts = await fetch('/api/contacts').then(r=>r.json());
        document.getElementById('contactsTable').innerHTML = contacts.map(c => '<tr><td><strong>'+esc(c.name)+'</strong></td><td>'+esc(c.email)+'</td><td>'+esc(c.company)+'</td><td>'+esc(c.source)+'</td><td><span class="badge '+c.status+'">'+c.status+'</span></td></tr>').join('');
    } catch(e) {}
}

async function loadLeads() {
    try {
        const leads = await fetch('/api/leads').then(r=>r.json());
        const total = leads.reduce((s,l)=>s+l.value, 0);
        const weighted = leads.reduce((s,l)=>s+(l.value*l.probability/100), 0);
        document.getElementById('pipelineValue').textContent = '€' + total.toLocaleString('de-DE');
        document.getElementById('weightedValue').textContent = '€' + Math.round(weighted).toLocaleString('de-DE');
        document.getElementById('leadsTable').innerHTML = leads.map(l => '<tr><td><strong>'+esc(l.name)+'</strong></td><td>'+esc(l.company)+'</td><td>€'+l.value.toLocaleString('de-DE')+'</td><td><span class="badge '+l.stage+'">'+l.stage+'</span></td><td>'+l.probability+'%</td></tr>').join('');
    } catch(e) {}
}

async function loadCampaigns() {
    try {
        const campaigns = await fetch('/api/campaigns').then(r=>r.json());
        document.getElementById('campaignsTable').innerHTML = campaigns.map(c => '<tr><td><strong>'+esc(c.name)+'</strong></td><td>'+c.sent+'</td><td>'+c.opened+'</td><td>'+c.clicked+'</td><td><span class="badge '+c.status+'">'+c.status+'</span></td></tr>').join('');
    } catch(e) {}
}

async function loadExplorium() {
    try {
        const data = await fetch('/api/explorium/stats').then(r=>r.json());
        document.getElementById('expCredits').textContent = data.credits;
        document.getElementById('expPlan').textContent = data.plan;
    } catch(e) {}
}

async function loadGaming() {
    try {
        const data = await fetch('/api/gaming/stats').then(r=>r.json());
        document.getElementById('gamingTwitch').textContent = data.twitch_followers?.toLocaleString('de-DE') || '0';
        document.getElementById('gamingYoutube').textContent = data.youtube_subs?.toLocaleString('de-DE') || '0';
        document.getElementById('gamingDiscord').textContent = data.discord_members?.toLocaleString('de-DE') || '0';
        document.getElementById('gamingPeak').textContent = data.peak_viewers?.toLocaleString('de-DE') || '0';
    } catch(e) {}
}

async function loadAutomations() {
    try {
        const data = await fetch('/api/automations/stats').then(r=>r.json());
        document.getElementById('autoSystems').textContent = data.active_systems || '0';
        document.getElementById('autoDevices').textContent = data.devices_connected?.toLocaleString('de-DE') || '0';
        document.getElementById('autoEnergy').textContent = (data.energy_saved_kwh?.toLocaleString('de-DE') || '0') + ' kWh';
    } catch(e) {}
}

async function loadSecurity() {
    try {
        const data = await fetch('/api/security/stats').then(r=>r.json());
        document.getElementById('secThreats').textContent = data.threats_blocked?.toLocaleString('de-DE') || '0';
        document.getElementById('secSystems').textContent = data.systems_protected || '0';
        document.getElementById('secUptime').textContent = (data.uptime_percent || '0') + '%';
        document.getElementById('secScore').textContent = (data.security_score || '0') + '/100';
    } catch(e) {}
}

async function searchHR() {
    const q = document.getElementById('hrQuery').value.trim();
    if (!q) return alert('Bitte Suchbegriff eingeben');
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

function closeModal() { document.getElementById('modal').classList.remove('active'); }
function esc(s) { return s ? String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') : ''; }
document.addEventListener('keydown', e => { if(e.key==='Escape') closeModal(); });
checkAuth();
</script>
</body>
</html>'''

if __name__ == '__main__':
    print("=" * 70)
    print("  ⚡ WEST MONEY OS v6.1 - ULTIMATE ENTERPRISE EDITION")
    print("=" * 70)
    print(f"  🌐 Landing: http://localhost:{PORT}")
    print(f"  💳 Pricing: http://localhost:{PORT}/pricing")
    print(f"  🎮 Demo:    http://localhost:{PORT}/demo")
    print(f"  📊 App:     http://localhost:{PORT}/app")
    print("=" * 70)
    print(f"  🔑 Login: admin / 663724")
    print(f"  🎮 Demo:  demo / demo123")
    print("=" * 70)
    app.run(host='0.0.0.0', port=PORT, debug=False)
