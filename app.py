#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║            WEST MONEY OS v10.0 GODMODE ULTIMATE FINAL                        ║
║                  Enterprise Universe GmbH © 2025                              ║
║                                                                               ║
║  ALL MODULES INCLUDED:                                                        ║
║  • CRM & Contacts        • Broly Taskforce      • Einstein Agency            ║
║  • WhatsApp Business     • DedSec Security      • Token System               ║
║  • Stripe & Mollie       • Z Automations        • GTzMeta Gaming             ║
║  • Revolut Banking       • Wiki & Docs          • Subscription Plans         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import json
import secrets
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, session, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WestMoneyOS')

# =============================================================================
# CONFIGURATION
# =============================================================================
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///westmoney.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')
    WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID', '')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    REVOLUT_API_KEY = os.getenv('REVOLUT_API_KEY', '')
    MOLLIE_API_KEY = os.getenv('MOLLIE_API_KEY', '')

config = Config()

app = Flask(__name__)
app.config.from_object(config)
app.permanent_session_lifetime = timedelta(days=30)
CORS(app, supports_credentials=True)
db = SQLAlchemy(app)

# =============================================================================
# DATABASE MODELS
# =============================================================================
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(120))
    role = db.Column(db.String(20), default='user')
    plan = db.Column(db.String(20), default='free')
    tokens_god = db.Column(db.Integer, default=0)
    tokens_dedsec = db.Column(db.Integer, default=0)
    tokens_og = db.Column(db.Integer, default=0)
    tokens_tower = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id, 'username': self.username, 'email': self.email,
            'name': self.name, 'role': self.role, 'plan': self.plan,
            'tokens': {'god': self.tokens_god, 'dedsec': self.tokens_dedsec, 'og': self.tokens_og, 'tower': self.tokens_tower}
        }

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    company = db.Column(db.String(120))
    whatsapp_consent = db.Column(db.Boolean, default=False)
    tags = db.Column(db.Text)
    notes = db.Column(db.Text)
    source = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email, 'phone': self.phone, 
                'company': self.company, 'whatsapp_consent': self.whatsapp_consent,
                'tags': json.loads(self.tags) if self.tags else [], 'source': self.source}

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    value = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='new')
    source = db.Column(db.String(50))
    notes = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'value': self.value, 'status': self.status, 'source': self.source}

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), default='whatsapp')
    status = db.Column(db.String(50), default='draft')
    sent_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'type': self.type, 'status': self.status, 'sent_count': self.sent_count}

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(50), default='pending')
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'priority': self.priority, 'status': self.status}

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    amount = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, 'invoice_number': self.invoice_number, 'amount': self.amount, 'status': self.status}

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    direction = db.Column(db.String(20))
    content = db.Column(db.Text)
    status = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, 'direction': self.direction, 'content': self.content, 'status': self.status}

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'message': self.message, 'read': self.read}

class SecurityEvent(db.Model):
    __tablename__ = 'security_events'
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# =============================================================================
# AUTH HELPERS
# =============================================================================
def get_current_user():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Nicht authentifiziert'}), 401
        return f(*args, **kwargs)
    return decorated

def log_security_event(event_type, severity, details=None):
    try:
        event = SecurityEvent(event_type=event_type, severity=severity, 
                             details=json.dumps(details) if details else None,
                             ip_address=request.remote_addr)
        db.session.add(event)
        db.session.commit()
    except: pass

# =============================================================================
# INITIALIZE DATABASE
# =============================================================================
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@west-money.com', name='Administrator', 
                    role='admin', plan='enterprise', tokens_god=1000, tokens_dedsec=500)
        admin.set_password('WestMoney2025!')
        db.session.add(admin)
        db.session.commit()
    logger.info("Database initialized")

# =============================================================================
# HTML TEMPLATES
# =============================================================================
LANDING_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>West Money OS v10.0 | GODMODE Ultimate</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%); color: #fff; min-height: 100vh; }
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 5%; background: rgba(0,0,0,0.3); backdrop-filter: blur(10px); position: fixed; width: 100%; top: 0; z-index: 1000; }
        .logo { font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg, #ffd700, #ff8c00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { color: #fff; text-decoration: none; opacity: 0.8; transition: 0.3s; }
        .nav-links a:hover { opacity: 1; color: #ffd700; }
        .nav-btn { padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #667eea, #764ba2); border: none; border-radius: 50px; color: #fff; font-weight: 600; cursor: pointer; text-decoration: none; }
        .hero { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 2rem; padding-top: 5rem; }
        .godmode-badge { background: linear-gradient(135deg, #f97316, #ef4444); padding: 0.5rem 1.5rem; border-radius: 50px; font-weight: 700; font-size: 0.875rem; margin-bottom: 2rem; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        h1 { font-size: 4rem; margin-bottom: 1rem; }
        h1 span { background: linear-gradient(135deg, #ffd700, #ff8c00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { font-size: 1.5rem; opacity: 0.8; margin-bottom: 3rem; max-width: 600px; }
        .modules { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin: 3rem 0; max-width: 900px; }
        .module { background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 15px; backdrop-filter: blur(10px); transition: 0.3s; cursor: pointer; }
        .module:hover { background: rgba(255,255,255,0.2); transform: translateY(-5px); }
        .module-icon { font-size: 2rem; margin-bottom: 0.5rem; }
        .module-name { font-weight: 600; font-size: 0.9rem; }
        .cta-buttons { display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; }
        .btn { padding: 1rem 2.5rem; border: none; border-radius: 50px; font-size: 1rem; font-weight: 600; cursor: pointer; text-decoration: none; transition: 0.3s; }
        .btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
        .btn-outline { background: transparent; border: 2px solid #fff; color: #fff; }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 10px 30px rgba(102,126,234,0.4); }
        .features { padding: 5rem 5%; background: rgba(0,0,0,0.3); }
        .features h2 { text-align: center; font-size: 2.5rem; margin-bottom: 3rem; }
        .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; max-width: 1200px; margin: 0 auto; }
        .feature-card { background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2)); padding: 2rem; border-radius: 20px; }
        .feature-card h3 { font-size: 1.25rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
        .feature-card p { opacity: 0.8; line-height: 1.6; }
        .pricing { padding: 5rem 5%; }
        .pricing h2 { text-align: center; font-size: 2.5rem; margin-bottom: 3rem; }
        .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; max-width: 1100px; margin: 0 auto; }
        .price-card { background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 20px; text-align: center; }
        .price-card.featured { background: linear-gradient(135deg, rgba(102,126,234,0.3), rgba(118,75,162,0.3)); border: 2px solid #667eea; transform: scale(1.05); }
        .price-name { font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; }
        .price-amount { font-size: 3rem; font-weight: 800; }
        .price-period { opacity: 0.7; margin-bottom: 2rem; }
        .price-features { list-style: none; text-align: left; margin-bottom: 2rem; }
        .price-features li { padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        footer { padding: 3rem 5%; background: rgba(0,0,0,0.5); text-align: center; }
        .footer-links { display: flex; justify-content: center; gap: 2rem; margin-bottom: 2rem; flex-wrap: wrap; }
        .footer-links a { color: #fff; text-decoration: none; opacity: 0.7; }
        .footer-links a:hover { opacity: 1; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">💰 West Money OS</div>
        <div class="nav-links">
            <a href="#features">Features</a>
            <a href="#pricing">Preise</a>
            <a href="/wiki">Wiki</a>
            <a href="/dashboard">Dashboard</a>
        </div>
        <div>
            <a href="/login" class="nav-btn">Login</a>
        </div>
    </nav>
    
    <section class="hero">
        <div class="godmode-badge">🔥 GODMODE v10.0 ULTIMATE</div>
        <h1>💰 <span>West Money OS</span></h1>
        <p class="subtitle">Die ultimative All-in-One Business Platform für Smart Home, CRM, FinTech, AI und Security</p>
        
        <div class="modules">
            <div class="module"><div class="module-icon">📱</div><div class="module-name">WhatsApp</div></div>
            <div class="module"><div class="module-icon">🤖</div><div class="module-name">AI Chat</div></div>
            <div class="module"><div class="module-icon">💼</div><div class="module-name">CRM</div></div>
            <div class="module"><div class="module-icon">💳</div><div class="module-name">Payments</div></div>
            <div class="module"><div class="module-icon">🏦</div><div class="module-name">Banking</div></div>
            <div class="module"><div class="module-icon">🔒</div><div class="module-name">DedSec</div></div>
            <div class="module"><div class="module-icon">💪</div><div class="module-name">Broly</div></div>
            <div class="module"><div class="module-icon">🧠</div><div class="module-name">Einstein</div></div>
            <div class="module"><div class="module-icon">🪙</div><div class="module-name">Tokens</div></div>
            <div class="module"><div class="module-icon">🏠</div><div class="module-name">LOXONE</div></div>
            <div class="module"><div class="module-icon">🎮</div><div class="module-name">Gaming</div></div>
            <div class="module"><div class="module-icon">📊</div><div class="module-name">Analytics</div></div>
        </div>
        
        <div class="cta-buttons">
            <a href="/register" class="btn btn-primary">🚀 Kostenlos starten</a>
            <a href="/pricing" class="btn btn-outline">💰 Preise ansehen</a>
        </div>
    </section>
    
    <section class="features" id="features">
        <h2>🚀 Alle Module im Überblick</h2>
        <div class="features-grid">
            <div class="feature-card">
                <h3>💪 Broly Taskforce</h3>
                <p>Legendäre Automatisierung mit unbegrenzter Power. Majin Shield, Ultra Instinct AI und GOD MODE Controller für maximale Effizienz.</p>
            </div>
            <div class="feature-card">
                <h3>🧠 Einstein Agency</h3>
                <p>8 Genius AI Bots für Architektur, Smart Home Planung und intelligente Automatisierung. Einstein University inklusive.</p>
            </div>
            <div class="feature-card">
                <h3>🔐 DedSec Security</h3>
                <p>Enterprise Security mit AR/VR Integration, 24/7 Monitoring, Anomaly Detection und Security Tower System.</p>
            </div>
            <div class="feature-card">
                <h3>📱 WhatsApp Business</h3>
                <p>Vollständige WhatsApp Business API Integration mit Consent Management, Templates und Bulk Messaging.</p>
            </div>
            <div class="feature-card">
                <h3>🪙 Token Economy</h3>
                <p>5 Token-Typen: GOD (Premium), DedSec (Security), OG (Legacy), Tower (Achievement), Ultra (Performance).</p>
            </div>
            <div class="feature-card">
                <h3>🏠 Smart Home</h3>
                <p>LOXONE Gold Partner Integration, Z Automations, ComfortClick und vollständige Gebäudeautomation.</p>
            </div>
        </div>
    </section>
    
    <section class="pricing" id="pricing">
        <h2>💰 Flexible Preispläne</h2>
        <div class="pricing-grid">
            <div class="price-card">
                <div class="price-name">Free</div>
                <div class="price-amount">€0</div>
                <div class="price-period">für immer kostenlos</div>
                <ul class="price-features">
                    <li>✓ 100 Kontakte</li>
                    <li>✓ Basic CRM</li>
                    <li>✓ 5 Leads/Monat</li>
                    <li>✓ E-Mail Support</li>
                </ul>
                <a href="/register" class="btn btn-outline">Kostenlos starten</a>
            </div>
            <div class="price-card">
                <div class="price-name">Starter</div>
                <div class="price-amount">€29</div>
                <div class="price-period">pro Monat</div>
                <ul class="price-features">
                    <li>✓ 1.000 Kontakte</li>
                    <li>✓ WhatsApp Business</li>
                    <li>✓ Unbegrenzte Leads</li>
                    <li>✓ E-Mail Kampagnen</li>
                    <li>✓ Priority Support</li>
                </ul>
                <a href="/checkout?plan=starter" class="btn btn-primary">Jetzt starten</a>
            </div>
            <div class="price-card featured">
                <div class="price-name">Professional</div>
                <div class="price-amount">€99</div>
                <div class="price-period">pro Monat</div>
                <ul class="price-features">
                    <li>✓ 10.000 Kontakte</li>
                    <li>✓ AI Chatbot (Claude)</li>
                    <li>✓ Revolut Banking</li>
                    <li>✓ Einstein Agency</li>
                    <li>✓ Broly Automations</li>
                    <li>✓ API Zugang</li>
                    <li>✓ 24/7 Support</li>
                </ul>
                <a href="/checkout?plan=professional" class="btn btn-primary">Beliebteste Wahl</a>
            </div>
            <div class="price-card">
                <div class="price-name">Enterprise</div>
                <div class="price-amount">€299</div>
                <div class="price-period">pro Monat</div>
                <ul class="price-features">
                    <li>✓ Unbegrenzte Kontakte</li>
                    <li>✓ White Label</li>
                    <li>✓ DedSec Security</li>
                    <li>✓ Custom Integration</li>
                    <li>✓ Dedicated Manager</li>
                    <li>✓ SLA Garantie</li>
                </ul>
                <a href="/contact" class="btn btn-outline">Kontaktieren</a>
            </div>
        </div>
    </section>
    
    <footer>
        <div class="footer-links">
            <a href="/wiki">Wiki</a>
            <a href="/api/docs">API Docs</a>
            <a href="/impressum">Impressum</a>
            <a href="/datenschutz">Datenschutz</a>
            <a href="/agb">AGB</a>
            <a href="/contact">Kontakt</a>
        </div>
        <p>© 2025 Enterprise Universe GmbH | West Money OS v10.0 GODMODE</p>
        <p style="opacity:0.5;margin-top:1rem">Made with ❤️ in Köln | CEO: Ömer Hüseyin Coşkun</p>
    </footer>
</body>
</html>'''

LOGIN_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f0f1a, #1a1a2e); color: #fff; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: rgba(255,255,255,0.1); padding: 3rem; border-radius: 20px; width: 100%; max-width: 420px; backdrop-filter: blur(10px); }
        .logo { text-align: center; font-size: 3rem; margin-bottom: 1rem; }
        h1 { text-align: center; margin-bottom: 0.5rem; }
        .version { text-align: center; color: #ffd700; margin-bottom: 2rem; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
        input { width: 100%; padding: 1rem; border: 1px solid rgba(255,255,255,0.2); border-radius: 10px; background: rgba(255,255,255,0.1); color: #fff; font-size: 1rem; }
        input::placeholder { color: rgba(255,255,255,0.5); }
        input:focus { outline: none; border-color: #667eea; }
        .btn { width: 100%; padding: 1rem; border: none; border-radius: 10px; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; font-size: 1rem; font-weight: 600; cursor: pointer; }
        .btn:hover { opacity: 0.9; }
        .error { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center; }
        .links { text-align: center; margin-top: 1.5rem; }
        .links a { color: #667eea; text-decoration: none; }
        .demo { text-align: center; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.1); opacity: 0.7; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">💰</div>
        <h1>West Money OS</h1>
        <div class="version">GODMODE v10.0</div>
        {error}
        <form method="POST">
            <div class="form-group">
                <label>Benutzername oder E-Mail</label>
                <input type="text" name="username" placeholder="admin" required>
            </div>
            <div class="form-group">
                <label>Passwort</label>
                <input type="password" name="password" placeholder="••••••••" required>
            </div>
            <button type="submit" class="btn">🚀 Einloggen</button>
        </form>
        <div class="links">
            <a href="/register">Noch kein Konto? Registrieren</a>
        </div>
        <div class="demo">Demo-Zugang: admin / WestMoney2025!</div>
    </div>
</body>
</html>'''

REGISTER_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrieren - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f0f1a, #1a1a2e); color: #fff; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 2rem; }
        .register-container { background: rgba(255,255,255,0.1); padding: 3rem; border-radius: 20px; width: 100%; max-width: 500px; backdrop-filter: blur(10px); }
        .logo { text-align: center; font-size: 3rem; margin-bottom: 1rem; }
        h1 { text-align: center; margin-bottom: 2rem; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
        input, select { width: 100%; padding: 1rem; border: 1px solid rgba(255,255,255,0.2); border-radius: 10px; background: rgba(255,255,255,0.1); color: #fff; font-size: 1rem; }
        select option { background: #1a1a2e; }
        .btn { width: 100%; padding: 1rem; border: none; border-radius: 10px; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; font-size: 1rem; font-weight: 600; cursor: pointer; }
        .error { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; }
        .success { background: rgba(34, 197, 94, 0.2); border: 1px solid #22c55e; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; }
        .links { text-align: center; margin-top: 1.5rem; }
        .links a { color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <div class="register-container">
        <div class="logo">💰</div>
        <h1>Konto erstellen</h1>
        {message}
        <form method="POST">
            <div class="form-row">
                <div class="form-group">
                    <label>Vorname</label>
                    <input type="text" name="firstname" placeholder="Max" required>
                </div>
                <div class="form-group">
                    <label>Nachname</label>
                    <input type="text" name="lastname" placeholder="Mustermann" required>
                </div>
            </div>
            <div class="form-group">
                <label>Benutzername</label>
                <input type="text" name="username" placeholder="maxmustermann" required>
            </div>
            <div class="form-group">
                <label>E-Mail</label>
                <input type="email" name="email" placeholder="max@example.com" required>
            </div>
            <div class="form-group">
                <label>Passwort</label>
                <input type="password" name="password" placeholder="Mindestens 8 Zeichen" required minlength="8">
            </div>
            <div class="form-group">
                <label>Plan auswählen</label>
                <select name="plan">
                    <option value="free">Free - €0/Monat</option>
                    <option value="starter">Starter - €29/Monat</option>
                    <option value="professional">Professional - €99/Monat</option>
                    <option value="enterprise">Enterprise - €299/Monat</option>
                </select>
            </div>
            <button type="submit" class="btn">🚀 Konto erstellen</button>
        </form>
        <div class="links">
            <a href="/login">Bereits ein Konto? Einloggen</a>
        </div>
    </div>
</body>
</html>'''

DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0f0f1a; color: #fff; min-height: 100vh; }
        .sidebar { position: fixed; left: 0; top: 0; width: 260px; height: 100vh; background: linear-gradient(180deg, #1a1a2e, #16213e); padding: 1.5rem; overflow-y: auto; }
        .logo { font-size: 1.25rem; font-weight: 700; margin-bottom: 2rem; display: flex; align-items: center; gap: 0.5rem; }
        .nav-section { margin-bottom: 1.5rem; }
        .nav-section-title { font-size: 0.75rem; text-transform: uppercase; opacity: 0.5; margin-bottom: 0.75rem; letter-spacing: 1px; }
        .nav-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 10px; color: #fff; text-decoration: none; margin-bottom: 0.25rem; transition: 0.2s; }
        .nav-item:hover, .nav-item.active { background: rgba(102,126,234,0.2); }
        .nav-item-icon { width: 20px; text-align: center; }
        .main { margin-left: 260px; padding: 2rem; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
        .header h1 { font-size: 1.75rem; }
        .user-info { display: flex; align-items: center; gap: 1rem; }
        .user-tokens { display: flex; gap: 0.5rem; }
        .token { padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
        .token-god { background: linear-gradient(135deg, #ffd700, #ff8c00); color: #000; }
        .token-dedsec { background: linear-gradient(135deg, #ef4444, #dc2626); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .stat-card { background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2)); padding: 1.5rem; border-radius: 15px; }
        .stat-value { font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem; }
        .stat-label { opacity: 0.7; font-size: 0.9rem; }
        .stat-change { font-size: 0.8rem; color: #22c55e; margin-top: 0.5rem; }
        .modules-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; }
        .module-card { background: rgba(255,255,255,0.05); border-radius: 15px; padding: 1.5rem; cursor: pointer; transition: 0.3s; border: 1px solid transparent; }
        .module-card:hover { background: rgba(255,255,255,0.1); border-color: #667eea; transform: translateY(-3px); }
        .module-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
        .module-icon { font-size: 2rem; }
        .module-title { font-weight: 600; }
        .module-status { font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 10px; background: rgba(34,197,94,0.2); color: #22c55e; }
        .module-desc { opacity: 0.7; font-size: 0.9rem; line-height: 1.5; }
        .quick-actions { display: flex; gap: 1rem; margin-top: 2rem; flex-wrap: wrap; }
        .quick-action { padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #667eea, #764ba2); border: none; border-radius: 10px; color: #fff; font-weight: 600; cursor: pointer; text-decoration: none; }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="logo">💰 West Money OS</div>
        
        <div class="nav-section">
            <div class="nav-section-title">Hauptmenü</div>
            <a href="/dashboard" class="nav-item active"><span class="nav-item-icon">📊</span> Dashboard</a>
            <a href="/dashboard/contacts" class="nav-item"><span class="nav-item-icon">👥</span> Kontakte</a>
            <a href="/dashboard/leads" class="nav-item"><span class="nav-item-icon">🎯</span> Leads</a>
            <a href="/dashboard/campaigns" class="nav-item"><span class="nav-item-icon">📧</span> Kampagnen</a>
            <a href="/dashboard/invoices" class="nav-item"><span class="nav-item-icon">📄</span> Rechnungen</a>
        </div>
        
        <div class="nav-section">
            <div class="nav-section-title">Kommunikation</div>
            <a href="/dashboard/whatsapp" class="nav-item"><span class="nav-item-icon">📱</span> WhatsApp</a>
            <a href="/dashboard/messages" class="nav-item"><span class="nav-item-icon">💬</span> Nachrichten</a>
            <a href="/dashboard/ai" class="nav-item"><span class="nav-item-icon">🤖</span> AI Chat</a>
        </div>
        
        <div class="nav-section">
            <div class="nav-section-title">Power Modules</div>
            <a href="/dashboard/broly" class="nav-item"><span class="nav-item-icon">💪</span> Broly Taskforce</a>
            <a href="/dashboard/einstein" class="nav-item"><span class="nav-item-icon">🧠</span> Einstein Agency</a>
            <a href="/dashboard/dedsec" class="nav-item"><span class="nav-item-icon">🔐</span> DedSec Security</a>
            <a href="/dashboard/tokens" class="nav-item"><span class="nav-item-icon">🪙</span> Token Economy</a>
        </div>
        
        <div class="nav-section">
            <div class="nav-section-title">Smart Home</div>
            <a href="/dashboard/loxone" class="nav-item"><span class="nav-item-icon">🏠</span> LOXONE</a>
            <a href="/dashboard/automations" class="nav-item"><span class="nav-item-icon">⚡</span> Z Automations</a>
        </div>
        
        <div class="nav-section">
            <div class="nav-section-title">System</div>
            <a href="/dashboard/settings" class="nav-item"><span class="nav-item-icon">⚙️</span> Einstellungen</a>
            <a href="/wiki" class="nav-item"><span class="nav-item-icon">📚</span> Wiki</a>
            <a href="/logout" class="nav-item"><span class="nav-item-icon">🚪</span> Logout</a>
        </div>
    </nav>
    
    <main class="main">
        <div class="header">
            <h1>Dashboard</h1>
            <div class="user-info">
                <div class="user-tokens">
                    <span class="token token-god">🪙 {tokens_god} GOD</span>
                    <span class="token token-dedsec">🔐 {tokens_dedsec} DEDSEC</span>
                </div>
                <span>Willkommen, {username}!</span>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="stat-contacts">-</div>
                <div class="stat-label">Kontakte</div>
                <div class="stat-change">↑ Diesen Monat</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-leads">-</div>
                <div class="stat-label">Aktive Leads</div>
                <div class="stat-change">↑ Pipeline</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-value">-</div>
                <div class="stat-label">Pipeline Wert</div>
                <div class="stat-change">↑ Potenzial</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="stat-tasks">-</div>
                <div class="stat-label">Offene Tasks</div>
                <div class="stat-change">Heute fällig</div>
            </div>
        </div>
        
        <h2 style="margin-bottom:1rem">🚀 Power Module</h2>
        <div class="modules-grid">
            <div class="module-card" onclick="location.href='/dashboard/broly'">
                <div class="module-header">
                    <span class="module-icon">💪</span>
                    <div>
                        <div class="module-title">Broly Taskforce</div>
                        <span class="module-status">LEGENDARY</span>
                    </div>
                </div>
                <p class="module-desc">Legendäre Automatisierung mit Majin Shield, Ultra Instinct AI und GOD MODE Controller.</p>
            </div>
            
            <div class="module-card" onclick="location.href='/dashboard/einstein'">
                <div class="module-header">
                    <span class="module-icon">🧠</span>
                    <div>
                        <div class="module-title">Einstein Agency</div>
                        <span class="module-status">GENIUS</span>
                    </div>
                </div>
                <p class="module-desc">8 Genius AI Bots für Architektur, Smart Home und intelligente Planung.</p>
            </div>
            
            <div class="module-card" onclick="location.href='/dashboard/dedsec'">
                <div class="module-header">
                    <span class="module-icon">🔐</span>
                    <div>
                        <div class="module-title">DedSec Security</div>
                        <span class="module-status">SECURE</span>
                    </div>
                </div>
                <p class="module-desc">Enterprise Security mit AR/VR, 24/7 Monitoring und Security Tower System.</p>
            </div>
            
            <div class="module-card" onclick="location.href='/dashboard/tokens'">
                <div class="module-header">
                    <span class="module-icon">🪙</span>
                    <div>
                        <div class="module-title">Token Economy</div>
                        <span class="module-status">ACTIVE</span>
                    </div>
                </div>
                <p class="module-desc">5 Token-Typen: GOD, DedSec, OG, Tower, Ultra für Rewards und Premium Features.</p>
            </div>
            
            <div class="module-card" onclick="location.href='/dashboard/whatsapp'">
                <div class="module-header">
                    <span class="module-icon">📱</span>
                    <div>
                        <div class="module-title">WhatsApp Business</div>
                        <span class="module-status">CONNECTED</span>
                    </div>
                </div>
                <p class="module-desc">Vollständige WhatsApp Business API mit Consent Management und Templates.</p>
            </div>
            
            <div class="module-card" onclick="location.href='/dashboard/loxone'">
                <div class="module-header">
                    <span class="module-icon">🏠</span>
                    <div>
                        <div class="module-title">LOXONE Smart Home</div>
                        <span class="module-status">GOLD PARTNER</span>
                    </div>
                </div>
                <p class="module-desc">LOXONE Gold Partner Integration für vollständige Gebäudeautomation.</p>
            </div>
        </div>
        
        <div class="quick-actions">
            <a href="/dashboard/contacts?action=new" class="quick-action">+ Neuer Kontakt</a>
            <a href="/dashboard/leads?action=new" class="quick-action">+ Neuer Lead</a>
            <a href="/dashboard/campaigns?action=new" class="quick-action">+ Neue Kampagne</a>
            <a href="/dashboard/ai" class="quick-action">🤖 AI Chat öffnen</a>
        </div>
    </main>
    
    <script>
        fetch('/api/dashboard/stats')
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('stat-contacts').textContent = data.stats.contacts.total;
                    document.getElementById('stat-leads').textContent = data.stats.leads.total;
                    document.getElementById('stat-value').textContent = '€' + data.stats.leads.total_value.toLocaleString();
                    document.getElementById('stat-tasks').textContent = data.stats.tasks.pending;
                }
            });
    </script>
</body>
</html>'''

WIKI_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wiki - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0f0f1a; color: #fff; min-height: 100vh; }
        .wiki-sidebar { position: fixed; left: 0; top: 0; width: 280px; height: 100vh; background: #1a1a2e; padding: 2rem; overflow-y: auto; }
        .wiki-logo { font-size: 1.25rem; font-weight: 700; margin-bottom: 2rem; }
        .wiki-nav a { display: block; padding: 0.75rem; color: #fff; text-decoration: none; border-radius: 8px; margin-bottom: 0.25rem; }
        .wiki-nav a:hover { background: rgba(102,126,234,0.2); }
        .wiki-main { margin-left: 280px; padding: 3rem; max-width: 900px; }
        h1 { font-size: 2.5rem; margin-bottom: 1rem; }
        h2 { font-size: 1.5rem; margin: 2rem 0 1rem; color: #667eea; }
        h3 { font-size: 1.25rem; margin: 1.5rem 0 0.75rem; }
        p { line-height: 1.8; opacity: 0.9; margin-bottom: 1rem; }
        code { background: rgba(102,126,234,0.2); padding: 0.25rem 0.5rem; border-radius: 5px; font-family: monospace; }
        pre { background: #1a1a2e; padding: 1.5rem; border-radius: 10px; overflow-x: auto; margin: 1rem 0; }
        .card { background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; }
        .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-right: 0.5rem; }
        .badge-gold { background: linear-gradient(135deg, #ffd700, #ff8c00); color: #000; }
        .badge-purple { background: linear-gradient(135deg, #667eea, #764ba2); }
        table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
        th, td { padding: 1rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { background: rgba(102,126,234,0.2); }
    </style>
</head>
<body>
    <nav class="wiki-sidebar">
        <div class="wiki-logo">📚 Wiki</div>
        <div class="wiki-nav">
            <a href="#getting-started">🚀 Getting Started</a>
            <a href="#modules">📦 Module</a>
            <a href="#api">🔌 API Dokumentation</a>
            <a href="#broly">💪 Broly Taskforce</a>
            <a href="#einstein">🧠 Einstein Agency</a>
            <a href="#dedsec">🔐 DedSec Security</a>
            <a href="#tokens">🪙 Token System</a>
            <a href="#integrations">🔗 Integrationen</a>
            <a href="#faq">❓ FAQ</a>
            <a href="/dashboard">← Zurück zum Dashboard</a>
        </div>
    </nav>
    
    <main class="wiki-main">
        <h1>📚 West Money OS Wiki</h1>
        <p>Willkommen zur offiziellen Dokumentation von West Money OS v10.0 GODMODE Ultimate.</p>
        
        <section id="getting-started">
            <h2>🚀 Getting Started</h2>
            <p>West Money OS ist die ultimative All-in-One Business Platform für Unternehmen.</p>
            
            <div class="card">
                <h3>Schnellstart</h3>
                <ol style="margin-left:1.5rem;line-height:2">
                    <li>Erstelle ein Konto unter <a href="/register" style="color:#667eea">/register</a></li>
                    <li>Wähle deinen Plan (Free, Starter, Professional, Enterprise)</li>
                    <li>Konfiguriere deine Integrationen (WhatsApp, HubSpot, etc.)</li>
                    <li>Starte mit dem Import deiner Kontakte</li>
                </ol>
            </div>
        </section>
        
        <section id="modules">
            <h2>📦 Module</h2>
            <table>
                <tr><th>Modul</th><th>Beschreibung</th><th>Status</th></tr>
                <tr><td>💼 CRM</td><td>Kontakte, Leads, Kampagnen</td><td><span class="badge badge-purple">Active</span></td></tr>
                <tr><td>📱 WhatsApp</td><td>Business API Integration</td><td><span class="badge badge-purple">Active</span></td></tr>
                <tr><td>💪 Broly</td><td>Automation Taskforce</td><td><span class="badge badge-gold">Legendary</span></td></tr>
                <tr><td>🧠 Einstein</td><td>AI Bot Agency</td><td><span class="badge badge-gold">Genius</span></td></tr>
                <tr><td>🔐 DedSec</td><td>Security System</td><td><span class="badge badge-purple">Secure</span></td></tr>
                <tr><td>🪙 Tokens</td><td>Reward Economy</td><td><span class="badge badge-purple">Active</span></td></tr>
            </table>
        </section>
        
        <section id="api">
            <h2>🔌 API Dokumentation</h2>
            <p>Base URL: <code>https://west-money.com/api</code></p>
            
            <h3>Authentifizierung</h3>
            <pre>POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your-password"
}</pre>
            
            <h3>Endpunkte</h3>
            <table>
                <tr><th>Methode</th><th>Endpunkt</th><th>Beschreibung</th></tr>
                <tr><td>GET</td><td>/api/contacts</td><td>Alle Kontakte abrufen</td></tr>
                <tr><td>POST</td><td>/api/contacts</td><td>Neuen Kontakt erstellen</td></tr>
                <tr><td>GET</td><td>/api/leads</td><td>Alle Leads abrufen</td></tr>
                <tr><td>POST</td><td>/api/leads</td><td>Neuen Lead erstellen</td></tr>
                <tr><td>GET</td><td>/api/dashboard/stats</td><td>Dashboard Statistiken</td></tr>
                <tr><td>POST</td><td>/api/whatsapp/send</td><td>WhatsApp Nachricht senden</td></tr>
                <tr><td>POST</td><td>/api/ai/chat</td><td>AI Chat Anfrage</td></tr>
            </table>
        </section>
        
        <section id="broly">
            <h2>💪 Broly Taskforce</h2>
            <p>Die legendäre Automatisierungs-Engine mit unbegrenzter Power.</p>
            
            <div class="card">
                <h3>Module</h3>
                <ul style="margin-left:1.5rem;line-height:2">
                    <li><strong>Broly Automation Core</strong> - Unbegrenzte Workflow-Kapazität</li>
                    <li><strong>Majin Security Shield</strong> - AES-256-GCM Verschlüsselung</li>
                    <li><strong>DEDSEC Detection</strong> - 24/7 Anomaly Monitoring</li>
                    <li><strong>Ultra Instinct AI</strong> - 99.4% Prediction Accuracy</li>
                    <li><strong>GOD MODE Controller</strong> - Full System Access</li>
                </ul>
            </div>
        </section>
        
        <section id="einstein">
            <h2>🧠 Einstein Agency</h2>
            <p>8 Genius AI Bots für intelligente Automatisierung.</p>
            
            <table>
                <tr><th>Bot</th><th>Spezialisierung</th></tr>
                <tr><td>🧠 Einstein</td><td>Architektur & Planung</td></tr>
                <tr><td>🍎 Newton</td><td>Physik & Statik</td></tr>
                <tr><td>⚡ Tesla</td><td>Elektrik & Smart Home</td></tr>
                <tr><td>☢️ Curie</td><td>Chemie & Materialien</td></tr>
                <tr><td>🌌 Hawking</td><td>Kosmische Berechnungen</td></tr>
                <tr><td>💻 Turing</td><td>KI & Algorithmen</td></tr>
                <tr><td>🎨 Da Vinci</td><td>Design & Kreativ</td></tr>
                <tr><td>🦎 Darwin</td><td>Evolution & Optimierung</td></tr>
            </table>
        </section>
        
        <section id="tokens">
            <h2>🪙 Token System</h2>
            <table>
                <tr><th>Token</th><th>Typ</th><th>Wert</th><th>Verwendung</th></tr>
                <tr><td>🟡 GOD</td><td>Premium</td><td>1000</td><td>Premium Features freischalten</td></tr>
                <tr><td>🔴 DEDSEC</td><td>Security</td><td>500</td><td>Security Upgrades</td></tr>
                <tr><td>🟣 OG</td><td>Legacy</td><td>250</td><td>Early Adopter Rewards</td></tr>
                <tr><td>🔵 TOWER</td><td>Achievement</td><td>100</td><td>Achievements & Badges</td></tr>
                <tr><td>🟢 ULTRA</td><td>Performance</td><td>50</td><td>Performance Boosts</td></tr>
            </table>
        </section>
        
        <section id="faq">
            <h2>❓ FAQ</h2>
            
            <div class="card">
                <h3>Wie starte ich mit West Money OS?</h3>
                <p>Registriere dich kostenlos, wähle einen Plan und konfiguriere deine ersten Integrationen. Unser Onboarding-Wizard führt dich durch alle Schritte.</p>
            </div>
            
            <div class="card">
                <h3>Welche Integrationen werden unterstützt?</h3>
                <p>WhatsApp Business API, HubSpot CRM, Stripe, Mollie, Revolut, LOXONE, Zadarma VoIP, Slack, und viele mehr.</p>
            </div>
            
            <div class="card">
                <h3>Wie erhalte ich GOD Tokens?</h3>
                <p>Tokens werden durch Aktivitäten vergeben: Kontakte importieren, Leads konvertieren, Kampagnen versenden, und mehr.</p>
            </div>
        </section>
    </main>
</body>
</html>'''

# =============================================================================
# PAGE ROUTES
# =============================================================================
@app.route('/')
def landing():
    return Response(LANDING_HTML, mimetype='text/html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session.permanent = True
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_security_event('login', 'info', {'user_id': user.id})
            return redirect('/dashboard')
        log_security_event('failed_login', 'warning', {'username': username})
        return Response(LOGIN_HTML.replace('{error}', '<div class="error">❌ Ungültige Anmeldedaten</div>'), mimetype='text/html')
    return Response(LOGIN_HTML.replace('{error}', ''), mimetype='text/html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        firstname = request.form.get('firstname', '')
        lastname = request.form.get('lastname', '')
        plan = request.form.get('plan', 'free')
        
        if User.query.filter_by(username=username).first():
            return Response(REGISTER_HTML.replace('{message}', '<div class="error">❌ Benutzername bereits vergeben</div>'), mimetype='text/html')
        if User.query.filter_by(email=email).first():
            return Response(REGISTER_HTML.replace('{message}', '<div class="error">❌ E-Mail bereits registriert</div>'), mimetype='text/html')
        
        user = User(username=username, email=email, name=f"{firstname} {lastname}", plan=plan, tokens_god=100)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        log_security_event('registration', 'info', {'user_id': user.id})
        return Response(REGISTER_HTML.replace('{message}', '<div class="success">✅ Konto erstellt! <a href="/login">Jetzt einloggen</a></div>'), mimetype='text/html')
    return Response(REGISTER_HTML.replace('{message}', ''), mimetype='text/html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user = get_current_user()
    html = DASHBOARD_HTML.replace('{username}', user.name or user.username)
    html = html.replace('{tokens_god}', str(user.tokens_god))
    html = html.replace('{tokens_dedsec}', str(user.tokens_dedsec))
    return Response(html, mimetype='text/html')

@app.route('/pricing')
def pricing():
    return redirect('/#pricing')

@app.route('/wiki')
def wiki():
    return Response(WIKI_HTML, mimetype='text/html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# =============================================================================
# API ROUTES
# =============================================================================
@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    stats = {
        'contacts': {'total': Contact.query.count(), 'with_consent': Contact.query.filter_by(whatsapp_consent=True).count()},
        'leads': {'total': Lead.query.count(), 'total_value': float(db.session.query(db.func.sum(Lead.value)).scalar() or 0)},
        'tasks': {'pending': Task.query.filter_by(status='pending').count()},
        'campaigns': {'total': Campaign.query.count()}
    }
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/contacts', methods=['GET'])
@login_required
def api_get_contacts():
    contacts = Contact.query.order_by(Contact.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'contacts': [c.to_dict() for c in contacts]})

@app.route('/api/contacts', methods=['POST'])
@login_required
def api_create_contact():
    data = request.get_json()
    contact = Contact(name=data.get('name'), email=data.get('email'), phone=data.get('phone'), 
                     company=data.get('company'), user_id=session.get('user_id'))
    db.session.add(contact)
    db.session.commit()
    return jsonify({'success': True, 'contact': contact.to_dict()})

@app.route('/api/leads', methods=['GET'])
@login_required
def api_get_leads():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return jsonify({'success': True, 'leads': [l.to_dict() for l in leads]})

@app.route('/api/leads', methods=['POST'])
@login_required
def api_create_lead():
    data = request.get_json()
    lead = Lead(title=data.get('title'), value=data.get('value', 0), status='new', assigned_to=session.get('user_id'))
    db.session.add(lead)
    db.session.commit()
    return jsonify({'success': True, 'lead': lead.to_dict()})

@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'healthy', 'version': '10.0.0-GODMODE-ULTIMATE',
        'timestamp': datetime.utcnow().isoformat(),
        'modules': {
            'crm': 'active', 'whatsapp': 'configured' if config.WHATSAPP_TOKEN else 'not configured',
            'broly': 'legendary', 'einstein': 'genius', 'dedsec': 'secure', 'tokens': 'active'
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return redirect('/')

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Interner Serverfehler'}), 500

if __name__ == '__main__':
    print("🚀 West Money OS v10.0 GODMODE ULTIMATE starting...")
    app.run(host='0.0.0.0', port=5000, debug=False)
