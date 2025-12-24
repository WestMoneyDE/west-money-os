"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🐉 BROLY AUTOMATION - WEST MONEY OS v12.0                                   ║
║  Automatische Kundenakquise & Kampagnen-System                               ║
║  Enterprise Universe GmbH - GOD MODE ULTIMATE                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Blueprint, render_template_string, request, jsonify, session
from datetime import datetime, timedelta
from functools import wraps
import json
import random
import hashlib

broly_bp = Blueprint('broly', __name__)

# ============================================================================
# DATABASE MODELS - Erweitert für Broly Automation
# ============================================================================

BROLY_MODELS = """
# Füge zu deinen Models hinzu:

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    
    # Lead Info
    company_name = db.Column(db.String(200))
    company_domain = db.Column(db.String(200))
    company_size = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    
    # Contact Info
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    linkedin_url = db.Column(db.String(300))
    job_title = db.Column(db.String(200))
    
    # Scoring & Status
    score = db.Column(db.Integer, default=0)  # 0-100
    stage = db.Column(db.String(50), default='new')  # new, contacted, qualified, proposal, won, lost
    temperature = db.Column(db.String(20), default='cold')  # cold, warm, hot
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Source & Attribution
    source = db.Column(db.String(100))  # explorium, hubspot, manual, website, referral
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(100))
    
    # Assignment
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted = db.Column(db.DateTime)
    next_followup = db.Column(db.DateTime)
    converted_at = db.Column(db.DateTime)
    
    # Intent & Engagement
    intent_score = db.Column(db.Integer, default=0)
    engagement_score = db.Column(db.Integer, default=0)
    website_visits = db.Column(db.Integer, default=0)
    email_opens = db.Column(db.Integer, default=0)
    email_clicks = db.Column(db.Integer, default=0)
    
    # Notes
    notes = db.Column(db.Text)
    tags = db.Column(db.Text)  # JSON array
    custom_fields = db.Column(db.Text)  # JSON object
    
    # External IDs
    hubspot_id = db.Column(db.String(50))
    explorium_id = db.Column(db.String(50))


class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Campaign Info
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50))  # email, whatsapp, sms, multi_channel, automation
    status = db.Column(db.String(50), default='draft')  # draft, scheduled, running, paused, completed
    
    # Targeting
    audience_filter = db.Column(db.Text)  # JSON filter criteria
    audience_count = db.Column(db.Integer, default=0)
    
    # Content
    subject = db.Column(db.String(500))
    content = db.Column(db.Text)
    template_id = db.Column(db.Integer)
    
    # Scheduling
    scheduled_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Automation Settings
    is_automation = db.Column(db.Boolean, default=False)
    automation_trigger = db.Column(db.String(100))  # new_lead, score_change, time_delay
    automation_conditions = db.Column(db.Text)  # JSON
    automation_actions = db.Column(db.Text)  # JSON
    
    # Sequence Settings
    is_sequence = db.Column(db.Boolean, default=False)
    sequence_steps = db.Column(db.Text)  # JSON array of steps
    
    # Stats
    sent_count = db.Column(db.Integer, default=0)
    delivered_count = db.Column(db.Integer, default=0)
    open_count = db.Column(db.Integer, default=0)
    click_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    bounce_count = db.Column(db.Integer, default=0)
    unsubscribe_count = db.Column(db.Integer, default=0)
    conversion_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CampaignEvent(db.Model):
    __tablename__ = 'campaign_events'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    
    event_type = db.Column(db.String(50))  # sent, delivered, opened, clicked, replied, bounced, unsubscribed, converted
    channel = db.Column(db.String(50))  # email, whatsapp, sms
    
    metadata = db.Column(db.Text)  # JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Automation(db.Model):
    __tablename__ = 'automations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Trigger
    trigger_type = db.Column(db.String(100))  # new_lead, score_threshold, tag_added, form_submit, webhook
    trigger_config = db.Column(db.Text)  # JSON
    
    # Conditions
    conditions = db.Column(db.Text)  # JSON array of conditions
    
    # Actions
    actions = db.Column(db.Text)  # JSON array of actions
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    run_count = db.Column(db.Integer, default=0)
    last_run = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LeadActivity(db.Model):
    __tablename__ = 'lead_activities'
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    activity_type = db.Column(db.String(50))  # note, call, email, meeting, task, status_change
    description = db.Column(db.Text)
    metadata = db.Column(db.Text)  # JSON
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Template(db.Model):
    __tablename__ = 'templates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50))  # email, whatsapp, sms
    category = db.Column(db.String(100))  # outreach, followup, proposal, reminder
    
    subject = db.Column(db.String(500))
    content = db.Column(db.Text)
    
    # Personalization
    variables = db.Column(db.Text)  # JSON array of variables used
    
    # Stats
    use_count = db.Column(db.Integer, default=0)
    avg_open_rate = db.Column(db.Float, default=0)
    avg_reply_rate = db.Column(db.Float, default=0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
"""


# ============================================================================
# BROLY AUTOMATION DASHBOARD
# ============================================================================

BROLY_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐉 BROLY AUTOMATION - West Money OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .broly-container {
            display: flex;
            min-height: 100vh;
        }
        
        /* Sidebar */
        .broly-sidebar {
            width: 280px;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255,215,0,0.2);
            padding: 20px;
        }
        
        .broly-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,215,0,0.2);
            margin-bottom: 20px;
        }
        
        .broly-logo-icon {
            font-size: 2.5rem;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .broly-logo-text {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffd700, #ff6b35);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .broly-nav a {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 16px;
            color: #aaa;
            text-decoration: none;
            border-radius: 12px;
            margin-bottom: 8px;
            transition: all 0.3s;
        }
        
        .broly-nav a:hover, .broly-nav a.active {
            background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,107,53,0.2));
            color: #ffd700;
            transform: translateX(5px);
        }
        
        .broly-nav a .icon { font-size: 1.3rem; }
        
        /* Main Content */
        .broly-main {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }
        
        .broly-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .broly-title {
            font-size: 2rem;
            font-weight: 700;
        }
        
        .broly-actions {
            display: flex;
            gap: 12px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #ffd700, #ff6b35);
            color: #000;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255,215,0,0.3);
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #ff4757, #ff3838);
            color: #fff;
        }
        
        .btn-success {
            background: linear-gradient(135deg, #2ed573, #1e90ff);
            color: #fff;
        }
        
        /* Stats Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            border-color: rgba(255,215,0,0.3);
        }
        
        .stat-card .icon {
            font-size: 2rem;
            margin-bottom: 12px;
        }
        
        .stat-card .value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffd700, #ff6b35);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-card .label {
            color: #888;
            font-size: 0.9rem;
            margin-top: 5px;
        }
        
        .stat-card .change {
            font-size: 0.85rem;
            margin-top: 8px;
        }
        
        .stat-card .change.positive { color: #2ed573; }
        .stat-card .change.negative { color: #ff4757; }
        
        /* Pipeline */
        .pipeline-container {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
        }
        
        .pipeline-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .pipeline-stages {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 15px;
        }
        
        .pipeline-stage {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 16px;
            min-height: 300px;
        }
        
        .pipeline-stage-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid;
        }
        
        .stage-new { border-color: #74b9ff; }
        .stage-contacted { border-color: #a29bfe; }
        .stage-qualified { border-color: #ffeaa7; }
        .stage-proposal { border-color: #fd79a8; }
        .stage-won { border-color: #2ed573; }
        .stage-lost { border-color: #ff4757; }
        
        .pipeline-stage-name {
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .pipeline-stage-count {
            background: rgba(255,255,255,0.2);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        
        .lead-card {
            background: rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .lead-card:hover {
            background: rgba(255,255,255,0.12);
            transform: translateY(-2px);
        }
        
        .lead-card-name {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .lead-card-company {
            font-size: 0.85rem;
            color: #888;
            margin-bottom: 8px;
        }
        
        .lead-card-score {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .score-hot { background: #ff4757; color: #fff; }
        .score-warm { background: #ffa502; color: #000; }
        .score-cold { background: #74b9ff; color: #000; }
        
        /* Campaigns Table */
        .campaigns-container {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
        }
        
        .campaigns-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .campaigns-table th,
        .campaigns-table td {
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .campaigns-table th {
            color: #888;
            font-weight: 500;
            font-size: 0.85rem;
            text-transform: uppercase;
        }
        
        .campaigns-table tr:hover {
            background: rgba(255,255,255,0.05);
        }
        
        .campaign-status {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .status-running { background: #2ed573; color: #000; }
        .status-paused { background: #ffa502; color: #000; }
        .status-draft { background: #636e72; color: #fff; }
        .status-completed { background: #74b9ff; color: #000; }
        
        /* Automation Cards */
        .automation-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .automation-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s;
        }
        
        .automation-card:hover {
            border-color: rgba(255,215,0,0.3);
            transform: translateY(-3px);
        }
        
        .automation-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .automation-card-title {
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .automation-card-trigger {
            font-size: 0.85rem;
            color: #888;
            margin-top: 5px;
        }
        
        .automation-toggle {
            position: relative;
            width: 50px;
            height: 26px;
        }
        
        .automation-toggle input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .automation-toggle .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255,255,255,0.2);
            border-radius: 26px;
            transition: 0.3s;
        }
        
        .automation-toggle .slider:before {
            position: absolute;
            content: "";
            height: 20px;
            width: 20px;
            left: 3px;
            bottom: 3px;
            background: #fff;
            border-radius: 50%;
            transition: 0.3s;
        }
        
        .automation-toggle input:checked + .slider {
            background: linear-gradient(135deg, #2ed573, #1e90ff);
        }
        
        .automation-toggle input:checked + .slider:before {
            transform: translateX(24px);
        }
        
        .automation-card-stats {
            display: flex;
            gap: 20px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .automation-stat {
            text-align: center;
        }
        
        .automation-stat-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: #ffd700;
        }
        
        .automation-stat-label {
            font-size: 0.75rem;
            color: #888;
        }
        
        /* Modal */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal-overlay.active { display: flex; }
        
        .modal {
            background: #1a1a2e;
            border: 1px solid rgba(255,215,0,0.3);
            border-radius: 20px;
            width: 90%;
            max-width: 800px;
            max-height: 90vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .modal-title {
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        .modal-close {
            background: none;
            border: none;
            color: #888;
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        .modal-body { padding: 24px; }
        
        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            padding: 24px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Form Elements */
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #ccc;
        }
        
        .form-input {
            width: 100%;
            padding: 14px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: #fff;
            font-size: 1rem;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #ffd700;
        }
        
        .form-select {
            width: 100%;
            padding: 14px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: #fff;
            font-size: 1rem;
        }
        
        .form-textarea {
            width: 100%;
            padding: 14px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: #fff;
            font-size: 1rem;
            min-height: 150px;
            resize: vertical;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 10px;
        }
        
        .tab {
            padding: 10px 20px;
            background: none;
            border: none;
            color: #888;
            font-size: 1rem;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.3s;
        }
        
        .tab:hover { color: #fff; }
        
        .tab.active {
            background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,107,53,0.2));
            color: #ffd700;
        }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* Sequence Builder */
        .sequence-builder {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 20px;
        }
        
        .sequence-step {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .sequence-step-number {
            width: 30px;
            height: 30px;
            background: linear-gradient(135deg, #ffd700, #ff6b35);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: #000;
        }
        
        .sequence-step-content { flex: 1; }
        
        .sequence-step-type {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .sequence-step-delay {
            font-size: 0.85rem;
            color: #888;
        }
        
        .sequence-connector {
            width: 2px;
            height: 30px;
            background: linear-gradient(to bottom, #ffd700, transparent);
            margin-left: 29px;
        }
        
        /* Quick Actions */
        .quick-actions {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }
        
        .quick-action-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
            flex: 1;
            min-width: 150px;
        }
        
        .quick-action-card:hover {
            background: rgba(255,215,0,0.1);
            border-color: rgba(255,215,0,0.3);
            transform: translateY(-3px);
        }
        
        .quick-action-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
        
        .quick-action-label {
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="broly-container">
        <!-- Sidebar -->
        <nav class="broly-sidebar">
            <div class="broly-logo">
                <span class="broly-logo-icon">🐉</span>
                <span class="broly-logo-text">BROLY</span>
            </div>
            
            <div class="broly-nav">
                <a href="#dashboard" class="active" onclick="showSection('dashboard')">
                    <span class="icon">📊</span>
                    <span>Dashboard</span>
                </a>
                <a href="#leads" onclick="showSection('leads')">
                    <span class="icon">🎯</span>
                    <span>Leads</span>
                </a>
                <a href="#campaigns" onclick="showSection('campaigns')">
                    <span class="icon">📧</span>
                    <span>Kampagnen</span>
                </a>
                <a href="#automations" onclick="showSection('automations')">
                    <span class="icon">⚡</span>
                    <span>Automationen</span>
                </a>
                <a href="#sequences" onclick="showSection('sequences')">
                    <span class="icon">🔄</span>
                    <span>Sequenzen</span>
                </a>
                <a href="#templates" onclick="showSection('templates')">
                    <span class="icon">📝</span>
                    <span>Templates</span>
                </a>
                <a href="#integrations" onclick="showSection('integrations')">
                    <span class="icon">🔗</span>
                    <span>Integrationen</span>
                </a>
                <a href="#analytics" onclick="showSection('analytics')">
                    <span class="icon">📈</span>
                    <span>Analytics</span>
                </a>
                <a href="/dashboard">
                    <span class="icon">🏠</span>
                    <span>Zurück zu OS</span>
                </a>
            </div>
        </nav>
        
        <!-- Main Content -->
        <main class="broly-main">
            <!-- Dashboard Section -->
            <section id="section-dashboard" class="section active">
                <div class="broly-header">
                    <h1 class="broly-title">🐉 Broly Command Center</h1>
                    <div class="broly-actions">
                        <button class="btn btn-secondary" onclick="syncAllData()">
                            🔄 Sync All
                        </button>
                        <button class="btn btn-primary" onclick="openModal('new-lead')">
                            ➕ Neuer Lead
                        </button>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="quick-actions">
                    <div class="quick-action-card" onclick="startQuickCampaign('whatsapp')">
                        <div class="quick-action-icon">💬</div>
                        <div class="quick-action-label">WhatsApp Blast</div>
                    </div>
                    <div class="quick-action-card" onclick="startQuickCampaign('email')">
                        <div class="quick-action-icon">📧</div>
                        <div class="quick-action-label">E-Mail Kampagne</div>
                    </div>
                    <div class="quick-action-card" onclick="importFromExplorium()">
                        <div class="quick-action-icon">🔍</div>
                        <div class="quick-action-label">B2B Leads finden</div>
                    </div>
                    <div class="quick-action-card" onclick="syncHubSpot()">
                        <div class="quick-action-icon">🔄</div>
                        <div class="quick-action-label">HubSpot Sync</div>
                    </div>
                    <div class="quick-action-card" onclick="openModal('ai-campaign')">
                        <div class="quick-action-icon">🤖</div>
                        <div class="quick-action-label">AI Kampagne</div>
                    </div>
                </div>
                
                <!-- Stats -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="icon">🎯</div>
                        <div class="value" id="stat-leads">{{ stats.total_leads }}</div>
                        <div class="label">Leads Gesamt</div>
                        <div class="change positive">+{{ stats.new_leads_today }} heute</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">🔥</div>
                        <div class="value" id="stat-hot">{{ stats.hot_leads }}</div>
                        <div class="label">Hot Leads</div>
                        <div class="change positive">Score > 70</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">📧</div>
                        <div class="value" id="stat-campaigns">{{ stats.active_campaigns }}</div>
                        <div class="label">Aktive Kampagnen</div>
                        <div class="change">{{ stats.sent_today }} gesendet</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">⚡</div>
                        <div class="value" id="stat-automations">{{ stats.active_automations }}</div>
                        <div class="label">Automationen</div>
                        <div class="change positive">{{ stats.automation_runs }} Runs</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">📈</div>
                        <div class="value" id="stat-conversion">{{ stats.conversion_rate }}%</div>
                        <div class="label">Conversion Rate</div>
                        <div class="change positive">+2.5% vs. letzte Woche</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">💰</div>
                        <div class="value" id="stat-revenue">€{{ stats.pipeline_value }}</div>
                        <div class="label">Pipeline Value</div>
                        <div class="change positive">Potenzial</div>
                    </div>
                </div>
                
                <!-- Pipeline -->
                <div class="pipeline-container">
                    <div class="pipeline-header">
                        <h2>🎯 Lead Pipeline</h2>
                        <div>
                            <button class="btn btn-secondary" onclick="filterPipeline()">
                                🔍 Filter
                            </button>
                        </div>
                    </div>
                    <div class="pipeline-stages" id="pipeline">
                        <!-- Filled by JavaScript -->
                    </div>
                </div>
                
                <!-- Recent Activity -->
                <div class="campaigns-container">
                    <h2 style="margin-bottom: 20px;">📊 Letzte Aktivitäten</h2>
                    <div id="recent-activities">
                        <!-- Filled by JavaScript -->
                    </div>
                </div>
            </section>
            
            <!-- Leads Section -->
            <section id="section-leads" class="section" style="display: none;">
                <div class="broly-header">
                    <h1 class="broly-title">🎯 Leads verwalten</h1>
                    <div class="broly-actions">
                        <button class="btn btn-secondary" onclick="exportLeads()">
                            📥 Export
                        </button>
                        <button class="btn btn-secondary" onclick="openModal('import-leads')">
                            📤 Import
                        </button>
                        <button class="btn btn-primary" onclick="openModal('new-lead')">
                            ➕ Neuer Lead
                        </button>
                    </div>
                </div>
                
                <!-- Filters -->
                <div style="display: flex; gap: 15px; margin-bottom: 20px;">
                    <select class="form-select" style="width: auto;" onchange="filterLeads(this.value)">
                        <option value="">Alle Stages</option>
                        <option value="new">New</option>
                        <option value="contacted">Contacted</option>
                        <option value="qualified">Qualified</option>
                        <option value="proposal">Proposal</option>
                        <option value="won">Won</option>
                        <option value="lost">Lost</option>
                    </select>
                    <select class="form-select" style="width: auto;" onchange="filterByTemperature(this.value)">
                        <option value="">Alle Temperatures</option>
                        <option value="hot">🔥 Hot</option>
                        <option value="warm">🌡️ Warm</option>
                        <option value="cold">❄️ Cold</option>
                    </select>
                    <input type="text" class="form-input" style="width: 300px;" placeholder="🔍 Suchen..." oninput="searchLeads(this.value)">
                </div>
                
                <!-- Leads Table -->
                <div class="campaigns-container">
                    <table class="campaigns-table">
                        <thead>
                            <tr>
                                <th>Lead</th>
                                <th>Firma</th>
                                <th>Score</th>
                                <th>Stage</th>
                                <th>Quelle</th>
                                <th>Letzter Kontakt</th>
                                <th>Aktionen</th>
                            </tr>
                        </thead>
                        <tbody id="leads-table">
                            <!-- Filled by JavaScript -->
                        </tbody>
                    </table>
                </div>
            </section>
            
            <!-- Campaigns Section -->
            <section id="section-campaigns" class="section" style="display: none;">
                <div class="broly-header">
                    <h1 class="broly-title">📧 Kampagnen</h1>
                    <div class="broly-actions">
                        <button class="btn btn-primary" onclick="openModal('new-campaign')">
                            ➕ Neue Kampagne
                        </button>
                    </div>
                </div>
                
                <div class="tabs">
                    <button class="tab active" onclick="showCampaignTab('all')">Alle</button>
                    <button class="tab" onclick="showCampaignTab('running')">🟢 Laufend</button>
                    <button class="tab" onclick="showCampaignTab('scheduled')">📅 Geplant</button>
                    <button class="tab" onclick="showCampaignTab('draft')">📝 Entwürfe</button>
                    <button class="tab" onclick="showCampaignTab('completed')">✅ Abgeschlossen</button>
                </div>
                
                <div class="campaigns-container">
                    <table class="campaigns-table">
                        <thead>
                            <tr>
                                <th>Kampagne</th>
                                <th>Typ</th>
                                <th>Status</th>
                                <th>Gesendet</th>
                                <th>Öffnungsrate</th>
                                <th>Klickrate</th>
                                <th>Conversions</th>
                                <th>Aktionen</th>
                            </tr>
                        </thead>
                        <tbody id="campaigns-table">
                            <!-- Filled by JavaScript -->
                        </tbody>
                    </table>
                </div>
            </section>
            
            <!-- Automations Section -->
            <section id="section-automations" class="section" style="display: none;">
                <div class="broly-header">
                    <h1 class="broly-title">⚡ Automationen</h1>
                    <div class="broly-actions">
                        <button class="btn btn-primary" onclick="openModal('new-automation')">
                            ➕ Neue Automation
                        </button>
                    </div>
                </div>
                
                <div class="automation-grid" id="automations-grid">
                    <!-- Filled by JavaScript -->
                </div>
            </section>
            
            <!-- Sequences Section -->
            <section id="section-sequences" class="section" style="display: none;">
                <div class="broly-header">
                    <h1 class="broly-title">🔄 E-Mail Sequenzen</h1>
                    <div class="broly-actions">
                        <button class="btn btn-primary" onclick="openModal('new-sequence')">
                            ➕ Neue Sequenz
                        </button>
                    </div>
                </div>
                
                <div class="automation-grid" id="sequences-grid">
                    <!-- Filled by JavaScript -->
                </div>
            </section>
            
            <!-- Templates Section -->
            <section id="section-templates" class="section" style="display: none;">
                <div class="broly-header">
                    <h1 class="broly-title">📝 Templates</h1>
                    <div class="broly-actions">
                        <button class="btn btn-primary" onclick="openModal('new-template')">
                            ➕ Neues Template
                        </button>
                    </div>
                </div>
                
                <div class="tabs">
                    <button class="tab active" onclick="showTemplateTab('email')">📧 E-Mail</button>
                    <button class="tab" onclick="showTemplateTab('whatsapp')">💬 WhatsApp</button>
                    <button class="tab" onclick="showTemplateTab('sms')">📱 SMS</button>
                </div>
                
                <div class="automation-grid" id="templates-grid">
                    <!-- Filled by JavaScript -->
                </div>
            </section>
            
            <!-- Integrations Section -->
            <section id="section-integrations" class="section" style="display: none;">
                <div class="broly-header">
                    <h1 class="broly-title">🔗 Integrationen</h1>
                </div>
                
                <div class="automation-grid">
                    <div class="automation-card">
                        <div class="automation-card-header">
                            <div>
                                <div class="automation-card-title">🧡 HubSpot CRM</div>
                                <div class="automation-card-trigger">Contacts, Deals, Companies</div>
                            </div>
                            <label class="automation-toggle">
                                <input type="checkbox" checked onchange="toggleIntegration('hubspot', this.checked)">
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div class="automation-card-stats">
                            <div class="automation-stat">
                                <div class="automation-stat-value">1,234</div>
                                <div class="automation-stat-label">Synced</div>
                            </div>
                            <div class="automation-stat">
                                <div class="automation-stat-value">5 min</div>
                                <div class="automation-stat-label">Last Sync</div>
                            </div>
                        </div>
                        <button class="btn btn-secondary" style="width: 100%; margin-top: 15px;" onclick="syncHubSpot()">
                            🔄 Jetzt synchronisieren
                        </button>
                    </div>
                    
                    <div class="automation-card">
                        <div class="automation-card-header">
                            <div>
                                <div class="automation-card-title">🔍 Explorium B2B</div>
                                <div class="automation-card-trigger">B2B Leads & Firmendaten</div>
                            </div>
                            <label class="automation-toggle">
                                <input type="checkbox" checked onchange="toggleIntegration('explorium', this.checked)">
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div class="automation-card-stats">
                            <div class="automation-stat">
                                <div class="automation-stat-value">∞</div>
                                <div class="automation-stat-label">Available</div>
                            </div>
                            <div class="automation-stat">
                                <div class="automation-stat-value">50</div>
                                <div class="automation-stat-label">Credits</div>
                            </div>
                        </div>
                        <button class="btn btn-primary" style="width: 100%; margin-top: 15px;" onclick="importFromExplorium()">
                            🎯 Leads suchen
                        </button>
                    </div>
                    
                    <div class="automation-card">
                        <div class="automation-card-header">
                            <div>
                                <div class="automation-card-title">💬 WhatsApp Business</div>
                                <div class="automation-card-trigger">Messaging & Broadcasts</div>
                            </div>
                            <label class="automation-toggle">
                                <input type="checkbox" checked onchange="toggleIntegration('whatsapp', this.checked)">
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div class="automation-card-stats">
                            <div class="automation-stat">
                                <div class="automation-stat-value">500</div>
                                <div class="automation-stat-label">Sent Today</div>
                            </div>
                            <div class="automation-stat">
                                <div class="automation-stat-value">89%</div>
                                <div class="automation-stat-label">Delivery</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="automation-card">
                        <div class="automation-card-header">
                            <div>
                                <div class="automation-card-title">📞 Zadarma VoIP</div>
                                <div class="automation-card-trigger">Calls & Recordings</div>
                            </div>
                            <label class="automation-toggle">
                                <input type="checkbox" onchange="toggleIntegration('zadarma', this.checked)">
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div class="automation-card-stats">
                            <div class="automation-stat">
                                <div class="automation-stat-value">--</div>
                                <div class="automation-stat-label">Calls</div>
                            </div>
                            <div class="automation-stat">
                                <div class="automation-stat-value">--</div>
                                <div class="automation-stat-label">Duration</div>
                            </div>
                        </div>
                        <button class="btn btn-secondary" style="width: 100%; margin-top: 15px;" onclick="configureZadarma()">
                            ⚙️ Konfigurieren
                        </button>
                    </div>
                    
                    <div class="automation-card">
                        <div class="automation-card-header">
                            <div>
                                <div class="automation-card-title">💳 Stripe Payments</div>
                                <div class="automation-card-trigger">Invoices & Subscriptions</div>
                            </div>
                            <label class="automation-toggle">
                                <input type="checkbox" onchange="toggleIntegration('stripe', this.checked)">
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div class="automation-card-stats">
                            <div class="automation-stat">
                                <div class="automation-stat-value">--</div>
                                <div class="automation-stat-label">Revenue</div>
                            </div>
                            <div class="automation-stat">
                                <div class="automation-stat-value">--</div>
                                <div class="automation-stat-label">Active Subs</div>
                            </div>
                        </div>
                        <button class="btn btn-secondary" style="width: 100%; margin-top: 15px;" onclick="configureStripe()">
                            ⚙️ Konfigurieren
                        </button>
                    </div>
                    
                    <div class="automation-card">
                        <div class="automation-card-header">
                            <div>
                                <div class="automation-card-title">🤖 Claude AI</div>
                                <div class="automation-card-trigger">AI Personalization</div>
                            </div>
                            <label class="automation-toggle">
                                <input type="checkbox" checked onchange="toggleIntegration('claude', this.checked)">
                                <span class="slider"></span>
                            </label>
                        </div>
                        <div class="automation-card-stats">
                            <div class="automation-stat">
                                <div class="automation-stat-value">∞</div>
                                <div class="automation-stat-label">Calls</div>
                            </div>
                            <div class="automation-stat">
                                <div class="automation-stat-value">Active</div>
                                <div class="automation-stat-label">Status</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            
            <!-- Analytics Section -->
            <section id="section-analytics" class="section" style="display: none;">
                <div class="broly-header">
                    <h1 class="broly-title">📈 Analytics</h1>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="icon">📧</div>
                        <div class="value">45.2%</div>
                        <div class="label">E-Mail Öffnungsrate</div>
                        <div class="change positive">+5.3% vs. Branche</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">🖱️</div>
                        <div class="value">12.8%</div>
                        <div class="label">Klickrate</div>
                        <div class="change positive">+3.1% vs. letzte Woche</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">💬</div>
                        <div class="value">89%</div>
                        <div class="label">WhatsApp Delivery</div>
                        <div class="change">Standard</div>
                    </div>
                    <div class="stat-card">
                        <div class="icon">📊</div>
                        <div class="value">8.5%</div>
                        <div class="label">Lead → Customer</div>
                        <div class="change positive">+1.2% Verbesserung</div>
                    </div>
                </div>
                
                <div class="campaigns-container">
                    <h2 style="margin-bottom: 20px;">📊 Performance Übersicht</h2>
                    <canvas id="analytics-chart" height="300"></canvas>
                </div>
            </section>
        </main>
    </div>
    
    <!-- Modals -->
    <div class="modal-overlay" id="modal-new-lead">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">➕ Neuer Lead</h2>
                <button class="modal-close" onclick="closeModal('new-lead')">×</button>
            </div>
            <div class="modal-body">
                <form id="new-lead-form">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div class="form-group">
                            <label class="form-label">Vorname *</label>
                            <input type="text" class="form-input" name="first_name" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Nachname *</label>
                            <input type="text" class="form-input" name="last_name" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">E-Mail *</label>
                            <input type="email" class="form-input" name="email" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Telefon</label>
                            <input type="tel" class="form-input" name="phone">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Firma</label>
                            <input type="text" class="form-input" name="company_name">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Position</label>
                            <input type="text" class="form-input" name="job_title">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Branche</label>
                            <select class="form-select" name="industry">
                                <option value="">Auswählen...</option>
                                <option value="construction">Bau & Immobilien</option>
                                <option value="technology">Technologie</option>
                                <option value="finance">Finanzen</option>
                                <option value="healthcare">Gesundheit</option>
                                <option value="retail">Handel</option>
                                <option value="manufacturing">Produktion</option>
                                <option value="services">Dienstleistungen</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Quelle</label>
                            <select class="form-select" name="source">
                                <option value="manual">Manuell</option>
                                <option value="website">Website</option>
                                <option value="referral">Empfehlung</option>
                                <option value="event">Event</option>
                                <option value="cold_outreach">Cold Outreach</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Notizen</label>
                        <textarea class="form-textarea" name="notes" rows="3"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('new-lead')">Abbrechen</button>
                <button class="btn btn-primary" onclick="saveLead()">💾 Speichern</button>
            </div>
        </div>
    </div>
    
    <div class="modal-overlay" id="modal-new-campaign">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">📧 Neue Kampagne</h2>
                <button class="modal-close" onclick="closeModal('new-campaign')">×</button>
            </div>
            <div class="modal-body">
                <form id="new-campaign-form">
                    <div class="form-group">
                        <label class="form-label">Kampagnen-Name *</label>
                        <input type="text" class="form-input" name="name" required placeholder="z.B. Smart Home Launch 2025">
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div class="form-group">
                            <label class="form-label">Typ</label>
                            <select class="form-select" name="type">
                                <option value="email">📧 E-Mail</option>
                                <option value="whatsapp">💬 WhatsApp</option>
                                <option value="sms">📱 SMS</option>
                                <option value="multi_channel">🔄 Multi-Channel</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Zielgruppe</label>
                            <select class="form-select" name="audience">
                                <option value="all">Alle Leads</option>
                                <option value="hot">🔥 Hot Leads</option>
                                <option value="warm">🌡️ Warm Leads</option>
                                <option value="cold">❄️ Cold Leads</option>
                                <option value="new">🆕 Neue Leads</option>
                                <option value="custom">⚙️ Custom Filter</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Betreff</label>
                        <input type="text" class="form-input" name="subject" placeholder="Personalisierung: {{first_name}}, {{company}}">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Nachricht</label>
                        <textarea class="form-textarea" name="content" rows="6" placeholder="Hallo {{first_name}},

ich habe gesehen, dass {{company}} im Bereich Smart Home aktiv ist...

Beste Grüße,
Ömer"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Senden</label>
                        <div style="display: flex; gap: 15px;">
                            <label style="display: flex; align-items: center; gap: 8px;">
                                <input type="radio" name="send_time" value="now"> Sofort
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px;">
                                <input type="radio" name="send_time" value="scheduled" checked> Geplant
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Geplant für</label>
                        <input type="datetime-local" class="form-input" name="scheduled_at">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('new-campaign')">Abbrechen</button>
                <button class="btn btn-secondary" onclick="saveCampaign('draft')">📝 Als Entwurf</button>
                <button class="btn btn-primary" onclick="saveCampaign('schedule')">🚀 Planen</button>
            </div>
        </div>
    </div>
    
    <div class="modal-overlay" id="modal-new-automation">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">⚡ Neue Automation</h2>
                <button class="modal-close" onclick="closeModal('new-automation')">×</button>
            </div>
            <div class="modal-body">
                <form id="new-automation-form">
                    <div class="form-group">
                        <label class="form-label">Automation Name *</label>
                        <input type="text" class="form-input" name="name" required placeholder="z.B. Welcome Sequence">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Trigger</label>
                        <select class="form-select" name="trigger_type" onchange="showTriggerConfig(this.value)">
                            <option value="new_lead">🆕 Neuer Lead</option>
                            <option value="score_threshold">🔥 Score erreicht</option>
                            <option value="tag_added">🏷️ Tag hinzugefügt</option>
                            <option value="form_submit">📝 Formular gesendet</option>
                            <option value="page_visit">👁️ Seite besucht</option>
                            <option value="email_opened">📧 E-Mail geöffnet</option>
                            <option value="time_delay">⏰ Zeit vergangen</option>
                        </select>
                    </div>
                    
                    <div id="trigger-config" class="form-group" style="display: none;">
                        <!-- Dynamically filled -->
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Aktionen</label>
                        <div id="automation-actions" class="sequence-builder">
                            <div class="sequence-step">
                                <div class="sequence-step-number">1</div>
                                <div class="sequence-step-content">
                                    <select class="form-select" name="action_1_type" style="margin-bottom: 10px;">
                                        <option value="send_email">📧 E-Mail senden</option>
                                        <option value="send_whatsapp">💬 WhatsApp senden</option>
                                        <option value="add_tag">🏷️ Tag hinzufügen</option>
                                        <option value="update_score">📊 Score ändern</option>
                                        <option value="assign_user">👤 Zuweisen</option>
                                        <option value="create_task">✅ Task erstellen</option>
                                        <option value="webhook">🔗 Webhook</option>
                                    </select>
                                    <input type="text" class="form-input" name="action_1_value" placeholder="Template auswählen oder Wert eingeben">
                                </div>
                            </div>
                        </div>
                        <button type="button" class="btn btn-secondary" style="margin-top: 10px;" onclick="addAutomationAction()">
                            ➕ Weitere Aktion
                        </button>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('new-automation')">Abbrechen</button>
                <button class="btn btn-primary" onclick="saveAutomation()">💾 Speichern & Aktivieren</button>
            </div>
        </div>
    </div>
    
    <div class="modal-overlay" id="modal-ai-campaign">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">🤖 AI Kampagne erstellen</h2>
                <button class="modal-close" onclick="closeModal('ai-campaign')">×</button>
            </div>
            <div class="modal-body">
                <form id="ai-campaign-form">
                    <div class="form-group">
                        <label class="form-label">Was möchtest du erreichen?</label>
                        <textarea class="form-textarea" name="goal" rows="4" placeholder="Beispiel: Ich möchte Smart Home Interessenten in der DACH-Region ansprechen, die kürzlich ein Haus gekauft haben und sich für Hausautomation interessieren."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Zielgruppe</label>
                        <input type="text" class="form-input" name="target" placeholder="z.B. Bauherren, Architekten, Immobilienentwickler">
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div class="form-group">
                            <label class="form-label">Budget (Leads)</label>
                            <select class="form-select" name="lead_count">
                                <option value="50">50 Leads</option>
                                <option value="100" selected>100 Leads</option>
                                <option value="250">250 Leads</option>
                                <option value="500">500 Leads</option>
                                <option value="1000">1000 Leads</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Kanäle</label>
                            <select class="form-select" name="channels" multiple>
                                <option value="email" selected>📧 E-Mail</option>
                                <option value="whatsapp" selected>💬 WhatsApp</option>
                                <option value="linkedin">💼 LinkedIn</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Ton der Ansprache</label>
                        <select class="form-select" name="tone">
                            <option value="professional">💼 Professionell</option>
                            <option value="friendly">😊 Freundlich</option>
                            <option value="direct">🎯 Direkt</option>
                            <option value="casual">🤙 Locker</option>
                        </select>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('ai-campaign')">Abbrechen</button>
                <button class="btn btn-primary" onclick="generateAICampaign()">🤖 Kampagne generieren</button>
            </div>
        </div>
    </div>
    
    <script>
        // Sample Data
        const sampleLeads = [
            { id: 1, first_name: 'Max', last_name: 'Mustermann', email: 'max@example.com', company: 'TechCorp GmbH', score: 85, stage: 'qualified', temperature: 'hot', source: 'website', last_contact: '2024-12-23' },
            { id: 2, first_name: 'Anna', last_name: 'Schmidt', email: 'anna@building.de', company: 'Building AG', score: 72, stage: 'contacted', temperature: 'warm', source: 'explorium', last_contact: '2024-12-22' },
            { id: 3, first_name: 'Stefan', last_name: 'Weber', email: 'stefan@immo.com', company: 'ImmoVest', score: 45, stage: 'new', temperature: 'cold', source: 'hubspot', last_contact: null },
            { id: 4, first_name: 'Lisa', last_name: 'Bauer', email: 'lisa@architekten.de', company: 'Architekten Plus', score: 91, stage: 'proposal', temperature: 'hot', source: 'referral', last_contact: '2024-12-24' },
            { id: 5, first_name: 'Thomas', last_name: 'Koch', email: 'thomas@smart.io', company: 'Smart Living', score: 68, stage: 'qualified', temperature: 'warm', source: 'event', last_contact: '2024-12-20' },
        ];
        
        const sampleCampaigns = [
            { id: 1, name: 'Smart Home Launch 2025', type: 'email', status: 'running', sent: 450, opened: 203, clicked: 67, conversions: 12 },
            { id: 2, name: 'LOXONE Partner Outreach', type: 'whatsapp', status: 'running', sent: 120, opened: 98, clicked: 45, conversions: 8 },
            { id: 3, name: 'Cold Email Sequence', type: 'email', status: 'paused', sent: 1200, opened: 480, clicked: 120, conversions: 24 },
            { id: 4, name: 'Event Follow-Up', type: 'multi_channel', status: 'completed', sent: 85, opened: 72, clicked: 38, conversions: 15 },
        ];
        
        const sampleAutomations = [
            { id: 1, name: 'Welcome Sequence', trigger: 'Neuer Lead', active: true, runs: 234, conversions: 45 },
            { id: 2, name: 'Hot Lead Alert', trigger: 'Score > 80', active: true, runs: 89, conversions: 23 },
            { id: 3, name: 'Re-engagement', trigger: '30 Tage inaktiv', active: false, runs: 156, conversions: 12 },
            { id: 4, name: 'Proposal Follow-Up', trigger: 'Stage = Proposal', active: true, runs: 67, conversions: 18 },
        ];
        
        // Navigation
        function showSection(section) {
            document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
            document.getElementById('section-' + section).style.display = 'block';
            
            document.querySelectorAll('.broly-nav a').forEach(a => a.classList.remove('active'));
            event.target.closest('a').classList.add('active');
        }
        
        // Modal Functions
        function openModal(type) {
            document.getElementById('modal-' + type).classList.add('active');
        }
        
        function closeModal(type) {
            document.getElementById('modal-' + type).classList.remove('active');
        }
        
        // Pipeline
        function renderPipeline() {
            const stages = ['new', 'contacted', 'qualified', 'proposal', 'won', 'lost'];
            const stageNames = {
                new: '🆕 Neu',
                contacted: '📞 Kontaktiert',
                qualified: '✅ Qualifiziert',
                proposal: '📋 Angebot',
                won: '🎉 Gewonnen',
                lost: '❌ Verloren'
            };
            
            const pipeline = document.getElementById('pipeline');
            pipeline.innerHTML = stages.map(stage => {
                const leads = sampleLeads.filter(l => l.stage === stage);
                return `
                    <div class="pipeline-stage stage-${stage}">
                        <div class="pipeline-stage-header">
                            <span class="pipeline-stage-name">${stageNames[stage]}</span>
                            <span class="pipeline-stage-count">${leads.length}</span>
                        </div>
                        ${leads.map(lead => `
                            <div class="lead-card" onclick="openLeadDetail(${lead.id})">
                                <div class="lead-card-name">${lead.first_name} ${lead.last_name}</div>
                                <div class="lead-card-company">${lead.company}</div>
                                <span class="lead-card-score score-${lead.temperature}">${lead.score} Punkte</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }).join('');
        }
        
        // Leads Table
        function renderLeadsTable() {
            const tbody = document.getElementById('leads-table');
            tbody.innerHTML = sampleLeads.map(lead => `
                <tr>
                    <td>
                        <strong>${lead.first_name} ${lead.last_name}</strong><br>
                        <small style="color: #888;">${lead.email}</small>
                    </td>
                    <td>${lead.company}</td>
                    <td><span class="lead-card-score score-${lead.temperature}">${lead.score}</span></td>
                    <td><span class="campaign-status status-${lead.stage === 'won' ? 'completed' : lead.stage === 'lost' ? 'draft' : 'running'}">${lead.stage}</span></td>
                    <td>${lead.source}</td>
                    <td>${lead.last_contact || '-'}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="openLeadDetail(${lead.id})">👁️</button>
                        <button class="btn btn-primary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="contactLead(${lead.id})">📧</button>
                    </td>
                </tr>
            `).join('');
        }
        
        // Campaigns Table
        function renderCampaignsTable() {
            const tbody = document.getElementById('campaigns-table');
            tbody.innerHTML = sampleCampaigns.map(c => `
                <tr>
                    <td><strong>${c.name}</strong></td>
                    <td>${c.type === 'email' ? '📧' : c.type === 'whatsapp' ? '💬' : '🔄'} ${c.type}</td>
                    <td><span class="campaign-status status-${c.status}">${c.status}</span></td>
                    <td>${c.sent}</td>
                    <td>${((c.opened / c.sent) * 100).toFixed(1)}%</td>
                    <td>${((c.clicked / c.sent) * 100).toFixed(1)}%</td>
                    <td>${c.conversions}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;">✏️</button>
                        <button class="btn btn-${c.status === 'running' ? 'danger' : 'success'}" style="padding: 6px 12px; font-size: 0.8rem;">
                            ${c.status === 'running' ? '⏸️' : '▶️'}
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
        // Automations Grid
        function renderAutomations() {
            const grid = document.getElementById('automations-grid');
            grid.innerHTML = sampleAutomations.map(a => `
                <div class="automation-card">
                    <div class="automation-card-header">
                        <div>
                            <div class="automation-card-title">${a.name}</div>
                            <div class="automation-card-trigger">Trigger: ${a.trigger}</div>
                        </div>
                        <label class="automation-toggle">
                            <input type="checkbox" ${a.active ? 'checked' : ''} onchange="toggleAutomation(${a.id}, this.checked)">
                            <span class="slider"></span>
                        </label>
                    </div>
                    <div class="automation-card-stats">
                        <div class="automation-stat">
                            <div class="automation-stat-value">${a.runs}</div>
                            <div class="automation-stat-label">Ausgeführt</div>
                        </div>
                        <div class="automation-stat">
                            <div class="automation-stat-value">${a.conversions}</div>
                            <div class="automation-stat-label">Conversions</div>
                        </div>
                        <div class="automation-stat">
                            <div class="automation-stat-value">${((a.conversions / a.runs) * 100).toFixed(1)}%</div>
                            <div class="automation-stat-label">Rate</div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        // API Functions
        async function saveLead() {
            const form = document.getElementById('new-lead-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/broly/leads', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    closeModal('new-lead');
                    alert('✅ Lead erfolgreich erstellt!');
                    location.reload();
                }
            } catch (error) {
                console.error('Error:', error);
                alert('❌ Fehler beim Speichern');
            }
        }
        
        async function saveCampaign(action) {
            const form = document.getElementById('new-campaign-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            data.status = action === 'draft' ? 'draft' : 'scheduled';
            
            try {
                const response = await fetch('/api/broly/campaigns', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    closeModal('new-campaign');
                    alert('✅ Kampagne erstellt!');
                    location.reload();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        async function saveAutomation() {
            const form = document.getElementById('new-automation-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/broly/automations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    closeModal('new-automation');
                    alert('✅ Automation erstellt und aktiviert!');
                    location.reload();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        async function generateAICampaign() {
            const form = document.getElementById('ai-campaign-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            alert('🤖 AI generiert deine Kampagne...');
            
            try {
                const response = await fetch('/api/broly/ai-campaign', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    closeModal('ai-campaign');
                    alert('✅ AI Kampagne erstellt! ' + result.message);
                    location.reload();
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        function syncHubSpot() {
            alert('🔄 HubSpot Sync gestartet...');
            fetch('/api/broly/sync/hubspot', { method: 'POST' })
                .then(r => r.json())
                .then(data => alert('✅ ' + data.message))
                .catch(e => alert('❌ Sync fehlgeschlagen'));
        }
        
        function importFromExplorium() {
            openModal('ai-campaign');
        }
        
        function syncAllData() {
            alert('🔄 Synchronisiere alle Daten...');
        }
        
        function toggleAutomation(id, active) {
            fetch(`/api/broly/automations/${id}/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ active })
            });
        }
        
        function toggleIntegration(name, active) {
            console.log(`Integration ${name}: ${active}`);
        }
        
        function addAutomationAction() {
            const container = document.getElementById('automation-actions');
            const count = container.querySelectorAll('.sequence-step').length + 1;
            
            const step = document.createElement('div');
            step.innerHTML = `
                <div class="sequence-connector"></div>
                <div class="sequence-step">
                    <div class="sequence-step-number">${count}</div>
                    <div class="sequence-step-content">
                        <select class="form-select" name="action_${count}_type" style="margin-bottom: 10px;">
                            <option value="send_email">📧 E-Mail senden</option>
                            <option value="send_whatsapp">💬 WhatsApp senden</option>
                            <option value="wait">⏰ Warten</option>
                            <option value="add_tag">🏷️ Tag hinzufügen</option>
                            <option value="update_score">📊 Score ändern</option>
                        </select>
                        <input type="text" class="form-input" name="action_${count}_value" placeholder="Konfiguration...">
                    </div>
                </div>
            `;
            container.appendChild(step);
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            renderPipeline();
            renderLeadsTable();
            renderCampaignsTable();
            renderAutomations();
        });
    </script>
</body>
</html>
"""


# ============================================================================
# API ROUTES - Broly Automation
# ============================================================================

@broly_bp.route('/broly')
def broly_dashboard():
    """Broly Automation Dashboard"""
    stats = {
        'total_leads': 1247,
        'new_leads_today': 23,
        'hot_leads': 89,
        'active_campaigns': 4,
        'sent_today': 156,
        'active_automations': 6,
        'automation_runs': 1893,
        'conversion_rate': 8.5,
        'pipeline_value': '145,000'
    }
    return render_template_string(BROLY_DASHBOARD_HTML, stats=stats)


# ----- LEADS API -----

@broly_bp.route('/api/broly/leads', methods=['GET'])
def get_leads():
    """Get all leads with optional filters"""
    # In production: Query from database with filters
    stage = request.args.get('stage')
    temperature = request.args.get('temperature')
    search = request.args.get('search')
    
    leads = [
        {'id': 1, 'first_name': 'Max', 'last_name': 'Mustermann', 'email': 'max@example.com', 
         'company_name': 'TechCorp GmbH', 'score': 85, 'stage': 'qualified', 'temperature': 'hot'},
        {'id': 2, 'first_name': 'Anna', 'last_name': 'Schmidt', 'email': 'anna@building.de',
         'company_name': 'Building AG', 'score': 72, 'stage': 'contacted', 'temperature': 'warm'},
    ]
    
    return jsonify({'success': True, 'leads': leads, 'total': len(leads)})


@broly_bp.route('/api/broly/leads', methods=['POST'])
def create_lead():
    """Create a new lead"""
    data = request.json
    
    # Calculate initial score based on data completeness
    score = 0
    if data.get('email'): score += 20
    if data.get('phone'): score += 15
    if data.get('company_name'): score += 15
    if data.get('job_title'): score += 10
    if data.get('industry'): score += 10
    
    # In production: Save to database
    lead = {
        'id': random.randint(100, 9999),
        **data,
        'score': score,
        'stage': 'new',
        'temperature': 'cold' if score < 40 else ('warm' if score < 70 else 'hot'),
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'success': True, 'lead': lead, 'message': 'Lead erfolgreich erstellt'})


@broly_bp.route('/api/broly/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Update a lead"""
    data = request.json
    # In production: Update in database
    return jsonify({'success': True, 'message': f'Lead {lead_id} aktualisiert'})


@broly_bp.route('/api/broly/leads/<int:lead_id>/score', methods=['POST'])
def update_lead_score(lead_id):
    """Recalculate lead score"""
    # AI-based scoring algorithm
    score_factors = {
        'email_opens': 5,
        'email_clicks': 10,
        'website_visits': 3,
        'form_submits': 20,
        'meeting_booked': 30,
        'proposal_viewed': 15
    }
    
    # In production: Calculate based on actual engagement
    new_score = random.randint(50, 95)
    temperature = 'cold' if new_score < 40 else ('warm' if new_score < 70 else 'hot')
    
    return jsonify({
        'success': True, 
        'lead_id': lead_id,
        'new_score': new_score,
        'temperature': temperature
    })


# ----- CAMPAIGNS API -----

@broly_bp.route('/api/broly/campaigns', methods=['GET'])
def get_campaigns():
    """Get all campaigns"""
    campaigns = [
        {'id': 1, 'name': 'Smart Home Launch 2025', 'type': 'email', 'status': 'running',
         'sent_count': 450, 'open_count': 203, 'click_count': 67, 'conversion_count': 12},
        {'id': 2, 'name': 'LOXONE Partner Outreach', 'type': 'whatsapp', 'status': 'running',
         'sent_count': 120, 'open_count': 98, 'click_count': 45, 'conversion_count': 8},
    ]
    return jsonify({'success': True, 'campaigns': campaigns})


@broly_bp.route('/api/broly/campaigns', methods=['POST'])
def create_campaign():
    """Create a new campaign"""
    data = request.json
    
    campaign = {
        'id': random.randint(100, 9999),
        **data,
        'created_at': datetime.now().isoformat(),
        'sent_count': 0,
        'open_count': 0,
        'click_count': 0
    }
    
    return jsonify({'success': True, 'campaign': campaign, 'message': 'Kampagne erstellt'})


@broly_bp.route('/api/broly/campaigns/<int:campaign_id>/start', methods=['POST'])
def start_campaign(campaign_id):
    """Start a campaign"""
    # In production: Start background job to send messages
    return jsonify({'success': True, 'message': f'Kampagne {campaign_id} gestartet'})


@broly_bp.route('/api/broly/campaigns/<int:campaign_id>/pause', methods=['POST'])
def pause_campaign(campaign_id):
    """Pause a campaign"""
    return jsonify({'success': True, 'message': f'Kampagne {campaign_id} pausiert'})


# ----- AUTOMATIONS API -----

@broly_bp.route('/api/broly/automations', methods=['GET'])
def get_automations():
    """Get all automations"""
    automations = [
        {'id': 1, 'name': 'Welcome Sequence', 'trigger_type': 'new_lead', 'is_active': True, 'run_count': 234},
        {'id': 2, 'name': 'Hot Lead Alert', 'trigger_type': 'score_threshold', 'is_active': True, 'run_count': 89},
    ]
    return jsonify({'success': True, 'automations': automations})


@broly_bp.route('/api/broly/automations', methods=['POST'])
def create_automation():
    """Create a new automation"""
    data = request.json
    
    automation = {
        'id': random.randint(100, 9999),
        **data,
        'is_active': True,
        'run_count': 0,
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'success': True, 'automation': automation, 'message': 'Automation erstellt und aktiviert'})


@broly_bp.route('/api/broly/automations/<int:automation_id>/toggle', methods=['POST'])
def toggle_automation(automation_id):
    """Toggle automation on/off"""
    data = request.json
    active = data.get('active', False)
    # In production: Update in database
    return jsonify({'success': True, 'automation_id': automation_id, 'active': active})


# ----- AI CAMPAIGN -----

@broly_bp.route('/api/broly/ai-campaign', methods=['POST'])
def create_ai_campaign():
    """Create an AI-powered campaign"""
    data = request.json
    
    goal = data.get('goal', '')
    target = data.get('target', '')
    lead_count = int(data.get('lead_count', 100))
    channels = data.get('channels', ['email'])
    tone = data.get('tone', 'professional')
    
    # AI würde hier:
    # 1. Explorium nach passenden Leads durchsuchen
    # 2. Personalisierte Nachrichten generieren
    # 3. Multi-Channel Sequenz erstellen
    # 4. Optimale Sendezeiten berechnen
    
    campaign_result = {
        'campaign_id': random.randint(1000, 9999),
        'name': f'AI Campaign - {target[:30]}',
        'leads_found': lead_count,
        'channels': channels,
        'estimated_reach': lead_count * 0.85,
        'estimated_conversions': int(lead_count * 0.08),
        'sequence_steps': 5,
        'personalization_level': 'high'
    }
    
    return jsonify({
        'success': True,
        'campaign': campaign_result,
        'message': f'{lead_count} Leads gefunden, {len(channels)} Kanäle konfiguriert, 5-Step Sequenz erstellt'
    })


# ----- SYNC APIs -----

@broly_bp.route('/api/broly/sync/hubspot', methods=['POST'])
def sync_hubspot():
    """Sync data with HubSpot"""
    # In production: Actual HubSpot API sync
    return jsonify({
        'success': True,
        'message': '234 Kontakte synchronisiert, 12 neue Leads importiert',
        'synced': {
            'contacts': 234,
            'deals': 45,
            'companies': 89
        }
    })


@broly_bp.route('/api/broly/sync/explorium', methods=['POST'])
def sync_explorium():
    """Search and import leads from Explorium"""
    data = request.json
    
    # In production: Use Explorium API
    # filters = data.get('filters', {})
    
    return jsonify({
        'success': True,
        'message': '150 neue B2B Leads gefunden',
        'leads_found': 150,
        'imported': 150
    })


# ----- WEBHOOKS -----

@broly_bp.route('/webhook/broly/lead', methods=['POST'])
def webhook_new_lead():
    """Webhook for new leads (forms, integrations)"""
    data = request.json
    
    # Process incoming lead
    # Trigger automations
    
    return jsonify({'success': True, 'message': 'Lead received'})


@broly_bp.route('/webhook/broly/email-event', methods=['POST'])
def webhook_email_event():
    """Webhook for email events (opens, clicks, bounces)"""
    data = request.json
    event_type = data.get('event')  # opened, clicked, bounced, unsubscribed
    
    # Update campaign stats
    # Update lead engagement score
    # Trigger follow-up automations
    
    return jsonify({'success': True})


# ----- ANALYTICS API -----

@broly_bp.route('/api/broly/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    period = request.args.get('period', '7d')
    
    analytics = {
        'leads': {
            'total': 1247,
            'new_this_period': 89,
            'converted': 34,
            'conversion_rate': 8.5
        },
        'campaigns': {
            'active': 4,
            'sent': 2450,
            'open_rate': 45.2,
            'click_rate': 12.8,
            'reply_rate': 5.3
        },
        'channels': {
            'email': {'sent': 1800, 'open_rate': 42.1, 'click_rate': 11.2},
            'whatsapp': {'sent': 500, 'delivery_rate': 89.0, 'reply_rate': 23.4},
            'sms': {'sent': 150, 'delivery_rate': 95.0, 'click_rate': 8.9}
        },
        'top_performing': [
            {'campaign': 'Smart Home Launch', 'conversions': 12, 'roi': 450},
            {'campaign': 'LOXONE Partners', 'conversions': 8, 'roi': 320}
        ]
    }
    
    return jsonify({'success': True, 'analytics': analytics})


# ----- TEMPLATES API -----

@broly_bp.route('/api/broly/templates', methods=['GET'])
def get_templates():
    """Get message templates"""
    template_type = request.args.get('type', 'all')
    
    templates = [
        {
            'id': 1,
            'name': 'Cold Email - Smart Home',
            'type': 'email',
            'category': 'outreach',
            'subject': 'Interesse an Smart Home für {{company}}?',
            'content': 'Hallo {{first_name}},\n\nich habe gesehen, dass {{company}} im Bereich...',
            'variables': ['first_name', 'company', 'industry'],
            'use_count': 234,
            'avg_open_rate': 48.5
        },
        {
            'id': 2,
            'name': 'WhatsApp - Erstansprache',
            'type': 'whatsapp',
            'category': 'outreach',
            'subject': None,
            'content': 'Hallo {{first_name}}! 👋\n\nHier ist Ömer von West Money...',
            'variables': ['first_name'],
            'use_count': 156,
            'avg_open_rate': 92.0
        }
    ]
    
    if template_type != 'all':
        templates = [t for t in templates if t['type'] == template_type]
    
    return jsonify({'success': True, 'templates': templates})


@broly_bp.route('/api/broly/templates', methods=['POST'])
def create_template():
    """Create a new template"""
    data = request.json
    
    # Extract variables from content
    import re
    content = data.get('content', '')
    variables = re.findall(r'\{\{(\w+)\}\}', content)
    
    template = {
        'id': random.randint(100, 9999),
        **data,
        'variables': list(set(variables)),
        'use_count': 0,
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'success': True, 'template': template})


# ============================================================================
# LEAD SCORING ENGINE
# ============================================================================

class LeadScoringEngine:
    """AI-powered lead scoring"""
    
    SCORING_RULES = {
        # Demographic factors
        'has_email': 10,
        'has_phone': 10,
        'has_company': 15,
        'has_job_title': 10,
        'is_decision_maker': 20,
        
        # Engagement factors
        'email_opened': 5,
        'email_clicked': 10,
        'website_visit': 3,
        'page_views': 1,  # per page
        'form_submit': 25,
        'meeting_booked': 40,
        
        # Company factors
        'company_size_match': 15,
        'industry_match': 20,
        'location_match': 10,
        
        # Behavior factors
        'pricing_page_view': 15,
        'demo_request': 35,
        'content_download': 10,
        'return_visitor': 10
    }
    
    DECAY_RATE = 0.05  # 5% decay per week of inactivity
    
    @classmethod
    def calculate_score(cls, lead_data: dict, engagement_data: dict = None) -> dict:
        """Calculate lead score based on data and engagement"""
        score = 0
        factors = []
        
        # Demographic scoring
        if lead_data.get('email'):
            score += cls.SCORING_RULES['has_email']
            factors.append(('has_email', cls.SCORING_RULES['has_email']))
            
        if lead_data.get('phone'):
            score += cls.SCORING_RULES['has_phone']
            factors.append(('has_phone', cls.SCORING_RULES['has_phone']))
            
        if lead_data.get('company_name'):
            score += cls.SCORING_RULES['has_company']
            factors.append(('has_company', cls.SCORING_RULES['has_company']))
            
        if lead_data.get('job_title'):
            score += cls.SCORING_RULES['has_job_title']
            factors.append(('has_job_title', cls.SCORING_RULES['has_job_title']))
            
            # Check if decision maker
            dm_titles = ['ceo', 'cto', 'cfo', 'owner', 'director', 'head', 'vp', 'president', 'founder']
            if any(t in lead_data['job_title'].lower() for t in dm_titles):
                score += cls.SCORING_RULES['is_decision_maker']
                factors.append(('is_decision_maker', cls.SCORING_RULES['is_decision_maker']))
        
        # Engagement scoring
        if engagement_data:
            score += engagement_data.get('email_opens', 0) * cls.SCORING_RULES['email_opened']
            score += engagement_data.get('email_clicks', 0) * cls.SCORING_RULES['email_clicked']
            score += engagement_data.get('website_visits', 0) * cls.SCORING_RULES['website_visit']
        
        # Cap score at 100
        score = min(score, 100)
        
        # Determine temperature
        if score >= 70:
            temperature = 'hot'
        elif score >= 40:
            temperature = 'warm'
        else:
            temperature = 'cold'
        
        return {
            'score': score,
            'temperature': temperature,
            'factors': factors,
            'recommendation': cls._get_recommendation(score, temperature)
        }
    
    @classmethod
    def _get_recommendation(cls, score: int, temperature: str) -> str:
        """Get action recommendation based on score"""
        if temperature == 'hot':
            return 'Sofort kontaktieren! Meeting vereinbaren.'
        elif temperature == 'warm':
            return 'Follow-up E-Mail senden. Personalisiertes Angebot erstellen.'
        else:
            return 'In Nurturing-Sequenz aufnehmen. Mehr Engagement generieren.'


# ============================================================================
# AUTOMATION ENGINE
# ============================================================================

class AutomationEngine:
    """Process and execute automations"""
    
    TRIGGERS = {
        'new_lead': 'Neuer Lead erstellt',
        'score_threshold': 'Score-Schwellenwert erreicht',
        'tag_added': 'Tag hinzugefügt',
        'form_submit': 'Formular abgesendet',
        'page_visit': 'Seite besucht',
        'email_opened': 'E-Mail geöffnet',
        'email_clicked': 'Link geklickt',
        'time_delay': 'Zeitverzögerung',
        'stage_change': 'Stage geändert'
    }
    
    ACTIONS = {
        'send_email': 'E-Mail senden',
        'send_whatsapp': 'WhatsApp senden',
        'send_sms': 'SMS senden',
        'add_tag': 'Tag hinzufügen',
        'remove_tag': 'Tag entfernen',
        'update_score': 'Score aktualisieren',
        'change_stage': 'Stage ändern',
        'assign_user': 'Benutzer zuweisen',
        'create_task': 'Aufgabe erstellen',
        'webhook': 'Webhook aufrufen',
        'wait': 'Warten',
        'condition': 'Bedingung prüfen'
    }
    
    @classmethod
    def check_trigger(cls, trigger_type: str, trigger_config: dict, event_data: dict) -> bool:
        """Check if automation should trigger"""
        if trigger_type == 'new_lead':
            return True
            
        elif trigger_type == 'score_threshold':
            threshold = trigger_config.get('threshold', 70)
            return event_data.get('score', 0) >= threshold
            
        elif trigger_type == 'tag_added':
            required_tag = trigger_config.get('tag')
            return required_tag in event_data.get('tags', [])
            
        elif trigger_type == 'stage_change':
            target_stage = trigger_config.get('stage')
            return event_data.get('new_stage') == target_stage
            
        return False
    
    @classmethod
    def execute_action(cls, action_type: str, action_config: dict, lead_data: dict) -> dict:
        """Execute an automation action"""
        result = {'success': False, 'message': ''}
        
        if action_type == 'send_email':
            # In production: Send actual email
            template_id = action_config.get('template_id')
            result = {'success': True, 'message': f'E-Mail gesendet (Template: {template_id})'}
            
        elif action_type == 'send_whatsapp':
            # In production: Send WhatsApp via API
            template_id = action_config.get('template_id')
            result = {'success': True, 'message': f'WhatsApp gesendet (Template: {template_id})'}
            
        elif action_type == 'add_tag':
            tag = action_config.get('tag')
            result = {'success': True, 'message': f'Tag "{tag}" hinzugefügt'}
            
        elif action_type == 'update_score':
            points = action_config.get('points', 0)
            result = {'success': True, 'message': f'Score um {points} Punkte geändert'}
            
        elif action_type == 'change_stage':
            stage = action_config.get('stage')
            result = {'success': True, 'message': f'Stage auf "{stage}" geändert'}
            
        elif action_type == 'create_task':
            task = action_config.get('task')
            result = {'success': True, 'message': f'Aufgabe erstellt: {task}'}
            
        elif action_type == 'wait':
            delay = action_config.get('delay', '1d')
            result = {'success': True, 'message': f'Warte {delay}', 'delay': delay}
        
        return result


# ============================================================================
# INTEGRATION: Register Blueprint
# ============================================================================

def register_broly_blueprint(app):
    """Register Broly blueprint with Flask app"""
    app.register_blueprint(broly_bp)
    print("🐉 BROLY AUTOMATION loaded!")


# Export
__all__ = ['broly_bp', 'register_broly_blueprint', 'LeadScoringEngine', 'AutomationEngine', 'BROLY_MODELS']
