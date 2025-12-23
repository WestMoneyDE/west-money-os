#!/usr/bin/env python3
"""
West Money OS v4.2 - Production Ready
=====================================
Deployment: Railway.app / Hetzner / Vercel
Domain: west-money.com
"""

from flask import Flask, jsonify, request, render_template_string, send_from_directory
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Konfiguration
OPENCORPORATES_BASE_URL = 'https://api.opencorporates.com/v0.4'
OPENCORPORATES_API_KEY = os.getenv('OPENCORPORATES_API_KEY', '')
PORT = int(os.getenv('PORT', 5000))

# ============================================================================
# API ENDPOINTS - Echte Handelsregister-Daten
# ============================================================================

@app.route('/api/hr/search')
def hr_search():
    """Echte Handelsregister-Suche via OpenCorporates"""
    query = request.args.get('q', '')
    jurisdiction = request.args.get('jurisdiction', 'de')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    
    if not query:
        return jsonify({'error': 'Suchbegriff fehlt', 'results': [], 'total': 0})
    
    try:
        url = f"{OPENCORPORATES_BASE_URL}/companies/search"
        params = {
            'q': query,
            'jurisdiction_code': jurisdiction,
            'page': page,
            'per_page': min(per_page, 100),
            'order': 'score'
        }
        if OPENCORPORATES_API_KEY:
            params['api_token'] = OPENCORPORATES_API_KEY
            
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for item in data.get('results', {}).get('companies', []):
            c = item.get('company', {})
            addr = c.get('registered_address', {}) or {}
            
            # Registerart extrahieren
            reg_type = ''
            cn = (c.get('company_number') or '').upper()
            for rt in ['HRB', 'HRA', 'GNR', 'PR', 'VR']:
                if rt in cn:
                    reg_type = rt
                    break
            
            results.append({
                'id': c.get('company_number', ''),
                'name': c.get('name', ''),
                'registerArt': reg_type,
                'registerNummer': c.get('company_number', ''),
                'gericht': extract_court(c.get('company_number', '')),
                'sitz': addr.get('locality', '') or addr.get('region', '') or '',
                'plz': addr.get('postal_code', ''),
                'strasse': addr.get('street_address', ''),
                'rechtsform': c.get('company_type', ''),
                'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv',
                'gruendung': c.get('incorporation_date', ''),
                'adresse': format_address(addr),
                'url': c.get('opencorporates_url', ''),
                'registry_url': c.get('registry_url', ''),
                'retrieved_at': c.get('retrieved_at', ''),
                'source': 'OpenCorporates'
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'jurisdiction': jurisdiction,
            'total': data.get('results', {}).get('total_count', 0),
            'page': data.get('results', {}).get('page', 1),
            'per_page': data.get('results', {}).get('per_page', 30),
            'total_pages': data.get('results', {}).get('total_pages', 1),
            'results': results,
            'source': 'OpenCorporates API - Echte Handelsregister-Daten',
            'timestamp': datetime.now().isoformat()
        })
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Timeout - bitte erneut versuchen', 'results': [], 'total': 0}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'API-Fehler: {str(e)}', 'results': [], 'total': 0}), 500


@app.route('/api/hr/company/<path:company_id>')
def hr_company_details(company_id):
    """Firmendetails abrufen"""
    jurisdiction = request.args.get('jurisdiction', 'de')
    
    try:
        url = f"{OPENCORPORATES_BASE_URL}/companies/{jurisdiction}/{company_id}"
        params = {}
        if OPENCORPORATES_API_KEY:
            params['api_token'] = OPENCORPORATES_API_KEY
            
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        c = data.get('results', {}).get('company', {})
        addr = c.get('registered_address', {}) or {}
        
        # Officers extrahieren
        officers = []
        for o in c.get('officers', []):
            off = o.get('officer', {})
            officers.append({
                'name': off.get('name', ''),
                'position': off.get('position', ''),
                'start_date': off.get('start_date', ''),
                'end_date': off.get('end_date', ''),
                'occupation': off.get('occupation', ''),
                'nationality': off.get('nationality', '')
            })
        
        # Frühere Namen
        previous_names = []
        for n in c.get('previous_names', []):
            previous_names.append({
                'name': n.get('company_name', ''),
                'start_date': n.get('start_date', ''),
                'end_date': n.get('end_date', '')
            })
        
        return jsonify({
            'success': True,
            'id': c.get('company_number', ''),
            'name': c.get('name', ''),
            'jurisdiction': c.get('jurisdiction_code', '').upper(),
            'rechtsform': c.get('company_type', ''),
            'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv',
            'gruendung': c.get('incorporation_date', ''),
            'aufloesung': c.get('dissolution_date', ''),
            'adresse': format_address(addr),
            'registered_address': addr,
            'officers': officers,
            'officers_count': len(officers),
            'previous_names': previous_names,
            'branch': c.get('branch', ''),
            'branch_status': c.get('branch_status', ''),
            'home_company': c.get('home_company', {}),
            'industry_codes': c.get('industry_codes', []),
            'filings_count': len(c.get('filings', [])),
            'url': c.get('opencorporates_url', ''),
            'registry_url': c.get('registry_url', ''),
            'retrieved_at': c.get('retrieved_at', ''),
            'source': 'OpenCorporates'
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/hr/officers/search')
def hr_officers_search():
    """Personen suchen (Geschäftsführer, Vorstände)"""
    query = request.args.get('q', '')
    jurisdiction = request.args.get('jurisdiction', 'de')
    
    if not query:
        return jsonify({'error': 'Suchbegriff fehlt', 'results': [], 'total': 0})
    
    try:
        url = f"{OPENCORPORATES_BASE_URL}/officers/search"
        params = {
            'q': query,
            'jurisdiction_code': jurisdiction
        }
        if OPENCORPORATES_API_KEY:
            params['api_token'] = OPENCORPORATES_API_KEY
            
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        for item in data.get('results', {}).get('officers', []):
            o = item.get('officer', {})
            comp = o.get('company', {})
            results.append({
                'name': o.get('name', ''),
                'position': o.get('position', ''),
                'company_name': comp.get('name', ''),
                'company_number': comp.get('company_number', ''),
                'jurisdiction': comp.get('jurisdiction_code', '').upper(),
                'start_date': o.get('start_date', ''),
                'end_date': o.get('end_date', ''),
                'inactive': o.get('inactive', False),
                'url': o.get('opencorporates_url', '')
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'total': data.get('results', {}).get('total_count', 0),
            'results': results,
            'source': 'OpenCorporates'
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': str(e), 'results': [], 'total': 0}), 500


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def extract_court(company_number):
    """Extrahiert Amtsgericht aus Firmennummer wenn möglich"""
    # OpenCorporates speichert das Gericht nicht direkt, 
    # aber manchmal in der Nummer encoded
    return 'Deutschland'

def format_address(addr):
    """Formatiert Adresse als String"""
    if not addr:
        return ''
    parts = [
        addr.get('street_address', ''),
        ' '.join(filter(None, [addr.get('postal_code', ''), addr.get('locality', '')])),
        addr.get('region', ''),
        addr.get('country', '')
    ]
    return ', '.join(p for p in parts if p)


# ============================================================================
# HEALTH & INFO
# ============================================================================

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'West Money OS - Handelsregister API',
        'version': '4.2.0',
        'timestamp': datetime.now().isoformat(),
        'api_key_configured': bool(OPENCORPORATES_API_KEY)
    })


@app.route('/api/info')
def info():
    return jsonify({
        'name': 'West Money OS',
        'version': '4.2.0',
        'description': 'Echte Handelsregister-Daten via OpenCorporates API',
        'endpoints': {
            '/api/hr/search?q=FIRMA': 'Firmensuche',
            '/api/hr/company/NUMMER': 'Firmendetails',
            '/api/hr/officers/search?q=NAME': 'Personensuche',
            '/api/health': 'Health Check'
        },
        'data_source': 'OpenCorporates (opencorporates.com)',
        'coverage': 'Handelsregister Deutschland (HRA, HRB, GnR, PR, VR)'
    })


# ============================================================================
# FRONTEND
# ============================================================================

@app.route('/')
def index():
    return render_template_string(FRONTEND_HTML)


FRONTEND_HTML = r'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>West Money OS | Handelsregister Live</title>
    <meta name="description" content="West Money OS - Echte Handelsregister-Daten für deutsche Unternehmen">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏛️</text></svg>">
    <style>
        :root{--bg:#09090b;--bg2:#111113;--bg3:#18181b;--bg4:#27272a;--text:#fafafa;--text2:#a1a1aa;--text3:#71717a;--primary:#6366f1;--emerald:#10b981;--amber:#f59e0b;--rose:#f43f5e;--hr:#1e3a8a;--cyan:#06b6d4;--border:rgba(255,255,255,0.08);--radius:12px}
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;line-height:1.6}
        .container{max-width:1200px;margin:0 auto;padding:24px}
        header{text-align:center;padding:40px 20px;background:linear-gradient(135deg,var(--bg2),var(--bg3));border-bottom:1px solid var(--border)}
        .logo{display:flex;align-items:center;justify-content:center;gap:16px;margin-bottom:16px}
        .logo-icon{width:64px;height:64px;background:linear-gradient(135deg,var(--hr),var(--primary));border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:32px}
        h1{font-size:32px;font-weight:700}
        .subtitle{color:var(--text2);margin-top:8px}
        .live-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(16,185,129,0.15);color:var(--emerald);padding:6px 16px;border-radius:20px;font-size:13px;font-weight:600;margin-top:16px}
        .live-badge .dot{width:8px;height:8px;background:var(--emerald);border-radius:50%;animation:pulse 2s infinite}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
        .search-section{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin:24px 0}
        .search-row{display:flex;gap:12px;margin-bottom:16px}
        .search-row:last-child{margin-bottom:0}
        input,select{flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:14px 18px;color:var(--text);font-size:15px;transition:border-color 0.2s}
        input:focus,select:focus{outline:none;border-color:var(--primary)}
        input::placeholder{color:var(--text3)}
        button{background:var(--hr);color:white;border:none;border-radius:8px;padding:14px 28px;font-size:15px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:8px;transition:all 0.2s}
        button:hover{opacity:0.9;transform:translateY(-1px)}
        button:disabled{opacity:0.5;cursor:not-allowed;transform:none}
        .btn-secondary{background:var(--bg4)}
        .btn-primary{background:linear-gradient(135deg,var(--primary),#8b5cf6)}
        .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}
        .stat{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:20px;text-align:center}
        .stat.hr{border-left:3px solid var(--hr)}
        .stat.success{border-left:3px solid var(--emerald)}
        .stat-value{font-size:32px;font-weight:700;line-height:1.2}
        .stat-label{font-size:13px;color:var(--text2);margin-top:4px}
        .results{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}
        .results-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
        .results-header h3{font-size:16px;display:flex;align-items:center;gap:8px}
        .result-count{background:var(--hr);color:white;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600}
        .result-item{padding:20px;border-bottom:1px solid var(--border);cursor:pointer;transition:background 0.2s}
        .result-item:hover{background:var(--bg3)}
        .result-item:last-child{border-bottom:none}
        .result-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;gap:12px}
        .result-name{font-weight:600;font-size:16px}
        .result-badges{display:flex;gap:8px;flex-wrap:wrap}
        .badge{padding:4px 10px;border-radius:6px;font-size:11px;font-weight:600;text-transform:uppercase}
        .badge.hrb{background:rgba(99,102,241,0.15);color:var(--primary)}
        .badge.hra{background:rgba(16,185,129,0.15);color:var(--emerald)}
        .badge.gnr{background:rgba(245,158,11,0.15);color:var(--amber)}
        .badge.vr{background:rgba(6,182,212,0.15);color:var(--cyan)}
        .badge.aktiv{background:rgba(16,185,129,0.15);color:var(--emerald)}
        .badge.inaktiv{background:rgba(244,63,94,0.15);color:var(--rose)}
        .result-meta{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;font-size:13px;color:var(--text2)}
        .result-meta div{display:flex;flex-direction:column;gap:2px}
        .result-meta strong{color:var(--text);font-weight:500}
        .loading{text-align:center;padding:60px 20px}
        .spinner{width:48px;height:48px;border:3px solid var(--bg4);border-top-color:var(--primary);border-radius:50%;animation:spin 1s linear infinite;margin:0 auto 16px}
        @keyframes spin{to{transform:rotate(360deg)}}
        .empty{text-align:center;padding:80px 20px;color:var(--text2)}
        .empty-icon{font-size:64px;margin-bottom:16px;opacity:0.5}
        .modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.85);display:none;align-items:center;justify-content:center;z-index:1000;padding:20px;backdrop-filter:blur(4px)}
        .modal-overlay.active{display:flex}
        .modal{background:var(--bg2);border:1px solid var(--border);border-radius:16px;width:100%;max-width:800px;max-height:90vh;overflow:hidden;animation:slideUp 0.3s}
        @keyframes slideUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
        .modal-header{padding:20px 24px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
        .modal-header h2{font-size:20px}
        .modal-close{background:none;border:none;color:var(--text2);font-size:28px;cursor:pointer;padding:0;line-height:1}
        .modal-close:hover{color:var(--text)}
        .modal-body{padding:24px;overflow-y:auto;max-height:calc(90vh - 80px)}
        .detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
        .detail-card{background:var(--bg3);border-radius:10px;padding:20px}
        .detail-card h4{font-size:14px;color:var(--text2);margin-bottom:16px;display:flex;align-items:center;gap:8px}
        .detail-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border);font-size:14px}
        .detail-row:last-child{border-bottom:none}
        .detail-row span:first-child{color:var(--text2)}
        .officer-card{padding:16px;background:var(--bg);border-radius:8px;margin-bottom:12px}
        .officer-card:last-child{margin-bottom:0}
        .officer-name{font-weight:600;font-size:15px}
        .officer-position{font-size:13px;color:var(--primary);margin-top:4px}
        .officer-dates{font-size:12px;color:var(--text3);margin-top:8px}
        .source-box{margin-top:20px;padding:16px;background:rgba(30,58,138,0.1);border:1px solid rgba(30,58,138,0.3);border-radius:10px;font-size:13px}
        .source-box a{color:var(--primary)}
        footer{text-align:center;padding:40px 20px;color:var(--text3);font-size:13px;border-top:1px solid var(--border);margin-top:40px}
        footer a{color:var(--text2)}
        @media(max-width:900px){.stats{grid-template-columns:1fr 1fr}.result-meta{grid-template-columns:1fr 1fr}}
        @media(max-width:600px){.stats{grid-template-columns:1fr}.search-row{flex-direction:column}.result-meta{grid-template-columns:1fr}.detail-grid{grid-template-columns:1fr}.result-header{flex-direction:column}}
    </style>
</head>
<body>
<header>
    <div class="logo">
        <div class="logo-icon">🏛️</div>
        <div>
            <h1>West Money OS</h1>
            <p class="subtitle">Handelsregister Deutschland</p>
        </div>
    </div>
    <div class="live-badge"><span class="dot"></span>Echte Daten via OpenCorporates</div>
</header>

<div class="container">
    <section class="search-section">
        <div class="search-row">
            <input type="text" id="searchQuery" placeholder="Firmenname eingeben (z.B. Deutsche Bahn, Siemens, BMW...)" autofocus>
            <button onclick="searchCompanies()" id="searchBtn">🔍 Suchen</button>
        </div>
        <div class="search-row">
            <input type="text" id="searchOfficer" placeholder="Person suchen (Geschäftsführer, Vorstand...)">
            <button onclick="searchOfficers()" class="btn-secondary">👤 Personen</button>
        </div>
    </section>
    
    <div class="stats">
        <div class="stat hr"><div class="stat-value" id="statTotal">-</div><div class="stat-label">Gefunden</div></div>
        <div class="stat"><div class="stat-value" id="statHRB">-</div><div class="stat-label">HRB</div></div>
        <div class="stat"><div class="stat-value" id="statHRA">-</div><div class="stat-label">HRA</div></div>
        <div class="stat success"><div class="stat-value" id="statAktiv">-</div><div class="stat-label">Aktiv</div></div>
    </div>
    
    <div class="results">
        <div class="results-header">
            <h3>📋 Suchergebnisse</h3>
            <span class="result-count" id="resultCount">0 Treffer</span>
        </div>
        <div id="resultsList">
            <div class="empty">
                <div class="empty-icon">🔍</div>
                <h3>Handelsregister durchsuchen</h3>
                <p>Gib einen Firmennamen ein, um echte Registerdaten abzurufen</p>
            </div>
        </div>
    </div>
</div>

<footer>
    <p><strong>West Money OS</strong> &copy; 2025 Enterprise Universe GmbH</p>
    <p>Daten: <a href="https://opencorporates.com" target="_blank">OpenCorporates</a> | 
       <a href="https://offeneregister.de" target="_blank">OffeneRegister.de</a></p>
</footer>

<div class="modal-overlay" id="modalOverlay" onclick="if(event.target===this)closeModal()">
    <div class="modal">
        <div class="modal-header">
            <h2 id="modalTitle">Firmendetails</h2>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="modal-body" id="modalBody"></div>
    </div>
</div>

<script>
let lastResults = [];

async function searchCompanies() {
    const query = document.getElementById('searchQuery').value.trim();
    if (!query) { alert('Bitte Suchbegriff eingeben'); return; }
    
    const btn = document.getElementById('searchBtn');
    const list = document.getElementById('resultsList');
    
    btn.disabled = true;
    btn.innerHTML = '⏳ Suche...';
    list.innerHTML = '<div class="loading"><div class="spinner"></div><p>Suche im Handelsregister...</p></div>';
    
    try {
        const resp = await fetch('/api/hr/search?q=' + encodeURIComponent(query));
        const data = await resp.json();
        
        document.getElementById('statTotal').textContent = data.total?.toLocaleString() || 0;
        document.getElementById('resultCount').textContent = (data.results?.length || 0) + ' Treffer';
        
        const hrb = data.results?.filter(r => r.registerArt === 'HRB').length || 0;
        const hra = data.results?.filter(r => r.registerArt === 'HRA').length || 0;
        const aktiv = data.results?.filter(r => r.status === 'aktiv').length || 0;
        document.getElementById('statHRB').textContent = hrb;
        document.getElementById('statHRA').textContent = hra;
        document.getElementById('statAktiv').textContent = aktiv;
        
        lastResults = data.results || [];
        
        if (!data.results?.length) {
            list.innerHTML = '<div class="empty"><div class="empty-icon">📭</div><h3>Keine Ergebnisse</h3><p>Versuche einen anderen Suchbegriff</p></div>';
        } else {
            list.innerHTML = data.results.map((r, i) => `
                <div class="result-item" onclick="showDetails(${i})">
                    <div class="result-header">
                        <span class="result-name">${esc(r.name)}</span>
                        <div class="result-badges">
                            ${r.registerArt ? `<span class="badge ${r.registerArt.toLowerCase()}">${r.registerArt}</span>` : ''}
                            <span class="badge ${r.status}">${r.status}</span>
                        </div>
                    </div>
                    <div class="result-meta">
                        <div><span>Registernummer</span><strong>${esc(r.registerNummer) || '-'}</strong></div>
                        <div><span>Sitz</span><strong>${esc(r.sitz) || '-'}</strong></div>
                        <div><span>Rechtsform</span><strong>${esc(r.rechtsform) || '-'}</strong></div>
                        <div><span>Gründung</span><strong>${r.gruendung || '-'}</strong></div>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        list.innerHTML = '<div class="empty"><div class="empty-icon">❌</div><h3>Fehler</h3><p>' + e.message + '</p></div>';
    }
    
    btn.disabled = false;
    btn.innerHTML = '🔍 Suchen';
}

async function searchOfficers() {
    const query = document.getElementById('searchOfficer').value.trim();
    if (!query) { alert('Bitte Namen eingeben'); return; }
    
    const list = document.getElementById('resultsList');
    list.innerHTML = '<div class="loading"><div class="spinner"></div><p>Suche Personen...</p></div>';
    
    try {
        const resp = await fetch('/api/hr/officers/search?q=' + encodeURIComponent(query));
        const data = await resp.json();
        
        document.getElementById('statTotal').textContent = data.total || 0;
        document.getElementById('resultCount').textContent = (data.results?.length || 0) + ' Personen';
        
        if (!data.results?.length) {
            list.innerHTML = '<div class="empty"><div class="empty-icon">👤</div><h3>Keine Personen gefunden</h3></div>';
        } else {
            list.innerHTML = data.results.map(r => `
                <div class="result-item">
                    <div class="result-header">
                        <span class="result-name">👤 ${esc(r.name)}</span>
                        <span class="badge">${esc(r.position) || 'Funktion'}</span>
                    </div>
                    <div class="result-meta">
                        <div><span>Firma</span><strong>${esc(r.company_name) || '-'}</strong></div>
                        <div><span>Register</span><strong>${esc(r.company_number) || '-'}</strong></div>
                        <div><span>Beginn</span><strong>${r.start_date || '-'}</strong></div>
                        <div><span>Ende</span><strong>${r.end_date || 'aktiv'}</strong></div>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        list.innerHTML = '<div class="empty"><div class="empty-icon">❌</div><h3>Fehler</h3><p>' + e.message + '</p></div>';
    }
}

async function showDetails(idx) {
    const r = lastResults[idx];
    if (!r) return;
    
    document.getElementById('modalTitle').textContent = r.name;
    document.getElementById('modalBody').innerHTML = '<div class="loading"><div class="spinner"></div><p>Lade Details...</p></div>';
    document.getElementById('modalOverlay').classList.add('active');
    
    try {
        const resp = await fetch('/api/hr/company/' + encodeURIComponent(r.id));
        const d = await resp.json();
        
        document.getElementById('modalBody').innerHTML = `
            <div class="detail-grid">
                <div class="detail-card">
                    <h4>📋 Registerdaten</h4>
                    <div class="detail-row"><span>Registerart</span><span class="badge ${r.registerArt?.toLowerCase() || ''}">${r.registerArt || '-'}</span></div>
                    <div class="detail-row"><span>Registernummer</span><strong>${d.id || '-'}</strong></div>
                    <div class="detail-row"><span>Status</span><span class="badge ${d.status}">${d.status}</span></div>
                    <div class="detail-row"><span>Gründung</span><strong>${d.gruendung || '-'}</strong></div>
                    ${d.aufloesung ? `<div class="detail-row"><span>Auflösung</span><strong>${d.aufloesung}</strong></div>` : ''}
                </div>
                <div class="detail-card">
                    <h4>🏢 Unternehmen</h4>
                    <div class="detail-row"><span>Rechtsform</span><strong>${d.rechtsform || '-'}</strong></div>
                    <div class="detail-row"><span>Adresse</span><strong>${d.adresse || '-'}</strong></div>
                    <div class="detail-row"><span>Dokumente</span><strong>${d.filings_count || 0}</strong></div>
                </div>
            </div>
            
            ${d.officers?.length ? `
            <div class="detail-card" style="margin-top:16px">
                <h4>👥 Vertretungsberechtigte (${d.officers_count})</h4>
                ${d.officers.slice(0,10).map(o => `
                    <div class="officer-card">
                        <div class="officer-name">${esc(o.name)}</div>
                        <div class="officer-position">${esc(o.position)}</div>
                        ${o.start_date ? `<div class="officer-dates">📅 ${o.start_date}${o.end_date ? ' bis ' + o.end_date : ' - heute'}</div>` : ''}
                    </div>
                `).join('')}
                ${d.officers.length > 10 ? `<p style="color:var(--text3);margin-top:12px">+ ${d.officers.length - 10} weitere</p>` : ''}
            </div>
            ` : ''}
            
            ${d.previous_names?.length ? `
            <div class="detail-card" style="margin-top:16px">
                <h4>📜 Frühere Namen</h4>
                ${d.previous_names.map(n => `<div class="detail-row"><span>${n.start_date || ''} - ${n.end_date || ''}</span><strong>${esc(n.name)}</strong></div>`).join('')}
            </div>
            ` : ''}
            
            <div class="source-box">
                <strong>📊 Datenquelle:</strong> OpenCorporates<br>
                ${d.url ? `<a href="${d.url}" target="_blank">→ Auf OpenCorporates ansehen</a>` : ''}
                ${d.registry_url ? ` | <a href="${d.registry_url}" target="_blank">→ Originalquelle</a>` : ''}
                ${d.retrieved_at ? `<br><small>Letzte Aktualisierung: ${d.retrieved_at}</small>` : ''}
            </div>
        `;
    } catch (e) {
        document.getElementById('modalBody').innerHTML = '<div class="empty"><div class="empty-icon">❌</div><h3>Fehler</h3><p>' + e.message + '</p></div>';
    }
}

function closeModal() { document.getElementById('modalOverlay').classList.remove('active'); }
function esc(s) { return s ? String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') : ''; }

document.getElementById('searchQuery').addEventListener('keypress', e => { if(e.key==='Enter') searchCompanies(); });
document.getElementById('searchOfficer').addEventListener('keypress', e => { if(e.key==='Enter') searchOfficers(); });
document.addEventListener('keydown', e => { if(e.key==='Escape') closeModal(); });
</script>
</body>
</html>'''


if __name__ == '__main__':
    print("=" * 60)
    print("🏛️ West Money OS v4.2 - Production Ready")
    print("=" * 60)
    print(f"✅ Port: {PORT}")
    print(f"✅ API Key: {'Konfiguriert' if OPENCORPORATES_API_KEY else 'Nicht gesetzt (optional)'}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=PORT, debug=False)
