"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ⚙️ SETTINGS & 🎮 TOKENS - WEST MONEY OS v12.0                                ║
║  System Settings, API Keys, Integrations, Gamification & Rewards             ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Blueprint, render_template_string, request, jsonify, session
from datetime import datetime
import json
import os

settings_bp = Blueprint('settings', __name__)
tokens_bp = Blueprint('tokens', __name__)

# ============================================================================
# SETTINGS MODULE
# ============================================================================

SETTINGS_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚙️ Settings - West Money OS</title>
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
            display: flex; align-items: center; gap: 12px;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .logo-icon { font-size: 1.8rem; }
        .logo-text {
            font-size: 1.2rem; font-weight: 700;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav a {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 16px; color: #888; text-decoration: none;
            border-radius: 10px; margin-bottom: 5px; transition: all 0.3s;
        }
        .nav a:hover, .nav a.active { background: rgba(255,0,255,0.1); color: #ff00ff; }
        .main { flex: 1; padding: 30px; overflow-y: auto; }
        .header { margin-bottom: 30px; }
        .title { font-size: 2rem; font-weight: 700; }
        .subtitle { color: #888; margin-top: 5px; }
        
        .settings-grid {
            display: grid;
            grid-template-columns: 250px 1fr;
            gap: 30px;
        }
        .settings-nav {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
        }
        .settings-nav-item {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 16px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 5px;
        }
        .settings-nav-item:hover { background: rgba(255,255,255,0.05); }
        .settings-nav-item.active {
            background: linear-gradient(135deg, rgba(255,0,255,0.2), rgba(0,255,255,0.2));
            color: #ff00ff;
        }
        
        .settings-content {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 30px;
        }
        .settings-section { margin-bottom: 40px; }
        .settings-section:last-child { margin-bottom: 0; }
        .settings-section-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; margin-bottom: 8px; color: #ccc; font-weight: 500; }
        .form-input {
            width: 100%; padding: 12px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px; color: #fff; font-size: 1rem;
        }
        .form-input:focus { outline: none; border-color: #ff00ff; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .form-hint { font-size: 0.85rem; color: #666; margin-top: 5px; }
        
        .toggle-switch {
            display: flex; align-items: center; justify-content: space-between;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .toggle-switch:last-child { border-bottom: none; }
        .toggle-label { font-weight: 500; }
        .toggle-desc { font-size: 0.85rem; color: #888; margin-top: 3px; }
        .toggle {
            width: 50px; height: 26px;
            background: rgba(255,255,255,0.2);
            border-radius: 13px;
            position: relative;
            cursor: pointer;
            transition: all 0.3s;
        }
        .toggle.active { background: linear-gradient(135deg, #ff00ff, #00ffff); }
        .toggle::after {
            content: '';
            width: 22px; height: 22px;
            background: #fff;
            border-radius: 50%;
            position: absolute;
            top: 2px; left: 2px;
            transition: all 0.3s;
        }
        .toggle.active::after { left: 26px; }
        
        .api-key-input {
            display: flex; gap: 10px;
        }
        .api-key-input input { flex: 1; }
        
        .integration-card {
            display: flex; align-items: center; gap: 20px;
            padding: 20px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            margin-bottom: 15px;
        }
        .integration-icon { font-size: 2.5rem; }
        .integration-info { flex: 1; }
        .integration-name { font-weight: 600; font-size: 1.1rem; }
        .integration-status { font-size: 0.85rem; margin-top: 3px; }
        .integration-status.connected { color: #00ffff; }
        .integration-status.disconnected { color: #ff4757; }
        
        .btn {
            padding: 12px 24px; border: none; border-radius: 10px;
            font-size: 0.95rem; font-weight: 600; cursor: pointer;
            transition: all 0.3s; display: inline-flex; align-items: center; gap: 8px;
        }
        .btn-primary { background: linear-gradient(135deg, #ff00ff, #00ffff); color: #000; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255,0,255,0.3); }
        .btn-secondary { background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.2); }
        .btn-danger { background: rgba(255,71,87,0.2); color: #ff4757; border: 1px solid rgba(255,71,87,0.3); }
        
        .toast {
            position: fixed; bottom: 30px; right: 30px;
            padding: 16px 24px; background: #00ffff; color: #000;
            border-radius: 10px; font-weight: 600; z-index: 9999;
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
                <a href="/broly"><span>🐉</span> Broly</a>
                <a href="/dashboard/campaigns"><span>📧</span> Kampagnen</a>
                <a href="/dashboard/invoices"><span>💰</span> Rechnungen</a>
                <a href="/dashboard/whatsapp"><span>💬</span> WhatsApp</a>
                <a href="/dashboard/tokens"><span>🎮</span> Tokens</a>
                <a href="/dashboard/settings" class="active"><span>⚙️</span> Settings</a>
            </div>
        </nav>
        
        <main class="main">
            <div class="header">
                <h1 class="title">⚙️ Einstellungen</h1>
                <p class="subtitle">System-Konfiguration und Integrationen verwalten</p>
            </div>
            
            <div class="settings-grid">
                <div class="settings-nav">
                    <div class="settings-nav-item active" onclick="showSection('general')">
                        <span>⚙️</span> Allgemein
                    </div>
                    <div class="settings-nav-item" onclick="showSection('integrations')">
                        <span>🔗</span> Integrationen
                    </div>
                    <div class="settings-nav-item" onclick="showSection('api')">
                        <span>🔑</span> API Keys
                    </div>
                    <div class="settings-nav-item" onclick="showSection('notifications')">
                        <span>🔔</span> Benachrichtigungen
                    </div>
                    <div class="settings-nav-item" onclick="showSection('security')">
                        <span>🔐</span> Sicherheit
                    </div>
                    <div class="settings-nav-item" onclick="showSection('billing')">
                        <span>💳</span> Abrechnung
                    </div>
                </div>
                
                <div class="settings-content">
                    <!-- General Settings -->
                    <div id="section-general" class="settings-section">
                        <h2 class="settings-section-title">⚙️ Allgemeine Einstellungen</h2>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Firmenname</label>
                                <input type="text" class="form-input" value="West Money Bau GmbH">
                            </div>
                            <div class="form-group">
                                <label class="form-label">E-Mail</label>
                                <input type="email" class="form-input" value="info@west-money.com">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">Telefon</label>
                                <input type="tel" class="form-input" value="+49 1234 567890">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Website</label>
                                <input type="url" class="form-input" value="https://west-money.com">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Adresse</label>
                            <input type="text" class="form-input" value="Frankfurt am Main, Deutschland">
                        </div>
                        
                        <div class="toggle-switch">
                            <div>
                                <div class="toggle-label">Dark Mode</div>
                                <div class="toggle-desc">Dunkles Theme aktivieren</div>
                            </div>
                            <div class="toggle active" onclick="this.classList.toggle('active')"></div>
                        </div>
                        
                        <div class="toggle-switch">
                            <div>
                                <div class="toggle-label">Sprache</div>
                                <div class="toggle-desc">Deutsch (DE)</div>
                            </div>
                            <select class="form-input" style="width: 150px;">
                                <option selected>Deutsch</option>
                                <option>English</option>
                            </select>
                        </div>
                        
                        <button class="btn btn-primary" style="margin-top: 20px;">💾 Speichern</button>
                    </div>
                    
                    <!-- Integrations -->
                    <div id="section-integrations" class="settings-section" style="display: none;">
                        <h2 class="settings-section-title">🔗 Integrationen</h2>
                        
                        <div class="integration-card">
                            <div class="integration-icon">🟠</div>
                            <div class="integration-info">
                                <div class="integration-name">HubSpot CRM</div>
                                <div class="integration-status connected">✅ Verbunden</div>
                            </div>
                            <button class="btn btn-secondary">⚙️ Konfigurieren</button>
                        </div>
                        
                        <div class="integration-card">
                            <div class="integration-icon">💬</div>
                            <div class="integration-info">
                                <div class="integration-name">WhatsApp Business API</div>
                                <div class="integration-status connected">✅ Verbunden</div>
                            </div>
                            <button class="btn btn-secondary">⚙️ Konfigurieren</button>
                        </div>
                        
                        <div class="integration-card">
                            <div class="integration-icon">💳</div>
                            <div class="integration-info">
                                <div class="integration-name">Stripe Payments</div>
                                <div class="integration-status connected">✅ Verbunden</div>
                            </div>
                            <button class="btn btn-secondary">⚙️ Konfigurieren</button>
                        </div>
                        
                        <div class="integration-card">
                            <div class="integration-icon">📞</div>
                            <div class="integration-info">
                                <div class="integration-name">Zadarma VoIP</div>
                                <div class="integration-status disconnected">❌ Nicht verbunden</div>
                            </div>
                            <button class="btn btn-primary">🔗 Verbinden</button>
                        </div>
                        
                        <div class="integration-card">
                            <div class="integration-icon">🏠</div>
                            <div class="integration-info">
                                <div class="integration-name">LOXONE Connect</div>
                                <div class="integration-status connected">✅ Verbunden</div>
                            </div>
                            <button class="btn btn-secondary">⚙️ Konfigurieren</button>
                        </div>
                        
                        <div class="integration-card">
                            <div class="integration-icon">📊</div>
                            <div class="integration-info">
                                <div class="integration-name">Explorium B2B</div>
                                <div class="integration-status connected">✅ Verbunden</div>
                            </div>
                            <button class="btn btn-secondary">⚙️ Konfigurieren</button>
                        </div>
                    </div>
                    
                    <!-- API Keys -->
                    <div id="section-api" class="settings-section" style="display: none;">
                        <h2 class="settings-section-title">🔑 API Keys</h2>
                        
                        <div class="form-group">
                            <label class="form-label">HubSpot API Key</label>
                            <div class="api-key-input">
                                <input type="password" class="form-input" value="pat-eu1-xxxxxxxxxxxxx">
                                <button class="btn btn-secondary">👁️</button>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">WhatsApp Business Token</label>
                            <div class="api-key-input">
                                <input type="password" class="form-input" value="EAAxxxxxxxxxxxxxx">
                                <button class="btn btn-secondary">👁️</button>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Stripe Secret Key</label>
                            <div class="api-key-input">
                                <input type="password" class="form-input" value="sk_live_xxxxxxxxxx">
                                <button class="btn btn-secondary">👁️</button>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">Claude API Key</label>
                            <div class="api-key-input">
                                <input type="password" class="form-input" value="sk-ant-xxxxxxxxxx">
                                <button class="btn btn-secondary">👁️</button>
                            </div>
                        </div>
                        
                        <button class="btn btn-primary" style="margin-top: 20px;">💾 Keys speichern</button>
                    </div>
                    
                    <!-- Security -->
                    <div id="section-security" class="settings-section" style="display: none;">
                        <h2 class="settings-section-title">🔐 Sicherheit</h2>
                        
                        <div class="toggle-switch">
                            <div>
                                <div class="toggle-label">2-Faktor-Authentifizierung</div>
                                <div class="toggle-desc">WhatsApp OTP für zusätzliche Sicherheit</div>
                            </div>
                            <div class="toggle active" onclick="this.classList.toggle('active')"></div>
                        </div>
                        
                        <div class="toggle-switch">
                            <div>
                                <div class="toggle-label">Session Timeout</div>
                                <div class="toggle-desc">Automatisch ausloggen nach Inaktivität</div>
                            </div>
                            <select class="form-input" style="width: 150px;">
                                <option>30 Minuten</option>
                                <option selected>1 Stunde</option>
                                <option>4 Stunden</option>
                                <option>8 Stunden</option>
                            </select>
                        </div>
                        
                        <div class="toggle-switch">
                            <div>
                                <div class="toggle-label">IP-Whitelist</div>
                                <div class="toggle-desc">Nur bestimmte IPs zulassen</div>
                            </div>
                            <div class="toggle" onclick="this.classList.toggle('active')"></div>
                        </div>
                        
                        <div class="form-group" style="margin-top: 30px;">
                            <label class="form-label">Passwort ändern</label>
                            <input type="password" class="form-input" placeholder="Aktuelles Passwort" style="margin-bottom: 10px;">
                            <input type="password" class="form-input" placeholder="Neues Passwort" style="margin-bottom: 10px;">
                            <input type="password" class="form-input" placeholder="Passwort bestätigen">
                        </div>
                        
                        <button class="btn btn-primary" style="margin-top: 20px;">🔐 Passwort ändern</button>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <script>
        function showSection(section) {
            document.querySelectorAll('.settings-section').forEach(s => s.style.display = 'none');
            document.querySelectorAll('.settings-nav-item').forEach(n => n.classList.remove('active'));
            
            document.getElementById('section-' + section).style.display = 'block';
            event.target.closest('.settings-nav-item').classList.add('active');
        }
        
        function showToast(message) {
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
    </script>
</body>
</html>
"""

# ============================================================================
# TOKENS / GAMIFICATION MODULE
# ============================================================================

TOKENS_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Tokens - West Money OS</title>
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
            border-right: 1px solid rgba(168,85,247,0.2);
            padding: 20px;
        }
        .logo {
            display: flex; align-items: center; gap: 12px;
            padding: 15px 0;
            border-bottom: 1px solid rgba(168,85,247,0.2);
            margin-bottom: 20px;
        }
        .logo-icon { font-size: 1.8rem; }
        .logo-text {
            font-size: 1.2rem; font-weight: 700;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav a {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 16px; color: #888; text-decoration: none;
            border-radius: 10px; margin-bottom: 5px; transition: all 0.3s;
        }
        .nav a:hover, .nav a.active { background: rgba(168,85,247,0.1); color: #ff00ff; }
        .main { flex: 1; padding: 30px; overflow-y: auto; }
        .header { margin-bottom: 30px; }
        .title { font-size: 2rem; font-weight: 700; }
        
        /* Token Balance */
        .token-balance {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .token-card {
            background: linear-gradient(135deg, rgba(168,85,247,0.2), rgba(236,72,153,0.2));
            border: 1px solid rgba(168,85,247,0.3);
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            transition: all 0.3s;
        }
        .token-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(168,85,247,0.3);
        }
        .token-icon { font-size: 3rem; margin-bottom: 15px; }
        .token-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .token-name { color: #888; margin-top: 5px; }
        .token-change { font-size: 0.85rem; margin-top: 10px; color: #00ffff; }
        
        /* Achievements */
        .achievements-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .achievement-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s;
        }
        .achievement-card.unlocked {
            border-color: rgba(168,85,247,0.5);
            background: linear-gradient(135deg, rgba(168,85,247,0.1), rgba(236,72,153,0.1));
        }
        .achievement-card.locked { opacity: 0.5; }
        .achievement-header {
            display: flex; align-items: center; gap: 15px;
            margin-bottom: 15px;
        }
        .achievement-icon { font-size: 2.5rem; }
        .achievement-title { font-weight: 600; font-size: 1.1rem; }
        .achievement-desc { color: #888; font-size: 0.9rem; margin-bottom: 15px; }
        .achievement-progress {
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
        }
        .achievement-progress-bar {
            height: 100%;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            border-radius: 4px;
            transition: width 0.5s;
        }
        .achievement-progress-text {
            display: flex;
            justify-content: space-between;
            margin-top: 8px;
            font-size: 0.8rem;
            color: #888;
        }
        
        /* Leaderboard */
        .leaderboard {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
        }
        .leaderboard-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 20px; }
        .leaderboard-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .leaderboard-item:last-child { border-bottom: none; }
        .leaderboard-rank {
            width: 40px; height: 40px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-weight: 700;
        }
        .rank-1 { background: linear-gradient(135deg, #ff00ff, #00ffff); color: #000; }
        .rank-2 { background: linear-gradient(135deg, #c0c0c0, #a0a0a0); color: #000; }
        .rank-3 { background: linear-gradient(135deg, #cd7f32, #b8860b); color: #000; }
        .rank-other { background: rgba(255,255,255,0.1); }
        .leaderboard-user { flex: 1; }
        .leaderboard-name { font-weight: 600; }
        .leaderboard-level { font-size: 0.85rem; color: #888; }
        .leaderboard-tokens { font-weight: 700; color: #ff00ff; }
        
        /* Rewards Shop */
        .rewards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        .reward-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            transition: all 0.3s;
        }
        .reward-card:hover {
            border-color: rgba(168,85,247,0.5);
            transform: translateY(-3px);
        }
        .reward-icon { font-size: 3rem; margin-bottom: 15px; }
        .reward-name { font-weight: 600; margin-bottom: 5px; }
        .reward-desc { font-size: 0.85rem; color: #888; margin-bottom: 15px; }
        .reward-price {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: linear-gradient(135deg, rgba(168,85,247,0.2), rgba(236,72,153,0.2));
            border-radius: 20px;
            font-weight: 600;
            color: #ff00ff;
        }
        
        .btn {
            padding: 12px 24px; border: none; border-radius: 10px;
            font-size: 0.95rem; font-weight: 600; cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary { background: linear-gradient(135deg, #ff00ff, #00ffff); color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <nav class="sidebar">
            <div class="logo">
                <span class="logo-icon">🎮</span>
                <span class="logo-text">Token System</span>
            </div>
            <div class="nav">
                <a href="/dashboard"><span>📊</span> Dashboard</a>
                <a href="/dashboard/tokens" class="active"><span>🎮</span> Tokens</a>
                <a href="/dashboard/tokens/achievements"><span>🏆</span> Achievements</a>
                <a href="/dashboard/tokens/leaderboard"><span>📊</span> Leaderboard</a>
                <a href="/dashboard/tokens/rewards"><span>🎁</span> Rewards</a>
                <a href="/broly"><span>🐉</span> Broly</a>
            </div>
        </nav>
        
        <main class="main">
            <div class="header">
                <h1 class="title">🎮 Token & Rewards System</h1>
            </div>
            
            <!-- Token Balance -->
            <div class="token-balance">
                <div class="token-card">
                    <div class="token-icon">🪙</div>
                    <div class="token-value">{{ tokens.god }}</div>
                    <div class="token-name">GOD Tokens</div>
                    <div class="token-change">+250 diese Woche</div>
                </div>
                <div class="token-card">
                    <div class="token-icon">💎</div>
                    <div class="token-value">{{ tokens.dedsec }}</div>
                    <div class="token-name">DedSec Tokens</div>
                    <div class="token-change">+75 diese Woche</div>
                </div>
                <div class="token-card">
                    <div class="token-icon">👑</div>
                    <div class="token-value">{{ tokens.og }}</div>
                    <div class="token-name">OG Tokens</div>
                    <div class="token-change">+50 diese Woche</div>
                </div>
                <div class="token-card">
                    <div class="token-icon">🗼</div>
                    <div class="token-value">{{ tokens.tower }}</div>
                    <div class="token-name">Tower Tokens</div>
                    <div class="token-change">+120 diese Woche</div>
                </div>
            </div>
            
            <!-- Achievements -->
            <h2 style="margin-bottom: 20px;">🏆 Achievements</h2>
            <div class="achievements-grid">
                <div class="achievement-card unlocked">
                    <div class="achievement-header">
                        <div class="achievement-icon">🚀</div>
                        <div class="achievement-title">First Lead</div>
                    </div>
                    <div class="achievement-desc">Erstelle deinen ersten Lead</div>
                    <div class="achievement-progress">
                        <div class="achievement-progress-bar" style="width: 100%;"></div>
                    </div>
                    <div class="achievement-progress-text">
                        <span>Abgeschlossen</span>
                        <span>+50 GOD</span>
                    </div>
                </div>
                
                <div class="achievement-card unlocked">
                    <div class="achievement-header">
                        <div class="achievement-icon">📧</div>
                        <div class="achievement-title">Email Master</div>
                    </div>
                    <div class="achievement-desc">Sende 100 E-Mails über Kampagnen</div>
                    <div class="achievement-progress">
                        <div class="achievement-progress-bar" style="width: 100%;"></div>
                    </div>
                    <div class="achievement-progress-text">
                        <span>100/100</span>
                        <span>+100 GOD</span>
                    </div>
                </div>
                
                <div class="achievement-card">
                    <div class="achievement-header">
                        <div class="achievement-icon">🔥</div>
                        <div class="achievement-title">Hot Lead Hunter</div>
                    </div>
                    <div class="achievement-desc">Generiere 50 Hot Leads (Score > 70)</div>
                    <div class="achievement-progress">
                        <div class="achievement-progress-bar" style="width: 68%;"></div>
                    </div>
                    <div class="achievement-progress-text">
                        <span>34/50</span>
                        <span>+200 GOD</span>
                    </div>
                </div>
                
                <div class="achievement-card">
                    <div class="achievement-header">
                        <div class="achievement-icon">💰</div>
                        <div class="achievement-title">Revenue King</div>
                    </div>
                    <div class="achievement-desc">Erreiche €1M Umsatz</div>
                    <div class="achievement-progress">
                        <div class="achievement-progress-bar" style="width: 84.7%;"></div>
                    </div>
                    <div class="achievement-progress-text">
                        <span>€847K/€1M</span>
                        <span>+500 GOD</span>
                    </div>
                </div>
                
                <div class="achievement-card locked">
                    <div class="achievement-header">
                        <div class="achievement-icon">🐉</div>
                        <div class="achievement-title">Broly Master</div>
                    </div>
                    <div class="achievement-desc">100 Leads automatisch via Broly generieren</div>
                    <div class="achievement-progress">
                        <div class="achievement-progress-bar" style="width: 23%;"></div>
                    </div>
                    <div class="achievement-progress-text">
                        <span>23/100</span>
                        <span>+300 GOD</span>
                    </div>
                </div>
                
                <div class="achievement-card locked">
                    <div class="achievement-header">
                        <div class="achievement-icon">🏠</div>
                        <div class="achievement-title">Smart Home Pro</div>
                    </div>
                    <div class="achievement-desc">10 LOXONE Projekte abschließen</div>
                    <div class="achievement-progress">
                        <div class="achievement-progress-bar" style="width: 30%;"></div>
                    </div>
                    <div class="achievement-progress-text">
                        <span>3/10</span>
                        <span>+1000 GOD</span>
                    </div>
                </div>
            </div>
            
            <!-- Leaderboard -->
            <h2 style="margin: 40px 0 20px;">📊 Leaderboard</h2>
            <div class="leaderboard">
                <div class="leaderboard-item">
                    <div class="leaderboard-rank rank-1">1</div>
                    <div class="leaderboard-user">
                        <div class="leaderboard-name">Ömer Coşkun</div>
                        <div class="leaderboard-level">Level 42 - GOD MODE</div>
                    </div>
                    <div class="leaderboard-tokens">12,450 GOD</div>
                </div>
                <div class="leaderboard-item">
                    <div class="leaderboard-rank rank-2">2</div>
                    <div class="leaderboard-user">
                        <div class="leaderboard-name">Team Sales</div>
                        <div class="leaderboard-level">Level 28 - Elite</div>
                    </div>
                    <div class="leaderboard-tokens">8,230 GOD</div>
                </div>
                <div class="leaderboard-item">
                    <div class="leaderboard-rank rank-3">3</div>
                    <div class="leaderboard-user">
                        <div class="leaderboard-name">Marketing Bot</div>
                        <div class="leaderboard-level">Level 21 - Pro</div>
                    </div>
                    <div class="leaderboard-tokens">5,680 GOD</div>
                </div>
            </div>
            
            <!-- Rewards Shop -->
            <h2 style="margin: 40px 0 20px;">🎁 Rewards Shop</h2>
            <div class="rewards-grid">
                <div class="reward-card">
                    <div class="reward-icon">☕</div>
                    <div class="reward-name">Kaffeepause</div>
                    <div class="reward-desc">1 Stunde Extra-Pause</div>
                    <div class="reward-price">🪙 100 GOD</div>
                </div>
                <div class="reward-card">
                    <div class="reward-icon">🎧</div>
                    <div class="reward-name">Premium Headphones</div>
                    <div class="reward-desc">Sony WH-1000XM5</div>
                    <div class="reward-price">🪙 5,000 GOD</div>
                </div>
                <div class="reward-card">
                    <div class="reward-icon">🏝️</div>
                    <div class="reward-name">Extra Urlaubstag</div>
                    <div class="reward-desc">1 zusätzlicher freier Tag</div>
                    <div class="reward-price">🪙 10,000 GOD</div>
                </div>
                <div class="reward-card">
                    <div class="reward-icon">💻</div>
                    <div class="reward-name">MacBook Pro</div>
                    <div class="reward-desc">Neuestes Modell</div>
                    <div class="reward-price">🪙 50,000 GOD</div>
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

@settings_bp.route('/dashboard/settings')
def settings_page():
    """Settings page"""
    return render_template_string(SETTINGS_HTML)


@settings_bp.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all settings"""
    settings = {
        'company_name': 'West Money Bau GmbH',
        'email': 'info@west-money.com',
        'phone': '+49 1234 567890',
        'website': 'https://west-money.com',
        'dark_mode': True,
        'language': 'de'
    }
    return jsonify({'success': True, 'settings': settings})


@settings_bp.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    data = request.json
    # In production: Save to database
    return jsonify({'success': True, 'message': 'Einstellungen gespeichert'})


@tokens_bp.route('/dashboard/tokens')
def tokens_page():
    """Tokens & Gamification page"""
    tokens = {
        'god': '12,450',
        'dedsec': '3,280',
        'og': '1,500',
        'tower': '4,720'
    }
    return render_template_string(TOKENS_HTML, tokens=tokens)


@tokens_bp.route('/api/tokens/balance', methods=['GET'])
def get_token_balance():
    """Get token balance"""
    balance = {
        'god': 12450,
        'dedsec': 3280,
        'og': 1500,
        'tower': 4720
    }
    return jsonify({'success': True, 'balance': balance})


@tokens_bp.route('/api/tokens/earn', methods=['POST'])
def earn_tokens():
    """Earn tokens for action"""
    data = request.json
    action = data.get('action')
    
    # Token rewards for actions
    rewards = {
        'create_lead': 10,
        'send_email': 5,
        'make_call': 15,
        'close_deal': 100,
        'complete_task': 20
    }
    
    earned = rewards.get(action, 0)
    
    return jsonify({
        'success': True,
        'earned': earned,
        'token_type': 'god',
        'action': action
    })


@tokens_bp.route('/api/tokens/achievements', methods=['GET'])
def get_achievements():
    """Get achievements"""
    achievements = [
        {'id': 1, 'name': 'First Lead', 'progress': 100, 'unlocked': True, 'reward': 50},
        {'id': 2, 'name': 'Email Master', 'progress': 100, 'unlocked': True, 'reward': 100},
        {'id': 3, 'name': 'Hot Lead Hunter', 'progress': 68, 'unlocked': False, 'reward': 200},
    ]
    return jsonify({'success': True, 'achievements': achievements})


def register_settings_blueprint(app):
    """Register Settings blueprint"""
    app.register_blueprint(settings_bp)
    print("⚙️ SETTINGS MODULE loaded!")


def register_tokens_blueprint(app):
    """Register Tokens blueprint"""
    app.register_blueprint(tokens_bp)
    print("🎮 TOKENS MODULE loaded!")


__all__ = ['settings_bp', 'tokens_bp', 'register_settings_blueprint', 'register_tokens_blueprint']
