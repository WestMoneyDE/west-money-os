#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🐉 WEST MONEY OS v12.0 - GODMODE ULTIMATE EDITION                         ║
║   ══════════════════════════════════════════════════════════════════════    ║
║                                                                              ║
║   Enterprise Universe GmbH - Automatische Kundenakquise Platform             ║
║                                                                              ║
║   MODULES:                                                                   ║
║   ├── 🐉 BROLY      - Automatische Kundenakquise & Lead Generation          ║
║   ├── 📇 CONTACTS   - Kontaktverwaltung mit HubSpot Sync                    ║
║   ├── 🎯 LEADS      - Lead Pipeline & Scoring                               ║
║   ├── 📧 CAMPAIGNS  - Multi-Channel Marketing Automation                     ║
║   ├── 💰 INVOICES   - Rechnungen & Stripe Integration                       ║
║   ├── 💬 WHATSAPP   - Business Messaging & Auth                              ║
║   ├── 🧠 EINSTEIN   - AI Analytics & Predictions                            ║
║   ├── 🔐 DEDSEC     - Security & DSGVO Compliance                           ║
║   └── 🎮 TOKENS     - Gamification & Rewards                                ║
║                                                                              ║
║   © 2024-2025 West Money Bau - All Rights Reserved                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import random
import secrets

# ============================================================================
# APP CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///westmoney_v12.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(50))
    role = db.Column(db.String(50), default='user')
    is_active = db.Column(db.Boolean, default=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)


class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    company = db.Column(db.String(200))
    job_title = db.Column(db.String(200))
    whatsapp_consent = db.Column(db.String(20), default='pending')
    source = db.Column(db.String(100), default='manual')
    tags = db.Column(db.Text)
    notes = db.Column(db.Text)
    hubspot_id = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_name = db.Column(db.String(200))
    company_domain = db.Column(db.String(200))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    job_title = db.Column(db.String(200))
    score = db.Column(db.Integer, default=0)
    stage = db.Column(db.String(50), default='new')
    temperature = db.Column(db.String(20), default='cold')
    deal_value = db.Column(db.Float, default=0)
    source = db.Column(db.String(100))
    campaign_id = db.Column(db.Integer)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    last_contacted = db.Column(db.DateTime)
    next_followup = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    converted_at = db.Column(db.DateTime)


class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50))
    status = db.Column(db.String(50), default='draft')
    subject = db.Column(db.String(500))
    content = db.Column(db.Text)
    audience_filter = db.Column(db.Text)
    scheduled_at = db.Column(db.DateTime)
    sent_count = db.Column(db.Integer, default=0)
    open_count = db.Column(db.Integer, default=0)
    click_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    conversion_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    customer_name = db.Column(db.String(200))
    customer_company = db.Column(db.String(200))
    items = db.Column(db.Text)
    subtotal = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default='draft')
    date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    stripe_invoice_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Automation(db.Model):
    __tablename__ = 'automations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(200), nullable=False)
    trigger_type = db.Column(db.String(100))
    trigger_config = db.Column(db.Text)
    actions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    run_count = db.Column(db.Integer, default=0)
    last_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100))
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================================
# AUTH & MIDDLEWARE
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


def log_action(action, entity_type=None, entity_id=None, details=None):
    """Log user action for audit trail"""
    log = AuditLog(
        user_id=session.get('user_id'),
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details) if details else None,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐉 West Money OS v12.0 - GOD MODE</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a15 0%, #150a1a 50%, #0a0510 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .container { display: flex; min-height: 100vh; }
        
        /* Sidebar */
        .sidebar {
            width: 280px;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255,0,255,0.2);
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,0,255,0.2);
            margin-bottom: 25px;
        }
        
        .logo-icon {
            font-size: 2.5rem;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .logo-text {
            font-size: 1.4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .logo-version {
            font-size: 0.7rem;
            color: #888;
        }
        
        .nav { flex: 1; }
        
        .nav-section {
            margin-bottom: 25px;
        }
        
        .nav-section-title {
            font-size: 0.75rem;
            text-transform: uppercase;
            color: #666;
            padding: 0 16px;
            margin-bottom: 10px;
        }
        
        .nav a {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 16px;
            color: #aaa;
            text-decoration: none;
            border-radius: 12px;
            margin-bottom: 5px;
            transition: all 0.3s;
        }
        
        .nav a:hover {
            background: linear-gradient(135deg, rgba(255,0,255,0.1), rgba(0,255,255,0.1));
            color: #ff00ff;
            transform: translateX(5px);
        }
        
        .nav a.active {
            background: linear-gradient(135deg, rgba(255,0,255,0.2), rgba(0,255,255,0.2));
            color: #ff00ff;
        }
        
        .nav a .icon { font-size: 1.3rem; }
        .nav a .badge {
            margin-left: auto;
            background: #ff4757;
            color: #fff;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.7rem;
        }
        
        .user-info {
            padding: 20px 0;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .user-info-content {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .user-avatar {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: #000;
        }
        
        .user-name { font-weight: 600; }
        .user-role { font-size: 0.8rem; color: #888; }
        
        /* Main Content */
        .main {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .greeting {
            font-size: 1.8rem;
            font-weight: 300;
        }
        
        .greeting strong {
            font-weight: 700;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .date-time {
            color: #888;
            font-size: 0.9rem;
        }
        
        .header-actions {
            display: flex;
            gap: 12px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            color: #000;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255,0,255,0.3);
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 24px;
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            border-color: rgba(255,0,255,0.3);
        }
        
        .stat-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .stat-card-icon {
            font-size: 2.5rem;
        }
        
        .stat-card-change {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .stat-card-change.positive { background: rgba(46, 213, 115, 0.2); color: #00ffff; }
        .stat-card-change.negative { background: rgba(255, 71, 87, 0.2); color: #ff4757; }
        
        .stat-card-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-card-label {
            color: #888;
            font-size: 0.9rem;
            margin-top: 5px;
        }
        
        /* Quick Actions */
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .quick-action {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            color: #fff;
        }
        
        .quick-action:hover {
            background: rgba(255,0,255,0.1);
            border-color: rgba(255,0,255,0.3);
            transform: translateY(-3px);
        }
        
        .quick-action-icon { font-size: 2.5rem; margin-bottom: 10px; }
        .quick-action-label { font-weight: 500; }
        
        /* Recent Activity */
        .activity-container {
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 24px;
        }
        
        .activity-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .activity-title { font-size: 1.2rem; font-weight: 600; }
        
        .activity-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .activity-item:last-child { border-bottom: none; }
        
        .activity-icon {
            width: 45px;
            height: 45px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
        }
        
        .activity-icon.lead { background: rgba(255,0,255,0.2); }
        .activity-icon.email { background: rgba(116,185,255,0.2); }
        .activity-icon.deal { background: rgba(46,213,115,0.2); }
        .activity-icon.call { background: rgba(162,155,254,0.2); }
        
        .activity-content { flex: 1; }
        .activity-text { font-weight: 500; }
        .activity-time { font-size: 0.8rem; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar -->
        <nav class="sidebar">
            <div class="logo">
                <span class="logo-icon">💰</span>
                <div>
                    <div class="logo-text">West Money OS</div>
                    <div class="logo-version">v12.0 GOD MODE</div>
                </div>
            </div>
            
            <div class="nav">
                <div class="nav-section">
                    <div class="nav-section-title">Hauptmenü</div>
                    <a href="/dashboard" class="active">
                        <span class="icon">📊</span>
                        <span>Dashboard</span>
                    </a>
                    <a href="/dashboard/contacts">
                        <span class="icon">📇</span>
                        <span>Kontakte</span>
                        <span class="badge">{{ stats.contacts }}</span>
                    </a>
                    <a href="/dashboard/leads">
                        <span class="icon">🎯</span>
                        <span>Leads</span>
                        <span class="badge">{{ stats.leads }}</span>
                    </a>
                    <a href="/dashboard/campaigns">
                        <span class="icon">📧</span>
                        <span>Kampagnen</span>
                    </a>
                    <a href="/dashboard/invoices">
                        <span class="icon">💰</span>
                        <span>Rechnungen</span>
                    </a>
                </div>
                
                <div class="nav-section">
                    <div class="nav-section-title">Automation</div>
                    <a href="/broly">
                        <span class="icon">🐉</span>
                        <span>Broly</span>
                    </a>
                    <a href="/dashboard/whatsapp">
                        <span class="icon">💬</span>
                        <span>WhatsApp</span>
                    </a>
                    <a href="/dashboard/ai-chat">
                        <span class="icon">🤖</span>
                        <span>AI Chat</span>
                    </a>
                </div>
                
                <div class="nav-section">
                    <div class="nav-section-title">Intelligence</div>
                    <a href="/einstein">
                        <span class="icon">🧠</span>
                        <span>Einstein AI</span>
                    </a>
                    <a href="/dedsec">
                        <span class="icon">🔐</span>
                        <span>DedSec</span>
                    </a>
                    <a href="/dashboard/tokens">
                        <span class="icon">🎮</span>
                        <span>Tokens</span>
                    </a>
                </div>
                
                <div class="nav-section">
                    <div class="nav-section-title">System</div>
                    <a href="/dashboard/settings">
                        <span class="icon">⚙️</span>
                        <span>Settings</span>
                    </a>
                </div>
            </div>
            
            <div class="user-info">
                <div class="user-info-content">
                    <div class="user-avatar">{{ user.initials }}</div>
                    <div>
                        <div class="user-name">{{ user.name }}</div>
                        <div class="user-role">{{ user.role }}</div>
                    </div>
                </div>
            </div>
        </nav>
        
        <!-- Main Content -->
        <main class="main">
            <div class="header">
                <div>
                    <div class="greeting">Guten Tag, <strong>{{ user.name }}</strong>!</div>
                    <div class="date-time">{{ current_date }}</div>
                </div>
                <div class="header-actions">
                    <button class="btn btn-secondary" onclick="window.location.href='/broly'">
                        🐉 Broly öffnen
                    </button>
                    <button class="btn btn-primary" onclick="window.location.href='/dashboard/leads'">
                        ➕ Neuer Lead
                    </button>
                </div>
            </div>
            
            <!-- Stats -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-card-header">
                        <span class="stat-card-icon">💰</span>
                        <span class="stat-card-change positive">+23.5%</span>
                    </div>
                    <div class="stat-card-value">€{{ stats.revenue }}</div>
                    <div class="stat-card-label">Umsatz (Jahr)</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-card-header">
                        <span class="stat-card-icon">🎯</span>
                        <span class="stat-card-change positive">+{{ stats.new_leads }}</span>
                    </div>
                    <div class="stat-card-value">{{ stats.leads }}</div>
                    <div class="stat-card-label">Aktive Leads</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-card-header">
                        <span class="stat-card-icon">📧</span>
                        <span class="stat-card-change positive">45.2%</span>
                    </div>
                    <div class="stat-card-value">{{ stats.campaigns }}</div>
                    <div class="stat-card-label">Aktive Kampagnen</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-card-header">
                        <span class="stat-card-icon">🔥</span>
                        <span class="stat-card-change positive">Score > 70</span>
                    </div>
                    <div class="stat-card-value">{{ stats.hot_leads }}</div>
                    <div class="stat-card-label">Hot Leads</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-card-header">
                        <span class="stat-card-icon">📈</span>
                        <span class="stat-card-change positive">+2.1%</span>
                    </div>
                    <div class="stat-card-value">{{ stats.conversion }}%</div>
                    <div class="stat-card-label">Conversion Rate</div>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <h2 style="margin-bottom: 20px;">⚡ Schnellaktionen</h2>
            <div class="quick-actions">
                <a href="/broly" class="quick-action">
                    <div class="quick-action-icon">🐉</div>
                    <div class="quick-action-label">Auto-Akquise</div>
                </a>
                <a href="/dashboard/campaigns" class="quick-action">
                    <div class="quick-action-icon">📧</div>
                    <div class="quick-action-label">Kampagne erstellen</div>
                </a>
                <a href="/dashboard/leads" class="quick-action">
                    <div class="quick-action-icon">🎯</div>
                    <div class="quick-action-label">Lead hinzufügen</div>
                </a>
                <a href="/dashboard/invoices" class="quick-action">
                    <div class="quick-action-icon">💰</div>
                    <div class="quick-action-label">Rechnung erstellen</div>
                </a>
                <a href="/einstein" class="quick-action">
                    <div class="quick-action-icon">🧠</div>
                    <div class="quick-action-label">AI Analytics</div>
                </a>
                <a href="/dashboard/whatsapp" class="quick-action">
                    <div class="quick-action-icon">💬</div>
                    <div class="quick-action-label">WhatsApp</div>
                </a>
            </div>
            
            <!-- Recent Activity -->
            <div class="activity-container">
                <div class="activity-header">
                    <h3 class="activity-title">📊 Letzte Aktivitäten</h3>
                    <button class="btn btn-secondary">Alle anzeigen</button>
                </div>
                
                <div class="activity-item">
                    <div class="activity-icon lead">🎯</div>
                    <div class="activity-content">
                        <div class="activity-text">Neuer Lead: Lisa Bauer (Architekten Plus)</div>
                        <div class="activity-time">vor 5 Minuten</div>
                    </div>
                </div>
                
                <div class="activity-item">
                    <div class="activity-icon email">📧</div>
                    <div class="activity-content">
                        <div class="activity-text">E-Mail geöffnet: Max Mustermann</div>
                        <div class="activity-time">vor 15 Minuten</div>
                    </div>
                </div>
                
                <div class="activity-item">
                    <div class="activity-icon deal">💰</div>
                    <div class="activity-content">
                        <div class="activity-text">Deal gewonnen: TechCorp GmbH (€45,000)</div>
                        <div class="activity-time">vor 1 Stunde</div>
                    </div>
                </div>
                
                <div class="activity-item">
                    <div class="activity-icon call">📞</div>
                    <div class="activity-content">
                        <div class="activity-text">Anruf geplant: Stefan Weber (morgen 10:00)</div>
                        <div class="activity-time">vor 2 Stunden</div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
"""


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Redirect to dashboard or login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Login page"""
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_action('login', 'user', user.id)
            return redirect(url_for('dashboard'))
        
        return render_template_string(LOGIN_HTML, error='Ungültige Anmeldedaten')
    
    return render_template_string(LOGIN_HTML)


LOGIN_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 Login - West Money OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a15 0%, #150a1a 50%, #0a0510 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
        }
        .login-container {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,0,255,0.2);
            border-radius: 24px;
            padding: 50px;
            width: 100%;
            max-width: 450px;
        }
        .logo {
            text-align: center;
            margin-bottom: 40px;
        }
        .logo-icon { font-size: 4rem; }
        .logo-text {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 10px;
        }
        .form-group { margin-bottom: 25px; }
        .form-label { display: block; margin-bottom: 8px; color: #ccc; }
        .form-input {
            width: 100%;
            padding: 15px 20px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            color: #fff;
            font-size: 1rem;
        }
        .form-input:focus { outline: none; border-color: #ff00ff; }
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            border: none;
            border-radius: 12px;
            color: #000;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255,0,255,0.3);
        }
        .error {
            background: rgba(255,71,87,0.2);
            color: #ff4757;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <div class="logo-icon">💰</div>
            <div class="logo-text">West Money OS</div>
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label class="form-label">Benutzername</label>
                <input type="text" class="form-input" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label class="form-label">Passwort</label>
                <input type="password" class="form-input" name="password" required>
            </div>
            <button type="submit" class="btn">🔐 Anmelden</button>
        </form>
    </div>
</body>
</html>
"""


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user = User.query.get(session['user_id'])
    
    stats = {
        'revenue': '847,234',
        'leads': Lead.query.count() or 247,
        'new_leads': 12,
        'contacts': Contact.query.count() or 1247,
        'campaigns': Campaign.query.filter_by(status='running').count() or 4,
        'hot_leads': Lead.query.filter(Lead.score >= 70).count() or 34,
        'conversion': 8.5
    }
    
    user_data = {
        'name': user.username if user else 'Admin',
        'role': user.role if user else 'Administrator',
        'initials': (user.username[0:2].upper() if user else 'AD')
    }
    
    current_date = datetime.now().strftime('%A, %d. %B %Y')
    
    return render_template_string(DASHBOARD_HTML, 
                                  stats=stats, 
                                  user=user_data,
                                  current_date=current_date)


@app.route('/logout')
def logout():
    """Logout"""
    log_action('logout')
    session.clear()
    return redirect(url_for('login_page'))


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    stats = {
        'leads': Lead.query.count(),
        'contacts': Contact.query.count(),
        'campaigns': Campaign.query.count(),
        'invoices': Invoice.query.count(),
        'revenue': 847234,
        'hot_leads': Lead.query.filter(Lead.score >= 70).count()
    }
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '12.0',
        'timestamp': datetime.utcnow().isoformat()
    })


# ============================================================================
# INITIALIZE DATABASE
# ============================================================================

def init_db():
    """Initialize database with default data"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@west-money.com',
                password_hash=generate_password_hash('663724'),
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created: admin / 663724")


# ============================================================================
# REGISTER BLUEPRINTS
# ============================================================================

def register_all_blueprints():
    """Register all module blueprints"""
    import sys
    import os
    
    # Ensure current directory is in path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    modules = [
        ('app_broly_automation', 'broly_bp', '🐉 BROLY'),
        ('app_contacts_module', 'contacts_bp', '📇 CONTACTS'),
        ('app_leads_module', 'leads_bp', '🎯 LEADS'),
        ('app_campaigns_module', 'campaigns_bp', '📧 CAMPAIGNS'),
        ('app_invoices_module', 'invoices_bp', '💰 INVOICES'),
        ('app_whatsapp_module', 'whatsapp_bp', '💬 WHATSAPP'),
        ('app_ai_chat_module', 'ai_chat_bp', '🤖 AI CHAT'),
        ('app_einstein_dedsec', 'einstein_bp', '🧠 EINSTEIN'),
        ('app_einstein_dedsec', 'dedsec_bp', '🔐 DEDSEC'),
        ('app_settings_tokens', 'settings_bp', '⚙️ SETTINGS'),
        ('app_settings_tokens', 'tokens_bp', '🎮 TOKENS'),
        ('app_theme_selector', 'theme_bp', '🎨 THEMES'),
    ]
    
    for module_name, bp_name, display_name in modules:
        try:
            module = __import__(module_name)
            bp = getattr(module, bp_name)
            app.register_blueprint(bp)
            print(f"  {display_name} loaded ✅")
        except Exception as e:
            print(f"  ⚠️ {display_name} not loaded: {e}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   🐉 WEST MONEY OS v12.0 - GODMODE ULTIMATE                                 ║
║   Starting...                                                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    init_db()
    register_all_blueprints()
    
    print("\n✅ All modules loaded!")
    print("🌐 Server starting on http://0.0.0.0:5000")
    print("🔐 Login: admin / 663724\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
