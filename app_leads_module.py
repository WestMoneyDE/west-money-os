"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🎯 LEADS MODUL - WEST MONEY OS v12.0                                         ║
║  Lead Management mit Pipeline, Scoring & Auto-Qualifizierung                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Blueprint, render_template_string, request, jsonify
from datetime import datetime, timedelta
import json
import random

leads_bp = Blueprint('leads', __name__)

# ============================================================================
# LEADS DASHBOARD HTML
# ============================================================================

LEADS_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Leads - West Money OS</title>
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
        
        /* Stats */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
        }
        
        .stat-card .icon { font-size: 2rem; margin-bottom: 10px; }
        .stat-card .value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-card .label { color: #888; font-size: 0.9rem; margin-top: 5px; }
        .stat-card .change { font-size: 0.85rem; margin-top: 8px; }
        .stat-card .change.positive { color: #00ffff; }
        .stat-card .change.negative { color: #ff4757; }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 15px;
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
            background: linear-gradient(135deg, rgba(255,0,255,0.2), rgba(0,255,255,0.2));
            color: #ff00ff;
        }
        
        /* Pipeline View */
        .pipeline-container {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .pipeline-column {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 15px;
            min-height: 500px;
        }
        
        .pipeline-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid;
        }
        
        .stage-new { border-color: #74b9ff; }
        .stage-contacted { border-color: #a29bfe; }
        .stage-qualified { border-color: #ffeaa7; }
        .stage-proposal { border-color: #fd79a8; }
        .stage-negotiation { border-color: #81ecec; }
        .stage-won { border-color: #00ffff; }
        
        .pipeline-title { font-weight: 600; font-size: 0.9rem; }
        .pipeline-count {
            background: rgba(255,255,255,0.2);
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        .pipeline-value {
            font-size: 0.8rem;
            color: #888;
            margin-top: 5px;
        }
        
        /* Lead Card */
        .lead-card {
            background: rgba(255,255,255,0.08);
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 10px;
            cursor: grab;
            transition: all 0.3s;
            border-left: 3px solid transparent;
        }
        
        .lead-card:hover {
            background: rgba(255,255,255,0.12);
            transform: translateY(-2px);
        }
        
        .lead-card.hot { border-left-color: #ff4757; }
        .lead-card.warm { border-left-color: #00ffff; }
        .lead-card.cold { border-left-color: #74b9ff; }
        
        .lead-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }
        
        .lead-card-name { font-weight: 600; font-size: 0.95rem; }
        .lead-card-score {
            padding: 3px 8px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
        }
        
        .score-high { background: #ff4757; color: #fff; }
        .score-medium { background: #00ffff; color: #000; }
        .score-low { background: #74b9ff; color: #000; }
        
        .lead-card-company { font-size: 0.85rem; color: #888; margin-bottom: 8px; }
        
        .lead-card-value {
            font-size: 0.9rem;
            color: #00ffff;
            font-weight: 600;
        }
        
        .lead-card-meta {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-size: 0.75rem;
            color: #888;
        }
        
        /* Table View */
        .table-container {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            overflow: hidden;
            display: none;
        }
        
        .table-container.active { display: block; }
        .pipeline-container.active { display: grid; }
        
        .leads-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .leads-table th,
        .leads-table td {
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .leads-table th {
            background: rgba(0,0,0,0.3);
            color: #888;
            font-weight: 500;
            font-size: 0.85rem;
            text-transform: uppercase;
        }
        
        .leads-table tr:hover { background: rgba(255,255,255,0.05); }
        
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
        
        /* Toast */
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
                <a href="/dashboard/leads" class="active"><span>🎯</span> Leads</a>
                <a href="/broly"><span>🐉</span> Broly</a>
                <a href="/dashboard/campaigns"><span>📧</span> Kampagnen</a>
                <a href="/dashboard/invoices"><span>💰</span> Rechnungen</a>
                <a href="/dashboard/whatsapp"><span>💬</span> WhatsApp</a>
                <a href="/dashboard/ai-chat"><span>🤖</span> AI Chat</a>
                <a href="/dashboard/settings"><span>⚙️</span> Settings</a>
            </div>
        </nav>
        
        <main class="main">
            <div class="header">
                <h1 class="title">🎯 Lead Pipeline</h1>
                <div class="actions">
                    <button class="btn btn-secondary" onclick="importLeads()">📤 Import</button>
                    <button class="btn btn-secondary" onclick="autoProspect()">🔍 Auto-Prospect</button>
                    <button class="btn btn-primary" onclick="openModal('new-lead')">➕ Neuer Lead</button>
                </div>
            </div>
            
            <!-- Stats -->
            <div class="stats-row">
                <div class="stat-card">
                    <div class="icon">🎯</div>
                    <div class="value">{{ stats.total }}</div>
                    <div class="label">Leads gesamt</div>
                    <div class="change positive">+{{ stats.new_today }} heute</div>
                </div>
                <div class="stat-card">
                    <div class="icon">🔥</div>
                    <div class="value">{{ stats.hot }}</div>
                    <div class="label">Hot Leads</div>
                    <div class="change">Score > 70</div>
                </div>
                <div class="stat-card">
                    <div class="icon">💰</div>
                    <div class="value">€{{ stats.pipeline_value }}</div>
                    <div class="label">Pipeline Wert</div>
                    <div class="change positive">+12% vs. Vorwoche</div>
                </div>
                <div class="stat-card">
                    <div class="icon">📈</div>
                    <div class="value">{{ stats.conversion_rate }}%</div>
                    <div class="label">Conversion Rate</div>
                    <div class="change positive">+2.1%</div>
                </div>
                <div class="stat-card">
                    <div class="icon">⏱️</div>
                    <div class="value">{{ stats.avg_cycle }}</div>
                    <div class="label">Ø Sales Cycle</div>
                    <div class="change">Tage</div>
                </div>
            </div>
            
            <!-- View Tabs -->
            <div class="tabs">
                <button class="tab active" onclick="switchView('pipeline')">📊 Pipeline</button>
                <button class="tab" onclick="switchView('table')">📋 Tabelle</button>
                <button class="tab" onclick="switchView('analytics')">📈 Analytics</button>
            </div>
            
            <!-- Pipeline View -->
            <div class="pipeline-container active" id="pipeline-view">
                <div class="pipeline-column">
                    <div class="pipeline-header stage-new">
                        <div>
                            <div class="pipeline-title">🆕 Neu</div>
                            <div class="pipeline-value">€45,000</div>
                        </div>
                        <span class="pipeline-count">12</span>
                    </div>
                    <div class="pipeline-leads" data-stage="new">
                        <!-- Leads here -->
                    </div>
                </div>
                
                <div class="pipeline-column">
                    <div class="pipeline-header stage-contacted">
                        <div>
                            <div class="pipeline-title">📞 Kontaktiert</div>
                            <div class="pipeline-value">€78,000</div>
                        </div>
                        <span class="pipeline-count">8</span>
                    </div>
                    <div class="pipeline-leads" data-stage="contacted"></div>
                </div>
                
                <div class="pipeline-column">
                    <div class="pipeline-header stage-qualified">
                        <div>
                            <div class="pipeline-title">✅ Qualifiziert</div>
                            <div class="pipeline-value">€120,000</div>
                        </div>
                        <span class="pipeline-count">6</span>
                    </div>
                    <div class="pipeline-leads" data-stage="qualified"></div>
                </div>
                
                <div class="pipeline-column">
                    <div class="pipeline-header stage-proposal">
                        <div>
                            <div class="pipeline-title">📋 Angebot</div>
                            <div class="pipeline-value">€89,000</div>
                        </div>
                        <span class="pipeline-count">4</span>
                    </div>
                    <div class="pipeline-leads" data-stage="proposal"></div>
                </div>
                
                <div class="pipeline-column">
                    <div class="pipeline-header stage-negotiation">
                        <div>
                            <div class="pipeline-title">🤝 Verhandlung</div>
                            <div class="pipeline-value">€156,000</div>
                        </div>
                        <span class="pipeline-count">3</span>
                    </div>
                    <div class="pipeline-leads" data-stage="negotiation"></div>
                </div>
                
                <div class="pipeline-column">
                    <div class="pipeline-header stage-won">
                        <div>
                            <div class="pipeline-title">🎉 Gewonnen</div>
                            <div class="pipeline-value">€234,000</div>
                        </div>
                        <span class="pipeline-count">15</span>
                    </div>
                    <div class="pipeline-leads" data-stage="won"></div>
                </div>
            </div>
            
            <!-- Table View -->
            <div class="table-container" id="table-view">
                <table class="leads-table">
                    <thead>
                        <tr>
                            <th>Lead</th>
                            <th>Firma</th>
                            <th>Wert</th>
                            <th>Score</th>
                            <th>Stage</th>
                            <th>Quelle</th>
                            <th>Letzter Kontakt</th>
                            <th>Aktionen</th>
                        </tr>
                    </thead>
                    <tbody id="leads-table-body">
                        <!-- Filled by JS -->
                    </tbody>
                </table>
            </div>
        </main>
    </div>
    
    <!-- New Lead Modal -->
    <div class="modal-overlay" id="modal-new-lead">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">➕ Neuer Lead</h2>
                <button class="modal-close" onclick="closeModal('new-lead')">×</button>
            </div>
            <div class="modal-body">
                <form id="lead-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Vorname *</label>
                            <input type="text" class="form-input" name="first_name" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Nachname *</label>
                            <input type="text" class="form-input" name="last_name" required>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">E-Mail *</label>
                            <input type="email" class="form-input" name="email" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Telefon</label>
                            <input type="tel" class="form-input" name="phone">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Firma *</label>
                            <input type="text" class="form-input" name="company_name" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Position</label>
                            <input type="text" class="form-input" name="job_title">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Deal Wert (€)</label>
                            <input type="number" class="form-input" name="deal_value" placeholder="z.B. 25000">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Quelle</label>
                            <select class="form-input" name="source">
                                <option value="website">Website</option>
                                <option value="referral">Empfehlung</option>
                                <option value="cold_outreach">Cold Outreach</option>
                                <option value="event">Event</option>
                                <option value="explorium">Explorium</option>
                                <option value="linkedin">LinkedIn</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Interesse</label>
                        <select class="form-input" name="interest">
                            <option value="smart_home">Smart Home / LOXONE</option>
                            <option value="construction">Bau & Renovierung</option>
                            <option value="consulting">Beratung</option>
                            <option value="partnership">Partnerschaft</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Notizen</label>
                        <textarea class="form-input" name="notes" rows="3"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('new-lead')">Abbrechen</button>
                <button class="btn btn-primary" onclick="saveLead()">💾 Speichern</button>
            </div>
        </div>
    </div>
    
    <script>
        // Sample Leads Data
        const leads = [
            { id: 1, first_name: 'Max', last_name: 'Mustermann', company: 'TechCorp GmbH', value: 45000, score: 85, stage: 'qualified', temperature: 'hot', source: 'website', last_contact: '2024-12-23' },
            { id: 2, first_name: 'Anna', last_name: 'Schmidt', company: 'Building AG', value: 78000, score: 72, stage: 'proposal', temperature: 'warm', source: 'referral', last_contact: '2024-12-22' },
            { id: 3, first_name: 'Stefan', last_name: 'Weber', company: 'ImmoVest', value: 32000, score: 45, stage: 'new', temperature: 'cold', source: 'explorium', last_contact: null },
            { id: 4, first_name: 'Lisa', last_name: 'Bauer', company: 'Architekten Plus', value: 156000, score: 91, stage: 'negotiation', temperature: 'hot', source: 'linkedin', last_contact: '2024-12-24' },
            { id: 5, first_name: 'Thomas', last_name: 'Koch', company: 'Smart Living', value: 25000, score: 68, stage: 'contacted', temperature: 'warm', source: 'event', last_contact: '2024-12-20' },
            { id: 6, first_name: 'Julia', last_name: 'Hoffmann', company: 'HomeDesign GmbH', value: 89000, score: 78, stage: 'qualified', temperature: 'hot', source: 'website', last_contact: '2024-12-21' },
        ];
        
        // Render Pipeline
        function renderPipeline() {
            const stages = ['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won'];
            
            stages.forEach(stage => {
                const container = document.querySelector(`.pipeline-leads[data-stage="${stage}"]`);
                if (!container) return;
                
                const stageLeads = leads.filter(l => l.stage === stage);
                container.innerHTML = stageLeads.map(lead => `
                    <div class="lead-card ${lead.temperature}" draggable="true" data-id="${lead.id}">
                        <div class="lead-card-header">
                            <div class="lead-card-name">${lead.first_name} ${lead.last_name}</div>
                            <span class="lead-card-score ${lead.score >= 70 ? 'score-high' : lead.score >= 50 ? 'score-medium' : 'score-low'}">${lead.score}</span>
                        </div>
                        <div class="lead-card-company">${lead.company}</div>
                        <div class="lead-card-value">€${lead.value.toLocaleString()}</div>
                        <div class="lead-card-meta">
                            <span>${lead.source}</span>
                            <span>${lead.last_contact || 'Neu'}</span>
                        </div>
                    </div>
                `).join('');
            });
        }
        
        // Render Table
        function renderTable() {
            const tbody = document.getElementById('leads-table-body');
            tbody.innerHTML = leads.map(lead => `
                <tr>
                    <td><strong>${lead.first_name} ${lead.last_name}</strong></td>
                    <td>${lead.company}</td>
                    <td>€${lead.value.toLocaleString()}</td>
                    <td><span class="lead-card-score ${lead.score >= 70 ? 'score-high' : lead.score >= 50 ? 'score-medium' : 'score-low'}">${lead.score}</span></td>
                    <td>${lead.stage}</td>
                    <td>${lead.source}</td>
                    <td>${lead.last_contact || '-'}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 6px 10px; font-size: 0.8rem;">👁️</button>
                        <button class="btn btn-primary" style="padding: 6px 10px; font-size: 0.8rem;">📧</button>
                    </td>
                </tr>
            `).join('');
        }
        
        // Switch View
        function switchView(view) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('pipeline-view').style.display = view === 'pipeline' ? 'grid' : 'none';
            document.getElementById('table-view').style.display = view === 'table' ? 'block' : 'none';
        }
        
        // Modal
        function openModal(type) {
            document.getElementById('modal-' + type).classList.add('active');
        }
        
        function closeModal(type) {
            document.getElementById('modal-' + type).classList.remove('active');
        }
        
        // Save Lead
        async function saveLead() {
            const form = document.getElementById('lead-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch('/api/leads', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    closeModal('new-lead');
                    showToast('✅ Lead erstellt!');
                    setTimeout(() => location.reload(), 1000);
                }
            } catch (error) {
                showToast('❌ Fehler', 'error');
            }
        }
        
        // Auto Prospect
        function autoProspect() {
            showToast('🔍 Suche neue Leads via Explorium...');
            // Trigger Explorium search
        }
        
        function importLeads() {
            showToast('📤 Import-Dialog öffnen...');
        }
        
        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
        
        // Init
        document.addEventListener('DOMContentLoaded', function() {
            renderPipeline();
            renderTable();
        });
    </script>
</body>
</html>
"""


# ============================================================================
# API ROUTES
# ============================================================================

@leads_bp.route('/dashboard/leads')
def leads_page():
    """Leads dashboard page"""
    stats = {
        'total': 247,
        'new_today': 12,
        'hot': 34,
        'pipeline_value': '523,000',
        'conversion_rate': 8.5,
        'avg_cycle': 23
    }
    return render_template_string(LEADS_HTML, stats=stats)


@leads_bp.route('/api/leads', methods=['GET'])
def get_leads():
    """Get all leads"""
    stage = request.args.get('stage')
    temperature = request.args.get('temperature')
    
    leads = [
        {'id': 1, 'first_name': 'Max', 'last_name': 'Mustermann', 'company_name': 'TechCorp', 
         'score': 85, 'stage': 'qualified', 'deal_value': 45000},
    ]
    
    return jsonify({'success': True, 'leads': leads})


@leads_bp.route('/api/leads', methods=['POST'])
def create_lead():
    """Create a new lead"""
    data = request.json
    
    # Auto-calculate initial score
    score = 20  # Base score
    if data.get('email'): score += 15
    if data.get('phone'): score += 10
    if data.get('company_name'): score += 15
    if data.get('job_title'): score += 10
    if data.get('deal_value') and int(data.get('deal_value', 0)) > 50000: score += 20
    
    lead = {
        'id': random.randint(100, 9999),
        **data,
        'score': min(score, 100),
        'stage': 'new',
        'temperature': 'cold' if score < 40 else ('warm' if score < 70 else 'hot'),
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'success': True, 'lead': lead})


@leads_bp.route('/api/leads/<int:lead_id>/stage', methods=['PUT'])
def update_lead_stage(lead_id):
    """Update lead stage (drag & drop in pipeline)"""
    data = request.json
    new_stage = data.get('stage')
    
    valid_stages = ['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost']
    if new_stage not in valid_stages:
        return jsonify({'success': False, 'error': 'Invalid stage'}), 400
    
    return jsonify({'success': True, 'lead_id': lead_id, 'stage': new_stage})


@leads_bp.route('/api/leads/<int:lead_id>/score', methods=['POST'])
def recalculate_score(lead_id):
    """Recalculate lead score based on engagement"""
    # In production: Calculate based on activities
    new_score = random.randint(50, 95)
    
    return jsonify({
        'success': True,
        'lead_id': lead_id,
        'score': new_score,
        'temperature': 'hot' if new_score >= 70 else ('warm' if new_score >= 50 else 'cold')
    })


@leads_bp.route('/api/leads/auto-prospect', methods=['POST'])
def auto_prospect():
    """Auto-prospect new leads from Explorium"""
    data = request.json
    
    # Parameters for Explorium search
    industry = data.get('industry', 'construction')
    location = data.get('location', 'DE')
    company_size = data.get('company_size', '10-500')
    
    # Simulated results
    new_leads = [
        {'company': 'SmartBuild GmbH', 'contact': 'Peter Müller', 'score': 72},
        {'company': 'HomeAutomation AG', 'contact': 'Sandra Weber', 'score': 68},
        {'company': 'ArchitekturPlus', 'contact': 'Michael Schmidt', 'score': 81},
    ]
    
    return jsonify({
        'success': True,
        'leads_found': len(new_leads),
        'leads': new_leads,
        'message': f'{len(new_leads)} neue Leads gefunden und importiert'
    })


def register_leads_blueprint(app):
    """Register leads blueprint"""
    app.register_blueprint(leads_bp)
    print("🎯 LEADS MODULE loaded!")


__all__ = ['leads_bp', 'register_leads_blueprint']
