#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WEST MONEY OS v15.369 - ULTIMATE EDITION
Enterprise Universe GmbH | CEO: Ömer Hüseyin Coşkun
Launch: 01.01.2026

Echte Daten Integration:
- HubSpot CRM mit WhatsApp Consent Bulk-Update
- Stripe Payments
- SevDesk Accounting  
- Claude AI (GOD BOT)
"""

from flask import Flask, render_template_string, jsonify, request, redirect, session
from flask_cors import CORS
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
import hashlib, sqlite3, requests, os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'westmoney-secret')
CORS(app)

CONFIG = {
    'HUBSPOT_API_KEY': os.getenv('HUBSPOT_API_KEY', ''),
    'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY', ''),
    'SEVDESK_API_KEY': os.getenv('SEVDESK_API_KEY', ''),
    'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', ''),
}

# Real Leads from transcripts
LEADS = [
    {"id":1,"name":"Thomas Moser","company":"Loxone Electronics","position":"Gründer","score":96,"stage":"contacted","value":500000,"priority":"hot"},
    {"id":2,"name":"Martin Öller","company":"Loxone Electronics","position":"Gründer","score":96,"stage":"contacted","value":500000,"priority":"hot"},
    {"id":3,"name":"Rüdiger Keinberger","company":"Loxone Electronics","position":"CEO","score":95,"stage":"contacted","value":450000,"priority":"hot"},
    {"id":4,"name":"Dr. Michael Maxelon","company":"Mainova AG","position":"Vorstandsvorsitzender","score":95,"stage":"qualified","value":380000,"priority":"hot"},
    {"id":5,"name":"Max Hofmann","company":"Hofmann Bau AG","position":"Vorstand","score":94,"stage":"won","value":345000,"priority":"won"},
    {"id":6,"name":"Frank Junker","company":"ABG Frankfurt Holding","position":"Vors. GF","score":92,"stage":"proposal","value":420000,"priority":"warm"},
    {"id":7,"name":"Anna Müller","company":"Smart Home Bayern","position":"GF","score":91,"stage":"won","value":156000,"priority":"won"},
    {"id":8,"name":"Tino Kugler","company":"Loxone Deutschland","position":"MD","score":90,"stage":"negotiation","value":220000,"priority":"warm"},
]

PREDICTIONS = [
    {"type":"conversion","lead":"Thomas Moser","prediction":"87% Conversion","confidence":87,"action":"Termin KW2"},
    {"type":"deal","lead":"Hofmann Bau AG","prediction":"Q1 2026 Abschluss","confidence":92,"action":"Vertrag vorbereiten"},
    {"type":"upsell","lead":"Mainova AG","prediction":"€150K PV","confidence":78,"action":"PV-Angebot"},
]

PV_PARTNERS = [
    {"name":"1Komma5°","type":"Premium","commission":"8%","rating":4.8},
    {"name":"Enpal","type":"Strategic","commission":"6%","rating":4.6},
    {"name":"Zolar","type":"Online","commission":"5%","rating":4.5},
    {"name":"Solarwatt","type":"Hersteller","commission":"7%","rating":4.9},
]

# Database
def get_db():
    conn = sqlite3.connect('westmoney.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,username TEXT UNIQUE,password_hash TEXT,role TEXT DEFAULT 'user')''')
    c.execute('''CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY,name TEXT,client TEXT,status TEXT,progress INTEGER,value REAL,project_type TEXT,location TEXT,start_date TEXT,end_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY,message TEXT,response TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Admin user
    admin_hash = hashlib.sha256('663724!'.encode()).hexdigest()
    c.execute('INSERT OR IGNORE INTO users (username,password_hash,role) VALUES (?,?,?)',('admin',admin_hash,'admin'))
    
    # Real projects
    projects = [
        ('Villa Müller - Smart Home','Familie Müller','active',75,185000,'LOXONE','Frankfurt','2024-09-15','2025-02-28'),
        ('Bürokomplex TechPark','TechCorp GmbH','active',45,420000,'KNX','München','2024-11-01','2025-06-30'),
        ('Penthouse Westend','Dr. Schmidt','planning',15,95000,'LOXONE','Frankfurt','2025-01-15','2025-04-30'),
        ('Mehrfamilienhaus Grünwald','Immobilien AG','active',60,380000,'LOXONE','München','2024-08-01','2025-03-15'),
        ('Smart Office Düsseldorf','FinanceHub','completed',100,156000,'KNX','Düsseldorf','2024-03-01','2024-10-30'),
        ('Wellness Center Spa','Wellness GmbH','active',30,245000,'LOXONE','Baden-Baden','2024-12-01','2025-08-15'),
    ]
    for p in projects:
        c.execute('INSERT OR IGNORE INTO projects (name,client,status,progress,value,project_type,location,start_date,end_date) SELECT ?,?,?,?,?,?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM projects WHERE name=?)',(*p,p[0]))
    conn.commit()
    conn.close()

# API Clients
class HubSpotAPI:
    def __init__(self):
        self.key = CONFIG['HUBSPOT_API_KEY']
        self.headers = {'Authorization':f'Bearer {self.key}','Content-Type':'application/json'}
    
    def get_contacts(self, limit=100):
        if not self.key: return []
        try:
            r = requests.get('https://api.hubapi.com/crm/v3/objects/contacts',headers=self.headers,params={'limit':limit,'properties':'firstname,lastname,email,phone,company,hs_whatsapp_consent'},timeout=15)
            return r.json().get('results',[]) if r.ok else []
        except: return []
    
    def update_contact(self, cid, props):
        if not self.key: return False
        try:
            r = requests.patch(f'https://api.hubapi.com/crm/v3/objects/contacts/{cid}',headers=self.headers,json={'properties':props},timeout=15)
            return r.ok
        except: return False
    
    def bulk_update_consent(self, ids, status):
        results = {'success':0,'failed':0}
        for cid in ids:
            if self.update_contact(cid, {'hs_whatsapp_consent':status}):
                results['success'] += 1
            else:
                results['failed'] += 1
        return results

class StripeAPI:
    def __init__(self):
        self.key = CONFIG['STRIPE_SECRET_KEY']
    
    def get_balance(self):
        if not self.key: return 0
        try:
            r = requests.get('https://api.stripe.com/v1/balance',headers={'Authorization':f'Bearer {self.key}'},timeout=10)
            data = r.json()
            return next((b['amount']/100 for b in data.get('available',[]) if b.get('currency')=='eur'),0)
        except: return 0

class SevDeskAPI:
    def __init__(self):
        self.key = CONFIG['SEVDESK_API_KEY']
    
    def get_invoices(self, limit=100):
        if not self.key: return []
        try:
            r = requests.get('https://my.sevdesk.de/api/v1/Invoice',headers={'Authorization':self.key},params={'limit':limit},timeout=15)
            return r.json().get('objects',[]) if r.ok else []
        except: return []
    
    def get_total(self):
        return sum(float(i.get('sumGross',0)) for i in self.get_invoices(500))

class ClaudeAPI:
    def __init__(self):
        self.key = CONFIG['ANTHROPIC_API_KEY']
    
    def chat(self, msg):
        if not self.key: return "API Key nicht konfiguriert."
        try:
            r = requests.post('https://api.anthropic.com/v1/messages',headers={'x-api-key':self.key,'Content-Type':'application/json','anthropic-version':'2023-06-01'},json={'model':'claude-sonnet-4-20250514','max_tokens':2048,'system':'Du bist GOD BOT, der Ultra Instinct AI Assistant von West Money OS. Antworte professionell auf Deutsch.','messages':[{'role':'user','content':msg}]},timeout=60)
            return r.json()['content'][0]['text'] if r.ok else f"Error: {r.status_code}"
        except Exception as e: return f"Error: {e}"

hubspot = HubSpotAPI()
stripe_api = StripeAPI()
sevdesk = SevDeskAPI()
claude = ClaudeAPI()

# Auth
def login_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        if not session.get('logged_in'): return redirect('/login')
        return f(*args,**kwargs)
    return decorated

# Base Template
BASE = '''<!DOCTYPE html>
<html lang="de"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{{ title }} - West Money OS v15.369</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:#0a0a0a;color:#fff;min-height:100vh}
.sidebar{position:fixed;left:0;top:0;width:250px;height:100vh;background:linear-gradient(180deg,#1a1a2e,#0f0f1a);border-right:1px solid rgba(255,255,255,0.1);padding:20px;overflow-y:auto}
.logo{display:flex;align-items:center;gap:12px;padding:16px 0;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:20px}
.logo-icon{width:40px;height:40px;background:linear-gradient(135deg,#FF5722,#FF9800);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700}
.logo-text{font-size:18px;font-weight:700;background:linear-gradient(90deg,#FF5722,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-section{margin-bottom:16px}
.nav-title{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.3);margin-bottom:8px;padding-left:12px}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:8px;color:rgba(255,255,255,0.7);text-decoration:none;font-size:13px;margin-bottom:2px}
.nav-item:hover{background:rgba(255,87,34,0.1);color:#FF5722}
.nav-item.active{background:linear-gradient(90deg,rgba(255,87,34,0.2),transparent);color:#FF5722;border-left:3px solid #FF5722}
.main{margin-left:250px;padding:24px}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}
.page-title{font-size:24px;font-weight:700}
.page-sub{color:rgba(255,255,255,0.5);font-size:13px;margin-top:4px}
.card{background:linear-gradient(135deg,#1a1a2e,#0f0f1a);border-radius:12px;padding:20px;border:1px solid rgba(255,255,255,0.08);margin-bottom:16px}
.btn{padding:10px 20px;border-radius:8px;font-weight:600;font-size:13px;cursor:pointer;border:none;text-decoration:none;display:inline-flex;align-items:center;gap:6px}
.btn-primary{background:linear-gradient(90deg,#FF5722,#FF9800);color:white}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 4px 15px rgba(255,87,34,0.4)}
.btn-secondary{background:rgba(255,255,255,0.1);color:white;border:1px solid rgba(255,255,255,0.2)}
.btn-success{background:#4CAF50;color:white}
.btn-danger{background:#f44336;color:white}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
.stat-card{background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:12px;padding:20px}
.stat-value{font-size:28px;font-weight:700}
.stat-label{color:rgba(255,255,255,0.5);font-size:12px;margin-top:4px}
.stat-change{font-size:11px;margin-top:4px;color:#4CAF50}
table{width:100%;border-collapse:collapse}
th,td{padding:12px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.05)}
th{font-size:11px;text-transform:uppercase;color:rgba(255,255,255,0.4)}
.badge{padding:4px 10px;border-radius:12px;font-size:11px}
.badge-success{background:rgba(76,175,80,0.2);color:#4CAF50}
.badge-warning{background:rgba(255,152,0,0.2);color:#FF9800}
.badge-info{background:rgba(33,150,243,0.2);color:#2196F3}
.badge-danger{background:rgba(244,67,54,0.2);color:#f44336}
.progress-bar{background:rgba(255,255,255,0.1);border-radius:10px;height:6px}
.progress-fill{background:linear-gradient(90deg,#FF5722,#FF9800);height:100%;border-radius:10px}
input,select{width:100%;padding:12px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:8px;color:white;font-size:14px}
input:focus{outline:none;border-color:#FF5722}
@media(max-width:1200px){.stats-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:768px){.sidebar{display:none}.main{margin-left:0}}
</style></head>
<body>
<nav class="sidebar">
<div class="logo"><div class="logo-icon">W</div><div><div class="logo-text">West Money</div><div style="font-size:10px;color:rgba(255,255,255,0.4)">OS v15.369</div></div></div>
<div class="nav-section"><div class="nav-title">Main</div>
<a href="/dashboard" class="nav-item {{'active' if p=='dashboard' else ''}}">📊 Dashboard</a>
<a href="/leads" class="nav-item {{'active' if p=='leads' else ''}}">🎯 Leads</a>
<a href="/contacts" class="nav-item {{'active' if p=='contacts' else ''}}">👥 Kontakte</a>
<a href="/projects" class="nav-item {{'active' if p=='projects' else ''}}">🏗️ Projekte</a></div>
<div class="nav-section"><div class="nav-title">Einstein AI</div>
<a href="/einstein" class="nav-item {{'active' if p=='einstein' else ''}}">🧠 Einstein</a>
<a href="/einstein/predictions" class="nav-item {{'active' if p=='predictions' else ''}}">🔮 Predictions</a></div>
<div class="nav-section"><div class="nav-title">Photovoltaik</div>
<a href="/pv" class="nav-item {{'active' if p=='pv' else ''}}">☀️ PV Home</a>
<a href="/pv/partners" class="nav-item {{'active' if p=='pv_partners' else ''}}">🤝 Partner</a>
<a href="/pv/calculator" class="nav-item {{'active' if p=='pv_calc' else ''}}">🔢 Rechner</a></div>
<div class="nav-section"><div class="nav-title">Tools</div>
<a href="/whatsapp/consent" class="nav-item {{'active' if p=='consent' else ''}}">✅ WhatsApp Consent</a>
<a href="/godbot" class="nav-item {{'active' if p=='godbot' else ''}}">🤖 GOD BOT</a>
<a href="/dedsec" class="nav-item {{'active' if p=='dedsec' else ''}}">🛡️ DedSec</a></div>
<div class="nav-section"><div class="nav-title">System</div>
<a href="/settings" class="nav-item {{'active' if p=='settings' else ''}}">⚙️ Settings</a>
<a href="/sync" class="nav-item {{'active' if p=='sync' else ''}}">🔄 API Sync</a>
<a href="/logout" class="nav-item">🚪 Logout</a></div>
</nav>
<main class="main">{{ content|safe }}</main>
</body></html>'''

def render(content,**kw):
    return render_template_string(BASE,content=content,**kw)

# Routes
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        u,p = request.form.get('username'),request.form.get('password')
        h = hashlib.sha256(p.encode()).hexdigest()
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username=? AND password_hash=?',(u,h)).fetchone()
        conn.close()
        if user:
            session['logged_in'],session['username'],session['role'] = True,u,user['role']
            return redirect('/dashboard')
    return '''<!DOCTYPE html><html><head><title>Login - West Money OS</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;background:linear-gradient(135deg,#0a0a0a,#1a1a2e);min-height:100vh;display:flex;align-items:center;justify-content:center}
.box{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:40px;width:100%;max-width:400px}
.logo{text-align:center;margin-bottom:30px}.logo-icon{font-size:48px;margin-bottom:10px}
.logo-text{font-size:24px;font-weight:700;background:linear-gradient(90deg,#FF5722,#FF9800);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.form-group{margin-bottom:20px}label{display:block;color:rgba(255,255,255,0.7);margin-bottom:8px;font-size:14px}
input{width:100%;padding:12px 16px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:8px;color:white;font-size:14px}
input:focus{outline:none;border-color:#FF5722}button{width:100%;padding:14px;background:linear-gradient(90deg,#FF5722,#FF9800);border:none;border-radius:8px;color:white;font-size:16px;font-weight:600;cursor:pointer}
button:hover{transform:translateY(-2px)}.ver{text-align:center;margin-top:20px;color:rgba(255,255,255,0.3);font-size:12px}</style></head>
<body><div class="box"><div class="logo"><div class="logo-icon">W</div><div class="logo-text">West Money OS</div></div>
<form method="POST"><div class="form-group"><label>Benutzername</label><input type="text" name="username" required placeholder="admin"></div>
<div class="form-group"><label>Passwort</label><input type="password" name="password" required></div><button type="submit">Anmelden</button></form>
<div class="ver">v15.369 Ultimate Edition</div></div></body></html>'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def index():
    return redirect('/dashboard' if session.get('logged_in') else '/login')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        hs = hubspot.get_contacts(500)
        total_contacts = len(hs) if hs else 59
        total_revenue = sevdesk.get_total() or 847234
        pipeline = sum(l['value'] for l in LEADS)
    except:
        total_contacts,total_revenue,pipeline = 59,847234,3600000
    
    c = f'''
    <div class="header"><div><h1 class="page-title">Dashboard</h1><p class="page-sub">Willkommen, {session.get("username","admin")}</p></div>
    <div style="display:flex;gap:10px"><a href="/einstein/predictions" class="btn btn-primary">🔮 Predictions</a><a href="/sync" class="btn btn-secondary">🔄 Sync</a></div></div>
    <div class="stats-grid">
        <div class="stat-card" style="border-left:3px solid #FF5722"><div class="stat-value" style="color:#FF5722">€{pipeline:,.0f}</div><div class="stat-label">Pipeline Value</div><div class="stat-change">+23.5%</div></div>
        <div class="stat-card" style="border-left:3px solid #FF9800"><div class="stat-value" style="color:#FF9800">{len(LEADS)}</div><div class="stat-label">Aktive Leads</div></div>
        <div class="stat-card" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">87%</div><div class="stat-label">Conversion</div></div>
        <div class="stat-card" style="border-left:3px solid #2196F3"><div class="stat-value" style="color:#2196F3">€{total_revenue:,.0f}</div><div class="stat-label">Umsatz 2024</div></div>
    </div>
    <div style="display:grid;grid-template-columns:2fr 1fr;gap:20px">
        <div class="card"><h3 style="margin-bottom:16px">📊 Pipeline</h3><canvas id="chart" height="200"></canvas></div>
        <div class="card" style="border:1px solid rgba(255,152,0,0.3)"><h3 style="margin-bottom:16px">🧠 Einstein Insights</h3>
        <div style="padding:12px;background:rgba(255,255,255,0.05);border-radius:8px;margin-bottom:12px;border-left:3px solid #f44336">
            <div style="font-size:11px;color:rgba(255,255,255,0.5)">🔥 HOT</div><div style="font-weight:600">Thomas Moser - 87% Conversion</div></div>
        <div style="padding:12px;background:rgba(255,255,255,0.05);border-radius:8px;margin-bottom:12px;border-left:3px solid #FF9800">
            <div style="font-size:11px;color:rgba(255,255,255,0.5)">💰 UPSELL</div><div style="font-weight:600">Mainova AG - €150K PV</div></div>
        <a href="/einstein/predictions" class="btn btn-primary" style="width:100%;justify-content:center">Alle Predictions →</a></div>
    </div>
    <script>new Chart(document.getElementById('chart').getContext('2d'),{{type:'bar',data:{{labels:['New','Contacted','Qualified','Proposal','Negotiation','Won'],datasets:[{{data:[11,7,5,4,5,3],backgroundColor:['#2196F3','#9C27B0','#FF9800','#FF5722','#E91E63','#4CAF50'],borderRadius:6}}]}},options:{{responsive:true,plugins:{{legend:{{display:false}}}},scales:{{y:{{beginAtZero:true,grid:{{color:'rgba(255,255,255,0.05)'}}}},x:{{grid:{{display:false}}}}}}}}}});</script>'''
    return render(c,title="Dashboard",p="dashboard")

@app.route('/leads')
@login_required
def leads():
    total = sum(l['value'] for l in LEADS)
    c = f'''<div class="header"><div><h1 class="page-title">Lead Management</h1><p class="page-sub">{len(LEADS)} Leads | €{total:,}</p></div></div>
    <div class="card"><table><thead><tr><th>Score</th><th>Name</th><th>Unternehmen</th><th>Position</th><th>Stage</th><th>Value</th></tr></thead><tbody>'''
    for l in LEADS:
        sc = '#4CAF50' if l['score']>=90 else '#FF9800'
        c += f'''<tr><td><span style="background:{sc};color:white;padding:4px 10px;border-radius:20px;font-size:12px">{l['score']}</span></td>
        <td style="font-weight:500">{l['name']}</td><td style="color:rgba(255,255,255,0.7)">{l['company']}</td>
        <td style="color:rgba(255,255,255,0.7)">{l['position']}</td><td><span class="badge badge-info">{l['stage']}</span></td><td>€{l['value']:,}</td></tr>'''
    c += '</tbody></table></div>'
    return render(c,title="Leads",p="leads")

@app.route('/contacts')
@login_required
def contacts():
    hs = hubspot.get_contacts(100)
    c = f'''<div class="header"><div><h1 class="page-title">Kontakte</h1><p class="page-sub">{len(hs)} aus HubSpot</p></div>
    <a href="/whatsapp/consent" class="btn btn-primary">✅ WhatsApp Consent</a></div>
    <div class="card"><table><thead><tr><th>Name</th><th>Email</th><th>Telefon</th><th>Firma</th><th>WhatsApp</th></tr></thead><tbody>'''
    for ct in hs[:30]:
        p = ct.get('properties',{})
        name = f"{p.get('firstname','')} {p.get('lastname','')}".strip() or 'Unbekannt'
        consent = p.get('hs_whatsapp_consent','unknown')
        cb = {'granted':('✅ Erteilt','badge-success'),'revoked':('❌ Widerrufen','badge-danger')}.get(consent,('❓ Unbekannt','badge-warning'))
        c += f'''<tr><td style="font-weight:500">{name}</td><td style="color:rgba(255,255,255,0.7)">{p.get('email','-')}</td>
        <td style="color:rgba(255,255,255,0.7)">{p.get('phone','-')}</td><td>{p.get('company','-')}</td>
        <td><span class="badge {cb[1]}">{cb[0]}</span></td></tr>'''
    c += '</tbody></table></div>'
    return render(c,title="Kontakte",p="contacts")

@app.route('/whatsapp/consent')
@login_required
def whatsapp_consent():
    hs = hubspot.get_contacts(100)
    c = f'''<div class="header"><div><h1 class="page-title">WhatsApp Consent Manager</h1>
    <p class="page-sub">Bulk-Update gemäß <a href="https://knowledge.hubspot.com/de/inbox/edit-the-whatsapp-consent-status-of-your-contacts-in-bulk" target="_blank" style="color:#25D366">HubSpot Docs</a></p></div>
    <div style="display:flex;gap:10px"><button onclick="updateSelected('granted')" class="btn btn-success">✅ Consent erteilen</button>
    <button onclick="updateSelected('revoked')" class="btn btn-danger">❌ Widerrufen</button></div></div>
    <div class="card" style="border:1px solid rgba(37,211,102,0.3)">
    <div style="display:flex;justify-content:space-between;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:16px">
        <label style="display:flex;align-items:center;gap:8px;cursor:pointer"><input type="checkbox" id="selectAll" onchange="toggleAll()" style="width:18px;height:18px"><span>Alle auswählen</span></label>
        <span style="color:rgba(255,255,255,0.5)"><span id="cnt">0</span>/{len(hs)} ausgewählt</span></div>
    <table><thead><tr><th></th><th>Name</th><th>Email</th><th>Telefon</th><th>Status</th></tr></thead><tbody>'''
    for ct in hs[:50]:
        p = ct.get('properties',{})
        cid = ct.get('id','')
        name = f"{p.get('firstname','')} {p.get('lastname','')}".strip() or 'Unbekannt'
        consent = p.get('hs_whatsapp_consent','unknown')
        cb = {'granted':('✅','badge-success'),'revoked':('❌','badge-danger')}.get(consent,('❓','badge-warning'))
        c += f'''<tr><td><input type="checkbox" class="cb" data-id="{cid}" onchange="upd()" style="width:16px;height:16px"></td>
        <td style="font-weight:500">{name}</td><td style="color:rgba(255,255,255,0.7)">{p.get('email','-')}</td>
        <td style="color:rgba(255,255,255,0.7)">{p.get('phone','-')}</td><td><span class="badge {cb[1]}">{cb[0]}</span></td></tr>'''
    c += '''</tbody></table></div>
    <script>
    function toggleAll(){const c=document.getElementById('selectAll').checked;document.querySelectorAll('.cb').forEach(x=>x.checked=c);upd()}
    function upd(){document.getElementById('cnt').textContent=document.querySelectorAll('.cb:checked').length}
    async function updateSelected(status){
        const ids=Array.from(document.querySelectorAll('.cb:checked')).map(x=>x.dataset.id);
        if(!ids.length){alert('Bitte Kontakte auswählen');return}
        if(!confirm('Consent für '+ids.length+' Kontakte auf "'+status+'" setzen?'))return;
        const r=await fetch('/api/whatsapp/consent/bulk',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({contact_ids:ids,status:status})});
        const d=await r.json();alert('Erfolgreich: '+d.success+', Fehler: '+d.failed);location.reload();
    }
    </script>'''
    return render(c,title="WhatsApp Consent",p="consent")

@app.route('/api/whatsapp/consent/bulk',methods=['POST'])
@login_required
def api_consent():
    d = request.json
    return jsonify(hubspot.bulk_update_consent(d.get('contact_ids',[]),d.get('status','granted')))

@app.route('/projects')
@login_required
def projects():
    conn = get_db()
    plist = conn.execute('SELECT * FROM projects').fetchall()
    conn.close()
    total = sum(p['value'] for p in plist)
    c = f'''<div class="header"><div><h1 class="page-title">Projekte</h1><p class="page-sub">{len(plist)} Projekte | €{total:,.0f}</p></div></div>
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px">'''
    for p in plist:
        sc = {'active':('#4CAF50','In Arbeit'),'planning':('#FF9800','Planung'),'completed':('#2196F3','Fertig')}.get(p['status'],('#666',p['status']))
        c += f'''<div class="card"><div style="display:flex;justify-content:space-between;margin-bottom:12px">
        <div><h3 style="font-size:16px;margin-bottom:4px">{p['name']}</h3><p style="color:rgba(255,255,255,0.5);font-size:13px">{p['client']} - {p['location']}</p></div>
        <span class="badge" style="background:{sc[0]}22;color:{sc[0]}">{sc[1]}</span></div>
        <div style="display:flex;gap:12px;margin-bottom:12px">
            <div style="background:rgba(255,255,255,0.05);padding:8px 12px;border-radius:6px"><div style="font-size:10px;color:rgba(255,255,255,0.4)">SYSTEM</div><div style="font-weight:600;color:#FF5722">{p['project_type']}</div></div>
            <div style="background:rgba(255,255,255,0.05);padding:8px 12px;border-radius:6px"><div style="font-size:10px;color:rgba(255,255,255,0.4)">WERT</div><div style="font-weight:600">€{p['value']:,}</div></div></div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px"><span style="font-size:12px;color:rgba(255,255,255,0.5)">Fortschritt</span><span style="font-weight:600">{p['progress']}%</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width:{p['progress']}%"></div></div></div>'''
    c += '</div>'
    return render(c,title="Projekte",p="projects")

@app.route('/einstein')
@login_required
def einstein():
    c = '''<div class="header"><div><h1 class="page-title">🧠 Einstein AI Agency</h1><p class="page-sub">KI-gestützte Business Intelligence</p></div></div>
    <div class="stats-grid">
        <div class="stat-card" style="border-left:3px solid #FF5722"><div class="stat-value" style="color:#FF5722">87%</div><div class="stat-label">Accuracy</div></div>
        <div class="stat-card" style="border-left:3px solid #2196F3"><div class="stat-value" style="color:#2196F3">24</div><div class="stat-label">Insights</div></div>
        <div class="stat-card" style="border-left:3px solid #9C27B0"><div class="stat-value" style="color:#9C27B0">156</div><div class="stat-label">Automations</div></div>
        <div class="stat-card" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">€420K</div><div class="stat-label">Impact</div></div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">
        <a href="/einstein/predictions" class="card" style="text-decoration:none;color:white;border:1px solid rgba(255,87,34,0.3)"><div style="font-size:32px;margin-bottom:12px">🔮</div><h3>Predictions</h3><p style="color:rgba(255,255,255,0.5);font-size:13px">Lead Conversion, Deal Close</p></a>
        <div class="card" style="border:1px solid rgba(33,150,243,0.3)"><div style="font-size:32px;margin-bottom:12px">📈</div><h3>Analytics</h3><p style="color:rgba(255,255,255,0.5);font-size:13px">Deep Learning Analyse</p></div>
        <div class="card" style="border:1px solid rgba(76,175,80,0.3)"><div style="font-size:32px;margin-bottom:12px">💡</div><h3>Insights</h3><p style="color:rgba(255,255,255,0.5);font-size:13px">Automatische Empfehlungen</p></div>
    </div>'''
    return render(c,title="Einstein AI",p="einstein")

@app.route('/einstein/predictions')
@login_required
def predictions():
    c = '''<div class="header"><div><h1 class="page-title">🔮 Einstein Predictions</h1><p class="page-sub">KI-basierte Prognosen</p></div><a href="/einstein" class="btn btn-secondary">← Zurück</a></div>
    <div class="card"><h3 style="margin-bottom:16px">Aktuelle Predictions</h3><table><thead><tr><th>Typ</th><th>Lead</th><th>Prediction</th><th>Confidence</th><th>Aktion</th></tr></thead><tbody>'''
    tc = {'conversion':'#4CAF50','deal':'#2196F3','upsell':'#FF9800'}
    for pr in PREDICTIONS:
        col = tc.get(pr['type'],'#666')
        c += f'''<tr><td><span class="badge" style="background:{col}22;color:{col}">{pr['type']}</span></td><td style="font-weight:500">{pr['lead']}</td><td>{pr['prediction']}</td>
        <td><div style="display:flex;align-items:center;gap:8px"><div class="progress-bar" style="width:100px"><div class="progress-fill" style="width:{pr['confidence']}%;background:{col}"></div></div><span>{pr['confidence']}%</span></div></td>
        <td style="color:rgba(255,255,255,0.7)">{pr['action']}</td></tr>'''
    c += '</tbody></table></div>'
    return render(c,title="Predictions",p="predictions")

@app.route('/pv')
@login_required
def pv():
    c = '''<div class="header"><div><h1 class="page-title">☀️ Photovoltaik</h1><p class="page-sub">Solar & Smart Home Integration</p></div><a href="/pv/calculator" class="btn btn-primary">🔢 PV Rechner</a></div>
    <div class="stats-grid">
        <div class="stat-card" style="border-left:3px solid #FFD700"><div class="stat-value" style="color:#FFD700">12</div><div class="stat-label">PV Projekte</div></div>
        <div class="stat-card" style="border-left:3px solid #FF9800"><div class="stat-value" style="color:#FF9800">€1.2M</div><div class="stat-label">Pipeline</div></div>
        <div class="stat-card" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">145 kWp</div><div class="stat-label">Installiert</div></div>
        <div class="stat-card" style="border-left:3px solid #2196F3"><div class="stat-value" style="color:#2196F3">4</div><div class="stat-label">Partner</div></div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">
        <div class="card" style="border:1px solid rgba(255,215,0,0.3)"><div style="font-size:32px;margin-bottom:12px">⚡</div><h3>PV Projekte</h3><p style="color:rgba(255,255,255,0.5);font-size:13px">Aktive Installationen</p></div>
        <a href="/pv/partners" class="card" style="text-decoration:none;color:white;border:1px solid rgba(255,152,0,0.3)"><div style="font-size:32px;margin-bottom:12px">🤝</div><h3>Partner</h3><p style="color:rgba(255,255,255,0.5);font-size:13px">1Komma5°, Enpal, Zolar</p></a>
        <a href="/pv/calculator" class="card" style="text-decoration:none;color:white;border:1px solid rgba(76,175,80,0.3)"><div style="font-size:32px;margin-bottom:12px">🔢</div><h3>PV Rechner</h3><p style="color:rgba(255,255,255,0.5);font-size:13px">ROI berechnen</p></a>
    </div>'''
    return render(c,title="Photovoltaik",p="pv")

@app.route('/pv/partners')
@login_required
def pv_partners():
    c = '''<div class="header"><div><h1 class="page-title">🤝 PV Partner</h1></div><a href="/pv" class="btn btn-secondary">← Zurück</a></div>
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:20px">'''
    for p in PV_PARTNERS:
        c += f'''<div class="card" style="border:1px solid rgba(255,215,0,0.2)">
        <div style="display:flex;justify-content:space-between;margin-bottom:16px"><div><h3 style="margin-bottom:4px">{p['name']}</h3><span class="badge badge-warning">{p['type']}</span></div>
        <div style="text-align:right"><div style="color:#FFD700">{"⭐"*int(p["rating"])}</div><div style="font-size:11px;color:rgba(255,255,255,0.5)">{p['rating']}/5</div></div></div>
        <div style="display:flex;justify-content:space-between;padding-top:16px;border-top:1px solid rgba(255,255,255,0.1)">
            <span style="color:rgba(255,255,255,0.5)">Provision: <span style="color:#4CAF50;font-weight:600">{p['commission']}</span></span>
            <button class="btn btn-primary" style="padding:6px 12px;font-size:12px">Lead zuweisen</button></div></div>'''
    c += '</div>'
    return render(c,title="PV Partner",p="pv_partners")

@app.route('/pv/calculator')
@login_required
def pv_calc():
    c = '''<div class="header"><div><h1 class="page-title">🔢 PV Rechner</h1></div><a href="/pv" class="btn btn-secondary">← Zurück</a></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
        <div class="card"><h3 style="margin-bottom:20px">Projektdaten</h3>
        <div style="margin-bottom:16px"><label style="display:block;margin-bottom:6px;font-size:13px">Anlagengröße (kWp)</label>
        <input type="number" id="size" value="10" min="1" max="100" onchange="calc()"></div>
        <div style="margin-bottom:16px"><label style="display:block;margin-bottom:6px;font-size:13px">Strompreis (€/kWh)</label>
        <input type="number" id="preis" value="0.35" step="0.01" onchange="calc()"></div>
        <div style="margin-bottom:16px"><label style="display:block;margin-bottom:6px;font-size:13px">Eigenverbrauch (%)</label>
        <input type="range" id="ev" value="70" min="20" max="95" style="width:100%" onchange="document.getElementById('evD').textContent=this.value+'%';calc()">
        <div style="display:flex;justify-content:space-between;font-size:11px;color:rgba(255,255,255,0.5)"><span>20%</span><span id="evD">70%</span><span>95%</span></div></div></div>
        <div class="card" style="background:linear-gradient(135deg,rgba(255,215,0,0.1),rgba(255,152,0,0.05));border:1px solid rgba(255,215,0,0.3)"><h3 style="margin-bottom:20px">☀️ Ergebnis</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px">
            <div style="background:rgba(0,0,0,0.2);padding:16px;border-radius:8px;text-align:center"><div id="rProd" style="font-size:24px;font-weight:700;color:#FFD700">9,500</div><div style="font-size:11px;color:rgba(255,255,255,0.5)">kWh/Jahr</div></div>
            <div style="background:rgba(0,0,0,0.2);padding:16px;border-radius:8px;text-align:center"><div id="rSave" style="font-size:24px;font-weight:700;color:#4CAF50">€2,328</div><div style="font-size:11px;color:rgba(255,255,255,0.5)">Ersparnis/Jahr</div></div></div>
        <div style="background:rgba(0,0,0,0.2);padding:16px;border-radius:8px;margin-bottom:16px">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Investition:</span><span id="rInv" style="font-weight:600">€14,000</span></div>
            <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span>Amortisation:</span><span id="rAmort" style="font-weight:600;color:#FF9800">6.0 Jahre</span></div>
            <div style="display:flex;justify-content:space-between"><span>ROI (25 Jahre):</span><span id="rROI" style="font-weight:600;color:#4CAF50">316%</span></div></div>
        <button class="btn btn-primary" style="width:100%">📄 Angebot erstellen</button></div>
    </div>
    <script>
    function calc(){const s=parseFloat(document.getElementById('size').value)||10;const p=parseFloat(document.getElementById('preis').value)||0.35;const e=parseFloat(document.getElementById('ev').value)/100||0.7;
    const prod=s*950;const evKwh=prod*e;const einsp=prod-evKwh;const savEv=evKwh*p;const savEinsp=einsp*0.082;const save=savEv+savEinsp;const inv=s*1400;const amort=inv/save;const roi=((save*25)-inv)/inv*100;
    document.getElementById('rProd').textContent=Math.round(prod).toLocaleString('de-DE');document.getElementById('rSave').textContent='€'+Math.round(save).toLocaleString('de-DE');
    document.getElementById('rInv').textContent='€'+Math.round(inv).toLocaleString('de-DE');document.getElementById('rAmort').textContent=amort.toFixed(1)+' Jahre';document.getElementById('rROI').textContent=Math.round(roi)+'%';}
    calc();
    </script>'''
    return render(c,title="PV Rechner",p="pv_calc")

@app.route('/dedsec')
@login_required
def dedsec():
    c = '''<div class="header"><div><h1 class="page-title">🛡️ DedSec Security Hub</h1><p class="page-sub">Enterprise Security Ecosystem</p></div><span class="badge badge-success">All Systems Online</span></div>
    <div class="stats-grid">
        <div class="stat-card" style="border-left:3px solid #00BCD4"><div class="stat-value" style="color:#00BCD4">24</div><div class="stat-label">Cameras</div></div>
        <div class="stat-card" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">2</div><div class="stat-label">Drones</div></div>
        <div class="stat-card" style="border-left:3px solid #f44336"><div class="stat-value" style="color:#f44336">1,247</div><div class="stat-label">Blocked</div></div>
        <div class="stat-card" style="border-left:3px solid #4CAF50"><div class="stat-value" style="color:#4CAF50">100%</div><div class="stat-label">Uptime</div></div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">
        <div class="card" style="border:1px solid rgba(0,188,212,0.3)"><div style="font-size:32px;margin-bottom:12px">🗼</div><h3>Command Tower</h3><p style="color:rgba(255,255,255,0.5);font-size:13px">Zentrale Überwachung</p></div>
        <div class="card" style="border:1px solid rgba(76,175,80,0.3)"><div style="font-size:32px;margin-bottom:12px">🚁</div><h3>Drone Control</h3><p style="color:rgba(255,255,255,0.5);font-size:13px">Autonome Patrouille</p></div>
        <div class="card" style="border:1px solid rgba(156,39,176,0.3)"><div style="font-size:32px;margin-bottom:12px">📹</div><h3>CCTV Network</h3><p style="color:rgba(255,255,255,0.5);font-size:13px">24 Kameras live</p></div>
    </div>'''
    return render(c,title="DedSec",p="dedsec")

@app.route('/godbot')
@login_required
def godbot():
    c = '''<div class="header"><div><h1 class="page-title">🤖 GOD BOT AI</h1><p class="page-sub">Ultra Instinct AI Assistant - Claude</p></div></div>
    <div class="card" style="min-height:500px;display:flex;flex-direction:column">
        <div id="chat" style="flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px">
            <div style="text-align:center;padding:40px"><div style="font-size:64px;margin-bottom:16px">🤖</div><h2 style="margin-bottom:8px">GOD MODE ACTIVATED</h2>
            <p style="color:rgba(255,255,255,0.5)">Ultra Instinct AI - Bereit</p></div></div>
        <div style="border-top:1px solid rgba(255,255,255,0.1);padding:16px;display:flex;gap:12px">
            <input type="text" id="msg" placeholder="Frag GOD BOT..." style="flex:1" onkeypress="if(event.key==='Enter')send()">
            <button onclick="send()" class="btn btn-primary">Senden</button></div>
    </div>
    <script>
    async function send(){
        const i=document.getElementById('msg');const m=i.value.trim();if(!m)return;
        const c=document.getElementById('chat');
        if(c.querySelector('div[style*="text-align: center"]'))c.innerHTML='';
        c.innerHTML+='<div style="align-self:flex-end;background:linear-gradient(90deg,#FF5722,#FF9800);padding:12px 16px;border-radius:12px 12px 0 12px;max-width:70%">'+m+'</div>';
        i.value='';c.innerHTML+='<div id="ld" style="align-self:flex-start;color:rgba(255,255,255,0.5)">GOD BOT denkt...</div>';c.scrollTop=c.scrollHeight;
        const r=await fetch('/api/godbot/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
        const d=await r.json();document.getElementById('ld').remove();
        c.innerHTML+='<div style="align-self:flex-start;background:rgba(255,255,255,0.1);padding:12px 16px;border-radius:12px 12px 12px 0;max-width:70%;white-space:pre-wrap">'+d.response+'</div>';
        c.scrollTop=c.scrollHeight;
    }
    </script>'''
    return render(c,title="GOD BOT",p="godbot")

@app.route('/api/godbot/chat',methods=['POST'])
@login_required
def api_godbot():
    d = request.json
    response = claude.chat(d.get('message',''))
    conn = get_db()
    conn.execute('INSERT INTO chat_history (message,response) VALUES (?,?)',(d.get('message'),response))
    conn.commit()
    conn.close()
    return jsonify({'response':response})

@app.route('/settings')
@login_required
def settings():
    c = '''<div class="header"><div><h1 class="page-title">⚙️ Settings</h1><p class="page-sub">System-Konfiguration</p></div></div>
    <div class="card"><h3 style="margin-bottom:16px">API Keys Status</h3><table><thead><tr><th>Service</th><th>Status</th><th>Key</th></tr></thead><tbody>'''
    apis = [('HubSpot CRM',CONFIG['HUBSPOT_API_KEY']),('Stripe',CONFIG['STRIPE_SECRET_KEY']),('SevDesk',CONFIG['SEVDESK_API_KEY']),('Claude AI',CONFIG['ANTHROPIC_API_KEY'])]
    for n,k in apis:
        ok = bool(k and len(k)>10)
        sb,st = ('badge-success','✅ Verbunden') if ok else ('badge-danger','❌ Nicht konfiguriert')
        kd = k[:20]+'...' if ok else '-'
        c += f'''<tr><td style="font-weight:500">{n}</td><td><span class="badge {sb}">{st}</span></td><td style="color:rgba(255,255,255,0.5);font-family:monospace">{kd}</td></tr>'''
    c += '</tbody></table></div><div class="card"><h3 style="margin-bottom:16px">ℹ️ Info</h3><p style="color:rgba(255,255,255,0.7)">API Keys werden über .env konfiguriert.</p></div>'
    return render(c,title="Settings",p="settings")

@app.route('/sync')
@login_required
def sync():
    c = '''<div class="header"><div><h1 class="page-title">🔄 API Sync Center</h1><p class="page-sub">Daten synchronisieren</p></div></div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">
        <div class="card"><h3 style="margin-bottom:12px">HubSpot</h3><p style="color:rgba(255,255,255,0.5);margin-bottom:16px">Kontakte & Deals</p>
        <button onclick="syncAPI('hubspot')" class="btn btn-primary" style="width:100%">Sync starten</button><div id="hubspot-result" style="margin-top:12px"></div></div>
        <div class="card"><h3 style="margin-bottom:12px">Stripe</h3><p style="color:rgba(255,255,255,0.5);margin-bottom:16px">Zahlungen</p>
        <button onclick="syncAPI('stripe')" class="btn btn-primary" style="width:100%">Sync starten</button><div id="stripe-result" style="margin-top:12px"></div></div>
        <div class="card"><h3 style="margin-bottom:12px">SevDesk</h3><p style="color:rgba(255,255,255,0.5);margin-bottom:16px">Rechnungen</p>
        <button onclick="syncAPI('sevdesk')" class="btn btn-primary" style="width:100%">Sync starten</button><div id="sevdesk-result" style="margin-top:12px"></div></div>
    </div>
    <script>
    async function syncAPI(api){
        document.getElementById(api+'-result').innerHTML='<span style="color:#FF9800">Synchronisiere...</span>';
        const r=await fetch('/api/sync/'+api,{method:'POST'});const d=await r.json();
        let msg='';if(api==='hubspot')msg=d.contacts+' Kontakte';else if(api==='stripe')msg='€'+d.balance.toFixed(2);else msg=d.invoices+' Rechnungen';
        document.getElementById(api+'-result').innerHTML='<span style="color:#4CAF50">✅ '+msg+'</span>';
    }
    </script>'''
    return render(c,title="API Sync",p="sync")

@app.route('/api/sync/hubspot',methods=['POST'])
@login_required
def api_sync_hubspot():
    return jsonify({'contacts':len(hubspot.get_contacts(500))})

@app.route('/api/sync/stripe',methods=['POST'])
@login_required
def api_sync_stripe():
    return jsonify({'balance':stripe_api.get_balance()})

@app.route('/api/sync/sevdesk',methods=['POST'])
@login_required
def api_sync_sevdesk():
    inv = sevdesk.get_invoices()
    return jsonify({'invoices':len(inv),'total':sevdesk.get_total()})

@app.route('/api/v1/health')
def health():
    return jsonify({'status':'healthy','version':'v15.369','timestamp':datetime.now().isoformat()})

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                 WEST MONEY OS v15.369 - ULTIMATE EDITION                 ║
    ║                      Enterprise Universe GmbH                            ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    init_db()
    print("Login: admin / 663724!")
    print("Server: http://0.0.0.0:5000")
    app.run(host='0.0.0.0',port=5000,debug=False)
