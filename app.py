#!/usr/bin/env python3
"""
================================================================================
    WEST MONEY OS v8.0 - ENTERPRISE SUPREME EDITION
    Enterprise Universe GmbH - Complete Business Suite
    
    Features:
    - WhatsApp Business API Integration
    - HubSpot CRM Sync
    - AI Chatbot Assistant
    - Stripe Payments
    - Multi-User Dashboard
    - API Management
    
    (c) 2025 Ömer Hüseyin Coşkun - GOD MODE ACTIVATED
================================================================================
"""

from flask import Flask, jsonify, request, Response, session, redirect, render_template_string
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
VERSION = "8.0.0"
EDITION = "ENTERPRISE SUPREME"

# API Keys from Environment
WHATSAPP_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')

# =============================================================================
# USER DATABASE (In Production: Use PostgreSQL/MySQL)
# =============================================================================
USERS = {
    'admin': {
        'password': hashlib.sha256('663724'.encode()).hexdigest(),
        'role': 'god',
        'name': 'Ömer Coşkun',
        'company': 'Enterprise Universe GmbH'
    },
    'demo': {
        'password': hashlib.sha256('demo123'.encode()).hexdigest(),
        'role': 'user',
        'name': 'Demo User',
        'company': 'Demo Company'
    }
}

# =============================================================================
# AUTHENTICATION DECORATOR
# =============================================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def god_mode_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session.get('role') != 'god':
            return jsonify({'error': 'GOD MODE required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# CSS STYLES - ENTERPRISE DARK THEME
# =============================================================================
STYLES = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-card: #1a1a25;
        --bg-hover: #252535;
        --accent-primary: #6366f1;
        --accent-secondary: #8b5cf6;
        --accent-success: #10b981;
        --accent-warning: #f59e0b;
        --accent-danger: #ef4444;
        --text-primary: #ffffff;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --border-color: #27272a;
        --gradient-primary: linear-gradient(135deg, #6366f1, #8b5cf6);
        --gradient-gold: linear-gradient(135deg, #f59e0b, #d97706);
    }
    
    body {
        font-family: 'Inter', -apple-system, sans-serif;
        background: var(--bg-primary);
        color: var(--text-primary);
        min-height: 100vh;
        line-height: 1.6;
    }
    
    /* Navigation */
    .navbar {
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border-color);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .logo {
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 700;
        font-size: 1.25rem;
    }
    
    .logo-icon {
        width: 40px;
        height: 40px;
        background: var(--gradient-gold);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .nav-links {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }
    
    .nav-link {
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .nav-link:hover {
        color: var(--text-primary);
        background: var(--bg-hover);
    }
    
    .nav-link.active {
        color: var(--accent-primary);
        background: rgba(99, 102, 241, 0.1);
    }
    
    /* Buttons */
    .btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
    }
    
    .btn-primary {
        background: var(--gradient-primary);
        color: white;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
    }
    
    .btn-secondary {
        background: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    .btn-secondary:hover {
        background: var(--bg-hover);
        border-color: var(--accent-primary);
    }
    
    .btn-success {
        background: var(--accent-success);
        color: white;
    }
    
    .btn-danger {
        background: var(--accent-danger);
        color: white;
    }
    
    /* Cards */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s;
    }
    
    .card:hover {
        border-color: var(--accent-primary);
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1rem;
    }
    
    .card-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .card-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    /* Hero Section */
    .hero {
        text-align: center;
        padding: 6rem 2rem;
        background: radial-gradient(ellipse at top, rgba(99, 102, 241, 0.15) 0%, transparent 50%);
    }
    
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.875rem;
        color: var(--accent-primary);
        margin-bottom: 1.5rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #fff 0%, #a1a1aa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        max-width: 600px;
        margin: 0 auto 2rem;
    }
    
    .hero-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    /* Features Grid */
    .features {
        padding: 4rem 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
    }
    
    .feature-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .feature-card:hover {
        border-color: var(--accent-primary);
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
    }
    
    .feature-icon {
        width: 64px;
        height: 64px;
        margin: 0 auto 1rem;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
    }
    
    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    /* Dashboard */
    .dashboard {
        display: grid;
        grid-template-columns: 250px 1fr;
        min-height: 100vh;
    }
    
    .sidebar {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
        padding: 1.5rem;
    }
    
    .sidebar-menu {
        list-style: none;
        margin-top: 2rem;
    }
    
    .sidebar-item {
        margin-bottom: 0.5rem;
    }
    
    .sidebar-link {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        color: var(--text-secondary);
        text-decoration: none;
        transition: all 0.2s;
    }
    
    .sidebar-link:hover, .sidebar-link.active {
        background: var(--bg-hover);
        color: var(--text-primary);
    }
    
    .main-content {
        padding: 2rem;
        overflow-y: auto;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
    }
    
    .stat-label {
        color: var(--text-secondary);
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .stat-change {
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }
    
    .stat-change.positive { color: var(--accent-success); }
    .stat-change.negative { color: var(--accent-danger); }
    
    /* Tables */
    .table-container {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        overflow: hidden;
    }
    
    .table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .table th, .table td {
        padding: 1rem;
        text-align: left;
        border-bottom: 1px solid var(--border-color);
    }
    
    .table th {
        background: var(--bg-secondary);
        font-weight: 600;
        color: var(--text-secondary);
        font-size: 0.875rem;
        text-transform: uppercase;
    }
    
    .table tr:hover td {
        background: var(--bg-hover);
    }
    
    /* Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .badge-success {
        background: rgba(16, 185, 129, 0.1);
        color: var(--accent-success);
    }
    
    .badge-warning {
        background: rgba(245, 158, 11, 0.1);
        color: var(--accent-warning);
    }
    
    .badge-danger {
        background: rgba(239, 68, 68, 0.1);
        color: var(--accent-danger);
    }
    
    .badge-primary {
        background: rgba(99, 102, 241, 0.1);
        color: var(--accent-primary);
    }
    
    /* Forms */
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: var(--text-secondary);
    }
    
    .form-input {
        width: 100%;
        padding: 0.875rem 1rem;
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        color: var(--text-primary);
        font-size: 1rem;
        transition: all 0.2s;
    }
    
    .form-input:focus {
        outline: none;
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Login Page */
    .login-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: radial-gradient(ellipse at center, rgba(99, 102, 241, 0.1) 0%, transparent 50%);
    }
    
    .login-box {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        padding: 3rem;
        width: 100%;
        max-width: 420px;
    }
    
    .login-logo {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-logo-icon {
        width: 80px;
        height: 80px;
        background: var(--gradient-gold);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        margin: 0 auto 1rem;
    }
    
    /* GOD MODE Badge */
    .god-mode-badge {
        background: var(--gradient-gold);
        color: #000;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.75rem;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
        50% { box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .dashboard {
            grid-template-columns: 1fr;
        }
        
        .sidebar {
            display: none;
        }
        
        .hero-title {
            font-size: 2rem;
        }
        
        .navbar {
            padding: 1rem;
        }
        
        .nav-links {
            display: none;
        }
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.5s ease-out;
    }
</style>
"""

# =============================================================================
# PAGE TEMPLATES
# =============================================================================

def get_base_template(content, title="West Money OS"):
    return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | v{VERSION}</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💰</text></svg>">
    {STYLES}
</head>
<body>
    {content}
</body>
</html>
"""

# =============================================================================
# ROUTES - LANDING PAGE
# =============================================================================
@app.route('/')
def landing():
    content = """
    <nav class="navbar">
        <div class="logo">
            <div class="logo-icon">💰</div>
            <span>West Money OS</span>
        </div>
        <div class="nav-links">
            <a href="#features" class="nav-link">Features</a>
            <a href="#pricing" class="nav-link">Preise</a>
            <a href="/api/status" class="nav-link">API Status</a>
            <a href="/login" class="btn btn-primary">Login →</a>
        </div>
    </nav>
    
    <section class="hero animate-in">
        <div class="hero-badge">
            ⚡ v8.0 ENTERPRISE SUPREME
        </div>
        <h1 class="hero-title">West Money OS</h1>
        <p class="hero-subtitle">
            Die ultimative All-in-One Business Platform für Smart Home, CRM, 
            WhatsApp Business, KI-Assistenten und mehr.
        </p>
        <div class="hero-buttons">
            <a href="/login" class="btn btn-primary">Dashboard öffnen →</a>
            <a href="#features" class="btn btn-secondary">Features ansehen</a>
            <a href="/api/status" class="btn btn-secondary">API Status</a>
        </div>
    </section>
    
    <section class="features" id="features">
        <div class="features-grid">
            <div class="feature-card" onclick="window.location='/login'">
                <div class="feature-icon" style="background: linear-gradient(135deg, #25D366, #128C7E);">📱</div>
                <h3 class="feature-title">WhatsApp Business</h3>
                <p class="feature-desc">Automatisierte Nachrichten, Consent Management & Chat-Verlauf</p>
            </div>
            
            <div class="feature-card" onclick="window.location='/login'">
                <div class="feature-icon" style="background: linear-gradient(135deg, #6366f1, #8b5cf6);">🤖</div>
                <h3 class="feature-title">AI Chatbots</h3>
                <p class="feature-desc">Claude AI Integration für intelligente Kundenbetreuung</p>
            </div>
            
            <div class="feature-card" onclick="window.location='/login'">
                <div class="feature-icon" style="background: linear-gradient(135deg, #ff7a59, #ff5c35);">📊</div>
                <h3 class="feature-title">CRM & Leads</h3>
                <p class="feature-desc">HubSpot Integration für vollständiges Lead Management</p>
            </div>
            
            <div class="feature-card" onclick="window.location='/login'">
                <div class="feature-icon" style="background: linear-gradient(135deg, #0066ff, #0052cc);">🏦</div>
                <h3 class="feature-title">Revolut Banking</h3>
                <p class="feature-desc">Business Banking API für Finanzverwaltung</p>
            </div>
            
            <div class="feature-card" onclick="window.location='/login'">
                <div class="feature-icon" style="background: linear-gradient(135deg, #635bff, #0a2540);">💳</div>
                <h3 class="feature-title">Stripe Payments</h3>
                <p class="feature-desc">Sichere Zahlungsabwicklung & Subscriptions</p>
            </div>
            
            <div class="feature-card" onclick="window.location='/login'">
                <div class="feature-icon" style="background: linear-gradient(135deg, #ef4444, #dc2626);">🔐</div>
                <h3 class="feature-title">Security Center</h3>
                <p class="feature-desc">DedSec Security Suite für maximalen Schutz</p>
            </div>
        </div>
    </section>
    
    <footer style="text-align: center; padding: 3rem; border-top: 1px solid var(--border-color);">
        <p style="color: var(--text-secondary);">
            © 2025 Enterprise Universe GmbH | Founder & CEO: Ömer Hüseyin Coşkun
        </p>
        <p style="color: var(--text-muted); font-size: 0.875rem; margin-top: 0.5rem;">
            West Money OS v8.0 ENTERPRISE SUPREME
        </p>
    </footer>
    """
    return get_base_template(content, "West Money OS - Enterprise Supreme")

# =============================================================================
# ROUTES - LOGIN
# =============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username in USERS and USERS[username]['password'] == password_hash:
            session['user'] = username
            session['role'] = USERS[username]['role']
            session['name'] = USERS[username]['name']
            return redirect('/dashboard')
        else:
            error = "Ungültige Anmeldedaten"
    
    error_html = f'<p style="color: var(--accent-danger); margin-bottom: 1rem;">{error}</p>' if error else ''
    
    content = f"""
    <div class="login-container">
        <div class="login-box animate-in">
            <div class="login-logo">
                <div class="login-logo-icon">💰</div>
                <h1 style="font-size: 1.5rem; margin-bottom: 0.5rem;">West Money OS</h1>
                <span class="hero-badge">v8.0 ENTERPRISE SUPREME</span>
            </div>
            
            {error_html}
            
            <form method="POST">
                <div class="form-group">
                    <label class="form-label">Benutzername</label>
                    <input type="text" name="username" class="form-input" placeholder="admin" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Passwort</label>
                    <input type="password" name="password" class="form-input" placeholder="••••••" required>
                </div>
                
                <button type="submit" class="btn btn-primary" style="width: 100%; justify-content: center;">
                    Anmelden →
                </button>
            </form>
            
            <p style="text-align: center; margin-top: 1.5rem; color: var(--text-muted); font-size: 0.875rem;">
                Demo: demo / demo123
            </p>
        </div>
    </div>
    """
    return get_base_template(content, "Login")

# =============================================================================
# ROUTES - DASHBOARD
# =============================================================================
@app.route('/dashboard')
@login_required
def dashboard():
    is_god = session.get('role') == 'god'
    god_badge = '<span class="god-mode-badge">⚡ GOD MODE</span>' if is_god else ''
    
    content = f"""
    <div class="dashboard">
        <aside class="sidebar">
            <div class="logo">
                <div class="logo-icon">💰</div>
                <span>West Money</span>
            </div>
            
            <ul class="sidebar-menu">
                <li class="sidebar-item">
                    <a href="/dashboard" class="sidebar-link active">
                        📊 Dashboard
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/whatsapp" class="sidebar-link">
                        📱 WhatsApp
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/crm" class="sidebar-link">
                        👥 CRM & Leads
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/ai" class="sidebar-link">
                        🤖 AI Assistant
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/payments" class="sidebar-link">
                        💳 Payments
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/security" class="sidebar-link">
                        🔐 Security
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/settings" class="sidebar-link">
                        ⚙️ Einstellungen
                    </a>
                </li>
                <li class="sidebar-item" style="margin-top: 2rem;">
                    <a href="/logout" class="sidebar-link" style="color: var(--accent-danger);">
                        🚪 Abmelden
                    </a>
                </li>
            </ul>
        </aside>
        
        <main class="main-content">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <div>
                    <h1 style="font-size: 1.75rem; font-weight: 700;">Willkommen, {session.get('name', 'User')}!</h1>
                    <p style="color: var(--text-secondary);">Hier ist dein Business-Überblick</p>
                </div>
                {god_badge}
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">WhatsApp Nachrichten</div>
                    <div class="stat-value">1,247</div>
                    <div class="stat-change positive">↑ 12% diese Woche</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Aktive Leads</div>
                    <div class="stat-value">89</div>
                    <div class="stat-change positive">↑ 8 neue heute</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">Umsatz (Monat)</div>
                    <div class="stat-value">€24,580</div>
                    <div class="stat-change positive">↑ 23% vs. Vormonat</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-label">API Calls</div>
                    <div class="stat-value">45.2K</div>
                    <div class="stat-change">99.9% Uptime</div>
                </div>
            </div>
            
            <div class="table-container">
                <div style="padding: 1rem 1.5rem; border-bottom: 1px solid var(--border-color);">
                    <h2 style="font-size: 1.1rem; font-weight: 600;">Letzte Aktivitäten</h2>
                </div>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Typ</th>
                            <th>Beschreibung</th>
                            <th>Zeit</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>📱 WhatsApp</td>
                            <td>Neue Nachricht von +49 170 ****</td>
                            <td>vor 2 Min</td>
                            <td><span class="badge badge-success">Neu</span></td>
                        </tr>
                        <tr>
                            <td>👥 CRM</td>
                            <td>Lead "Max Mustermann" erstellt</td>
                            <td>vor 15 Min</td>
                            <td><span class="badge badge-primary">Erstellt</span></td>
                        </tr>
                        <tr>
                            <td>💳 Payment</td>
                            <td>Zahlung €299.00 erhalten</td>
                            <td>vor 1 Std</td>
                            <td><span class="badge badge-success">Erfolg</span></td>
                        </tr>
                        <tr>
                            <td>🤖 AI</td>
                            <td>Chatbot Anfrage beantwortet</td>
                            <td>vor 2 Std</td>
                            <td><span class="badge badge-success">Erledigt</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
    """
    return get_base_template(content, "Dashboard")

# =============================================================================
# ROUTES - WHATSAPP MODULE
# =============================================================================
@app.route('/dashboard/whatsapp')
@login_required
def whatsapp_dashboard():
    content = f"""
    <div class="dashboard">
        <aside class="sidebar">
            <div class="logo">
                <div class="logo-icon">💰</div>
                <span>West Money</span>
            </div>
            
            <ul class="sidebar-menu">
                <li class="sidebar-item">
                    <a href="/dashboard" class="sidebar-link">
                        📊 Dashboard
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/whatsapp" class="sidebar-link active">
                        📱 WhatsApp
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/crm" class="sidebar-link">
                        👥 CRM & Leads
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/ai" class="sidebar-link">
                        🤖 AI Assistant
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/payments" class="sidebar-link">
                        💳 Payments
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/security" class="sidebar-link">
                        🔐 Security
                    </a>
                </li>
                <li class="sidebar-item">
                    <a href="/dashboard/settings" class="sidebar-link">
                        ⚙️ Einstellungen
                    </a>
                </li>
                <li class="sidebar-item" style="margin-top: 2rem;">
                    <a href="/logout" class="sidebar-link" style="color: var(--accent-danger);">
                        🚪 Abmelden
                    </a>
                </li>
            </ul>
        </aside>
        
        <main class="main-content">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <div>
                    <h1 style="font-size: 1.75rem; font-weight: 700;">📱 WhatsApp Business</h1>
                    <p style="color: var(--text-secondary);">Nachrichten & Consent Management</p>
                </div>
                <button class="btn btn-primary" onclick="sendTestMessage()">
                    + Neue Nachricht
                </button>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Gesendete Nachrichten</div>
                    <div class="stat-value">1,247</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Empfangene</div>
                    <div class="stat-value">892</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Opt-In Rate</div>
                    <div class="stat-value">78%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Templates</div>
                    <div class="stat-value">12</div>
                </div>
            </div>
            
            <div class="card" style="margin-bottom: 1.5rem;">
                <h3 style="margin-bottom: 1rem;">Schnell-Nachricht senden</h3>
                <div style="display: flex; gap: 1rem;">
                    <input type="text" id="phoneNumber" class="form-input" placeholder="+49 170 1234567" style="flex: 1;">
                    <input type="text" id="messageText" class="form-input" placeholder="Nachricht eingeben..." style="flex: 2;">
                    <button class="btn btn-success" onclick="sendMessage()">Senden</button>
                </div>
                <p id="sendStatus" style="margin-top: 0.5rem; color: var(--text-secondary);"></p>
            </div>
            
            <div class="table-container">
                <div style="padding: 1rem 1.5rem; border-bottom: 1px solid var(--border-color);">
                    <h2 style="font-size: 1.1rem; font-weight: 600;">Letzte Konversationen</h2>
                </div>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Kontakt</th>
                            <th>Letzte Nachricht</th>
                            <th>Zeit</th>
                            <th>Consent</th>
                            <th>Aktion</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>+49 170 ****123</td>
                            <td>Vielen Dank für Ihre Anfrage...</td>
                            <td>vor 5 Min</td>
                            <td><span class="badge badge-success">Opt-In</span></td>
                            <td><button class="btn btn-secondary" style="padding: 0.4rem 0.8rem;">Antworten</button></td>
                        </tr>
                        <tr>
                            <td>+49 171 ****456</td>
                            <td>Können Sie mir mehr Infos...</td>
                            <td>vor 23 Min</td>
                            <td><span class="badge badge-success">Opt-In</span></td>
                            <td><button class="btn btn-secondary" style="padding: 0.4rem 0.8rem;">Antworten</button></td>
                        </tr>
                        <tr>
                            <td>+49 172 ****789</td>
                            <td>Termin bestätigt für...</td>
                            <td>vor 1 Std</td>
                            <td><span class="badge badge-warning">Pending</span></td>
                            <td><button class="btn btn-secondary" style="padding: 0.4rem 0.8rem;">Antworten</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </main>
    </div>
    
    <script>
        async function sendMessage() {{
            const phone = document.getElementById('phoneNumber').value;
            const message = document.getElementById('messageText').value;
            const status = document.getElementById('sendStatus');
            
            if (!phone || !message) {{
                status.textContent = '⚠️ Bitte Telefonnummer und Nachricht eingeben';
                status.style.color = 'var(--accent-warning)';
                return;
            }}
            
            status.textContent = '⏳ Sende...';
            status.style.color = 'var(--text-secondary)';
            
            try {{
                const response = await fetch('/api/whatsapp/send', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ to: phone, message: message }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    status.textContent = '✅ Nachricht gesendet!';
                    status.style.color = 'var(--accent-success)';
                    document.getElementById('messageText').value = '';
                }} else {{
                    status.textContent = '❌ Fehler: ' + (data.error || 'Unbekannter Fehler');
                    status.style.color = 'var(--accent-danger)';
                }}
            }} catch (error) {{
                status.textContent = '❌ Verbindungsfehler';
                status.style.color = 'var(--accent-danger)';
            }}
        }}
    </script>
    """
    return get_base_template(content, "WhatsApp Business")

# =============================================================================
# ROUTES - OTHER MODULES (Placeholders)
# =============================================================================
@app.route('/dashboard/crm')
@login_required
def crm_dashboard():
    return create_module_page("CRM & Leads", "👥", "HubSpot Integration & Lead Management")

@app.route('/dashboard/ai')
@login_required
def ai_dashboard():
    return create_module_page("AI Assistant", "🤖", "Claude AI Chatbot Integration")

@app.route('/dashboard/payments')
@login_required
def payments_dashboard():
    return create_module_page("Payments", "💳", "Stripe Payment Integration")

@app.route('/dashboard/security')
@login_required
def security_dashboard():
    return create_module_page("Security Center", "🔐", "DedSec Security Suite")

@app.route('/dashboard/settings')
@login_required
def settings_dashboard():
    return create_module_page("Einstellungen", "⚙️", "System & API Konfiguration")

def create_module_page(title, icon, description):
    content = f"""
    <div class="dashboard">
        <aside class="sidebar">
            <div class="logo">
                <div class="logo-icon">💰</div>
                <span>West Money</span>
            </div>
            
            <ul class="sidebar-menu">
                <li class="sidebar-item"><a href="/dashboard" class="sidebar-link">📊 Dashboard</a></li>
                <li class="sidebar-item"><a href="/dashboard/whatsapp" class="sidebar-link">📱 WhatsApp</a></li>
                <li class="sidebar-item"><a href="/dashboard/crm" class="sidebar-link">👥 CRM & Leads</a></li>
                <li class="sidebar-item"><a href="/dashboard/ai" class="sidebar-link">🤖 AI Assistant</a></li>
                <li class="sidebar-item"><a href="/dashboard/payments" class="sidebar-link">💳 Payments</a></li>
                <li class="sidebar-item"><a href="/dashboard/security" class="sidebar-link">🔐 Security</a></li>
                <li class="sidebar-item"><a href="/dashboard/settings" class="sidebar-link">⚙️ Einstellungen</a></li>
                <li class="sidebar-item" style="margin-top: 2rem;">
                    <a href="/logout" class="sidebar-link" style="color: var(--accent-danger);">🚪 Abmelden</a>
                </li>
            </ul>
        </aside>
        
        <main class="main-content">
            <div style="text-align: center; padding: 4rem 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
                <h1 style="font-size: 2rem; margin-bottom: 0.5rem;">{title}</h1>
                <p style="color: var(--text-secondary); margin-bottom: 2rem;">{description}</p>
                <span class="badge badge-warning">🚧 Coming Soon</span>
            </div>
        </main>
    </div>
    """
    return get_base_template(content, title)

# =============================================================================
# ROUTES - LOGOUT
# =============================================================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# =============================================================================
# API ROUTES
# =============================================================================
@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'online',
        'version': VERSION,
        'edition': EDITION,
        'timestamp': datetime.now().isoformat(),
        'services': {
            'whatsapp': bool(WHATSAPP_TOKEN),
            'hubspot': bool(HUBSPOT_API_KEY),
            'stripe': bool(STRIPE_SECRET_KEY),
            'claude': bool(CLAUDE_API_KEY)
        }
    })

@app.route('/api/whatsapp/send', methods=['POST'])
@login_required
def api_whatsapp_send():
    data = request.get_json()
    to = data.get('to', '').replace(' ', '').replace('+', '')
    message = data.get('message', '')
    
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        return jsonify({'success': False, 'error': 'WhatsApp nicht konfiguriert'})
    
    try:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        if 'messages' in result:
            return jsonify({'success': True, 'message_id': result['messages'][0]['id']})
        else:
            return jsonify({'success': False, 'error': result.get('error', {}).get('message', 'API Fehler')})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    return jsonify({
        'messages': {'total': 1247, 'today': 42},
        'leads': {'total': 89, 'new': 8},
        'revenue': {'monthly': 24580, 'growth': 23},
        'api_calls': {'total': 45200, 'uptime': 99.9}
    })

# =============================================================================
# WEBHOOK ROUTES
# =============================================================================
@app.route('/webhook/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'westmoney_verify')
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == verify_token:
            return challenge, 200
        return 'Forbidden', 403
    
    # POST - Incoming message
    data = request.get_json()
    print(f"📱 WhatsApp Webhook: {json.dumps(data, indent=2)}")
    return 'OK', 200

# =============================================================================
# ERROR HANDLERS
# =============================================================================
@app.errorhandler(404)
def not_found(e):
    content = """
    <div class="login-container">
        <div class="login-box animate-in" style="text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🔍</div>
            <h1 style="font-size: 2rem; margin-bottom: 0.5rem;">404 - Nicht gefunden</h1>
            <p style="color: var(--text-secondary); margin-bottom: 2rem;">Die Seite existiert nicht.</p>
            <a href="/" class="btn btn-primary">Zur Startseite</a>
        </div>
    </div>
    """
    return get_base_template(content, "404"), 404

@app.errorhandler(500)
def server_error(e):
    content = """
    <div class="login-container">
        <div class="login-box animate-in" style="text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">⚠️</div>
            <h1 style="font-size: 2rem; margin-bottom: 0.5rem;">500 - Server Fehler</h1>
            <p style="color: var(--text-secondary); margin-bottom: 2rem;">Etwas ist schief gelaufen.</p>
            <a href="/" class="btn btn-primary">Zur Startseite</a>
        </div>
    </div>
    """
    return get_base_template(content, "500"), 500

# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     ⚡ WEST MONEY OS v{VERSION} - {EDITION} ⚡                          
╠══════════════════════════════════════════════════════════════════════════════╣
║  🏢 Enterprise Universe GmbH                                                 ║
║  👤 Founder & CEO: Ömer Hüseyin Coşkun                                       ║
║  🌐 Starting on port 5000...                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=False)
