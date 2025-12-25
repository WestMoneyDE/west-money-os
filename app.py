#!/usr/bin/env python3
from flask import Flask, render_template_string, jsonify, request, redirect, url_for, session
from flask_cors import CORS
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
import os, requests, hashlib, sqlite3

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'westmoney-v15-369')
CORS(app)

CONFIG = {'HUBSPOT_API_KEY': os.getenv('HUBSPOT_API_KEY', ''), 'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY', ''), 'SEVDESK_API_KEY': os.getenv('SEVDESK_API_KEY', ''), 'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', '')}

def get_db():
    conn = sqlite3.connect('westmoney.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT DEFAULT "user")')
    c.execute('CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, name TEXT, client TEXT, status TEXT DEFAULT "planning", progress INTEGER DEFAULT 0, value REAL DEFAULT 0, project_type TEXT, location TEXT, start_date DATE, end_date DATE)')
    admin_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    c.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)', ('admin', admin_hash, 'admin'))
    projects = [('Villa Mueller Smart Home', 'Familie Mueller', 'active', 75, 185000, 'LOXONE', 'Frankfurt', '2024-09-15', '2025-02-28'),
        ('Buerokomplex TechPark', 'TechCorp GmbH', 'active', 45, 420000, 'KNX', 'Muenchen', '2024-11-01', '2025-06-30'),
        ('Penthouse Westend', 'Dr. Schmidt', 'planning', 15, 95000, 'LOXONE', 'Frankfurt', '2025-01-15', '2025-04-30'),
        ('Mehrfamilienhaus Gruenwald', 'Immobilien AG', 'active', 60, 380000, 'LOXONE', 'Muenchen', '2024-08-01', '2025-03-15'),
        ('Smart Office Duesseldorf', 'FinanceHub', 'completed', 100, 156000, 'KNX', 'Duesseldorf', '2024-03-01', '2024-10-30'),
        ('Wellness Center Spa', 'Wellness GmbH', 'active', 30, 245000, 'LOXONE', 'Baden-Baden', '2024-12-01', '2025-08-15')]
    for p in projects:
        c.execute('INSERT OR IGNORE INTO projects (name,client,status,progress,value,project_type,location,start_date,end_date) SELECT ?,?,?,?,?,?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM projects WHERE name=?)', (*p, p[0]))
    conn.commit()
    conn.close()

class HubSpotAPI:
    def __init__(self):
        self.api_key = CONFIG['HUBSPOT_API_KEY']
        self.headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
    def get_contacts(self, limit=100):
        if not self.api_key: return []
        try:
            r = requests.get('https://api.hubapi.com/crm/v3/objects/contacts', headers=self.headers, params={'limit': limit, 'properties': 'firstname,lastname,email,phone,company,hs_lead_status,hs_whatsapp_consent'}, timeout=10)
            return r.json().get('results', []) if r.ok else []
        except: return []
    def get_deals(self, limit=100):
        if not self.api_key: return []
        try:
            r = requests.get('https://api.hubapi.com/crm/v3/objects/deals', headers=self.headers, params={'limit': limit, 'properties': 'dealname,amount,dealstage'}, timeout=10)
            return r.json().get('results', []) if r.ok else []
        except: return []
    def bulk_update_consent(self, ids, status):
        results = {'success': 0, 'failed': 0}
        for cid in ids:
            try:
                r = requests.patch(f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}', headers=self.headers, json={'properties': {'hs_whatsapp_consent': status}}, timeout=10)
                if r.ok: results['success'] += 1
                else: results['failed'] += 1
            except: results['failed'] += 1
        return results

class StripeAPI:
    def __init__(self):
        self.api_key = CONFIG['STRIPE_SECRET_KEY']
        self.headers = {'Authorization': f'Bearer {self.api_key}'}
    def get_balance(self):
        if not self.api_key: return 0
        try:
            r = requests.get('https://api.stripe.com/v1/balance', headers=self.headers, timeout=10)
            return next((b['amount']/100 for b in r.json().get('available', []) if b.get('currency') == 'eur'), 0)
        except: return 0
    def get_revenue(self):
        if not self.api_key: return 0
        try:
            r = requests.get('https://api.stripe.com/v1/payment_intents', headers=self.headers, params={'limit': 100}, timeout=10)
            return sum(p.get('amount', 0)/100 for p in r.json().get('data', []) if p.get('status') == 'succeeded')
        except: return 0

class SevDeskAPI:
    def __init__(self):
        self.api_key = CONFIG['SEVDESK_API_KEY']
        self.headers = {'Authorization': self.api_key}
    def get_invoices(self, limit=100):
        if not self.api_key: return []
        try:
            r = requests.get('https://my.sevdesk.de/api/v1/Invoice', headers=self.headers, params={'limit': limit}, timeout=10)
            return r.json().get('objects', [])
        except: return []
    def get_total(self):
        return sum(float(i.get('sumGross', 0)) for i in self.get_invoices(500))

class ClaudeAPI:
    def __init__(self):
        self.api_key = CONFIG['ANTHROPIC_API_KEY']
        self.headers = {'x-api-key': self.api_key, 'Content-Type': 'application/json', 'anthropic-version': '2023-06-01'}
    def chat(self, message, system=None):
        if not self.api_key: return "API Key nicht konfiguriert."
        try:
            data = {'model': 'claude-sonnet-4-20250514', 'max_tokens': 2048, 'messages': [{'role': 'user', 'content': message}]}
            if system: data['system'] = system
            r = requests.post('https://api.anthropic.com/v1/messages', headers=self.headers, json=data, timeout=60)
            return r.json()['content'][0]['text'] if r.ok else f"Error: {r.status_code}"
        except Exception as e: return str(e)

hubspot = HubSpotAPI()
stripe_api = StripeAPI()
sevdesk = SevDeskAPI()
claude = ClaudeAPI()

LEADS = [{"id": 1, "name": "Thomas Moser", "company": "Loxone Electronics", "position": "Gruender", "score": 96, "stage": "contacted", "value": 500000},
    {"id": 2, "name": "Martin Oeller", "company": "Loxone Electronics", "position": "Gruender", "score": 96, "stage": "contacted", "value": 500000},
    {"id": 3, "name": "Ruediger Keinberger", "company": "Loxone Electronics", "position": "CEO", "score": 95, "stage": "contacted", "value": 450000},
    {"id": 4, "name": "Dr. Michael Maxelon", "company": "Mainova AG", "position": "Vorstand", "score": 95, "stage": "qualified", "value": 380000},
    {"id": 5, "name": "Max Hofmann", "company": "Hofmann Bau AG", "position": "Vorstand", "score": 94, "stage": "won", "value": 345000},
    {"id": 6, "name": "Frank Junker", "company": "ABG Frankfurt", "position": "GF", "score": 92, "stage": "proposal", "value": 420000},
    {"id": 7, "name": "Anna Mueller", "company": "Smart Home Bayern", "position": "GF", "score": 91, "stage": "won", "value": 156000},
    {"id": 8, "name": "Tino Kugler", "company": "Loxone Deutschland", "position": "MD", "score": 90, "stage": "negotiation", "value": 220000}]

PREDICTIONS = [{"type": "conversion", "lead": "Thomas Moser", "prediction": "87% Wahrscheinlichkeit", "confidence": 87},
    {"type": "deal", "lead": "Hofmann Bau AG", "prediction": "Q1 2026 Abschluss", "confidence": 92},
    {"type": "upsell", "lead": "Mainova AG", "prediction": "150k PV-Integration", "confidence": 78}]

DEDSEC = [{"name": "Command Tower Frankfurt", "status": "online", "details": "24 Cameras"},
    {"name": "Patrol Drone Alpha", "status": "active", "details": "Battery: 87%"},
    {"name": "Patrol Drone Beta", "status": "charging", "details": "Battery: 23%"},
    {"name": "Cyber Shield Main", "status": "active", "details": "1247 blocked"}]

PV_PARTNERS = [{"name": "1Komma5", "logo": "T", "type": "Premium", "commission": "8%", "rating": 4.8},
    {"name": "Enpal", "logo": "S", "type": "Strategic", "commission": "6%", "rating": 4.6},
    {"name": "Zolar", "logo": "Z", "type": "Online", "commission": "5%", "rating": 4.5},
    {"name": "Solarwatt", "logo": "B", "type": "Premium", "commission": "7%", "rating": 4.9}]

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'): return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

BASE = '''<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{ title }} - West Money OS v15.369</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"><script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;background:#0a0a0a;color:#fff;min-height:100vh}.sidebar{position:fixed;left:0;top:0;width:250px;height:100vh;background:linear-gradient(180deg,#1a1a2e,#0f0f1a);border-right:1px solid rgba(255,255,255,0.1);padding:16px;overflow-y:auto;z-index:1000}.logo{display:flex;align-items:center;gap:10px;padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:16px}.logo-icon{width:38px;height:38px;background:linear-gradient(135deg,#FF5722,#FF9800);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px}.logo-text{font-size:16px;font-weight:700;background:linear-gradient(90deg,#FF5722,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.logo-version{font-size:9px;color:rgba(255,255,255,0.4)}.nav-section{margin-bottom:16px}.nav-title{font-size:9px;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.3);margin-bottom:8px;padding-left:10px}.nav-item{display:flex;align-items:center;gap:8px;padding:9px 10px;border-radius:6px;color:rgba(255,255,255,0.7);text-decoration:none;font-size:13px;transition:all 0.2s;margin-bottom:2px}.nav-item:hover{background:rgba(255,87,34,0.1);color:#FF5722}.nav-item.active{background:linear-gradient(90deg,rgba(255,87,34,0.2),transparent);color:#FF5722;border-left:2px solid #FF5722}.nav-icon{width:16px;text-align:center;font-size:12px}.main{margin-left:250px;padding:20px;min-height:100vh}.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}.page-title{font-size:22px;font-weight:700}.page-sub{color:rgba(255,255,255,0.5);font-size:12px;margin-top:2px}.card{background:linear-gradient(135deg,#1a1a2e,#0f0f1a);border-radius:10px;padding:16px;border:1px solid rgba(255,255,255,0.08);margin-bottom:16px}.btn{padding:8px 16px;border-radius:6px;font-weight:600;font-size:12px;cursor:pointer;border:none;transition:all 0.2s;text-decoration:none;display:inline-flex;align-items:center;gap:5px}.btn-primary{background:linear-gradient(90deg,#FF5722,#FF9800);color:white}.btn-primary:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(255,87,34,0.4)}.btn-secondary{background:rgba(255,255,255,0.1);color:white;border:1px solid rgba(255,255,255,0.2)}.btn-success{background:#4CAF50;color:white}.btn-danger{background:#f44336;color:white}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px}.stat{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:10px;padding:16px;border:1px solid rgba(255,255,255,0.08)}.stat-value{font-size:26px;font-weight:700}.stat-label{color:rgba(255,255,255,0.5);font-size:11px;margin-top:2px}.stat-change{font-size:10px;margin-top:2px}.stat-change.up{color:#4CAF50}table{width:100%;border-collapse:collapse}th,td{padding:10px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.05)}th{font-size:10px;text-transform:uppercase;letter-spacing:0.5px;color:rgba(255,255,255,0.4);font-weight:500}.badge{padding:3px 8px;border-radius:10px;font-size:10px;font-weight:500}.badge-success{background:rgba(76,175,80,0.2);color:#4CAF50}.badge-warning{background:rgba(255,152,0,0.2);color:#FF9800}.badge-danger{background:rgba(244,67,54,0.2);color:#f44336}.badge-info{background:rgba(33,150,243,0.2);color:#2196F3}.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}input,select,textarea{width:100%;padding:10px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:6px;color:white;font-size:13px}input:focus,select:focus{outline:none;border-color:#FF5722}.progress{background:rgba(255,255,255,0.1);border-radius:8px;height:6px;overflow:hidden}.progress-bar{height:100%;border-radius:8px;background:linear-gradient(90deg,#FF5722,#FF9800)}@media(max-width:1200px){.stats{grid-template-columns:repeat(2,1fr)}}@media(max-width:768px){.sidebar{width:100%;height:auto;position:relative}.main{margin-left:0}.stats{grid-template-columns:1fr}}</style></head>
<body><nav class="sidebar"><div class="logo"><div class="logo-icon">W</div><div><div class="logo-text">West Money</div><div class="logo-version">OS v15.369</div></div></div>
<div class="nav-section"><div class="nav-title">Main</div><a href="/dashboard" class="nav-item {{ 'active' if active_page == 'dashboard' else '' }}"><span class="nav-icon">D</span> Dashboard</a><a href="/leads" class="nav-item {{ 'active' if active_page == 'leads' else '' }}"><span class="nav-icon">L</span> Leads</a><a href="/contacts" class="nav-item {{ 'active' if active_page == 'contacts' else '' }}"><span class="nav-icon">C</span> Kontakte</a><a href="/projects" class="nav-item {{ 'active' if active_page == 'projects' else '' }}"><span class="nav-icon">P</span> Projekte</a><a href="/invoices" class="nav-item {{ 'active' if active_page == 'invoices' else '' }}"><span class="nav-icon">I</span> Rechnungen</a></div>
<div class="nav-section"><div class="nav-title">Einstein AI</div><a href="/einstein" class="nav-item {{ 'active' if active_page == 'einstein' else '' }}"><span class="nav-icon">E</span> Einstein Home</a><a href="/einstein/predictions" class="nav-item {{ 'active' if active_page == 'predictions' else '' }}"><span class="nav-icon">P</span> Predictions</a><a href="/einstein/analytics" class="nav-item {{ 'active' if active_page == 'analytics' else '' }}"><span class="nav-icon">A</span> Analytics</a><a href="/einstein/insights" class="nav-item {{ 'active' if active_page == 'insights' else '' }}"><span class="nav-icon">I</span> Insights</a></div>
<div class="nav-section"><div class="nav-title">Photovoltaik</div><a href="/pv" class="nav-item {{ 'active' if active_page == 'pv' else '' }}"><span class="nav-icon">S</span> PV Home</a><a href="/pv/partners" class="nav-item {{ 'active' if active_page == 'pv_partners' else '' }}"><span class="nav-icon">P</span> Partner</a><a href="/pv/calculator" class="nav-item {{ 'active' if active_page == 'pv_calc' else '' }}"><span class="nav-icon">R</span> PV Rechner</a></div>
<div class="nav-section"><div class="nav-title">DedSec Security</div><a href="/dedsec" class="nav-item {{ 'active' if active_page == 'dedsec' else '' }}"><span class="nav-icon">S</span> Security Hub</a><a href="/dedsec/tower" class="nav-item {{ 'active' if active_page == 'tower' else '' }}"><span class="nav-icon">T</span> Tower</a><a href="/dedsec/drones" class="nav-item {{ 'active' if active_page == 'drones' else '' }}"><span class="nav-icon">D</span> Drones</a><a href="/dedsec/cctv" class="nav-item {{ 'active' if active_page == 'cctv' else '' }}"><span class="nav-icon">C</span> CCTV</a></div>
<div class="nav-section"><div class="nav-title">Tools</div><a href="/whatsapp" class="nav-item {{ 'active' if active_page == 'whatsapp' else '' }}"><span class="nav-icon">W</span> WhatsApp</a><a href="/whatsapp/consent" class="nav-item {{ 'active' if active_page == 'consent' else '' }}"><span class="nav-icon">C</span> Consent</a><a href="/godbot" class="nav-item {{ 'active' if active_page == 'godbot' else '' }}"><span class="nav-icon">G</span> GOD BOT</a><a href="/locker" class="nav-item {{ 'active' if active_page == 'locker' else '' }}"><span class="nav-icon">L</span> Locker</a></div>
<div class="nav-section"><div class="nav-title">System</div><a href="/settings" class="nav-item {{ 'active' if active_page == 'settings' else '' }}"><span class="nav-icon">S</span> Settings</a><a href="/sync" class="nav-item {{ 'active' if active_page == 'sync' else '' }}"><span class="nav-icon">R</span> API Sync</a><a href="/logout" class="nav-item"><span class="nav-icon">X</span> Logout</a></div></nav>
<main class="main">{{ content|safe }}</main></body></html>'''

def render_page(content, **kwargs):
    rendered = render_template_string(content, **kwargs)
    return render_template_string(BASE, content=rendered, **kwargs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username=? AND password_hash=?', (username, password_hash)).fetchone()
        conn.close()
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
    return render_template_string('''<!DOCTYPE html><html><head><title>Login - West Money OS</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;background:linear-gradient(135deg,#0a0a0a,#1a1a2e);min-height:100vh;display:flex;align-items:center;justify-content:center}.box{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:40px;width:100%;max-width:380px}.logo{text-align:center;margin-bottom:30px}.logo-icon{font-size:48px;margin-bottom:10px}.logo-text{font-size:24px;font-weight:700;background:linear-gradient(90deg,#FF5722,#FF9800);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.form-group{margin-bottom:20px}label{display:block;color:rgba(255,255,255,0.7);margin-bottom:8px;font-size:14px}input{width:100%;padding:12px 16px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:8px;color:white;font-size:14px}input:focus{outline:none;border-color:#FF5722}button{width:100%;padding:14px;background:linear-gradient(90deg,#FF5722,#FF9800);border:none;border-radius:8px;color:white;font-size:16px;font-weight:600;cursor:pointer}button:hover{transform:translateY(-2px)}.version{text-align:center;margin-top:20px;color:rgba(255,255,255,0.3);font-size:12px}</style></head><body><div class="box"><div class="logo"><div class="logo-icon">W</div><div class="logo-text">West Money OS</div></div><form method="POST"><div class="form-group"><label>Benutzername</label><input type="text" name="username" required placeholder="admin"></div><div class="form-group"><label>Passwort</label><input type="password" name="password" required placeholder="********"></div><button type="submit">Anmelden</button></form><div class="version">v15.369 Ultimate Edition</div></div></body></html>''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('dashboard') if session.get('logged_in') else url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        hs_contacts = hubspot.get_contacts(500)
        hs_deals = hubspot.get_deals(500)
        stripe_rev = stripe_api.get_revenue()
        sevdesk_total = sevdesk.get_total()
        total_contacts = len(hs_contacts) or 247
        total_deals = len(hs_deals) or 59
        total_revenue = (stripe_rev + sevdesk_total) or 847234
        pipeline = sum(float(d.get('properties', {}).get('amount', 0) or 0) for d in hs_deals) or 3600000
    except:
        total_contacts, total_deals, total_revenue, pipeline = 247, 59, 847234, 3600000
    content = f'''<div class="header"><div><h1 class="page-title">Dashboard</h1><p class="page-sub">Willkommen, {session.get("username", "Admin")}</p></div><div style="display:flex;gap:10px"><a href="/einstein/predictions" class="btn btn-primary">Einstein Predictions</a><a href="/sync" class="btn btn-secondary">Sync</a></div></div>
<div class="stats"><div class="stat" style="border-left:3px solid #FF5722"><div class="stat-value" style="color:#FF5722">EUR {pipeline:,.0f}</div><div class="stat-label">Pipeline Value</div><div class="stat-change up">+23.5%</div></div><div class="stat" style="border-left:3px solid #FF9800"><div class="stat-value" style="color:#FF9800">{total_deals}</div><div class="stat-label">Aktive Leads</div><div class="stat-change up">+12</div></div><div class="stat" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">87%</div><div class="stat-label">Conversion Rate</div><div class="stat-change up">+5.2%</div></div><div class="stat" style="border-left:3px solid #2196F3"><div class="stat-value" style="color:#2196F3">EUR {total_revenue:,.0f}</div><div class="stat-label">Umsatz 2024</div><div class="stat-change up">+23.5%</div></div></div>
<div class="grid-2"><div class="card"><h3 style="margin-bottom:16px">Pipeline Overview</h3><canvas id="chart" height="200"></canvas></div><div class="card" style="border:1px solid rgba(255,152,0,0.3)"><h3 style="margin-bottom:16px">Einstein Insights</h3><div style="padding:12px;background:rgba(255,255,255,0.05);border-radius:8px;margin-bottom:12px"><div style="font-size:11px;color:rgba(255,255,255,0.5)">Top Prediction</div><div style="font-weight:600">Thomas Moser - 87% Conversion</div></div><div style="padding:12px;background:rgba(255,255,255,0.05);border-radius:8px;margin-bottom:12px"><div style="font-size:11px;color:rgba(255,255,255,0.5)">Empfehlung</div><div style="font-weight:600">Kontaktiere Mainova AG</div></div><a href="/einstein/predictions" class="btn btn-primary" style="width:100%;justify-content:center">Alle Predictions</a></div></div>
<script>new Chart(document.getElementById('chart'),{{type:'bar',data:{{labels:['New','Contacted','Qualified','Proposal','Negotiation','Won'],datasets:[{{data:[11,7,5,4,5,3],backgroundColor:['#2196F3','#9C27B0','#FF9800','#FF5722','#E91E63','#4CAF50'],borderRadius:6}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,0.05)'}}}},x:{{grid:{{display:false}}}}}}}}}});</script>'''
    return render_page(content, title="Dashboard", active_page="dashboard")

@app.route('/leads')
@login_required
def leads():
    hs = hubspot.get_contacts(100)
    leads_list = [{"id": c.get('id'), "name": f"{c.get('properties',{}).get('firstname','')} {c.get('properties',{}).get('lastname','')}".strip() or 'Unbekannt', "company": c.get('properties',{}).get('company','-'), "position": c.get('properties',{}).get('jobtitle','-'), "score": 85, "stage": c.get('properties',{}).get('hs_lead_status','new'), "value": 100000} for c in hs] if hs else LEADS
    total = sum(l.get('value',0) for l in leads_list)
    rows = ''
    for l in leads_list[:20]:
        sc = '#4CAF50' if l['score']>=90 else '#FF9800' if l['score']>=70 else '#f44336'
        stc = {'new':'#2196F3','contacted':'#9C27B0','qualified':'#FF9800','proposal':'#FF5722','negotiation':'#E91E63','won':'#4CAF50'}.get(l['stage'],'#666')
        rows += f'<tr><td><span style="background:{sc};color:white;padding:4px 10px;border-radius:20px;font-size:11px">{l["score"]}</span></td><td style="font-weight:500">{l["name"]}</td><td style="color:rgba(255,255,255,0.7)">{l["company"]}</td><td style="color:rgba(255,255,255,0.7)">{l["position"]}</td><td><span class="badge" style="background:{stc}22;color:{stc}">{l["stage"]}</span></td><td>EUR {l["value"]:,}</td></tr>'
    content = f'''<div class="header"><div><h1 class="page-title">Lead Management</h1><p class="page-sub">{len(leads_list)} Leads | Pipeline: EUR {total:,.0f}</p></div><div style="display:flex;gap:10px"><button class="btn btn-secondary">Import</button><button class="btn btn-primary">+ Neuer Lead</button></div></div><div class="card"><table><thead><tr><th>Score</th><th>Name</th><th>Unternehmen</th><th>Position</th><th>Stage</th><th>Value</th></tr></thead><tbody>{rows}</tbody></table></div>'''
    return render_page(content, title="Leads", active_page="leads")

@app.route('/contacts')
@login_required
def contacts():
    hs = hubspot.get_contacts(200)
    rows = ''
    for c in hs[:30]:
        p = c.get('properties',{})
        name = f"{p.get('firstname','')} {p.get('lastname','')}".strip() or 'Unbekannt'
        consent = p.get('hs_whatsapp_consent','unknown')
        cb = {'granted':('Erteilt','badge-success'),'revoked':('Widerrufen','badge-danger')}.get(consent,('Unbekannt','badge-warning'))
        rows += f'<tr><td style="font-weight:500">{name}</td><td style="color:rgba(255,255,255,0.7)">{p.get("email","-")}</td><td style="color:rgba(255,255,255,0.7)">{p.get("phone","-")}</td><td style="color:rgba(255,255,255,0.7)">{p.get("company","-")}</td><td><span class="badge {cb[1]}">{cb[0]}</span></td></tr>'
    content = f'''<div class="header"><div><h1 class="page-title">Kontakte</h1><p class="page-sub">{len(hs)} Kontakte aus HubSpot</p></div><div style="display:flex;gap:10px"><a href="/sync" class="btn btn-secondary">Sync</a><button class="btn btn-primary">+ Neu</button></div></div><div class="card"><table><thead><tr><th>Name</th><th>Email</th><th>Telefon</th><th>Unternehmen</th><th>WhatsApp</th></tr></thead><tbody>{rows}</tbody></table></div>'''
    return render_page(content, title="Kontakte", active_page="contacts")

@app.route('/projects')
@login_required
def projects():
    conn = get_db()
    plist = conn.execute('SELECT * FROM projects ORDER BY id DESC').fetchall()
    conn.close()
    total = sum(p['value'] for p in plist)
    active = len([p for p in plist if p['status']=='active'])
    cards = ''
    for p in plist:
        sc = {'active':('#4CAF50','In Arbeit'),'planning':('#FF9800','Planung'),'completed':('#2196F3','Abgeschlossen')}.get(p['status'],('#666',p['status']))
        cards += f'''<div class="card"><div style="display:flex;justify-content:space-between;margin-bottom:12px"><div><h3 style="font-size:15px;margin-bottom:4px">{p['name']}</h3><p style="color:rgba(255,255,255,0.5);font-size:12px">{p['client']} - {p['location']}</p></div><span class="badge" style="background:{sc[0]}22;color:{sc[0]}">{sc[1]}</span></div><div style="display:flex;gap:10px;margin-bottom:12px"><div style="background:rgba(255,255,255,0.05);padding:6px 10px;border-radius:6px"><div style="font-size:9px;color:rgba(255,255,255,0.4)">SYSTEM</div><div style="font-weight:600;color:#FF5722">{p['project_type']}</div></div><div style="background:rgba(255,255,255,0.05);padding:6px 10px;border-radius:6px"><div style="font-size:9px;color:rgba(255,255,255,0.4)">WERT</div><div style="font-weight:600">EUR {p['value']:,}</div></div><div style="background:rgba(255,255,255,0.05);padding:6px 10px;border-radius:6px"><div style="font-size:9px;color:rgba(255,255,255,0.4)">DEADLINE</div><div style="font-weight:600">{p['end_date']}</div></div></div><div style="display:flex;justify-content:space-between;margin-bottom:6px"><span style="font-size:11px;color:rgba(255,255,255,0.5)">Fortschritt</span><span style="font-weight:600">{p['progress']}%</span></div><div class="progress"><div class="progress-bar" style="width:{p['progress']}%"></div></div></div>'''
    content = f'''<div class="header"><div><h1 class="page-title">Projekte</h1><p class="page-sub">{len(plist)} Projekte | EUR {total:,.0f}</p></div><button class="btn btn-primary">+ Neues Projekt</button></div><div class="stats"><div class="stat" style="border-left:3px solid #FF5722"><div class="stat-value" style="color:#FF5722">EUR {total:,.0f}</div><div class="stat-label">Gesamtvolumen</div></div><div class="stat" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">{active}</div><div class="stat-label">Aktiv</div></div><div class="stat" style="border-left:3px solid #2196F3"><div class="stat-value" style="color:#2196F3">{len([p for p in plist if p['status']=='completed'])}</div><div class="stat-label">Abgeschlossen</div></div><div class="stat" style="border-left:3px solid #9C27B0"><div class="stat-value" style="color:#9C27B0">{len(plist)}</div><div class="stat-label">Gesamt</div></div></div><div class="grid-2">{cards}</div>'''
    return render_page(content, title="Projekte", active_page="projects")

@app.route('/invoices')
@login_required
def invoices():
    inv = sevdesk.get_invoices(20)
    total = sevdesk.get_total()
    rows = ''
    if inv:
        for i in inv[:15]:
            st = {'100':('Entwurf','badge-secondary'),'200':('Offen','badge-warning'),'1000':('Bezahlt','badge-success')}.get(i.get('status',''),('?','badge-secondary'))
            rows += f'<tr><td style="font-weight:500">{i.get("invoiceNumber","-")}</td><td>-</td><td>EUR {float(i.get("sumGross",0)):,.2f}</td><td><span class="badge {st[1]}">{st[0]}</span></td><td style="color:rgba(255,255,255,0.7)">{i.get("invoiceDate","-")}</td></tr>'
    else:
        rows = '<tr><td colspan="5" style="text-align:center;padding:40px;color:rgba(255,255,255,0.5)">Keine Rechnungen. SevDesk API verbinden.</td></tr>'
    content = f'''<div class="header"><div><h1 class="page-title">Rechnungen</h1><p class="page-sub">{len(inv)} Rechnungen | EUR {total:,.2f}</p></div><button class="btn btn-primary">+ Neue Rechnung</button></div><div class="card"><table><thead><tr><th>Nummer</th><th>Kunde</th><th>Betrag</th><th>Status</th><th>Datum</th></tr></thead><tbody>{rows}</tbody></table></div>'''
    return render_page(content, title="Rechnungen", active_page="invoices")

@app.route('/einstein')
@login_required
def einstein():
    content = '''<div class="header"><div><h1 class="page-title">Einstein AI Agency</h1><p class="page-sub">KI-gestuetzte Business Intelligence</p></div></div><div class="stats"><div class="stat" style="border-left:3px solid #FF5722"><div class="stat-value" style="color:#FF5722">87%</div><div class="stat-label">Prediction Accuracy</div></div><div class="stat" style="border-left:3px solid #2196F3"><div class="stat-value" style="color:#2196F3">24</div><div class="stat-label">Active Insights</div></div><div class="stat" style="border-left:3px solid #9C27B0"><div class="stat-value" style="color:#9C27B0">156</div><div class="stat-label">Automations</div></div><div class="stat" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">EUR 420K</div><div class="stat-label">Revenue Impact</div></div></div><div class="grid-3"><a href="/einstein/predictions" class="card" style="text-decoration:none;color:white"><div style="font-size:32px;margin-bottom:12px">P</div><h3>Predictions</h3><p style="color:rgba(255,255,255,0.5);font-size:12px">Lead Conversion, Deal Close</p></a><a href="/einstein/analytics" class="card" style="text-decoration:none;color:white"><div style="font-size:32px;margin-bottom:12px">A</div><h3>Analytics</h3><p style="color:rgba(255,255,255,0.5);font-size:12px">Deep Learning Analyse</p></a><a href="/einstein/insights" class="card" style="text-decoration:none;color:white"><div style="font-size:32px;margin-bottom:12px">I</div><h3>Insights</h3><p style="color:rgba(255,255,255,0.5);font-size:12px">Auto Empfehlungen</p></a></div>'''
    return render_page(content, title="Einstein AI", active_page="einstein")

@app.route('/einstein/predictions')
@login_required
def einstein_predictions():
    rows = ''
    for p in PREDICTIONS:
        c = {'conversion':'#4CAF50','deal':'#2196F3','upsell':'#FF9800'}.get(p['type'],'#666')
        rows += f'<tr><td><span class="badge" style="background:{c}22;color:{c}">{p["type"]}</span></td><td style="font-weight:500">{p["lead"]}</td><td>{p["prediction"]}</td><td><div style="display:flex;align-items:center;gap:8px"><div class="progress" style="flex:1"><div class="progress-bar" style="width:{p["confidence"]}%;background:{c}"></div></div><span>{p["confidence"]}%</span></div></td></tr>'
    content = f'''<div class="header"><div><h1 class="page-title">Einstein Predictions</h1><p class="page-sub">KI-basierte Prognosen</p></div><a href="/einstein" class="btn btn-secondary">Zurueck</a></div><div class="card"><h3 style="margin-bottom:16px">Aktuelle Predictions</h3><table><thead><tr><th>Typ</th><th>Lead</th><th>Prediction</th><th>Confidence</th></tr></thead><tbody>{rows}</tbody></table></div>'''
    return render_page(content, title="Predictions", active_page="predictions")

@app.route('/einstein/analytics')
@login_required
def einstein_analytics():
    content = '''<div class="header"><div><h1 class="page-title">Einstein Analytics</h1><p class="page-sub">Deep Learning Analyse</p></div><a href="/einstein" class="btn btn-secondary">Zurueck</a></div><div class="stats"><div class="stat" style="border-left:3px solid #FF5722"><div class="stat-value" style="color:#FF5722">1.2M</div><div class="stat-label">Datenpunkte</div></div><div class="stat" style="border-left:3px solid #2196F3"><div class="stat-value" style="color:#2196F3">47</div><div class="stat-label">ML Models</div></div><div class="stat" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">99.2%</div><div class="stat-label">Accuracy</div></div></div><div class="card"><h3 style="margin-bottom:16px">Performance</h3><canvas id="chart" height="250"></canvas></div><script>new Chart(document.getElementById('chart'),{type:'line',data:{labels:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],datasets:[{label:'Revenue',data:[65,72,78,74,82,89,95,91,99,105,112,125],borderColor:'#FF5722',fill:false,tension:0.4},{label:'Leads',data:[28,32,35,39,42,48,52,58,61,65,72,78],borderColor:'#2196F3',fill:false,tension:0.4}]},options:{responsive:true}});</script>'''
    return render_page(content, title="Analytics", active_page="analytics")

@app.route('/einstein/insights')
@login_required
def einstein_insights():
    insights = [{"type":"hot","title":"Hot Opportunity","desc":"Thomas Moser (Loxone) - 87% Conversion","color":"#f44336"},{"type":"upsell","title":"Upsell Potenzial","desc":"Mainova AG - EUR 150k PV-Integration","color":"#FF9800"},{"type":"pv","title":"PV Opportunity","desc":"Smart Home Bayern - 15 kWp Anfrage","color":"#FFD700"},{"type":"trend","title":"Trend Alert","desc":"Smart Home +45% - Marketing erhoehen?","color":"#2196F3"}]
    items = ''
    for i in insights:
        items += f'<div style="display:flex;justify-content:space-between;align-items:center;padding:16px;background:rgba(255,255,255,0.03);border-radius:8px;margin-bottom:12px;border-left:3px solid {i["color"]}"><div><div style="font-weight:600;color:{i["color"]};margin-bottom:4px">{i["title"]}</div><div style="color:rgba(255,255,255,0.8)">{i["desc"]}</div></div><button class="btn btn-primary">Aktion</button></div>'
    content = f'''<div class="header"><div><h1 class="page-title">Einstein Insights</h1><p class="page-sub">Automatische Empfehlungen</p></div><a href="/einstein" class="btn btn-secondary">Zurueck</a></div><div class="card"><h3 style="margin-bottom:16px">Aktuelle Empfehlungen</h3>{items}</div>'''
    return render_page(content, title="Insights", active_page="insights")

@app.route('/pv')
@login_required
def pv():
    content = '''<div class="header"><div><h1 class="page-title">Photovoltaik</h1><p class="page-sub">Solar und Smart Home Integration</p></div><a href="/pv/calculator" class="btn btn-primary">PV Rechner</a></div><div class="stats"><div class="stat" style="border-left:3px solid #FFD700"><div class="stat-value" style="color:#FFD700">12</div><div class="stat-label">PV Projekte</div></div><div class="stat" style="border-left:3px solid #FF9800"><div class="stat-value" style="color:#FF9800">EUR 1.2M</div><div class="stat-label">PV Pipeline</div></div><div class="stat" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">145 kWp</div><div class="stat-label">Installiert</div></div><div class="stat" style="border-left:3px solid #2196F3"><div class="stat-value" style="color:#2196F3">4</div><div class="stat-label">Partner</div></div></div><div class="grid-3"><a href="/pv/projects" class="card" style="text-decoration:none;color:white;border:1px solid rgba(255,215,0,0.3)"><div style="font-size:32px;margin-bottom:12px">H</div><h3>PV Projekte</h3></a><a href="/pv/partners" class="card" style="text-decoration:none;color:white;border:1px solid rgba(255,152,0,0.3)"><div style="font-size:32px;margin-bottom:12px">P</div><h3>Partner</h3></a><a href="/pv/calculator" class="card" style="text-decoration:none;color:white;border:1px solid rgba(76,175,80,0.3)"><div style="font-size:32px;margin-bottom:12px">R</div><h3>PV Rechner</h3></a></div>'''
    return render_page(content, title="Photovoltaik", active_page="pv")

@app.route('/pv/partners')
@login_required
def pv_partners():
    cards = ''
    for p in PV_PARTNERS:
        cards += f'''<div class="card" style="border:1px solid rgba(255,215,0,0.2)"><div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:16px"><div style="display:flex;align-items:center;gap:12px"><div style="font-size:40px">{p['logo']}</div><div><h3 style="margin-bottom:4px">{p['name']}</h3><span class="badge badge-warning">{p['type']}</span></div></div><div style="text-align:right"><div style="color:#FFD700;font-size:12px">{p['rating']}/5.0</div></div></div><div style="display:flex;justify-content:space-between;align-items:center;padding-top:16px;border-top:1px solid rgba(255,255,255,0.1)"><div><span style="color:rgba(255,255,255,0.5);font-size:12px">Provision:</span><span style="color:#4CAF50;font-weight:600"> {p['commission']}</span></div><button class="btn btn-primary" style="padding:6px 10px;font-size:11px">Lead</button></div></div>'''
    content = f'''<div class="header"><div><h1 class="page-title">PV Partner</h1><p class="page-sub">Strategische Partnerschaften</p></div><a href="/pv" class="btn btn-secondary">Zurueck</a></div><div class="grid-2">{cards}</div>'''
    return render_page(content, title="PV Partner", active_page="pv_partners")

@app.route('/pv/calculator')
@login_required
def pv_calculator():
    content = '''<div class="header"><div><h1 class="page-title">PV Rechner</h1><p class="page-sub">ROI und Amortisation</p></div><a href="/pv" class="btn btn-secondary">Zurueck</a></div><div class="grid-2"><div class="card"><h3 style="margin-bottom:20px">Projektdaten</h3><div style="margin-bottom:16px"><label style="display:block;margin-bottom:6px;font-size:12px;color:rgba(255,255,255,0.7)">Anlagegroesse (kWp)</label><input type="number" id="size" value="10" onchange="calc()"></div><div style="margin-bottom:16px"><label style="display:block;margin-bottom:6px;font-size:12px;color:rgba(255,255,255,0.7)">Strompreis (EUR/kWh)</label><input type="number" id="price" value="0.35" step="0.01" onchange="calc()"></div><div style="margin-bottom:16px"><label style="display:block;margin-bottom:6px;font-size:12px;color:rgba(255,255,255,0.7)">Eigenverbrauch (%)</label><input type="range" id="ev" value="70" min="20" max="95" onchange="document.getElementById('evD').textContent=this.value+'%';calc()"><div style="display:flex;justify-content:space-between;font-size:10px;color:rgba(255,255,255,0.5)"><span>20%</span><span id="evD">70%</span><span>95%</span></div></div><label style="display:flex;align-items:center;gap:8px;margin-bottom:12px;cursor:pointer"><input type="checkbox" id="bat" onchange="calc()"><span style="font-size:13px">Speicher (+EUR 8.000)</span></label></div><div class="card" style="background:linear-gradient(135deg,rgba(255,215,0,0.1),rgba(255,152,0,0.05));border:1px solid rgba(255,215,0,0.3)"><h3 style="margin-bottom:20px">Ergebnis</h3><div class="grid-2" style="margin-bottom:20px"><div style="background:rgba(0,0,0,0.2);padding:16px;border-radius:8px;text-align:center"><div id="rProd" style="font-size:24px;font-weight:700;color:#FFD700">9,500</div><div style="font-size:10px;color:rgba(255,255,255,0.5)">kWh/Jahr</div></div><div style="background:rgba(0,0,0,0.2);padding:16px;border-radius:8px;text-align:center"><div id="rSave" style="font-size:24px;font-weight:700;color:#4CAF50">EUR 2,328</div><div style="font-size:10px;color:rgba(255,255,255,0.5)">Ersparnis/Jahr</div></div></div><div style="background:rgba(0,0,0,0.2);padding:16px;border-radius:8px;margin-bottom:16px"><div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Investition:</span><span id="rCost" style="font-weight:600">EUR 14,000</span></div><div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Amortisation:</span><span id="rAmort" style="font-weight:600;color:#FF9800">6.0 Jahre</span></div><div style="display:flex;justify-content:space-between"><span>ROI (25J):</span><span id="rROI" style="font-weight:600;color:#4CAF50">316%</span></div></div><button class="btn btn-primary" style="width:100%;justify-content:center">Angebot erstellen</button></div></div><script>function calc(){const s=parseFloat(document.getElementById('size').value)||10,p=parseFloat(document.getElementById('price').value)||0.35,e=(parseFloat(document.getElementById('ev').value)||70)/100,bat=document.getElementById('bat').checked;const prod=s*950,evKwh=prod*e,ein=prod-evKwh,save=evKwh*p+ein*0.082;let cost=s*1400;if(bat)cost+=8000;const amort=cost/save,roi=((save*25)-cost)/cost*100;document.getElementById('rProd').textContent=Math.round(prod).toLocaleString('de-DE');document.getElementById('rSave').textContent='EUR '+Math.round(save).toLocaleString('de-DE');document.getElementById('rCost').textContent='EUR '+Math.round(cost).toLocaleString('de-DE');document.getElementById('rAmort').textContent=amort.toFixed(1)+' Jahre';document.getElementById('rROI').textContent=Math.round(roi)+'%';}calc();</script>'''
    return render_page(content, title="PV Rechner", active_page="pv_calc")

@app.route('/pv/projects')
@login_required
def pv_projects():
    content = '''<div class="header"><div><h1 class="page-title">PV Projekte</h1></div><a href="/pv" class="btn btn-secondary">Zurueck</a></div><div class="card"><p style="text-align:center;padding:40px;color:rgba(255,255,255,0.5)">PV Projekte werden bald hinzugefuegt...</p></div>'''
    return render_page(content, title="PV Projekte", active_page="pv")

@app.route('/dedsec')
@login_required
def dedsec():
    rows = ''
    for s in DEDSEC:
        sc = {'online':'badge-success','active':'badge-success','charging':'badge-warning','locked':'badge-info'}.get(s['status'],'badge-secondary')
        rows += f'<tr><td style="font-weight:500">{s["name"]}</td><td><span class="badge {sc}">{s["status"]}</span></td><td style="color:rgba(255,255,255,0.7)">{s["details"]}</td></tr>'
    content = f'''<div class="header"><div><h1 class="page-title">DedSec Security Hub</h1></div><span class="badge badge-success">All Systems Online</span></div><div class="stats"><div class="stat" style="border-left:3px solid #00BCD4"><div class="stat-value" style="color:#00BCD4">24</div><div class="stat-label">Cameras</div></div><div class="stat" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">2</div><div class="stat-label">Drones</div></div><div class="stat" style="border-left:3px solid #f44336"><div class="stat-value" style="color:#f44336">1,247</div><div class="stat-label">Threats Blocked</div></div><div class="stat" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">100%</div><div class="stat-label">Uptime</div></div></div><div class="grid-3" style="margin-bottom:16px"><a href="/dedsec/tower" class="card" style="text-decoration:none;color:white;border:1px solid rgba(0,188,212,0.3)"><div style="font-size:32px;margin-bottom:12px">T</div><h3>Command Tower</h3></a><a href="/dedsec/drones" class="card" style="text-decoration:none;color:white;border:1px solid rgba(76,175,80,0.3)"><div style="font-size:32px;margin-bottom:12px">D</div><h3>Drone Control</h3></a><a href="/dedsec/cctv" class="card" style="text-decoration:none;color:white;border:1px solid rgba(156,39,176,0.3)"><div style="font-size:32px;margin-bottom:12px">C</div><h3>CCTV Network</h3></a></div><div class="card"><h3 style="margin-bottom:16px">System Status</h3><table><thead><tr><th>System</th><th>Status</th><th>Details</th></tr></thead><tbody>{rows}</tbody></table></div>'''
    return render_page(content, title="DedSec", active_page="dedsec")

@app.route('/dedsec/tower')
@login_required
def dedsec_tower():
    content = '''<div class="header"><div><h1 class="page-title">Command Tower</h1></div><span class="badge badge-success">LIVE</span></div><div class="grid-2"><div class="card" style="border:1px solid rgba(0,188,212,0.3)"><h3 style="margin-bottom:16px">Live Map</h3><div style="background:rgba(0,0,0,0.3);border-radius:8px;height:350px;display:flex;align-items:center;justify-content:center"><div style="text-align:center"><div style="font-size:48px;margin-bottom:12px">M</div><div style="color:#00BCD4">Live Security Map</div></div></div></div><div><div class="card" style="margin-bottom:16px;border:1px solid rgba(255,87,34,0.3)"><h3 style="margin-bottom:12px">Quick Actions</h3><button class="btn btn-danger" style="width:100%;margin-bottom:8px">Alarm</button><button class="btn btn-secondary" style="width:100%;margin-bottom:8px">Lockdown</button><button class="btn btn-secondary" style="width:100%">Alle Kameras</button></div><div class="card" style="border:1px solid rgba(76,175,80,0.3)"><h3 style="margin-bottom:12px">Heute</h3><div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05)"><span>Bewegungen</span><span style="color:#2196F3">47</span></div><div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05)"><span>Alerts</span><span style="color:#4CAF50">0</span></div><div style="display:flex;justify-content:space-between;padding:8px 0"><span>Health</span><span style="color:#4CAF50">100%</span></div></div></div></div>'''
    return render_page(content, title="Tower", active_page="tower")

@app.route('/dedsec/drones')
@login_required
def dedsec_drones():
    content = '''<div class="header"><div><h1 class="page-title">Drone Control</h1></div></div><div class="grid-2"><div class="card" style="border:1px solid rgba(76,175,80,0.3)"><div style="display:flex;justify-content:space-between;margin-bottom:16px"><h3>Patrol Drone Alpha</h3><span class="badge badge-success">Active</span></div><div style="text-align:center;margin-bottom:16px;font-size:48px">D1</div><div style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Battery</span><span style="color:#4CAF50">87%</span></div><div class="progress"><div class="progress-bar" style="width:87%;background:#4CAF50"></div></div></div><button class="btn btn-primary" style="width:100%;margin-top:12px">Track Live</button></div><div class="card" style="border:1px solid rgba(255,152,0,0.3)"><div style="display:flex;justify-content:space-between;margin-bottom:16px"><h3>Patrol Drone Beta</h3><span class="badge badge-warning">Charging</span></div><div style="text-align:center;margin-bottom:16px;font-size:48px">D2</div><div style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;margin-bottom:4px"><span>Battery</span><span style="color:#FF9800">23%</span></div><div class="progress"><div class="progress-bar" style="width:23%;background:#FF9800"></div></div></div><button class="btn btn-secondary" style="width:100%;margin-top:12px">Charging...</button></div></div>'''
    return render_page(content, title="Drones", active_page="drones")

@app.route('/dedsec/cctv')
@login_required
def dedsec_cctv():
    cams = ''
    for i in range(8):
        cams += f'<div class="card" style="padding:0;overflow:hidden"><div style="background:linear-gradient(135deg,rgba(0,188,212,0.2),rgba(0,150,136,0.1));height:80px;display:flex;align-items:center;justify-content:center"><div style="font-size:28px;opacity:0.5">C{i+1}</div></div><div style="padding:10px"><div style="font-weight:600;font-size:12px">CAM-0{i+1}</div><span class="badge badge-success" style="margin-top:6px;font-size:9px">Live</span></div></div>'
    content = f'''<div class="header"><div><h1 class="page-title">CCTV Network</h1><p class="page-sub">24 Kameras | Live</p></div><span class="badge badge-success">24/24 Online</span></div><div class="grid-4">{cams}</div>'''
    return render_page(content, title="CCTV", active_page="cctv")

@app.route('/whatsapp')
@login_required
def whatsapp():
    content = '''<div class="header"><div><h1 class="page-title">WhatsApp Business</h1></div></div><div class="stats"><div class="stat" style="border-left:3px solid #25D366"><div class="stat-value" style="color:#25D366">1,247</div><div class="stat-label">Kontakte</div></div><div class="stat" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">89%</div><div class="stat-label">Open Rate</div></div><div class="stat" style="border-left:3px solid #FF9800"><div class="stat-value" style="color:#FF9800">12</div><div class="stat-label">Kampagnen</div></div></div><div class="card"><h3 style="margin-bottom:16px">Quick Actions</h3><div class="grid-3"><a href="/whatsapp/consent" class="btn btn-primary" style="text-align:center;padding:20px;justify-content:center">Consent Manager</a><a href="#" class="btn btn-secondary" style="text-align:center;padding:20px;justify-content:center">Kampagnen</a><a href="#" class="btn btn-secondary" style="text-align:center;padding:20px;justify-content:center">Templates</a></div></div>'''
    return render_page(content, title="WhatsApp", active_page="whatsapp")

@app.route('/whatsapp/consent')
@login_required
def whatsapp_consent():
    contacts = hubspot.get_contacts(200)
    rows = ''
    for c in contacts[:50]:
        p = c.get('properties',{})
        name = f"{p.get('firstname','')} {p.get('lastname','')}".strip() or 'Unbekannt'
        consent = p.get('hs_whatsapp_consent','unknown')
        cc = {'granted':('#4CAF50','Erteilt'),'revoked':('#f44336','Widerrufen')}.get(consent,('#FF9800','Unbekannt'))
        rows += f'<tr><td><input type="checkbox" class="cb" data-id="{c.get("id")}" onchange="upd()"></td><td style="font-weight:500">{name}</td><td style="color:rgba(255,255,255,0.7)">{p.get("email","-")}</td><td style="color:rgba(255,255,255,0.7)">{p.get("phone","-")}</td><td><span class="badge" style="background:{cc[0]}22;color:{cc[0]}">{cc[1]}</span></td></tr>'
    content = f'''<div class="header"><div><h1 class="page-title">WhatsApp Consent</h1></div><div style="display:flex;gap:10px"><button onclick="bulk('granted')" class="btn btn-success">Consent erteilen</button><button onclick="bulk('revoked')" class="btn btn-danger">Widerrufen</button></div></div><div class="card"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.1)"><label style="display:flex;align-items:center;gap:8px;cursor:pointer"><input type="checkbox" id="all" onchange="toggle()"><span>Alle auswaehlen</span></label><span style="color:rgba(255,255,255,0.5)"><span id="cnt">0</span> von {len(contacts)} ausgewaehlt</span></div><table><thead><tr><th></th><th>Name</th><th>Email</th><th>Telefon</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div><script>function toggle(){{document.querySelectorAll('.cb').forEach(c=>c.checked=document.getElementById('all').checked);upd()}}function upd(){{document.getElementById('cnt').textContent=document.querySelectorAll('.cb:checked').length}}async function bulk(s){{const ids=Array.from(document.querySelectorAll('.cb:checked')).map(c=>c.dataset.id);if(!ids.length){{alert('Bitte auswaehlen');return}}if(!confirm('Consent fuer '+ids.length+' Kontakte auf "'+s+'" setzen?'))return;const r=await fetch('/api/whatsapp/consent/bulk',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{contact_ids:ids,status:s}})}});const d=await r.json();alert('Erfolgreich: '+d.success+', Fehler: '+d.failed);location.reload()}}</script>'''
    return render_page(content, title="Consent", active_page="consent")

@app.route('/api/whatsapp/consent/bulk', methods=['POST'])
@login_required
def api_consent_bulk():
    data = request.json
    result = hubspot.bulk_update_consent(data.get('contact_ids',[]), data.get('status','granted'))
    return jsonify(result)

@app.route('/godbot')
@login_required
def godbot():
    content = '''<div class="header"><div><h1 class="page-title">GOD BOT AI</h1><p class="page-sub">Ultra Instinct Assistant - Claude</p></div></div><div class="card" style="min-height:500px;display:flex;flex-direction:column"><div id="chat" style="flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px"><div style="text-align:center;padding:40px"><div style="font-size:64px;margin-bottom:16px">G</div><h2 style="margin-bottom:8px">GOD MODE ACTIVATED</h2><p style="color:rgba(255,255,255,0.5)">Ultra Instinct AI - Bereit</p></div></div><div style="border-top:1px solid rgba(255,255,255,0.1);padding:16px;display:flex;gap:12px"><input type="text" id="inp" placeholder="Frag GOD BOT..." style="flex:1" onkeypress="if(event.key==='Enter')send()"><button onclick="send()" class="btn btn-primary">Senden</button></div></div><script>async function send(){const i=document.getElementById('inp'),m=i.value.trim();if(!m)return;const c=document.getElementById('chat');c.innerHTML+='<div style="align-self:flex-end;background:linear-gradient(90deg,#FF5722,#FF9800);padding:12px 16px;border-radius:12px 12px 0 12px;max-width:70%">'+m+'</div>';i.value='';c.innerHTML+='<div id="ld" style="align-self:flex-start;color:rgba(255,255,255,0.5)">GOD BOT denkt...</div>';c.scrollTop=c.scrollHeight;const r=await fetch('/api/godbot/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});const d=await r.json();document.getElementById('ld').remove();c.innerHTML+='<div style="align-self:flex-start;background:rgba(255,255,255,0.1);padding:12px 16px;border-radius:12px 12px 12px 0;max-width:70%">'+d.response+'</div>';c.scrollTop=c.scrollHeight}</script>'''
    return render_page(content, title="GOD BOT", active_page="godbot")

@app.route('/api/godbot/chat', methods=['POST'])
@login_required
def api_godbot_chat():
    data = request.json
    system = "Du bist GOD BOT, der Ultra Instinct AI Assistant von West Money OS. Du hilfst bei CRM, Leads, Projekten, Smart Home, PV. Antworte professionell auf Deutsch."
    response = claude.chat(data.get('message',''), system)
    return jsonify({'response': response})

@app.route('/locker')
@login_required
def locker():
    content = '''<div class="header"><div><h1 class="page-title">Private Locker</h1></div><button class="btn btn-primary">Upload</button></div><div class="stats"><div class="stat" style="border-left:3px solid #FF5722"><div class="stat-value" style="color:#FF5722">892</div><div class="stat-label">Dokumente</div></div><div class="stat" style="border-left:3px solid #9C27B0"><div class="stat-value" style="color:#9C27B0">45</div><div class="stat-label">Vertraege</div></div><div class="stat" style="border-left:3px solid #2196F3"><div class="stat-value" style="color:#2196F3">128</div><div class="stat-label">Rechnungen</div></div><div class="stat" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">2.4 GB</div><div class="stat-label">Speicher</div></div></div><div class="card"><h3 style="margin-bottom:16px">Ordner</h3><div class="grid-4"><div style="text-align:center;padding:20px;background:rgba(255,255,255,0.03);border-radius:8px;cursor:pointer"><div style="font-size:40px;margin-bottom:8px">D</div><div style="font-weight:500">Dokumente</div><div style="font-size:12px;color:rgba(255,255,255,0.5)">892 Dateien</div></div><div style="text-align:center;padding:20px;background:rgba(255,255,255,0.03);border-radius:8px;cursor:pointer"><div style="font-size:40px;margin-bottom:8px">V</div><div style="font-weight:500">Vertraege</div><div style="font-size:12px;color:rgba(255,255,255,0.5)">45 Dateien</div></div><div style="text-align:center;padding:20px;background:rgba(255,255,255,0.03);border-radius:8px;cursor:pointer"><div style="font-size:40px;margin-bottom:8px">R</div><div style="font-weight:500">Rechnungen</div><div style="font-size:12px;color:rgba(255,255,255,0.5)">128 Dateien</div></div><div style="text-align:center;padding:20px;background:rgba(255,255,255,0.03);border-radius:8px;cursor:pointer"><div style="font-size:40px;margin-bottom:8px">P</div><div style="font-weight:500">Projekte</div><div style="font-size:12px;color:rgba(255,255,255,0.5)">67 Dateien</div></div></div></div>'''
    return render_page(content, title="Locker", active_page="locker")

@app.route('/settings')
@login_required
def settings():
    apis = [('HubSpot CRM', CONFIG['HUBSPOT_API_KEY']), ('Stripe', CONFIG['STRIPE_SECRET_KEY']), ('SevDesk', CONFIG['SEVDESK_API_KEY']), ('Claude AI', CONFIG['ANTHROPIC_API_KEY'])]
    rows = ''
    for n, k in apis:
        has = bool(k and len(k)>10)
        rows += f'<tr><td style="font-weight:500">{n}</td><td><span class="badge {"badge-success" if has else "badge-danger"}">{"Verbunden" if has else "Nicht konfiguriert"}</span></td><td style="color:rgba(255,255,255,0.5);font-family:monospace">{k[:20]+"..." if has else "-"}</td></tr>'
    content = f'''<div class="header"><div><h1 class="page-title">Settings</h1></div></div><div class="card"><h3 style="margin-bottom:16px">API Keys</h3><table><thead><tr><th>Service</th><th>Status</th><th>Key</th></tr></thead><tbody>{rows}</tbody></table></div><div class="card"><h3 style="margin-bottom:16px">Hinweis</h3><p style="color:rgba(255,255,255,0.7)">API Keys in .env konfigurieren. Neustart erforderlich.</p></div>'''
    return render_page(content, title="Settings", active_page="settings")

@app.route('/sync')
@login_required
def sync():
    content = '''<div class="header"><div><h1 class="page-title">API Sync</h1></div></div><div class="grid-3"><div class="card"><h3 style="margin-bottom:12px">HubSpot</h3><p style="color:rgba(255,255,255,0.5);margin-bottom:16px;font-size:13px">Kontakte und Deals sync</p><button onclick="syncAPI('hubspot')" class="btn btn-primary" style="width:100%">Sync</button><div id="hubspot-r" style="margin-top:12px"></div></div><div class="card"><h3 style="margin-bottom:12px">Stripe</h3><p style="color:rgba(255,255,255,0.5);margin-bottom:16px;font-size:13px">Zahlungen abrufen</p><button onclick="syncAPI('stripe')" class="btn btn-primary" style="width:100%">Sync</button><div id="stripe-r" style="margin-top:12px"></div></div><div class="card"><h3 style="margin-bottom:12px">SevDesk</h3><p style="color:rgba(255,255,255,0.5);margin-bottom:16px;font-size:13px">Rechnungen import</p><button onclick="syncAPI('sevdesk')" class="btn btn-primary" style="width:100%">Sync</button><div id="sevdesk-r" style="margin-top:12px"></div></div></div><script>async function syncAPI(t){document.getElementById(t+'-r').innerHTML='<span style="color:#FF9800">Synchronisiere...</span>';const r=await fetch('/api/sync/'+t,{method:'POST'});const d=await r.json();document.getElementById(t+'-r').innerHTML='<span style="color:#4CAF50">'+JSON.stringify(d)+'</span>'}</script>'''
    return render_page(content, title="API Sync", active_page="sync")

@app.route('/api/sync/hubspot', methods=['POST'])
@login_required
def api_sync_hubspot():
    contacts = hubspot.get_contacts(500)
    return jsonify({'synced': len(contacts)})

@app.route('/api/sync/stripe', methods=['POST'])
@login_required
def api_sync_stripe():
    return jsonify({'balance': stripe_api.get_balance(), 'revenue': stripe_api.get_revenue()})

@app.route('/api/sync/sevdesk', methods=['POST'])
@login_required
def api_sync_sevdesk():
    return jsonify({'invoices': len(sevdesk.get_invoices()), 'total': sevdesk.get_total()})

@app.route('/api/v1/health')
def api_health():
    return jsonify({'status': 'healthy', 'version': 'v15.369', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print('\nWEST MONEY OS v15.369 - ULTIMATE EDITION')
    print('Login: admin / admin123')
    print('Server: http://0.0.0.0:5000\n')
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
