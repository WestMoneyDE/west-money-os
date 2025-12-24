"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  📧 KAMPAGNEN MODUL - WEST MONEY OS v12.0                                     ║
║  Multi-Channel Kampagnen mit Auto-Sequenzen & AI-Personalisierung            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Blueprint, render_template_string, request, jsonify
from datetime import datetime, timedelta
import json
import random

campaigns_bp = Blueprint('campaigns', __name__)

CAMPAIGNS_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📧 Kampagnen - West Money OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a15 0%, #150a1a 50%, #0a0510 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { display: flex; min-height: 100vh; }
        .sidebar {
            width: 260px;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255,255,255,0.1);
            padding: 20px;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .logo-icon { font-size: 1.8rem; }
        .logo-text {
            font-size: 1.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav a {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            color: #888;
            text-decoration: none;
            border-radius: 10px;
            margin-bottom: 5px;
            transition: all 0.3s;
        }
        .nav a:hover, .nav a.active {
            background: rgba(255,0,255,0.1);
            color: #ff00ff;
        }
        .main { flex: 1; padding: 30px; overflow-y: auto; }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        .title { font-size: 2rem; font-weight: 700; }
        .actions { display: flex; gap: 12px; }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
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
            box-shadow: 0 8px 25px rgba(255,0,255,0.3);
        }
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .btn-success { background: linear-gradient(135deg, #00ffff, #1e90ff); color: #fff; }
        .btn-danger { background: linear-gradient(135deg, #ff4757, #ff3838); color: #fff; }
        
        /* Stats */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
        }
        .stat-card .icon { font-size: 1.8rem; margin-bottom: 8px; }
        .stat-card .value {
            font-size: 2rem;
            font-weight: 700;
            color: #ff00ff;
        }
        .stat-card .label { color: #888; font-size: 0.85rem; margin-top: 5px; }
        
        /* Campaign Types */
        .campaign-types {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .campaign-type-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .campaign-type-card:hover {
            border-color: #ff00ff;
            transform: translateY(-5px);
        }
        .campaign-type-card .icon { font-size: 3rem; margin-bottom: 15px; }
        .campaign-type-card .name { font-size: 1.1rem; font-weight: 600; margin-bottom: 5px; }
        .campaign-type-card .desc { font-size: 0.85rem; color: #888; }
        
        /* Campaigns Grid */
        .campaigns-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        .campaign-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            overflow: hidden;
            transition: all 0.3s;
        }
        .campaign-card:hover {
            border-color: rgba(255,0,255,0.3);
            transform: translateY(-3px);
        }
        .campaign-card-header {
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .campaign-card-title { font-size: 1.1rem; font-weight: 600; }
        .campaign-card-type { font-size: 0.85rem; color: #888; margin-top: 5px; }
        .campaign-status {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-running { background: #00ffff; color: #000; }
        .status-paused { background: #00ffff; color: #000; }
        .status-draft { background: #636e72; color: #fff; }
        .status-completed { background: #74b9ff; color: #000; }
        .status-scheduled { background: #a29bfe; color: #000; }
        
        .campaign-card-body { padding: 20px; }
        .campaign-stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }
        .campaign-stat {
            text-align: center;
        }
        .campaign-stat-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: #ff00ff;
        }
        .campaign-stat-label {
            font-size: 0.7rem;
            color: #888;
            text-transform: uppercase;
        }
        
        .campaign-card-footer {
            padding: 15px 20px;
            background: rgba(0,0,0,0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .campaign-actions { display: flex; gap: 8px; }
        .action-btn {
            padding: 8px 12px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s;
        }
        .action-btn:hover { background: rgba(255,0,255,0.2); }
        
        /* Modal */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal-overlay.active { display: flex; }
        .modal {
            background: #150a1a;
            border: 1px solid rgba(255,0,255,0.3);
            border-radius: 20px;
            width: 90%;
            max-width: 900px;
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
        .modal-title { font-size: 1.3rem; font-weight: 700; }
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
            padding: 20px 24px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .form-group { margin-bottom: 20px; }
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #ccc;
        }
        .form-input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: #fff;
            font-size: 1rem;
        }
        .form-input:focus {
            outline: none;
            border-color: #ff00ff;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        /* Sequence Builder */
        .sequence-builder {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
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
            width: 35px;
            height: 35px;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: #000;
        }
        .sequence-step-content { flex: 1; }
        .sequence-connector {
            width: 2px;
            height: 25px;
            background: linear-gradient(to bottom, #ff00ff, transparent);
            margin-left: 32px;
        }
        
        .template-preview {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 20px;
            margin-top: 15px;
        }
        .template-preview-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 16px 24px;
            background: #00ffff;
            color: #000;
            border-radius: 10px;
            font-weight: 600;
            z-index: 9999;
        }
    </style>
</head>
<body>
    <div class="container">
        <nav class="sidebar">
            <div class="logo">
                <span class="logo-icon">💰</span>
                <span class="logo-text">West Money OS</span>
            </div>
            <div class="nav">
                <a href="/dashboard"><span>📊</span> Dashboard</a>
                <a href="/dashboard/contacts"><span>📇</span> Kontakte</a>
                <a href="/dashboard/leads"><span>🎯</span> Leads</a>
                <a href="/broly"><span>🐉</span> Broly</a>
                <a href="/dashboard/campaigns" class="active"><span>📧</span> Kampagnen</a>
                <a href="/dashboard/invoices"><span>💰</span> Rechnungen</a>
                <a href="/dashboard/whatsapp"><span>💬</span> WhatsApp</a>
                <a href="/dashboard/ai-chat"><span>🤖</span> AI Chat</a>
                <a href="/dashboard/settings"><span>⚙️</span> Settings</a>
            </div>
        </nav>
        
        <main class="main">
            <div class="header">
                <h1 class="title">📧 Kampagnen</h1>
                <div class="actions">
                    <button class="btn btn-secondary" onclick="showTemplates()">📝 Templates</button>
                    <button class="btn btn-primary" onclick="openModal('new-campaign')">➕ Neue Kampagne</button>
                </div>
            </div>
            
            <!-- Stats -->
            <div class="stats-row">
                <div class="stat-card">
                    <div class="icon">📧</div>
                    <div class="value">{{ stats.total_sent }}</div>
                    <div class="label">Gesendet gesamt</div>
                </div>
                <div class="stat-card">
                    <div class="icon">👁️</div>
                    <div class="value">{{ stats.open_rate }}%</div>
                    <div class="label">Öffnungsrate</div>
                </div>
                <div class="stat-card">
                    <div class="icon">🖱️</div>
                    <div class="value">{{ stats.click_rate }}%</div>
                    <div class="label">Klickrate</div>
                </div>
                <div class="stat-card">
                    <div class="icon">💬</div>
                    <div class="value">{{ stats.reply_rate }}%</div>
                    <div class="label">Antwortrate</div>
                </div>
                <div class="stat-card">
                    <div class="icon">🎯</div>
                    <div class="value">{{ stats.conversions }}</div>
                    <div class="label">Conversions</div>
                </div>
            </div>
            
            <!-- Campaign Types -->
            <h2 style="margin-bottom: 20px;">🚀 Schnellstart</h2>
            <div class="campaign-types">
                <div class="campaign-type-card" onclick="createCampaign('email')">
                    <div class="icon">📧</div>
                    <div class="name">E-Mail Kampagne</div>
                    <div class="desc">Newsletter & Outreach</div>
                </div>
                <div class="campaign-type-card" onclick="createCampaign('whatsapp')">
                    <div class="icon">💬</div>
                    <div class="name">WhatsApp Broadcast</div>
                    <div class="desc">Direkte Nachrichten</div>
                </div>
                <div class="campaign-type-card" onclick="createCampaign('sequence')">
                    <div class="icon">🔄</div>
                    <div class="name">Auto-Sequenz</div>
                    <div class="desc">Drip-Kampagne</div>
                </div>
                <div class="campaign-type-card" onclick="createCampaign('ai')">
                    <div class="icon">🤖</div>
                    <div class="name">AI Kampagne</div>
                    <div class="desc">Vollautomatisch</div>
                </div>
            </div>
            
            <!-- Active Campaigns -->
            <h2 style="margin-bottom: 20px;">📊 Aktive Kampagnen</h2>
            <div class="campaigns-grid">
                {% for campaign in campaigns %}
                <div class="campaign-card">
                    <div class="campaign-card-header">
                        <div>
                            <div class="campaign-card-title">{{ campaign.name }}</div>
                            <div class="campaign-card-type">{{ campaign.type_icon }} {{ campaign.type }}</div>
                        </div>
                        <span class="campaign-status status-{{ campaign.status }}">{{ campaign.status_text }}</span>
                    </div>
                    <div class="campaign-card-body">
                        <div class="campaign-stats">
                            <div class="campaign-stat">
                                <div class="campaign-stat-value">{{ campaign.sent }}</div>
                                <div class="campaign-stat-label">Gesendet</div>
                            </div>
                            <div class="campaign-stat">
                                <div class="campaign-stat-value">{{ campaign.open_rate }}%</div>
                                <div class="campaign-stat-label">Geöffnet</div>
                            </div>
                            <div class="campaign-stat">
                                <div class="campaign-stat-value">{{ campaign.click_rate }}%</div>
                                <div class="campaign-stat-label">Geklickt</div>
                            </div>
                            <div class="campaign-stat">
                                <div class="campaign-stat-value">{{ campaign.conversions }}</div>
                                <div class="campaign-stat-label">Conversions</div>
                            </div>
                        </div>
                    </div>
                    <div class="campaign-card-footer">
                        <span style="color: #888; font-size: 0.85rem;">{{ campaign.audience }} Empfänger</span>
                        <div class="campaign-actions">
                            <button class="action-btn" onclick="viewCampaign({{ campaign.id }})">📊</button>
                            <button class="action-btn" onclick="editCampaign({{ campaign.id }})">✏️</button>
                            {% if campaign.status == 'running' %}
                            <button class="action-btn" onclick="pauseCampaign({{ campaign.id }})">⏸️</button>
                            {% else %}
                            <button class="action-btn" onclick="startCampaign({{ campaign.id }})">▶️</button>
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </main>
    </div>
    
    <!-- New Campaign Modal -->
    <div class="modal-overlay" id="modal-new-campaign">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">📧 Neue Kampagne erstellen</h2>
                <button class="modal-close" onclick="closeModal('new-campaign')">×</button>
            </div>
            <div class="modal-body">
                <form id="campaign-form">
                    <div class="form-group">
                        <label class="form-label">Kampagnen-Name *</label>
                        <input type="text" class="form-input" name="name" required placeholder="z.B. Smart Home Launch Q1 2025">
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Typ</label>
                            <select class="form-input" name="type" onchange="updateCampaignType(this.value)">
                                <option value="email">📧 E-Mail</option>
                                <option value="whatsapp">💬 WhatsApp</option>
                                <option value="sms">📱 SMS</option>
                                <option value="sequence">🔄 Multi-Step Sequenz</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Zielgruppe</label>
                            <select class="form-input" name="audience">
                                <option value="all_leads">Alle Leads</option>
                                <option value="hot_leads">🔥 Hot Leads (Score > 70)</option>
                                <option value="warm_leads">🌡️ Warm Leads</option>
                                <option value="cold_leads">❄️ Cold Leads</option>
                                <option value="customers">👥 Bestandskunden</option>
                                <option value="new_contacts">🆕 Neue Kontakte</option>
                                <option value="custom">⚙️ Custom Filter</option>
                            </select>
                        </div>
                    </div>
                    
                    <div id="email-fields">
                        <div class="form-group">
                            <label class="form-label">Betreff</label>
                            <input type="text" class="form-input" name="subject" placeholder="{{first_name}}, entdecke Smart Home Lösungen">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Nachricht</label>
                        <textarea class="form-input" name="content" rows="8" placeholder="Hallo {{first_name}},

ich hoffe, es geht Ihnen gut! Ich wollte Ihnen kurz von unseren neuesten Smart Home Lösungen erzählen...

Beste Grüße,
Ömer Coşkun
West Money Bau"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Personalisierungs-Variablen</label>
                        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                            <span class="tag" onclick="insertVariable('first_name')">{{first_name}}</span>
                            <span class="tag" onclick="insertVariable('last_name')">{{last_name}}</span>
                            <span class="tag" onclick="insertVariable('company')">{{company}}</span>
                            <span class="tag" onclick="insertVariable('job_title')">{{job_title}}</span>
                            <span class="tag" onclick="insertVariable('industry')">{{industry}}</span>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Versand</label>
                            <select class="form-input" name="send_time">
                                <option value="now">Sofort senden</option>
                                <option value="scheduled">Geplant</option>
                                <option value="optimal">🤖 Optimale Zeit (AI)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Geplant für</label>
                            <input type="datetime-local" class="form-input" name="scheduled_at">
                        </div>
                    </div>
                    
                    <!-- Sequence Builder (hidden by default) -->
                    <div id="sequence-builder" style="display: none;">
                        <label class="form-label">Sequenz-Schritte</label>
                        <div class="sequence-builder">
                            <div class="sequence-step">
                                <div class="sequence-step-number">1</div>
                                <div class="sequence-step-content">
                                    <select class="form-input" style="margin-bottom: 10px;">
                                        <option>📧 E-Mail senden</option>
                                        <option>💬 WhatsApp senden</option>
                                        <option>⏰ Warten</option>
                                    </select>
                                    <input type="text" class="form-input" placeholder="Betreff / Nachricht">
                                </div>
                            </div>
                            <div class="sequence-connector"></div>
                            <div class="sequence-step">
                                <div class="sequence-step-number">2</div>
                                <div class="sequence-step-content">
                                    <select class="form-input" style="margin-bottom: 10px;">
                                        <option>⏰ Warten (3 Tage)</option>
                                    </select>
                                </div>
                            </div>
                            <div class="sequence-connector"></div>
                            <div class="sequence-step">
                                <div class="sequence-step-number">3</div>
                                <div class="sequence-step-content">
                                    <select class="form-input" style="margin-bottom: 10px;">
                                        <option>📧 Follow-Up E-Mail</option>
                                    </select>
                                    <input type="text" class="form-input" placeholder="Follow-Up Nachricht">
                                </div>
                            </div>
                            <button type="button" class="btn btn-secondary" style="margin-top: 15px;" onclick="addSequenceStep()">
                                ➕ Schritt hinzufügen
                            </button>
                        </div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('new-campaign')">Abbrechen</button>
                <button class="btn btn-secondary" onclick="saveCampaign('draft')">📝 Als Entwurf</button>
                <button class="btn btn-primary" onclick="saveCampaign('send')">🚀 Kampagne starten</button>
            </div>
        </div>
    </div>
    
    <script>
        function openModal(type) {
            document.getElementById('modal-' + type).classList.add('active');
        }
        
        function closeModal(type) {
            document.getElementById('modal-' + type).classList.remove('active');
        }
        
        function createCampaign(type) {
            openModal('new-campaign');
            document.querySelector('select[name="type"]').value = type;
            updateCampaignType(type);
        }
        
        function updateCampaignType(type) {
            document.getElementById('email-fields').style.display = type !== 'whatsapp' ? 'block' : 'none';
            document.getElementById('sequence-builder').style.display = type === 'sequence' ? 'block' : 'none';
        }
        
        function insertVariable(variable) {
            const textarea = document.querySelector('textarea[name="content"]');
            const cursorPos = textarea.selectionStart;
            const text = textarea.value;
            textarea.value = text.substring(0, cursorPos) + '{{' + variable + '}}' + text.substring(cursorPos);
        }
        
        function addSequenceStep() {
            showToast('➕ Schritt hinzugefügt');
        }
        
        async function saveCampaign(action) {
            const form = document.getElementById('campaign-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            data.status = action === 'draft' ? 'draft' : 'scheduled';
            
            try {
                const response = await fetch('/api/campaigns', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    closeModal('new-campaign');
                    showToast(action === 'draft' ? '📝 Entwurf gespeichert!' : '🚀 Kampagne gestartet!');
                    setTimeout(() => location.reload(), 1500);
                }
            } catch (error) {
                showToast('❌ Fehler', 'error');
            }
        }
        
        function pauseCampaign(id) {
            fetch(`/api/campaigns/${id}/pause`, { method: 'POST' })
                .then(() => {
                    showToast('⏸️ Kampagne pausiert');
                    location.reload();
                });
        }
        
        function startCampaign(id) {
            fetch(`/api/campaigns/${id}/start`, { method: 'POST' })
                .then(() => {
                    showToast('▶️ Kampagne gestartet');
                    location.reload();
                });
        }
        
        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
        
        // Tag styling
        document.querySelectorAll('.tag').forEach(tag => {
            tag.style.cssText = 'display: inline-block; padding: 6px 12px; background: rgba(255,0,255,0.2); color: #ff00ff; border-radius: 20px; font-size: 0.85rem; cursor: pointer; transition: all 0.3s;';
        });
    </script>
</body>
</html>
"""


@campaigns_bp.route('/dashboard/campaigns')
def campaigns_page():
    """Campaigns dashboard page"""
    stats = {
        'total_sent': '12,450',
        'open_rate': 45.2,
        'click_rate': 12.8,
        'reply_rate': 5.3,
        'conversions': 156
    }
    
    campaigns = [
        {'id': 1, 'name': 'Smart Home Launch 2025', 'type': 'E-Mail', 'type_icon': '📧', 
         'status': 'running', 'status_text': 'Läuft', 'sent': 450, 'open_rate': 48.2, 
         'click_rate': 15.3, 'conversions': 12, 'audience': 500},
        {'id': 2, 'name': 'LOXONE Partner Outreach', 'type': 'WhatsApp', 'type_icon': '💬',
         'status': 'running', 'status_text': 'Läuft', 'sent': 120, 'open_rate': 92.0,
         'click_rate': 34.2, 'conversions': 8, 'audience': 150},
        {'id': 3, 'name': 'Cold Email Sequence', 'type': 'Sequenz', 'type_icon': '🔄',
         'status': 'paused', 'status_text': 'Pausiert', 'sent': 1200, 'open_rate': 38.5,
         'click_rate': 9.2, 'conversions': 24, 'audience': 1500},
        {'id': 4, 'name': 'Newsletter Januar', 'type': 'E-Mail', 'type_icon': '📧',
         'status': 'scheduled', 'status_text': 'Geplant', 'sent': 0, 'open_rate': 0,
         'click_rate': 0, 'conversions': 0, 'audience': 2500},
    ]
    
    return render_template_string(CAMPAIGNS_HTML, stats=stats, campaigns=campaigns)


@campaigns_bp.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get all campaigns"""
    campaigns = []
    return jsonify({'success': True, 'campaigns': campaigns})


@campaigns_bp.route('/api/campaigns', methods=['POST'])
def create_campaign():
    """Create a new campaign"""
    data = request.json
    
    campaign = {
        'id': random.randint(100, 9999),
        **data,
        'sent_count': 0,
        'open_count': 0,
        'click_count': 0,
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'success': True, 'campaign': campaign})


@campaigns_bp.route('/api/campaigns/<int:campaign_id>/start', methods=['POST'])
def start_campaign(campaign_id):
    """Start a campaign"""
    return jsonify({'success': True, 'message': f'Kampagne {campaign_id} gestartet'})


@campaigns_bp.route('/api/campaigns/<int:campaign_id>/pause', methods=['POST'])
def pause_campaign(campaign_id):
    """Pause a campaign"""
    return jsonify({'success': True, 'message': f'Kampagne {campaign_id} pausiert'})


@campaigns_bp.route('/api/campaigns/<int:campaign_id>/stats', methods=['GET'])
def get_campaign_stats(campaign_id):
    """Get campaign statistics"""
    stats = {
        'sent': 450,
        'delivered': 445,
        'opened': 215,
        'clicked': 68,
        'replied': 23,
        'bounced': 5,
        'unsubscribed': 2,
        'conversions': 12
    }
    return jsonify({'success': True, 'stats': stats})


def register_campaigns_blueprint(app):
    """Register campaigns blueprint"""
    app.register_blueprint(campaigns_bp)
    print("📧 CAMPAIGNS MODULE loaded!")


__all__ = ['campaigns_bp', 'register_campaigns_blueprint']
