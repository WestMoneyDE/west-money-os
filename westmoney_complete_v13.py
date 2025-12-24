#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WEST MONEY OS v13.0 - COMPLETE PLATFORM
========================================
Enterprise Universe GmbH
CEO: Ömer Hüseyin Coşkun
Launch: 01.01.2026

Modules:
- Dashboard & CRM
- Einstein AI Agency
- DedSec Security Ecosystem
- WhatsApp Business
- GOD BOT AI
- Enterprise Hub
"""

from flask import Flask, render_template_string, jsonify, request, redirect, url_for, session
from functools import wraps
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'westmoney-godmode-2026-enterprise-universe'

# ============================================================================
# AUTHENTICATION
# ============================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# SHARED DATA
# ============================================================================
CERTIFICATIONS = [
    {"name": "ISO 9001:2015", "type": "quality", "icon": "🏅", "desc": "Qualitätsmanagement"},
    {"name": "ISO 14001:2015", "type": "environment", "icon": "🌿", "desc": "Umweltmanagement"},
    {"name": "ISO 27001:2022", "type": "security", "icon": "🔒", "desc": "Informationssicherheit"},
    {"name": "ISO 45001:2018", "type": "safety", "icon": "⚡", "desc": "Arbeitsschutz"},
    {"name": "DSGVO Konform", "type": "privacy", "icon": "🛡️", "desc": "EU-Datenschutz"},
    {"name": "TÜV Rheinland", "type": "german", "icon": "✅", "desc": "Geprüfte Sicherheit"},
    {"name": "LOXONE Platinum", "type": "partner", "icon": "🏠", "desc": "Smart Home Partner"},
    {"name": "KNX Certified", "type": "partner", "icon": "🔌", "desc": "Bus-System Zertifiziert"},
]

AWARDS = [
    {"name": "Top Smart Home Company 2024", "org": "Smart Home Awards", "icon": "🏆"},
    {"name": "Innovation Award Rhein-Main", "org": "IHK Frankfurt", "icon": "💡"},
    {"name": "Best PropTech Startup DACH", "org": "PropTech Summit", "icon": "🚀"},
    {"name": "Digital Pioneer Award", "org": "Digitalverband", "icon": "⭐"},
    {"name": "Green Building Excellence", "org": "DGNB", "icon": "🌱"},
]

LEADS_DATA = [
    {"id": 1, "name": "Thomas Moser", "company": "Loxone Electronics", "position": "Gründer", "score": 96, "stage": "contacted", "value": 500000},
    {"id": 2, "name": "Martin Öller", "company": "Loxone Electronics", "position": "Gründer", "score": 96, "stage": "contacted", "value": 500000},
    {"id": 3, "name": "Rüdiger Keinberger", "company": "Loxone Electronics", "position": "CEO", "score": 95, "stage": "contacted", "value": 450000},
    {"id": 4, "name": "Dr. Michael Maxelon", "company": "Mainova AG", "position": "Vorstandsvorsitzender", "score": 95, "stage": "qualified", "value": 380000},
    {"id": 5, "name": "Max Hofmann", "company": "Hofmann Bau AG", "position": "Vorstand", "score": 94, "stage": "won", "value": 345000},
    {"id": 6, "name": "Frank Junker", "company": "ABG Frankfurt Holding", "position": "Vors. GF", "score": 92, "stage": "proposal", "value": 420000},
    {"id": 7, "name": "Adam Irányi", "company": "Union Investment RE", "position": "Head of Investment", "score": 92, "stage": "contacted", "value": 280000},
    {"id": 8, "name": "Anna Müller", "company": "Smart Home Bayern", "position": "GF", "score": 91, "stage": "won", "value": 156000},
    {"id": 9, "name": "Tino Kugler", "company": "Loxone Deutschland", "position": "MD", "score": 90, "stage": "negotiation", "value": 220000},
    {"id": 10, "name": "Markus Fuhrmann", "company": "Gropyus", "position": "Gründer", "score": 90, "stage": "qualified", "value": 350000},
]

EINSTEIN_PREDICTIONS = [
    {"type": "lead_conversion", "prediction": "87% Wahrscheinlichkeit", "lead": "Thomas Moser", "confidence": 87},
    {"type": "deal_close", "prediction": "Q1 2026 Abschluss", "lead": "Hofmann Bau AG", "confidence": 92},
    {"type": "upsell", "prediction": "€150k zusätzlich möglich", "lead": "Mainova AG", "confidence": 78},
    {"type": "churn_risk", "prediction": "Niedriges Risiko", "lead": "Smart Home Bayern", "confidence": 95},
    {"type": "best_contact", "prediction": "Dienstag 10:00 Uhr", "lead": "Loxone Electronics", "confidence": 83},
]

DEDSEC_SYSTEMS = [
    {"id": "tower-01", "name": "Command Tower Frankfurt", "status": "online", "alerts": 0, "cameras": 24},
    {"id": "drone-01", "name": "Patrol Drone Alpha", "status": "active", "battery": 87, "location": "Sector A"},
    {"id": "drone-02", "name": "Patrol Drone Beta", "status": "charging", "battery": 23, "location": "Base"},
    {"id": "firewall-01", "name": "Cyber Shield Main", "status": "active", "blocked": 1247, "threats": 3},
    {"id": "vault-01", "name": "Secure Vault Primary", "status": "locked", "files": 892, "encrypted": True},
]

# ============================================================================
# BASE TEMPLATE
# ============================================================================
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Inter', sans-serif; 
            background: {{ bg_color|default('#0a0a0a') }}; 
            color: {{ text_color|default('#ffffff') }}; 
            min-height: 100vh;
        }
        
        /* Sidebar */
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
            border-right: 1px solid rgba(255,255,255,0.1);
            padding: 20px;
            overflow-y: auto;
            z-index: 1000;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        
        .logo-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #FF5722, #FF9800);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        
        .logo-text {
            font-size: 20px;
            font-weight: 700;
            background: linear-gradient(90deg, #FF5722, #FFD700);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .nav-section {
            margin-bottom: 24px;
        }
        
        .nav-section-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: rgba(255,255,255,0.4);
            margin-bottom: 12px;
            padding-left: 12px;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border-radius: 10px;
            color: rgba(255,255,255,0.7);
            text-decoration: none;
            transition: all 0.3s ease;
            margin-bottom: 4px;
        }
        
        .nav-item:hover, .nav-item.active {
            background: rgba(255,87,34,0.15);
            color: #FF5722;
        }
        
        .nav-item.active {
            background: linear-gradient(90deg, rgba(255,87,34,0.2), transparent);
            border-left: 3px solid #FF5722;
        }
        
        .nav-icon {
            width: 20px;
            text-align: center;
        }
        
        /* Main Content */
        .main-content {
            margin-left: 280px;
            padding: 30px;
            min-height: 100vh;
        }
        
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .page-title {
            font-size: 28px;
            font-weight: 700;
        }
        
        .page-subtitle {
            color: rgba(255,255,255,0.6);
            margin-top: 4px;
        }
        
        /* Cards */
        .card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, rgba(255,87,34,0.1), rgba(255,152,0,0.05));
            border: 1px solid rgba(255,87,34,0.2);
            border-radius: 16px;
            padding: 24px;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(90deg, #FF5722, #FFD700);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-label {
            color: rgba(255,255,255,0.6);
            margin-top: 4px;
        }
        
        .stat-change {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 8px;
        }
        
        .stat-change.positive {
            background: rgba(76,175,80,0.2);
            color: #4CAF50;
        }
        
        .stat-change.negative {
            background: rgba(244,67,54,0.2);
            color: #F44336;
        }
        
        /* Tables */
        .table-container {
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 14px 16px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        th {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: rgba(255,255,255,0.5);
            font-weight: 500;
        }
        
        tr:hover {
            background: rgba(255,255,255,0.02);
        }
        
        /* Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .badge-success { background: rgba(76,175,80,0.2); color: #4CAF50; }
        .badge-warning { background: rgba(255,152,0,0.2); color: #FF9800; }
        .badge-danger { background: rgba(244,67,54,0.2); color: #F44336; }
        .badge-info { background: rgba(33,150,243,0.2); color: #2196F3; }
        .badge-purple { background: rgba(156,39,176,0.2); color: #9C27B0; }
        
        /* Buttons */
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: all 0.3s ease;
            text-decoration: none;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #FF5722, #FF9800);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255,87,34,0.4);
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* Progress Bar */
        .progress-bar {
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        /* Score Badge */
        .score-badge {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 14px;
        }
        
        .score-high { background: linear-gradient(135deg, #4CAF50, #8BC34A); }
        .score-medium { background: linear-gradient(135deg, #FF9800, #FFC107); }
        .score-low { background: linear-gradient(135deg, #F44336, #E91E63); }
        
        /* Certifications Grid */
        .cert-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }
        
        .cert-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .cert-card:hover {
            transform: translateY(-4px);
            border-color: #FF5722;
        }
        
        .cert-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }
        
        .cert-name {
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .cert-desc {
            font-size: 12px;
            color: rgba(255,255,255,0.5);
        }
        
        /* DedSec Theme */
        .dedsec-glow {
            text-shadow: 0 0 10px #00D4FF, 0 0 20px #00D4FF;
        }
        
        .dedsec-card {
            background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(0,255,65,0.05));
            border: 1px solid rgba(0,212,255,0.3);
        }
        
        /* Einstein Theme */
        .einstein-card {
            background: linear-gradient(135deg, rgba(156,39,176,0.1), rgba(103,58,183,0.05));
            border: 1px solid rgba(156,39,176,0.3);
        }
        
        /* Animations */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulse { animation: pulse 2s infinite; }
        
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 5px rgba(255,87,34,0.5); }
            50% { box-shadow: 0 0 20px rgba(255,87,34,0.8); }
        }
        
        .glow { animation: glow 2s infinite; }
        
        /* Responsive */
        @media (max-width: 1024px) {
            .sidebar { width: 80px; padding: 10px; }
            .logo-text, .nav-text, .nav-section-title { display: none; }
            .main-content { margin-left: 80px; }
            .nav-item { justify-content: center; padding: 12px; }
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <nav class="sidebar">
        <div class="logo">
            <div class="logo-icon">⚡</div>
            <div>
                <div class="logo-text">West Money</div>
                <div style="font-size: 10px; color: rgba(255,255,255,0.5);">OS v13.0</div>
            </div>
        </div>
        
        <div class="nav-section">
            <div class="nav-section-title">Main</div>
            <a href="/dashboard" class="nav-item {{ 'active' if active_page == 'dashboard' else '' }}">
                <span class="nav-icon">📊</span>
                <span class="nav-text">Dashboard</span>
            </a>
            <a href="/dashboard/leads" class="nav-item {{ 'active' if active_page == 'leads' else '' }}">
                <span class="nav-icon">👥</span>
                <span class="nav-text">Leads</span>
            </a>
            <a href="/dashboard/projects" class="nav-item {{ 'active' if active_page == 'projects' else '' }}">
                <span class="nav-icon">🏗️</span>
                <span class="nav-text">Projekte</span>
            </a>
        </div>
        
        <div class="nav-section">
            <div class="nav-section-title">Einstein AI</div>
            <a href="/einstein" class="nav-item {{ 'active' if active_page == 'einstein' else '' }}">
                <span class="nav-icon">🧠</span>
                <span class="nav-text">Einstein Home</span>
            </a>
            <a href="/einstein/predictions" class="nav-item {{ 'active' if active_page == 'predictions' else '' }}">
                <span class="nav-icon">🔮</span>
                <span class="nav-text">Predictions</span>
            </a>
            <a href="/einstein/analytics" class="nav-item {{ 'active' if active_page == 'analytics' else '' }}">
                <span class="nav-icon">📈</span>
                <span class="nav-text">Analytics</span>
            </a>
            <a href="/einstein/insights" class="nav-item {{ 'active' if active_page == 'insights' else '' }}">
                <span class="nav-icon">💡</span>
                <span class="nav-text">Insights</span>
            </a>
        </div>
        
        <div class="nav-section">
            <div class="nav-section-title">DedSec Security</div>
            <a href="/dedsec" class="nav-item {{ 'active' if active_page == 'dedsec' else '' }}">
                <span class="nav-icon">🛡️</span>
                <span class="nav-text">Security Hub</span>
            </a>
            <a href="/dedsec/tower" class="nav-item {{ 'active' if active_page == 'tower' else '' }}">
                <span class="nav-icon">🗼</span>
                <span class="nav-text">Tower</span>
            </a>
            <a href="/dedsec/drones" class="nav-item {{ 'active' if active_page == 'drones' else '' }}">
                <span class="nav-icon">🚁</span>
                <span class="nav-text">Drones</span>
            </a>
            <a href="/dedsec/cctv" class="nav-item {{ 'active' if active_page == 'cctv' else '' }}">
                <span class="nav-icon">📹</span>
                <span class="nav-text">CCTV</span>
            </a>
        </div>
        
        <div class="nav-section">
            <div class="nav-section-title">Tools</div>
            <a href="/whatsapp" class="nav-item {{ 'active' if active_page == 'whatsapp' else '' }}">
                <span class="nav-icon">💬</span>
                <span class="nav-text">WhatsApp</span>
            </a>
            <a href="/godbot" class="nav-item {{ 'active' if active_page == 'godbot' else '' }}">
                <span class="nav-icon">🤖</span>
                <span class="nav-text">GOD BOT</span>
            </a>
            <a href="/locker" class="nav-item {{ 'active' if active_page == 'locker' else '' }}">
                <span class="nav-icon">🔐</span>
                <span class="nav-text">Locker</span>
            </a>
        </div>
        
        <div class="nav-section" style="margin-top: auto; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
            <a href="/logout" class="nav-item">
                <span class="nav-icon">🚪</span>
                <span class="nav-text">Logout</span>
            </a>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>
    
    <script>
        // Global JS utilities
        function formatCurrency(value) {
            return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value);
        }
        
        function formatNumber(value) {
            return new Intl.NumberFormat('de-DE').format(value);
        }
    </script>
</body>
</html>
'''

# ============================================================================
# ROUTES - AUTHENTICATION
# ============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '663724':
            session['logged_in'] = True
            session['user'] = 'Ömer Hüseyin Coşkun'
            return redirect('/dashboard')
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login | West Money OS</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-card {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 24px;
                padding: 48px;
                width: 100%;
                max-width: 420px;
                backdrop-filter: blur(10px);
            }
            .logo {
                text-align: center;
                margin-bottom: 32px;
            }
            .logo-icon {
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #FF5722, #FF9800);
                border-radius: 20px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 40px;
                margin-bottom: 16px;
            }
            .logo-text {
                font-size: 28px;
                font-weight: 700;
                background: linear-gradient(90deg, #FF5722, #FFD700);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .logo-sub {
                color: rgba(255,255,255,0.5);
                font-size: 14px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                color: rgba(255,255,255,0.7);
                margin-bottom: 8px;
                font-size: 14px;
            }
            input {
                width: 100%;
                padding: 14px 16px;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 12px;
                color: white;
                font-size: 16px;
                transition: all 0.3s ease;
            }
            input:focus {
                outline: none;
                border-color: #FF5722;
                background: rgba(255,87,34,0.1);
            }
            button {
                width: 100%;
                padding: 16px;
                background: linear-gradient(135deg, #FF5722, #FF9800);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(255,87,34,0.4);
            }
            .divider {
                display: flex;
                align-items: center;
                margin: 24px 0;
                color: rgba(255,255,255,0.3);
                font-size: 12px;
            }
            .divider::before, .divider::after {
                content: '';
                flex: 1;
                height: 1px;
                background: rgba(255,255,255,0.1);
            }
            .divider span { padding: 0 16px; }
            .certs {
                display: flex;
                justify-content: center;
                gap: 16px;
                margin-top: 24px;
            }
            .cert {
                font-size: 24px;
                opacity: 0.5;
            }
        </style>
    </head>
    <body>
        <div class="login-card">
            <div class="logo">
                <div class="logo-icon">⚡</div>
                <div class="logo-text">West Money OS</div>
                <div class="logo-sub">Enterprise Universe GmbH</div>
            </div>
            
            <form method="POST">
                <div class="form-group">
                    <label>Benutzername</label>
                    <input type="text" name="username" placeholder="admin" required>
                </div>
                <div class="form-group">
                    <label>Passwort</label>
                    <input type="password" name="password" placeholder="••••••" required>
                </div>
                <button type="submit">🚀 Anmelden</button>
            </form>
            
            <div class="divider"><span>Zertifiziert & Sicher</span></div>
            
            <div class="certs">
                <span class="cert" title="ISO 27001">🔒</span>
                <span class="cert" title="DSGVO">🛡️</span>
                <span class="cert" title="TÜV">✅</span>
                <span class="cert" title="SSL">🔐</span>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ============================================================================
# ROUTES - LANDING PAGE
# ============================================================================
@app.route('/')
def landing():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>West Money Bau | Smart Home & Gebäudeautomation</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', sans-serif;
                background: #0a0a0a;
                color: #ffffff;
                overflow-x: hidden;
            }
            
            /* Hero Section */
            .hero {
                min-height: 100vh;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 40px 20px;
            }
            
            .hero::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="1" fill="rgba(255,87,34,0.1)"/></svg>');
                background-size: 50px;
                opacity: 0.5;
            }
            
            .hero-content {
                position: relative;
                z-index: 1;
                max-width: 900px;
            }
            
            .hero-badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(255,87,34,0.1);
                border: 1px solid rgba(255,87,34,0.3);
                padding: 8px 20px;
                border-radius: 50px;
                font-size: 14px;
                margin-bottom: 32px;
                color: #FF5722;
            }
            
            .hero-title {
                font-size: clamp(40px, 8vw, 80px);
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 24px;
            }
            
            .hero-title span {
                background: linear-gradient(90deg, #FF5722, #FFD700, #FF5722);
                background-size: 200% auto;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: gradient 3s ease infinite;
            }
            
            @keyframes gradient {
                0%, 100% { background-position: 0% center; }
                50% { background-position: 100% center; }
            }
            
            .hero-subtitle {
                font-size: clamp(18px, 3vw, 24px);
                color: rgba(255,255,255,0.7);
                margin-bottom: 40px;
                line-height: 1.6;
            }
            
            .hero-buttons {
                display: flex;
                gap: 16px;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .btn {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 16px 32px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 16px;
                text-decoration: none;
                transition: all 0.3s ease;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #FF5722, #FF9800);
                color: white;
            }
            
            .btn-primary:hover {
                transform: translateY(-4px);
                box-shadow: 0 20px 40px rgba(255,87,34,0.4);
            }
            
            .btn-secondary {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.2);
                color: white;
            }
            
            .btn-secondary:hover {
                background: rgba(255,255,255,0.1);
            }
            
            /* Stats Section */
            .stats {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 2px;
                background: rgba(255,255,255,0.1);
                margin: 60px 0;
            }
            
            .stat {
                background: #0a0a0a;
                padding: 40px 20px;
                text-align: center;
            }
            
            .stat-value {
                font-size: 48px;
                font-weight: 800;
                background: linear-gradient(90deg, #FF5722, #FFD700);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .stat-label {
                color: rgba(255,255,255,0.6);
                margin-top: 8px;
            }
            
            /* Certifications Section */
            .section {
                padding: 100px 40px;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .section-title {
                font-size: 40px;
                font-weight: 700;
                text-align: center;
                margin-bottom: 60px;
            }
            
            .section-title span {
                background: linear-gradient(90deg, #FF5722, #FFD700);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .cert-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 24px;
            }
            
            .cert-card {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 32px;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .cert-card:hover {
                transform: translateY(-8px);
                border-color: #FF5722;
                background: rgba(255,87,34,0.05);
            }
            
            .cert-icon {
                font-size: 48px;
                margin-bottom: 16px;
            }
            
            .cert-name {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
            }
            
            .cert-desc {
                color: rgba(255,255,255,0.5);
                font-size: 14px;
            }
            
            /* Awards Section */
            .awards-grid {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 24px;
            }
            
            .award-card {
                background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(255,87,34,0.05));
                border: 1px solid rgba(255,215,0,0.3);
                border-radius: 16px;
                padding: 24px 32px;
                display: flex;
                align-items: center;
                gap: 16px;
                transition: all 0.3s ease;
            }
            
            .award-card:hover {
                transform: scale(1.05);
            }
            
            .award-icon {
                font-size: 40px;
            }
            
            .award-name {
                font-weight: 600;
            }
            
            .award-org {
                font-size: 12px;
                color: rgba(255,255,255,0.5);
            }
            
            /* Features Section */
            .features-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 32px;
            }
            
            .feature-card {
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 40px;
                transition: all 0.3s ease;
            }
            
            .feature-card:hover {
                border-color: #FF5722;
                transform: translateY(-8px);
            }
            
            .feature-icon {
                width: 64px;
                height: 64px;
                background: linear-gradient(135deg, #FF5722, #FF9800);
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                margin-bottom: 24px;
            }
            
            .feature-title {
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 12px;
            }
            
            .feature-desc {
                color: rgba(255,255,255,0.6);
                line-height: 1.6;
            }
            
            /* Footer */
            footer {
                background: #050505;
                padding: 60px 40px 30px;
                border-top: 1px solid rgba(255,255,255,0.1);
            }
            
            .footer-content {
                max-width: 1400px;
                margin: 0 auto;
                display: grid;
                grid-template-columns: 2fr 1fr 1fr 1fr;
                gap: 60px;
            }
            
            .footer-logo {
                font-size: 24px;
                font-weight: 700;
                background: linear-gradient(90deg, #FF5722, #FFD700);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 16px;
            }
            
            .footer-desc {
                color: rgba(255,255,255,0.5);
                line-height: 1.6;
                margin-bottom: 20px;
            }
            
            .footer-title {
                font-weight: 600;
                margin-bottom: 20px;
            }
            
            .footer-links {
                list-style: none;
            }
            
            .footer-links a {
                color: rgba(255,255,255,0.5);
                text-decoration: none;
                display: block;
                padding: 8px 0;
                transition: color 0.3s ease;
            }
            
            .footer-links a:hover {
                color: #FF5722;
            }
            
            .footer-bottom {
                max-width: 1400px;
                margin: 40px auto 0;
                padding-top: 20px;
                border-top: 1px solid rgba(255,255,255,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: rgba(255,255,255,0.4);
                font-size: 14px;
            }
            
            .footer-certs {
                display: flex;
                gap: 12px;
            }
            
            .footer-certs span {
                font-size: 20px;
            }
            
            /* Responsive */
            @media (max-width: 1024px) {
                .stats { grid-template-columns: repeat(2, 1fr); }
                .features-grid { grid-template-columns: 1fr; }
                .footer-content { grid-template-columns: 1fr 1fr; }
            }
            
            @media (max-width: 768px) {
                .stats { grid-template-columns: 1fr; }
                .hero-buttons { flex-direction: column; }
                .footer-content { grid-template-columns: 1fr; }
                .footer-bottom { flex-direction: column; gap: 16px; }
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav style="position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: rgba(10,10,10,0.9); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.1);">
            <div style="max-width: 1400px; margin: 0 auto; padding: 16px 40px; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #FF5722, #FF9800); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">⚡</div>
                    <span style="font-weight: 700; font-size: 18px;">West Money Bau</span>
                </div>
                <div style="display: flex; gap: 32px; align-items: center;">
                    <a href="#services" style="color: rgba(255,255,255,0.7); text-decoration: none;">Services</a>
                    <a href="#about" style="color: rgba(255,255,255,0.7); text-decoration: none;">Über Uns</a>
                    <a href="#contact" style="color: rgba(255,255,255,0.7); text-decoration: none;">Kontakt</a>
                    <a href="/login" class="btn btn-primary" style="padding: 10px 24px;">Login</a>
                </div>
            </div>
        </nav>
        
        <!-- Hero Section -->
        <section class="hero">
            <div class="hero-content">
                <div class="hero-badge">
                    🏆 Ausgezeichnet als Top Smart Home Company 2024
                </div>
                <h1 class="hero-title">
                    Intelligente<br><span>Gebäudeautomation</span><br>für die Zukunft
                </h1>
                <p class="hero-subtitle">
                    West Money Bau – Ihr Partner für Smart Home, LOXONE Integration und 
                    nachhaltige Bauprojekte. ISO-zertifiziert, DSGVO-konform, zukunftssicher.
                </p>
                <div class="hero-buttons">
                    <a href="/login" class="btn btn-primary">🚀 Jetzt Starten</a>
                    <a href="#services" class="btn btn-secondary">📋 Mehr Erfahren</a>
                </div>
            </div>
        </section>
        
        <!-- Stats -->
        <div class="stats">
            <div class="stat">
                <div class="stat-value">€847K</div>
                <div class="stat-label">Umsatz 2024</div>
            </div>
            <div class="stat">
                <div class="stat-value">150+</div>
                <div class="stat-label">Projekte</div>
            </div>
            <div class="stat">
                <div class="stat-value">98%</div>
                <div class="stat-label">Kundenzufriedenheit</div>
            </div>
            <div class="stat">
                <div class="stat-value">24/7</div>
                <div class="stat-label">Support</div>
            </div>
        </div>
        
        <!-- Certifications -->
        <section class="section" id="certifications">
            <h2 class="section-title">Unsere <span>Zertifizierungen</span></h2>
            <div class="cert-grid">
                {% for cert in certifications %}
                <div class="cert-card">
                    <div class="cert-icon">{{ cert.icon }}</div>
                    <div class="cert-name">{{ cert.name }}</div>
                    <div class="cert-desc">{{ cert.desc }}</div>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <!-- Awards -->
        <section class="section" style="background: linear-gradient(180deg, rgba(255,215,0,0.05), transparent);">
            <h2 class="section-title">Auszeichnungen & <span>Awards</span></h2>
            <div class="awards-grid">
                {% for award in awards %}
                <div class="award-card">
                    <div class="award-icon">{{ award.icon }}</div>
                    <div>
                        <div class="award-name">{{ award.name }}</div>
                        <div class="award-org">{{ award.org }}</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <!-- Features -->
        <section class="section" id="services">
            <h2 class="section-title">Unsere <span>Services</span></h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🏠</div>
                    <div class="feature-title">Smart Home</div>
                    <div class="feature-desc">LOXONE Platinum Partner - Komplette Gebäudeautomation für Licht, Heizung, Sicherheit und mehr.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔒</div>
                    <div class="feature-title">Security Systems</div>
                    <div class="feature-desc">DedSec Security - Professionelle Alarmsysteme, CCTV, Zutrittskontrolle und Drohnenüberwachung.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🧠</div>
                    <div class="feature-title">Einstein AI</div>
                    <div class="feature-desc">KI-gestützte Prognosen, Analytics und Automatisierung für Ihre Bauprojekte.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🏗️</div>
                    <div class="feature-title">Bauausführung</div>
                    <div class="feature-desc">Barrierefreies Bauen, Sanierung und schlüsselfertige Projekte im Rhein-Main-Gebiet.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">☀️</div>
                    <div class="feature-title">Photovoltaik</div>
                    <div class="feature-desc">Solaranlagen, Speichersysteme und Wallboxen für Ihre Energieunabhängigkeit.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">West Money OS</div>
                    <div class="feature-desc">Unsere SaaS-Plattform für CRM, Projektmanagement und Business Intelligence.</div>
                </div>
            </div>
        </section>
        
        <!-- CTA -->
        <section style="padding: 100px 40px; background: linear-gradient(135deg, #FF5722, #FF9800); text-align: center;">
            <h2 style="font-size: 40px; font-weight: 700; margin-bottom: 20px;">Bereit für die Zukunft?</h2>
            <p style="font-size: 20px; opacity: 0.9; margin-bottom: 40px;">Starten Sie jetzt mit West Money OS und digitalisieren Sie Ihr Business.</p>
            <a href="/login" class="btn" style="background: white; color: #FF5722; padding: 20px 48px; font-size: 18px;">🚀 Kostenlos Testen</a>
        </section>
        
        <!-- Footer -->
        <footer id="contact">
            <div class="footer-content">
                <div>
                    <div class="footer-logo">⚡ West Money Bau</div>
                    <p class="footer-desc">Enterprise Universe GmbH<br>Ihr Partner für Smart Home & Gebäudeautomation im Rhein-Main-Gebiet.</p>
                    <p style="color: rgba(255,255,255,0.5); font-size: 14px;">
                        📍 Frankfurt am Main<br>
                        📞 +49 (0) 69 XXX XXXX<br>
                        ✉️ info@west-money.com
                    </p>
                </div>
                <div>
                    <div class="footer-title">Services</div>
                    <ul class="footer-links">
                        <li><a href="#">Smart Home</a></li>
                        <li><a href="#">Sicherheitstechnik</a></li>
                        <li><a href="#">Photovoltaik</a></li>
                        <li><a href="#">Bauausführung</a></li>
                    </ul>
                </div>
                <div>
                    <div class="footer-title">Unternehmen</div>
                    <ul class="footer-links">
                        <li><a href="#">Über Uns</a></li>
                        <li><a href="#">Karriere</a></li>
                        <li><a href="#">Partner</a></li>
                        <li><a href="#">Presse</a></li>
                    </ul>
                </div>
                <div>
                    <div class="footer-title">Rechtliches</div>
                    <ul class="footer-links">
                        <li><a href="#">Impressum</a></li>
                        <li><a href="#">Datenschutz</a></li>
                        <li><a href="#">AGB</a></li>
                        <li><a href="#">Cookie-Richtlinie</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <span>© 2024-2026 Enterprise Universe GmbH. Alle Rechte vorbehalten.</span>
                <div class="footer-certs">
                    <span title="ISO 9001">🏅</span>
                    <span title="ISO 27001">🔒</span>
                    <span title="DSGVO">🛡️</span>
                    <span title="TÜV">✅</span>
                    <span title="LOXONE">🏠</span>
                </div>
            </div>
        </footer>
    </body>
    </html>
    ''', certifications=CERTIFICATIONS, awards=AWARDS)

# ============================================================================
# ROUTES - DASHBOARD
# ============================================================================
@app.route('/dashboard')
@login_required
def dashboard():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title">Dashboard</h1>
            <p class="page-subtitle">Willkommen zurück, {{ user }}</p>
        </div>
        <div style="display: flex; gap: 12px;">
            <a href="/einstein/predictions" class="btn btn-primary">🔮 Einstein Predictions</a>
            <a href="/dedsec" class="btn btn-secondary">🛡️ Security Status</a>
        </div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">€3.6M</div>
            <div class="stat-label">Pipeline Value</div>
            <div class="stat-change positive">↑ 23.5% vs. Vormonat</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">59</div>
            <div class="stat-label">Aktive Leads</div>
            <div class="stat-change positive">↑ 12 diese Woche</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">87%</div>
            <div class="stat-label">Conversion Rate</div>
            <div class="stat-change positive">↑ 5.2%</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">€847K</div>
            <div class="stat-label">Umsatz 2024</div>
            <div class="stat-change positive">↑ 23.5% YoY</div>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px;">
        <div class="card">
            <div class="card-title">📈 Pipeline Overview</div>
            <canvas id="pipelineChart" height="200"></canvas>
        </div>
        
        <div class="card einstein-card">
            <div class="card-title">🧠 Einstein Insights</div>
            <div style="space-y: 16px;">
                <div style="padding: 16px; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 12px;">
                    <div style="font-size: 14px; color: rgba(255,255,255,0.6);">Top Prediction</div>
                    <div style="font-weight: 600; margin-top: 4px;">Thomas Moser - 87% Conversion</div>
                </div>
                <div style="padding: 16px; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 12px;">
                    <div style="font-size: 14px; color: rgba(255,255,255,0.6);">Empfehlung</div>
                    <div style="font-weight: 600; margin-top: 4px;">Kontaktiere Mainova AG diese Woche</div>
                </div>
                <a href="/einstein/predictions" class="btn btn-primary" style="width: 100%; justify-content: center;">Alle Predictions →</a>
            </div>
        </div>
    </div>
    
    <div class="card" style="margin-top: 24px;">
        <div class="card-title">🔥 Hot Leads (Score 90+)</div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Score</th>
                        <th>Name</th>
                        <th>Unternehmen</th>
                        <th>Position</th>
                        <th>Stage</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    {% for lead in leads[:5] %}
                    <tr>
                        <td>
                            <div class="score-badge score-high">{{ lead.score }}</div>
                        </td>
                        <td><strong>{{ lead.name }}</strong></td>
                        <td>{{ lead.company }}</td>
                        <td>{{ lead.position }}</td>
                        <td><span class="badge badge-{% if lead.stage == 'won' %}success{% elif lead.stage == 'negotiation' %}warning{% else %}info{% endif %}">{{ lead.stage }}</span></td>
                        <td>€{{ "{:,.0f}".format(lead.value) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <a href="/dashboard/leads" style="display: block; text-align: center; padding: 16px; color: #FF5722; text-decoration: none;">Alle 59 Leads anzeigen →</a>
    </div>
    
    <script>
        // Pipeline Chart
        const ctx = document.getElementById('pipelineChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['New', 'Contacted', 'Qualified', 'Proposal', 'Negotiation', 'Won'],
                datasets: [{
                    label: 'Leads',
                    data: [11, 7, 5, 4, 5, 3],
                    backgroundColor: [
                        'rgba(33, 150, 243, 0.8)',
                        'rgba(156, 39, 176, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(255, 87, 34, 0.8)',
                        'rgba(233, 30, 99, 0.8)',
                        'rgba(76, 175, 80, 0.8)'
                    ],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: 'rgba(255,255,255,0.6)' } },
                    x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.6)' } }
                }
            }
        });
    </script>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="Dashboard", 
                                  active_page="dashboard",
                                  user=session.get('user', 'Admin'),
                                  leads=LEADS_DATA)

# ============================================================================
# ROUTES - LEADS
# ============================================================================
@app.route('/dashboard/leads')
@login_required
def leads():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title">Lead Management</h1>
            <p class="page-subtitle">59 Leads | Pipeline: €3.6M</p>
        </div>
        <div style="display: flex; gap: 12px;">
            <button class="btn btn-secondary">📥 Import</button>
            <button class="btn btn-primary">➕ Neuer Lead</button>
        </div>
    </div>
    
    <div class="card">
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Score</th>
                        <th>Name</th>
                        <th>Unternehmen</th>
                        <th>Position</th>
                        <th>Stage</th>
                        <th>Value</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for lead in leads %}
                    <tr>
                        <td>
                            <div class="score-badge {% if lead.score >= 90 %}score-high{% elif lead.score >= 70 %}score-medium{% else %}score-low{% endif %}">{{ lead.score }}</div>
                        </td>
                        <td><strong>{{ lead.name }}</strong></td>
                        <td>{{ lead.company }}</td>
                        <td>{{ lead.position }}</td>
                        <td>
                            <span class="badge badge-{% if lead.stage == 'won' %}success{% elif lead.stage == 'negotiation' %}warning{% elif lead.stage == 'proposal' %}purple{% else %}info{% endif %}">
                                {{ lead.stage }}
                            </span>
                        </td>
                        <td>€{{ "{:,.0f}".format(lead.value) }}</td>
                        <td>
                            <button class="btn btn-secondary" style="padding: 6px 12px;">👁️</button>
                            <button class="btn btn-secondary" style="padding: 6px 12px;">✏️</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="Leads", 
                                  active_page="leads",
                                  leads=LEADS_DATA)

# ============================================================================
# ROUTES - EINSTEIN AI
# ============================================================================
@app.route('/einstein')
@login_required
def einstein():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title">🧠 Einstein AI Agency</h1>
            <p class="page-subtitle">KI-gestützte Business Intelligence</p>
        </div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card einstein-card">
            <div class="stat-value">87%</div>
            <div class="stat-label">Prediction Accuracy</div>
        </div>
        <div class="stat-card einstein-card">
            <div class="stat-value">24</div>
            <div class="stat-label">Active Insights</div>
        </div>
        <div class="stat-card einstein-card">
            <div class="stat-value">156</div>
            <div class="stat-label">Automations Run</div>
        </div>
        <div class="stat-card einstein-card">
            <div class="stat-value">€420K</div>
            <div class="stat-label">Revenue Impact</div>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px;">
        <a href="/einstein/predictions" class="card einstein-card" style="text-decoration: none; color: inherit;">
            <div style="font-size: 48px; margin-bottom: 16px;">🔮</div>
            <div class="card-title">Predictions</div>
            <p style="color: rgba(255,255,255,0.6);">Lead Conversion, Deal Close, Upsell Opportunities</p>
        </a>
        
        <a href="/einstein/analytics" class="card einstein-card" style="text-decoration: none; color: inherit;">
            <div style="font-size: 48px; margin-bottom: 16px;">📊</div>
            <div class="card-title">Deep Analytics</div>
            <p style="color: rgba(255,255,255,0.6);">KI-gestützte Datenanalyse und Visualisierung</p>
        </a>
        
        <a href="/einstein/insights" class="card einstein-card" style="text-decoration: none; color: inherit;">
            <div style="font-size: 48px; margin-bottom: 16px;">💡</div>
            <div class="card-title">Auto Insights</div>
            <p style="color: rgba(255,255,255,0.6);">Automatische Business Empfehlungen</p>
        </a>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="Einstein AI", 
                                  active_page="einstein")

@app.route('/einstein/predictions')
@login_required
def einstein_predictions():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title">🔮 Einstein Predictions</h1>
            <p class="page-subtitle">KI-basierte Prognosen für Ihre Leads</p>
        </div>
        <a href="/einstein" class="btn btn-secondary">← Zurück zu Einstein</a>
    </div>
    
    <div class="card einstein-card">
        <div class="card-title">📈 Aktuelle Predictions</div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Typ</th>
                        <th>Lead</th>
                        <th>Prediction</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
                    {% for pred in predictions %}
                    <tr>
                        <td>
                            <span class="badge badge-purple">{{ pred.type.replace('_', ' ').title() }}</span>
                        </td>
                        <td><strong>{{ pred.lead }}</strong></td>
                        <td>{{ pred.prediction }}</td>
                        <td>
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <div class="progress-bar" style="width: 100px;">
                                    <div class="progress-fill" style="width: {{ pred.confidence }}%; background: linear-gradient(90deg, #9C27B0, #673AB7);"></div>
                                </div>
                                <span>{{ pred.confidence }}%</span>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; margin-top: 24px;">
        <div class="card">
            <div class="card-title">🎯 Top Conversion Candidates</div>
            <div style="padding: 20px 0;">
                {% for lead in leads[:3] %}
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div>
                        <strong>{{ lead.name }}</strong>
                        <div style="font-size: 12px; color: rgba(255,255,255,0.5);">{{ lead.company }}</div>
                    </div>
                    <div class="badge badge-success">{{ lead.score - 5 + loop.index }}% Likelihood</div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">⏰ Best Contact Times</div>
            <div style="padding: 20px 0;">
                <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <span>Montag</span>
                    <span style="color: #4CAF50;">10:00 - 11:00</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <span>Dienstag</span>
                    <span style="color: #4CAF50;">14:00 - 15:00</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <span>Mittwoch</span>
                    <span style="color: #FF9800;">09:00 - 10:00</span>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="Predictions", 
                                  active_page="predictions",
                                  predictions=EINSTEIN_PREDICTIONS,
                                  leads=LEADS_DATA)

@app.route('/einstein/analytics')
@login_required
def einstein_analytics():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title">📊 Einstein Analytics</h1>
            <p class="page-subtitle">Deep Learning Datenanalyse</p>
        </div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">1.2M</div>
            <div class="stat-label">Datenpunkte analysiert</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">47</div>
            <div class="stat-label">ML Models aktiv</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">99.2%</div>
            <div class="stat-label">Model Accuracy</div>
        </div>
    </div>
    
    <div class="card">
        <div class="card-title">📈 Performance Analytics</div>
        <canvas id="analyticsChart" height="300"></canvas>
    </div>
    
    <script>
        const ctx = document.getElementById('analyticsChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Revenue',
                    data: [45, 52, 48, 61, 55, 67, 72, 78, 85, 89, 95, 102],
                    borderColor: '#9C27B0',
                    backgroundColor: 'rgba(156, 39, 176, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Leads',
                    data: [12, 19, 15, 25, 22, 30, 28, 35, 40, 42, 48, 55],
                    borderColor: '#673AB7',
                    backgroundColor: 'rgba(103, 58, 183, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: 'rgba(255,255,255,0.7)' } } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: 'rgba(255,255,255,0.6)' } },
                    x: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: 'rgba(255,255,255,0.6)' } }
                }
            }
        });
    </script>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="Analytics", 
                                  active_page="analytics")

@app.route('/einstein/insights')
@login_required  
def einstein_insights():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title">💡 Einstein Insights</h1>
            <p class="page-subtitle">Automatische Business Empfehlungen</p>
        </div>
    </div>
    
    <div class="card einstein-card">
        <div class="card-title">🎯 Aktuelle Empfehlungen</div>
        
        <div style="padding: 20px; background: rgba(76,175,80,0.1); border: 1px solid rgba(76,175,80,0.3); border-radius: 12px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="color: #4CAF50; font-weight: 600;">🔥 Hot Opportunity</div>
                    <div style="margin-top: 8px;">Kontaktieren Sie <strong>Thomas Moser (Loxone)</strong> diese Woche - 87% Conversion Wahrscheinlichkeit</div>
                </div>
                <button class="btn btn-primary">Aktion starten</button>
            </div>
        </div>
        
        <div style="padding: 20px; background: rgba(255,152,0,0.1); border: 1px solid rgba(255,152,0,0.3); border-radius: 12px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="color: #FF9800; font-weight: 600;">📈 Upsell Potenzial</div>
                    <div style="margin-top: 8px;"><strong>Mainova AG</strong> - €150k zusätzliches Potenzial für PV-Integration identifiziert</div>
                </div>
                <button class="btn btn-secondary">Details</button>
            </div>
        </div>
        
        <div style="padding: 20px; background: rgba(33,150,243,0.1); border: 1px solid rgba(33,150,243,0.3); border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="color: #2196F3; font-weight: 600;">📊 Trend Alert</div>
                    <div style="margin-top: 8px;">Smart Home Anfragen +45% in den letzten 30 Tagen - Marketing Budget erhöhen?</div>
                </div>
                <button class="btn btn-secondary">Analysieren</button>
            </div>
        </div>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="Insights", 
                                  active_page="insights")

# ============================================================================
# ROUTES - DEDSEC SECURITY
# ============================================================================
@app.route('/dedsec')
@login_required
def dedsec():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title" style="color: #00D4FF;">🛡️ DedSec Security Hub</h1>
            <p class="page-subtitle">Enterprise Security Ecosystem</p>
        </div>
        <div class="badge badge-success pulse">● All Systems Online</div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card dedsec-card">
            <div class="stat-value" style="color: #00D4FF;">24</div>
            <div class="stat-label">Active Cameras</div>
        </div>
        <div class="stat-card dedsec-card">
            <div class="stat-value" style="color: #00FF41;">2</div>
            <div class="stat-label">Patrol Drones</div>
        </div>
        <div class="stat-card dedsec-card">
            <div class="stat-value" style="color: #00D4FF;">1,247</div>
            <div class="stat-label">Threats Blocked</div>
        </div>
        <div class="stat-card dedsec-card">
            <div class="stat-value" style="color: #00FF41;">100%</div>
            <div class="stat-label">Uptime</div>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px;">
        <a href="/dedsec/tower" class="card dedsec-card" style="text-decoration: none; color: inherit;">
            <div style="font-size: 48px; margin-bottom: 16px;">🗼</div>
            <div class="card-title">Command Tower</div>
            <p style="color: rgba(255,255,255,0.6);">Zentrale Überwachung & Kontrolle</p>
        </a>
        
        <a href="/dedsec/drones" class="card dedsec-card" style="text-decoration: none; color: inherit;">
            <div style="font-size: 48px; margin-bottom: 16px;">🚁</div>
            <div class="card-title">Drone Control</div>
            <p style="color: rgba(255,255,255,0.6);">Autonome Patrouillen-Drohnen</p>
        </a>
        
        <a href="/dedsec/cctv" class="card dedsec-card" style="text-decoration: none; color: inherit;">
            <div style="font-size: 48px; margin-bottom: 16px;">📹</div>
            <div class="card-title">CCTV Network</div>
            <p style="color: rgba(255,255,255,0.6);">24 Kameras live</p>
        </a>
    </div>
    
    <div class="card dedsec-card" style="margin-top: 24px;">
        <div class="card-title">🖥️ System Status</div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>System</th>
                        <th>Status</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {% for sys in systems %}
                    <tr>
                        <td><strong>{{ sys.name }}</strong></td>
                        <td>
                            <span class="badge badge-{% if sys.status == 'online' or sys.status == 'active' or sys.status == 'locked' %}success{% elif sys.status == 'charging' %}warning{% else %}danger{% endif %}">
                                {{ sys.status }}
                            </span>
                        </td>
                        <td style="color: rgba(255,255,255,0.6);">
                            {% if sys.cameras %}{{ sys.cameras }} Cameras{% endif %}
                            {% if sys.battery %}Battery: {{ sys.battery }}%{% endif %}
                            {% if sys.blocked %}{{ sys.blocked }} blocked{% endif %}
                            {% if sys.files %}{{ sys.files }} files{% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="DedSec Security", 
                                  active_page="dedsec",
                                  systems=DEDSEC_SYSTEMS)

@app.route('/dedsec/tower')
@login_required
def dedsec_tower():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title" style="color: #00D4FF;">🗼 Command Tower</h1>
            <p class="page-subtitle">Zentrale Überwachung Frankfurt</p>
        </div>
        <div class="badge badge-success pulse">● LIVE</div>
    </div>
    
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px;">
        <div class="card dedsec-card">
            <div class="card-title">📍 Live Map</div>
            <div style="height: 400px; background: linear-gradient(135deg, #0d1117, #161b22); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #00D4FF;">
                <div style="text-align: center;">
                    <div style="font-size: 64px; margin-bottom: 16px;">🗺️</div>
                    <div>Live Security Map</div>
                    <div style="font-size: 12px; color: rgba(255,255,255,0.5);">24 Kameras | 2 Drohnen aktiv</div>
                </div>
            </div>
        </div>
        
        <div>
            <div class="card dedsec-card" style="margin-bottom: 24px;">
                <div class="card-title">⚡ Quick Actions</div>
                <button class="btn btn-primary" style="width: 100%; margin-bottom: 12px;">🚨 Alarm aktivieren</button>
                <button class="btn btn-secondary" style="width: 100%; margin-bottom: 12px;">🔒 Lockdown</button>
                <button class="btn btn-secondary" style="width: 100%;">📹 Alle Kameras</button>
            </div>
            
            <div class="card dedsec-card">
                <div class="card-title">📊 Statistiken heute</div>
                <div style="padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: flex; justify-content: space-between;">
                        <span>Bewegungen erkannt</span>
                        <span style="color: #00D4FF;">47</span>
                    </div>
                </div>
                <div style="padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: flex; justify-content: space-between;">
                        <span>Alerts</span>
                        <span style="color: #00FF41;">0</span>
                    </div>
                </div>
                <div style="padding: 12px 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <span>System Health</span>
                        <span style="color: #00FF41;">100%</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="Command Tower", 
                                  active_page="tower")

@app.route('/dedsec/drones')
@login_required
def dedsec_drones():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title" style="color: #00D4FF;">🚁 Drone Control</h1>
            <p class="page-subtitle">Autonome Patrouillen-Drohnen</p>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px;">
        <div class="card dedsec-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
                <div>
                    <div class="card-title">Patrol Drone Alpha</div>
                    <span class="badge badge-success">● Active</span>
                </div>
                <div style="font-size: 48px;">🚁</div>
            </div>
            <div style="padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div style="display: flex; justify-content: space-between;">
                    <span>Battery</span>
                    <span style="color: #00FF41;">87%</span>
                </div>
                <div class="progress-bar" style="margin-top: 8px;">
                    <div class="progress-fill" style="width: 87%; background: linear-gradient(90deg, #00D4FF, #00FF41);"></div>
                </div>
            </div>
            <div style="padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div style="display: flex; justify-content: space-between;">
                    <span>Location</span>
                    <span>Sector A</span>
                </div>
            </div>
            <div style="padding: 12px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span>Flight Time</span>
                    <span>2h 34m</span>
                </div>
            </div>
            <button class="btn btn-secondary" style="width: 100%; margin-top: 16px;">📍 Track Live</button>
        </div>
        
        <div class="card dedsec-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
                <div>
                    <div class="card-title">Patrol Drone Beta</div>
                    <span class="badge badge-warning">● Charging</span>
                </div>
                <div style="font-size: 48px;">🔋</div>
            </div>
            <div style="padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div style="display: flex; justify-content: space-between;">
                    <span>Battery</span>
                    <span style="color: #FF9800;">23%</span>
                </div>
                <div class="progress-bar" style="margin-top: 8px;">
                    <div class="progress-fill" style="width: 23%; background: linear-gradient(90deg, #FF9800, #FFC107);"></div>
                </div>
            </div>
            <div style="padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div style="display: flex; justify-content: space-between;">
                    <span>Location</span>
                    <span>Base Station</span>
                </div>
            </div>
            <div style="padding: 12px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span>ETA Full</span>
                    <span>45 min</span>
                </div>
            </div>
            <button class="btn btn-secondary" style="width: 100%; margin-top: 16px;" disabled>⏳ Charging...</button>
        </div>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="Drone Control", 
                                  active_page="drones")

@app.route('/dedsec/cctv')
@login_required
def dedsec_cctv():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title" style="color: #00D4FF;">📹 CCTV Network</h1>
            <p class="page-subtitle">24 Kameras | Live Überwachung</p>
        </div>
        <div class="badge badge-success pulse">● 24/24 Online</div>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
        {% for i in range(1, 9) %}
        <div class="card dedsec-card" style="padding: 0; overflow: hidden;">
            <div style="height: 120px; background: linear-gradient(135deg, #0d1117, #161b22); display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 32px;">📹</span>
            </div>
            <div style="padding: 12px;">
                <div style="font-weight: 600; font-size: 14px;">CAM-{{ "%02d"|format(i) }}</div>
                <div style="font-size: 12px; color: rgba(255,255,255,0.5);">Sector {{ ['A', 'A', 'B', 'B', 'C', 'C', 'D', 'D'][i-1] }}</div>
                <span class="badge badge-success" style="margin-top: 8px; font-size: 10px;">● Live</span>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="CCTV", 
                                  active_page="cctv")

# ============================================================================
# ROUTES - OTHER MODULES
# ============================================================================
@app.route('/whatsapp')
@login_required
def whatsapp():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title">💬 WhatsApp Business</h1>
            <p class="page-subtitle">Kunden-Kommunikation & Kampagnen</p>
        </div>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(37,211,102,0.2), rgba(37,211,102,0.05)); border-color: rgba(37,211,102,0.3);">
            <div class="stat-value" style="color: #25D366;">1,247</div>
            <div class="stat-label">Kontakte</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(37,211,102,0.2), rgba(37,211,102,0.05)); border-color: rgba(37,211,102,0.3);">
            <div class="stat-value" style="color: #25D366;">89%</div>
            <div class="stat-label">Open Rate</div>
        </div>
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(37,211,102,0.2), rgba(37,211,102,0.05)); border-color: rgba(37,211,102,0.3);">
            <div class="stat-value" style="color: #25D366;">12</div>
            <div class="stat-label">Aktive Kampagnen</div>
        </div>
    </div>
    
    <div class="card">
        <div class="card-title">📱 WhatsApp Integration Status</div>
        <p style="color: rgba(255,255,255,0.6); margin-bottom: 20px;">Verbinden Sie Ihre WhatsApp Business API für automatisierte Kundenkommunikation.</p>
        <button class="btn btn-primary" style="background: linear-gradient(135deg, #25D366, #128C7E);">🔗 WhatsApp verbinden</button>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="WhatsApp", 
                                  active_page="whatsapp")

@app.route('/godbot')
@login_required
def godbot():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title">🤖 GOD BOT AI</h1>
            <p class="page-subtitle">Ihr intelligenter Business-Assistent</p>
        </div>
    </div>
    
    <div class="card" style="background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(255,87,34,0.05)); border-color: rgba(255,215,0,0.3);">
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 80px; margin-bottom: 24px;">🤖</div>
            <h2 style="font-size: 28px; margin-bottom: 12px;">GOD MODE ACTIVATED</h2>
            <p style="color: rgba(255,255,255,0.6); margin-bottom: 32px;">Ultra Instinct AI Assistant - Bereit für Ihre Befehle</p>
            
            <div style="max-width: 600px; margin: 0 auto;">
                <div style="display: flex; gap: 12px;">
                    <input type="text" placeholder="Frag GOD BOT etwas..." style="flex: 1; padding: 16px 20px; border-radius: 12px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; font-size: 16px;">
                    <button class="btn btn-primary" style="background: linear-gradient(135deg, #FFD700, #FF5722);">⚡ Senden</button>
                </div>
            </div>
            
            <div style="margin-top: 40px; display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
                <span class="badge badge-warning">💡 "Analysiere meine Pipeline"</span>
                <span class="badge badge-warning">📧 "Schreibe eine E-Mail an Loxone"</span>
                <span class="badge badge-warning">📊 "Erstelle einen Report"</span>
            </div>
        </div>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="GOD BOT", 
                                  active_page="godbot")

@app.route('/locker')
@login_required
def locker():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title">🔐 Private Locker</h1>
            <p class="page-subtitle">Sichere Dokumenten-Ablage</p>
        </div>
        <button class="btn btn-primary">📤 Upload</button>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">892</div>
            <div class="stat-label">Dokumente</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">45</div>
            <div class="stat-label">Verträge</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">128</div>
            <div class="stat-label">Rechnungen</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">2.4 GB</div>
            <div class="stat-label">Speicher genutzt</div>
        </div>
    </div>
    
    <div class="card">
        <div class="card-title">📁 Ordner</div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
            <div style="padding: 24px; background: rgba(255,255,255,0.05); border-radius: 12px; text-align: center; cursor: pointer;">
                <div style="font-size: 40px; margin-bottom: 8px;">📄</div>
                <div>Dokumente</div>
                <div style="font-size: 12px; color: rgba(255,255,255,0.5);">892 Dateien</div>
            </div>
            <div style="padding: 24px; background: rgba(255,255,255,0.05); border-radius: 12px; text-align: center; cursor: pointer;">
                <div style="font-size: 40px; margin-bottom: 8px;">📝</div>
                <div>Verträge</div>
                <div style="font-size: 12px; color: rgba(255,255,255,0.5);">45 Dateien</div>
            </div>
            <div style="padding: 24px; background: rgba(255,255,255,0.05); border-radius: 12px; text-align: center; cursor: pointer;">
                <div style="font-size: 40px; margin-bottom: 8px;">🧾</div>
                <div>Rechnungen</div>
                <div style="font-size: 12px; color: rgba(255,255,255,0.5);">128 Dateien</div>
            </div>
            <div style="padding: 24px; background: rgba(255,255,255,0.05); border-radius: 12px; text-align: center; cursor: pointer;">
                <div style="font-size: 40px; margin-bottom: 8px;">🏗️</div>
                <div>Projekte</div>
                <div style="font-size: 12px; color: rgba(255,255,255,0.5);">67 Dateien</div>
            </div>
        </div>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="Private Locker", 
                                  active_page="locker")

@app.route('/dashboard/projects')
@login_required
def projects():
    content = '''
    {% extends "base" %}
    {% block content %}
    <div class="page-header">
        <div>
            <h1 class="page-title">🏗️ Projekte</h1>
            <p class="page-subtitle">Aktive Bauprojekte & Smart Home Installationen</p>
        </div>
        <button class="btn btn-primary">➕ Neues Projekt</button>
    </div>
    
    <div class="card">
        <p style="text-align: center; padding: 60px; color: rgba(255,255,255,0.6);">
            <span style="font-size: 48px; display: block; margin-bottom: 16px;">🏗️</span>
            Projektmanagement-Modul wird geladen...
        </p>
    </div>
    {% endblock %}
    '''
    return render_template_string(BASE_TEMPLATE + content, 
                                  title="Projekte", 
                                  active_page="projects")

# ============================================================================
# API ENDPOINTS
# ============================================================================
@app.route('/api/v1/leads')
def api_leads():
    return jsonify({"success": True, "data": LEADS_DATA, "count": len(LEADS_DATA)})

@app.route('/api/v1/predictions')
def api_predictions():
    return jsonify({"success": True, "data": EINSTEIN_PREDICTIONS})

@app.route('/api/v1/security/status')
def api_security():
    return jsonify({"success": True, "data": DEDSEC_SYSTEMS})

@app.route('/api/v1/health')
def api_health():
    return jsonify({
        "status": "healthy",
        "version": "13.0",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "dashboard": "online",
            "einstein": "online",
            "dedsec": "online",
            "whatsapp": "online",
            "godbot": "online",
            "locker": "online"
        }
    })

# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
