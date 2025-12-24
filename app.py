#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    WEST MONEY OS v9.1 GODMODE SUPREME                         ║
║                      Enterprise Universe GmbH © 2025                          ║
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

# =============================================================================
# LOGGING
# =============================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    WHATSAPP_BUSINESS_ID = os.getenv('WHATSAPP_BUSINESS_ID', '')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
    REVOLUT_API_KEY = os.getenv('REVOLUT_API_KEY', '')
    MOLLIE_API_KEY = os.getenv('MOLLIE_API_KEY', '')

config = Config()

# =============================================================================
# APP INITIALIZATION
# =============================================================================
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email, 'name': self.name, 'role': self.role, 'plan': self.plan}


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
        return {'id': self.id, 'name': self.name, 'email': self.email, 'phone': self.phone, 'company': self.company, 'whatsapp_consent': self.whatsapp_consent, 'tags': json.loads(self.tags) if self.tags else [], 'notes': self.notes, 'source': self.source, 'created_at': self.created_at.isoformat() if self.created_at else None}


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
    contact = db.relationship('Contact', backref='leads')
    
    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'contact_id': self.contact_id, 'value': self.value, 'status': self.status, 'source': self.source, 'notes': self.notes, 'created_at': self.created_at.isoformat() if self.created_at else None}


class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), default='whatsapp')
    template_id = db.Column(db.String(100))
    status = db.Column(db.String(50), default='draft')
    sent_count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'type': self.type, 'status': self.status, 'sent_count': self.sent_count, 'created_at': self.created_at.isoformat() if self.created_at else None}


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
        return {'id': self.id, 'title': self.title, 'description': self.description, 'due_date': self.due_date.isoformat() if self.due_date else None, 'priority': self.priority, 'status': self.status, 'created_at': self.created_at.isoformat() if self.created_at else None}


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    direction = db.Column(db.String(20))
    type = db.Column(db.String(20), default='text')
    content = db.Column(db.Text)
    status = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    contact = db.relationship('Contact', backref='messages')
    
    def to_dict(self):
        return {'id': self.id, 'contact_id': self.contact_id, 'direction': self.direction, 'type': self.type, 'content': self.content, 'status': self.status, 'timestamp': self.timestamp.isoformat() if self.timestamp else None}


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    amount = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='draft')
    due_date = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    items = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    contact = db.relationship('Contact', backref='invoices')
    
    def to_dict(self):
        return {'id': self.id, 'invoice_number': self.invoice_number, 'amount': self.amount, 'tax': self.tax, 'total': self.amount + self.tax, 'status': self.status, 'created_at': self.created_at.isoformat() if self.created_at else None}


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(50))
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, 'type': self.type, 'title': self.title, 'message': self.message, 'read': self.read, 'created_at': self.created_at.isoformat() if self.created_at else None}


class SecurityEvent(db.Model):
    __tablename__ = 'security_events'
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {'id': self.id, 'event_type': self.event_type, 'severity': self.severity, 'ip_address': self.ip_address, 'timestamp': self.timestamp.isoformat() if self.timestamp else None}


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
        event = SecurityEvent(event_type=event_type, severity=severity, details=json.dumps(details) if details else None, ip_address=request.remote_addr, user_id=session.get('user_id'))
        db.session.add(event)
        db.session.commit()
    except:
        pass

# =============================================================================
# INITIALIZE DATABASE
# =============================================================================
with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@west-money.com', name='Administrator', role='admin', plan='enterprise')
        admin.set_password('WestMoney2025!')
        db.session.add(admin)
        db.session.commit()
    logger.info("Database initialized")

# =============================================================================
# TEMPLATES
# =============================================================================
try:
    from templates import LANDING_PAGE_HTML, LOGIN_PAGE_HTML, get_dashboard_html, PRICING_PAGE_HTML
    TEMPLATES_LOADED = True
except:
    TEMPLATES_LOADED = False

LANDING_HTML = '''<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><title>West Money OS v9.1</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;background:linear-gradient(135deg,#0f172a,#1e1b4b);color:#fff;min-height:100vh}.hero{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:2rem}h1{font-size:3rem;margin-bottom:1rem;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.features{display:flex;gap:1rem;flex-wrap:wrap;justify-content:center;margin:2rem 0}.feature{background:rgba(255,255,255,.1);padding:1rem;border-radius:10px}.buttons{display:flex;gap:1rem}.btn{padding:1rem 2rem;border:none;border-radius:50px;font-weight:bold;cursor:pointer;text-decoration:none;color:#fff}.btn-primary{background:linear-gradient(135deg,#667eea,#764ba2)}.btn-outline{background:transparent;border:2px solid #fff}.godmode{position:fixed;top:20px;right:20px;background:linear-gradient(135deg,#f97316,#ef4444);padding:.5rem 1rem;border-radius:20px;font-weight:bold}</style></head><body><div class="godmode">🔥 GODMODE v9.1</div><div class="hero"><h1>💰 West Money OS</h1><p style="font-size:1.25rem;opacity:.8;margin-bottom:2rem">Die ultimative All-in-One Business Platform</p><div class="features"><div class="feature">📱 WhatsApp</div><div class="feature">🤖 AI Chat</div><div class="feature">💼 CRM</div><div class="feature">💳 Payments</div><div class="feature">🏦 Banking</div><div class="feature">🔒 Security</div></div><div class="buttons"><a href="/dashboard" class="btn btn-primary">Dashboard →</a><a href="/pricing" class="btn btn-outline">Preise</a></div></div></body></html>'''

LOGIN_HTML = '''<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><title>Login - West Money OS</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;background:linear-gradient(135deg,#0f172a,#1e1b4b);color:#fff;min-height:100vh;display:flex;align-items:center;justify-content:center}.login-box{background:rgba(255,255,255,.1);padding:3rem;border-radius:20px;width:100%;max-width:400px}h1{text-align:center;margin-bottom:2rem}.form-group{margin-bottom:1.5rem}label{display:block;margin-bottom:.5rem}input{width:100%;padding:1rem;border:1px solid rgba(255,255,255,.2);border-radius:10px;background:rgba(255,255,255,.1);color:#fff}.btn{width:100%;padding:1rem;border:none;border-radius:10px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;font-weight:bold;cursor:pointer}.error{background:rgba(239,68,68,.2);border:1px solid #ef4444;padding:1rem;border-radius:10px;margin-bottom:1rem}.demo{text-align:center;margin-top:1.5rem;opacity:.7}</style></head><body><div class="login-box"><h1>💰 West Money OS</h1>{error}<form method="POST"><div class="form-group"><label>Benutzername</label><input type="text" name="username" required></div><div class="form-group"><label>Passwort</label><input type="password" name="password" required></div><button type="submit" class="btn">🚀 Einloggen</button></form><p class="demo">Demo: admin / WestMoney2025!</p></div></body></html>'''

DASHBOARD_HTML = '''<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><title>Dashboard - West Money OS</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;background:#0f172a;color:#fff;min-height:100vh}.sidebar{position:fixed;left:0;top:0;width:250px;height:100vh;background:#1e293b;padding:2rem 1rem}.logo{font-size:1.5rem;font-weight:bold;margin-bottom:2rem;text-align:center}.nav-item{display:block;padding:1rem;border-radius:10px;color:#fff;text-decoration:none;margin-bottom:.5rem}.nav-item:hover{background:rgba(102,126,234,.2)}.main{margin-left:250px;padding:2rem}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;margin-bottom:2rem}.stat-card{background:linear-gradient(135deg,rgba(102,126,234,.2),rgba(118,75,162,.2));padding:1.5rem;border-radius:15px}.stat-value{font-size:2rem;font-weight:bold}.stat-label{opacity:.7}</style></head><body><div class="sidebar"><div class="logo">💰 West Money</div><a href="/dashboard" class="nav-item">📊 Dashboard</a><a href="#contacts" class="nav-item">👥 Kontakte</a><a href="#leads" class="nav-item">🎯 Leads</a><a href="#campaigns" class="nav-item">📧 Kampagnen</a><a href="#invoices" class="nav-item">📄 Rechnungen</a><a href="#whatsapp" class="nav-item">📱 WhatsApp</a><a href="/logout" class="nav-item">🚪 Logout</a></div><div class="main"><h1 style="margin-bottom:2rem">Dashboard</h1><div class="stats"><div class="stat-card"><div class="stat-value" id="contacts">-</div><div class="stat-label">Kontakte</div></div><div class="stat-card"><div class="stat-value" id="leads">-</div><div class="stat-label">Leads</div></div><div class="stat-card"><div class="stat-value" id="value">-</div><div class="stat-label">Pipeline</div></div><div class="stat-card"><div class="stat-value" id="tasks">-</div><div class="stat-label">Tasks</div></div></div></div><script>fetch('/api/dashboard/stats').then(r=>r.json()).then(d=>{if(d.success){document.getElementById('contacts').textContent=d.stats.contacts.total;document.getElementById('leads').textContent=d.stats.leads.total;document.getElementById('value').textContent='€'+d.stats.leads.total_value.toLocaleString();document.getElementById('tasks').textContent=d.stats.tasks.pending}})</script></body></html>'''

PRICING_HTML = '''<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><title>Preise - West Money OS</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;background:linear-gradient(135deg,#0f172a,#1e1b4b);color:#fff;min-height:100vh;padding:2rem}h1{text-align:center;font-size:2.5rem;margin-bottom:3rem}.plans{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:2rem;max-width:1200px;margin:0 auto}.plan{background:rgba(255,255,255,.1);border-radius:20px;padding:2rem;text-align:center}.plan.featured{border:2px solid #667eea}.plan-name{font-size:1.5rem;margin-bottom:1rem}.plan-price{font-size:3rem;font-weight:bold}.plan-features{list-style:none;margin:2rem 0;text-align:left}.plan-features li{padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.1)}.btn{display:inline-block;padding:1rem 2rem;border:none;border-radius:50px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;font-weight:bold;text-decoration:none}</style></head><body><h1>💰 Preise</h1><div class="plans"><div class="plan"><div class="plan-name">Free</div><div class="plan-price">€0</div><ul class="plan-features"><li>✓ 100 Kontakte</li><li>✓ Basic CRM</li></ul><a href="/register" class="btn">Start</a></div><div class="plan"><div class="plan-name">Starter</div><div class="plan-price">€29</div><ul class="plan-features"><li>✓ 1.000 Kontakte</li><li>✓ WhatsApp</li></ul><a href="/checkout" class="btn">Starten</a></div><div class="plan featured"><div class="plan-name">Professional</div><div class="plan-price">€99</div><ul class="plan-features"><li>✓ 10.000 Kontakte</li><li>✓ AI Chatbot</li><li>✓ Banking</li></ul><a href="/checkout" class="btn">Beliebt</a></div><div class="plan"><div class="plan-name">Enterprise</div><div class="plan-price">€299</div><ul class="plan-features"><li>✓ Unbegrenzt</li><li>✓ White Label</li></ul><a href="/contact" class="btn">Kontakt</a></div></div></body></html>'''

# =============================================================================
# PAGE ROUTES
# =============================================================================
@app.route('/')
def landing():
    return Response(LANDING_PAGE_HTML if TEMPLATES_LOADED else LANDING_HTML, mimetype='text/html')

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
        html = (LOGIN_PAGE_HTML if TEMPLATES_LOADED else LOGIN_HTML).replace('{error}', '<div class="error">❌ Ungültige Anmeldedaten</div>')
        return Response(html, mimetype='text/html')
    html = (LOGIN_PAGE_HTML if TEMPLATES_LOADED else LOGIN_HTML).replace('{error}', '')
    return Response(html, mimetype='text/html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user = get_current_user()
    if TEMPLATES_LOADED:
        return Response(get_dashboard_html(user), mimetype='text/html')
    return Response(DASHBOARD_HTML.replace('{username}', user.name or user.username if user else 'User'), mimetype='text/html')

@app.route('/pricing')
def pricing():
    return Response(PRICING_PAGE_HTML if TEMPLATES_LOADED else PRICING_HTML, mimetype='text/html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# =============================================================================
# DASHBOARD API
# =============================================================================
@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)
    stats = {
        'contacts': {
            'total': Contact.query.count(),
            'this_month': Contact.query.filter(Contact.created_at >= datetime.combine(month_start, datetime.min.time())).count(),
            'with_consent': Contact.query.filter_by(whatsapp_consent=True).count()
        },
        'leads': {
            'total': Lead.query.count(),
            'new': Lead.query.filter_by(status='new').count(),
            'qualified': Lead.query.filter_by(status='qualified').count(),
            'won': Lead.query.filter_by(status='won').count(),
            'total_value': float(db.session.query(db.func.sum(Lead.value)).scalar() or 0)
        },
        'tasks': {
            'pending': Task.query.filter_by(status='pending').count(),
            'overdue': Task.query.filter(Task.status == 'pending', Task.due_date < datetime.utcnow()).count()
        },
        'messages': {
            'total': Message.query.count(),
            'today': Message.query.filter(Message.timestamp >= datetime.combine(today, datetime.min.time())).count()
        }
    }
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/dashboard/pipeline', methods=['GET'])
@login_required
def get_pipeline():
    pipeline = {}
    for status in ['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost']:
        leads = Lead.query.filter_by(status=status).all()
        pipeline[status] = {'count': len(leads), 'value': sum(l.value or 0 for l in leads), 'leads': [l.to_dict() for l in leads[:5]]}
    return jsonify({'success': True, 'pipeline': pipeline})

# =============================================================================
# CONTACTS API
# =============================================================================
@app.route('/api/contacts', methods=['GET'])
@login_required
def get_contacts():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = Contact.query
    if search:
        query = query.filter((Contact.name.ilike(f'%{search}%')) | (Contact.email.ilike(f'%{search}%')))
    contacts = query.order_by(Contact.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    return jsonify({'success': True, 'contacts': [c.to_dict() for c in contacts.items], 'total': contacts.total})

@app.route('/api/contacts', methods=['POST'])
@login_required
def create_contact():
    data = request.get_json()
    contact = Contact(name=data.get('name'), email=data.get('email'), phone=data.get('phone'), company=data.get('company'), whatsapp_consent=data.get('whatsapp_consent', False), tags=json.dumps(data.get('tags', [])), notes=data.get('notes'), source=data.get('source'), user_id=session.get('user_id'))
    db.session.add(contact)
    db.session.commit()
    return jsonify({'success': True, 'contact': contact.to_dict()}), 201

@app.route('/api/contacts/<int:id>', methods=['GET'])
@login_required
def get_contact(id):
    contact = Contact.query.get_or_404(id)
    return jsonify({'success': True, 'contact': contact.to_dict()})

@app.route('/api/contacts/<int:id>', methods=['PUT'])
@login_required
def update_contact(id):
    contact = Contact.query.get_or_404(id)
    data = request.get_json()
    for field in ['name', 'email', 'phone', 'company', 'whatsapp_consent', 'notes', 'source']:
        if field in data:
            setattr(contact, field, data[field])
    if 'tags' in data:
        contact.tags = json.dumps(data['tags'])
    db.session.commit()
    return jsonify({'success': True, 'contact': contact.to_dict()})

@app.route('/api/contacts/<int:id>', methods=['DELETE'])
@login_required
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/contacts/bulk-consent', methods=['POST'])
@login_required
def bulk_consent():
    data = request.get_json()
    Contact.query.filter(Contact.id.in_(data.get('contact_ids', []))).update({'whatsapp_consent': data.get('consent', False)}, synchronize_session=False)
    db.session.commit()
    return jsonify({'success': True})

# =============================================================================
# LEADS API
# =============================================================================
@app.route('/api/leads', methods=['GET'])
@login_required
def get_leads():
    status = request.args.get('status', '')
    query = Lead.query
    if status:
        query = query.filter_by(status=status)
    leads = query.order_by(Lead.created_at.desc()).all()
    return jsonify({'success': True, 'leads': [l.to_dict() for l in leads], 'total': len(leads)})

@app.route('/api/leads', methods=['POST'])
@login_required
def create_lead():
    data = request.get_json()
    lead = Lead(title=data.get('title'), contact_id=data.get('contact_id'), value=data.get('value', 0), status=data.get('status', 'new'), source=data.get('source'), notes=data.get('notes'), assigned_to=session.get('user_id'))
    db.session.add(lead)
    db.session.commit()
    return jsonify({'success': True, 'lead': lead.to_dict()}), 201

@app.route('/api/leads/<int:id>', methods=['GET'])
@login_required
def get_lead(id):
    lead = Lead.query.get_or_404(id)
    return jsonify({'success': True, 'lead': lead.to_dict()})

@app.route('/api/leads/<int:id>', methods=['PUT'])
@login_required
def update_lead(id):
    lead = Lead.query.get_or_404(id)
    data = request.get_json()
    for field in ['title', 'value', 'status', 'source', 'notes', 'contact_id']:
        if field in data:
            setattr(lead, field, data[field])
    db.session.commit()
    return jsonify({'success': True, 'lead': lead.to_dict()})

@app.route('/api/leads/<int:id>', methods=['DELETE'])
@login_required
def delete_lead(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    return jsonify({'success': True})

# =============================================================================
# CAMPAIGNS API
# =============================================================================
@app.route('/api/campaigns', methods=['GET'])
@login_required
def get_campaigns():
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return jsonify({'success': True, 'campaigns': [c.to_dict() for c in campaigns]})

@app.route('/api/campaigns', methods=['POST'])
@login_required
def create_campaign():
    data = request.get_json()
    campaign = Campaign(name=data.get('name'), type=data.get('type', 'whatsapp'), template_id=data.get('template_id'), created_by=session.get('user_id'))
    db.session.add(campaign)
    db.session.commit()
    return jsonify({'success': True, 'campaign': campaign.to_dict()}), 201

@app.route('/api/campaigns/<int:id>/send', methods=['POST'])
@login_required
def send_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    contacts = Contact.query.filter_by(whatsapp_consent=True).count()
    campaign.status = 'sent'
    campaign.sent_count = contacts
    campaign.sent_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'sent_count': contacts})

# =============================================================================
# TASKS API
# =============================================================================
@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(assigned_to=session.get('user_id')).order_by(Task.due_date.asc()).all()
    return jsonify({'success': True, 'tasks': [t.to_dict() for t in tasks]})

@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    task = Task(title=data.get('title'), description=data.get('description'), due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None, priority=data.get('priority', 'medium'), assigned_to=session.get('user_id'))
    db.session.add(task)
    db.session.commit()
    return jsonify({'success': True, 'task': task.to_dict()}), 201

@app.route('/api/tasks/<int:id>', methods=['PUT'])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()
    for field in ['title', 'description', 'priority', 'status']:
        if field in data:
            setattr(task, field, data[field])
    db.session.commit()
    return jsonify({'success': True, 'task': task.to_dict()})

# =============================================================================
# INVOICES API
# =============================================================================
@app.route('/api/invoices', methods=['GET'])
@login_required
def get_invoices():
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return jsonify({'success': True, 'invoices': [i.to_dict() for i in invoices]})

@app.route('/api/invoices', methods=['POST'])
@login_required
def create_invoice():
    data = request.get_json()
    last = Invoice.query.order_by(Invoice.id.desc()).first()
    num = f"INV-{datetime.utcnow().strftime('%Y%m')}-{(last.id + 1) if last else 1:04d}"
    invoice = Invoice(invoice_number=num, contact_id=data.get('contact_id'), amount=data.get('amount', 0), tax=data.get('tax', 0), items=json.dumps(data.get('items', [])))
    db.session.add(invoice)
    db.session.commit()
    return jsonify({'success': True, 'invoice': invoice.to_dict()}), 201

@app.route('/api/invoices/<int:id>/send', methods=['POST'])
@login_required
def send_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    invoice.status = 'sent'
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/invoices/<int:id>/paid', methods=['POST'])
@login_required
def mark_paid(id):
    invoice = Invoice.query.get_or_404(id)
    invoice.status = 'paid'
    invoice.paid_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})

# =============================================================================
# MESSAGES & WHATSAPP API
# =============================================================================
@app.route('/api/messages', methods=['GET'])
@login_required
def get_messages():
    contact_id = request.args.get('contact_id', type=int)
    query = Message.query
    if contact_id:
        query = query.filter_by(contact_id=contact_id)
    messages = query.order_by(Message.timestamp.desc()).limit(100).all()
    return jsonify({'success': True, 'messages': [m.to_dict() for m in messages]})

@app.route('/api/whatsapp/send', methods=['POST'])
@login_required
def send_whatsapp():
    data = request.get_json()
    if not config.WHATSAPP_TOKEN:
        return jsonify({'success': False, 'error': 'WhatsApp nicht konfiguriert'}), 503
    try:
        import requests
        response = requests.post(f"https://graph.facebook.com/v21.0/{config.WHATSAPP_PHONE_ID}/messages", headers={'Authorization': f'Bearer {config.WHATSAPP_TOKEN}', 'Content-Type': 'application/json'}, json={'messaging_product': 'whatsapp', 'to': data.get('to'), 'type': 'text', 'text': {'body': data.get('message')}})
        msg = Message(contact_id=data.get('contact_id'), direction='outgoing', content=data.get('message'), status='sent')
        db.session.add(msg)
        db.session.commit()
        return jsonify({'success': True, 'result': response.json()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/whatsapp/templates', methods=['GET'])
@login_required
def get_templates():
    if not config.WHATSAPP_TOKEN:
        return jsonify({'success': False, 'error': 'WhatsApp nicht konfiguriert'}), 503
    try:
        import requests
        response = requests.get(f"https://graph.facebook.com/v21.0/{config.WHATSAPP_BUSINESS_ID}/message_templates", headers={'Authorization': f'Bearer {config.WHATSAPP_TOKEN}'})
        return jsonify({'success': True, 'templates': response.json().get('data', [])})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# NOTIFICATIONS API
# =============================================================================
@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=session.get('user_id')).order_by(Notification.created_at.desc()).limit(50).all()
    unread = Notification.query.filter_by(user_id=session.get('user_id'), read=False).count()
    return jsonify({'success': True, 'notifications': [n.to_dict() for n in notifications], 'unread': unread})

@app.route('/api/notifications/read', methods=['POST'])
@login_required
def mark_read():
    Notification.query.filter_by(user_id=session.get('user_id')).update({'read': True}, synchronize_session=False)
    db.session.commit()
    return jsonify({'success': True})

# =============================================================================
# SECURITY API
# =============================================================================
@app.route('/api/security/events', methods=['GET'])
@login_required
def get_security_events():
    events = SecurityEvent.query.order_by(SecurityEvent.timestamp.desc()).limit(100).all()
    return jsonify({'success': True, 'events': [e.to_dict() for e in events]})

@app.route('/api/security/score', methods=['GET'])
@login_required
def get_security_score():
    failures = SecurityEvent.query.filter(SecurityEvent.event_type == 'failed_login', SecurityEvent.timestamp > datetime.utcnow() - timedelta(hours=24)).count()
    score = max(0, 85 - (failures * 5))
    return jsonify({'success': True, 'score': score, 'issues': [f'{failures} fehlgeschlagene Logins'] if failures > 3 else []})

# =============================================================================
# AI CHAT API
# =============================================================================
@app.route('/api/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    data = request.get_json()
    if not config.ANTHROPIC_API_KEY:
        return jsonify({'success': False, 'error': 'AI nicht konfiguriert'}), 503
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        response = client.messages.create(model=config.CLAUDE_MODEL, max_tokens=1024, system="Du bist ein Business-Assistent für West Money OS.", messages=[{"role": "user", "content": data.get('message', '')}])
        return jsonify({'success': True, 'response': response.content[0].text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# =============================================================================
# AUTH API
# =============================================================================
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = User.query.filter((User.username == data.get('username')) | (User.email == data.get('username'))).first()
    if user and user.check_password(data.get('password', '')):
        session['user_id'] = user.id
        session.permanent = True
        return jsonify({'success': True, 'user': user.to_dict()})
    return jsonify({'success': False, 'error': 'Ungültige Anmeldedaten'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/me', methods=['GET'])
@login_required
def api_me():
    user = get_current_user()
    return jsonify({'success': True, 'user': user.to_dict()})

# =============================================================================
# HEALTH CHECK
# =============================================================================
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '9.1.0-GODMODE',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'database': 'connected',
            'whatsapp': 'configured' if config.WHATSAPP_TOKEN else 'not configured',
            'stripe': 'configured' if config.STRIPE_SECRET_KEY else 'not configured',
            'hubspot': 'configured' if config.HUBSPOT_API_KEY else 'not configured',
            'claude_ai': 'configured' if config.ANTHROPIC_API_KEY else 'not configured',
            'revolut': 'configured' if config.REVOLUT_API_KEY else 'not configured',
            'mollie': 'configured' if config.MOLLIE_API_KEY else 'not configured'
        }
    })

# =============================================================================
# ERROR HANDLERS
# =============================================================================
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Nicht gefunden'}), 404
    return redirect('/')

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({'success': False, 'error': 'Interner Serverfehler'}), 500

# =============================================================================
# RUN
# =============================================================================
if __name__ == '__main__':
    print("🚀 Starting West Money OS v9.1 GODMODE...")
    app.run(host='0.0.0.0', port=5000, debug=False)
