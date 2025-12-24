#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║         WEST MONEY OS v11.0 - ULTIMATE GODMODE EDITION                        ║
║                    Enterprise Universe GmbH © 2025                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import os, json, secrets, logging, re, requests
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, session, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WestMoneyOS')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///westmoney.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(Config())
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
    tokens_god = db.Column(db.Integer, default=100)
    tokens_dedsec = db.Column(db.Integer, default=50)
    tokens_og = db.Column(db.Integer, default=25)
    tokens_tower = db.Column(db.Integer, default=10)
    avatar = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email, 'name': self.name, 'role': self.role, 'plan': self.plan,
            'tokens': {'god': self.tokens_god, 'dedsec': self.tokens_dedsec, 'og': self.tokens_og, 'tower': self.tokens_tower}}

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    company = db.Column(db.String(120))
    position = db.Column(db.String(100))
    whatsapp_consent = db.Column(db.Boolean, default=False)
    tags = db.Column(db.Text, default='[]')
    notes = db.Column(db.Text)
    source = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email, 'phone': self.phone, 'company': self.company, 
            'position': self.position, 'whatsapp_consent': self.whatsapp_consent, 'status': self.status,
            'tags': json.loads(self.tags) if self.tags else [], 'notes': self.notes, 'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None}

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    contact_name = db.Column(db.String(120))
    company = db.Column(db.String(120))
    value = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='new')
    priority = db.Column(db.String(20), default='medium')
    source = db.Column(db.String(50))
    notes = db.Column(db.Text)
    expected_close = db.Column(db.DateTime)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'contact_name': self.contact_name, 'company': self.company,
            'value': self.value, 'status': self.status, 'priority': self.priority, 'source': self.source, 'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None}

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), default='whatsapp')
    status = db.Column(db.String(50), default='draft')
    template = db.Column(db.Text)
    target_tags = db.Column(db.Text, default='[]')
    sent_count = db.Column(db.Integer, default=0)
    open_count = db.Column(db.Integer, default=0)
    click_count = db.Column(db.Integer, default=0)
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'type': self.type, 'status': self.status, 'template': self.template,
            'sent_count': self.sent_count, 'open_count': self.open_count, 'click_count': self.click_count,
            'created_at': self.created_at.isoformat() if self.created_at else None}

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    contact_name = db.Column(db.String(120))
    contact_email = db.Column(db.String(120))
    items = db.Column(db.Text, default='[]')
    subtotal = db.Column(db.Float, default=0)
    tax_rate = db.Column(db.Float, default=19)
    tax_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='draft')
    due_date = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'invoice_number': self.invoice_number, 'contact_name': self.contact_name, 'contact_email': self.contact_email,
            'items': json.loads(self.items) if self.items else [], 'subtotal': self.subtotal, 'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount, 'total': self.total, 'status': self.status, 'notes': self.notes,
            'due_date': self.due_date.isoformat() if self.due_date else None, 'created_at': self.created_at.isoformat() if self.created_at else None}

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    contact_name = db.Column(db.String(120))
    direction = db.Column(db.String(20))
    channel = db.Column(db.String(20), default='whatsapp')
    content = db.Column(db.Text)
    status = db.Column(db.String(50), default='sent')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'contact_name': self.contact_name, 'direction': self.direction, 'channel': self.channel,
            'content': self.content, 'status': self.status, 'created_at': self.created_at.isoformat() if self.created_at else None}

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role = db.Column(db.String(20))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'role': self.role, 'content': self.content, 'created_at': self.created_at.isoformat() if self.created_at else None}

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(50), default='pending')
    category = db.Column(db.String(50))
    assigned_bot = db.Column(db.String(50))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'description': self.description, 'priority': self.priority, 
            'status': self.status, 'category': self.category, 'assigned_bot': self.assigned_bot,
            'due_date': self.due_date.isoformat() if self.due_date else None}

class SecurityEvent(db.Model):
    __tablename__ = 'security_events'
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    source = db.Column(db.String(100))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'event_type': self.event_type, 'severity': self.severity, 'source': self.source,
            'details': self.details, 'resolved': self.resolved, 'created_at': self.created_at.isoformat() if self.created_at else None}

class TokenTransaction(db.Model):
    __tablename__ = 'token_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    token_type = db.Column(db.String(20))
    amount = db.Column(db.Integer)
    action = db.Column(db.String(50))
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'token_type': self.token_type, 'amount': self.amount, 'action': self.action,
            'description': self.description, 'created_at': self.created_at.isoformat() if self.created_at else None}

class Automation(db.Model):
    __tablename__ = 'automations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    trigger_type = db.Column(db.String(50))
    trigger_config = db.Column(db.Text, default='{}')
    action_type = db.Column(db.String(50))
    action_config = db.Column(db.Text, default='{}')
    is_active = db.Column(db.Boolean, default=True)
    run_count = db.Column(db.Integer, default=0)
    last_run = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'trigger_type': self.trigger_type, 'action_type': self.action_type,
            'is_active': self.is_active, 'run_count': self.run_count, 'last_run': self.last_run.isoformat() if self.last_run else None}

# =============================================================================
# HELPERS
# =============================================================================
def get_current_user():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Nicht authentifiziert'}), 401
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

def get_env_var(key):
    try:
        with open('/var/www/westmoney/.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    if k == key:
                        return v
    except:
        pass
    return os.getenv(key, '')

def award_tokens(user_id, token_type, amount, description):
    user = User.query.get(user_id)
    if user:
        if token_type == 'god': user.tokens_god += amount
        elif token_type == 'dedsec': user.tokens_dedsec += amount
        elif token_type == 'og': user.tokens_og += amount
        elif token_type == 'tower': user.tokens_tower += amount
        tx = TokenTransaction(user_id=user_id, token_type=token_type, amount=amount, action='earn', description=description)
        db.session.add(tx)
        db.session.commit()

def generate_invoice_number():
    year_month = datetime.now().strftime('%Y%m')
    count = Invoice.query.filter(Invoice.invoice_number.like(f'INV-{year_month}%')).count()
    return f'INV-{year_month}-{count+1:04d}'
# =============================================================================
# SHARED STYLES (Continuation)
# =============================================================================
BASE_CSS = '''
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: #0a0a12; color: #fff; min-height: 100vh; }
a { color: inherit; text-decoration: none; }

.sidebar { position: fixed; left: 0; top: 0; width: 260px; height: 100vh; background: linear-gradient(180deg, #12121a 0%, #1a1a2e 100%); padding: 1.5rem; overflow-y: auto; border-right: 1px solid rgba(255,255,255,0.05); z-index: 100; }
.logo { font-size: 1.25rem; font-weight: 700; margin-bottom: 2rem; display: flex; align-items: center; gap: 0.5rem; }
.nav-section { margin-bottom: 1.5rem; }
.nav-title { font-size: 0.7rem; text-transform: uppercase; opacity: 0.4; margin-bottom: 0.75rem; letter-spacing: 1px; padding-left: 1rem; }
.nav-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 12px; color: rgba(255,255,255,0.7); margin-bottom: 0.25rem; transition: all 0.2s; }
.nav-item:hover { background: rgba(102,126,234,0.15); color: #fff; }
.nav-item.active { background: linear-gradient(135deg, rgba(102,126,234,0.3), rgba(118,75,162,0.3)); color: #fff; border: 1px solid rgba(102,126,234,0.3); }

.main { margin-left: 260px; min-height: 100vh; }
.topbar { padding: 1rem 2rem; background: rgba(0,0,0,0.3); border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 50; backdrop-filter: blur(10px); }
.topbar h1 { font-size: 1.5rem; font-weight: 600; }
.topbar-right { display: flex; align-items: center; gap: 1rem; }
.token-badge { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }
.token-badge.god { background: rgba(255,215,0,0.15); border: 1px solid rgba(255,215,0,0.3); color: #ffd700; }
.token-badge.dedsec { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #ef4444; }

.content { padding: 2rem; }
.card { background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.card-title { font-size: 1.1rem; font-weight: 600; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.stat-card { background: linear-gradient(135deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%); border: 1px solid rgba(102,126,234,0.2); border-radius: 16px; padding: 1.5rem; }
.stat-value { font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem; }
.stat-label { font-size: 0.85rem; opacity: 0.7; }
.stat-change { font-size: 0.8rem; color: #22c55e; margin-top: 0.5rem; }

.btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; border: none; border-radius: 10px; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102,126,234,0.4); }
.btn-secondary { background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.2); }
.btn-success { background: linear-gradient(135deg, #22c55e, #16a34a); color: #fff; }
.btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); color: #fff; }
.btn-sm { padding: 0.5rem 1rem; font-size: 0.8rem; }

.form-group { margin-bottom: 1rem; }
.form-label { display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem; }
.form-input { width: 100%; padding: 0.75rem 1rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: #fff; font-size: 0.95rem; }
.form-input:focus { outline: none; border-color: #667eea; background: rgba(255,255,255,0.08); }
select.form-input option { background: #1a1a2e; color: #fff; }
textarea.form-input { resize: vertical; min-height: 100px; }

table { width: 100%; border-collapse: collapse; }
th, td { padding: 1rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
th { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6; }
tr:hover { background: rgba(255,255,255,0.02); }

.badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-success { background: rgba(34,197,94,0.2); color: #22c55e; }
.badge-warning { background: rgba(245,158,11,0.2); color: #f59e0b; }
.badge-danger { background: rgba(239,68,68,0.2); color: #ef4444; }
.badge-info { background: rgba(59,130,246,0.2); color: #3b82f6; }
.badge-purple { background: rgba(139,92,246,0.2); color: #8b5cf6; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.8); display: none; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(5px); }
.modal-overlay.active { display: flex; }
.modal { background: #1a1a2e; border-radius: 20px; padding: 2rem; width: 90%; max-width: 500px; max-height: 90vh; overflow-y: auto; border: 1px solid rgba(255,255,255,0.1); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.modal-title { font-size: 1.25rem; font-weight: 600; }
.modal-close { background: none; border: none; color: #fff; font-size: 1.5rem; cursor: pointer; }

.empty-state { text-align: center; padding: 4rem 2rem; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; opacity: 0.5; }

.pipeline { display: flex; gap: 1rem; overflow-x: auto; padding-bottom: 1rem; }
.pipeline-column { flex: 0 0 280px; background: rgba(255,255,255,0.03); border-radius: 12px; padding: 1rem; }
.pipeline-header { font-size: 0.85rem; font-weight: 600; margin-bottom: 1rem; display: flex; justify-content: space-between; }
.pipeline-count { background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 10px; font-size: 0.75rem; }
.pipeline-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 1rem; margin-bottom: 0.75rem; cursor: pointer; }
.pipeline-card:hover { transform: translateY(-2px); border-color: rgba(102,126,234,0.3); }
.pipeline-card-title { font-weight: 500; margin-bottom: 0.5rem; }
.pipeline-card-meta { font-size: 0.8rem; opacity: 0.6; }
.pipeline-card-value { font-size: 0.9rem; color: #22c55e; font-weight: 600; margin-top: 0.5rem; }

.chat-container { display: flex; flex-direction: column; height: calc(100vh - 180px); }
.chat-messages { flex: 1; overflow-y: auto; padding: 1rem; }
.chat-message { max-width: 80%; margin-bottom: 1rem; }
.chat-message.user { margin-left: auto; }
.chat-message.assistant { margin-right: auto; }
.chat-bubble { padding: 1rem 1.25rem; border-radius: 16px; line-height: 1.5; }
.chat-message.user .chat-bubble { background: linear-gradient(135deg, #667eea, #764ba2); }
.chat-message.assistant .chat-bubble { background: rgba(255,255,255,0.1); }
.chat-input-container { padding: 1rem; border-top: 1px solid rgba(255,255,255,0.1); display: flex; gap: 1rem; }
.chat-input { flex: 1; padding: 1rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: #fff; resize: none; }

.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }

.fade-in { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.pulse { animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

@media (max-width: 768px) { .sidebar { transform: translateX(-100%); } .main { margin-left: 0; } .grid-2, .grid-3 { grid-template-columns: 1fr; } }
'''

def get_sidebar_html(active_page=''):
    return f'''
    <nav class="sidebar">
        <div class="logo">💰 West Money OS</div>
        <div class="nav-section">
            <div class="nav-title">Hauptmenü</div>
            <a href="/dashboard" class="nav-item {'active' if active_page == 'dashboard' else ''}"><span>📊</span> Dashboard</a>
            <a href="/dashboard/contacts" class="nav-item {'active' if active_page == 'contacts' else ''}"><span>👥</span> Kontakte</a>
            <a href="/dashboard/leads" class="nav-item {'active' if active_page == 'leads' else ''}"><span>🎯</span> Leads</a>
            <a href="/dashboard/campaigns" class="nav-item {'active' if active_page == 'campaigns' else ''}"><span>📧</span> Kampagnen</a>
            <a href="/dashboard/invoices" class="nav-item {'active' if active_page == 'invoices' else ''}"><span>📄</span> Rechnungen</a>
        </div>
        <div class="nav-section">
            <div class="nav-title">Kommunikation</div>
            <a href="/dashboard/whatsapp" class="nav-item {'active' if active_page == 'whatsapp' else ''}"><span>📱</span> WhatsApp</a>
            <a href="/dashboard/messages" class="nav-item {'active' if active_page == 'messages' else ''}"><span>💬</span> Nachrichten</a>
            <a href="/dashboard/ai" class="nav-item {'active' if active_page == 'ai' else ''}"><span>🤖</span> AI Chat</a>
        </div>
        <div class="nav-section">
            <div class="nav-title">Power Modules</div>
            <a href="/dashboard/broly" class="nav-item {'active' if active_page == 'broly' else ''}"><span>💪</span> Broly Taskforce</a>
            <a href="/dashboard/einstein" class="nav-item {'active' if active_page == 'einstein' else ''}"><span>🧠</span> Einstein Agency</a>
            <a href="/dashboard/dedsec" class="nav-item {'active' if active_page == 'dedsec' else ''}"><span>🔐</span> DedSec Security</a>
            <a href="/dashboard/tokens" class="nav-item {'active' if active_page == 'tokens' else ''}"><span>🪙</span> Token Economy</a>
        </div>
        <div class="nav-section">
            <div class="nav-title">Smart Home</div>
            <a href="/dashboard/loxone" class="nav-item {'active' if active_page == 'loxone' else ''}"><span>🏠</span> LOXONE</a>
            <a href="/dashboard/automations" class="nav-item {'active' if active_page == 'automations' else ''}"><span>⚡</span> Z Automations</a>
        </div>
        <div class="nav-section">
            <div class="nav-title">System</div>
            <a href="/dashboard/settings" class="nav-item {'active' if active_page == 'settings' else ''}"><span>⚙️</span> Einstellungen</a>
            <a href="/wiki" class="nav-item"><span>📚</span> Wiki</a>
            <a href="/logout" class="nav-item"><span>🚪</span> Logout</a>
        </div>
    </nav>'''

def get_topbar_html(title, user):
    return f'''
    <div class="topbar">
        <h1>{title}</h1>
        <div class="topbar-right">
            <div class="token-badge god">🪙 {user.tokens_god} GOD</div>
            <div class="token-badge dedsec">🔐 {user.tokens_dedsec} DEDSEC</div>
            <span style="opacity:0.7">Willkommen, {user.name or user.username}!</span>
        </div>
    </div>'''

def render_page(title, content, active_page='', user=None):
    if not user:
        user = get_current_user()
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>{BASE_CSS}</style>
</head>
<body>
    {get_sidebar_html(active_page)}
    <main class="main">
        {get_topbar_html(title, user)}
        <div class="content fade-in">{content}</div>
    </main>
</body>
</html>'''
# =============================================================================
# LANDING PAGE
# =============================================================================
LANDING_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>West Money OS | All-in-One Business Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0a0a12; color: #fff; }
        .navbar { position: fixed; top: 0; width: 100%; padding: 1rem 5%; display: flex; justify-content: space-between; align-items: center; z-index: 1000; background: rgba(10,10,18,0.9); backdrop-filter: blur(20px); }
        .nav-logo { font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg, #ffd700, #ff8c00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .nav-btn { padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50px; color: #fff; text-decoration: none; font-weight: 600; }
        .hero { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 2rem; padding-top: 100px; background: radial-gradient(circle at 50% 50%, rgba(102,126,234,0.1) 0%, transparent 50%); }
        .hero-badge { background: linear-gradient(135deg, #f97316, #ef4444); padding: 0.5rem 1.5rem; border-radius: 50px; font-weight: 700; font-size: 0.85rem; margin-bottom: 2rem; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        .hero h1 { font-size: 4rem; font-weight: 800; margin-bottom: 1.5rem; line-height: 1.1; }
        .hero h1 span { background: linear-gradient(135deg, #667eea, #764ba2, #f97316); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero p { font-size: 1.25rem; opacity: 0.7; max-width: 600px; margin-bottom: 3rem; }
        .hero-btns { display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center; }
        .hero-btns .btn { padding: 1rem 2.5rem; border-radius: 50px; font-size: 1rem; font-weight: 600; text-decoration: none; }
        .btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; }
        .btn-outline { border: 2px solid rgba(255,255,255,0.3); color: #fff; }
        .modules { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1rem; margin-top: 4rem; max-width: 900px; }
        .module { background: rgba(255,255,255,0.05); padding: 1.5rem 1rem; border-radius: 16px; text-align: center; cursor: pointer; }
        .module:hover { background: rgba(255,255,255,0.1); transform: translateY(-5px); }
        .module-icon { font-size: 2rem; margin-bottom: 0.5rem; }
        .module-name { font-size: 0.8rem; }
        .features { padding: 6rem 5%; background: rgba(0,0,0,0.3); }
        .features h2 { text-align: center; font-size: 2.5rem; margin-bottom: 3rem; }
        .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; max-width: 1200px; margin: 0 auto; }
        .feature-card { background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1)); border: 1px solid rgba(102,126,234,0.2); border-radius: 20px; padding: 2rem; }
        .feature-icon { font-size: 2.5rem; margin-bottom: 1rem; }
        .feature-card h3 { font-size: 1.25rem; margin-bottom: 0.75rem; }
        .feature-card p { opacity: 0.7; }
        footer { padding: 3rem 5%; text-align: center; border-top: 1px solid rgba(255,255,255,0.05); }
        @media (max-width: 768px) { .hero h1 { font-size: 2.5rem; } .modules { grid-template-columns: repeat(3, 1fr); } }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-logo">💰 West Money OS</div>
        <a href="/login" class="nav-btn">Login →</a>
    </nav>
    <section class="hero">
        <div class="hero-badge">🔥 v11.0 GODMODE ULTIMATE</div>
        <h1>Die <span>All-in-One</span><br>Business Platform</h1>
        <p>CRM, WhatsApp, AI, Payments, Smart Home und Security - alles in einer Plattform.</p>
        <div class="hero-btns">
            <a href="/register" class="btn btn-primary">🚀 Kostenlos starten</a>
            <a href="#features" class="btn btn-outline">Features ansehen</a>
        </div>
        <div class="modules">
            <div class="module"><div class="module-icon">👥</div><div class="module-name">CRM</div></div>
            <div class="module"><div class="module-icon">📱</div><div class="module-name">WhatsApp</div></div>
            <div class="module"><div class="module-icon">🤖</div><div class="module-name">AI Chat</div></div>
            <div class="module"><div class="module-icon">💳</div><div class="module-name">Payments</div></div>
            <div class="module"><div class="module-icon">🏠</div><div class="module-name">Smart Home</div></div>
            <div class="module"><div class="module-icon">🔐</div><div class="module-name">Security</div></div>
        </div>
    </section>
    <section class="features" id="features">
        <h2>Alles was du brauchst</h2>
        <div class="features-grid">
            <div class="feature-card"><div class="feature-icon">💪</div><h3>Broly Taskforce</h3><p>Legendäre Automatisierung mit Majin Shield und GOD MODE.</p></div>
            <div class="feature-card"><div class="feature-icon">🧠</div><h3>Einstein Agency</h3><p>8 spezialisierte AI Bots für Architektur und Smart Home.</p></div>
            <div class="feature-card"><div class="feature-icon">🔐</div><h3>DedSec Security</h3><p>Enterprise Security mit 24/7 Monitoring.</p></div>
            <div class="feature-card"><div class="feature-icon">📱</div><h3>WhatsApp Business</h3><p>API Integration mit Consent Management.</p></div>
            <div class="feature-card"><div class="feature-icon">🪙</div><h3>Token Economy</h3><p>5 Token-Typen für Rewards und Premium Features.</p></div>
            <div class="feature-card"><div class="feature-icon">🏠</div><h3>LOXONE Smart Home</h3><p>Gold Partner Integration für Gebäudeautomation.</p></div>
        </div>
    </section>
    <footer><p>© 2025 Enterprise Universe GmbH | West Money OS v11.0</p></footer>
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
        body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0a0a12 0%, #1a1a2e 100%); color: #fff; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { width: 100%; max-width: 420px; padding: 2rem; }
        .login-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; padding: 3rem; backdrop-filter: blur(20px); }
        .logo { text-align: center; font-size: 3.5rem; margin-bottom: 1rem; }
        h1 { text-align: center; font-size: 1.75rem; margin-bottom: 0.5rem; }
        .subtitle { text-align: center; color: #667eea; font-weight: 600; margin-bottom: 2rem; }
        .form-group { margin-bottom: 1.25rem; }
        label { display: block; font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem; }
        input { width: 100%; padding: 1rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: #fff; font-size: 1rem; }
        input:focus { outline: none; border-color: #667eea; }
        .btn { width: 100%; padding: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); border: none; border-radius: 12px; color: #fff; font-size: 1rem; font-weight: 600; cursor: pointer; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(102,126,234,0.4); }
        .error { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #ef4444; padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center; }
        .links { text-align: center; margin-top: 1.5rem; }
        .links a { color: #667eea; text-decoration: none; }
        .demo { text-align: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.1); }
        .demo-title { font-size: 0.75rem; text-transform: uppercase; opacity: 0.5; margin-bottom: 0.5rem; }
        .demo-creds code { background: rgba(102,126,234,0.2); padding: 0.25rem 0.5rem; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-card">
            <div class="logo">💰</div>
            <h1>West Money OS</h1>
            <div class="subtitle">GODMODE v11.0</div>
            {error}
            <form method="POST">
                <div class="form-group">
                    <label>Benutzername oder E-Mail</label>
                    <input type="text" name="username" placeholder="admin" required autofocus>
                </div>
                <div class="form-group">
                    <label>Passwort</label>
                    <input type="password" name="password" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn">🚀 Einloggen</button>
            </form>
            <div class="links"><a href="/register">Noch kein Konto? Registrieren</a></div>
            <div class="demo">
                <div class="demo-title">Demo-Zugang</div>
                <div class="demo-creds"><code>admin</code> / <code>663724</code></div>
            </div>
        </div>
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
        body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0a0a12 0%, #1a1a2e 100%); color: #fff; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 2rem; }
        .register-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; padding: 2.5rem; width: 100%; max-width: 500px; }
        .logo { text-align: center; font-size: 3rem; margin-bottom: 1rem; }
        h1 { text-align: center; font-size: 1.5rem; margin-bottom: 2rem; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; font-size: 0.85rem; margin-bottom: 0.5rem; }
        input, select { width: 100%; padding: 0.875rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: #fff; font-size: 1rem; }
        input:focus, select:focus { outline: none; border-color: #667eea; }
        select option { background: #1a1a2e; }
        .btn { width: 100%; padding: 1rem; background: linear-gradient(135deg, #667eea, #764ba2); border: none; border-radius: 12px; color: #fff; font-weight: 600; cursor: pointer; }
        .error { background: rgba(239,68,68,0.15); color: #ef4444; padding: 1rem; border-radius: 12px; margin-bottom: 1rem; }
        .success { background: rgba(34,197,94,0.15); color: #22c55e; padding: 1rem; border-radius: 12px; margin-bottom: 1rem; }
        .links { text-align: center; margin-top: 1.5rem; }
        .links a { color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <div class="register-card">
        <div class="logo">💰</div>
        <h1>Konto erstellen</h1>
        {message}
        <form method="POST">
            <div class="form-row">
                <div class="form-group"><label>Vorname</label><input type="text" name="firstname" required></div>
                <div class="form-group"><label>Nachname</label><input type="text" name="lastname" required></div>
            </div>
            <div class="form-group"><label>Benutzername</label><input type="text" name="username" required></div>
            <div class="form-group"><label>E-Mail</label><input type="email" name="email" required></div>
            <div class="form-group"><label>Passwort</label><input type="password" name="password" required minlength="6"></div>
            <div class="form-group">
                <label>Plan</label>
                <select name="plan">
                    <option value="free">Free - €0/Monat</option>
                    <option value="professional">Professional - €99/Monat</option>
                    <option value="enterprise">Enterprise - €299/Monat</option>
                </select>
            </div>
            <button type="submit" class="btn">🚀 Konto erstellen</button>
        </form>
        <div class="links"><a href="/login">Bereits registriert? Einloggen</a></div>
    </div>
</body>
</html>'''

# =============================================================================
# AUTH ROUTES
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
            return redirect('/dashboard')
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
            return Response(REGISTER_HTML.replace('{message}', '<div class="error">❌ Benutzername vergeben</div>'), mimetype='text/html')
        if User.query.filter_by(email=email).first():
            return Response(REGISTER_HTML.replace('{message}', '<div class="error">❌ E-Mail registriert</div>'), mimetype='text/html')
        user = User(username=username, email=email, name=f"{firstname} {lastname}", plan=plan, tokens_god=100)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        award_tokens(user.id, 'god', 50, 'Willkommensbonus')
        return Response(REGISTER_HTML.replace('{message}', '<div class="success">✅ Konto erstellt! <a href="/login">Jetzt einloggen</a></div>'), mimetype='text/html')
    return Response(REGISTER_HTML.replace('{message}', ''), mimetype='text/html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
# =============================================================================
# DASHBOARD ROUTE
# =============================================================================
@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    contacts_count = Contact.query.count()
    leads_count = Lead.query.count()
    leads_value = db.session.query(db.func.sum(Lead.value)).scalar() or 0
    tasks_pending = Task.query.filter_by(status='pending').count()
    
    content = f'''
    <div class="stats-grid">
        <div class="stat-card"><div class="stat-value">{contacts_count}</div><div class="stat-label">Kontakte</div></div>
        <div class="stat-card"><div class="stat-value">{leads_count}</div><div class="stat-label">Aktive Leads</div></div>
        <div class="stat-card"><div class="stat-value">€{leads_value:,.0f}</div><div class="stat-label">Pipeline Wert</div></div>
        <div class="stat-card"><div class="stat-value">{tasks_pending}</div><div class="stat-label">Offene Tasks</div></div>
    </div>
    <h2 style="margin-bottom:1.5rem">🚀 Power Module</h2>
    <div class="grid-3">
        <a href="/dashboard/broly" class="card" style="cursor:pointer">
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
                <span style="font-size:2.5rem">💪</span>
                <div><div style="font-weight:600">Broly Taskforce</div><span class="badge badge-warning">LEGENDARY</span></div>
            </div>
            <p style="opacity:0.7;font-size:0.9rem">Legendäre Automatisierung mit GOD MODE.</p>
        </a>
        <a href="/dashboard/einstein" class="card" style="cursor:pointer">
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
                <span style="font-size:2.5rem">🧠</span>
                <div><div style="font-weight:600">Einstein Agency</div><span class="badge badge-purple">GENIUS</span></div>
            </div>
            <p style="opacity:0.7;font-size:0.9rem">8 AI Bots für Architektur und Smart Home.</p>
        </a>
        <a href="/dashboard/dedsec" class="card" style="cursor:pointer">
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
                <span style="font-size:2.5rem">🔐</span>
                <div><div style="font-weight:600">DedSec Security</div><span class="badge badge-success">SECURE</span></div>
            </div>
            <p style="opacity:0.7;font-size:0.9rem">Enterprise Security mit 24/7 Monitoring.</p>
        </a>
        <a href="/dashboard/tokens" class="card" style="cursor:pointer">
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
                <span style="font-size:2.5rem">🪙</span>
                <div><div style="font-weight:600">Token Economy</div><span class="badge badge-info">ACTIVE</span></div>
            </div>
            <p style="opacity:0.7;font-size:0.9rem">GOD, DedSec, OG, Tower Tokens.</p>
        </a>
        <a href="/dashboard/whatsapp" class="card" style="cursor:pointer">
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
                <span style="font-size:2.5rem">📱</span>
                <div><div style="font-weight:600">WhatsApp Business</div><span class="badge badge-success">CONNECTED</span></div>
            </div>
            <p style="opacity:0.7;font-size:0.9rem">Business API mit Consent Management.</p>
        </a>
        <a href="/dashboard/loxone" class="card" style="cursor:pointer">
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
                <span style="font-size:2.5rem">🏠</span>
                <div><div style="font-weight:600">LOXONE Smart Home</div><span class="badge" style="background:rgba(255,215,0,0.2);color:#ffd700">GOLD</span></div>
            </div>
            <p style="opacity:0.7;font-size:0.9rem">Vollständige Gebäudeautomation.</p>
        </a>
    </div>
    <div style="display:flex;gap:1rem;margin-top:2rem;flex-wrap:wrap">
        <a href="/dashboard/contacts" class="btn btn-primary">+ Neuer Kontakt</a>
        <a href="/dashboard/leads" class="btn btn-primary">+ Neuer Lead</a>
        <a href="/dashboard/ai" class="btn btn-secondary">🤖 AI Chat öffnen</a>
    </div>'''
    return Response(render_page('Dashboard', content, 'dashboard', user), mimetype='text/html')

# =============================================================================
# CONTACTS PAGE
# =============================================================================
@app.route('/dashboard/contacts')
@login_required
def contacts_page():
    user = get_current_user()
    contacts = Contact.query.order_by(Contact.created_at.desc()).limit(100).all()
    rows = ''
    for c in contacts:
        consent = '<span class="badge badge-success">✓</span>' if c.whatsapp_consent else '<span class="badge badge-danger">✗</span>'
        rows += f'<tr onclick="editContact({c.id})" style="cursor:pointer"><td><strong>{c.name}</strong></td><td>{c.email or "-"}</td><td>{c.phone or "-"}</td><td>{c.company or "-"}</td><td>{consent}</td><td><button class="btn btn-sm btn-secondary" onclick="event.stopPropagation();editContact({c.id})">✏️</button> <button class="btn btn-sm btn-danger" onclick="event.stopPropagation();deleteContact({c.id})">🗑️</button></td></tr>'
    if not contacts:
        rows = '<tr><td colspan="6" class="empty-state"><div class="empty-icon">👥</div><div>Keine Kontakte</div></td></tr>'
    content = f'''
    <div class="card">
        <div class="card-header"><div class="card-title">👥 Kontakte ({len(contacts)})</div><button class="btn btn-primary" onclick="openModal('contact-modal')">+ Neuer Kontakt</button></div>
        <div class="table-container"><table><thead><tr><th>Name</th><th>E-Mail</th><th>Telefon</th><th>Firma</th><th>WhatsApp</th><th>Aktionen</th></tr></thead><tbody>{rows}</tbody></table></div>
    </div>
    <div id="contact-modal" class="modal-overlay" onclick="if(event.target===this)closeModal('contact-modal')">
        <div class="modal">
            <div class="modal-header"><div class="modal-title">Kontakt</div><button class="modal-close" onclick="closeModal('contact-modal')">&times;</button></div>
            <form id="contact-form" onsubmit="saveContact(event)">
                <input type="hidden" name="id" id="contact-id">
                <div class="form-group"><label class="form-label">Name *</label><input type="text" id="contact-name" class="form-input" required></div>
                <div class="grid-2">
                    <div class="form-group"><label class="form-label">E-Mail</label><input type="email" id="contact-email" class="form-input"></div>
                    <div class="form-group"><label class="form-label">Telefon</label><input type="tel" id="contact-phone" class="form-input"></div>
                </div>
                <div class="grid-2">
                    <div class="form-group"><label class="form-label">Firma</label><input type="text" id="contact-company" class="form-input"></div>
                    <div class="form-group"><label class="form-label">Position</label><input type="text" id="contact-position" class="form-input"></div>
                </div>
                <div class="form-group"><label class="form-label">Tags</label><input type="text" id="contact-tags" class="form-input" placeholder="VIP, Kunde, Lead"></div>
                <div class="form-group"><label><input type="checkbox" id="contact-consent"> WhatsApp Einwilligung</label></div>
                <div class="form-group"><label class="form-label">Notizen</label><textarea id="contact-notes" class="form-input"></textarea></div>
                <button type="submit" class="btn btn-primary" style="width:100%">💾 Speichern</button>
            </form>
        </div>
    </div>
    <script>
    function openModal(id) {{ document.getElementById(id).classList.add('active'); }}
    function closeModal(id) {{ document.getElementById(id).classList.remove('active'); document.getElementById('contact-form').reset(); }}
    async function saveContact(e) {{
        e.preventDefault();
        const id = document.getElementById('contact-id').value;
        const data = {{ name: document.getElementById('contact-name').value, email: document.getElementById('contact-email').value, phone: document.getElementById('contact-phone').value, company: document.getElementById('contact-company').value, position: document.getElementById('contact-position').value, tags: document.getElementById('contact-tags').value, whatsapp_consent: document.getElementById('contact-consent').checked, notes: document.getElementById('contact-notes').value }};
        await fetch(id ? `/api/contacts/${{id}}` : '/api/contacts', {{ method: id ? 'PUT' : 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(data) }});
        location.reload();
    }}
    async function editContact(id) {{
        const res = await fetch(`/api/contacts/${{id}}`);
        const data = await res.json();
        if (data.success) {{
            const c = data.contact;
            document.getElementById('contact-id').value = c.id;
            document.getElementById('contact-name').value = c.name;
            document.getElementById('contact-email').value = c.email || '';
            document.getElementById('contact-phone').value = c.phone || '';
            document.getElementById('contact-company').value = c.company || '';
            document.getElementById('contact-position').value = c.position || '';
            document.getElementById('contact-tags').value = (c.tags || []).join(', ');
            document.getElementById('contact-consent').checked = c.whatsapp_consent;
            document.getElementById('contact-notes').value = c.notes || '';
            openModal('contact-modal');
        }}
    }}
    async function deleteContact(id) {{ if(confirm('Löschen?')) {{ await fetch(`/api/contacts/${{id}}`, {{method:'DELETE'}}); location.reload(); }} }}
    </script>'''
    return Response(render_page('Kontakte', content, 'contacts', user), mimetype='text/html')

# =============================================================================
# LEADS PAGE
# =============================================================================
@app.route('/dashboard/leads')
@login_required
def leads_page():
    user = get_current_user()
    stages = [('new', '🆕 Neu'), ('qualified', '✅ Qualifiziert'), ('proposal', '📝 Angebot'), ('negotiation', '🤝 Verhandlung'), ('won', '🏆 Gewonnen'), ('lost', '❌ Verloren')]
    pipeline_html = ''
    for status, title in stages:
        leads = Lead.query.filter_by(status=status).all()
        total = sum(l.value for l in leads)
        cards = ''.join([f'<div class="pipeline-card" onclick="editLead({l.id})"><div class="pipeline-card-title">{l.title}</div><div class="pipeline-card-meta">{l.contact_name or l.company or "N/A"}</div><div class="pipeline-card-value">€{l.value:,.0f}</div></div>' for l in leads])
        pipeline_html += f'<div class="pipeline-column"><div class="pipeline-header"><span>{title}</span><span class="pipeline-count">{len(leads)} | €{total:,.0f}</span></div>{cards}</div>'
    content = f'''
    <div class="card">
        <div class="card-header"><div class="card-title">🎯 Sales Pipeline</div><button class="btn btn-primary" onclick="openModal('lead-modal')">+ Neuer Lead</button></div>
        <div class="pipeline">{pipeline_html}</div>
    </div>
    <div id="lead-modal" class="modal-overlay" onclick="if(event.target===this)closeModal('lead-modal')">
        <div class="modal">
            <div class="modal-header"><div class="modal-title">Lead</div><button class="modal-close" onclick="closeModal('lead-modal')">&times;</button></div>
            <form id="lead-form" onsubmit="saveLead(event)">
                <input type="hidden" id="lead-id">
                <div class="form-group"><label class="form-label">Titel *</label><input type="text" id="lead-title" class="form-input" required></div>
                <div class="grid-2">
                    <div class="form-group"><label class="form-label">Kontakt</label><input type="text" id="lead-contact" class="form-input"></div>
                    <div class="form-group"><label class="form-label">Firma</label><input type="text" id="lead-company" class="form-input"></div>
                </div>
                <div class="grid-2">
                    <div class="form-group"><label class="form-label">Wert (€)</label><input type="number" id="lead-value" class="form-input" value="0"></div>
                    <div class="form-group"><label class="form-label">Status</label><select id="lead-status" class="form-input"><option value="new">Neu</option><option value="qualified">Qualifiziert</option><option value="proposal">Angebot</option><option value="negotiation">Verhandlung</option><option value="won">Gewonnen</option><option value="lost">Verloren</option></select></div>
                </div>
                <div class="form-group"><label class="form-label">Priorität</label><select id="lead-priority" class="form-input"><option value="low">Niedrig</option><option value="medium" selected>Mittel</option><option value="high">Hoch</option></select></div>
                <div class="form-group"><label class="form-label">Notizen</label><textarea id="lead-notes" class="form-input"></textarea></div>
                <button type="submit" class="btn btn-primary" style="width:100%">💾 Speichern</button>
            </form>
        </div>
    </div>
    <script>
    function openModal(id) {{ document.getElementById(id).classList.add('active'); }}
    function closeModal(id) {{ document.getElementById(id).classList.remove('active'); document.getElementById('lead-form').reset(); }}
    async function saveLead(e) {{
        e.preventDefault();
        const id = document.getElementById('lead-id').value;
        const data = {{ title: document.getElementById('lead-title').value, contact_name: document.getElementById('lead-contact').value, company: document.getElementById('lead-company').value, value: parseFloat(document.getElementById('lead-value').value) || 0, status: document.getElementById('lead-status').value, priority: document.getElementById('lead-priority').value, notes: document.getElementById('lead-notes').value }};
        await fetch(id ? `/api/leads/${{id}}` : '/api/leads', {{ method: id ? 'PUT' : 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(data) }});
        location.reload();
    }}
    async function editLead(id) {{
        const res = await fetch(`/api/leads/${{id}}`);
        const data = await res.json();
        if (data.success) {{
            const l = data.lead;
            document.getElementById('lead-id').value = l.id;
            document.getElementById('lead-title').value = l.title;
            document.getElementById('lead-contact').value = l.contact_name || '';
            document.getElementById('lead-company').value = l.company || '';
            document.getElementById('lead-value').value = l.value;
            document.getElementById('lead-status').value = l.status;
            document.getElementById('lead-priority').value = l.priority;
            document.getElementById('lead-notes').value = l.notes || '';
            openModal('lead-modal');
        }}
    }}
    </script>'''
    return Response(render_page('Leads', content, 'leads', user), mimetype='text/html')
# =============================================================================
# AI CHAT PAGE
# =============================================================================
@app.route('/dashboard/ai')
@login_required
def ai_chat_page():
    user = get_current_user()
    history = ChatHistory.query.filter_by(user_id=user.id).order_by(ChatHistory.created_at.desc()).limit(50).all()
    history.reverse()
    messages_html = ''.join([f'<div class="chat-message {msg.role}"><div class="chat-bubble">{msg.content}</div></div>' for msg in history])
    if not history:
        messages_html = '<div style="text-align:center;padding:4rem;opacity:0.6"><div style="font-size:4rem;margin-bottom:1rem">🤖</div><h3>Willkommen beim AI Chat!</h3><p>Ich bin Claude, dein KI-Assistent.</p></div>'
    content = f'''
    <div class="card" style="height:calc(100vh - 180px);display:flex;flex-direction:column;padding:0">
        <div class="card-header" style="padding:1rem 1.5rem;border-bottom:1px solid rgba(255,255,255,0.1)"><div class="card-title">🤖 AI Chat (Claude)</div><button class="btn btn-sm btn-secondary" onclick="clearChat()">🗑️ Chat leeren</button></div>
        <div class="chat-messages" id="chat-messages">{messages_html}</div>
        <div class="chat-input-container">
            <textarea id="chat-input" class="chat-input" placeholder="Nachricht eingeben..." rows="1" onkeydown="if(event.key==='Enter'&&!event.shiftKey){{event.preventDefault();sendMessage()}}"></textarea>
            <button class="btn btn-primary" onclick="sendMessage()">Senden →</button>
        </div>
    </div>
    <script>
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
    async function sendMessage() {{
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;
        chatMessages.innerHTML += `<div class="chat-message user"><div class="chat-bubble">${{message}}</div></div>`;
        input.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight;
        const loadingId = 'loading-' + Date.now();
        chatMessages.innerHTML += `<div class="chat-message assistant" id="${{loadingId}}"><div class="chat-bubble pulse">⏳ Claude denkt nach...</div></div>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;
        try {{
            const res = await fetch('/api/ai/chat', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{ message }}) }});
            const data = await res.json();
            document.getElementById(loadingId).remove();
            if (data.success) {{ chatMessages.innerHTML += `<div class="chat-message assistant"><div class="chat-bubble">${{data.response}}</div></div>`; }}
            else {{ chatMessages.innerHTML += `<div class="chat-message assistant"><div class="chat-bubble" style="border:1px solid #ef4444">❌ ${{data.error}}</div></div>`; }}
        }} catch (err) {{
            document.getElementById(loadingId).remove();
            chatMessages.innerHTML += `<div class="chat-message assistant"><div class="chat-bubble" style="border:1px solid #ef4444">❌ Verbindungsfehler</div></div>`;
        }}
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }}
    async function clearChat() {{ if (confirm('Chat leeren?')) {{ await fetch('/api/ai/clear', {{ method: 'POST' }}); location.reload(); }} }}
    </script>'''
    return Response(render_page('AI Chat', content, 'ai', user), mimetype='text/html')

# =============================================================================
# BROLY PAGE
# =============================================================================
@app.route('/dashboard/broly')
@login_required
def broly_page():
    user = get_current_user()
    automations = Automation.query.filter_by(user_id=user.id).all()
    
    auto_rows = ''
    for a in automations:
        status_badge = '<span class="badge badge-success">Aktiv</span>' if a.is_active else '<span class="badge badge-danger">Inaktiv</span>'
        auto_rows += f'<tr><td><strong>{a.name}</strong></td><td>{a.trigger_type}</td><td>{a.action_type}</td><td>{a.run_count}</td><td>{status_badge}</td><td><button class="btn btn-sm btn-secondary" onclick="toggleAutomation({a.id})">⏯️</button></td></tr>'
    
    content = f'''
    <div class="stats-grid">
        <div class="stat-card" style="background:linear-gradient(135deg,rgba(239,68,68,0.2),rgba(220,38,38,0.2))"><div class="stat-value" style="color:#ef4444">∞</div><div class="stat-label">Power Level</div><div class="stat-change">LEGENDARY</div></div>
        <div class="stat-card"><div class="stat-value">{len(automations)}</div><div class="stat-label">Automations</div></div>
        <div class="stat-card"><div class="stat-value">{sum(a.run_count for a in automations)}</div><div class="stat-label">Ausführungen</div></div>
        <div class="stat-card"><div class="stat-value">{len([a for a in automations if a.is_active])}</div><div class="stat-label">Aktiv</div></div>
    </div>
    <div class="grid-2">
        <div class="card"><div class="card-header"><div class="card-title">💪 Broly Module</div></div>
            <div class="grid-2" style="gap:1rem">
                <div style="background:rgba(239,68,68,0.1);padding:1rem;border-radius:12px"><div style="font-size:1.5rem;margin-bottom:0.5rem">🔮</div><div style="font-weight:600">Majin Shield</div><div style="font-size:0.8rem;opacity:0.7">AES-256-GCM</div></div>
                <div style="background:rgba(139,92,246,0.1);padding:1rem;border-radius:12px"><div style="font-size:1.5rem;margin-bottom:0.5rem">👁️</div><div style="font-weight:600">DEDSEC Detection</div><div style="font-size:0.8rem;opacity:0.7">24/7 Active</div></div>
                <div style="background:rgba(34,197,94,0.1);padding:1rem;border-radius:12px"><div style="font-size:1.5rem;margin-bottom:0.5rem">🧠</div><div style="font-weight:600">Ultra Instinct AI</div><div style="font-size:0.8rem;opacity:0.7">99.4% Accuracy</div></div>
                <div style="background:rgba(255,215,0,0.1);padding:1rem;border-radius:12px"><div style="font-size:1.5rem;margin-bottom:0.5rem">👑</div><div style="font-weight:600">GOD MODE</div><div style="font-size:0.8rem;opacity:0.7">Full Access</div></div>
            </div>
        </div>
        <div class="card"><div class="card-header"><div class="card-title">👑 GOD MODE Commands</div></div>
            <div style="display:flex;flex-direction:column;gap:0.75rem">
                <button class="btn btn-secondary" onclick="godMode('SCAN_ALL')">🔍 Security Scan starten</button>
                <button class="btn btn-secondary" onclick="godMode('OPTIMIZE')">⚡ System optimieren</button>
                <button class="btn btn-secondary" onclick="godMode('SYNC_ALL')">🔄 Alle Daten synchronisieren</button>
                <button class="btn btn-danger" onclick="godMode('ULTRA_INSTINCT')">🧠 Ultra Instinct aktivieren</button>
            </div>
        </div>
    </div>
    <div class="card"><div class="card-header"><div class="card-title">⚡ Automations</div><button class="btn btn-primary" onclick="openModal('auto-modal')">+ Neue Automation</button></div>
        <div class="table-container"><table><thead><tr><th>Name</th><th>Trigger</th><th>Aktion</th><th>Runs</th><th>Status</th><th>Aktionen</th></tr></thead><tbody>{auto_rows if auto_rows else '<tr><td colspan="6" style="text-align:center;opacity:0.6">Keine Automations</td></tr>'}</tbody></table></div>
    </div>
    <div id="auto-modal" class="modal-overlay" onclick="if(event.target===this)closeModal('auto-modal')">
        <div class="modal">
            <div class="modal-header"><div class="modal-title">Neue Automation</div><button class="modal-close" onclick="closeModal('auto-modal')">&times;</button></div>
            <form onsubmit="saveAutomation(event)">
                <div class="form-group"><label class="form-label">Name</label><input type="text" name="name" class="form-input" required></div>
                <div class="form-group"><label class="form-label">Trigger</label><select name="trigger_type" class="form-input"><option value="new_contact">Neuer Kontakt</option><option value="lead_won">Lead gewonnen</option><option value="message_received">Nachricht empfangen</option></select></div>
                <div class="form-group"><label class="form-label">Aktion</label><select name="action_type" class="form-input"><option value="send_whatsapp">WhatsApp senden</option><option value="send_email">E-Mail senden</option><option value="create_task">Task erstellen</option><option value="award_tokens">Tokens vergeben</option></select></div>
                <button type="submit" class="btn btn-primary" style="width:100%">💾 Speichern</button>
            </form>
        </div>
    </div>
    <script>
    function openModal(id) {{ document.getElementById(id).classList.add('active'); }}
    function closeModal(id) {{ document.getElementById(id).classList.remove('active'); }}
    async function godMode(cmd) {{ alert('GOD MODE: ' + cmd + ' aktiviert!'); }}
    async function saveAutomation(e) {{ e.preventDefault(); const f = e.target; await fetch('/api/automations', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{ name: f.name.value, trigger_type: f.trigger_type.value, action_type: f.action_type.value }}) }}); location.reload(); }}
    async function toggleAutomation(id) {{ await fetch('/api/automations/' + id + '/toggle', {{ method: 'POST' }}); location.reload(); }}
    </script>'''
    return Response(render_page('Broly Taskforce', content, 'broly', user), mimetype='text/html')

# =============================================================================
# EINSTEIN PAGE
# =============================================================================
@app.route('/dashboard/einstein')
@login_required
def einstein_page():
    user = get_current_user()
    bots = [('🧠', 'Einstein', 'Architektur & Planung', 'genius'), ('🍎', 'Newton', 'Physik & Statik', 'active'), ('⚡', 'Tesla', 'Elektrik & Smart Home', 'active'), ('☢️', 'Curie', 'Chemie & Materialien', 'active'), ('🌌', 'Hawking', 'Kosmische Berechnungen', 'standby'), ('💻', 'Turing', 'KI & Algorithmen', 'active'), ('🎨', 'Da Vinci', 'Design & Kreativ', 'active'), ('🦎', 'Darwin', 'Evolution & Optimierung', 'standby')]
    
    bots_html = ''
    for icon, name, specialty, status in bots:
        if status == 'genius':
            badge = '<span class="badge badge-purple">GENIUS</span>'
        elif status == 'active':
            badge = '<span class="badge badge-success">AKTIV</span>'
        else:
            badge = '<span class="badge badge-warning">STANDBY</span>'
        bots_html += f'''<div class="card" style="cursor:pointer" onclick="activateBot('{name}')"><div style="display:flex;align-items:flex-start;gap:1rem"><div style="font-size:2.5rem">{icon}</div><div style="flex:1"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem"><div style="font-weight:600;font-size:1.1rem">{name} Bot</div>{badge}</div><div style="color:#667eea;font-size:0.85rem">{specialty}</div></div></div></div>'''
    
    task_count = Task.query.filter(Task.assigned_bot.isnot(None)).count()
    content = f'''
    <div class="stats-grid">
        <div class="stat-card" style="background:linear-gradient(135deg,rgba(139,92,246,0.2),rgba(109,40,217,0.2))"><div class="stat-value">8</div><div class="stat-label">Genius Bots</div></div>
        <div class="stat-card"><div class="stat-value">6</div><div class="stat-label">Aktive Bots</div></div>
        <div class="stat-card"><div class="stat-value">{task_count}</div><div class="stat-label">Tasks</div></div>
        <div class="stat-card"><div class="stat-value">99.4%</div><div class="stat-label">Accuracy</div></div>
    </div>
    <h2 style="margin-bottom:1.5rem">🧠 Bot Armee</h2>
    <div class="grid-4">{bots_html}</div>
    <script>function activateBot(name) {{ alert(name + ' Bot aktiviert!'); }}</script>'''
    return Response(render_page('Einstein Agency', content, 'einstein', user), mimetype='text/html')

# =============================================================================
# DEDSEC PAGE
# =============================================================================
@app.route('/dashboard/dedsec')
@login_required
def dedsec_page():
    user = get_current_user()
    events = SecurityEvent.query.order_by(SecurityEvent.created_at.desc()).limit(20).all()
    total = SecurityEvent.query.count()
    resolved = SecurityEvent.query.filter_by(resolved=True).count()
    high_sev = SecurityEvent.query.filter_by(severity='high', resolved=False).count()
    score = max(0, min(100, 100 - high_sev * 10 - (total - resolved) * 2))
    score_color = '#22c55e' if score >= 80 else '#f59e0b' if score >= 50 else '#ef4444'
    
    events_html = ''
    for e in events:
        date_str = e.created_at.strftime("%d.%m.%Y %H:%M") if e.created_at else "-"
        if e.severity == 'high':
            sev_badge = '<span class="badge badge-danger">HIGH</span>'
        elif e.severity == 'medium':
            sev_badge = '<span class="badge badge-warning">MEDIUM</span>'
        else:
            sev_badge = '<span class="badge badge-info">LOW</span>'
        status = "✅" if e.resolved else "⏳"
        events_html += f'<tr><td>{date_str}</td><td>{e.event_type}</td><td>{sev_badge}</td><td>{e.source or "-"}</td><td>{status}</td></tr>'
    
    content = f'''
    <div class="stats-grid">
        <div class="stat-card" style="background:linear-gradient(135deg,rgba(34,197,94,0.2),rgba(22,163,74,0.2));border-color:{score_color}"><div class="stat-value" style="color:{score_color}">{score}</div><div class="stat-label">Security Score</div></div>
        <div class="stat-card"><div class="stat-value">{total}</div><div class="stat-label">Events gesamt</div></div>
        <div class="stat-card"><div class="stat-value">{resolved}</div><div class="stat-label">Behoben</div></div>
        <div class="stat-card"><div class="stat-value">{high_sev}</div><div class="stat-label">Kritisch offen</div></div>
    </div>
    <div class="grid-2">
        <div class="card"><div class="card-header"><div class="card-title">🔐 Security Module</div></div>
            <div style="display:flex;flex-direction:column;gap:1rem">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(34,197,94,0.1);border-radius:12px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">🔥</span><div><div style="font-weight:600">Firewall</div></div></div><span class="badge badge-success">AKTIV</span></div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(34,197,94,0.1);border-radius:12px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">🔒</span><div><div style="font-weight:600">SSL/TLS</div></div></div><span class="badge badge-success">AKTIV</span></div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(34,197,94,0.1);border-radius:12px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">👁️</span><div><div style="font-weight:600">Monitoring</div></div></div><span class="badge badge-success">AKTIV</span></div>
            </div>
        </div>
        <div class="card"><div class="card-header"><div class="card-title">⚡ Quick Actions</div></div>
            <div style="display:flex;flex-direction:column;gap:0.75rem">
                <button class="btn btn-secondary" onclick="alert('Security Scan gestartet')">🔍 Security Scan</button>
                <button class="btn btn-secondary" onclick="alert('Logs werden geladen')">📋 Logs ansehen</button>
                <button class="btn btn-danger" onclick="if(confirm('Lockdown aktivieren?'))alert('🚨 Lockdown Mode!')">🚨 Lockdown Mode</button>
            </div>
        </div>
    </div>
    <div class="card"><div class="card-header"><div class="card-title">📋 Security Events</div></div><div class="table-container"><table><thead><tr><th>Zeit</th><th>Event</th><th>Severity</th><th>Quelle</th><th>Status</th></tr></thead><tbody>{events_html if events_html else '<tr><td colspan="5" style="text-align:center;opacity:0.6">Keine Events</td></tr>'}</tbody></table></div></div>'''
    return Response(render_page('DedSec Security', content, 'dedsec', user), mimetype='text/html')

# =============================================================================
# TOKENS PAGE
# =============================================================================
@app.route('/dashboard/tokens')
@login_required
def tokens_page():
    user = get_current_user()
    transactions = TokenTransaction.query.filter_by(user_id=user.id).order_by(TokenTransaction.created_at.desc()).limit(20).all()
    
    tx_html = ''
    for tx in transactions:
        date_str = tx.created_at.strftime("%d.%m.%Y %H:%M") if tx.created_at else "-"
        if tx.token_type == 'god':
            token_badge = '<span class="badge badge-warning">GOD</span>'
        elif tx.token_type == 'dedsec':
            token_badge = '<span class="badge badge-danger">DEDSEC</span>'
        elif tx.token_type == 'og':
            token_badge = '<span class="badge badge-purple">OG</span>'
        else:
            token_badge = '<span class="badge badge-info">TOWER</span>'
        amount_color = "#22c55e" if tx.amount > 0 else "#ef4444"
        amount_sign = "+" if tx.amount > 0 else ""
        tx_html += f'<tr><td>{date_str}</td><td>{token_badge}</td><td style="color:{amount_color};font-weight:600">{amount_sign}{tx.amount}</td><td>{tx.action}</td><td>{tx.description}</td></tr>'
    
    content = f'''
    <div class="stats-grid">
        <div class="stat-card" style="background:linear-gradient(135deg,rgba(255,215,0,0.2),rgba(255,140,0,0.2))"><div class="stat-value" style="color:#ffd700">{user.tokens_god}</div><div class="stat-label">🪙 GOD Tokens</div></div>
        <div class="stat-card" style="background:linear-gradient(135deg,rgba(239,68,68,0.2),rgba(220,38,38,0.2))"><div class="stat-value" style="color:#ef4444">{user.tokens_dedsec}</div><div class="stat-label">🔐 DEDSEC Tokens</div></div>
        <div class="stat-card" style="background:linear-gradient(135deg,rgba(139,92,246,0.2),rgba(109,40,217,0.2))"><div class="stat-value" style="color:#8b5cf6">{user.tokens_og}</div><div class="stat-label">🟣 OG Tokens</div></div>
        <div class="stat-card" style="background:linear-gradient(135deg,rgba(59,130,246,0.2),rgba(37,99,235,0.2))"><div class="stat-value" style="color:#3b82f6">{user.tokens_tower}</div><div class="stat-label">🏗️ TOWER Tokens</div></div>
    </div>
    <div class="grid-2">
        <div class="card"><div class="card-header"><div class="card-title">🎁 Tokens verdienen</div></div>
            <div style="display:flex;flex-direction:column;gap:1rem">
                <div style="display:flex;justify-content:space-between;padding:1rem;background:rgba(255,255,255,0.03);border-radius:12px"><div><div style="font-weight:500">Kontakt erstellen</div></div><span style="color:#ffd700;font-weight:600">+5 GOD</span></div>
                <div style="display:flex;justify-content:space-between;padding:1rem;background:rgba(255,255,255,0.03);border-radius:12px"><div><div style="font-weight:500">Lead gewinnen</div></div><span style="color:#ffd700;font-weight:600">+50 GOD</span></div>
                <div style="display:flex;justify-content:space-between;padding:1rem;background:rgba(255,255,255,0.03);border-radius:12px"><div><div style="font-weight:500">Security Scan</div></div><span style="color:#ef4444;font-weight:600">+10 DEDSEC</span></div>
                <div style="display:flex;justify-content:space-between;padding:1rem;background:rgba(255,255,255,0.03);border-radius:12px"><div><div style="font-weight:500">Täglicher Login</div></div><span style="color:#3b82f6;font-weight:600">+1 TOWER</span></div>
            </div>
        </div>
        <div class="card"><div class="card-header"><div class="card-title">🛒 Token Shop</div></div>
            <div style="display:flex;flex-direction:column;gap:1rem">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(255,215,0,0.1);border-radius:12px"><div><div style="font-weight:500">Premium Badge</div></div><button class="btn btn-sm btn-primary">100 GOD</button></div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(139,92,246,0.1);border-radius:12px"><div><div style="font-weight:500">Extra Kontakte</div></div><button class="btn btn-sm btn-primary">250 GOD</button></div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(239,68,68,0.1);border-radius:12px"><div><div style="font-weight:500">DedSec Shield</div></div><button class="btn btn-sm btn-danger">500 DEDSEC</button></div>
            </div>
        </div>
    </div>
    <div class="card"><div class="card-header"><div class="card-title">📜 Transaktionen</div></div><div class="table-container"><table><thead><tr><th>Datum</th><th>Token</th><th>Betrag</th><th>Aktion</th><th>Beschreibung</th></tr></thead><tbody>{tx_html if tx_html else '<tr><td colspan="5" style="text-align:center;opacity:0.6">Keine Transaktionen</td></tr>'}</tbody></table></div></div>'''
    return Response(render_page('Token Economy', content, 'tokens', user), mimetype='text/html')
# =============================================================================
# GENERIC DASHBOARD SUB-PAGES
# =============================================================================
@app.route('/dashboard/<page>')
@login_required
def dashboard_subpage(page):
    user = get_current_user()
    pages_config = {
        'whatsapp': ('📱 WhatsApp Business', 'whatsapp', generate_whatsapp_content),
        'messages': ('💬 Nachrichten', 'messages', generate_messages_content),
        'campaigns': ('📧 Kampagnen', 'campaigns', generate_campaigns_content),
        'invoices': ('📄 Rechnungen', 'invoices', generate_invoices_content),
        'loxone': ('🏠 LOXONE Smart Home', 'loxone', generate_loxone_content),
        'automations': ('⚡ Z Automations', 'automations', generate_automations_content),
        'settings': ('⚙️ Einstellungen', 'settings', generate_settings_content),
    }
    if page not in pages_config:
        return redirect('/dashboard')
    title, active, content_func = pages_config[page]
    content = content_func(user)
    return Response(render_page(title, content, active, user), mimetype='text/html')

def generate_whatsapp_content(user):
    consent_count = Contact.query.filter_by(whatsapp_consent=True).count()
    return f'''
    <div class="stats-grid">
        <div class="stat-card"><div class="stat-value">{consent_count}</div><div class="stat-label">Kontakte mit Consent</div></div>
        <div class="stat-card"><div class="stat-value">{Message.query.filter_by(channel='whatsapp').count()}</div><div class="stat-label">Nachrichten</div></div>
        <div class="stat-card"><div class="stat-value">98%</div><div class="stat-label">Zustellrate</div></div>
        <div class="stat-card"><div class="stat-value">45%</div><div class="stat-label">Öffnungsrate</div></div>
    </div>
    <div class="grid-2">
        <div class="card"><div class="card-header"><div class="card-title">📤 Nachricht senden</div></div>
            <form onsubmit="sendWhatsApp(event)">
                <div class="form-group"><label class="form-label">Empfänger (Telefon)</label><input type="tel" name="phone" class="form-input" placeholder="+49170..." required></div>
                <div class="form-group"><label class="form-label">Nachricht</label><textarea name="message" class="form-input" rows="4" required></textarea></div>
                <button type="submit" class="btn btn-success" style="width:100%">📱 Senden</button>
            </form>
        </div>
        <div class="card"><div class="card-header"><div class="card-title">📋 Templates</div></div>
            <div style="display:flex;flex-direction:column;gap:0.75rem">
                <div style="padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px;cursor:pointer"><div style="font-weight:500">👋 Willkommen</div><div style="font-size:0.8rem;opacity:0.6">Begrüßungsnachricht</div></div>
                <div style="padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px;cursor:pointer"><div style="font-weight:500">📞 Follow-Up</div><div style="font-size:0.8rem;opacity:0.6">Nachfass-Nachricht</div></div>
                <div style="padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px;cursor:pointer"><div style="font-weight:500">💰 Angebot</div><div style="font-size:0.8rem;opacity:0.6">Angebots-Nachricht</div></div>
            </div>
        </div>
    </div>
    <script>async function sendWhatsApp(e) {{ e.preventDefault(); alert('📱 WhatsApp wird gesendet...'); }}</script>'''

def generate_messages_content(user):
    return '''<div class="card"><div class="empty-state"><div class="empty-icon">💬</div><div class="empty-title">Nachrichten</div><div class="empty-text">Inbox wird bald verfügbar!</div></div></div>'''

def generate_campaigns_content(user):
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).limit(10).all()
    rows = ''.join([f'<tr><td><strong>{c.name}</strong></td><td>{c.type}</td><td><span class="badge badge-{"success" if c.status == "sent" else "warning" if c.status == "scheduled" else "info"}">{c.status}</span></td><td>{c.sent_count}</td><td>{c.open_count}</td></tr>' for c in campaigns])
    return f'''
    <div class="card">
        <div class="card-header"><div class="card-title">📧 Kampagnen</div><button class="btn btn-primary" onclick="openModal('campaign-modal')">+ Neue Kampagne</button></div>
        <div class="table-container"><table><thead><tr><th>Name</th><th>Typ</th><th>Status</th><th>Gesendet</th><th>Geöffnet</th></tr></thead><tbody>{rows if rows else '<tr><td colspan="5" style="text-align:center;opacity:0.6">Keine Kampagnen</td></tr>'}</tbody></table></div>
    </div>
    <div id="campaign-modal" class="modal-overlay" onclick="if(event.target===this)closeModal('campaign-modal')">
        <div class="modal">
            <div class="modal-header"><div class="modal-title">Neue Kampagne</div><button class="modal-close" onclick="closeModal('campaign-modal')">&times;</button></div>
            <form onsubmit="saveCampaign(event)">
                <div class="form-group"><label class="form-label">Name</label><input type="text" name="name" class="form-input" required></div>
                <div class="form-group"><label class="form-label">Typ</label><select name="type" class="form-input"><option value="whatsapp">WhatsApp</option><option value="email">E-Mail</option></select></div>
                <div class="form-group"><label class="form-label">Nachricht</label><textarea name="template" class="form-input" rows="4"></textarea></div>
                <button type="submit" class="btn btn-primary" style="width:100%">💾 Speichern</button>
            </form>
        </div>
    </div>
    <script>
    function openModal(id) {{ document.getElementById(id).classList.add('active'); }}
    function closeModal(id) {{ document.getElementById(id).classList.remove('active'); }}
    async function saveCampaign(e) {{ e.preventDefault(); const f = e.target; await fetch('/api/campaigns', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{ name: f.name.value, type: f.type.value, template: f.template.value }}) }}); location.reload(); }}
    </script>'''

def generate_invoices_content(user):
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(20).all()
    rows = ''.join([f'<tr><td><strong>{inv.invoice_number}</strong></td><td>{inv.contact_name or "-"}</td><td>€{inv.total:,.2f}</td><td>{inv.created_at.strftime("%d.%m.%Y") if inv.created_at else "-"}</td><td><span class="badge badge-{"success" if inv.status == "paid" else "warning" if inv.status == "sent" else "danger" if inv.status == "overdue" else "info"}">{inv.status}</span></td></tr>' for inv in invoices])
    return f'''
    <div class="stats-grid">
        <div class="stat-card"><div class="stat-value">€{sum(i.total for i in invoices if i.status == "paid"):,.0f}</div><div class="stat-label">Umsatz (bezahlt)</div></div>
        <div class="stat-card"><div class="stat-value">€{sum(i.total for i in invoices if i.status in ["sent", "overdue"]):,.0f}</div><div class="stat-label">Offene Rechnungen</div></div>
        <div class="stat-card"><div class="stat-value">{len(invoices)}</div><div class="stat-label">Rechnungen gesamt</div></div>
    </div>
    <div class="card">
        <div class="card-header"><div class="card-title">📄 Rechnungen</div><button class="btn btn-primary" onclick="openModal('invoice-modal')">+ Neue Rechnung</button></div>
        <div class="table-container"><table><thead><tr><th>Nr.</th><th>Kunde</th><th>Betrag</th><th>Datum</th><th>Status</th></tr></thead><tbody>{rows if rows else '<tr><td colspan="5" style="text-align:center;opacity:0.6">Keine Rechnungen</td></tr>'}</tbody></table></div>
    </div>
    <div id="invoice-modal" class="modal-overlay" onclick="if(event.target===this)closeModal('invoice-modal')">
        <div class="modal">
            <div class="modal-header"><div class="modal-title">Neue Rechnung</div><button class="modal-close" onclick="closeModal('invoice-modal')">&times;</button></div>
            <form onsubmit="saveInvoice(event)">
                <div class="form-group"><label class="form-label">Kunde</label><input type="text" name="contact_name" class="form-input" required></div>
                <div class="form-group"><label class="form-label">E-Mail</label><input type="email" name="contact_email" class="form-input"></div>
                <div class="form-group"><label class="form-label">Betrag (€)</label><input type="number" name="total" class="form-input" step="0.01" required></div>
                <button type="submit" class="btn btn-primary" style="width:100%">💾 Erstellen</button>
            </form>
        </div>
    </div>
    <script>
    function openModal(id) {{ document.getElementById(id).classList.add('active'); }}
    function closeModal(id) {{ document.getElementById(id).classList.remove('active'); }}
    async function saveInvoice(e) {{ e.preventDefault(); const f = e.target; await fetch('/api/invoices', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{ contact_name: f.contact_name.value, contact_email: f.contact_email.value, total: parseFloat(f.total.value) }}) }}); location.reload(); }}
    </script>'''

def generate_loxone_content(user):
    return '''
    <div class="stats-grid">
        <div class="stat-card" style="background:linear-gradient(135deg,rgba(34,197,94,0.2),rgba(22,163,74,0.2))"><div class="stat-value" style="color:#22c55e">12</div><div class="stat-label">Geräte verbunden</div></div>
        <div class="stat-card"><div class="stat-value">4</div><div class="stat-label">Räume</div></div>
        <div class="stat-card"><div class="stat-value">22°C</div><div class="stat-label">Durchschn. Temp</div></div>
        <div class="stat-card"><div class="stat-value">45%</div><div class="stat-label">Energie gespart</div></div>
    </div>
    <div class="grid-2">
        <div class="card"><div class="card-header"><div class="card-title">🏠 Räume</div></div>
            <div style="display:flex;flex-direction:column;gap:0.75rem">
                <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">🛋️</span><div><div style="font-weight:500">Wohnzimmer</div><div style="font-size:0.8rem;opacity:0.6">22°C • Licht 80%</div></div></div><span class="badge badge-success">Komfort</span></div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">🛏️</span><div><div style="font-weight:500">Schlafzimmer</div><div style="font-size:0.8rem;opacity:0.6">19°C • Licht Aus</div></div></div><span class="badge badge-info">Nacht</span></div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">🍳</span><div><div style="font-weight:500">Küche</div><div style="font-size:0.8rem;opacity:0.6">21°C • Licht 100%</div></div></div><span class="badge badge-success">Aktiv</span></div>
                <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">💼</span><div><div style="font-weight:500">Büro</div><div style="font-size:0.8rem;opacity:0.6">23°C • Licht 70%</div></div></div><span class="badge badge-purple">Fokus</span></div>
            </div>
        </div>
        <div class="card"><div class="card-header"><div class="card-title">🎬 Szenen</div></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem">
                <button class="btn btn-secondary" onclick="alert('Morgen aktiviert!')" style="padding:1.5rem;flex-direction:column;height:auto"><span style="font-size:2rem;margin-bottom:0.5rem">🌅</span><span>Morgen</span></button>
                <button class="btn btn-secondary" onclick="alert('Arbeit aktiviert!')" style="padding:1.5rem;flex-direction:column;height:auto"><span style="font-size:2rem;margin-bottom:0.5rem">💼</span><span>Arbeit</span></button>
                <button class="btn btn-secondary" onclick="alert('Entspannen aktiviert!')" style="padding:1.5rem;flex-direction:column;height:auto"><span style="font-size:2rem;margin-bottom:0.5rem">🌙</span><span>Entspannen</span></button>
                <button class="btn btn-secondary" onclick="alert('Abwesend aktiviert!')" style="padding:1.5rem;flex-direction:column;height:auto"><span style="font-size:2rem;margin-bottom:0.5rem">🏃</span><span>Abwesend</span></button>
            </div>
        </div>
    </div>
    <div class="card"><div class="card-header"><div class="card-title">⚡ Energieverbrauch</div></div>
        <div style="display:flex;justify-content:space-between;align-items:center;padding:2rem;background:linear-gradient(135deg,rgba(34,197,94,0.1),rgba(22,163,74,0.1));border-radius:12px">
            <div><div style="font-size:3rem;font-weight:700;color:#22c55e">2.4 kWh</div><div style="opacity:0.7">Heute verbraucht</div></div>
            <div style="text-align:right"><div style="color:#22c55e;font-size:1.25rem;font-weight:600">↓ 15%</div><div style="opacity:0.7;font-size:0.9rem">vs. gestern</div></div>
        </div>
    </div>'''

def generate_automations_content(user):
    return '''<div class="card"><div class="empty-state"><div class="empty-icon">⚡</div><div class="empty-title">Z Automations</div><div class="empty-text">Workflow Engine wird bald verfügbar!</div><a href="/dashboard/broly" class="btn btn-primary">Broly Taskforce nutzen</a></div></div>'''

def generate_settings_content(user):
    return f'''
    <div class="grid-2">
        <div class="card"><div class="card-header"><div class="card-title">👤 Profil</div></div>
            <form onsubmit="saveProfile(event)">
                <div class="form-group"><label class="form-label">Name</label><input type="text" name="name" class="form-input" value="{user.name or ''}"></div>
                <div class="form-group"><label class="form-label">E-Mail</label><input type="email" name="email" class="form-input" value="{user.email}"></div>
                <div class="form-group"><label class="form-label">Neues Passwort</label><input type="password" name="password" class="form-input" placeholder="Leer lassen um nicht zu ändern"></div>
                <button type="submit" class="btn btn-primary">💾 Speichern</button>
            </form>
        </div>
        <div class="card"><div class="card-header"><div class="card-title">📊 Plan</div></div>
            <div style="padding:1.5rem;background:linear-gradient(135deg,rgba(102,126,234,0.2),rgba(118,75,162,0.2));border-radius:12px;margin-bottom:1rem"><div style="font-size:0.8rem;opacity:0.6;margin-bottom:0.25rem">Aktueller Plan</div><div style="font-size:1.5rem;font-weight:700">{user.plan.upper()}</div></div>
            <a href="#" class="btn btn-primary" style="width:100%">⬆️ Plan upgraden</a>
        </div>
    </div>
    <div class="card"><div class="card-header"><div class="card-title">🔑 API Konfiguration</div></div>
        <div style="display:flex;flex-direction:column;gap:1rem">
            <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">🤖</span><div><div style="font-weight:500">Claude AI</div></div></div><span class="badge badge-success">✓ Konfiguriert</span></div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">📱</span><div><div style="font-weight:500">WhatsApp Business</div></div></div><span class="badge badge-warning">⏳ Pending</span></div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">💳</span><div><div style="font-weight:500">Stripe</div></div></div><span class="badge badge-warning">⏳ Pending</span></div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:1rem;background:rgba(255,255,255,0.03);border-radius:10px"><div style="display:flex;align-items:center;gap:1rem"><span style="font-size:1.5rem">🏠</span><div><div style="font-weight:500">LOXONE</div></div></div><span class="badge badge-warning">⏳ Pending</span></div>
        </div>
    </div>
    <script>async function saveProfile(e) {{ e.preventDefault(); const f = e.target; await fetch('/api/user/profile', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{ name: f.name.value, email: f.email.value, password: f.password.value }}) }}); alert('Profil gespeichert!'); }}</script>'''

# =============================================================================
# WIKI PAGE
# =============================================================================
@app.route('/wiki')
def wiki_page():
    return Response(render_page('Wiki', '''
    <div class="card"><div class="card-header"><div class="card-title">📚 West Money OS Dokumentation</div></div>
        <div style="display:flex;flex-direction:column;gap:1rem">
            <div style="padding:1.5rem;background:rgba(255,255,255,0.03);border-radius:12px"><h3 style="margin-bottom:0.5rem">🚀 Getting Started</h3><p style="opacity:0.7">Lerne die Grundlagen von West Money OS und starte durch.</p></div>
            <div style="padding:1.5rem;background:rgba(255,255,255,0.03);border-radius:12px"><h3 style="margin-bottom:0.5rem">👥 CRM Module</h3><p style="opacity:0.7">Kontakte, Leads und Kampagnen verwalten.</p></div>
            <div style="padding:1.5rem;background:rgba(255,255,255,0.03);border-radius:12px"><h3 style="margin-bottom:0.5rem">💪 Power Modules</h3><p style="opacity:0.7">Broly, Einstein, DedSec und Token Economy.</p></div>
            <div style="padding:1.5rem;background:rgba(255,255,255,0.03);border-radius:12px"><h3 style="margin-bottom:0.5rem">🔌 API Integration</h3><p style="opacity:0.7">WhatsApp, Stripe, LOXONE und mehr.</p></div>
        </div>
    </div>''', '', get_current_user() if 'user_id' in session else User(username='Guest', tokens_god=0, tokens_dedsec=0)), mimetype='text/html')
# =============================================================================
# LEGAL PAGES - DSGVO COMPLIANCE
# =============================================================================

LEGAL_STYLES = '''
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', sans-serif; background: #0a0a12; color: #fff; line-height: 1.8; }
    .legal-nav { padding: 1rem 5%; background: rgba(0,0,0,0.5); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; backdrop-filter: blur(10px); z-index: 100; }
    .legal-nav a { color: #fff; text-decoration: none; }
    .legal-nav .logo { font-weight: 700; font-size: 1.25rem; }
    .legal-content { max-width: 900px; margin: 0 auto; padding: 3rem 2rem; }
    .legal-content h1 { font-size: 2.5rem; margin-bottom: 0.5rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .legal-content .updated { opacity: 0.6; margin-bottom: 3rem; }
    .legal-content h2 { font-size: 1.5rem; margin: 2.5rem 0 1rem; color: #667eea; }
    .legal-content h3 { font-size: 1.2rem; margin: 2rem 0 0.75rem; }
    .legal-content p { margin-bottom: 1rem; opacity: 0.9; }
    .legal-content ul, .legal-content ol { margin: 1rem 0 1rem 2rem; }
    .legal-content li { margin-bottom: 0.5rem; }
    .legal-content a { color: #667eea; }
    .legal-content .highlight { background: rgba(102,126,234,0.1); border-left: 4px solid #667eea; padding: 1rem 1.5rem; margin: 1.5rem 0; border-radius: 0 10px 10px 0; }
    .legal-content table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
    .legal-content th, .legal-content td { padding: 1rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .legal-content th { background: rgba(102,126,234,0.1); }
    .legal-footer { padding: 2rem 5%; border-top: 1px solid rgba(255,255,255,0.1); text-align: center; opacity: 0.6; }
    .legal-links { display: flex; gap: 2rem; justify-content: center; margin-bottom: 1rem; }
    .legal-links a { color: #667eea; text-decoration: none; }
</style>
'''

def legal_page_wrapper(title, content):
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - West Money OS | Enterprise Universe GmbH</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    {LEGAL_STYLES}
</head>
<body>
    <nav class="legal-nav">
        <a href="/" class="logo">💰 West Money OS</a>
        <div style="display:flex;gap:2rem">
            <a href="/impressum">Impressum</a>
            <a href="/datenschutz">Datenschutz</a>
            <a href="/agb">AGB</a>
            <a href="/login">Login</a>
        </div>
    </nav>
    <main class="legal-content">{content}</main>
    <footer class="legal-footer">
        <div class="legal-links">
            <a href="/impressum">Impressum</a>
            <a href="/datenschutz">Datenschutz</a>
            <a href="/agb">AGB</a>
            <a href="/widerruf">Widerrufsrecht</a>
        </div>
        <p>© 2025 Enterprise Universe GmbH. Alle Rechte vorbehalten.</p>
    </footer>
</body>
</html>'''

@app.route('/impressum')
def impressum():
    content = '''
    <h1>Impressum</h1>
    <p class="updated">Stand: Dezember 2025</p>
    
    <h2>Angaben gemäß § 5 TMG</h2>
    <p><strong>Enterprise Universe GmbH</strong><br>
    Geschäftsführer: Ömer Hüseyin Coşkun<br>
    [Geschäftsadresse einfügen]<br>
    [PLZ Stadt], Deutschland</p>
    
    <h2>Kontakt</h2>
    <p>E-Mail: info@enterprise-universe.de<br>
    Telefon: [Telefonnummer einfügen]<br>
    Website: www.west-money.com</p>
    
    <h2>Registereintrag</h2>
    <p>Handelsregister: [Amtsgericht]<br>
    Registernummer: HRB [Nummer]<br>
    USt-IdNr.: DE[Nummer]</p>
    
    <h2>Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2>
    <p>Ömer Hüseyin Coşkun<br>
    [Adresse wie oben]</p>
    
    <h2>Zugehörige Unternehmen</h2>
    <ul>
        <li><strong>West Money Bau</strong> - Smart Home Konstruktion & LOXONE Integration</li>
        <li><strong>Z Automation</strong> - Gebäudeautomation</li>
        <li><strong>DedSec World AI</strong> - AR/VR Security Systeme</li>
    </ul>
    
    <h2>EU-Streitschlichtung</h2>
    <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: 
    <a href="https://ec.europa.eu/consumers/odr/" target="_blank">https://ec.europa.eu/consumers/odr/</a></p>
    <p>Unsere E-Mail-Adresse finden Sie oben im Impressum.</p>
    
    <h2>Verbraucherstreitbeilegung/Universalschlichtungsstelle</h2>
    <p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer 
    Verbraucherschlichtungsstelle teilzunehmen.</p>
    
    <h2>Haftung für Inhalte</h2>
    <p>Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den 
    allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht 
    verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen 
    zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.</p>
    
    <h2>Haftung für Links</h2>
    <p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. 
    Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten 
    Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich.</p>
    
    <h2>Urheberrecht</h2>
    <p>Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen 
    Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der 
    Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.</p>
    '''
    return Response(legal_page_wrapper('Impressum', content), mimetype='text/html')

@app.route('/datenschutz')
def datenschutz():
    content = '''
    <h1>Datenschutzerklärung</h1>
    <p class="updated">Stand: Dezember 2025 | DSGVO-konform</p>
    
    <div class="highlight">
        <strong>Kurzübersicht:</strong> Wir nehmen den Schutz Ihrer persönlichen Daten sehr ernst. 
        Diese Datenschutzerklärung informiert Sie über Art, Umfang und Zweck der Verarbeitung 
        personenbezogener Daten auf unserer Plattform West Money OS.
    </div>
    
    <h2>1. Verantwortlicher</h2>
    <p><strong>Enterprise Universe GmbH</strong><br>
    Geschäftsführer: Ömer Hüseyin Coşkun<br>
    E-Mail: datenschutz@enterprise-universe.de</p>
    
    <h2>2. Erhebung und Speicherung personenbezogener Daten</h2>
    <h3>2.1 Beim Besuch der Website</h3>
    <p>Beim Aufrufen unserer Website werden automatisch Informationen an den Server übermittelt:</p>
    <ul>
        <li>IP-Adresse des anfragenden Rechners</li>
        <li>Datum und Uhrzeit des Zugriffs</li>
        <li>Name und URL der abgerufenen Datei</li>
        <li>Website, von der aus der Zugriff erfolgt (Referrer-URL)</li>
        <li>Verwendeter Browser und ggf. das Betriebssystem</li>
    </ul>
    <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse)</p>
    
    <h3>2.2 Bei Registrierung und Nutzung</h3>
    <p>Bei der Registrierung erheben wir:</p>
    <ul>
        <li>Name, Vorname</li>
        <li>E-Mail-Adresse</li>
        <li>Telefonnummer (optional)</li>
        <li>Unternehmensdaten (optional)</li>
        <li>Passwort (verschlüsselt gespeichert)</li>
    </ul>
    <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)</p>
    
    <h2>3. WhatsApp Business Integration</h2>
    <div class="highlight">
        <strong>Wichtig:</strong> Die Nutzung der WhatsApp Business API erfordert Ihre ausdrückliche Einwilligung.
    </div>
    <h3>3.1 Einwilligung (Consent)</h3>
    <p>Bevor wir Sie über WhatsApp kontaktieren können, müssen Sie aktiv einwilligen. Diese Einwilligung:</p>
    <ul>
        <li>Wird separat für jeden Kontakt erfasst</li>
        <li>Kann jederzeit widerrufen werden</li>
        <li>Wird mit Zeitstempel dokumentiert</li>
    </ul>
    <h3>3.2 Verarbeitete Daten</h3>
    <ul>
        <li>Telefonnummer</li>
        <li>Nachrichteninhalt</li>
        <li>Zustellstatus</li>
        <li>Zeitstempel</li>
    </ul>
    <p><strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. a DSGVO (Einwilligung)</p>
    <h3>3.3 Bulk-Consent-Management</h3>
    <p>Sie können den WhatsApp-Consent-Status mehrerer Kontakte gleichzeitig bearbeiten. 
    Weitere Informationen: <a href="https://knowledge.hubspot.com/de/inbox/edit-the-whatsapp-consent-status-of-your-contacts-in-bulk" target="_blank">HubSpot WhatsApp Consent Guide</a></p>
    
    <h2>4. CRM-Datenverarbeitung</h2>
    <p>Im Rahmen unseres CRM-Systems verarbeiten wir:</p>
    <table>
        <tr><th>Datenkategorie</th><th>Zweck</th><th>Speicherdauer</th></tr>
        <tr><td>Kontaktdaten</td><td>Kundenbeziehungsmanagement</td><td>Bis Löschungsanfrage</td></tr>
        <tr><td>Lead-Informationen</td><td>Vertriebsprozesse</td><td>3 Jahre nach Inaktivität</td></tr>
        <tr><td>Kommunikationshistorie</td><td>Serviceverbesserung</td><td>2 Jahre</td></tr>
        <tr><td>Rechnungsdaten</td><td>Buchführung</td><td>10 Jahre (gesetzlich)</td></tr>
    </table>
    
    <h2>5. Cookies und Tracking</h2>
    <h3>5.1 Technisch notwendige Cookies</h3>
    <p>Wir verwenden Session-Cookies für die Authentifizierung. Diese sind für den Betrieb erforderlich.</p>
    <h3>5.2 Optionale Cookies</h3>
    <p>Analyse-Cookies werden nur mit Ihrer ausdrücklichen Einwilligung gesetzt.</p>
    
    <h2>6. Ihre Rechte (DSGVO Art. 15-22)</h2>
    <ul>
        <li><strong>Auskunft (Art. 15):</strong> Sie können Auskunft über Ihre gespeicherten Daten verlangen</li>
        <li><strong>Berichtigung (Art. 16):</strong> Sie können unrichtige Daten korrigieren lassen</li>
        <li><strong>Löschung (Art. 17):</strong> Sie können die Löschung Ihrer Daten verlangen</li>
        <li><strong>Einschränkung (Art. 18):</strong> Sie können die Verarbeitung einschränken lassen</li>
        <li><strong>Datenübertragbarkeit (Art. 20):</strong> Sie können Ihre Daten in einem gängigen Format erhalten</li>
        <li><strong>Widerspruch (Art. 21):</strong> Sie können der Verarbeitung widersprechen</li>
    </ul>
    
    <div class="highlight">
        <strong>Anfragen:</strong> Senden Sie Ihre Datenschutzanfragen an: datenschutz@enterprise-universe.de
    </div>
    
    <h2>7. Datensicherheit</h2>
    <p>Wir setzen technische und organisatorische Sicherheitsmaßnahmen ein:</p>
    <ul>
        <li>SSL/TLS-Verschlüsselung</li>
        <li>Passwort-Hashing (bcrypt)</li>
        <li>Regelmäßige Sicherheitsaudits</li>
        <li>Zugriffskontrolle</li>
        <li>DedSec Security Module für 24/7 Monitoring</li>
    </ul>
    
    <h2>8. Drittanbieter und Auftragsverarbeitung</h2>
    <table>
        <tr><th>Dienst</th><th>Anbieter</th><th>Zweck</th><th>Standort</th></tr>
        <tr><td>WhatsApp Business API</td><td>Meta Platforms</td><td>Messaging</td><td>USA (Standardvertragsklauseln)</td></tr>
        <tr><td>Claude AI</td><td>Anthropic</td><td>KI-Assistenz</td><td>USA (Standardvertragsklauseln)</td></tr>
        <tr><td>Hosting</td><td>Hetzner Online GmbH</td><td>Server-Infrastruktur</td><td>Deutschland</td></tr>
    </table>
    
    <h2>9. Änderungen dieser Datenschutzerklärung</h2>
    <p>Wir behalten uns vor, diese Datenschutzerklärung anzupassen, um sie an geänderte Rechtslagen oder 
    bei Änderungen des Dienstes anzupassen. Die aktuelle Version finden Sie stets auf dieser Seite.</p>
    
    <h2>10. Beschwerderecht</h2>
    <p>Sie haben das Recht, sich bei einer Aufsichtsbehörde zu beschweren. Die für uns zuständige 
    Aufsichtsbehörde ist: [Landesbeauftragter für Datenschutz einfügen]</p>
    '''
    return Response(legal_page_wrapper('Datenschutzerklärung', content), mimetype='text/html')

@app.route('/agb')
def agb():
    content = '''
    <h1>Allgemeine Geschäftsbedingungen (AGB)</h1>
    <p class="updated">Stand: Dezember 2025</p>
    
    <h2>§ 1 Geltungsbereich</h2>
    <p>(1) Diese Allgemeinen Geschäftsbedingungen gelten für alle Verträge zwischen der 
    Enterprise Universe GmbH (nachfolgend "Anbieter") und dem Kunden über die Nutzung der 
    Software-as-a-Service-Plattform "West Money OS".</p>
    <p>(2) Abweichende Bedingungen des Kunden werden nicht anerkannt, es sei denn, der Anbieter 
    stimmt ihrer Geltung ausdrücklich schriftlich zu.</p>
    
    <h2>§ 2 Vertragsgegenstand</h2>
    <p>(1) Der Anbieter stellt dem Kunden die cloudbasierte Business-Plattform "West Money OS" 
    zur Nutzung bereit. Der Funktionsumfang richtet sich nach dem gewählten Tarif:</p>
    <ul>
        <li><strong>Free:</strong> Grundfunktionen, begrenzte Kontakte</li>
        <li><strong>Professional (€99/Monat):</strong> Erweiterte Features, WhatsApp Integration</li>
        <li><strong>Enterprise (€299/Monat):</strong> Vollzugriff, API-Zugang, Priority Support</li>
    </ul>
    <p>(2) Der Anbieter schuldet die Bereitstellung der Plattform mit einer Verfügbarkeit von 99% 
    im Jahresmittel, ausgenommen geplante Wartungsarbeiten.</p>
    
    <h2>§ 3 Registrierung und Vertragsschluss</h2>
    <p>(1) Die Registrierung erfolgt über die Website. Mit Absenden der Registrierung gibt der 
    Kunde ein verbindliches Angebot ab.</p>
    <p>(2) Der Vertrag kommt mit der Freischaltung des Accounts durch den Anbieter zustande.</p>
    
    <h2>§ 4 Pflichten des Kunden</h2>
    <p>(1) Der Kunde ist verpflichtet:</p>
    <ul>
        <li>Seine Zugangsdaten geheim zu halten</li>
        <li>Die Plattform nur im Rahmen der geltenden Gesetze zu nutzen</li>
        <li>Keine rechtswidrigen Inhalte zu speichern oder zu verbreiten</li>
        <li>Bei WhatsApp-Kommunikation die erforderlichen Einwilligungen einzuholen</li>
    </ul>
    
    <h2>§ 5 Zahlungsbedingungen</h2>
    <p>(1) Die Vergütung richtet sich nach dem gewählten Tarif und ist monatlich im Voraus fällig.</p>
    <p>(2) Rechnungen werden per E-Mail zugestellt.</p>
    <p>(3) Bei Zahlungsverzug ist der Anbieter berechtigt, den Zugang zur Plattform zu sperren.</p>
    
    <h2>§ 6 Laufzeit und Kündigung</h2>
    <p>(1) Der Vertrag wird auf unbestimmte Zeit geschlossen.</p>
    <p>(2) Die Kündigung ist mit einer Frist von 30 Tagen zum Monatsende möglich.</p>
    <p>(3) Das Recht zur außerordentlichen Kündigung bleibt unberührt.</p>
    
    <h2>§ 7 Haftung</h2>
    <p>(1) Der Anbieter haftet unbeschränkt für Vorsatz und grobe Fahrlässigkeit.</p>
    <p>(2) Bei leichter Fahrlässigkeit haftet der Anbieter nur bei Verletzung wesentlicher 
    Vertragspflichten, begrenzt auf den vorhersehbaren, vertragstypischen Schaden.</p>
    <p>(3) Die Haftung für Datenverlust ist auf den typischen Wiederherstellungsaufwand begrenzt.</p>
    
    <h2>§ 8 Datenschutz</h2>
    <p>Die Verarbeitung personenbezogener Daten erfolgt gemäß unserer Datenschutzerklärung und 
    im Einklang mit der DSGVO.</p>
    
    <h2>§ 9 Änderungen der AGB</h2>
    <p>(1) Der Anbieter behält sich vor, diese AGB zu ändern.</p>
    <p>(2) Änderungen werden dem Kunden mindestens 30 Tage vor Inkrafttreten mitgeteilt.</p>
    <p>(3) Widerspricht der Kunde nicht innerhalb von 14 Tagen, gelten die Änderungen als genehmigt.</p>
    
    <h2>§ 10 Schlussbestimmungen</h2>
    <p>(1) Es gilt das Recht der Bundesrepublik Deutschland.</p>
    <p>(2) Gerichtsstand ist der Sitz des Anbieters.</p>
    <p>(3) Sollten einzelne Bestimmungen unwirksam sein, bleibt die Wirksamkeit der übrigen unberührt.</p>
    '''
    return Response(legal_page_wrapper('AGB', content), mimetype='text/html')

@app.route('/widerruf')
def widerruf():
    content = '''
    <h1>Widerrufsbelehrung</h1>
    <p class="updated">Stand: Dezember 2025</p>
    
    <h2>Widerrufsrecht</h2>
    <p>Sie haben das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen.</p>
    <p>Die Widerrufsfrist beträgt vierzehn Tage ab dem Tag des Vertragsabschlusses.</p>
    
    <p>Um Ihr Widerrufsrecht auszuüben, müssen Sie uns</p>
    <div class="highlight">
        <strong>Enterprise Universe GmbH</strong><br>
        E-Mail: widerruf@enterprise-universe.de
    </div>
    <p>mittels einer eindeutigen Erklärung (z.B. ein mit der Post versandter Brief oder E-Mail) 
    über Ihren Entschluss, diesen Vertrag zu widerrufen, informieren.</p>
    
    <h2>Folgen des Widerrufs</h2>
    <p>Wenn Sie diesen Vertrag widerrufen, haben wir Ihnen alle Zahlungen, die wir von Ihnen erhalten 
    haben, unverzüglich und spätestens binnen vierzehn Tagen ab dem Tag zurückzuzahlen, an dem die 
    Mitteilung über Ihren Widerruf dieses Vertrags bei uns eingegangen ist.</p>
    
    <h2>Besondere Hinweise</h2>
    <p>Haben Sie verlangt, dass die Dienstleistungen während der Widerrufsfrist beginnen sollen, so 
    haben Sie uns einen angemessenen Betrag zu zahlen, der dem Anteil der bis zu dem Zeitpunkt, zu 
    dem Sie uns von der Ausübung des Widerrufsrechts hinsichtlich dieses Vertrags unterrichten, 
    bereits erbrachten Dienstleistungen im Vergleich zum Gesamtumfang der im Vertrag vorgesehenen 
    Dienstleistungen entspricht.</p>
    
    <h2>Muster-Widerrufsformular</h2>
    <div class="highlight">
        <p><em>(Wenn Sie den Vertrag widerrufen wollen, dann füllen Sie bitte dieses Formular aus und senden Sie es zurück.)</em></p>
        <p>An: Enterprise Universe GmbH, E-Mail: widerruf@enterprise-universe.de</p>
        <p>Hiermit widerrufe(n) ich/wir (*) den von mir/uns (*) abgeschlossenen Vertrag über die 
        Erbringung der folgenden Dienstleistung: West Money OS</p>
        <p>Bestellt am (*)/erhalten am (*):</p>
        <p>Name des/der Verbraucher(s):</p>
        <p>Anschrift des/der Verbraucher(s):</p>
        <p>Unterschrift des/der Verbraucher(s) (nur bei Mitteilung auf Papier):</p>
        <p>Datum:</p>
        <p><small>(*) Unzutreffendes streichen.</small></p>
    </div>
    '''
    return Response(legal_page_wrapper('Widerrufsbelehrung', content), mimetype='text/html')

# =============================================================================
# COOKIE CONSENT BANNER (DSGVO)
# =============================================================================
COOKIE_BANNER_JS = '''
<script>
(function() {
    if (localStorage.getItem('cookie_consent')) return;
    
    const banner = document.createElement('div');
    banner.id = 'cookie-banner';
    banner.innerHTML = `
        <div style="position:fixed;bottom:0;left:0;right:0;background:#1a1a2e;border-top:1px solid rgba(102,126,234,0.3);padding:1.5rem;z-index:9999;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:1rem">
            <div style="flex:1;min-width:300px">
                <strong style="color:#667eea">🍪 Cookie-Einstellungen</strong>
                <p style="margin:0.5rem 0;opacity:0.8;font-size:0.9rem">Wir verwenden Cookies für die Authentifizierung und zur Verbesserung unserer Dienste. 
                <a href="/datenschutz" style="color:#667eea">Mehr erfahren</a></p>
            </div>
            <div style="display:flex;gap:0.75rem">
                <button onclick="setCookieConsent('essential')" style="padding:0.75rem 1.5rem;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.2);border-radius:10px;color:#fff;cursor:pointer">Nur notwendige</button>
                <button onclick="setCookieConsent('all')" style="padding:0.75rem 1.5rem;background:linear-gradient(135deg,#667eea,#764ba2);border:none;border-radius:10px;color:#fff;cursor:pointer;font-weight:600">Alle akzeptieren</button>
            </div>
        </div>
    `;
    document.body.appendChild(banner);
    
    window.setCookieConsent = function(type) {
        localStorage.setItem('cookie_consent', type);
        localStorage.setItem('cookie_consent_date', new Date().toISOString());
        document.getElementById('cookie-banner').remove();
    };
})();
</script>
'''

# =============================================================================
# WHATSAPP CONSENT MANAGEMENT API
# =============================================================================
@app.route('/api/contacts/whatsapp-consent/bulk', methods=['POST'])
@login_required
def api_bulk_whatsapp_consent():
    """Bulk-Update des WhatsApp-Consent-Status für mehrere Kontakte"""
    data = request.get_json()
    contact_ids = data.get('contact_ids', [])
    consent_status = data.get('consent', False)
    
    if not contact_ids:
        return jsonify({'success': False, 'error': 'Keine Kontakte ausgewählt'})
    
    updated = 0
    for cid in contact_ids:
        contact = Contact.query.get(cid)
        if contact:
            contact.whatsapp_consent = consent_status
            updated += 1
    
    db.session.commit()
    
    # Log für DSGVO-Compliance
    logger.info(f"WhatsApp consent bulk update: {updated} contacts set to {consent_status} by user {session.get('user_id')}")
    
    return jsonify({
        'success': True, 
        'updated': updated,
        'consent_status': consent_status,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/contacts/export-consent-log')
@login_required
def api_export_consent_log():
    """Export des Consent-Logs für DSGVO-Dokumentation"""
    contacts = Contact.query.filter_by(whatsapp_consent=True).all()
    
    log_data = [{
        'id': c.id,
        'name': c.name,
        'phone': c.phone,
        'whatsapp_consent': c.whatsapp_consent,
        'updated_at': c.updated_at.isoformat() if c.updated_at else None
    } for c in contacts]
    
    return jsonify({
        'success': True,
        'export_date': datetime.utcnow().isoformat(),
        'total_with_consent': len(log_data),
        'contacts': log_data
    })

@app.route('/api/user/data-export')
@login_required
def api_user_data_export():
    """DSGVO Art. 20 - Datenübertragbarkeit"""
    user = get_current_user()
    
    # Alle Nutzerdaten sammeln
    contacts = Contact.query.filter_by(user_id=user.id).all()
    leads = Lead.query.filter_by(assigned_to=user.id).all()
    messages = Message.query.filter_by(user_id=user.id).all()
    
    export = {
        'export_date': datetime.utcnow().isoformat(),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'created_at': user.created_at.isoformat() if user.created_at else None
        },
        'contacts': [c.to_dict() for c in contacts],
        'leads': [l.to_dict() for l in leads],
        'messages': [m.to_dict() for m in messages]
    }
    
    return jsonify({'success': True, 'data': export})

@app.route('/api/user/delete-account', methods=['POST'])
@login_required
def api_delete_account():
    """DSGVO Art. 17 - Recht auf Löschung"""
    user = get_current_user()
    data = request.get_json()
    
    # Passwort-Bestätigung erforderlich
    if not user.check_password(data.get('password', '')):
        return jsonify({'success': False, 'error': 'Passwort falsch'})
    
    # Alle verknüpften Daten löschen
    Contact.query.filter_by(user_id=user.id).delete()
    Lead.query.filter_by(assigned_to=user.id).delete()
    Message.query.filter_by(user_id=user.id).delete()
    ChatHistory.query.filter_by(user_id=user.id).delete()
    Task.query.filter_by(assigned_to=user.id).delete()
    TokenTransaction.query.filter_by(user_id=user.id).delete()
    Automation.query.filter_by(user_id=user.id).delete()
    
    # User löschen
    db.session.delete(user)
    db.session.commit()
    
    session.clear()
    
    logger.info(f"Account deleted: User ID {user.id}")
    
    return jsonify({'success': True, 'message': 'Konto und alle Daten wurden gelöscht'})
# =============================================================================
# API ROUTES
# =============================================================================
# Contacts API
@app.route('/api/contacts', methods=['GET', 'POST'])
@login_required
def api_contacts():
    if request.method == 'POST':
        data = request.get_json()
        tags = data.get('tags', '')
        if isinstance(tags, str):
            tags = json.dumps([t.strip() for t in tags.split(',') if t.strip()])
        contact = Contact(name=data.get('name'), email=data.get('email'), phone=data.get('phone'), company=data.get('company'), position=data.get('position'), whatsapp_consent=data.get('whatsapp_consent', False), tags=tags, notes=data.get('notes'), user_id=session.get('user_id'))
        db.session.add(contact)
        db.session.commit()
        award_tokens(session.get('user_id'), 'god', 5, 'Kontakt erstellt')
        return jsonify({'success': True, 'contact': contact.to_dict()})
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return jsonify({'success': True, 'contacts': [c.to_dict() for c in contacts]})

@app.route('/api/contacts/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_contact(id):
    contact = Contact.query.get_or_404(id)
    if request.method == 'DELETE':
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'success': True})
    if request.method == 'PUT':
        data = request.get_json()
        contact.name = data.get('name', contact.name)
        contact.email = data.get('email', contact.email)
        contact.phone = data.get('phone', contact.phone)
        contact.company = data.get('company', contact.company)
        contact.position = data.get('position', contact.position)
        contact.whatsapp_consent = data.get('whatsapp_consent', contact.whatsapp_consent)
        tags = data.get('tags', '')
        if isinstance(tags, str):
            contact.tags = json.dumps([t.strip() for t in tags.split(',') if t.strip()])
        contact.notes = data.get('notes', contact.notes)
        db.session.commit()
        return jsonify({'success': True, 'contact': contact.to_dict()})
    return jsonify({'success': True, 'contact': contact.to_dict()})

# Leads API
@app.route('/api/leads', methods=['GET', 'POST'])
@login_required
def api_leads():
    if request.method == 'POST':
        data = request.get_json()
        lead = Lead(title=data.get('title'), contact_name=data.get('contact_name'), company=data.get('company'), value=data.get('value', 0), status=data.get('status', 'new'), priority=data.get('priority', 'medium'), source=data.get('source'), notes=data.get('notes'), assigned_to=session.get('user_id'))
        db.session.add(lead)
        db.session.commit()
        return jsonify({'success': True, 'lead': lead.to_dict()})
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return jsonify({'success': True, 'leads': [l.to_dict() for l in leads]})

@app.route('/api/leads/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_lead(id):
    lead = Lead.query.get_or_404(id)
    if request.method == 'DELETE':
        db.session.delete(lead)
        db.session.commit()
        return jsonify({'success': True})
    if request.method == 'PUT':
        data = request.get_json()
        old_status = lead.status
        lead.title = data.get('title', lead.title)
        lead.contact_name = data.get('contact_name', lead.contact_name)
        lead.company = data.get('company', lead.company)
        lead.value = data.get('value', lead.value)
        lead.status = data.get('status', lead.status)
        lead.priority = data.get('priority', lead.priority)
        lead.notes = data.get('notes', lead.notes)
        db.session.commit()
        if lead.status == 'won' and old_status != 'won':
            award_tokens(session.get('user_id'), 'god', 50, f'Lead gewonnen: {lead.title}')
        return jsonify({'success': True, 'lead': lead.to_dict()})
    return jsonify({'success': True, 'lead': lead.to_dict()})

# Campaigns API
@app.route('/api/campaigns', methods=['GET', 'POST'])
@login_required
def api_campaigns():
    if request.method == 'POST':
        data = request.get_json()
        campaign = Campaign(name=data.get('name'), type=data.get('type', 'whatsapp'), template=data.get('template'), user_id=session.get('user_id'))
        db.session.add(campaign)
        db.session.commit()
        return jsonify({'success': True, 'campaign': campaign.to_dict()})
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return jsonify({'success': True, 'campaigns': [c.to_dict() for c in campaigns]})

# Invoices API
@app.route('/api/invoices', methods=['GET', 'POST'])
@login_required
def api_invoices():
    if request.method == 'POST':
        data = request.get_json()
        invoice = Invoice(invoice_number=generate_invoice_number(), contact_name=data.get('contact_name'), contact_email=data.get('contact_email'), total=data.get('total', 0), status='draft', user_id=session.get('user_id'))
        invoice.subtotal = invoice.total / 1.19
        invoice.tax_amount = invoice.total - invoice.subtotal
        db.session.add(invoice)
        db.session.commit()
        return jsonify({'success': True, 'invoice': invoice.to_dict()})
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return jsonify({'success': True, 'invoices': [i.to_dict() for i in invoices]})

# Tasks API
@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def api_tasks():
    if request.method == 'POST':
        data = request.get_json()
        task = Task(title=data.get('title'), description=data.get('description'), category=data.get('category'), assigned_bot=data.get('assigned_bot'), assigned_to=session.get('user_id'))
        db.session.add(task)
        db.session.commit()
        return jsonify({'success': True, 'task': task.to_dict()})
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify({'success': True, 'tasks': [t.to_dict() for t in tasks]})

# Automations API
@app.route('/api/automations', methods=['GET', 'POST'])
@login_required
def api_automations():
    if request.method == 'POST':
        data = request.get_json()
        automation = Automation(name=data.get('name'), trigger_type=data.get('trigger_type'), action_type=data.get('action_type'), user_id=session.get('user_id'))
        db.session.add(automation)
        db.session.commit()
        return jsonify({'success': True, 'automation': automation.to_dict()})
    automations = Automation.query.filter_by(user_id=session.get('user_id')).all()
    return jsonify({'success': True, 'automations': [a.to_dict() for a in automations]})

@app.route('/api/automations/<int:id>/toggle', methods=['POST'])
@login_required
def api_toggle_automation(id):
    automation = Automation.query.get_or_404(id)
    automation.is_active = not automation.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': automation.is_active})

# AI Chat API
@app.route('/api/ai/chat', methods=['POST'])
@login_required
def api_ai_chat():
    data = request.get_json()
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'success': False, 'error': 'Keine Nachricht'})
    user_id = session.get('user_id')
    user_msg = ChatHistory(user_id=user_id, role='user', content=message)
    db.session.add(user_msg)
    db.session.commit()
    api_key = get_env_var('ANTHROPIC_API_KEY')
    if not api_key or not api_key.startswith('sk-ant'):
        response_text = f"AI ist nicht konfiguriert. Deine Nachricht war: {message}"
    else:
        try:
            history = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.created_at.desc()).limit(20).all()
            history.reverse()
            messages = [{"role": h.role, "content": h.content} for h in history]
            res = requests.post('https://api.anthropic.com/v1/messages', headers={'x-api-key': api_key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'}, json={'model': 'claude-sonnet-4-20250514', 'max_tokens': 2000, 'system': 'Du bist ein hilfreicher KI-Assistent für West Money OS, eine Business-Plattform. Antworte auf Deutsch, präzise und freundlich.', 'messages': messages}, timeout=60)
            if res.status_code == 200:
                response_text = res.json()['content'][0]['text']
            else:
                response_text = f"API Fehler: {res.status_code}"
        except Exception as e:
            response_text = f"Fehler: {str(e)}"
    assistant_msg = ChatHistory(user_id=user_id, role='assistant', content=response_text)
    db.session.add(assistant_msg)
    db.session.commit()
    return jsonify({'success': True, 'response': response_text})

@app.route('/api/ai/clear', methods=['POST'])
@login_required
def api_ai_clear():
    ChatHistory.query.filter_by(user_id=session.get('user_id')).delete()
    db.session.commit()
    return jsonify({'success': True})

# User Profile API
@app.route('/api/user/profile', methods=['POST'])
@login_required
def api_user_profile():
    user = get_current_user()
    data = request.get_json()
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    if data.get('password'):
        user.set_password(data.get('password'))
    db.session.commit()
    return jsonify({'success': True})

# Dashboard Stats API
@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    return jsonify({
        'success': True,
        'contacts': Contact.query.count(),
        'leads': Lead.query.count(),
        'pipeline_value': db.session.query(db.func.sum(Lead.value)).scalar() or 0,
        'tasks_pending': Task.query.filter_by(status='pending').count()
    })

# Health Check
@app.route('/api/health')
def api_health():
    return jsonify({'status': 'healthy', 'version': '11.0.0-GODMODE-ULTIMATE', 'timestamp': datetime.utcnow().isoformat()})

# =============================================================================
# ERROR HANDLERS
# =============================================================================
@app.errorhandler(404)
def not_found(e):
    return redirect('/')

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Interner Serverfehler'}), 500

# =============================================================================
# INITIALIZE
# =============================================================================
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@west-money.com', name='Administrator', role='admin', plan='enterprise', tokens_god=1000, tokens_dedsec=500, tokens_og=250, tokens_tower=100)
        admin.set_password('663724')
        db.session.add(admin)
        db.session.commit()
    logger.info("✅ West Money OS v11.0 GODMODE ULTIMATE initialized")

if __name__ == '__main__':
    print("🚀 West Money OS v11.0 GODMODE ULTIMATE starting...")
    app.run(host='0.0.0.0', port=5000, debug=False)
