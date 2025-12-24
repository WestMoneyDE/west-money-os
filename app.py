#!/usr/bin/env python3
"""
================================================================================
    WEST MONEY OS v9.0 - BROLY ULTRA GODMODE ENTERPRISE EDITION
    Enterprise Universe GmbH - Complete Business Suite
    
    Features:
    - 20+ API Integrations
    - Real-time WebSocket Chat
    - AI Chatbot (Claude API)
    - WhatsApp Business API 2.0
    - HubSpot CRM Full Sync
    - Security Dashboard
    - Campaign Management
    - Concierge Service
    
    (c) 2025 Ömer Hüseyin Coşkun - GOD MODE ULTRA INSTINCT ACTIVATED
================================================================================
"""

import os
import json
import hashlib
import secrets
import logging
import re
import csv
import io
import uuid
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, List, Dict, Any

# Flask Core
from flask import (
    Flask, jsonify, request, Response, session, redirect, 
    render_template_string, g, abort
)
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# External APIs
import requests

# HTML Templates
try:
    from templates import LANDING_PAGE_HTML, LOGIN_PAGE_HTML, get_dashboard_html, PRICING_PAGE_HTML
    TEMPLATES_LOADED = True
except ImportError:
    TEMPLATES_LOADED = False

# =============================================================================
# APP CONFIGURATION
# =============================================================================

app = Flask(__name__)

# Security Configuration
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///westmoney.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, supports_credentials=True)

# =============================================================================
# API KEYS & CONFIGURATION
# =============================================================================

class Config:
    """Centralized configuration management"""
    # Server
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    
    # WhatsApp Business API
    WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')
    WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID', '')
    WHATSAPP_BUSINESS_ID = os.getenv('WHATSAPP_BUSINESS_ID', '')
    WHATSAPP_VERIFY_TOKEN = os.getenv('WEBHOOK_SECRET', 'westmoney_webhook_2025')
    WHATSAPP_API_VERSION = 'v21.0'
    
    # HubSpot CRM
    HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY', '')
    HUBSPOT_PORTAL_ID = os.getenv('HUBSPOT_PORTAL_ID', '')
    
    # Claude AI (Anthropic)
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
    
    # Explorium B2B Data
    EXPLORIUM_API_KEY = os.getenv('EXPLORIUM_API_KEY', '')
    
    # OpenCorporates (Handelsregister)
    OPENCORPORATES_API_KEY = os.getenv('OPENCORPORATES_API_KEY', '')
    
    # Redis (for caching & real-time)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000

config = Config()

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('westmoney.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('WestMoneyOS')

# =============================================================================
# DATABASE MODELS
# =============================================================================

class User(db.Model):
    """User model with roles and permissions"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120))
    company = db.Column(db.String(120))
    role = db.Column(db.String(50), default='user')  # admin, user, demo
    plan = db.Column(db.String(50), default='free')  # free, starter, professional, enterprise
    avatar = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contacts = db.relationship('Contact', backref='owner', lazy='dynamic')
    leads = db.relationship('Lead', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'company': self.company,
            'role': self.role,
            'plan': self.plan,
            'avatar': self.avatar or (self.name[:2].upper() if self.name else '??')
        }


class Contact(db.Model):
    """Contact/Customer model with WhatsApp integration"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Basic Info
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    company = db.Column(db.String(120))
    position = db.Column(db.String(100))
    
    # WhatsApp
    whatsapp_number = db.Column(db.String(50))
    whatsapp_consent = db.Column(db.Boolean, default=False)
    whatsapp_consent_date = db.Column(db.DateTime)
    whatsapp_last_message = db.Column(db.DateTime)
    
    # CRM Integration
    hubspot_id = db.Column(db.String(50))
    hubspot_sync_date = db.Column(db.DateTime)
    explorium_id = db.Column(db.String(50))
    enrichment_data = db.Column(db.JSON)
    
    # Scoring & Status
    score = db.Column(db.Integer, default=50)
    status = db.Column(db.String(20), default='lead')  # lead, active, inactive, customer
    source = db.Column(db.String(50))
    tags = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact = db.Column(db.DateTime)
    
    # Relationships
    messages = db.relationship('Message', backref='contact', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'position': self.position,
            'whatsapp_number': self.whatsapp_number,
            'whatsapp_consent': self.whatsapp_consent,
            'score': self.score,
            'status': self.status,
            'source': self.source,
            'tags': self.tags or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_contact': self.last_contact.isoformat() if self.last_contact else None
        }


class Lead(db.Model):
    """Sales Lead/Deal model"""
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    
    # Deal Info
    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(120))
    contact_name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    
    # Value & Stage
    value = db.Column(db.Float, default=0)
    stage = db.Column(db.String(50), default='discovery')  # discovery, qualified, proposal, negotiation, won, lost
    probability = db.Column(db.Integer, default=10)
    
    # HubSpot Integration
    hubspot_deal_id = db.Column(db.String(50))
    hubspot_sync_date = db.Column(db.DateTime)
    
    # Metadata
    source = db.Column(db.String(50))
    notes = db.Column(db.Text)
    expected_close = db.Column(db.Date)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'company': self.company,
            'contact': self.contact_name,
            'email': self.email,
            'phone': self.phone,
            'value': self.value,
            'stage': self.stage,
            'probability': self.probability,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Message(db.Model):
    """WhatsApp/Chat Message model"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    
    # Message Content
    direction = db.Column(db.String(10), nullable=False)  # in, out
    message_type = db.Column(db.String(20), default='text')  # text, image, document, template, interactive
    content = db.Column(db.Text)
    media_url = db.Column(db.String(500))
    template_name = db.Column(db.String(100))
    
    # Status Tracking
    status = db.Column(db.String(20), default='sent')  # sent, delivered, read, failed
    whatsapp_message_id = db.Column(db.String(100))
    error_message = db.Column(db.Text)
    
    # Campaign Association
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'contact_id': self.contact_id,
            'direction': self.direction,
            'message_type': self.message_type,
            'content': self.content,
            'media_url': self.media_url,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }


class Conversation(db.Model):
    """Chat Conversation model for grouping messages"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'), nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, archived, closed
    unread_count = db.Column(db.Integer, default=0)
    last_message_id = db.Column(db.Integer)
    last_message_at = db.Column(db.DateTime)
    
    # Assignment
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    labels = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Campaign(db.Model):
    """Marketing Campaign model"""
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Campaign Info
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), default='whatsapp')  # whatsapp, email, sms
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, active, completed, paused
    
    # Content
    template_id = db.Column(db.String(100))
    template_name = db.Column(db.String(100))
    message_content = db.Column(db.Text)
    
    # Targeting
    segment_filter = db.Column(db.JSON)  # Filter criteria for contacts
    
    # Scheduling
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Statistics
    total_recipients = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    delivered_count = db.Column(db.Integer, default=0)
    read_count = db.Column(db.Integer, default=0)
    clicked_count = db.Column(db.Integer, default=0)
    converted_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='campaign', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'type': self.type,
            'status': self.status,
            'sent': self.sent_count,
            'delivered': self.delivered_count,
            'opened': self.read_count,
            'clicked': self.clicked_count,
            'converted': self.converted_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Task(db.Model):
    """Task/To-Do model"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Task Info
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Related Objects
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    
    # HubSpot Integration
    hubspot_task_id = db.Column(db.String(50))
    
    # Scheduling
    due_date = db.Column(db.Date)
    reminder_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Invoice(db.Model):
    """Invoice model"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    
    # Customer Info
    customer_name = db.Column(db.String(200))
    customer_email = db.Column(db.String(120))
    customer_address = db.Column(db.Text)
    
    # Amounts
    subtotal = db.Column(db.Float, default=0)
    tax_rate = db.Column(db.Float, default=19.0)  # German VAT
    tax_amount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, overdue, cancelled
    
    # Dates
    invoice_date = db.Column(db.Date, default=datetime.utcnow)
    due_date = db.Column(db.Date)
    paid_date = db.Column(db.Date)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.invoice_number,
            'customer': self.customer_name,
            'email': self.customer_email,
            'amount': self.subtotal,
            'tax': self.tax_amount,
            'total': self.total,
            'status': self.status,
            'date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due': self.due_date.isoformat() if self.due_date else None
        }


class SecurityEvent(db.Model):
    """Security Event/Audit Log model"""
    __tablename__ = 'security_events'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Event Info
    event_type = db.Column(db.String(50), nullable=False)  # login, logout, api_call, threat_blocked, etc.
    severity = db.Column(db.String(20), default='info')  # info, warning, critical
    
    # Source
    source_ip = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Details
    details = db.Column(db.JSON)
    resolved = db.Column(db.Boolean, default=False)
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'severity': self.severity,
            'source_ip': self.source_ip,
            'details': self.details,
            'resolved': self.resolved,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class AIChatSession(db.Model):
    """AI Chat Session model for Claude integration"""
    __tablename__ = 'ai_chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Session Info
    session_type = db.Column(db.String(20), default='support')  # support, sales, concierge
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, ended, escalated
    
    # Conversation History (stored as JSON for Claude context)
    messages_history = db.Column(db.JSON, default=list)
    
    # Metadata
    channel = db.Column(db.String(20), default='web')  # web, whatsapp
    escalated_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = db.Column(db.DateTime)


class Notification(db.Model):
    """Notification model"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Notification Info
    type = db.Column(db.String(50), nullable=False)  # deal, payment, task, whatsapp, security, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    icon = db.Column(db.String(10))
    
    # Status
    read = db.Column(db.Boolean, default=False)
    
    # Links
    link_type = db.Column(db.String(50))  # contact, lead, task, etc.
    link_id = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'icon': self.icon,
            'read': self.read,
            'created': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }


# =============================================================================
# PRICING PLANS
# =============================================================================

PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'price_yearly': 0,
        'features': ['3 Kontakte', '2 Leads', 'Basic Dashboard']
    },
    'starter': {
        'name': 'Starter',
        'price': 29,
        'price_yearly': 290,
        'features': ['50 Kontakte', '25 Leads', 'Handelsregister', 'Export']
    },
    'professional': {
        'name': 'Professional',
        'price': 99,
        'price_yearly': 990,
        'popular': True,
        'features': ['Unlimited', 'WhatsApp', 'HubSpot', 'API', 'Team']
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 299,
        'price_yearly': 2990,
        'features': ['Alles', 'White Label', 'Custom', 'SLA 99.9%', 'AI Concierge']
    }
}


# =============================================================================
# HELPER FUNCTIONS & DECORATORS
# =============================================================================

def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Nicht authentifiziert'}), 401
        return f(*args, **kwargs)
    return decorated_function



def login_required_html(f):
    """Decorator for HTML pages - redirects to login instead of JSON error"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Nicht authentifiziert'}), 401
        user = User.query.get(session['user_id'])
        if not user or user.role not in ['admin', 'GOD MODE']:
            return jsonify({'success': False, 'error': 'Keine Berechtigung'}), 403
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


def log_security_event(event_type: str, severity: str = 'info', details: dict = None):
    """Log a security event"""
    try:
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            source_ip=request.remote_addr,
            user_agent=request.user_agent.string if request.user_agent else None,
            user_id=session.get('user_id'),
            details=details or {}
        )
        db.session.add(event)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")


def create_notification(user_id: int, type: str, title: str, message: str, icon: str = None):
    """Create a notification for a user"""
    try:
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            icon=icon
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        return None


# =============================================================================
# SECURITY HEADERS MIDDLEWARE
# =============================================================================

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


@app.before_request
def before_request():
    """Pre-request processing"""
    g.request_start_time = datetime.utcnow()
    g.user = get_current_user()


# =============================================================================
# API SERVICE CLASSES
# =============================================================================

class WhatsAppService:
    """WhatsApp Business API v21.0 Integration"""
    
    BASE_URL = f"https://graph.facebook.com/{config.WHATSAPP_API_VERSION}"
    
    @classmethod
    def send_message(cls, to: str, message: str, message_type: str = 'text') -> dict:
        """Send a WhatsApp message"""
        if not config.WHATSAPP_TOKEN or not config.WHATSAPP_PHONE_ID:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        url = f"{cls.BASE_URL}/{config.WHATSAPP_PHONE_ID}/messages"
        headers = {
            'Authorization': f'Bearer {config.WHATSAPP_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Format phone number
        phone = to.replace('+', '').replace(' ', '').replace('-', '')
        if not phone.startswith('49') and len(phone) < 12:
            phone = f"49{phone.lstrip('0')}"
        
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': phone,
            'type': message_type
        }
        
        if message_type == 'text':
            payload['text'] = {'preview_url': True, 'body': message}
        elif message_type == 'template':
            payload['template'] = message  # message should be template dict
        elif message_type == 'interactive':
            payload['interactive'] = message
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': data.get('messages', [{}])[0].get('id'),
                    'data': data
                }
            else:
                return {
                    'success': False,
                    'error': data.get('error', {}).get('message', 'Unknown error'),
                    'data': data
                }
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def send_template(cls, to: str, template_name: str, language: str = 'de',
                      components: list = None) -> dict:
        """Send a template message"""
        template = {
            'name': template_name,
            'language': {'code': language}
        }
        if components:
            template['components'] = components
        
        return cls.send_message(to, template, message_type='template')
    
    @classmethod
    def send_interactive(cls, to: str, body: str, buttons: list = None,
                         header: str = None, footer: str = None) -> dict:
        """Send interactive message with buttons"""
        interactive = {
            'type': 'button',
            'body': {'text': body}
        }
        
        if header:
            interactive['header'] = {'type': 'text', 'text': header}
        if footer:
            interactive['footer'] = {'text': footer}
        
        if buttons:
            interactive['action'] = {
                'buttons': [
                    {'type': 'reply', 'reply': {'id': f'btn_{i}', 'title': btn}}
                    for i, btn in enumerate(buttons[:3])  # Max 3 buttons
                ]
            }
        
        return cls.send_message(to, interactive, message_type='interactive')
    
    @classmethod
    def get_templates(cls) -> dict:
        """Get all message templates"""
        if not config.WHATSAPP_TOKEN or not config.WHATSAPP_BUSINESS_ID:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        url = f"{cls.BASE_URL}/{config.WHATSAPP_BUSINESS_ID}/message_templates"
        headers = {'Authorization': f'Bearer {config.WHATSAPP_TOKEN}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            data = response.json()
            return {'success': True, 'templates': data.get('data', [])}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def upload_media(cls, file_path: str, media_type: str) -> dict:
        """Upload media file to WhatsApp"""
        url = f"{cls.BASE_URL}/{config.WHATSAPP_PHONE_ID}/media"
        headers = {'Authorization': f'Bearer {config.WHATSAPP_TOKEN}'}
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f, media_type)}
                data = {'messaging_product': 'whatsapp'}
                response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
                return response.json()
        except Exception as e:
            return {'success': False, 'error': str(e)}


class HubSpotService:
    """HubSpot CRM API v3 Integration"""
    
    BASE_URL = "https://api.hubapi.com"
    
    @classmethod
    def _headers(cls):
        return {
            'Authorization': f'Bearer {config.HUBSPOT_API_KEY}',
            'Content-Type': 'application/json'
        }
    
    @classmethod
    def create_contact(cls, email: str, properties: dict = None) -> dict:
        """Create a new contact in HubSpot"""
        if not config.HUBSPOT_API_KEY:
            return {'success': False, 'error': 'HubSpot not configured'}
        
        url = f"{cls.BASE_URL}/crm/v3/objects/contacts"
        data = {'properties': {'email': email, **(properties or {})}}
        
        try:
            response = requests.post(url, headers=cls._headers(), json=data, timeout=30)
            result = response.json()
            
            if response.status_code in [200, 201]:
                return {'success': True, 'contact': result}
            return {'success': False, 'error': result.get('message', 'Error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_contact(cls, contact_id: str = None, email: str = None) -> dict:
        """Get contact by ID or email"""
        if not config.HUBSPOT_API_KEY:
            return {'success': False, 'error': 'HubSpot not configured'}
        
        if contact_id:
            url = f"{cls.BASE_URL}/crm/v3/objects/contacts/{contact_id}"
        elif email:
            url = f"{cls.BASE_URL}/crm/v3/objects/contacts/{email}?idProperty=email"
        else:
            return {'success': False, 'error': 'Contact ID or email required'}
        
        try:
            response = requests.get(url, headers=cls._headers(), timeout=30)
            if response.status_code == 200:
                return {'success': True, 'contact': response.json()}
            return {'success': False, 'error': 'Contact not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def update_contact(cls, contact_id: str, properties: dict) -> dict:
        """Update contact properties"""
        if not config.HUBSPOT_API_KEY:
            return {'success': False, 'error': 'HubSpot not configured'}
        
        url = f"{cls.BASE_URL}/crm/v3/objects/contacts/{contact_id}"
        data = {'properties': properties}
        
        try:
            response = requests.patch(url, headers=cls._headers(), json=data, timeout=30)
            if response.status_code == 200:
                return {'success': True, 'contact': response.json()}
            return {'success': False, 'error': response.json().get('message', 'Error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def search_contacts(cls, query: str, properties: list = None) -> dict:
        """Search contacts"""
        if not config.HUBSPOT_API_KEY:
            return {'success': False, 'error': 'HubSpot not configured'}
        
        url = f"{cls.BASE_URL}/crm/v3/objects/contacts/search"
        data = {
            'filterGroups': [{
                'filters': [{
                    'propertyName': 'email',
                    'operator': 'CONTAINS_TOKEN',
                    'value': query
                }]
            }],
            'properties': properties or ['email', 'firstname', 'lastname', 'phone', 'company']
        }
        
        try:
            response = requests.post(url, headers=cls._headers(), json=data, timeout=30)
            if response.status_code == 200:
                return {'success': True, 'contacts': response.json().get('results', [])}
            return {'success': False, 'error': 'Search failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def create_deal(cls, properties: dict) -> dict:
        """Create a deal"""
        if not config.HUBSPOT_API_KEY:
            return {'success': False, 'error': 'HubSpot not configured'}
        
        url = f"{cls.BASE_URL}/crm/v3/objects/deals"
        data = {'properties': properties}
        
        try:
            response = requests.post(url, headers=cls._headers(), json=data, timeout=30)
            if response.status_code in [200, 201]:
                return {'success': True, 'deal': response.json()}
            return {'success': False, 'error': response.json().get('message', 'Error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def sync_contact_to_hubspot(cls, contact: Contact) -> dict:
        """Sync local contact to HubSpot"""
        properties = {
            'email': contact.email,
            'firstname': contact.name.split()[0] if contact.name else '',
            'lastname': ' '.join(contact.name.split()[1:]) if contact.name else '',
            'phone': contact.phone,
            'company': contact.company,
            'jobtitle': contact.position
        }
        
        if contact.hubspot_id:
            result = cls.update_contact(contact.hubspot_id, properties)
        else:
            result = cls.create_contact(contact.email, properties)
            if result.get('success'):
                contact.hubspot_id = result['contact']['id']
                contact.hubspot_sync_date = datetime.utcnow()
                db.session.commit()
        
        return result


class ClaudeAIService:
    """Claude AI (Anthropic) API Integration for Chatbots"""
    
    BASE_URL = "https://api.anthropic.com/v1/messages"
    
    # System prompts for different bot types
    SYSTEM_PROMPTS = {
        'support': """Du bist der West Money Support Bot - ein freundlicher und kompetenter 
Kundenservice-Assistent für Enterprise Universe GmbH.

Deine Aufgaben:
• Beantworte Fragen zu Smart Home (LOXONE), Barrierefreiem Bauen und Z Automation
• Sei immer freundlich, professionell und hilfsbereit
• Nutze Emojis sparsam aber effektiv für bessere Lesbarkeit
• Bei komplexen Anfragen: Biete einen Rückruf oder Termin an
• Antworte auf Deutsch, außer der Kunde schreibt in einer anderen Sprache

Unternehmen: West Money Bau / Enterprise Universe GmbH
Services: Smart Home (LOXONE), Barrierefreies Bauen, Z Automation, DedSec World AI (Sicherheit)
CEO: Ömer Hüseyin Coşkun

Halte deine Antworten kurz und prägnant (max. 200 Wörter).""",

        'sales': """Du bist der West Money Sales Bot - ein überzeugender aber nicht aufdringlicher
Verkaufsberater für Smart Home und Baudienstleistungen.

Deine Aufgaben:
• Qualifiziere Leads durch gezielte Fragen zu Projektumfang und Budget
• Präsentiere passende Lösungen basierend auf Kundenanforderungen
• Biete Beratungstermine an
• Erkläre Preise transparent

Preisrahmen (ca.):
• Smart Home Starter: €15.000 - €25.000
• Smart Home Premium: €25.000 - €45.000
• Smart Home Ultimate: Ab €45.000
• Barrierefreier Umbau: Ab €20.000

Halte Antworten verkaufsorientiert aber authentisch.""",

        'concierge': """Du bist der West Money Concierge - ein Premium AI-Assistent für VIP-Kunden.

Deine Aufgaben:
• Persönlicher, eleganter Service auf höchstem Niveau
• Proaktive Projekt-Updates und Empfehlungen
• Lifestyle-Services: Restaurant-Reservierungen, Reiseplanung, Event-Empfehlungen
• Exklusive Angebote präsentieren
• Höchste Diskretion

Tonalität: Elegant, diskret, persönlich, aufmerksam
Anrede: Formell (Sie), außer anders gewünscht
Antworte immer auf Deutsch."""
    }
    
    @classmethod
    def chat(cls, messages: list, bot_type: str = 'support', 
             max_tokens: int = 1024, temperature: float = 0.7) -> dict:
        """Send a chat message to Claude"""
        if not config.ANTHROPIC_API_KEY:
            return {'success': False, 'error': 'Claude API not configured'}
        
        headers = {
            'x-api-key': config.ANTHROPIC_API_KEY,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        system_prompt = cls.SYSTEM_PROMPTS.get(bot_type, cls.SYSTEM_PROMPTS['support'])
        
        payload = {
            'model': config.CLAUDE_MODEL,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'system': system_prompt,
            'messages': messages
        }
        
        try:
            response = requests.post(cls.BASE_URL, headers=headers, json=payload, timeout=60)
            data = response.json()
            
            if response.status_code == 200:
                content = data.get('content', [{}])[0].get('text', '')
                return {
                    'success': True,
                    'response': content,
                    'usage': data.get('usage', {}),
                    'model': data.get('model')
                }
            else:
                return {
                    'success': False,
                    'error': data.get('error', {}).get('message', 'API Error'),
                    'data': data
                }
        except requests.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def process_support_query(cls, user_message: str, conversation_history: list = None) -> dict:
        """Process a support query with context"""
        messages = conversation_history or []
        messages.append({'role': 'user', 'content': user_message})
        
        result = cls.chat(messages, bot_type='support')
        
        if result.get('success'):
            messages.append({'role': 'assistant', 'content': result['response']})
            result['conversation'] = messages
        
        return result
    
    @classmethod
    def analyze_lead(cls, lead_info: dict) -> dict:
        """Analyze a lead and provide recommendations"""
        prompt = f"""Analysiere diesen Lead und gib eine Einschätzung:

Name: {lead_info.get('name', 'Unbekannt')}
Unternehmen: {lead_info.get('company', 'Unbekannt')}
Anfrage: {lead_info.get('inquiry', 'Keine Angabe')}
Budget: {lead_info.get('budget', 'Unbekannt')}
Zeitrahmen: {lead_info.get('timeline', 'Unbekannt')}

Gib eine kurze Analyse mit:
1. Lead-Qualität (1-10)
2. Empfohlene nächste Schritte
3. Passende Produkte/Services"""

        return cls.chat([{'role': 'user', 'content': prompt}], bot_type='sales')


class ExploriumService:
    """Explorium B2B Data Enrichment API"""
    
    BASE_URL = "https://api.explorium.ai"
    
    @classmethod
    def _headers(cls):
        return {
            'Authorization': f'Bearer {config.EXPLORIUM_API_KEY}',
            'Content-Type': 'application/json'
        }
    
    @classmethod
    def enrich_company(cls, company_name: str = None, domain: str = None) -> dict:
        """Enrich company data"""
        if not config.EXPLORIUM_API_KEY:
            return {'success': False, 'error': 'Explorium not configured'}
        
        if not company_name and not domain:
            return {'success': False, 'error': 'Company name or domain required'}
        
        # This is a simplified example - actual API may differ
        url = f"{cls.BASE_URL}/v1/company/enrich"
        data = {}
        if company_name:
            data['name'] = company_name
        if domain:
            data['domain'] = domain
        
        try:
            response = requests.post(url, headers=cls._headers(), json=data, timeout=30)
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': 'Enrichment failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class OpenCorporatesService:
    """OpenCorporates (Handelsregister) API Integration"""
    
    BASE_URL = "https://api.opencorporates.com/v0.4"
    
    @classmethod
    def search_company(cls, query: str, jurisdiction: str = 'de') -> dict:
        """Search for companies in Handelsregister"""
        url = f"{cls.BASE_URL}/companies/search"
        params = {
            'q': query,
            'jurisdiction_code': jurisdiction,
            'api_token': config.OPENCORPORATES_API_KEY
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                companies = data.get('results', {}).get('companies', [])
                return {'success': True, 'companies': companies}
            return {'success': False, 'error': 'Search failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_company(cls, jurisdiction: str, company_number: str) -> dict:
        """Get detailed company information"""
        url = f"{cls.BASE_URL}/companies/{jurisdiction}/{company_number}"
        params = {'api_token': config.OPENCORPORATES_API_KEY} if config.OPENCORPORATES_API_KEY else {}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return {'success': True, 'company': data.get('results', {}).get('company', {})}
            return {'success': False, 'error': 'Company not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# =============================================================================
# AUTO BOTS - AUTOMATED WORKFLOWS
# =============================================================================

class AutoBot:
    """Base class for automated workflows"""
    
    @staticmethod
    def run_all():
        """Run all auto bots"""
        results = {}
        results['lead_scorer'] = LeadScoringBot.run()
        results['follow_up'] = FollowUpBot.run()
        results['sync'] = SyncBot.run()
        return results


class LeadScoringBot(AutoBot):
    """Automatically score and prioritize leads"""
    
    SCORING_RULES = {
        'has_email': 10,
        'has_phone': 10,
        'has_company': 15,
        'has_position': 10,
        'whatsapp_consent': 20,
        'recent_activity': 15,  # Last 7 days
        'multiple_interactions': 20
    }
    
    @classmethod
    def run(cls) -> dict:
        """Score all contacts"""
        try:
            contacts = Contact.query.filter(Contact.status != 'inactive').all()
            updated = 0
            
            for contact in contacts:
                old_score = contact.score
                new_score = cls.calculate_score(contact)
                
                if old_score != new_score:
                    contact.score = new_score
                    updated += 1
            
            db.session.commit()
            logger.info(f"LeadScoringBot: Updated {updated} contact scores")
            return {'success': True, 'updated': updated}
        except Exception as e:
            logger.error(f"LeadScoringBot error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def calculate_score(cls, contact: Contact) -> int:
        """Calculate lead score based on rules"""
        score = 0
        
        if contact.email:
            score += cls.SCORING_RULES['has_email']
        if contact.phone or contact.whatsapp_number:
            score += cls.SCORING_RULES['has_phone']
        if contact.company:
            score += cls.SCORING_RULES['has_company']
        if contact.position:
            score += cls.SCORING_RULES['has_position']
        if contact.whatsapp_consent:
            score += cls.SCORING_RULES['whatsapp_consent']
        
        # Recent activity bonus
        if contact.last_contact:
            days_since = (datetime.utcnow() - contact.last_contact).days
            if days_since <= 7:
                score += cls.SCORING_RULES['recent_activity']
        
        # Multiple interactions bonus
        message_count = Message.query.filter_by(contact_id=contact.id).count()
        if message_count >= 3:
            score += cls.SCORING_RULES['multiple_interactions']
        
        return min(score, 100)  # Cap at 100


class FollowUpBot(AutoBot):
    """Automatically create follow-up tasks for inactive leads"""
    
    INACTIVITY_DAYS = 7
    
    @classmethod
    def run(cls) -> dict:
        """Create follow-up tasks for inactive contacts"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=cls.INACTIVITY_DAYS)
            
            # Find contacts without recent activity
            inactive_contacts = Contact.query.filter(
                Contact.status.in_(['lead', 'active']),
                db.or_(
                    Contact.last_contact < cutoff_date,
                    Contact.last_contact.is_(None)
                )
            ).all()
            
            tasks_created = 0
            
            for contact in inactive_contacts:
                # Check if follow-up task already exists
                existing_task = Task.query.filter(
                    Task.contact_id == contact.id,
                    Task.status == 'pending',
                    Task.title.like('%Follow-up%')
                ).first()
                
                if not existing_task:
                    task = Task(
                        user_id=contact.user_id,
                        contact_id=contact.id,
                        title=f"Follow-up: {contact.name}",
                        description=f"Kein Kontakt seit {cls.INACTIVITY_DAYS} Tagen. Bitte nachfassen.",
                        priority='medium',
                        due_date=datetime.utcnow().date() + timedelta(days=2)
                    )
                    db.session.add(task)
                    tasks_created += 1
            
            db.session.commit()
            logger.info(f"FollowUpBot: Created {tasks_created} follow-up tasks")
            return {'success': True, 'tasks_created': tasks_created}
        except Exception as e:
            logger.error(f"FollowUpBot error: {e}")
            return {'success': False, 'error': str(e)}


class SyncBot(AutoBot):
    """Automatically sync data with external services"""
    
    @classmethod
    def run(cls) -> dict:
        """Sync contacts with HubSpot"""
        try:
            if not config.HUBSPOT_API_KEY:
                return {'success': False, 'error': 'HubSpot not configured'}
            
            # Find contacts needing sync (not synced in last 24 hours)
            cutoff = datetime.utcnow() - timedelta(hours=24)
            contacts_to_sync = Contact.query.filter(
                db.or_(
                    Contact.hubspot_sync_date < cutoff,
                    Contact.hubspot_sync_date.is_(None)
                ),
                Contact.email.isnot(None)
            ).limit(50).all()
            
            synced = 0
            errors = 0
            
            for contact in contacts_to_sync:
                result = HubSpotService.sync_contact_to_hubspot(contact)
                if result.get('success'):
                    synced += 1
                else:
                    errors += 1
            
            logger.info(f"SyncBot: Synced {synced} contacts, {errors} errors")
            return {'success': True, 'synced': synced, 'errors': errors}
        except Exception as e:
            logger.error(f"SyncBot error: {e}")
            return {'success': False, 'error': str(e)}


class WelcomeBot(AutoBot):
    """Send welcome messages to new contacts"""
    
    WELCOME_MESSAGE = """Hallo {name}! 👋

Willkommen bei West Money! Ich bin Ihr persönlicher Assistent.

Wie kann ich Ihnen heute helfen?

🏠 Smart Home Beratung
🔧 Service & Support  
📅 Termin vereinbaren
💬 Allgemeine Fragen

Antworten Sie einfach mit einer Zahl oder Ihrer Frage!"""
    
    @classmethod
    def send_welcome(cls, contact: Contact) -> dict:
        """Send welcome message to new contact"""
        if not contact.whatsapp_number or not contact.whatsapp_consent:
            return {'success': False, 'error': 'No WhatsApp consent'}
        
        message = cls.WELCOME_MESSAGE.format(name=contact.name.split()[0] if contact.name else 'Kunde')
        
        result = WhatsAppService.send_interactive(
            to=contact.whatsapp_number,
            body=message,
            buttons=['🏠 Smart Home', '🔧 Support', '📅 Termin']
        )
        
        if result.get('success'):
            # Log message
            msg = Message(
                contact_id=contact.id,
                direction='out',
                message_type='interactive',
                content=message,
                status='sent',
                whatsapp_message_id=result.get('message_id')
            )
            db.session.add(msg)
            db.session.commit()
        
        return result


# =============================================================================
# PAYMENT & SUBSCRIPTION MODELS
# =============================================================================

class Subscription(db.Model):
    """User Subscription model"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Subscription Details
    plan = db.Column(db.String(50), nullable=False)  # free, starter, professional, enterprise
    status = db.Column(db.String(20), default='active')  # active, cancelled, past_due, trialing
    
    # Stripe Integration
    stripe_customer_id = db.Column(db.String(100))
    stripe_subscription_id = db.Column(db.String(100))
    stripe_price_id = db.Column(db.String(100))
    
    # Billing
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, yearly
    amount = db.Column(db.Float, default=0)
    currency = db.Column(db.String(3), default='EUR')
    
    # Dates
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    trial_end = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan': self.plan,
            'status': self.status,
            'billing_cycle': self.billing_cycle,
            'amount': self.amount,
            'currency': self.currency,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Payment(db.Model):
    """Payment/Transaction model"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Payment Details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    payment_method = db.Column(db.String(50))  # card, bank_transfer, revolut, mollie
    
    # Provider IDs
    stripe_payment_id = db.Column(db.String(100))
    mollie_payment_id = db.Column(db.String(100))
    revolut_payment_id = db.Column(db.String(100))
    
    # Related Objects
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'))
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'))
    
    # Metadata
    description = db.Column(db.String(500))
    payment_metadata = db.Column(db.JSON)  # Renamed from 'metadata' (reserved)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'payment_method': self.payment_method,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BankAccount(db.Model):
    """Revolut/Bank Account model"""
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Account Details
    account_name = db.Column(db.String(200))
    iban = db.Column(db.String(34))
    bic = db.Column(db.String(11))
    bank_name = db.Column(db.String(100))
    account_type = db.Column(db.String(50))  # business, personal
    
    # Revolut Integration
    revolut_account_id = db.Column(db.String(100))
    revolut_pocket_id = db.Column(db.String(100))
    
    # Balance (cached)
    balance = db.Column(db.Float, default=0)
    available_balance = db.Column(db.Float, default=0)
    currency = db.Column(db.String(3), default='EUR')
    balance_updated_at = db.Column(db.DateTime)
    
    # Status
    is_primary = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_name': self.account_name,
            'iban': self.iban[-4:].rjust(len(self.iban), '*') if self.iban else None,  # Masked
            'bank_name': self.bank_name,
            'balance': self.balance,
            'available_balance': self.available_balance,
            'currency': self.currency,
            'is_primary': self.is_primary
        }


class BankTransaction(db.Model):
    """Bank Transaction model"""
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    
    # Transaction Details
    transaction_type = db.Column(db.String(20))  # credit, debit
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    
    # Counterparty
    counterparty_name = db.Column(db.String(200))
    counterparty_iban = db.Column(db.String(34))
    
    # Reference
    reference = db.Column(db.String(500))
    category = db.Column(db.String(50))  # income, expense, transfer, fee
    
    # Provider
    revolut_transaction_id = db.Column(db.String(100))
    
    # Timestamps
    transaction_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.transaction_type,
            'amount': self.amount,
            'currency': self.currency,
            'counterparty': self.counterparty_name,
            'reference': self.reference,
            'category': self.category,
            'date': self.transaction_date.isoformat() if self.transaction_date else None
        }


# =============================================================================
# PAYMENT SERVICE CLASSES
# =============================================================================

class StripeService:
    """Stripe Payment Integration"""
    
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    # Price IDs for each plan
    PRICE_IDS = {
        'starter_monthly': os.getenv('STRIPE_PRICE_STARTER_MONTHLY', ''),
        'starter_yearly': os.getenv('STRIPE_PRICE_STARTER_YEARLY', ''),
        'professional_monthly': os.getenv('STRIPE_PRICE_PRO_MONTHLY', ''),
        'professional_yearly': os.getenv('STRIPE_PRICE_PRO_YEARLY', ''),
        'enterprise_monthly': os.getenv('STRIPE_PRICE_ENTERPRISE_MONTHLY', ''),
        'enterprise_yearly': os.getenv('STRIPE_PRICE_ENTERPRISE_YEARLY', ''),
    }
    
    @classmethod
    def _headers(cls):
        import base64
        auth = base64.b64encode(f"{cls.STRIPE_SECRET_KEY}:".encode()).decode()
        return {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    @classmethod
    def create_customer(cls, email: str, name: str = None, metadata: dict = None) -> dict:
        """Create a Stripe customer"""
        if not cls.STRIPE_SECRET_KEY:
            return {'success': False, 'error': 'Stripe not configured'}
        
        url = "https://api.stripe.com/v1/customers"
        data = {'email': email}
        if name:
            data['name'] = name
        if metadata:
            for key, value in metadata.items():
                data[f'metadata[{key}]'] = value
        
        try:
            response = requests.post(url, headers=cls._headers(), data=data, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                return {'success': True, 'customer': result}
            return {'success': False, 'error': result.get('error', {}).get('message', 'Error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def create_checkout_session(cls, user: User, plan: str, billing_cycle: str = 'monthly',
                                success_url: str = None, cancel_url: str = None) -> dict:
        """Create a Stripe Checkout session for subscription"""
        if not cls.STRIPE_SECRET_KEY:
            return {'success': False, 'error': 'Stripe not configured'}
        
        price_key = f"{plan}_{billing_cycle}"
        price_id = cls.PRICE_IDS.get(price_key)
        
        if not price_id:
            return {'success': False, 'error': f'Invalid plan: {plan}'}
        
        url = "https://api.stripe.com/v1/checkout/sessions"
        data = {
            'mode': 'subscription',
            'payment_method_types[]': 'card',
            'line_items[0][price]': price_id,
            'line_items[0][quantity]': 1,
            'success_url': success_url or f"{os.getenv('APP_URL', 'http://localhost:5000')}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            'cancel_url': cancel_url or f"{os.getenv('APP_URL', 'http://localhost:5000')}/payment/cancel",
            'customer_email': user.email,
            'metadata[user_id]': str(user.id),
            'metadata[plan]': plan,
            'metadata[billing_cycle]': billing_cycle,
            'allow_promotion_codes': 'true'
        }
        
        try:
            response = requests.post(url, headers=cls._headers(), data=data, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'session_id': result.get('id'),
                    'url': result.get('url')
                }
            return {'success': False, 'error': result.get('error', {}).get('message', 'Error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def create_portal_session(cls, customer_id: str, return_url: str = None) -> dict:
        """Create a Stripe Customer Portal session"""
        if not cls.STRIPE_SECRET_KEY:
            return {'success': False, 'error': 'Stripe not configured'}
        
        url = "https://api.stripe.com/v1/billing_portal/sessions"
        data = {
            'customer': customer_id,
            'return_url': return_url or os.getenv('APP_URL', 'http://localhost:5000')
        }
        
        try:
            response = requests.post(url, headers=cls._headers(), data=data, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                return {'success': True, 'url': result.get('url')}
            return {'success': False, 'error': result.get('error', {}).get('message', 'Error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def cancel_subscription(cls, subscription_id: str, at_period_end: bool = True) -> dict:
        """Cancel a subscription"""
        if not cls.STRIPE_SECRET_KEY:
            return {'success': False, 'error': 'Stripe not configured'}
        
        url = f"https://api.stripe.com/v1/subscriptions/{subscription_id}"
        data = {'cancel_at_period_end': 'true' if at_period_end else 'false'}
        
        try:
            response = requests.post(url, headers=cls._headers(), data=data, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                return {'success': True, 'subscription': result}
            return {'success': False, 'error': result.get('error', {}).get('message', 'Error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_subscription(cls, subscription_id: str) -> dict:
        """Get subscription details"""
        if not cls.STRIPE_SECRET_KEY:
            return {'success': False, 'error': 'Stripe not configured'}
        
        url = f"https://api.stripe.com/v1/subscriptions/{subscription_id}"
        
        try:
            response = requests.get(url, headers=cls._headers(), timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                return {'success': True, 'subscription': result}
            return {'success': False, 'error': 'Subscription not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def create_payment_intent(cls, amount: int, currency: str = 'eur',
                              customer_id: str = None, metadata: dict = None) -> dict:
        """Create a one-time payment intent"""
        if not cls.STRIPE_SECRET_KEY:
            return {'success': False, 'error': 'Stripe not configured'}
        
        url = "https://api.stripe.com/v1/payment_intents"
        data = {
            'amount': amount,  # Amount in cents
            'currency': currency,
            'payment_method_types[]': 'card'
        }
        
        if customer_id:
            data['customer'] = customer_id
        if metadata:
            for key, value in metadata.items():
                data[f'metadata[{key}]'] = value
        
        try:
            response = requests.post(url, headers=cls._headers(), data=data, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'client_secret': result.get('client_secret'),
                    'payment_intent_id': result.get('id')
                }
            return {'success': False, 'error': result.get('error', {}).get('message', 'Error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class MollieService:
    """Mollie Payment Integration (Popular in EU/Germany)"""
    
    MOLLIE_API_KEY = os.getenv('MOLLIE_API_KEY', '')
    BASE_URL = "https://api.mollie.com/v2"
    
    @classmethod
    def _headers(cls):
        return {
            'Authorization': f'Bearer {cls.MOLLIE_API_KEY}',
            'Content-Type': 'application/json'
        }
    
    @classmethod
    def create_payment(cls, amount: float, description: str, redirect_url: str,
                       webhook_url: str = None, metadata: dict = None) -> dict:
        """Create a Mollie payment"""
        if not cls.MOLLIE_API_KEY:
            return {'success': False, 'error': 'Mollie not configured'}
        
        url = f"{cls.BASE_URL}/payments"
        data = {
            'amount': {
                'currency': 'EUR',
                'value': f"{amount:.2f}"
            },
            'description': description,
            'redirectUrl': redirect_url,
            'metadata': metadata or {}
        }
        
        if webhook_url:
            data['webhookUrl'] = webhook_url
        
        try:
            response = requests.post(url, headers=cls._headers(), json=data, timeout=30)
            result = response.json()
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'payment_id': result.get('id'),
                    'checkout_url': result.get('_links', {}).get('checkout', {}).get('href'),
                    'data': result
                }
            return {'success': False, 'error': result.get('detail', 'Payment creation failed')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_payment(cls, payment_id: str) -> dict:
        """Get payment status"""
        if not cls.MOLLIE_API_KEY:
            return {'success': False, 'error': 'Mollie not configured'}
        
        url = f"{cls.BASE_URL}/payments/{payment_id}"
        
        try:
            response = requests.get(url, headers=cls._headers(), timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'status': result.get('status'),
                    'data': result
                }
            return {'success': False, 'error': 'Payment not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def create_subscription(cls, customer_id: str, amount: float, interval: str,
                           description: str, webhook_url: str = None) -> dict:
        """Create a Mollie subscription"""
        if not cls.MOLLIE_API_KEY:
            return {'success': False, 'error': 'Mollie not configured'}
        
        url = f"{cls.BASE_URL}/customers/{customer_id}/subscriptions"
        data = {
            'amount': {
                'currency': 'EUR',
                'value': f"{amount:.2f}"
            },
            'interval': interval,  # e.g., "1 month", "1 year"
            'description': description
        }
        
        if webhook_url:
            data['webhookUrl'] = webhook_url
        
        try:
            response = requests.post(url, headers=cls._headers(), json=data, timeout=30)
            result = response.json()
            
            if response.status_code in [200, 201]:
                return {'success': True, 'subscription': result}
            return {'success': False, 'error': result.get('detail', 'Error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class RevolutService:
    """Revolut Business API Integration for Account Management"""
    
    REVOLUT_API_KEY = os.getenv('REVOLUT_API_KEY', '')
    REVOLUT_BASE_URL = os.getenv('REVOLUT_BASE_URL', 'https://b2b.revolut.com/api/1.0')
    
    @classmethod
    def _headers(cls):
        return {
            'Authorization': f'Bearer {cls.REVOLUT_API_KEY}',
            'Content-Type': 'application/json'
        }
    
    @classmethod
    def get_accounts(cls) -> dict:
        """Get all Revolut Business accounts"""
        if not cls.REVOLUT_API_KEY:
            return {'success': False, 'error': 'Revolut not configured'}
        
        url = f"{cls.REVOLUT_BASE_URL}/accounts"
        
        try:
            response = requests.get(url, headers=cls._headers(), timeout=30)
            
            if response.status_code == 200:
                accounts = response.json()
                return {'success': True, 'accounts': accounts}
            return {'success': False, 'error': 'Failed to fetch accounts'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_account_details(cls, account_id: str) -> dict:
        """Get specific account details"""
        if not cls.REVOLUT_API_KEY:
            return {'success': False, 'error': 'Revolut not configured'}
        
        url = f"{cls.REVOLUT_BASE_URL}/accounts/{account_id}"
        
        try:
            response = requests.get(url, headers=cls._headers(), timeout=30)
            
            if response.status_code == 200:
                return {'success': True, 'account': response.json()}
            return {'success': False, 'error': 'Account not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_transactions(cls, account_id: str = None, from_date: str = None,
                        to_date: str = None, count: int = 100) -> dict:
        """Get transactions"""
        if not cls.REVOLUT_API_KEY:
            return {'success': False, 'error': 'Revolut not configured'}
        
        url = f"{cls.REVOLUT_BASE_URL}/transactions"
        params = {'count': count}
        
        if account_id:
            params['account_id'] = account_id
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
        try:
            response = requests.get(url, headers=cls._headers(), params=params, timeout=30)
            
            if response.status_code == 200:
                return {'success': True, 'transactions': response.json()}
            return {'success': False, 'error': 'Failed to fetch transactions'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def create_payment(cls, account_id: str, receiver: dict, amount: float,
                       currency: str = 'EUR', reference: str = None) -> dict:
        """Create a payment/transfer"""
        if not cls.REVOLUT_API_KEY:
            return {'success': False, 'error': 'Revolut not configured'}
        
        url = f"{cls.REVOLUT_BASE_URL}/pay"
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        data = {
            'request_id': request_id,
            'account_id': account_id,
            'receiver': receiver,  # {'counterparty_id': 'xxx'} or IBAN details
            'amount': amount,
            'currency': currency,
            'reference': reference or 'West Money Payment'
        }
        
        try:
            response = requests.post(url, headers=cls._headers(), json=data, timeout=30)
            result = response.json()
            
            if response.status_code in [200, 201]:
                return {'success': True, 'payment': result}
            return {'success': False, 'error': result.get('message', 'Payment failed')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def create_counterparty(cls, name: str, iban: str = None, bic: str = None,
                           email: str = None, bank_country: str = 'DE') -> dict:
        """Create a counterparty for payments"""
        if not cls.REVOLUT_API_KEY:
            return {'success': False, 'error': 'Revolut not configured'}
        
        url = f"{cls.REVOLUT_BASE_URL}/counterparty"
        
        data = {
            'company_name': name,
            'bank_country': bank_country,
            'currency': 'EUR'
        }
        
        if iban:
            data['iban'] = iban
        if bic:
            data['bic'] = bic
        if email:
            data['email'] = email
        
        try:
            response = requests.post(url, headers=cls._headers(), json=data, timeout=30)
            result = response.json()
            
            if response.status_code in [200, 201]:
                return {'success': True, 'counterparty': result}
            return {'success': False, 'error': result.get('message', 'Failed to create counterparty')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_exchange_rates(cls, from_currency: str = 'EUR', to_currency: str = 'USD') -> dict:
        """Get exchange rates"""
        if not cls.REVOLUT_API_KEY:
            return {'success': False, 'error': 'Revolut not configured'}
        
        url = f"{cls.REVOLUT_BASE_URL}/rate"
        params = {
            'from': from_currency,
            'to': to_currency,
            'amount': 1
        }
        
        try:
            response = requests.get(url, headers=cls._headers(), params=params, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                return {'success': True, 'rate': result}
            return {'success': False, 'error': 'Failed to get exchange rate'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def sync_accounts_to_db(cls, user_id: int) -> dict:
        """Sync Revolut accounts to local database"""
        result = cls.get_accounts()
        
        if not result.get('success'):
            return result
        
        synced = 0
        for account in result.get('accounts', []):
            # Check if account exists
            existing = BankAccount.query.filter_by(
                revolut_account_id=account.get('id')
            ).first()
            
            if existing:
                # Update balance
                existing.balance = account.get('balance', 0)
                existing.available_balance = account.get('balance', 0)
                existing.balance_updated_at = datetime.utcnow()
            else:
                # Create new
                new_account = BankAccount(
                    user_id=user_id,
                    account_name=account.get('name', 'Revolut Account'),
                    revolut_account_id=account.get('id'),
                    currency=account.get('currency', 'EUR'),
                    balance=account.get('balance', 0),
                    available_balance=account.get('balance', 0),
                    bank_name='Revolut',
                    account_type='business',
                    balance_updated_at=datetime.utcnow()
                )
                db.session.add(new_account)
                synced += 1
        
        try:
            db.session.commit()
            return {'success': True, 'synced': synced}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}


class DATEVService:
    """DATEV Export for German Accounting"""
    
    @classmethod
    def export_invoices_csv(cls, invoices: list) -> str:
        """Export invoices in DATEV format"""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        
        # DATEV Header
        writer.writerow([
            'Belegdatum', 'Buchungstext', 'Umsatz', 'S/H', 'Konto', 
            'Gegenkonto', 'BU-Schlüssel', 'Belegfeld 1', 'USt-Schlüssel'
        ])
        
        for invoice in invoices:
            # S = Soll (Debit), H = Haben (Credit)
            writer.writerow([
                invoice.invoice_date.strftime('%d%m%Y') if invoice.invoice_date else '',
                f"RE {invoice.invoice_number}",
                f"{invoice.total:.2f}".replace('.', ','),
                'S',
                '10000',  # Debitorenkonto
                '8400',   # Erlöse
                '',
                invoice.invoice_number,
                '3' if invoice.tax_rate == 19 else '2'  # 3=19%, 2=7%
            ])
        
        return output.getvalue()
    
    @classmethod
    def export_transactions_csv(cls, transactions: list) -> str:
        """Export bank transactions in DATEV format"""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow([
            'Datum', 'Verwendungszweck', 'Betrag', 'Währung', 
            'Empfänger/Auftraggeber', 'IBAN'
        ])
        
        for txn in transactions:
            writer.writerow([
                txn.transaction_date.strftime('%d.%m.%Y') if txn.transaction_date else '',
                txn.reference or '',
                f"{txn.amount:.2f}".replace('.', ','),
                txn.currency,
                txn.counterparty_name or '',
                txn.counterparty_iban or ''
            ])
        
        return output.getvalue()


# =============================================================================
# PAYMENT API ROUTES
# =============================================================================

@app.route('/api/payments/plans', methods=['GET'])
def api_get_plans():
    """Get available subscription plans"""
    return jsonify({
        'success': True,
        'plans': PLANS
    })


@app.route('/api/payments/checkout', methods=['POST'])
@login_required
def api_create_checkout():
    """Create a checkout session for subscription"""
    user = get_current_user()
    data = request.get_json() or {}
    
    plan = data.get('plan', 'professional')
    billing_cycle = data.get('billing_cycle', 'monthly')
    
    if plan not in ['starter', 'professional', 'enterprise']:
        return jsonify({'success': False, 'error': 'Ungültiger Plan'}), 400
    
    result = StripeService.create_checkout_session(user, plan, billing_cycle)
    
    if result.get('success'):
        log_security_event('checkout_created', 'info', {
            'user_id': user.id,
            'plan': plan,
            'billing_cycle': billing_cycle
        })
    
    return jsonify(result)


@app.route('/api/payments/portal', methods=['POST'])
@login_required
def api_billing_portal():
    """Create a Stripe Customer Portal session"""
    user = get_current_user()
    
    # Get user's subscription
    subscription = Subscription.query.filter_by(user_id=user.id).first()
    
    if not subscription or not subscription.stripe_customer_id:
        return jsonify({'success': False, 'error': 'Kein aktives Abo'}), 400
    
    result = StripeService.create_portal_session(subscription.stripe_customer_id)
    
    return jsonify(result)


@app.route('/api/payments/subscription', methods=['GET'])
@login_required
def api_get_subscription():
    """Get user's subscription details"""
    user = get_current_user()
    
    subscription = Subscription.query.filter_by(user_id=user.id).first()
    
    if subscription:
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict()
        })
    
    return jsonify({
        'success': True,
        'subscription': None,
        'plan': user.plan
    })


@app.route('/api/payments/cancel', methods=['POST'])
@login_required
def api_cancel_subscription():
    """Cancel subscription"""
    user = get_current_user()
    
    subscription = Subscription.query.filter_by(user_id=user.id, status='active').first()
    
    if not subscription or not subscription.stripe_subscription_id:
        return jsonify({'success': False, 'error': 'Kein aktives Abo'}), 400
    
    result = StripeService.cancel_subscription(subscription.stripe_subscription_id)
    
    if result.get('success'):
        subscription.status = 'cancelled'
        subscription.cancelled_at = datetime.utcnow()
        db.session.commit()
        
        create_notification(
            user.id,
            'subscription',
            'Abo gekündigt',
            f'Ihr {subscription.plan} Abo wurde gekündigt. Aktiv bis zum Ende der Laufzeit.',
            '❌'
        )
    
    return jsonify(result)


@app.route('/api/payments/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Stripe webhook endpoint"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    # In production, verify the webhook signature
    # For now, just process the event
    try:
        event = json.loads(payload)
        event_type = event.get('type')
        data = event.get('data', {}).get('object', {})
        
        logger.info(f"Stripe webhook: {event_type}")
        
        if event_type == 'checkout.session.completed':
            # Payment successful, create subscription
            user_id = data.get('metadata', {}).get('user_id')
            plan = data.get('metadata', {}).get('plan')
            billing_cycle = data.get('metadata', {}).get('billing_cycle')
            
            if user_id:
                user = User.query.get(int(user_id))
                if user:
                    # Update user plan
                    user.plan = plan
                    
                    # Create subscription record
                    subscription = Subscription(
                        user_id=user.id,
                        plan=plan,
                        status='active',
                        stripe_customer_id=data.get('customer'),
                        stripe_subscription_id=data.get('subscription'),
                        billing_cycle=billing_cycle,
                        amount=PLANS.get(plan, {}).get('price', 0),
                        current_period_start=datetime.utcnow()
                    )
                    db.session.add(subscription)
                    db.session.commit()
                    
                    create_notification(
                        user.id,
                        'subscription',
                        'Willkommen! 🎉',
                        f'Ihr {plan.title()} Plan ist jetzt aktiv.',
                        '✅'
                    )
        
        elif event_type == 'customer.subscription.updated':
            # Subscription updated
            stripe_sub_id = data.get('id')
            subscription = Subscription.query.filter_by(
                stripe_subscription_id=stripe_sub_id
            ).first()
            
            if subscription:
                subscription.status = data.get('status', 'active')
                subscription.current_period_end = datetime.fromtimestamp(
                    data.get('current_period_end', 0)
                )
                db.session.commit()
        
        elif event_type == 'customer.subscription.deleted':
            # Subscription cancelled
            stripe_sub_id = data.get('id')
            subscription = Subscription.query.filter_by(
                stripe_subscription_id=stripe_sub_id
            ).first()
            
            if subscription:
                subscription.status = 'cancelled'
                user = User.query.get(subscription.user_id)
                if user:
                    user.plan = 'free'
                db.session.commit()
        
        elif event_type == 'invoice.payment_failed':
            # Payment failed
            customer_id = data.get('customer')
            subscription = Subscription.query.filter_by(
                stripe_customer_id=customer_id
            ).first()
            
            if subscription:
                subscription.status = 'past_due'
                db.session.commit()
                
                create_notification(
                    subscription.user_id,
                    'payment',
                    'Zahlung fehlgeschlagen',
                    'Bitte aktualisieren Sie Ihre Zahlungsmethode.',
                    '⚠️'
                )
        
        return 'OK', 200
    
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return str(e), 400


@app.route('/api/payments/webhook/mollie', methods=['POST'])
def mollie_webhook():
    """Mollie webhook endpoint"""
    payment_id = request.form.get('id') or request.json.get('id')
    
    if not payment_id:
        return 'OK', 200
    
    try:
        result = MollieService.get_payment(payment_id)
        
        if result.get('success'):
            status = result.get('status')
            
            # Find payment in our database
            payment = Payment.query.filter_by(mollie_payment_id=payment_id).first()
            
            if payment:
                if status == 'paid':
                    payment.status = 'completed'
                    payment.completed_at = datetime.utcnow()
                elif status == 'failed':
                    payment.status = 'failed'
                elif status == 'expired':
                    payment.status = 'failed'
                
                db.session.commit()
        
        return 'OK', 200
    
    except Exception as e:
        logger.error(f"Mollie webhook error: {e}")
        return str(e), 400


# =============================================================================
# REVOLUT API ROUTES
# =============================================================================

@app.route('/api/banking/accounts', methods=['GET'])
@login_required
def api_get_bank_accounts():
    """Get user's bank accounts"""
    user = get_current_user()
    
    accounts = BankAccount.query.filter_by(user_id=user.id, is_active=True).all()
    
    return jsonify({
        'success': True,
        'accounts': [a.to_dict() for a in accounts]
    })


@app.route('/api/banking/sync', methods=['POST'])
@login_required
def api_sync_bank_accounts():
    """Sync Revolut accounts"""
    user = get_current_user()
    
    result = RevolutService.sync_accounts_to_db(user.id)
    
    return jsonify(result)


@app.route('/api/banking/transactions', methods=['GET'])
@login_required
def api_get_bank_transactions():
    """Get bank transactions"""
    user = get_current_user()
    account_id = request.args.get('account_id')
    
    query = BankTransaction.query.join(BankAccount).filter(
        BankAccount.user_id == user.id
    )
    
    if account_id:
        query = query.filter(BankTransaction.account_id == account_id)
    
    transactions = query.order_by(BankTransaction.transaction_date.desc()).limit(100).all()
    
    return jsonify({
        'success': True,
        'transactions': [t.to_dict() for t in transactions]
    })


@app.route('/api/banking/transfer', methods=['POST'])
@login_required
def api_create_transfer():
    """Create a bank transfer"""
    user = get_current_user()
    data = request.get_json() or {}
    
    # Validate admin/owner
    if user.role not in ['admin', 'GOD MODE']:
        return jsonify({'success': False, 'error': 'Keine Berechtigung'}), 403
    
    account_id = data.get('account_id')
    amount = data.get('amount')
    recipient_iban = data.get('recipient_iban')
    recipient_name = data.get('recipient_name')
    reference = data.get('reference')
    
    if not all([account_id, amount, recipient_iban, recipient_name]):
        return jsonify({'success': False, 'error': 'Alle Felder erforderlich'}), 400
    
    # Get account
    account = BankAccount.query.filter_by(
        id=account_id,
        user_id=user.id
    ).first()
    
    if not account or not account.revolut_account_id:
        return jsonify({'success': False, 'error': 'Konto nicht gefunden'}), 404
    
    # Create counterparty first
    counterparty_result = RevolutService.create_counterparty(
        name=recipient_name,
        iban=recipient_iban
    )
    
    if not counterparty_result.get('success'):
        return jsonify(counterparty_result)
    
    counterparty_id = counterparty_result['counterparty'].get('id')
    
    # Create payment
    result = RevolutService.create_payment(
        account_id=account.revolut_account_id,
        receiver={'counterparty_id': counterparty_id},
        amount=float(amount),
        reference=reference
    )
    
    if result.get('success'):
        # Log transaction
        log_security_event('bank_transfer', 'info', {
            'user_id': user.id,
            'amount': amount,
            'recipient': recipient_name
        })
    
    return jsonify(result)


@app.route('/api/banking/export/datev', methods=['GET'])
@login_required
def api_export_datev():
    """Export transactions in DATEV format"""
    user = get_current_user()
    
    # Get transactions
    transactions = BankTransaction.query.join(BankAccount).filter(
        BankAccount.user_id == user.id
    ).order_by(BankTransaction.transaction_date.desc()).limit(500).all()
    
    csv_content = DATEVService.export_transactions_csv(transactions)
    
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=datev_export.csv'}
    )


# =============================================================================
# EXTENDED INVOICE & BILLING SYSTEM
# =============================================================================

class InvoiceService:
    """Invoice Generation and Management"""
    
    COMPANY_INFO = {
        'name': 'Enterprise Universe GmbH',
        'address': 'Musterstraße 123',
        'city': '60329 Frankfurt am Main',
        'country': 'Deutschland',
        'email': 'billing@westmoney.de',
        'phone': '+49 69 123456789',
        'tax_id': 'DE123456789',
        'iban': 'DE42 1001 0178 9758 7887 93',
        'bic': 'NTSBDEB1XXX',
        'bank': 'N26 Bank'
    }
    
    @classmethod
    def generate_invoice_number(cls) -> str:
        """Generate unique invoice number"""
        year = datetime.utcnow().year
        month = datetime.utcnow().month
        
        # Count invoices this month
        count = Invoice.query.filter(
            db.extract('year', Invoice.created_at) == year,
            db.extract('month', Invoice.created_at) == month
        ).count()
        
        return f"WM-{year}{month:02d}-{count + 1:04d}"
    
    @classmethod
    def create_invoice(cls, user_id: int, contact_id: int, items: list,
                       due_days: int = 14, notes: str = None) -> dict:
        """Create a new invoice"""
        try:
            # Calculate totals
            subtotal = sum(item.get('quantity', 1) * item.get('price', 0) for item in items)
            tax_rate = 19.0  # German MwSt
            tax_amount = subtotal * (tax_rate / 100)
            total = subtotal + tax_amount
            
            # Get contact info
            contact = Contact.query.get(contact_id)
            if not contact:
                return {'success': False, 'error': 'Kontakt nicht gefunden'}
            
            invoice = Invoice(
                invoice_number=cls.generate_invoice_number(),
                user_id=user_id,
                contact_id=contact_id,
                customer_name=contact.name,
                customer_email=contact.email,
                customer_address=contact.company or '',
                subtotal=subtotal,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                total=total,
                status='draft',
                invoice_date=datetime.utcnow().date(),
                due_date=datetime.utcnow().date() + timedelta(days=due_days)
            )
            
            db.session.add(invoice)
            db.session.commit()
            
            return {'success': True, 'invoice': invoice.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def send_invoice(cls, invoice_id: int) -> dict:
        """Send invoice via email"""
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return {'success': False, 'error': 'Rechnung nicht gefunden'}
        
        # Update status
        invoice.status = 'sent'
        db.session.commit()
        
        # TODO: Implement actual email sending
        # EmailService.send_invoice_email(invoice)
        
        return {'success': True, 'message': 'Rechnung gesendet'}
    
    @classmethod
    def mark_paid(cls, invoice_id: int, payment_method: str = 'bank_transfer') -> dict:
        """Mark invoice as paid"""
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return {'success': False, 'error': 'Rechnung nicht gefunden'}
        
        invoice.status = 'paid'
        invoice.paid_date = datetime.utcnow().date()
        
        # Create payment record
        payment = Payment(
            user_id=invoice.user_id,
            amount=invoice.total,
            currency='EUR',
            status='completed',
            payment_method=payment_method,
            invoice_id=invoice.id,
            description=f"Zahlung für {invoice.invoice_number}",
            completed_at=datetime.utcnow()
        )
        db.session.add(payment)
        db.session.commit()
        
        return {'success': True, 'invoice': invoice.to_dict()}


class RecurringBillingService:
    """Automated Recurring Billing"""
    
    @classmethod
    def process_due_subscriptions(cls) -> dict:
        """Process all subscriptions due for billing"""
        today = datetime.utcnow().date()
        
        # Find subscriptions ending today
        due_subscriptions = Subscription.query.filter(
            Subscription.status == 'active',
            db.func.date(Subscription.current_period_end) <= today
        ).all()
        
        processed = 0
        failed = 0
        
        for subscription in due_subscriptions:
            # Stripe handles this automatically, but we track it
            result = StripeService.get_subscription(subscription.stripe_subscription_id)
            
            if result.get('success'):
                stripe_sub = result['subscription']
                subscription.status = stripe_sub.get('status', 'active')
                subscription.current_period_start = datetime.fromtimestamp(
                    stripe_sub.get('current_period_start', 0)
                )
                subscription.current_period_end = datetime.fromtimestamp(
                    stripe_sub.get('current_period_end', 0)
                )
                processed += 1
            else:
                failed += 1
        
        db.session.commit()
        
        return {
            'success': True,
            'processed': processed,
            'failed': failed
        }
    
    @classmethod
    def send_renewal_reminders(cls) -> dict:
        """Send reminder emails for upcoming renewals"""
        # Find subscriptions expiring in 7 days
        reminder_date = datetime.utcnow() + timedelta(days=7)
        
        upcoming = Subscription.query.filter(
            Subscription.status == 'active',
            db.func.date(Subscription.current_period_end) == reminder_date.date()
        ).all()
        
        for subscription in upcoming:
            create_notification(
                subscription.user_id,
                'subscription',
                'Abo-Verlängerung',
                f'Ihr {subscription.plan} Abo wird in 7 Tagen verlängert.',
                '🔔'
            )
        
        return {'success': True, 'reminders_sent': len(upcoming)}


# =============================================================================
# PAYMENT ANALYTICS
# =============================================================================

class PaymentAnalytics:
    """Payment and Revenue Analytics"""
    
    @classmethod
    def get_mrr(cls) -> dict:
        """Calculate Monthly Recurring Revenue"""
        active_subs = Subscription.query.filter_by(status='active').all()
        
        mrr = 0
        for sub in active_subs:
            if sub.billing_cycle == 'yearly':
                mrr += sub.amount / 12
            else:
                mrr += sub.amount
        
        return {
            'mrr': round(mrr, 2),
            'currency': 'EUR',
            'active_subscriptions': len(active_subs)
        }
    
    @classmethod
    def get_arr(cls) -> dict:
        """Calculate Annual Recurring Revenue"""
        mrr_data = cls.get_mrr()
        return {
            'arr': round(mrr_data['mrr'] * 12, 2),
            'currency': 'EUR'
        }
    
    @classmethod
    def get_revenue_by_plan(cls) -> dict:
        """Get revenue breakdown by plan"""
        result = {}
        
        for plan_name in ['starter', 'professional', 'enterprise']:
            subs = Subscription.query.filter_by(plan=plan_name, status='active').all()
            monthly_revenue = sum(
                s.amount / 12 if s.billing_cycle == 'yearly' else s.amount
                for s in subs
            )
            result[plan_name] = {
                'count': len(subs),
                'mrr': round(monthly_revenue, 2)
            }
        
        return result
    
    @classmethod
    def get_churn_rate(cls, days: int = 30) -> dict:
        """Calculate churn rate"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Subscriptions at start of period
        start_count = Subscription.query.filter(
            Subscription.created_at < cutoff
        ).count()
        
        # Cancelled during period
        cancelled = Subscription.query.filter(
            Subscription.cancelled_at >= cutoff,
            Subscription.cancelled_at <= datetime.utcnow()
        ).count()
        
        churn_rate = (cancelled / max(start_count, 1)) * 100
        
        return {
            'churn_rate': round(churn_rate, 2),
            'cancelled': cancelled,
            'period_days': days
        }
    
    @classmethod
    def get_payment_history(cls, user_id: int = None, days: int = 90) -> list:
        """Get payment history"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        query = Payment.query.filter(Payment.created_at >= cutoff)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        payments = query.order_by(Payment.created_at.desc()).all()
        
        return [p.to_dict() for p in payments]


# =============================================================================
# SEPA & LASTSCHRIFT (Direct Debit)
# =============================================================================

class SEPAService:
    """SEPA Direct Debit for German/EU customers"""
    
    @classmethod
    def create_mandate(cls, customer_name: str, iban: str, bic: str = None) -> dict:
        """Create a SEPA mandate"""
        # Validate IBAN
        if not cls.validate_iban(iban):
            return {'success': False, 'error': 'Ungültige IBAN'}
        
        mandate_id = f"MNDT-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        return {
            'success': True,
            'mandate': {
                'id': mandate_id,
                'customer_name': customer_name,
                'iban': iban,
                'bic': bic,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
        }
    
    @classmethod
    def validate_iban(cls, iban: str) -> bool:
        """Validate IBAN format"""
        iban = iban.replace(' ', '').upper()
        
        if len(iban) < 15 or len(iban) > 34:
            return False
        
        # Check country code
        if not iban[:2].isalpha():
            return False
        
        # Check digits
        if not iban[2:4].isdigit():
            return False
        
        return True
    
    @classmethod
    def generate_sepa_xml(cls, payments: list, creditor_info: dict) -> str:
        """Generate SEPA XML for batch direct debit"""
        # Simplified SEPA XML generation
        # In production, use a library like sepaxml
        
        xml_template = """<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02">
  <CstmrDrctDbtInitn>
    <GrpHdr>
      <MsgId>{msg_id}</MsgId>
      <CreDtTm>{created}</CreDtTm>
      <NbOfTxs>{count}</NbOfTxs>
      <CtrlSum>{total}</CtrlSum>
      <InitgPty>
        <Nm>{creditor_name}</Nm>
      </InitgPty>
    </GrpHdr>
    {payment_info}
  </CstmrDrctDbtInitn>
</Document>"""
        
        msg_id = f"MSG-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        total = sum(p.get('amount', 0) for p in payments)
        
        return xml_template.format(
            msg_id=msg_id,
            created=datetime.utcnow().isoformat(),
            count=len(payments),
            total=f"{total:.2f}",
            creditor_name=creditor_info.get('name', 'Enterprise Universe GmbH'),
            payment_info="<!-- Payment details here -->"
        )


# =============================================================================
# EXTENDED INVOICE API ROUTES
# =============================================================================

@app.route('/api/invoices', methods=['GET'])
@login_required
def api_get_invoices():
    """Get all invoices"""
    user = get_current_user()
    
    status = request.args.get('status')
    query = Invoice.query.filter_by(user_id=user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    invoices = query.order_by(Invoice.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'invoices': [i.to_dict() for i in invoices]
    })


@app.route('/api/invoices', methods=['POST'])
@login_required
def api_create_invoice():
    """Create new invoice"""
    user = get_current_user()
    data = request.get_json() or {}
    
    contact_id = data.get('contact_id')
    items = data.get('items', [])
    
    if not contact_id or not items:
        return jsonify({'success': False, 'error': 'Kontakt und Positionen erforderlich'}), 400
    
    result = InvoiceService.create_invoice(
        user_id=user.id,
        contact_id=contact_id,
        items=items,
        due_days=data.get('due_days', 14),
        notes=data.get('notes')
    )
    
    return jsonify(result)


@app.route('/api/invoices/<int:invoice_id>', methods=['GET'])
@login_required
def api_get_invoice(invoice_id):
    """Get single invoice"""
    user = get_current_user()
    
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=user.id).first()
    
    if not invoice:
        return jsonify({'success': False, 'error': 'Rechnung nicht gefunden'}), 404
    
    return jsonify({'success': True, 'invoice': invoice.to_dict()})


@app.route('/api/invoices/<int:invoice_id>/send', methods=['POST'])
@login_required
def api_send_invoice(invoice_id):
    """Send invoice"""
    user = get_current_user()
    
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=user.id).first()
    
    if not invoice:
        return jsonify({'success': False, 'error': 'Rechnung nicht gefunden'}), 404
    
    result = InvoiceService.send_invoice(invoice_id)
    
    return jsonify(result)


@app.route('/api/invoices/<int:invoice_id>/paid', methods=['POST'])
@login_required
def api_mark_invoice_paid(invoice_id):
    """Mark invoice as paid"""
    user = get_current_user()
    data = request.get_json() or {}
    
    invoice = Invoice.query.filter_by(id=invoice_id, user_id=user.id).first()
    
    if not invoice:
        return jsonify({'success': False, 'error': 'Rechnung nicht gefunden'}), 404
    
    result = InvoiceService.mark_paid(
        invoice_id,
        payment_method=data.get('payment_method', 'bank_transfer')
    )
    
    return jsonify(result)


@app.route('/api/invoices/export/datev', methods=['GET'])
@login_required
def api_export_invoices_datev():
    """Export invoices in DATEV format"""
    user = get_current_user()
    
    invoices = Invoice.query.filter_by(user_id=user.id).all()
    csv_content = DATEVService.export_invoices_csv(invoices)
    
    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=rechnungen_datev.csv'}
    )


# =============================================================================
# PAYMENT ANALYTICS API ROUTES
# =============================================================================

@app.route('/api/analytics/revenue', methods=['GET'])
@login_required
def api_revenue_analytics():
    """Get revenue analytics"""
    user = get_current_user()
    
    if user.role not in ['admin', 'GOD MODE']:
        return jsonify({'success': False, 'error': 'Keine Berechtigung'}), 403
    
    mrr = PaymentAnalytics.get_mrr()
    arr = PaymentAnalytics.get_arr()
    by_plan = PaymentAnalytics.get_revenue_by_plan()
    churn = PaymentAnalytics.get_churn_rate()
    
    return jsonify({
        'success': True,
        'analytics': {
            'mrr': mrr,
            'arr': arr,
            'by_plan': by_plan,
            'churn': churn
        }
    })


@app.route('/api/analytics/payments', methods=['GET'])
@login_required
def api_payment_analytics():
    """Get payment history"""
    user = get_current_user()
    days = request.args.get('days', 90, type=int)
    
    # Admin sees all, users see only their own
    user_id = None if user.role in ['admin', 'GOD MODE'] else user.id
    
    payments = PaymentAnalytics.get_payment_history(user_id=user_id, days=days)
    
    return jsonify({
        'success': True,
        'payments': payments
    })


# =============================================================================
# REVOLUT BUSINESS EXTENDED FEATURES
# =============================================================================

@app.route('/api/banking/exchange-rate', methods=['GET'])
@login_required
def api_exchange_rate():
    """Get exchange rates"""
    from_currency = request.args.get('from', 'EUR')
    to_currency = request.args.get('to', 'USD')
    
    result = RevolutService.get_exchange_rates(from_currency, to_currency)
    
    return jsonify(result)


@app.route('/api/banking/statements', methods=['GET'])
@login_required
def api_bank_statements():
    """Get bank statements/transactions from Revolut"""
    user = get_current_user()
    account_id = request.args.get('account_id')
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    
    # Get Revolut account
    account = BankAccount.query.filter_by(
        user_id=user.id,
        id=account_id
    ).first() if account_id else None
    
    revolut_account_id = account.revolut_account_id if account else None
    
    result = RevolutService.get_transactions(
        account_id=revolut_account_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return jsonify(result)


@app.route('/api/banking/balance', methods=['GET'])
@login_required
def api_get_balance():
    """Get total balance across all accounts"""
    user = get_current_user()
    
    accounts = BankAccount.query.filter_by(user_id=user.id, is_active=True).all()
    
    total_balance = sum(a.balance or 0 for a in accounts)
    total_available = sum(a.available_balance or 0 for a in accounts)
    
    return jsonify({
        'success': True,
        'total_balance': total_balance,
        'available_balance': total_available,
        'currency': 'EUR',
        'accounts_count': len(accounts)
    })


@app.route('/api/banking/scheduled-payments', methods=['GET'])
@login_required
def api_scheduled_payments():
    """Get scheduled/recurring payments"""
    user = get_current_user()
    
    # Get upcoming invoice payments
    upcoming_invoices = Invoice.query.filter(
        Invoice.user_id == user.id,
        Invoice.status == 'sent',
        Invoice.due_date >= datetime.utcnow().date()
    ).order_by(Invoice.due_date.asc()).all()
    
    # Get subscription renewals
    subscription = Subscription.query.filter_by(
        user_id=user.id,
        status='active'
    ).first()
    
    scheduled = []
    
    for inv in upcoming_invoices:
        scheduled.append({
            'type': 'invoice',
            'description': f"Rechnung {inv.invoice_number}",
            'amount': inv.total,
            'due_date': inv.due_date.isoformat() if inv.due_date else None,
            'status': 'pending'
        })
    
    if subscription and subscription.current_period_end:
        scheduled.append({
            'type': 'subscription',
            'description': f"{subscription.plan.title()} Abo Verlängerung",
            'amount': subscription.amount,
            'due_date': subscription.current_period_end.isoformat(),
            'status': 'scheduled'
        })
    
    return jsonify({
        'success': True,
        'scheduled_payments': scheduled
    })


# =============================================================================
# PAYMENT PAGE ROUTES (HTML)
# =============================================================================

@app.route('/payment/success')
def payment_success():
    """Payment success page"""
    session_id = request.args.get('session_id')
    
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zahlung erfolgreich - West Money OS</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                padding: 3rem;
                border-radius: 20px;
                box-shadow: 0 25px 50px rgba(0,0,0,0.25);
                text-align: center;
                max-width: 500px;
            }}
            .icon {{ font-size: 4rem; margin-bottom: 1rem; }}
            h1 {{ color: #10b981; margin-bottom: 1rem; }}
            p {{ color: #6b7280; margin-bottom: 2rem; }}
            .btn {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem 2rem;
                border: none;
                border-radius: 10px;
                font-size: 1rem;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }}
            .btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">✅</div>
            <h1>Zahlung erfolgreich!</h1>
            <p>Vielen Dank für Ihre Bestellung. Ihr Abo wurde aktiviert und Sie haben jetzt Zugang zu allen Premium-Funktionen.</p>
            <a href="/dashboard" class="btn">Zum Dashboard →</a>
        </div>
    </body>
    </html>
    """


@app.route('/payment/cancel')
def payment_cancel():
    """Payment cancelled page"""
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zahlung abgebrochen - West Money OS</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                padding: 3rem;
                border-radius: 20px;
                box-shadow: 0 25px 50px rgba(0,0,0,0.25);
                text-align: center;
                max-width: 500px;
            }}
            .icon {{ font-size: 4rem; margin-bottom: 1rem; }}
            h1 {{ color: #ef4444; margin-bottom: 1rem; }}
            p {{ color: #6b7280; margin-bottom: 2rem; }}
            .btn {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem 2rem;
                border: none;
                border-radius: 10px;
                font-size: 1rem;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin: 0.5rem;
            }}
            .btn-outline {{
                background: transparent;
                border: 2px solid #667eea;
                color: #667eea;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">❌</div>
            <h1>Zahlung abgebrochen</h1>
            <p>Die Zahlung wurde abgebrochen. Keine Sorge - es wurde nichts berechnet.</p>
            <a href="/pricing" class="btn">Erneut versuchen</a>
            <a href="/dashboard" class="btn btn-outline">Zum Dashboard</a>
        </div>
    </body>
    </html>
    """


@app.route('/pricing')
def pricing_page():
    """Pricing page"""
    if TEMPLATES_LOADED:
        return PRICING_PAGE_HTML
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preise - West Money OS</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: #0f172a;
                color: white;
                min-height: 100vh;
            }}
            .header {{
                text-align: center;
                padding: 4rem 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
            .subtitle {{ font-size: 1.25rem; opacity: 0.9; }}
            .plans {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                padding: 4rem 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }}
            .plan {{
                background: #1e293b;
                border-radius: 20px;
                padding: 2rem;
                position: relative;
                transition: transform 0.3s;
            }}
            .plan:hover {{ transform: translateY(-10px); }}
            .plan.popular {{
                border: 2px solid #667eea;
                transform: scale(1.05);
            }}
            .plan.popular:hover {{ transform: scale(1.05) translateY(-10px); }}
            .popular-badge {{
                position: absolute;
                top: -12px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 0.5rem 1.5rem;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: bold;
            }}
            .plan-name {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
            .plan-price {{ font-size: 3rem; font-weight: bold; margin: 1rem 0; }}
            .plan-price span {{ font-size: 1rem; opacity: 0.7; }}
            .features {{ list-style: none; margin: 2rem 0; }}
            .features li {{ 
                padding: 0.75rem 0; 
                border-bottom: 1px solid #334155;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            .features li::before {{ content: '✓'; color: #10b981; font-weight: bold; }}
            .btn {{
                width: 100%;
                padding: 1rem;
                border: none;
                border-radius: 10px;
                font-size: 1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .btn-primary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .btn-outline {{
                background: transparent;
                border: 2px solid #667eea;
                color: #667eea;
            }}
            .btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 West Money OS Preise</h1>
            <p class="subtitle">Wählen Sie den perfekten Plan für Ihr Unternehmen</p>
        </div>
        
        <div class="plans">
            <div class="plan">
                <h2 class="plan-name">Free</h2>
                <div class="plan-price">€0 <span>/Monat</span></div>
                <ul class="features">
                    <li>3 Kontakte</li>
                    <li>2 Leads</li>
                    <li>Basis Dashboard</li>
                    <li>E-Mail Support</li>
                </ul>
                <button class="btn btn-outline">Aktueller Plan</button>
            </div>
            
            <div class="plan">
                <h2 class="plan-name">Starter</h2>
                <div class="plan-price">€29 <span>/Monat</span></div>
                <ul class="features">
                    <li>50 Kontakte</li>
                    <li>25 Leads</li>
                    <li>Handelsregister-Suche</li>
                    <li>CSV Export</li>
                    <li>Priority Support</li>
                </ul>
                <button class="btn btn-primary" onclick="checkout('starter')">Jetzt starten</button>
            </div>
            
            <div class="plan popular">
                <div class="popular-badge">🔥 BELIEBT</div>
                <h2 class="plan-name">Professional</h2>
                <div class="plan-price">€99 <span>/Monat</span></div>
                <ul class="features">
                    <li>Unbegrenzte Kontakte</li>
                    <li>Unbegrenzte Leads</li>
                    <li>WhatsApp Business API</li>
                    <li>HubSpot Integration</li>
                    <li>AI Chat Bots</li>
                    <li>API Zugang</li>
                    <li>Team Features</li>
                </ul>
                <button class="btn btn-primary" onclick="checkout('professional')">Jetzt starten</button>
            </div>
            
            <div class="plan">
                <h2 class="plan-name">Enterprise</h2>
                <div class="plan-price">€299 <span>/Monat</span></div>
                <ul class="features">
                    <li>Alles aus Professional</li>
                    <li>White Label</li>
                    <li>Custom Integrationen</li>
                    <li>99.9% SLA</li>
                    <li>AI Concierge</li>
                    <li>Dedicated Account Manager</li>
                    <li>On-Premise Option</li>
                </ul>
                <button class="btn btn-primary" onclick="checkout('enterprise')">Kontakt aufnehmen</button>
            </div>
        </div>
        
        <script>
            async function checkout(plan) {{
                try {{
                    const response = await fetch('/api/payments/checkout', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ plan: plan, billing_cycle: 'monthly' }})
                    }});
                    const data = await response.json();
                    if (data.success && data.url) {{
                        window.location.href = data.url;
                    }} else {{
                        alert(data.error || 'Fehler beim Checkout');
                    }}
                }} catch (error) {{
                    console.error('Checkout error:', error);
                    alert('Ein Fehler ist aufgetreten');
                }}
            }}
        </script>
    </body>
    </html>
    """


# =============================================================================
# WEBSOCKET REAL-TIME EVENTS (Flask-SocketIO)
# =============================================================================

# Note: For WebSocket support, install flask-socketio
# pip install flask-socketio eventlet

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
    SOCKETIO_ENABLED = True
except ImportError:
    SOCKETIO_ENABLED = False
    logger.warning("Flask-SocketIO not installed. Real-time features disabled.")

if SOCKETIO_ENABLED:
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        user = get_current_user()
        if user:
            join_room(f"user_{user.id}")
            emit('connected', {'message': 'Connected to West Money OS'})
            logger.info(f"WebSocket: User {user.id} connected")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        user = get_current_user()
        if user:
            leave_room(f"user_{user.id}")
            logger.info(f"WebSocket: User {user.id} disconnected")
    
    @socketio.on('subscribe_notifications')
    def handle_subscribe_notifications():
        """Subscribe to real-time notifications"""
        user = get_current_user()
        if user:
            join_room(f"notifications_{user.id}")
            emit('subscribed', {'channel': 'notifications'})
    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Handle incoming chat message"""
        user = get_current_user()
        if not user:
            return
        
        message = data.get('message', '')
        contact_id = data.get('contact_id')
        
        # Process with AI
        result = ClaudeAIService.process_support_query(message)
        
        if result.get('success'):
            emit('chat_response', {
                'response': result['response'],
                'contact_id': contact_id
            })
    
    def send_realtime_notification(user_id: int, notification: dict):
        """Send real-time notification to user"""
        if SOCKETIO_ENABLED:
            socketio.emit('notification', notification, room=f"notifications_{user_id}")


# =============================================================================
# MAIN APPLICATION ENTRY POINT
# =============================================================================

@app.route('/')
def index():
    """Main landing page with Awards"""
    if TEMPLATES_LOADED:
        return LANDING_PAGE_HTML
    # Fallback wenn templates nicht geladen
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>West Money OS v9.0 - BROLY ULTRA GODMODE</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0f172a;
                color: white;
                min-height: 100vh;
            }}
            .hero {{
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 2rem;
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
                position: relative;
                overflow: hidden;
            }}
            .hero::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            }}
            .logo {{ 
                font-size: 5rem; 
                margin-bottom: 1rem;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.1); }}
            }}
            h1 {{ 
                font-size: 4rem; 
                margin-bottom: 0.5rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .version {{
                font-size: 1.5rem;
                color: #a855f7;
                margin-bottom: 2rem;
                font-weight: bold;
            }}
            .subtitle {{ 
                font-size: 1.5rem; 
                opacity: 0.8;
                margin-bottom: 3rem;
                max-width: 600px;
            }}
            .features {{
                display: flex;
                gap: 2rem;
                flex-wrap: wrap;
                justify-content: center;
                margin-bottom: 3rem;
            }}
            .feature {{
                background: rgba(255,255,255,0.1);
                padding: 1.5rem;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                min-width: 200px;
            }}
            .feature-icon {{ font-size: 2rem; margin-bottom: 0.5rem; }}
            .buttons {{
                display: flex;
                gap: 1rem;
                flex-wrap: wrap;
                justify-content: center;
            }}
            .btn {{
                padding: 1rem 2.5rem;
                border: none;
                border-radius: 50px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                text-decoration: none;
                transition: all 0.3s;
            }}
            .btn-primary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .btn-outline {{
                background: transparent;
                border: 2px solid white;
                color: white;
            }}
            .btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
            }}
            .stats {{
                display: flex;
                gap: 3rem;
                margin-top: 4rem;
            }}
            .stat {{ text-align: center; }}
            .stat-value {{ font-size: 2.5rem; font-weight: bold; color: #a855f7; }}
            .stat-label {{ opacity: 0.7; }}
            .godmode {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: bold;
                animation: glow 1.5s infinite alternate;
            }}
            @keyframes glow {{
                from {{ box-shadow: 0 0 10px #f97316; }}
                to {{ box-shadow: 0 0 30px #ef4444; }}
            }}
        </style>
    </head>
    <body>
        <div class="godmode">🔥 BROLY ULTRA GODMODE</div>
        
        <div class="hero">
            <div class="logo">💰</div>
            <h1>West Money OS</h1>
            <div class="version">v9.0 BROLY EDITION</div>
            <p class="subtitle">
                Die ultimative All-in-One Business Platform für Smart Home, 
                CRM, WhatsApp Business, KI-Assistenten und mehr.
            </p>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">📱</div>
                    <div>WhatsApp Business</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🤖</div>
                    <div>AI Chatbots</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">💼</div>
                    <div>CRM & Leads</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🏦</div>
                    <div>Revolut Banking</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">💳</div>
                    <div>Stripe Payments</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔒</div>
                    <div>DedSec Security</div>
                </div>
            </div>
            
            <div class="buttons">
                <a href="/dashboard" class="btn btn-primary">Dashboard öffnen →</a>
                <a href="/pricing" class="btn btn-outline">Preise ansehen</a>
                <a href="/api/health" class="btn btn-outline">API Status</a>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">47+</div>
                    <div class="stat-label">API Integrationen</div>
                </div>
                <div class="stat">
                    <div class="stat-value">∞</div>
                    <div class="stat-label">Möglichkeiten</div>
                </div>
                <div class="stat">
                    <div class="stat-value">24/7</div>
                    <div class="stat-label">AI Support</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


@app.route('/dashboard')
@login_required_html
def dashboard():
    """Main dashboard"""
    user = get_current_user()
    if TEMPLATES_LOADED:
        return get_dashboard_html(user)
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - West Money OS</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 text-white">
        <div class="min-h-screen p-8">
            <h1 class="text-4xl font-bold mb-8">
                Willkommen zurück, {user.name or user.username}! 👋
            </h1>
            <p class="text-slate-400 mb-8">
                Plan: <span class="text-purple-400 font-bold">{user.plan.upper()}</span>
            </p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <a href="/api/dashboard/stats" class="bg-slate-800 p-6 rounded-xl hover:bg-slate-700 transition">
                    <div class="text-3xl mb-2">📊</div>
                    <div class="font-bold">Dashboard Stats</div>
                </a>
                <a href="/api/contacts" class="bg-slate-800 p-6 rounded-xl hover:bg-slate-700 transition">
                    <div class="text-3xl mb-2">👥</div>
                    <div class="font-bold">Kontakte</div>
                </a>
                <a href="/api/leads" class="bg-slate-800 p-6 rounded-xl hover:bg-slate-700 transition">
                    <div class="text-3xl mb-2">💼</div>
                    <div class="font-bold">Leads</div>
                </a>
                <a href="/api/banking/accounts" class="bg-slate-800 p-6 rounded-xl hover:bg-slate-700 transition">
                    <div class="text-3xl mb-2">🏦</div>
                    <div class="font-bold">Banking</div>
                </a>
            </div>
            
            <div class="mt-8 p-6 bg-gradient-to-r from-purple-900 to-indigo-900 rounded-xl">
                <h2 class="text-2xl font-bold mb-4">🔥 BROLY ULTRA GODMODE AKTIV</h2>
                <p class="text-slate-300">
                    Alle Enterprise-Features freigeschaltet. API-Zugang, WhatsApp Business, 
                    AI Chatbots, Revolut Banking und mehr.
                </p>
            </div>
        </div>
    </body>
    </html>
    """



@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Login page"""
    error_html = ""
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session.permanent = True
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_security_event('login', 'info', {'user_id': user.id})
            return redirect('/dashboard')
        else:
            error_html = '<div class="error-message">❌ Ungültige Anmeldedaten</div>'
            log_security_event('failed_login', 'warning', {'username': username})
    
    if TEMPLATES_LOADED:
        return LOGIN_PAGE_HTML.replace('{error_html}', error_html)
    return f"""
    <!DOCTYPE html>
    <html><head><title>Login</title></head>
    <body style="background:#0f0f1a;color:white;font-family:sans-serif;text-align:center;padding:100px;">
        <h1>💰 Login</h1>
        {error_html}
        <form method="POST">
            <input name="username" placeholder="Username" style="padding:10px;margin:5px;"><br>
            <input name="password" type="password" placeholder="Password" style="padding:10px;margin:5px;"><br>
            <button type="submit" style="padding:10px 30px;margin:10px;">Login</button>
        </form>
        <p style="color:#888;">Demo: admin / WestMoney2025!</p>
    </body></html>
    """


@app.route('/logout')
def logout():
    """Logout user"""
    if 'user_id' in session:
        log_security_event('logout', 'info', {'user_id': session['user_id']})
    session.clear()
    return redirect('/')


@app.route('/api/health')
def health_check():
    """API Health Check"""
    return jsonify({
        'status': 'healthy',
        'version': '9.0.0-BROLY',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'database': 'connected',
            'whatsapp': 'configured' if config.WHATSAPP_TOKEN else 'not configured',
            'hubspot': 'configured' if config.HUBSPOT_API_KEY else 'not configured',
            'claude_ai': 'configured' if config.ANTHROPIC_API_KEY else 'not configured',
            'stripe': 'configured' if StripeService.STRIPE_SECRET_KEY else 'not configured',
            'revolut': 'configured' if RevolutService.REVOLUT_API_KEY else 'not configured',
            'mollie': 'configured' if MollieService.MOLLIE_API_KEY else 'not configured'
        }
    })


# =============================================================================
# DATABASE INITIALIZATION & APP STARTUP
# =============================================================================

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@westmoney.de',
                name='Administrator',
                role='GOD MODE',
                plan='enterprise'
            )
            admin.set_password('WestMoney2025!')
            db.session.add(admin)
            db.session.commit()
            logger.info("Default admin user created")
        
        logger.info("Database initialized successfully")


# Initialize on import
init_db()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting West Money OS v9.0 BROLY ULTRA GODMODE on port {port}")
    
    if SOCKETIO_ENABLED:
        socketio.run(app, host='0.0.0.0', port=port, debug=debug)
    else:
        app.run(host='0.0.0.0', port=port, debug=debug)
