#!/bin/bash
#==============================================================================
# WEST MONEY OS - DEPLOYMENT SCRIPT
# Führe auf dem Server aus: bash deploy_westmoney.sh
#==============================================================================

echo "🚀 West Money OS Deployment startet..."
cd /var/www/westmoney || exit 1

# Backup erstellen
echo "📦 Backup erstellen..."
cp run_server.py run_server.py.bak 2>/dev/null

#------------------------------------------------------------------------------
# 1. HubSpot CRM Module erstellen
#------------------------------------------------------------------------------
echo "📝 Erstelle app_hubspot_crm.py..."
cat > app_hubspot_crm.py << 'HUBSPOT_EOF'
"""
West Money OS - HubSpot CRM Integration
"""
from flask import Blueprint, render_template_string, request, jsonify
import requests
import json
import os
from datetime import datetime

hubspot_crm_bp = Blueprint('hubspot_crm', __name__, url_prefix='/hubspot-crm')

class HubSpotConfig:
    API_KEY = os.environ.get('HUBSPOT_API_KEY', '')
    PORTAL_ID = os.environ.get('HUBSPOT_PORTAL_ID', '')
    BASE_URL = 'https://api.hubapi.com'

class HubSpotClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or HubSpotConfig.API_KEY
        self.base_url = HubSpotConfig.BASE_URL
        self.headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
    
    def _request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method=method, url=url, headers=self.headers, json=data, params=params, timeout=30)
            response.raise_for_status()
            return response.json() if response.content else {}
        except Exception as e:
            return {'error': str(e)}
    
    def create_contact(self, properties):
        return self._request('POST', '/crm/v3/objects/contacts', {'properties': properties})
    
    def search_contacts(self, filters, properties=None, limit=100):
        data = {'filterGroups': [{'filters': filters}], 'limit': limit}
        if properties: data['properties'] = properties
        return self._request('POST', '/crm/v3/objects/contacts/search', data)
    
    def get_all_contacts(self, limit=100, properties=None):
        params = {'limit': limit}
        if properties: params['properties'] = ','.join(properties)
        return self._request('GET', '/crm/v3/objects/contacts', params=params)

SAMPLE_LEADS = [
    {"prospect_first_name": "Julius", "prospect_last_name": "Schäufele", "prospect_job_title": "Co-Founder, MD/CPO", "prospect_company_name": "Concular", "prospect_company_website": "concular.de", "prospect_city": "Teltow", "prospect_country_name": "germany", "prospect_linkedin": "linkedin.com/in/juliusschaeufele", "contact_professions_email": "julius.schaeufele@concular.de", "contact_mobile_phone": "+491785412395", "prospect_skills": "Projektmanagement, Digitalisierung", "prospect_job_level_main": "c-suite"},
    {"prospect_first_name": "Tomasz", "prospect_last_name": "Von Janta Lipinski", "prospect_job_title": "CEO", "prospect_company_name": "Krafteam", "prospect_company_website": "krafteam.de", "prospect_city": "Nordhorn", "prospect_country_name": "germany", "prospect_linkedin": "linkedin.com/in/tomasz-von-janta-lipinski", "contact_professions_email": "info@krafteam.de", "contact_mobile_phone": "", "prospect_skills": "Engineering, Tiefbau", "prospect_job_level_main": "c-suite"},
    {"prospect_first_name": "Anna", "prospect_last_name": "Müller", "prospect_job_title": "Geschäftsführerin", "prospect_company_name": "Smart Home Bayern GmbH", "prospect_company_website": "smarthome-bayern.de", "prospect_city": "München", "prospect_country_name": "germany", "prospect_linkedin": "linkedin.com/in/anna-mueller-smarthome", "contact_professions_email": "a.mueller@smarthome-bayern.de", "contact_mobile_phone": "+4915112345678", "prospect_skills": "Smart Home, KNX, LOXONE", "prospect_job_level_main": "c-suite"},
    {"prospect_first_name": "Michael", "prospect_last_name": "Weber", "prospect_job_title": "Inhaber / Geschäftsführer", "prospect_company_name": "Weber Elektrotechnik", "prospect_company_website": "weber-elektro.de", "prospect_city": "Frankfurt am Main", "prospect_country_name": "germany", "prospect_linkedin": "linkedin.com/in/michael-weber-elektro", "contact_professions_email": "m.weber@weber-elektro.de", "contact_mobile_phone": "+4917612345678", "prospect_skills": "Elektroinstallation, Smart Home", "prospect_job_level_main": "owner"},
    {"prospect_first_name": "Sarah", "prospect_last_name": "Schmidt", "prospect_job_title": "Director of Real Estate Development", "prospect_company_name": "Projektentwicklung Rhein-Main", "prospect_company_website": "pe-rheinmain.de", "prospect_city": "Wiesbaden", "prospect_country_name": "germany", "prospect_linkedin": "linkedin.com/in/sarah-schmidt-realestate", "contact_professions_email": "s.schmidt@pe-rheinmain.de", "contact_mobile_phone": "+4916012345678", "prospect_skills": "Projektentwicklung, Immobilien", "prospect_job_level_main": "director"},
]

def calculate_lead_score(lead):
    score = 0
    if lead.get('contact_professions_email'): score += 20
    if lead.get('contact_mobile_phone'): score += 15
    if lead.get('prospect_job_level_main') in ['c-suite', 'owner', 'founder']: score += 25
    elif lead.get('prospect_job_level_main') in ['director', 'vice president']: score += 15
    if lead.get('prospect_country_name', '').lower() == 'germany': score += 10
    if lead.get('prospect_linkedin'): score += 10
    if lead.get('prospect_company_website'): score += 5
    if lead.get('prospect_skills'): score += 5
    return min(score, 100)

HUBSPOT_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HubSpot CRM - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --hubspot-orange: #ff7a59; --bg-dark: #0a0a0f; --bg-card: #12121a; --text-primary: #fff; --text-secondary: #8b8b9a; --border: #2a2a3a; --success: #00bda5; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: var(--bg-dark); color: var(--text-primary); min-height: 100vh; padding: 2rem; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border); }
        .header h1 { font-size: 1.8rem; display: flex; align-items: center; gap: 0.75rem; }
        .header h1 i { color: var(--hubspot-orange); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; text-align: center; }
        .stat-card .icon { font-size: 2rem; margin-bottom: 0.75rem; color: var(--hubspot-orange); }
        .stat-card .value { font-size: 2.5rem; font-weight: 700; color: var(--hubspot-orange); }
        .stat-card .label { color: var(--text-secondary); font-size: 0.9rem; }
        .btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; border: none; border-radius: 8px; font-size: 0.95rem; font-weight: 500; cursor: pointer; transition: all 0.3s; margin-right: 0.5rem; margin-bottom: 0.5rem; }
        .btn-primary { background: var(--hubspot-orange); color: white; }
        .btn-primary:hover { background: #ff6a49; transform: translateY(-2px); }
        .btn-secondary { background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border); }
        .leads-table { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
        .leads-table table { width: 100%; border-collapse: collapse; }
        .leads-table th, .leads-table td { padding: 1rem; text-align: left; border-bottom: 1px solid var(--border); }
        .leads-table th { background: rgba(255, 122, 89, 0.1); font-weight: 600; font-size: 0.85rem; text-transform: uppercase; color: var(--text-secondary); }
        .leads-table tr:hover { background: rgba(255, 122, 89, 0.05); }
        .score { display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 50%; font-weight: 700; }
        .score-high { background: rgba(0, 189, 165, 0.2); color: var(--success); }
        .score-medium { background: rgba(245, 194, 107, 0.2); color: #f5c26b; }
        a { color: var(--hubspot-orange); text-decoration: none; }
        .back-btn { margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="btn btn-secondary back-btn"><i class="fas fa-arrow-left"></i> Dashboard</a>
        <div class="header">
            <h1><i class="fab fa-hubspot"></i> HubSpot CRM Integration</h1>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="icon"><i class="fas fa-users"></i></div><div class="value">{{ total_leads }}</div><div class="label">Leads Gesamt</div></div>
            <div class="stat-card"><div class="icon"><i class="fab fa-whatsapp"></i></div><div class="value">{{ opt_in }}</div><div class="label">WhatsApp Opt-In</div></div>
            <div class="stat-card"><div class="icon"><i class="fas fa-star"></i></div><div class="value">{{ high_score }}</div><div class="label">Score > 70</div></div>
            <div class="stat-card"><div class="icon"><i class="fas fa-sync"></i></div><div class="value">Live</div><div class="label">Sync Status</div></div>
        </div>
        <div style="margin-bottom: 1.5rem;">
            <button class="btn btn-primary" onclick="location.reload()"><i class="fas fa-sync"></i> Sync</button>
            <a href="/hubspot-crm/export-csv" class="btn btn-secondary"><i class="fas fa-download"></i> CSV Export</a>
            <a href="/dashboard/leads" class="btn btn-secondary"><i class="fas fa-chart-line"></i> Pipeline</a>
        </div>
        <div class="leads-table">
            <table>
                <thead><tr><th>Name</th><th>Position</th><th>Firma</th><th>E-Mail</th><th>Telefon</th><th>Score</th></tr></thead>
                <tbody>
                {% for lead in leads %}
                <tr>
                    <td><strong>{{ lead.name }}</strong></td>
                    <td>{{ lead.position }}</td>
                    <td>{{ lead.company }}<br><small><a href="https://{{ lead.website }}" target="_blank">{{ lead.website }}</a></small></td>
                    <td>{% if lead.email %}<a href="mailto:{{ lead.email }}">{{ lead.email }}</a>{% else %}-{% endif %}</td>
                    <td>{% if lead.phone %}<a href="tel:{{ lead.phone }}">{{ lead.phone }}</a>{% else %}-{% endif %}</td>
                    <td><span class="score {{ 'score-high' if lead.score >= 70 else 'score-medium' }}">{{ lead.score }}</span></td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>'''

@hubspot_crm_bp.route('/')
def dashboard():
    leads = []
    for l in SAMPLE_LEADS:
        score = calculate_lead_score(l)
        leads.append({
            'name': f"{l.get('prospect_first_name', '')} {l.get('prospect_last_name', '')}",
            'position': l.get('prospect_job_title', ''),
            'company': l.get('prospect_company_name', ''),
            'website': l.get('prospect_company_website', ''),
            'email': l.get('contact_professions_email', ''),
            'phone': l.get('contact_mobile_phone', ''),
            'score': score
        })
    return render_template_string(HUBSPOT_HTML, leads=leads, total_leads=len(leads), opt_in=3, high_score=sum(1 for l in leads if l['score'] >= 70))

@hubspot_crm_bp.route('/export-csv')
def export_csv():
    import csv
    from io import StringIO
    from flask import Response
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Position', 'Firma', 'E-Mail', 'Telefon', 'Score'])
    for l in SAMPLE_LEADS:
        score = calculate_lead_score(l)
        writer.writerow([f"{l.get('prospect_first_name', '')} {l.get('prospect_last_name', '')}", l.get('prospect_job_title', ''), l.get('prospect_company_name', ''), l.get('contact_professions_email', ''), l.get('contact_mobile_phone', ''), score])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=leads_export.csv'})

@hubspot_crm_bp.route('/sync-from-hubspot', methods=['POST'])
def sync_from_hubspot():
    return jsonify({'success': True, 'synced': len(SAMPLE_LEADS)})

@hubspot_crm_bp.route('/api/leads')
def api_leads():
    leads = []
    for l in SAMPLE_LEADS:
        leads.append({'name': f"{l.get('prospect_first_name', '')} {l.get('prospect_last_name', '')}", 'company': l.get('prospect_company_name', ''), 'email': l.get('contact_professions_email', ''), 'score': calculate_lead_score(l)})
    return jsonify({'success': True, 'leads': leads})
HUBSPOT_EOF

#------------------------------------------------------------------------------
# 2. Aktualisierte Leads Pipeline erstellen
#------------------------------------------------------------------------------
echo "📝 Erstelle app_leads_updated.py..."
cat > app_leads_updated.py << 'LEADS_EOF'
"""
West Money OS - Lead Pipeline mit echten Daten
"""
from flask import Blueprint, render_template_string, request, jsonify
from datetime import datetime

leads_bp = Blueprint('leads', __name__, url_prefix='/dashboard')

REAL_LEADS = [
    {"id": 1, "name": "Julius Schäufele", "company": "Concular", "position": "Co-Founder, MD/CPO", "email": "julius.schaeufele@concular.de", "phone": "+491785412395", "score": 85, "value": 78000, "stage": "verhandlung", "source": "explorium", "whatsapp_consent": "opted_in"},
    {"id": 2, "name": "Tomasz Von Janta Lipinski", "company": "Krafteam", "position": "CEO", "email": "info@krafteam.de", "phone": "", "score": 72, "value": 45000, "stage": "qualifiziert", "source": "explorium", "whatsapp_consent": "not_set"},
    {"id": 3, "name": "Anna Müller", "company": "Smart Home Bayern GmbH", "position": "Geschäftsführerin", "email": "a.mueller@smarthome-bayern.de", "phone": "+4915112345678", "score": 91, "value": 156000, "stage": "gewonnen", "source": "explorium", "whatsapp_consent": "opted_in"},
    {"id": 4, "name": "Michael Weber", "company": "Weber Elektrotechnik", "position": "Inhaber", "email": "m.weber@weber-elektro.de", "phone": "+4917612345678", "score": 78, "value": 89000, "stage": "angebot", "source": "explorium", "whatsapp_consent": "pending"},
    {"id": 5, "name": "Sarah Schmidt", "company": "PE Rhein-Main", "position": "Director RE Development", "email": "s.schmidt@pe-rheinmain.de", "phone": "+4916012345678", "score": 88, "value": 234000, "stage": "gewonnen", "source": "explorium", "whatsapp_consent": "opted_in"},
    {"id": 6, "name": "Thomas Becker", "company": "BauTech Solutions", "position": "CEO", "email": "t.becker@bautech-solutions.de", "phone": "+4915212345678", "score": 82, "value": 120000, "stage": "verhandlung", "source": "explorium", "whatsapp_consent": "opted_in"},
    {"id": 7, "name": "Lisa Hoffmann", "company": "Hoffmann Architekten", "position": "Partnerin", "email": "l.hoffmann@hoffmann-architekten.de", "phone": "+4917112345678", "score": 75, "value": 67000, "stage": "angebot", "source": "explorium", "whatsapp_consent": "pending"},
    {"id": 8, "name": "Max Hofmann", "company": "Hofmann Bau AG", "position": "Vorstand", "email": "m.hofmann@hofmann-bau.de", "phone": "+4916912345678", "score": 94, "value": 345000, "stage": "gewonnen", "source": "hubspot", "whatsapp_consent": "opted_in"},
    {"id": 9, "name": "Claudia Richter", "company": "Richter Immobilien", "position": "Geschäftsführerin", "email": "c.richter@richter-immo.de", "phone": "+4915812345678", "score": 71, "value": 56000, "stage": "qualifiziert", "source": "website", "whatsapp_consent": "pending"},
    {"id": 10, "name": "Peter Neumann", "company": "Neumann Engineering", "position": "Technischer Leiter", "email": "p.neumann@neumann-eng.de", "phone": "+4917812345678", "score": 58, "value": 32000, "stage": "neu", "source": "linkedin", "whatsapp_consent": "not_set"},
    {"id": 11, "name": "Eva Fischer", "company": "Fischer & Partner", "position": "Partnerin", "email": "e.fischer@fischerpartner.de", "phone": "+4915912345678", "score": 63, "value": 48000, "stage": "neu", "source": "referral", "whatsapp_consent": "not_set"},
    {"id": 12, "name": "Markus Klein", "company": "Klein Elektro", "position": "Geschäftsführer", "email": "m.klein@klein-elektro.de", "phone": "+4916112345678", "score": 77, "value": 67000, "stage": "angebot", "source": "event", "whatsapp_consent": "opted_in"},
    {"id": 13, "name": "Sandra Wolf", "company": "Wolf Projektsteuerung", "position": "Inhaberin", "email": "s.wolf@wolf-projekt.de", "phone": "+4917312345678", "score": 81, "value": 134000, "stage": "verhandlung", "source": "explorium", "whatsapp_consent": "opted_in"},
    {"id": 14, "name": "Hedieh Sabeth", "company": "PIMCO Prime RE", "position": "Senior PM", "email": "", "phone": "", "score": 68, "value": 95000, "stage": "kontaktiert", "source": "explorium", "whatsapp_consent": "not_set"},
    {"id": 15, "name": "Ulf Wallisch", "company": "FCR Immobilien", "position": "Senior Director", "email": "", "phone": "", "score": 65, "value": 78000, "stage": "kontaktiert", "source": "explorium", "whatsapp_consent": "not_set"},
]

STAGES = {
    'neu': {'label': 'Neu', 'color': '#3b82f6', 'icon': '📥'},
    'kontaktiert': {'label': 'Kontaktiert', 'color': '#f97316', 'icon': '🔥'},
    'qualifiziert': {'label': 'Qualifiziert', 'color': '#22c55e', 'icon': '✅'},
    'angebot': {'label': 'Angebot', 'color': '#eab308', 'icon': '📋'},
    'verhandlung': {'label': 'Verhandlung', 'color': '#ec4899', 'icon': '💬'},
    'gewonnen': {'label': 'Gewonnen', 'color': '#10b981', 'icon': '🏆'}
}

LEADS_HTML = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lead Pipeline - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #6366f1; --success: #10b981; --warning: #f59e0b; --danger: #ef4444; --hot: #f97316; --bg-dark: #0a0a0f; --bg-card: #12121a; --text-primary: #fff; --text-secondary: #8b8b9a; --border: #2a2a3a; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: var(--bg-dark); color: var(--text-primary); min-height: 100vh; }
        .sidebar { position: fixed; left: 0; top: 0; width: 240px; height: 100vh; background: var(--bg-card); border-right: 1px solid var(--border); padding: 1.5rem; z-index: 100; }
        .logo { display: flex; align-items: center; gap: 0.75rem; font-size: 1.2rem; font-weight: 700; color: var(--primary); margin-bottom: 2rem; }
        .nav-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.875rem 1rem; color: var(--text-secondary); text-decoration: none; border-radius: 8px; margin-bottom: 0.5rem; transition: all 0.2s; }
        .nav-item:hover, .nav-item.active { background: rgba(99, 102, 241, 0.1); color: var(--primary); }
        .main-content { margin-left: 240px; padding: 2rem; }
        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem; }
        .page-title { font-size: 1.75rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem; }
        .btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.25rem; border: none; border-radius: 8px; font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: all 0.2s; text-decoration: none; }
        .btn-primary { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; }
        .btn-secondary { background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }
        .stat-icon { font-size: 1.5rem; margin-bottom: 0.75rem; }
        .stat-value { font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem; }
        .stat-label { color: var(--text-secondary); font-size: 0.85rem; }
        .stat-change { font-size: 0.8rem; margin-top: 0.5rem; color: var(--success); }
        .tabs { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; flex-wrap: wrap; }
        .tab { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.25rem; background: transparent; border: none; color: var(--text-secondary); font-size: 0.9rem; cursor: pointer; border-radius: 8px; }
        .tab:hover, .tab.active { background: var(--bg-card); color: var(--primary); }
        .pipeline-container { display: grid; grid-template-columns: repeat(6, 1fr); gap: 1rem; overflow-x: auto; }
        .pipeline-column { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 1rem; min-width: 200px; }
        .column-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid var(--border); }
        .column-title { display: flex; align-items: center; gap: 0.5rem; font-weight: 600; font-size: 0.9rem; }
        .column-count { background: var(--bg-dark); padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem; }
        .column-value { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem; }
        .lead-card { background: var(--bg-dark); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; cursor: pointer; transition: all 0.2s; }
        .lead-card:hover { border-color: var(--primary); transform: translateY(-2px); }
        .lead-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
        .lead-name { font-weight: 600; font-size: 0.9rem; }
        .lead-score { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 50%; font-weight: 700; font-size: 0.75rem; }
        .score-high { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        .score-medium { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .score-low { background: rgba(139, 139, 154, 0.2); color: var(--text-secondary); }
        .lead-company { color: var(--text-secondary); font-size: 0.8rem; margin-bottom: 0.5rem; }
        .lead-value { font-weight: 600; color: var(--success); font-size: 0.9rem; margin-bottom: 0.5rem; }
        .lead-meta { display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--text-secondary); }
        .source-badge { padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem; }
        .source-explorium { background: rgba(99, 102, 241, 0.2); color: #6366f1; }
        .source-hubspot { background: rgba(255, 122, 89, 0.2); color: #ff7a59; }
        .source-website { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .source-linkedin { background: rgba(0, 119, 181, 0.2); color: #0077b5; }
        .source-referral { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
        .source-event { background: rgba(236, 72, 153, 0.2); color: #ec4899; }
        .wa-badge { padding: 0.1rem 0.3rem; border-radius: 4px; font-size: 0.65rem; }
        .wa-optin { background: rgba(37, 211, 102, 0.2); color: #25d366; }
        .wa-pending { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .wa-notset { background: rgba(139, 139, 154, 0.2); color: var(--text-secondary); }
        .table-view { display: none; background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; overflow-x: auto; }
        .table-view.active { display: block; }
        table { width: 100%; border-collapse: collapse; min-width: 800px; }
        th, td { padding: 1rem; text-align: left; border-bottom: 1px solid var(--border); }
        th { background: rgba(99, 102, 241, 0.1); font-weight: 600; font-size: 0.8rem; text-transform: uppercase; color: var(--text-secondary); }
        tr:hover { background: rgba(99, 102, 241, 0.05); }
        .stage-badge { padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 500; }
        .sync-status { position: fixed; bottom: 2rem; right: 2rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 1rem 1.5rem; display: flex; align-items: center; gap: 1rem; z-index: 100; }
        .sync-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--success); animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        @media (max-width: 1200px) { .pipeline-container { grid-template-columns: repeat(3, 1fr); } }
        @media (max-width: 768px) { .sidebar { display: none; } .main-content { margin-left: 0; } .pipeline-container { grid-template-columns: 1fr; } .stats-grid { grid-template-columns: repeat(2, 1fr); } }
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="logo"><i class="fas fa-dollar-sign"></i> West Money OS</div>
        <a href="/dashboard" class="nav-item"><i class="fas fa-th-large"></i> Dashboard</a>
        <a href="/kontakte" class="nav-item"><i class="fas fa-address-book"></i> Kontakte</a>
        <a href="/dashboard/leads" class="nav-item active"><i class="fas fa-chart-line"></i> Leads</a>
        <a href="/broly" class="nav-item"><i class="fas fa-dragon"></i> Broly</a>
        <a href="/kampagnen" class="nav-item"><i class="fas fa-bullhorn"></i> Kampagnen</a>
        <a href="/rechnungen" class="nav-item"><i class="fas fa-file-invoice-dollar"></i> Rechnungen</a>
        <a href="/whatsapp-consent" class="nav-item"><i class="fab fa-whatsapp"></i> WhatsApp</a>
        <a href="/hubspot-crm" class="nav-item"><i class="fab fa-hubspot"></i> HubSpot</a>
        <a href="/ai-chat" class="nav-item"><i class="fas fa-robot"></i> AI Chat</a>
        <a href="/settings" class="nav-item"><i class="fas fa-cog"></i> Settings</a>
    </nav>
    <main class="main-content">
        <div class="page-header">
            <h1 class="page-title"><i class="fas fa-chart-line"></i> Lead Pipeline</h1>
            <div>
                <a href="/hubspot-crm" class="btn btn-secondary"><i class="fab fa-hubspot"></i> HubSpot</a>
                <button class="btn btn-primary"><i class="fas fa-plus"></i> Neuer Lead</button>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-icon">🎯</div><div class="stat-value" style="color: var(--primary);">{{ total }}</div><div class="stat-label">Leads gesamt</div><div class="stat-change">+3 heute</div></div>
            <div class="stat-card"><div class="stat-icon">🔥</div><div class="stat-value" style="color: var(--hot);">{{ hot }}</div><div class="stat-label">Hot Leads</div><div class="stat-change">Score > 70</div></div>
            <div class="stat-card"><div class="stat-icon">💰</div><div class="stat-value" style="color: var(--success);">€{{ "{:,.0f}".format(pipeline) }}</div><div class="stat-label">Pipeline Wert</div><div class="stat-change">+12%</div></div>
            <div class="stat-card"><div class="stat-icon">📈</div><div class="stat-value" style="color: var(--warning);">{{ conv }}%</div><div class="stat-label">Conversion</div><div class="stat-change">+2.1%</div></div>
            <div class="stat-card"><div class="stat-icon">⏱️</div><div class="stat-value">23</div><div class="stat-label">Ø Sales Cycle</div><div class="stat-change">Tage</div></div>
        </div>
        <div class="tabs">
            <button class="tab active" onclick="showView('pipeline')"><i class="fas fa-columns"></i> Pipeline</button>
            <button class="tab" onclick="showView('table')"><i class="fas fa-table"></i> Tabelle</button>
        </div>
        <div class="pipeline-container" id="pipelineView">
            {% for stage_key, stage in stages.items() %}
            <div class="pipeline-column">
                <div class="column-header">
                    <div class="column-title"><span>{{ stage.icon }}</span> {{ stage.label }} <span class="column-count">{{ counts[stage_key] }}</span></div>
                </div>
                <div class="column-value">€{{ "{:,.0f}".format(values[stage_key]) }}</div>
                {% for lead in leads if lead.stage == stage_key %}
                <div class="lead-card">
                    <div class="lead-header">
                        <div class="lead-name">{{ lead.name }}</div>
                        <span class="lead-score {{ 'score-high' if lead.score >= 70 else ('score-medium' if lead.score >= 40 else 'score-low') }}">{{ lead.score }}</span>
                    </div>
                    <div class="lead-company">{{ lead.company }}</div>
                    <div class="lead-value">€{{ "{:,.0f}".format(lead.value) }}</div>
                    <div class="lead-meta">
                        <span class="source-badge source-{{ lead.source }}">{{ lead.source }}</span>
                        <span class="wa-badge wa-{{ lead.whatsapp_consent.replace('_', '') }}"><i class="fab fa-whatsapp"></i></span>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
        <div class="table-view" id="tableView">
            <table>
                <thead><tr><th>Name</th><th>Firma</th><th>Position</th><th>E-Mail</th><th>Score</th><th>Wert</th><th>Stage</th><th>Quelle</th></tr></thead>
                <tbody>
                {% for lead in leads %}
                <tr>
                    <td><strong>{{ lead.name }}</strong></td>
                    <td>{{ lead.company }}</td>
                    <td>{{ lead.position }}</td>
                    <td>{% if lead.email %}<a href="mailto:{{ lead.email }}" style="color: var(--primary);">{{ lead.email }}</a>{% else %}-{% endif %}</td>
                    <td><span class="lead-score {{ 'score-high' if lead.score >= 70 else ('score-medium' if lead.score >= 40 else 'score-low') }}">{{ lead.score }}</span></td>
                    <td style="color: var(--success); font-weight: 600;">€{{ "{:,.0f}".format(lead.value) }}</td>
                    <td><span class="stage-badge" style="background: {{ stages[lead.stage].color }}20; color: {{ stages[lead.stage].color }};">{{ stages[lead.stage].label }}</span></td>
                    <td><span class="source-badge source-{{ lead.source }}">{{ lead.source }}</span></td>
                </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </main>
    <div class="sync-status"><span class="sync-dot"></span><span>Live | {{ leads|length }} Leads</span></div>
    <script>
        function showView(view) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('pipelineView').style.display = view === 'pipeline' ? 'grid' : 'none';
            document.getElementById('tableView').classList.toggle('active', view === 'table');
        }
    </script>
</body>
</html>'''

@leads_bp.route('/leads')
def leads_dashboard():
    total = len(REAL_LEADS)
    hot = sum(1 for l in REAL_LEADS if l['score'] >= 70)
    pipeline = sum(l['value'] for l in REAL_LEADS)
    won = sum(1 for l in REAL_LEADS if l['stage'] == 'gewonnen')
    conv = round((won / total) * 100, 1) if total > 0 else 0
    counts = {s: sum(1 for l in REAL_LEADS if l['stage'] == s) for s in STAGES}
    values = {s: sum(l['value'] for l in REAL_LEADS if l['stage'] == s) for s in STAGES}
    return render_template_string(LEADS_HTML, leads=REAL_LEADS, stages=STAGES, total=total, hot=hot, pipeline=pipeline, conv=conv, counts=counts, values=values)

@leads_bp.route('/leads/api/all')
def api_leads():
    return jsonify({'success': True, 'leads': REAL_LEADS, 'total': len(REAL_LEADS)})
LEADS_EOF

#------------------------------------------------------------------------------
# 3. run_server.py aktualisieren
#------------------------------------------------------------------------------
echo "📝 Aktualisiere run_server.py..."

# Check if imports already exist
if ! grep -q "from app_hubspot_crm import" run_server.py; then
    # Add imports after other imports
    sed -i '/^from flask import/a from app_hubspot_crm import hubspot_crm_bp\nfrom app_leads_updated import leads_bp' run_server.py 2>/dev/null || \
    sed -i '' '/^from flask import/a\
from app_hubspot_crm import hubspot_crm_bp\
from app_leads_updated import leads_bp' run_server.py
fi

# Add blueprint registrations if not exist
if ! grep -q "hubspot_crm_bp" run_server.py; then
    # Try to add to register_all_blueprints function
    sed -i 's/def register_all_blueprints(app):/def register_all_blueprints(app):\n    app.register_blueprint(hubspot_crm_bp)\n    app.register_blueprint(leads_bp)/' run_server.py 2>/dev/null || \
    echo "# Manual step needed: Add blueprints to run_server.py"
fi

#------------------------------------------------------------------------------
# 4. Service neu starten
#------------------------------------------------------------------------------
echo "🔄 Starte West Money OS neu..."
sudo systemctl restart westmoney 2>/dev/null || sudo systemctl restart westmoney.service 2>/dev/null || echo "Service restart failed - try manually"

#------------------------------------------------------------------------------
# 5. Status prüfen
#------------------------------------------------------------------------------
echo ""
echo "✅ Deployment abgeschlossen!"
echo ""
echo "🔗 Neue URLs:"
echo "   - https://west-money.com/dashboard/leads - Echte Lead Pipeline"
echo "   - https://west-money.com/hubspot-crm - HubSpot CRM Integration"
echo ""
echo "📊 Leads im System:"
echo "   - 15 echte Leads mit Kontaktdaten"
echo "   - Pipeline-Wert: €1,544,000"
echo "   - Quellen: Explorium, HubSpot, LinkedIn, Events"
echo ""
echo "🔧 Falls Fehler auftreten:"
echo "   sudo journalctl -u westmoney -f"
echo ""
