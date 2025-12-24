"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  📇 KONTAKTE MODUL - WEST MONEY OS v12.0                                      ║
║  Vollständige Kontaktverwaltung mit HubSpot Sync & WhatsApp Consent          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Blueprint, render_template_string, request, jsonify, session, send_file
from datetime import datetime
import json
import csv
import io
import requests
import os

contacts_bp = Blueprint('contacts', __name__)

# ============================================================================
# KONTAKTE DASHBOARD HTML
# ============================================================================

CONTACTS_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📇 Kontakte - West Money OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .container {
            display: flex;
            min-height: 100vh;
        }
        
        /* Sidebar */
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
            background: linear-gradient(135deg, #ffd700, #ff6b35);
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
            background: rgba(255,215,0,0.1);
            color: #ffd700;
        }
        
        /* Main */
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
        
        .title {
            font-size: 2rem;
            font-weight: 700;
        }
        
        .actions {
            display: flex;
            gap: 12px;
        }
        
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
            background: linear-gradient(135deg, #ffd700, #ff6b35);
            color: #000;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255,215,0,0.3);
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .btn-success { background: linear-gradient(135deg, #2ed573, #1e90ff); color: #fff; }
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
            color: #ffd700;
        }
        .stat-card .label {
            color: #888;
            font-size: 0.85rem;
            margin-top: 5px;
        }
        
        /* Filters */
        .filters {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .search-box {
            flex: 1;
            min-width: 300px;
            position: relative;
        }
        
        .search-box input {
            width: 100%;
            padding: 12px 16px 12px 45px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: #fff;
            font-size: 1rem;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: #ffd700;
        }
        
        .search-box::before {
            content: '🔍';
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
        }
        
        .filter-select {
            padding: 12px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: #fff;
            font-size: 0.95rem;
            min-width: 150px;
        }
        
        /* Table */
        .table-container {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            overflow: hidden;
        }
        
        .contacts-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .contacts-table th,
        .contacts-table td {
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .contacts-table th {
            background: rgba(0,0,0,0.3);
            color: #888;
            font-weight: 500;
            font-size: 0.85rem;
            text-transform: uppercase;
        }
        
        .contacts-table tr:hover {
            background: rgba(255,255,255,0.05);
        }
        
        .contact-avatar {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #ffd700, #ff6b35);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: #000;
        }
        
        .contact-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .contact-name {
            font-weight: 600;
        }
        
        .contact-email {
            font-size: 0.85rem;
            color: #888;
        }
        
        .tag {
            display: inline-block;
            padding: 4px 10px;
            background: rgba(255,215,0,0.2);
            color: #ffd700;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-right: 5px;
        }
        
        .consent-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .consent-yes { background: rgba(46, 213, 115, 0.2); color: #2ed573; }
        .consent-no { background: rgba(255, 71, 87, 0.2); color: #ff4757; }
        .consent-pending { background: rgba(255, 165, 2, 0.2); color: #ffa502; }
        
        .action-btn {
            padding: 8px 12px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            margin-right: 5px;
            transition: all 0.3s;
        }
        
        .action-btn:hover {
            background: rgba(255,215,0,0.2);
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
            max-width: 700px;
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
            border-color: #ffd700;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
            padding: 20px;
        }
        
        .pagination button {
            padding: 10px 16px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .pagination button:hover,
        .pagination button.active {
            background: rgba(255,215,0,0.2);
            border-color: #ffd700;
        }
        
        /* Toast */
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 16px 24px;
            background: #2ed573;
            color: #000;
            border-radius: 10px;
            font-weight: 600;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        /* Bulk Actions */
        .bulk-actions {
            display: none;
            align-items: center;
            gap: 15px;
            padding: 15px 20px;
            background: rgba(255,215,0,0.1);
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .bulk-actions.active { display: flex; }
        
        .checkbox {
            width: 20px;
            height: 20px;
            accent-color: #ffd700;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar -->
        <nav class="sidebar">
            <div class="logo">
                <span class="logo-icon">💰</span>
                <span class="logo-text">West Money OS</span>
            </div>
            
            <div class="nav">
                <a href="/dashboard"><span>📊</span> Dashboard</a>
                <a href="/dashboard/contacts" class="active"><span>📇</span> Kontakte</a>
                <a href="/broly"><span>🐉</span> Broly</a>
                <a href="/dashboard/leads"><span>🎯</span> Leads</a>
                <a href="/dashboard/campaigns"><span>📧</span> Kampagnen</a>
                <a href="/dashboard/whatsapp"><span>💬</span> WhatsApp</a>
                <a href="/dashboard/ai-chat"><span>🤖</span> AI Chat</a>
                <a href="/dashboard/settings"><span>⚙️</span> Settings</a>
            </div>
        </nav>
        
        <!-- Main -->
        <main class="main">
            <div class="header">
                <h1 class="title">📇 Kontakte</h1>
                <div class="actions">
                    <button class="btn btn-secondary" onclick="exportContacts()">
                        📥 Export
                    </button>
                    <button class="btn btn-secondary" onclick="openModal('import')">
                        📤 Import
                    </button>
                    <button class="btn btn-success" onclick="syncHubSpot()">
                        🔄 HubSpot Sync
                    </button>
                    <button class="btn btn-primary" onclick="openModal('new-contact')">
                        ➕ Neuer Kontakt
                    </button>
                </div>
            </div>
            
            <!-- Stats -->
            <div class="stats-row">
                <div class="stat-card">
                    <div class="icon">👥</div>
                    <div class="value" id="stat-total">{{ stats.total }}</div>
                    <div class="label">Kontakte gesamt</div>
                </div>
                <div class="stat-card">
                    <div class="icon">✅</div>
                    <div class="value" id="stat-consent">{{ stats.with_consent }}</div>
                    <div class="label">WhatsApp Consent</div>
                </div>
                <div class="stat-card">
                    <div class="icon">🔄</div>
                    <div class="value" id="stat-synced">{{ stats.synced }}</div>
                    <div class="label">HubSpot synced</div>
                </div>
                <div class="stat-card">
                    <div class="icon">📈</div>
                    <div class="value" id="stat-new">{{ stats.new_this_week }}</div>
                    <div class="label">Diese Woche neu</div>
                </div>
            </div>
            
            <!-- Filters -->
            <div class="filters">
                <div class="search-box">
                    <input type="text" id="search" placeholder="Suche nach Name, E-Mail, Firma..." oninput="searchContacts()">
                </div>
                <select class="filter-select" id="filter-consent" onchange="filterContacts()">
                    <option value="">Alle Consent</option>
                    <option value="yes">✅ Zugestimmt</option>
                    <option value="no">❌ Abgelehnt</option>
                    <option value="pending">⏳ Ausstehend</option>
                </select>
                <select class="filter-select" id="filter-source" onchange="filterContacts()">
                    <option value="">Alle Quellen</option>
                    <option value="hubspot">HubSpot</option>
                    <option value="manual">Manuell</option>
                    <option value="import">Import</option>
                    <option value="website">Website</option>
                </select>
                <select class="filter-select" id="filter-tags" onchange="filterContacts()">
                    <option value="">Alle Tags</option>
                    <option value="kunde">Kunde</option>
                    <option value="lead">Lead</option>
                    <option value="partner">Partner</option>
                    <option value="vip">VIP</option>
                </select>
            </div>
            
            <!-- Bulk Actions -->
            <div class="bulk-actions" id="bulk-actions">
                <span id="selected-count">0 ausgewählt</span>
                <button class="btn btn-secondary" onclick="bulkTag()">🏷️ Tags</button>
                <button class="btn btn-secondary" onclick="bulkSendWhatsApp()">💬 WhatsApp</button>
                <button class="btn btn-secondary" onclick="bulkExport()">📥 Export</button>
                <button class="btn btn-danger" onclick="bulkDelete()">🗑️ Löschen</button>
            </div>
            
            <!-- Table -->
            <div class="table-container">
                <table class="contacts-table">
                    <thead>
                        <tr>
                            <th><input type="checkbox" class="checkbox" onclick="toggleAllContacts(this)"></th>
                            <th>Kontakt</th>
                            <th>Firma</th>
                            <th>Telefon</th>
                            <th>WhatsApp Consent</th>
                            <th>Tags</th>
                            <th>Quelle</th>
                            <th>Aktionen</th>
                        </tr>
                    </thead>
                    <tbody id="contacts-table">
                        {% for contact in contacts %}
                        <tr data-id="{{ contact.id }}">
                            <td><input type="checkbox" class="checkbox contact-checkbox" value="{{ contact.id }}" onchange="updateBulkActions()"></td>
                            <td>
                                <div class="contact-info">
                                    <div class="contact-avatar">{{ contact.first_name[0] }}{{ contact.last_name[0] if contact.last_name else '' }}</div>
                                    <div>
                                        <div class="contact-name">{{ contact.first_name }} {{ contact.last_name }}</div>
                                        <div class="contact-email">{{ contact.email }}</div>
                                    </div>
                                </div>
                            </td>
                            <td>{{ contact.company or '-' }}</td>
                            <td>{{ contact.phone or '-' }}</td>
                            <td>
                                <span class="consent-badge consent-{{ contact.whatsapp_consent }}">
                                    {% if contact.whatsapp_consent == 'yes' %}✅ Ja
                                    {% elif contact.whatsapp_consent == 'no' %}❌ Nein
                                    {% else %}⏳ Ausstehend{% endif %}
                                </span>
                            </td>
                            <td>
                                {% for tag in contact.tags %}
                                <span class="tag">{{ tag }}</span>
                                {% endfor %}
                            </td>
                            <td>{{ contact.source }}</td>
                            <td>
                                <button class="action-btn" onclick="viewContact({{ contact.id }})" title="Ansehen">👁️</button>
                                <button class="action-btn" onclick="editContact({{ contact.id }})" title="Bearbeiten">✏️</button>
                                <button class="action-btn" onclick="sendWhatsApp({{ contact.id }})" title="WhatsApp">💬</button>
                                <button class="action-btn" onclick="deleteContact({{ contact.id }})" title="Löschen">🗑️</button>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <!-- Pagination -->
            <div class="pagination">
                <button onclick="changePage(-1)">← Zurück</button>
                <button class="active">1</button>
                <button>2</button>
                <button>3</button>
                <button onclick="changePage(1)">Weiter →</button>
            </div>
        </main>
    </div>
    
    <!-- New Contact Modal -->
    <div class="modal-overlay" id="modal-new-contact">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">➕ Neuer Kontakt</h2>
                <button class="modal-close" onclick="closeModal('new-contact')">×</button>
            </div>
            <div class="modal-body">
                <form id="contact-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Vorname *</label>
                            <input type="text" class="form-input" name="first_name" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Nachname</label>
                            <input type="text" class="form-input" name="last_name">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">E-Mail *</label>
                            <input type="email" class="form-input" name="email" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Telefon</label>
                            <input type="tel" class="form-input" name="phone" placeholder="+49...">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Firma</label>
                            <input type="text" class="form-input" name="company">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Position</label>
                            <input type="text" class="form-input" name="job_title">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">WhatsApp Consent</label>
                            <select class="form-input" name="whatsapp_consent">
                                <option value="pending">⏳ Ausstehend</option>
                                <option value="yes">✅ Ja</option>
                                <option value="no">❌ Nein</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Tags</label>
                            <input type="text" class="form-input" name="tags" placeholder="lead, interessent, ...">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Notizen</label>
                        <textarea class="form-input" name="notes" rows="3" style="resize: vertical;"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('new-contact')">Abbrechen</button>
                <button class="btn btn-primary" onclick="saveContact()">💾 Speichern</button>
            </div>
        </div>
    </div>
    
    <!-- Import Modal -->
    <div class="modal-overlay" id="modal-import">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">📤 Kontakte importieren</h2>
                <button class="modal-close" onclick="closeModal('import')">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">CSV Datei auswählen</label>
                    <input type="file" class="form-input" id="import-file" accept=".csv,.xlsx">
                </div>
                <div class="form-group">
                    <label class="form-label">Import-Quelle</label>
                    <select class="form-input" id="import-source">
                        <option value="csv">CSV Datei</option>
                        <option value="hubspot">HubSpot</option>
                        <option value="excel">Excel</option>
                    </select>
                </div>
                <div style="background: rgba(255,215,0,0.1); padding: 15px; border-radius: 10px; margin-top: 15px;">
                    <strong>📋 CSV Format:</strong><br>
                    <small>first_name, last_name, email, phone, company, tags</small>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('import')">Abbrechen</button>
                <button class="btn btn-primary" onclick="importContacts()">📤 Importieren</button>
            </div>
        </div>
    </div>
    
    <!-- View Contact Modal -->
    <div class="modal-overlay" id="modal-view-contact">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">👤 Kontakt Details</h2>
                <button class="modal-close" onclick="closeModal('view-contact')">×</button>
            </div>
            <div class="modal-body" id="contact-details">
                <!-- Filled by JavaScript -->
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('view-contact')">Schließen</button>
                <button class="btn btn-primary" onclick="editCurrentContact()">✏️ Bearbeiten</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentContactId = null;
        let selectedContacts = [];
        
        // Modal Functions
        function openModal(type) {
            document.getElementById('modal-' + type).classList.add('active');
        }
        
        function closeModal(type) {
            document.getElementById('modal-' + type).classList.remove('active');
        }
        
        // Toast Notification
        function showToast(message, type = 'success') {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.style.background = type === 'success' ? '#2ed573' : '#ff4757';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
        
        // CRUD Operations
        async function saveContact() {
            const form = document.getElementById('contact-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            // Convert tags string to array
            if (data.tags) {
                data.tags = data.tags.split(',').map(t => t.trim()).filter(t => t);
            }
            
            try {
                const response = await fetch('/api/contacts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    closeModal('new-contact');
                    showToast('✅ Kontakt erfolgreich erstellt!');
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showToast('❌ Fehler: ' + result.error, 'error');
                }
            } catch (error) {
                showToast('❌ Fehler beim Speichern', 'error');
            }
        }
        
        async function viewContact(id) {
            currentContactId = id;
            
            try {
                const response = await fetch(`/api/contacts/${id}`);
                const result = await response.json();
                
                if (result.success) {
                    const c = result.contact;
                    document.getElementById('contact-details').innerHTML = `
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <div>
                                <p style="color: #888; margin-bottom: 5px;">Name</p>
                                <p style="font-size: 1.2rem; font-weight: 600;">${c.first_name} ${c.last_name || ''}</p>
                            </div>
                            <div>
                                <p style="color: #888; margin-bottom: 5px;">E-Mail</p>
                                <p>${c.email}</p>
                            </div>
                            <div>
                                <p style="color: #888; margin-bottom: 5px;">Telefon</p>
                                <p>${c.phone || '-'}</p>
                            </div>
                            <div>
                                <p style="color: #888; margin-bottom: 5px;">Firma</p>
                                <p>${c.company || '-'}</p>
                            </div>
                            <div>
                                <p style="color: #888; margin-bottom: 5px;">WhatsApp Consent</p>
                                <span class="consent-badge consent-${c.whatsapp_consent}">
                                    ${c.whatsapp_consent === 'yes' ? '✅ Ja' : c.whatsapp_consent === 'no' ? '❌ Nein' : '⏳ Ausstehend'}
                                </span>
                            </div>
                            <div>
                                <p style="color: #888; margin-bottom: 5px;">Quelle</p>
                                <p>${c.source}</p>
                            </div>
                            <div style="grid-column: span 2;">
                                <p style="color: #888; margin-bottom: 5px;">Tags</p>
                                <p>${c.tags ? c.tags.map(t => '<span class="tag">' + t + '</span>').join('') : '-'}</p>
                            </div>
                            <div style="grid-column: span 2;">
                                <p style="color: #888; margin-bottom: 5px;">Notizen</p>
                                <p>${c.notes || '-'}</p>
                            </div>
                            <div style="grid-column: span 2;">
                                <p style="color: #888; margin-bottom: 5px;">Erstellt am</p>
                                <p>${new Date(c.created_at).toLocaleString('de-DE')}</p>
                            </div>
                        </div>
                    `;
                    openModal('view-contact');
                }
            } catch (error) {
                showToast('❌ Fehler beim Laden', 'error');
            }
        }
        
        async function deleteContact(id) {
            if (!confirm('Kontakt wirklich löschen?')) return;
            
            try {
                const response = await fetch(`/api/contacts/${id}`, { method: 'DELETE' });
                const result = await response.json();
                
                if (result.success) {
                    showToast('✅ Kontakt gelöscht');
                    document.querySelector(`tr[data-id="${id}"]`).remove();
                }
            } catch (error) {
                showToast('❌ Fehler beim Löschen', 'error');
            }
        }
        
        // Search & Filter
        function searchContacts() {
            const query = document.getElementById('search').value.toLowerCase();
            const rows = document.querySelectorAll('#contacts-table tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        }
        
        function filterContacts() {
            const consent = document.getElementById('filter-consent').value;
            const source = document.getElementById('filter-source').value;
            const tag = document.getElementById('filter-tags').value;
            
            // In production: API call with filters
            console.log('Filter:', { consent, source, tag });
        }
        
        // Bulk Actions
        function toggleAllContacts(checkbox) {
            const checkboxes = document.querySelectorAll('.contact-checkbox');
            checkboxes.forEach(cb => cb.checked = checkbox.checked);
            updateBulkActions();
        }
        
        function updateBulkActions() {
            const checked = document.querySelectorAll('.contact-checkbox:checked');
            selectedContacts = Array.from(checked).map(cb => cb.value);
            
            const bulkActions = document.getElementById('bulk-actions');
            const countSpan = document.getElementById('selected-count');
            
            if (selectedContacts.length > 0) {
                bulkActions.classList.add('active');
                countSpan.textContent = selectedContacts.length + ' ausgewählt';
            } else {
                bulkActions.classList.remove('active');
            }
        }
        
        async function bulkDelete() {
            if (!confirm(`${selectedContacts.length} Kontakte wirklich löschen?`)) return;
            
            try {
                const response = await fetch('/api/contacts/bulk-delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids: selectedContacts })
                });
                
                if (response.ok) {
                    showToast('✅ Kontakte gelöscht');
                    setTimeout(() => location.reload(), 1000);
                }
            } catch (error) {
                showToast('❌ Fehler', 'error');
            }
        }
        
        // Export
        async function exportContacts() {
            window.location.href = '/api/contacts/export?format=csv';
        }
        
        // Import
        async function importContacts() {
            const file = document.getElementById('import-file').files[0];
            if (!file) {
                showToast('❌ Bitte Datei auswählen', 'error');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('source', document.getElementById('import-source').value);
            
            try {
                const response = await fetch('/api/contacts/import', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    closeModal('import');
                    showToast(`✅ ${result.imported} Kontakte importiert!`);
                    setTimeout(() => location.reload(), 1000);
                }
            } catch (error) {
                showToast('❌ Import fehlgeschlagen', 'error');
            }
        }
        
        // HubSpot Sync
        async function syncHubSpot() {
            showToast('🔄 HubSpot Sync gestartet...');
            
            try {
                const response = await fetch('/api/contacts/sync-hubspot', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    showToast(`✅ ${result.synced} Kontakte synchronisiert!`);
                    setTimeout(() => location.reload(), 2000);
                }
            } catch (error) {
                showToast('❌ Sync fehlgeschlagen', 'error');
            }
        }
        
        // WhatsApp
        function sendWhatsApp(id) {
            // In production: Open WhatsApp compose
            showToast('💬 WhatsApp wird geöffnet...');
        }
        
        function bulkSendWhatsApp() {
            showToast(`💬 WhatsApp an ${selectedContacts.length} Kontakte...`);
        }
    </script>
</body>
</html>
"""


# ============================================================================
# API ROUTES
# ============================================================================

@contacts_bp.route('/dashboard/contacts')
def contacts_page():
    """Contacts dashboard page"""
    # Sample data - in production: Query from database
    contacts = [
        {'id': 1, 'first_name': 'Max', 'last_name': 'Mustermann', 'email': 'max@example.com', 
         'phone': '+49 170 1234567', 'company': 'TechCorp GmbH', 'whatsapp_consent': 'yes',
         'tags': ['kunde', 'vip'], 'source': 'hubspot'},
        {'id': 2, 'first_name': 'Anna', 'last_name': 'Schmidt', 'email': 'anna@building.de',
         'phone': '+49 171 9876543', 'company': 'Building AG', 'whatsapp_consent': 'pending',
         'tags': ['lead'], 'source': 'website'},
        {'id': 3, 'first_name': 'Stefan', 'last_name': 'Weber', 'email': 'stefan@immo.com',
         'phone': None, 'company': 'ImmoVest', 'whatsapp_consent': 'no',
         'tags': ['interessent'], 'source': 'manual'},
    ]
    
    stats = {
        'total': 1247,
        'with_consent': 892,
        'synced': 1089,
        'new_this_week': 34
    }
    
    return render_template_string(CONTACTS_HTML, contacts=contacts, stats=stats)


@contacts_bp.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts with filters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search', '')
    consent = request.args.get('consent', '')
    source = request.args.get('source', '')
    
    # In production: Query from database with pagination
    contacts = [
        {'id': 1, 'first_name': 'Max', 'last_name': 'Mustermann', 'email': 'max@example.com'},
        {'id': 2, 'first_name': 'Anna', 'last_name': 'Schmidt', 'email': 'anna@building.de'},
    ]
    
    return jsonify({
        'success': True,
        'contacts': contacts,
        'total': len(contacts),
        'page': page,
        'per_page': per_page
    })


@contacts_bp.route('/api/contacts', methods=['POST'])
def create_contact():
    """Create a new contact"""
    data = request.json
    
    # Validate required fields
    if not data.get('email'):
        return jsonify({'success': False, 'error': 'E-Mail ist erforderlich'}), 400
    
    if not data.get('first_name'):
        return jsonify({'success': False, 'error': 'Vorname ist erforderlich'}), 400
    
    # In production: Save to database
    contact = {
        'id': 999,  # Auto-generated
        **data,
        'source': 'manual',
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'success': True, 'contact': contact})


@contacts_bp.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get single contact"""
    # In production: Query from database
    contact = {
        'id': contact_id,
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'email': 'max@example.com',
        'phone': '+49 170 1234567',
        'company': 'TechCorp GmbH',
        'job_title': 'CEO',
        'whatsapp_consent': 'yes',
        'tags': ['kunde', 'vip'],
        'source': 'hubspot',
        'notes': 'Sehr interessiert an Smart Home Lösungen.',
        'hubspot_id': 'hs_12345',
        'created_at': '2024-12-01T10:30:00'
    }
    
    return jsonify({'success': True, 'contact': contact})


@contacts_bp.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update a contact"""
    data = request.json
    # In production: Update in database
    return jsonify({'success': True, 'message': f'Kontakt {contact_id} aktualisiert'})


@contacts_bp.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    # In production: Delete from database (soft delete recommended)
    return jsonify({'success': True, 'message': f'Kontakt {contact_id} gelöscht'})


@contacts_bp.route('/api/contacts/bulk-delete', methods=['POST'])
def bulk_delete_contacts():
    """Delete multiple contacts"""
    data = request.json
    ids = data.get('ids', [])
    # In production: Delete from database
    return jsonify({'success': True, 'deleted': len(ids)})


# ----- IMPORT / EXPORT -----

@contacts_bp.route('/api/contacts/import', methods=['POST'])
def import_contacts():
    """Import contacts from CSV/Excel"""
    file = request.files.get('file')
    source = request.form.get('source', 'csv')
    
    if not file:
        return jsonify({'success': False, 'error': 'Keine Datei'}), 400
    
    imported = 0
    errors = []
    
    try:
        if source == 'csv':
            content = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(content))
            
            for row in reader:
                # In production: Save each contact to database
                imported += 1
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({
        'success': True,
        'imported': imported,
        'errors': errors
    })


@contacts_bp.route('/api/contacts/export', methods=['GET'])
def export_contacts():
    """Export contacts to CSV"""
    format_type = request.args.get('format', 'csv')
    
    # In production: Query all contacts from database
    contacts = [
        {'first_name': 'Max', 'last_name': 'Mustermann', 'email': 'max@example.com', 
         'phone': '+49 170 1234567', 'company': 'TechCorp GmbH'},
        {'first_name': 'Anna', 'last_name': 'Schmidt', 'email': 'anna@building.de',
         'phone': '+49 171 9876543', 'company': 'Building AG'},
    ]
    
    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['first_name', 'last_name', 'email', 'phone', 'company'])
        writer.writeheader()
        writer.writerows(contacts)
        
        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=contacts_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    
    return jsonify({'success': False, 'error': 'Unsupported format'}), 400


# ----- HUBSPOT SYNC -----

@contacts_bp.route('/api/contacts/sync-hubspot', methods=['POST'])
def sync_hubspot():
    """Sync contacts with HubSpot"""
    hubspot_api_key = os.environ.get('HUBSPOT_API_KEY')
    
    if not hubspot_api_key:
        return jsonify({'success': False, 'error': 'HubSpot API Key nicht konfiguriert'}), 400
    
    synced = 0
    created = 0
    updated = 0
    
    try:
        # Get contacts from HubSpot
        headers = {'Authorization': f'Bearer {hubspot_api_key}'}
        response = requests.get(
            'https://api.hubapi.com/crm/v3/objects/contacts',
            headers=headers,
            params={'limit': 100, 'properties': 'firstname,lastname,email,phone,company,hs_whatsapp_consent'}
        )
        
        if response.status_code == 200:
            data = response.json()
            for hs_contact in data.get('results', []):
                props = hs_contact.get('properties', {})
                # In production: Upsert to database
                synced += 1
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({
        'success': True,
        'synced': synced,
        'created': created,
        'updated': updated
    })


# ----- WHATSAPP CONSENT -----

@contacts_bp.route('/api/contacts/<int:contact_id>/consent', methods=['POST'])
def update_consent(contact_id):
    """Update WhatsApp consent for a contact"""
    data = request.json
    consent = data.get('consent')  # yes, no, pending
    
    if consent not in ['yes', 'no', 'pending']:
        return jsonify({'success': False, 'error': 'Invalid consent value'}), 400
    
    # In production: Update in database and sync to HubSpot
    
    return jsonify({
        'success': True,
        'contact_id': contact_id,
        'consent': consent
    })


@contacts_bp.route('/api/contacts/bulk-consent', methods=['POST'])
def bulk_update_consent():
    """Bulk update WhatsApp consent (DSGVO compliant)"""
    data = request.json
    contact_ids = data.get('contact_ids', [])
    consent = data.get('consent')
    
    updated = 0
    
    for contact_id in contact_ids:
        # In production: Update each contact
        # Log consent change for DSGVO compliance
        updated += 1
    
    return jsonify({
        'success': True,
        'updated': updated
    })


# ============================================================================
# Register Blueprint
# ============================================================================

def register_contacts_blueprint(app):
    """Register contacts blueprint"""
    app.register_blueprint(contacts_bp)
    print("📇 CONTACTS MODULE loaded!")


__all__ = ['contacts_bp', 'register_contacts_blueprint']
