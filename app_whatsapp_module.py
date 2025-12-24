"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  💬 WHATSAPP MODUL - WEST MONEY OS v12.0                                      ║
║  WhatsApp Business API, Consent Management, Bulk Messaging, OTP Auth         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Blueprint, render_template_string, request, jsonify, session
from datetime import datetime, timedelta
import json
import random
import hashlib
import os

whatsapp_bp = Blueprint('whatsapp', __name__)

# Store OTPs temporarily (in production: use Redis)
otp_store = {}

WHATSAPP_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💬 WhatsApp - West Money OS</title>
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
            border-right: 1px solid rgba(37,211,102,0.2);
            padding: 20px;
        }
        .logo {
            display: flex; align-items: center; gap: 12px;
            padding: 15px 0;
            border-bottom: 1px solid rgba(37,211,102,0.2);
            margin-bottom: 20px;
        }
        .logo-icon { font-size: 1.8rem; }
        .logo-text {
            font-size: 1.2rem; font-weight: 700;
            background: linear-gradient(135deg, #00ffff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav a {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 16px; color: #888; text-decoration: none;
            border-radius: 10px; margin-bottom: 5px; transition: all 0.3s;
        }
        .nav a:hover, .nav a.active { background: rgba(37,211,102,0.1); color: #00ffff; }
        .main { flex: 1; padding: 30px; overflow-y: auto; }
        .header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 30px;
        }
        .title { font-size: 2rem; font-weight: 700; }
        .btn {
            padding: 12px 24px; border: none; border-radius: 10px;
            font-size: 0.95rem; font-weight: 600; cursor: pointer;
            transition: all 0.3s; display: flex; align-items: center; gap: 8px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #00ffff, #ff00ff); color: #fff;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(37,211,102,0.3);
        }
        .btn-secondary {
            background: rgba(255,255,255,0.1); color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* Stats */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px; padding: 20px; text-align: center;
        }
        .stat-card .icon { font-size: 2rem; margin-bottom: 10px; }
        .stat-card .value {
            font-size: 2rem; font-weight: 700; color: #00ffff;
        }
        .stat-card .label { color: #888; font-size: 0.85rem; margin-top: 5px; }
        
        /* Chat Interface */
        .chat-container {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            height: calc(100vh - 250px);
        }
        .chat-list {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            overflow: hidden;
        }
        .chat-list-header {
            padding: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .chat-list-search {
            width: 100%;
            padding: 10px 15px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: #fff;
        }
        .chat-list-items {
            overflow-y: auto;
            max-height: calc(100% - 80px);
        }
        .chat-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 15px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            cursor: pointer;
            transition: all 0.3s;
        }
        .chat-item:hover, .chat-item.active {
            background: rgba(37,211,102,0.1);
        }
        .chat-item-avatar {
            width: 45px; height: 45px;
            background: linear-gradient(135deg, #00ffff, #ff00ff);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; color: #fff;
        }
        .chat-item-info { flex: 1; }
        .chat-item-name { font-weight: 600; }
        .chat-item-preview { font-size: 0.85rem; color: #888; }
        .chat-item-time { font-size: 0.75rem; color: #666; }
        .chat-item-badge {
            background: #00ffff;
            color: #fff;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.7rem;
        }
        
        .chat-window {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            display: flex;
            flex-direction: column;
        }
        .chat-window-header {
            padding: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .chat-window-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .message {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 12px;
            margin-bottom: 10px;
        }
        .message.sent {
            background: linear-gradient(135deg, #00ffff, #ff00ff);
            color: #fff;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }
        .message.received {
            background: rgba(255,255,255,0.1);
            border-bottom-left-radius: 4px;
        }
        .message-time {
            font-size: 0.7rem;
            color: rgba(255,255,255,0.6);
            margin-top: 5px;
            text-align: right;
        }
        .chat-window-input {
            padding: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
            display: flex;
            gap: 12px;
        }
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 25px;
            color: #fff;
            font-size: 1rem;
        }
        .chat-input:focus { outline: none; border-color: #00ffff; }
        .send-btn {
            width: 50px; height: 50px;
            background: linear-gradient(135deg, #00ffff, #ff00ff);
            border: none;
            border-radius: 50%;
            color: #fff;
            font-size: 1.2rem;
            cursor: pointer;
        }
        
        /* Bulk Messaging */
        .bulk-container {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
        }
        .bulk-header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 20px;
        }
        .bulk-form { display: grid; gap: 20px; }
        .form-group { margin-bottom: 0; }
        .form-label { display: block; margin-bottom: 8px; color: #ccc; }
        .form-input, .form-textarea {
            width: 100%;
            padding: 12px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: #fff;
            font-size: 1rem;
        }
        .form-textarea { min-height: 120px; resize: vertical; }
        .form-input:focus, .form-textarea:focus { outline: none; border-color: #00ffff; }
        
        /* Consent Table */
        .consent-table {
            width: 100%;
            border-collapse: collapse;
        }
        .consent-table th, .consent-table td {
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .consent-table th {
            background: rgba(0,0,0,0.3);
            color: #888;
            font-weight: 500;
            font-size: 0.85rem;
        }
        .consent-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .consent-yes { background: rgba(37,211,102,0.2); color: #00ffff; }
        .consent-no { background: rgba(255,71,87,0.2); color: #ff4757; }
        .consent-pending { background: rgba(255,165,2,0.2); color: #00ffff; }
        
        /* Modal */
        .modal-overlay {
            display: none; position: fixed; top: 0; left: 0;
            width: 100%; height: 100%; background: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px); z-index: 1000;
            justify-content: center; align-items: center;
        }
        .modal-overlay.active { display: flex; }
        .modal {
            background: #150a1a; border: 1px solid rgba(37,211,102,0.3);
            border-radius: 20px; width: 90%; max-width: 600px;
            max-height: 90vh; overflow-y: auto;
        }
        .modal-header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 24px; border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .modal-title { font-size: 1.3rem; font-weight: 700; }
        .modal-close {
            background: none; border: none; color: #888;
            font-size: 1.5rem; cursor: pointer;
        }
        .modal-body { padding: 24px; }
        .modal-footer {
            display: flex; justify-content: flex-end; gap: 12px;
            padding: 20px 24px; border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Tabs */
        .tabs {
            display: flex; gap: 10px; margin-bottom: 25px;
            border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;
        }
        .tab {
            padding: 10px 20px; background: none; border: none;
            color: #888; font-size: 1rem; cursor: pointer;
            border-radius: 8px; transition: all 0.3s;
        }
        .tab:hover { color: #fff; }
        .tab.active {
            background: rgba(37,211,102,0.2); color: #00ffff;
        }
        
        .toast {
            position: fixed; bottom: 30px; right: 30px;
            padding: 16px 24px; background: #00ffff; color: #fff;
            border-radius: 10px; font-weight: 600; z-index: 9999;
        }
    </style>
</head>
<body>
    <div class="container">
        <nav class="sidebar">
            <div class="logo">
                <span class="logo-icon">💬</span>
                <span class="logo-text">WhatsApp Business</span>
            </div>
            <div class="nav">
                <a href="/dashboard"><span>📊</span> Dashboard</a>
                <a href="/dashboard/whatsapp" class="active"><span>💬</span> Chats</a>
                <a href="/dashboard/whatsapp/broadcast"><span>📢</span> Broadcast</a>
                <a href="/dashboard/whatsapp/consent"><span>✅</span> Consent</a>
                <a href="/dashboard/whatsapp/templates"><span>📝</span> Templates</a>
                <a href="/dashboard/whatsapp/settings"><span>⚙️</span> Einstellungen</a>
                <a href="/broly"><span>🐉</span> Broly</a>
            </div>
        </nav>
        
        <main class="main">
            <div class="header">
                <h1 class="title">💬 WhatsApp Business</h1>
                <div style="display: flex; gap: 12px;">
                    <button class="btn btn-secondary" onclick="syncContacts()">🔄 Sync</button>
                    <button class="btn btn-primary" onclick="openModal('broadcast')">📢 Broadcast</button>
                </div>
            </div>
            
            <!-- Stats -->
            <div class="stats-row">
                <div class="stat-card">
                    <div class="icon">💬</div>
                    <div class="value">{{ stats.messages_sent }}</div>
                    <div class="label">Gesendet (heute)</div>
                </div>
                <div class="stat-card">
                    <div class="icon">📥</div>
                    <div class="value">{{ stats.messages_received }}</div>
                    <div class="label">Empfangen</div>
                </div>
                <div class="stat-card">
                    <div class="icon">✅</div>
                    <div class="value">{{ stats.consent_rate }}%</div>
                    <div class="label">Consent Rate</div>
                </div>
                <div class="stat-card">
                    <div class="icon">📊</div>
                    <div class="value">{{ stats.delivery_rate }}%</div>
                    <div class="label">Delivery Rate</div>
                </div>
                <div class="stat-card">
                    <div class="icon">💬</div>
                    <div class="value">{{ stats.response_rate }}%</div>
                    <div class="label">Response Rate</div>
                </div>
            </div>
            
            <!-- Tabs -->
            <div class="tabs">
                <button class="tab active" onclick="showTab('chats')">💬 Chats</button>
                <button class="tab" onclick="showTab('broadcast')">📢 Broadcast</button>
                <button class="tab" onclick="showTab('consent')">✅ Consent Management</button>
            </div>
            
            <!-- Chat Interface -->
            <div id="tab-chats" class="tab-content">
                <div class="chat-container">
                    <div class="chat-list">
                        <div class="chat-list-header">
                            <input type="text" class="chat-list-search" placeholder="🔍 Suchen...">
                        </div>
                        <div class="chat-list-items">
                            <div class="chat-item active">
                                <div class="chat-item-avatar">MM</div>
                                <div class="chat-item-info">
                                    <div class="chat-item-name">Max Mustermann</div>
                                    <div class="chat-item-preview">Ja, das klingt interessant!</div>
                                </div>
                                <div>
                                    <div class="chat-item-time">10:45</div>
                                    <span class="chat-item-badge">2</span>
                                </div>
                            </div>
                            <div class="chat-item">
                                <div class="chat-item-avatar">AS</div>
                                <div class="chat-item-info">
                                    <div class="chat-item-name">Anna Schmidt</div>
                                    <div class="chat-item-preview">Können wir morgen telefonieren?</div>
                                </div>
                                <div class="chat-item-time">09:30</div>
                            </div>
                            <div class="chat-item">
                                <div class="chat-item-avatar">LB</div>
                                <div class="chat-item-info">
                                    <div class="chat-item-name">Lisa Bauer</div>
                                    <div class="chat-item-preview">Danke für das Angebot!</div>
                                </div>
                                <div class="chat-item-time">Gestern</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="chat-window">
                        <div class="chat-window-header">
                            <div class="chat-item-avatar">MM</div>
                            <div>
                                <div class="chat-item-name">Max Mustermann</div>
                                <div class="chat-item-preview">TechCorp GmbH • Online</div>
                            </div>
                        </div>
                        <div class="chat-window-messages">
                            <div class="message received">
                                Hallo! Ich habe Ihre Nachricht bezüglich Smart Home erhalten.
                                <div class="message-time">10:30</div>
                            </div>
                            <div class="message sent">
                                Freut mich! Haben Sie Interesse an einer Beratung?
                                <div class="message-time">10:35 ✓✓</div>
                            </div>
                            <div class="message received">
                                Ja, das klingt interessant! Wann hätten Sie Zeit?
                                <div class="message-time">10:45</div>
                            </div>
                        </div>
                        <div class="chat-window-input">
                            <input type="text" class="chat-input" placeholder="Nachricht eingeben..." id="message-input">
                            <button class="send-btn" onclick="sendMessage()">📤</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Broadcast Tab -->
            <div id="tab-broadcast" class="tab-content" style="display: none;">
                <div class="bulk-container">
                    <div class="bulk-header">
                        <h2>📢 Broadcast Nachricht</h2>
                    </div>
                    <form class="bulk-form" id="broadcast-form">
                        <div class="form-group">
                            <label class="form-label">Empfänger</label>
                            <select class="form-input" name="recipients">
                                <option value="all_consent">Alle mit Consent ({{ stats.with_consent }})</option>
                                <option value="hot_leads">🔥 Hot Leads</option>
                                <option value="customers">👥 Bestandskunden</option>
                                <option value="custom">⚙️ Custom Filter</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Template</label>
                            <select class="form-input" name="template">
                                <option value="">Kein Template</option>
                                <option value="welcome">👋 Willkommen</option>
                                <option value="followup">🔄 Follow-Up</option>
                                <option value="offer">🎁 Angebot</option>
                                <option value="reminder">⏰ Erinnerung</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Nachricht</label>
                            <textarea class="form-textarea" name="message" placeholder="Hallo {{name}}! 👋

Ich hoffe, es geht Ihnen gut..."></textarea>
                        </div>
                        <div style="display: flex; gap: 12px;">
                            <button type="button" class="btn btn-secondary" onclick="previewBroadcast()">👁️ Vorschau</button>
                            <button type="button" class="btn btn-primary" onclick="sendBroadcast()">📤 Senden</button>
                        </div>
                    </form>
                </div>
            </div>
            
            <!-- Consent Tab -->
            <div id="tab-consent" class="tab-content" style="display: none;">
                <div class="bulk-container">
                    <div class="bulk-header">
                        <h2>✅ WhatsApp Consent Management</h2>
                        <div style="display: flex; gap: 12px;">
                            <button class="btn btn-secondary" onclick="exportConsent()">📥 Export</button>
                            <button class="btn btn-secondary" onclick="syncHubSpotConsent()">🔄 HubSpot Sync</button>
                            <button class="btn btn-primary" onclick="openModal('bulk-consent')">📝 Bulk Update</button>
                        </div>
                    </div>
                    
                    <table class="consent-table">
                        <thead>
                            <tr>
                                <th><input type="checkbox" onclick="toggleAll(this)"></th>
                                <th>Kontakt</th>
                                <th>Telefon</th>
                                <th>Consent Status</th>
                                <th>Aktualisiert</th>
                                <th>Aktionen</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><input type="checkbox" class="consent-checkbox"></td>
                                <td>
                                    <strong>Max Mustermann</strong><br>
                                    <small style="color: #888;">TechCorp GmbH</small>
                                </td>
                                <td>+49 170 1234567</td>
                                <td><span class="consent-badge consent-yes">✅ Zugestimmt</span></td>
                                <td>23.12.2024</td>
                                <td>
                                    <button class="btn btn-secondary" style="padding: 6px 12px;" onclick="updateConsent(1, 'revoke')">❌ Widerrufen</button>
                                </td>
                            </tr>
                            <tr>
                                <td><input type="checkbox" class="consent-checkbox"></td>
                                <td>
                                    <strong>Anna Schmidt</strong><br>
                                    <small style="color: #888;">Building AG</small>
                                </td>
                                <td>+49 171 9876543</td>
                                <td><span class="consent-badge consent-pending">⏳ Ausstehend</span></td>
                                <td>22.12.2024</td>
                                <td>
                                    <button class="btn btn-primary" style="padding: 6px 12px;" onclick="requestConsent(2)">📤 Anfragen</button>
                                </td>
                            </tr>
                            <tr>
                                <td><input type="checkbox" class="consent-checkbox"></td>
                                <td>
                                    <strong>Stefan Weber</strong><br>
                                    <small style="color: #888;">ImmoVest</small>
                                </td>
                                <td>+49 172 5551234</td>
                                <td><span class="consent-badge consent-no">❌ Abgelehnt</span></td>
                                <td>20.12.2024</td>
                                <td>
                                    <button class="btn btn-secondary" style="padding: 6px 12px;" disabled>-</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>
    
    <!-- Broadcast Modal -->
    <div class="modal-overlay" id="modal-broadcast">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">📢 Broadcast senden</h2>
                <button class="modal-close" onclick="closeModal('broadcast')">×</button>
            </div>
            <div class="modal-body">
                <p>Broadcast an <strong id="broadcast-count">0</strong> Empfänger senden?</p>
                <div id="broadcast-preview" style="margin-top: 20px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                    <!-- Preview -->
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('broadcast')">Abbrechen</button>
                <button class="btn btn-primary" onclick="confirmBroadcast()">📤 Senden</button>
            </div>
        </div>
    </div>
    
    <!-- Bulk Consent Modal -->
    <div class="modal-overlay" id="modal-bulk-consent">
        <div class="modal">
            <div class="modal-header">
                <h2 class="modal-title">📝 Bulk Consent Update</h2>
                <button class="modal-close" onclick="closeModal('bulk-consent')">×</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label class="form-label">Neuer Status</label>
                    <select class="form-input" id="bulk-consent-status">
                        <option value="yes">✅ Zugestimmt</option>
                        <option value="pending">⏳ Ausstehend</option>
                        <option value="no">❌ Abgelehnt</option>
                    </select>
                </div>
                <p style="color: #888; font-size: 0.9rem;">
                    ⚠️ Hinweis: Änderungen werden in HubSpot synchronisiert und für DSGVO-Compliance protokolliert.
                </p>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('bulk-consent')">Abbrechen</button>
                <button class="btn btn-primary" onclick="applyBulkConsent()">💾 Speichern</button>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
            
            event.target.classList.add('active');
            document.getElementById('tab-' + tab).style.display = 'block';
        }
        
        function openModal(type) {
            document.getElementById('modal-' + type).classList.add('active');
        }
        
        function closeModal(type) {
            document.getElementById('modal-' + type).classList.remove('active');
        }
        
        function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            if (!message) return;
            
            const messagesContainer = document.querySelector('.chat-window-messages');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message sent';
            msgDiv.innerHTML = message + '<div class="message-time">' + new Date().toLocaleTimeString('de-DE', {hour: '2-digit', minute: '2-digit'}) + ' ✓</div>';
            messagesContainer.appendChild(msgDiv);
            
            input.value = '';
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            showToast('📤 Nachricht gesendet');
        }
        
        function sendBroadcast() {
            const form = document.getElementById('broadcast-form');
            const formData = new FormData(form);
            
            document.getElementById('broadcast-count').textContent = '892';
            document.getElementById('broadcast-preview').innerHTML = formData.get('message');
            openModal('broadcast');
        }
        
        function confirmBroadcast() {
            closeModal('broadcast');
            showToast('📢 Broadcast wird gesendet...');
            
            setTimeout(() => {
                showToast('✅ 892 Nachrichten erfolgreich gesendet!');
            }, 2000);
        }
        
        function previewBroadcast() {
            showToast('👁️ Vorschau...');
        }
        
        function syncContacts() {
            showToast('🔄 Kontakte werden synchronisiert...');
        }
        
        function syncHubSpotConsent() {
            showToast('🔄 HubSpot Consent Sync gestartet...');
            
            fetch('/api/whatsapp/sync-hubspot-consent', { method: 'POST' })
                .then(r => r.json())
                .then(data => showToast('✅ ' + data.message));
        }
        
        function updateConsent(id, action) {
            fetch('/api/whatsapp/consent/' + id, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: action })
            }).then(() => {
                showToast('✅ Consent aktualisiert');
                location.reload();
            });
        }
        
        function requestConsent(id) {
            showToast('📤 Consent-Anfrage gesendet');
        }
        
        function applyBulkConsent() {
            const status = document.getElementById('bulk-consent-status').value;
            closeModal('bulk-consent');
            showToast('✅ Consent für ausgewählte Kontakte aktualisiert');
        }
        
        function exportConsent() {
            window.location.href = '/api/whatsapp/consent/export';
        }
        
        function toggleAll(checkbox) {
            document.querySelectorAll('.consent-checkbox').forEach(cb => {
                cb.checked = checkbox.checked;
            });
        }
        
        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
        
        // Enter to send
        document.getElementById('message-input')?.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""


# ============================================================================
# ROUTES
# ============================================================================

@whatsapp_bp.route('/dashboard/whatsapp')
def whatsapp_page():
    """WhatsApp dashboard"""
    stats = {
        'messages_sent': 156,
        'messages_received': 89,
        'consent_rate': 71,
        'delivery_rate': 94,
        'response_rate': 34,
        'with_consent': 892
    }
    return render_template_string(WHATSAPP_HTML, stats=stats)


@whatsapp_bp.route('/api/whatsapp/send', methods=['POST'])
def send_whatsapp():
    """Send WhatsApp message"""
    data = request.json
    phone = data.get('phone')
    message = data.get('message')
    
    # In production: Use WhatsApp Business API
    # response = requests.post('https://graph.facebook.com/v18.0/PHONE_NUMBER_ID/messages', ...)
    
    return jsonify({
        'success': True,
        'message': 'WhatsApp gesendet',
        'to': phone
    })


@whatsapp_bp.route('/api/whatsapp/broadcast', methods=['POST'])
def send_broadcast():
    """Send broadcast message"""
    data = request.json
    recipients = data.get('recipients', 'all_consent')
    message = data.get('message')
    
    # Get recipient count based on filter
    counts = {
        'all_consent': 892,
        'hot_leads': 34,
        'customers': 156,
        'custom': 50
    }
    
    count = counts.get(recipients, 0)
    
    return jsonify({
        'success': True,
        'message': f'Broadcast an {count} Empfänger gestartet',
        'count': count
    })


@whatsapp_bp.route('/api/whatsapp/consent/<int:contact_id>', methods=['POST'])
def update_consent(contact_id):
    """Update WhatsApp consent for contact"""
    data = request.json
    action = data.get('action')  # grant, revoke
    
    # Log for GDPR compliance
    # In production: Update database and sync to HubSpot
    
    return jsonify({
        'success': True,
        'contact_id': contact_id,
        'action': action
    })


@whatsapp_bp.route('/api/whatsapp/sync-hubspot-consent', methods=['POST'])
def sync_hubspot_consent():
    """Sync consent status with HubSpot"""
    # In production: Use HubSpot API
    # https://knowledge.hubspot.com/de/inbox/edit-the-whatsapp-consent-status-of-your-contacts-in-bulk
    
    return jsonify({
        'success': True,
        'message': '234 Kontakte synchronisiert',
        'synced': 234
    })


@whatsapp_bp.route('/api/whatsapp/consent/export', methods=['GET'])
def export_consent():
    """Export consent data for GDPR"""
    # Generate CSV export
    content = "contact_id,name,phone,consent_status,updated_at\n"
    content += "1,Max Mustermann,+49 170 1234567,yes,2024-12-23\n"
    content += "2,Anna Schmidt,+49 171 9876543,pending,2024-12-22\n"
    
    return content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=whatsapp_consent_{datetime.now().strftime("%Y%m%d")}.csv'
    }


# ----- OTP AUTHENTICATION -----

@whatsapp_bp.route('/api/whatsapp/send-otp', methods=['POST'])
def send_otp():
    """Send OTP via WhatsApp"""
    data = request.json
    phone = data.get('phone')
    
    if not phone:
        return jsonify({'success': False, 'error': 'Phone number required'}), 400
    
    # Generate 6-digit OTP
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Store OTP with expiry (5 minutes)
    otp_hash = hashlib.sha256(f"{phone}:{otp}".encode()).hexdigest()
    otp_store[phone] = {
        'otp_hash': otp_hash,
        'expires': datetime.now() + timedelta(minutes=5)
    }
    
    # In production: Send via WhatsApp Business API
    message = f"🔐 Ihr West Money OS Verifizierungscode: {otp}\n\nGültig für 5 Minuten."
    
    return jsonify({
        'success': True,
        'message': 'OTP gesendet',
        'expires_in': 300,
        # Remove in production:
        'debug_otp': otp
    })


@whatsapp_bp.route('/api/whatsapp/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP"""
    data = request.json
    phone = data.get('phone')
    otp = data.get('otp')
    
    if not phone or not otp:
        return jsonify({'success': False, 'error': 'Phone and OTP required'}), 400
    
    stored = otp_store.get(phone)
    
    if not stored:
        return jsonify({'success': False, 'error': 'OTP nicht gefunden oder abgelaufen'}), 400
    
    if datetime.now() > stored['expires']:
        del otp_store[phone]
        return jsonify({'success': False, 'error': 'OTP abgelaufen'}), 400
    
    otp_hash = hashlib.sha256(f"{phone}:{otp}".encode()).hexdigest()
    
    if otp_hash != stored['otp_hash']:
        return jsonify({'success': False, 'error': 'Ungültiger OTP'}), 400
    
    # OTP valid - clean up
    del otp_store[phone]
    
    # Set session
    session['phone_verified'] = phone
    session['2fa_verified'] = True
    
    return jsonify({
        'success': True,
        'message': 'OTP verifiziert',
        'verified': True
    })


def register_whatsapp_blueprint(app):
    """Register WhatsApp blueprint"""
    app.register_blueprint(whatsapp_bp)
    print("💬 WHATSAPP MODULE loaded!")


__all__ = ['whatsapp_bp', 'register_whatsapp_blueprint']
