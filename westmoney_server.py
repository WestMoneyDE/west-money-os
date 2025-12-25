#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WEST MONEY OS v99.999 - DIVINE EDITION
Enterprise Universe GmbH | CEO: Ömer Hüseyin Coşkun
"""

from flask import Flask, render_template_string, jsonify, request, redirect, session
from functools import wraps
from datetime import datetime
import hashlib, sqlite3, os

app = Flask(__name__)
app.secret_key = 'westmoney-divine-2026-secret-key'

# Database
def get_db():
    conn = sqlite3.connect('westmoney.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, email TEXT, role TEXT DEFAULT 'user')''')
    c.execute('''CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, firstname TEXT, lastname TEXT, email TEXT, phone TEXT, company TEXT, lead_score INTEGER DEFAULT 0, lead_status TEXT DEFAULT 'new', whatsapp_consent TEXT DEFAULT 'not_asked', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    admin_hash = hashlib.sha256('663724!'.encode()).hexdigest()
    c.execute('INSERT OR IGNORE INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)', ('admin', admin_hash, 'info@enterprise-universe.com', 'admin'))
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# Landing Page
LANDING = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>West Money OS - Smart Home & PropTech Platform</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root{--primary:#FF5722;--gold:#FFD700;--dark:#0a0a0a;--gradient:linear-gradient(135deg,#FF5722,#FF9800,#FFD700)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:var(--dark);color:#fff;line-height:1.6}
.navbar{position:fixed;top:0;left:0;right:0;padding:20px 5%;display:flex;justify-content:space-between;align-items:center;background:rgba(10,10,10,0.95);backdrop-filter:blur(20px);z-index:1000;border-bottom:1px solid rgba(255,255,255,0.05)}
.logo{display:flex;align-items:center;gap:12px;text-decoration:none}
.logo-icon{width:48px;height:48px;background:var(--gradient);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:900}
.logo-text{font-size:24px;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-links{display:flex;gap:24px;align-items:center}
.nav-links a{color:rgba(255,255,255,0.7);text-decoration:none;font-weight:500}
.nav-links a:hover{color:var(--primary)}
.btn{padding:14px 28px;border-radius:12px;font-weight:600;text-decoration:none;display:inline-flex;align-items:center;gap:10px;transition:all 0.3s;cursor:pointer;border:none}
.btn-primary{background:var(--gradient);color:#fff;box-shadow:0 4px 20px rgba(255,87,34,0.3)}
.btn-primary:hover{transform:translateY(-4px);box-shadow:0 8px 30px rgba(255,87,34,0.5)}
.btn-outline{background:transparent;color:#fff;border:2px solid rgba(255,255,255,0.2)}
.hero{min-height:100vh;display:flex;align-items:center;padding:120px 5% 80px;position:relative}
.hero::before{content:'';position:absolute;top:-50%;right:-20%;width:80%;height:150%;background:radial-gradient(ellipse,rgba(255,87,34,0.15),transparent 60%)}
.hero-content{max-width:700px;position:relative;z-index:1}
.hero-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(255,87,34,0.1);border:1px solid rgba(255,87,34,0.3);padding:8px 16px;border-radius:50px;font-size:13px;font-weight:600;color:var(--primary);margin-bottom:24px}
.hero h1{font-size:clamp(40px,6vw,72px);font-weight:900;line-height:1.1;margin-bottom:24px;letter-spacing:-2px}
.hero h1 span{background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{font-size:20px;color:rgba(255,255,255,0.6);margin-bottom:40px}
.hero-buttons{display:flex;gap:16px;flex-wrap:wrap}
.hero-stats{display:flex;gap:48px;margin-top:60px;padding-top:40px;border-top:1px solid rgba(255,255,255,0.1)}
.stat-item h3{font-size:36px;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat-item p{font-size:14px;color:rgba(255,255,255,0.5)}
.awards{padding:40px 5%;background:rgba(255,255,255,0.02);border-top:1px solid rgba(255,255,255,0.05);border-bottom:1px solid rgba(255,255,255,0.05)}
.awards-inner{display:flex;justify-content:center;gap:60px;flex-wrap:wrap}
.award-item{display:flex;align-items:center;gap:12px;opacity:0.7}
.award-item:hover{opacity:1}
.award-icon{font-size:32px}
.award-text{font-size:13px;font-weight:600;color:rgba(255,255,255,0.6)}
.award-text span{display:block;color:var(--gold);font-size:11px}
.features{padding:120px 5%}
.section-header{text-align:center;max-width:700px;margin:0 auto 80px}
.section-header h2{font-size:48px;font-weight:800;margin-bottom:20px}
.section-header p{font-size:18px;color:rgba(255,255,255,0.6)}
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:32px;max-width:1400px;margin:0 auto}
.feature-card{background:linear-gradient(135deg,#1a1a2e,rgba(15,15,26,0.8));border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:40px;transition:all 0.4s}
.feature-card:hover{transform:translateY(-8px);border-color:rgba(255,87,34,0.3);box-shadow:0 20px 40px rgba(0,0,0,0.3)}
.feature-icon{width:64px;height:64px;background:rgba(255,87,34,0.1);border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:28px;margin-bottom:24px}
.feature-card h3{font-size:22px;font-weight:700;margin-bottom:12px}
.feature-card p{color:rgba(255,255,255,0.6);font-size:15px}
.pricing{padding:120px 5%;background:linear-gradient(180deg,#0a0a0a,#1a1a2e)}
.pricing-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px;max-width:1400px;margin:0 auto}
.pricing-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:24px;padding:40px 32px;text-align:center;transition:all 0.4s}
.pricing-card.featured{background:linear-gradient(135deg,rgba(255,87,34,0.1),rgba(255,152,0,0.05));border-color:rgba(255,87,34,0.3);transform:scale(1.05)}
.pricing-card:hover{transform:translateY(-8px);border-color:rgba(255,87,34,0.4)}
.pricing-tier{font-size:14px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--primary);margin-bottom:16px}
.pricing-price{font-size:48px;font-weight:800;margin-bottom:8px}
.pricing-price span{font-size:18px;font-weight:400;color:rgba(255,255,255,0.5)}
.pricing-features{list-style:none;text-align:left;margin:24px 0}
.pricing-features li{padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:14px;display:flex;align-items:center;gap:12px}
.pricing-features li::before{content:'✓';color:#4CAF50;font-weight:700}
.cta{padding:120px 5%;text-align:center;position:relative}
.cta::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(255,87,34,0.2),transparent 60%)}
.cta-content{position:relative;z-index:1}
.cta h2{font-size:48px;font-weight:800;margin-bottom:20px}
.cta p{font-size:20px;color:rgba(255,255,255,0.6);margin-bottom:40px}
.footer{padding:60px 5% 40px;background:rgba(0,0,0,0.5);border-top:1px solid rgba(255,255,255,0.05)}
.footer-content{max-width:1400px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:24px}
.footer p{color:rgba(255,255,255,0.5);font-size:14px}
@media(max-width:768px){.hero h1{font-size:36px}.hero-stats{flex-direction:column;gap:24px}.nav-links{display:none}.pricing-card.featured{transform:none}}
</style>
</head>
<body>
<nav class="navbar">
<a href="/" class="logo"><div class="logo-icon">W</div><span class="logo-text">West Money OS</span></a>
<div class="nav-links">
<a href="#features">Features</a>
<a href="#pricing">Preise</a>
<a href="/login" class="btn btn-outline">Login</a>
<a href="#pricing" class="btn btn-primary">Kostenlos testen</a>
</div>
</nav>

<section class="hero">
<div class="hero-content">
<div class="hero-badge">🏆 LOXONE Gold Partner 2024</div>
<h1>Die <span>Smart Home</span> & PropTech Plattform der Zukunft</h1>
<p>Verwalten Sie Leads, Projekte und Kunden mit KI-gestützter Automatisierung. Gebaut für Smart Home Integratoren.</p>
<div class="hero-buttons">
<a href="#pricing" class="btn btn-primary">🚀 14 Tage kostenlos</a>
<a href="#features" class="btn btn-outline">Features ansehen</a>
</div>
<div class="hero-stats">
<div class="stat-item"><h3>€847K+</h3><p>Umsatz verwaltet</p></div>
<div class="stat-item"><h3>250+</h3><p>Aktive Nutzer</p></div>
<div class="stat-item"><h3>99.9%</h3><p>Uptime</p></div>
</div>
</div>
</section>

<section class="awards">
<div class="awards-inner">
<div class="award-item"><div class="award-icon">🏆</div><div class="award-text">LOXONE Gold Partner<span>2024</span></div></div>
<div class="award-item"><div class="award-icon">🏅</div><div class="award-text">PropTech Germany<span>Top 50</span></div></div>
<div class="award-item"><div class="award-icon">🔒</div><div class="award-text">ISO 27001<span>Zertifiziert</span></div></div>
<div class="award-item"><div class="award-icon">✅</div><div class="award-text">DSGVO<span>Compliant</span></div></div>
<div class="award-item"><div class="award-icon">🇩🇪</div><div class="award-text">Made in Germany<span>Köln</span></div></div>
</div>
</section>

<section class="features" id="features">
<div class="section-header">
<h2>Alles was Sie brauchen</h2>
<p>Eine Plattform für Lead Management, Projektsteuerung und Kundenbeziehungen.</p>
</div>
<div class="features-grid">
<div class="feature-card"><div class="feature-icon">🧠</div><h3>HAIKU AI Scoring</h3><p>KI-gestützte Lead-Bewertung mit Claude AI. Priorisieren Sie automatisch.</p></div>
<div class="feature-card"><div class="feature-icon">🏠</div><h3>Smart Home Integration</h3><p>Native Integration mit LOXONE, KNX und anderen Systemen.</p></div>
<div class="feature-card"><div class="feature-icon">💬</div><h3>WhatsApp Business</h3><p>Meta API Integration mit Consent Management.</p></div>
<div class="feature-card"><div class="feature-icon">📊</div><h3>Einstein Analytics</h3><p>Echtzeit-Dashboards mit Umsatzprognosen.</p></div>
<div class="feature-card"><div class="feature-icon">🔄</div><h3>CRM Sync</h3><p>HubSpot, Salesforce und mehr.</p></div>
<div class="feature-card"><div class="feature-icon">🛡️</div><h3>Enterprise Security</h3><p>ISO 27001, SSO, 2FA.</p></div>
</div>
</section>

<section class="pricing" id="pricing">
<div class="section-header">
<h2>Transparente Preise</h2>
<p>Starten Sie kostenlos und skalieren Sie mit Ihrem Business.</p>
</div>
<div class="pricing-grid">
<div class="pricing-card">
<div class="pricing-tier">Starter</div>
<div class="pricing-price">€49<span>/mo</span></div>
<ul class="pricing-features"><li>5 Benutzer</li><li>500 Kontakte</li><li>Basic CRM</li><li>E-Mail Support</li></ul>
<a href="mailto:info@enterprise-universe.com?subject=Starter" class="btn btn-outline" style="width:100%">Starten</a>
</div>
<div class="pricing-card featured">
<div class="pricing-tier">Business</div>
<div class="pricing-price">€149<span>/mo</span></div>
<ul class="pricing-features"><li>25 Benutzer</li><li>5.000 Kontakte</li><li>HAIKU AI</li><li>WhatsApp</li><li>Priority Support</li></ul>
<a href="mailto:info@enterprise-universe.com?subject=Business" class="btn btn-primary" style="width:100%">Testen</a>
</div>
<div class="pricing-card">
<div class="pricing-tier">Enterprise</div>
<div class="pricing-price">€449<span>/mo</span></div>
<ul class="pricing-features"><li>Unlimited</li><li>White-Label</li><li>24/7 Support</li><li>Dedicated</li></ul>
<a href="mailto:info@enterprise-universe.com?subject=Enterprise" class="btn btn-outline" style="width:100%">Kontakt</a>
</div>
<div class="pricing-card">
<div class="pricing-tier">🔥 GOD MODE</div>
<div class="pricing-price">Custom</div>
<ul class="pricing-features"><li>Source Code</li><li>On-Premise</li><li>SLA 99.99%</li><li>Custom Dev</li></ul>
<a href="mailto:info@enterprise-universe.com?subject=GOD%20MODE" class="btn btn-outline" style="width:100%">Anfragen</a>
</div>
</div>
</section>

<section class="cta">
<div class="cta-content">
<h2>Bereit durchzustarten?</h2>
<p>14 Tage kostenlos. Keine Kreditkarte.</p>
<a href="mailto:info@enterprise-universe.com?subject=Demo" class="btn btn-primary" style="font-size:18px;padding:18px 40px">🚀 Jetzt starten</a>
</div>
</section>

<footer class="footer">
<div class="footer-content">
<a href="/" class="logo"><div class="logo-icon">W</div><span class="logo-text">West Money OS</span></a>
<p>© 2024-2026 Enterprise Universe GmbH | CEO: Ömer Hüseyin Coşkun | Köln</p>
</div>
</footer>
</body>
</html>'''

# Login Page
LOGIN = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login - West Money OS</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:linear-gradient(135deg,#0a0a0a,#1a1a2e);min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.1);border-radius:24px;padding:48px;width:100%;max-width:420px}
.logo{display:flex;align-items:center;gap:12px;justify-content:center;margin-bottom:40px}
.logo-icon{width:56px;height:56px;background:linear-gradient(135deg,#FF5722,#FF9800);border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:900;color:#fff}
.logo-text{font-size:28px;font-weight:800;background:linear-gradient(135deg,#FF5722,#FF9800);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
h2{color:#fff;text-align:center;font-size:24px;margin-bottom:8px}
.subtitle{color:rgba(255,255,255,0.5);text-align:center;font-size:14px;margin-bottom:32px}
.form-group{margin-bottom:20px}
label{display:block;color:rgba(255,255,255,0.7);font-size:13px;margin-bottom:8px}
input{width:100%;padding:14px 16px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:12px;color:#fff;font-size:15px}
input:focus{outline:none;border-color:#FF5722}
.btn{width:100%;padding:16px;background:linear-gradient(135deg,#FF5722,#FF9800);border:none;border-radius:12px;color:#fff;font-size:16px;font-weight:700;cursor:pointer}
.btn:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(255,87,34,0.4)}
.error{background:rgba(244,67,54,0.1);border:1px solid rgba(244,67,54,0.3);color:#f44336;padding:12px;border-radius:8px;margin-bottom:20px;font-size:14px}
.back{text-align:center;margin-top:24px}
.back a{color:#FF5722;text-decoration:none}
</style>
</head>
<body>
<div class="card">
<div class="logo"><div class="logo-icon">W</div><span class="logo-text">West Money OS</span></div>
<h2>Willkommen zurück</h2>
<p class="subtitle">Melden Sie sich an</p>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<form method="POST">
<div class="form-group"><label>Benutzername</label><input type="text" name="username" placeholder="admin" required></div>
<div class="form-group"><label>Passwort</label><input type="password" name="password" placeholder="••••••••" required></div>
<button type="submit" class="btn">🚀 Anmelden</button>
</form>
<p class="back"><a href="/">← Zurück zur Startseite</a></p>
</div>
</body>
</html>'''

# Dashboard
DASHBOARD = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard - West Money OS</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:#0a0a0a;color:#fff;min-height:100vh}
.sidebar{width:260px;background:#1a1a2e;position:fixed;height:100vh;padding:24px;border-right:1px solid rgba(255,255,255,0.08)}
.logo{display:flex;align-items:center;gap:12px;margin-bottom:40px}
.logo-icon{width:42px;height:42px;background:linear-gradient(135deg,#FF5722,#FF9800);border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:20px}
.logo-text{font-size:20px;font-weight:800;background:linear-gradient(135deg,#FF5722,#FF9800);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-section{margin-bottom:32px}
.nav-title{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,0.4);margin-bottom:12px;padding-left:12px}
.nav-item{display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:10px;color:rgba(255,255,255,0.7);text-decoration:none;margin-bottom:4px;transition:all 0.3s}
.nav-item:hover{background:rgba(255,255,255,0.05);color:#fff}
.nav-item.active{background:rgba(255,87,34,0.15);color:#FF5722}
.main{margin-left:260px;padding:32px}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:32px}
.header h1{font-size:28px;font-weight:800}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin-bottom:32px}
.stat-card{background:#1a1a2e;border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:24px;transition:all 0.3s}
.stat-card:hover{transform:translateY(-4px);border-color:rgba(255,87,34,0.3)}
.stat-icon{width:48px;height:48px;background:rgba(255,87,34,0.1);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:16px}
.stat-value{font-size:32px;font-weight:800;margin-bottom:4px}
.stat-label{font-size:13px;color:rgba(255,255,255,0.5)}
.card{background:#1a1a2e;border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:24px;margin-bottom:24px}
.card-title{font-size:18px;font-weight:700;margin-bottom:20px}
table{width:100%;border-collapse:collapse}
th,td{padding:14px 16px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.05)}
th{font-size:11px;text-transform:uppercase;color:rgba(255,255,255,0.4)}
.badge{padding:4px 10px;border-radius:6px;font-size:11px;font-weight:600}
.badge-success{background:rgba(76,175,80,0.2);color:#4CAF50}
.badge-warning{background:rgba(255,193,7,0.2);color:#FFC107}
.btn{padding:10px 20px;border-radius:10px;font-weight:600;text-decoration:none;display:inline-flex;align-items:center;gap:8px;cursor:pointer;border:none;transition:all 0.3s}
.btn-primary{background:linear-gradient(135deg,#FF5722,#FF9800);color:#fff}
@media(max-width:1200px){.stats-grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:768px){.sidebar{display:none}.main{margin-left:0}.stats-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<aside class="sidebar">
<div class="logo"><div class="logo-icon">W</div><span class="logo-text">West Money OS</span></div>
<div class="nav-section">
<div class="nav-title">Hauptmenü</div>
<a href="/dashboard" class="nav-item active"><span>📊</span> Dashboard</a>
<a href="/leads" class="nav-item"><span>👥</span> Leads</a>
<a href="/projects" class="nav-item"><span>📁</span> Projekte</a>
</div>
<div class="nav-section">
<div class="nav-title">Tools</div>
<a href="/einstein" class="nav-item"><span>🧠</span> Einstein AI</a>
<a href="/whatsapp" class="nav-item"><span>💬</span> WhatsApp</a>
</div>
<div class="nav-section">
<div class="nav-title">Admin</div>
<a href="/settings" class="nav-item"><span>⚙️</span> Einstellungen</a>
<a href="/logout" class="nav-item"><span>🚪</span> Logout</a>
</div>
</aside>
<main class="main">
<div class="header">
<div><h1>Dashboard</h1><p style="color:rgba(255,255,255,0.5);margin-top:4px">Willkommen, {{ username }}!</p></div>
<a href="/leads/new" class="btn btn-primary">+ Neuer Lead</a>
</div>
<div class="stats-grid">
<div class="stat-card"><div class="stat-icon">👥</div><div class="stat-value">{{ stats.leads }}</div><div class="stat-label">Aktive Leads</div></div>
<div class="stat-card"><div class="stat-icon">💬</div><div class="stat-value">{{ stats.whatsapp }}</div><div class="stat-label">WhatsApp Opt-ins</div></div>
<div class="stat-card"><div class="stat-icon">📁</div><div class="stat-value">12</div><div class="stat-label">Projekte</div></div>
<div class="stat-card"><div class="stat-icon">💰</div><div class="stat-value">€847K</div><div class="stat-label">Pipeline</div></div>
</div>
<div class="card">
<h3 class="card-title">Neueste Leads</h3>
<table>
<thead><tr><th>Name</th><th>Unternehmen</th><th>Score</th><th>Status</th></tr></thead>
<tbody>
{% for lead in leads %}
<tr>
<td><strong>{{ lead.firstname }} {{ lead.lastname }}</strong><br><span style="font-size:12px;color:rgba(255,255,255,0.5)">{{ lead.email }}</span></td>
<td>{{ lead.company or '-' }}</td>
<td>{{ lead.lead_score }}</td>
<td><span class="badge badge-{{ 'success' if lead.lead_status == 'qualified' else 'warning' }}">{{ lead.lead_status }}</span></td>
</tr>
{% endfor %}
{% if not leads %}
<tr><td colspan="4" style="text-align:center;color:rgba(255,255,255,0.5)">Keine Leads vorhanden</td></tr>
{% endif %}
</tbody>
</table>
</div>
</main>
</body>
</html>'''

# Routes
@app.route('/')
def landing():
    return render_template_string(LANDING)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE (username=? OR email=?) AND password_hash=?', (username, username, pw_hash)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')
        error = 'Ungültige Anmeldedaten'
    return render_template_string(LOGIN, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    leads_count = conn.execute('SELECT COUNT(*) FROM leads').fetchone()[0]
    whatsapp_count = conn.execute("SELECT COUNT(*) FROM leads WHERE whatsapp_consent='granted'").fetchone()[0]
    leads = conn.execute('SELECT * FROM leads ORDER BY created_at DESC LIMIT 10').fetchall()
    conn.close()
    return render_template_string(DASHBOARD, username=session.get('username', 'Admin'), stats={'leads': leads_count, 'whatsapp': whatsapp_count}, leads=leads)

@app.route('/leads')
@login_required
def leads_list():
    conn = get_db()
    leads = conn.execute('SELECT * FROM leads ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(l) for l in leads])

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'online', 'version': 'v99.999', 'name': 'West Money OS Divine Edition'})

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════╗
║     WEST MONEY OS v99.999 - DIVINE EDITION                       ║
║     Enterprise Universe GmbH | CEO: Ömer Hüseyin Coşkun          ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    init_db()
    print("✅ Database initialized")
    print("🚀 Server: http://0.0.0.0:5000")
    print("🔐 Login: admin / 663724!")
    app.run(host='0.0.0.0', port=5000, debug=False)
