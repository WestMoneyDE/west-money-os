#!/usr/bin/env python3
"""
West Money OS v4.2 - LIVE VERSION
=================================
Mit echten Handelsregister-Daten via OpenCorporates API

Installation:
    pip install flask flask-cors requests

Starten:
    python app.py

Öffnen:
    http://localhost:5000
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# =============================================================================
# KONFIGURATION
# =============================================================================

OPENCORPORATES_BASE_URL = 'https://api.opencorporates.com/v0.4'
OPENCORPORATES_API_KEY = os.getenv('OPENCORPORATES_API_KEY', '')

# =============================================================================
# ECHTE HANDELSREGISTER-SUCHE
# =============================================================================

@app.route('/api/hr/search')
def hr_search():
    """Echte Handelsregister-Suche via OpenCorporates"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Suchbegriff fehlt', 'results': []})
    
    try:
        url = f"{OPENCORPORATES_BASE_URL}/companies/search"
        params = {
            'q': query,
            'jurisdiction_code': 'de',
            'per_page': 30,
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
                'gericht': addr.get('locality', '') or 'Deutschland',
                'sitz': addr.get('locality', '') or addr.get('region', '') or '',
                'rechtsform': c.get('company_type', ''),
                'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv',
                'gruendung': c.get('incorporation_date', ''),
                'adresse': ', '.join(filter(None, [
                    addr.get('street_address', ''),
                    addr.get('postal_code', ''),
                    addr.get('locality', ''),
                    addr.get('country', '')
                ])),
                'url': c.get('opencorporates_url', ''),
                'source': 'OpenCorporates (Handelsregister DE)',
                'retrieved': c.get('retrieved_at', '')
            })
        
        return jsonify({
            'query': query,
            'total': data.get('results', {}).get('total_count', 0),
            'results': results,
            'source': 'OpenCorporates API - Echte Handelsregister-Daten'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'results': []})


@app.route('/api/hr/company/<path:company_id>')
def hr_company_details(company_id):
    """Firmendetails abrufen"""
    try:
        url = f"{OPENCORPORATES_BASE_URL}/companies/de/{company_id}"
        params = {}
        if OPENCORPORATES_API_KEY:
            params['api_token'] = OPENCORPORATES_API_KEY
            
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        c = data.get('results', {}).get('company', {})
        addr = c.get('registered_address', {}) or {}
        
        officers = []
        for o in c.get('officers', []):
            off = o.get('officer', {})
            officers.append({
                'name': off.get('name', ''),
                'position': off.get('position', ''),
                'start': off.get('start_date', ''),
                'end': off.get('end_date', '')
            })
        
        return jsonify({
            'id': c.get('company_number', ''),
            'name': c.get('name', ''),
            'rechtsform': c.get('company_type', ''),
            'status': 'aktiv' if c.get('current_status') == 'Active' else 'inaktiv',
            'gruendung': c.get('incorporation_date', ''),
            'adresse': ', '.join(filter(None, [
                addr.get('street_address', ''),
                addr.get('postal_code', ''),
                addr.get('locality', ''),
                addr.get('country', '')
            ])),
            'officers': officers,
            'previous_names': [n.get('company_name', '') for n in c.get('previous_names', [])],
            'filings': len(c.get('filings', [])),
            'url': c.get('opencorporates_url', ''),
            'registry_url': c.get('registry_url', ''),
            'source': 'OpenCorporates API'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/hr/officers/search')
def hr_officers_search():
    """Personen suchen (Geschäftsführer etc.)"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Suchbegriff fehlt', 'results': []})
    
    try:
        url = f"{OPENCORPORATES_BASE_URL}/officers/search"
        params = {
            'q': query,
            'jurisdiction_code': 'de'
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
                'company': comp.get('name', ''),
                'company_number': comp.get('company_number', ''),
                'start': o.get('start_date', ''),
                'end': o.get('end_date', ''),
                'url': o.get('opencorporates_url', '')
            })
        
        return jsonify({
            'query': query,
            'total': data.get('results', {}).get('total_count', 0),
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'results': []})


# =============================================================================
# HAUPTSEITE - KOMPLETTES FRONTEND
# =============================================================================

@app.route('/')
def index():
    return render_template_string(FRONTEND_HTML)


FRONTEND_HTML = r'''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>West Money OS v4.2 LIVE | Echte Handelsregister-Daten</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        :root{--bg:#09090b;--bg2:#131316;--bg3:#1a1a1f;--text:#fafafa;--text2:#a1a1aa;--primary:#6366f1;--emerald:#10b981;--amber:#f59e0b;--rose:#f43f5e;--hr:#1e3a8a;--border:rgba(255,255,255,0.08)}
        body{font-family:-apple-system,system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;padding:20px}
        .container{max-width:1200px;margin:0 auto}
        h1{font-size:28px;margin-bottom:8px;display:flex;align-items:center;gap:12px}
        .subtitle{color:var(--text2);margin-bottom:24px}
        .live-badge{background:linear-gradient(135deg,var(--emerald),#059669);color:white;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600;animation:pulse 2s infinite}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.7}}
        .search-box{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:24px}
        .search-row{display:flex;gap:12px;margin-bottom:16px}
        input,select{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:12px 16px;color:var(--text);font-size:14px;flex:1}
        input:focus,select:focus{outline:none;border-color:var(--primary)}
        button{background:var(--hr);color:white;border:none;border-radius:8px;padding:12px 24px;font-size:14px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:8px}
        button:hover{opacity:0.9}
        button:disabled{opacity:0.5;cursor:not-allowed}
        .btn-secondary{background:var(--bg3);border:1px solid var(--border)}
        .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px}
        .stat{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px;text-align:center}
        .stat.hr{border-left:3px solid var(--hr)}
        .stat-value{font-size:28px;font-weight:700}
        .stat-label{font-size:12px;color:var(--text2);margin-top:4px}
        .results{background:var(--bg2);border:1px solid var(--border);border-radius:12px;overflow:hidden}
        .results-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
        .results-header h3{font-size:15px}
        .result-count{background:var(--hr);color:white;padding:4px 12px;border-radius:20px;font-size:12px}
        .result-item{padding:16px 20px;border-bottom:1px solid var(--border);cursor:pointer;transition:background 0.2s}
        .result-item:hover{background:var(--bg3)}
        .result-item:last-child{border-bottom:none}
        .result-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
        .result-name{font-weight:600;font-size:15px}
        .result-badges{display:flex;gap:8px}
        .badge{padding:4px 8px;border-radius:4px;font-size:10px;font-weight:600}
        .badge.hrb{background:rgba(99,102,241,0.15);color:var(--primary)}
        .badge.hra{background:rgba(16,185,129,0.15);color:var(--emerald)}
        .badge.aktiv{background:rgba(16,185,129,0.15);color:var(--emerald)}
        .badge.inaktiv{background:rgba(244,63,94,0.15);color:var(--rose)}
        .result-meta{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;font-size:12px;color:var(--text2)}
        .result-meta strong{color:var(--text);display:block}
        .loading{text-align:center;padding:40px;color:var(--text2)}
        .loading-spinner{width:40px;height:40px;border:3px solid var(--bg3);border-top-color:var(--primary);border-radius:50%;animation:spin 1s linear infinite;margin:0 auto 16px}
        @keyframes spin{to{transform:rotate(360deg)}}
        .empty{text-align:center;padding:60px 20px;color:var(--text2)}
        .empty-icon{font-size:48px;margin-bottom:16px;opacity:0.5}
        .modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.8);display:none;align-items:center;justify-content:center;z-index:1000;padding:20px}
        .modal-overlay.active{display:flex}
        .modal{background:var(--bg2);border:1px solid var(--border);border-radius:16px;width:100%;max-width:700px;max-height:90vh;overflow:hidden}
        .modal-header{padding:20px 24px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
        .modal-header h2{font-size:18px}
        .modal-close{background:none;border:none;color:var(--text2);font-size:24px;cursor:pointer;padding:0}
        .modal-body{padding:24px;overflow-y:auto;max-height:60vh}
        .detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
        .detail-card{background:var(--bg3);border-radius:8px;padding:16px}
        .detail-card h4{font-size:13px;color:var(--text2);margin-bottom:12px}
        .detail-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);font-size:13px}
        .detail-row:last-child{border-bottom:none}
        .officer-item{padding:12px;background:var(--bg);border-radius:8px;margin-bottom:8px}
        .officer-name{font-weight:600}
        .officer-position{font-size:12px;color:var(--text2)}
        .source-info{margin-top:16px;padding:12px;background:rgba(30,58,138,0.1);border-radius:8px;font-size:12px;color:var(--text2)}
        .source-info a{color:var(--primary)}
        .api-info{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:24px;font-size:13px}
        .api-info h4{margin-bottom:8px;color:var(--emerald)}
        @media(max-width:768px){.stats{grid-template-columns:1fr 1fr}.search-row{flex-direction:column}.detail-grid{grid-template-columns:1fr}.result-meta{grid-template-columns:1fr}}
    </style>
</head>
<body>
<div class="container">
    <h1>🏛️ West Money OS <span class="live-badge">🔴 LIVE DATEN</span></h1>
    <p class="subtitle">Echte Handelsregister-Daten via OpenCorporates API</p>
    
    <div class="api-info">
        <h4>✅ Echte Daten aktiv</h4>
        <p>Diese Anwendung ruft echte Firmendaten aus dem deutschen Handelsregister ab. Datenquelle: <a href="https://opencorporates.com" target="_blank">OpenCorporates</a> - Die weltweit größte offene Firmendatenbank.</p>
    </div>
    
    <div class="search-box">
        <div class="search-row">
            <input type="text" id="searchQuery" placeholder="Firmenname eingeben (z.B. Deutsche Bahn, Siemens, BMW...)" onkeypress="if(event.key==='Enter')searchCompanies()">
            <button onclick="searchCompanies()" id="searchBtn">🔍 Suchen</button>
        </div>
        <div class="search-row">
            <input type="text" id="searchOfficer" placeholder="Person suchen (Geschäftsführer, Vorstand...)" onkeypress="if(event.key==='Enter')searchOfficers()">
            <button onclick="searchOfficers()" class="btn-secondary">👤 Personen suchen</button>
        </div>
    </div>
    
    <div class="stats">
        <div class="stat hr"><div class="stat-value" id="statTotal">-</div><div class="stat-label">Gefundene Firmen</div></div>
        <div class="stat"><div class="stat-value" id="statSearches">0</div><div class="stat-label">Suchen heute</div></div>
        <div class="stat"><div class="stat-value" id="statHRB">-</div><div class="stat-label">HRB Einträge</div></div>
        <div class="stat"><div class="stat-value" id="statHRA">-</div><div class="stat-label">HRA Einträge</div></div>
    </div>
    
    <div class="results" id="resultsContainer">
        <div class="results-header">
            <h3>📋 Suchergebnisse</h3>
            <span class="result-count" id="resultCount">0 Treffer</span>
        </div>
        <div id="resultsList">
            <div class="empty">
                <div class="empty-icon">🔍</div>
                <h3>Suche starten</h3>
                <p>Gib einen Firmennamen ein, um echte Handelsregister-Daten abzurufen</p>
            </div>
        </div>
    </div>
</div>

<div class="modal-overlay" id="modalOverlay" onclick="if(event.target===this)closeModal()">
    <div class="modal">
        <div class="modal-header">
            <h2 id="modalTitle">Firmendetails</h2>
            <button class="modal-close" onclick="closeModal()">×</button>
        </div>
        <div class="modal-body" id="modalBody"></div>
    </div>
</div>

<script>
let searchCount = 0;
let lastResults = [];

async function searchCompanies() {
    const query = document.getElementById('searchQuery').value.trim();
    if (!query) return alert('Bitte Suchbegriff eingeben');
    
    const btn = document.getElementById('searchBtn');
    const list = document.getElementById('resultsList');
    
    btn.disabled = true;
    btn.innerHTML = '⏳ Suche...';
    list.innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Suche im Handelsregister...</p></div>';
    
    try {
        const resp = await fetch(`/api/hr/search?q=${encodeURIComponent(query)}`);
        const data = await resp.json();
        
        searchCount++;
        document.getElementById('statSearches').textContent = searchCount;
        document.getElementById('statTotal').textContent = data.total || 0;
        document.getElementById('resultCount').textContent = `${data.results?.length || 0} Treffer`;
        
        // Statistiken
        const hrb = data.results?.filter(r => r.registerArt === 'HRB').length || 0;
        const hra = data.results?.filter(r => r.registerArt === 'HRA').length || 0;
        document.getElementById('statHRB').textContent = hrb;
        document.getElementById('statHRA').textContent = hra;
        
        lastResults = data.results || [];
        
        if (!data.results || data.results.length === 0) {
            list.innerHTML = '<div class="empty"><div class="empty-icon">📭</div><h3>Keine Ergebnisse</h3><p>Versuche einen anderen Suchbegriff</p></div>';
        } else {
            list.innerHTML = data.results.map((r, i) => `
                <div class="result-item" onclick="showDetails(${i})">
                    <div class="result-header">
                        <span class="result-name">${escapeHtml(r.name)}</span>
                        <div class="result-badges">
                            ${r.registerArt ? `<span class="badge ${r.registerArt.toLowerCase()}">${r.registerArt}</span>` : ''}
                            <span class="badge ${r.status}">${r.status}</span>
                        </div>
                    </div>
                    <div class="result-meta">
                        <div><span>Registernummer</span><strong>${escapeHtml(r.registerNummer || '-')}</strong></div>
                        <div><span>Sitz</span><strong>${escapeHtml(r.sitz || '-')}</strong></div>
                        <div><span>Rechtsform</span><strong>${escapeHtml(r.rechtsform || '-')}</strong></div>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        list.innerHTML = `<div class="empty"><div class="empty-icon">❌</div><h3>Fehler</h3><p>${e.message}</p></div>`;
    }
    
    btn.disabled = false;
    btn.innerHTML = '🔍 Suchen';
}

async function searchOfficers() {
    const query = document.getElementById('searchOfficer').value.trim();
    if (!query) return alert('Bitte Namen eingeben');
    
    const list = document.getElementById('resultsList');
    list.innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Suche Personen...</p></div>';
    
    try {
        const resp = await fetch(`/api/hr/officers/search?q=${encodeURIComponent(query)}`);
        const data = await resp.json();
        
        searchCount++;
        document.getElementById('statSearches').textContent = searchCount;
        document.getElementById('resultCount').textContent = `${data.results?.length || 0} Personen`;
        
        if (!data.results || data.results.length === 0) {
            list.innerHTML = '<div class="empty"><div class="empty-icon">👤</div><h3>Keine Personen gefunden</h3></div>';
        } else {
            list.innerHTML = data.results.map(r => `
                <div class="result-item">
                    <div class="result-header">
                        <span class="result-name">👤 ${escapeHtml(r.name)}</span>
                        <span class="badge">${escapeHtml(r.position || 'Funktion unbekannt')}</span>
                    </div>
                    <div class="result-meta">
                        <div><span>Firma</span><strong>${escapeHtml(r.company || '-')}</strong></div>
                        <div><span>Beginn</span><strong>${r.start || '-'}</strong></div>
                        <div><span>Ende</span><strong>${r.end || 'aktiv'}</strong></div>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        list.innerHTML = `<div class="empty"><div class="empty-icon">❌</div><h3>Fehler</h3><p>${e.message}</p></div>`;
    }
}

async function showDetails(index) {
    const r = lastResults[index];
    if (!r) return;
    
    document.getElementById('modalTitle').textContent = r.name;
    document.getElementById('modalBody').innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Lade Details...</p></div>';
    document.getElementById('modalOverlay').classList.add('active');
    
    try {
        const resp = await fetch(`/api/hr/company/${encodeURIComponent(r.id)}`);
        const data = await resp.json();
        
        document.getElementById('modalBody').innerHTML = `
            <div class="detail-grid">
                <div class="detail-card">
                    <h4>📋 Registerdaten</h4>
                    <div class="detail-row"><span>Registerart</span><strong>${r.registerArt || '-'}</strong></div>
                    <div class="detail-row"><span>Registernummer</span><strong>${data.id || r.registerNummer}</strong></div>
                    <div class="detail-row"><span>Status</span><span class="badge ${data.status}">${data.status}</span></div>
                    <div class="detail-row"><span>Gründung</span><strong>${data.gruendung || '-'}</strong></div>
                </div>
                <div class="detail-card">
                    <h4>🏢 Unternehmensdaten</h4>
                    <div class="detail-row"><span>Rechtsform</span><strong>${data.rechtsform || '-'}</strong></div>
                    <div class="detail-row"><span>Adresse</span><strong>${data.adresse || '-'}</strong></div>
                    <div class="detail-row"><span>Dokumente</span><strong>${data.filings || 0} Einträge</strong></div>
                </div>
            </div>
            
            ${data.officers && data.officers.length > 0 ? `
            <div class="detail-card" style="margin-top:16px">
                <h4>👥 Vertretungsberechtigte (${data.officers.length})</h4>
                ${data.officers.map(o => `
                    <div class="officer-item">
                        <div class="officer-name">${escapeHtml(o.name)}</div>
                        <div class="officer-position">${escapeHtml(o.position)} ${o.start ? `(seit ${o.start})` : ''}</div>
                    </div>
                `).join('')}
            </div>
            ` : ''}
            
            ${data.previous_names && data.previous_names.length > 0 ? `
            <div class="detail-card" style="margin-top:16px">
                <h4>📜 Frühere Namen</h4>
                ${data.previous_names.map(n => `<div style="padding:4px 0">${escapeHtml(n)}</div>`).join('')}
            </div>
            ` : ''}
            
            <div class="source-info">
                <strong>Datenquelle:</strong> OpenCorporates (${data.source})<br>
                ${data.url ? `<a href="${data.url}" target="_blank">→ Auf OpenCorporates ansehen</a>` : ''}
                ${data.registry_url ? ` | <a href="${data.registry_url}" target="_blank">→ Originalquelle</a>` : ''}
            </div>
        `;
    } catch (e) {
        document.getElementById('modalBody').innerHTML = `<div class="empty"><div class="empty-icon">❌</div><h3>Fehler</h3><p>${e.message}</p></div>`;
    }
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Keyboard shortcuts
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});
</script>
</body>
</html>
'''

if __name__ == '__main__':
    print("=" * 60)
    print("🏛️ West Money OS v4.2 - LIVE VERSION")
    print("=" * 60)
    print("✅ Echte Handelsregister-Daten via OpenCorporates API")
    print("")
    print("Server starten auf: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
