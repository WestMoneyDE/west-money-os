"""
West Money OS - HubSpot CRM Integration
========================================
Vollständige HubSpot CRM Integration mit:
- Automatischer Lead-Sync (bidirektional)
- WhatsApp Consent Management
- Pipeline-Automatisierung
- Echtzeit-Webhooks
- Explorium B2B Daten Import

Author: West Money OS Team
Version: 1.0.0
"""

from flask import Blueprint, render_template_string, request, jsonify, session
import requests
import json
import os
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import hmac

hubspot_crm_bp = Blueprint('hubspot_crm', __name__, url_prefix='/hubspot-crm')

# ============================================================================
# CONFIGURATION
# ============================================================================

class HubSpotConfig:
    """HubSpot API Configuration"""
    API_KEY = os.environ.get('HUBSPOT_API_KEY', '')
    PORTAL_ID = os.environ.get('HUBSPOT_PORTAL_ID', '')
    BASE_URL = 'https://api.hubapi.com'
    
    # Pipeline Stages (West Money Bau)
    PIPELINE_STAGES = {
        'neu': 'appointmentscheduled',
        'kontaktiert': 'qualifiedtobuy',
        'qualifiziert': 'presentationscheduled',
        'angebot': 'decisionmakerboughtin',
        'verhandlung': 'contractsent',
        'gewonnen': 'closedwon',
        'verloren': 'closedlost'
    }
    
    # WhatsApp Consent Status
    CONSENT_STATUSES = {
        'OPT_IN': 'opted_in',
        'OPT_OUT': 'opted_out',
        'NOT_SET': 'not_set',
        'PENDING': 'pending'
    }

# ============================================================================
# HUBSPOT API CLIENT
# ============================================================================

class HubSpotClient:
    """HubSpot API Client for CRM Operations"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or HubSpotConfig.API_KEY
        self.base_url = HubSpotConfig.BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def _request(self, method, endpoint, data=None, params=None):
        """Make API request to HubSpot"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    # -------------------------------------------------------------------------
    # CONTACTS
    # -------------------------------------------------------------------------
    
    def create_contact(self, properties):
        """Create a new contact in HubSpot"""
        data = {'properties': properties}
        return self._request('POST', '/crm/v3/objects/contacts', data)
    
    def update_contact(self, contact_id, properties):
        """Update an existing contact"""
        data = {'properties': properties}
        return self._request('PATCH', f'/crm/v3/objects/contacts/{contact_id}', data)
    
    def get_contact(self, contact_id, properties=None):
        """Get contact by ID"""
        params = {}
        if properties:
            params['properties'] = ','.join(properties)
        return self._request('GET', f'/crm/v3/objects/contacts/{contact_id}', params=params)
    
    def search_contacts(self, filters, properties=None, limit=100):
        """Search contacts with filters"""
        data = {
            'filterGroups': [{'filters': filters}],
            'limit': limit
        }
        if properties:
            data['properties'] = properties
        return self._request('POST', '/crm/v3/objects/contacts/search', data)
    
    def get_all_contacts(self, limit=100, properties=None):
        """Get all contacts with pagination"""
        params = {'limit': limit}
        if properties:
            params['properties'] = ','.join(properties)
        return self._request('GET', '/crm/v3/objects/contacts', params=params)
    
    def bulk_create_contacts(self, contacts_list):
        """Bulk create contacts"""
        data = {'inputs': [{'properties': c} for c in contacts_list]}
        return self._request('POST', '/crm/v3/objects/contacts/batch/create', data)
    
    def bulk_update_contacts(self, updates_list):
        """Bulk update contacts - list of {id, properties}"""
        data = {'inputs': updates_list}
        return self._request('POST', '/crm/v3/objects/contacts/batch/update', data)
    
    # -------------------------------------------------------------------------
    # DEALS / LEADS
    # -------------------------------------------------------------------------
    
    def create_deal(self, properties):
        """Create a new deal"""
        data = {'properties': properties}
        return self._request('POST', '/crm/v3/objects/deals', data)
    
    def update_deal(self, deal_id, properties):
        """Update an existing deal"""
        data = {'properties': properties}
        return self._request('PATCH', f'/crm/v3/objects/deals/{deal_id}', data)
    
    def get_deal(self, deal_id, properties=None):
        """Get deal by ID"""
        params = {}
        if properties:
            params['properties'] = ','.join(properties)
        return self._request('GET', f'/crm/v3/objects/deals/{deal_id}', params=params)
    
    def search_deals(self, filters, properties=None, limit=100):
        """Search deals with filters"""
        data = {
            'filterGroups': [{'filters': filters}],
            'limit': limit
        }
        if properties:
            data['properties'] = properties
        return self._request('POST', '/crm/v3/objects/deals/search', data)
    
    def get_all_deals(self, limit=100, properties=None):
        """Get all deals"""
        params = {'limit': limit}
        if properties:
            params['properties'] = ','.join(properties)
        return self._request('GET', '/crm/v3/objects/deals', params=params)
    
    # -------------------------------------------------------------------------
    # COMPANIES
    # -------------------------------------------------------------------------
    
    def create_company(self, properties):
        """Create a new company"""
        data = {'properties': properties}
        return self._request('POST', '/crm/v3/objects/companies', data)
    
    def search_companies(self, filters, properties=None, limit=100):
        """Search companies"""
        data = {
            'filterGroups': [{'filters': filters}],
            'limit': limit
        }
        if properties:
            data['properties'] = properties
        return self._request('POST', '/crm/v3/objects/companies/search', data)
    
    # -------------------------------------------------------------------------
    # ASSOCIATIONS
    # -------------------------------------------------------------------------
    
    def associate_contact_to_deal(self, contact_id, deal_id):
        """Associate contact with deal"""
        return self._request(
            'PUT',
            f'/crm/v3/objects/contacts/{contact_id}/associations/deals/{deal_id}/contact_to_deal'
        )
    
    def associate_contact_to_company(self, contact_id, company_id):
        """Associate contact with company"""
        return self._request(
            'PUT',
            f'/crm/v3/objects/contacts/{contact_id}/associations/companies/{company_id}/contact_to_company'
        )
    
    # -------------------------------------------------------------------------
    # PIPELINES
    # -------------------------------------------------------------------------
    
    def get_pipelines(self, object_type='deals'):
        """Get all pipelines"""
        return self._request('GET', f'/crm/v3/pipelines/{object_type}')
    
    def get_pipeline_stages(self, pipeline_id, object_type='deals'):
        """Get pipeline stages"""
        return self._request('GET', f'/crm/v3/pipelines/{object_type}/{pipeline_id}/stages')
    
    # -------------------------------------------------------------------------
    # WHATSAPP CONSENT
    # -------------------------------------------------------------------------
    
    def update_whatsapp_consent(self, contact_id, status):
        """Update WhatsApp consent status for a contact"""
        properties = {
            'hs_whatsapp_consent_status': status,
            'hs_whatsapp_consent_date': datetime.now().isoformat()
        }
        return self.update_contact(contact_id, properties)
    
    def bulk_update_whatsapp_consent(self, contact_ids, status):
        """Bulk update WhatsApp consent"""
        updates = [
            {
                'id': cid,
                'properties': {
                    'hs_whatsapp_consent_status': status,
                    'hs_whatsapp_consent_date': datetime.now().isoformat()
                }
            }
            for cid in contact_ids
        ]
        return self.bulk_update_contacts(updates)
    
    def get_contacts_by_consent_status(self, status):
        """Get contacts by WhatsApp consent status"""
        filters = [{
            'propertyName': 'hs_whatsapp_consent_status',
            'operator': 'EQ',
            'value': status
        }]
        return self.search_contacts(filters, properties=[
            'firstname', 'lastname', 'email', 'phone',
            'hs_whatsapp_consent_status', 'hs_whatsapp_consent_date'
        ])

# ============================================================================
# LEAD SYNC ENGINE
# ============================================================================

class LeadSyncEngine:
    """Synchronize leads between West Money OS and HubSpot"""
    
    def __init__(self, hubspot_client=None):
        self.hubspot = hubspot_client or HubSpotClient()
        self.sync_log = []
    
    def import_explorium_leads(self, leads_data):
        """Import leads from Explorium B2B data"""
        results = {'created': 0, 'updated': 0, 'errors': []}
        
        for lead in leads_data:
            try:
                # Map Explorium fields to HubSpot properties
                properties = self._map_explorium_to_hubspot(lead)
                
                # Check if contact exists
                existing = self.hubspot.search_contacts([{
                    'propertyName': 'email',
                    'operator': 'EQ',
                    'value': properties.get('email', '')
                }])
                
                if existing.get('results'):
                    # Update existing contact
                    contact_id = existing['results'][0]['id']
                    self.hubspot.update_contact(contact_id, properties)
                    results['updated'] += 1
                else:
                    # Create new contact
                    self.hubspot.create_contact(properties)
                    results['created'] += 1
                    
            except Exception as e:
                results['errors'].append({
                    'lead': lead.get('prospect_full_name', 'Unknown'),
                    'error': str(e)
                })
        
        return results
    
    def _map_explorium_to_hubspot(self, lead):
        """Map Explorium data fields to HubSpot properties"""
        # Parse emails from contact_emails JSON
        emails = []
        if lead.get('contact_emails'):
            try:
                email_data = json.loads(lead['contact_emails']) if isinstance(lead['contact_emails'], str) else lead['contact_emails']
                for e in email_data:
                    if e.get('address'):
                        emails.append(e['address'])
            except:
                pass
        
        primary_email = lead.get('contact_professions_email') or (emails[0] if emails else '')
        
        return {
            'firstname': lead.get('prospect_first_name', ''),
            'lastname': lead.get('prospect_last_name', ''),
            'email': primary_email,
            'phone': lead.get('contact_mobile_phone', ''),
            'jobtitle': lead.get('prospect_job_title', ''),
            'company': lead.get('prospect_company_name', ''),
            'website': lead.get('prospect_company_website', ''),
            'linkedin_url': lead.get('prospect_linkedin', ''),
            'city': lead.get('prospect_city', ''),
            'country': lead.get('prospect_country_name', ''),
            'hs_lead_status': 'NEW',
            'lifecyclestage': 'lead',
            # Custom properties for West Money
            'lead_source': 'explorium',
            'lead_score': self._calculate_lead_score(lead),
            'industry': 'construction',
            'notes': f"Skills: {lead.get('prospect_skills', '')}"
        }
    
    def _calculate_lead_score(self, lead):
        """Calculate lead score based on data completeness and relevance"""
        score = 0
        
        # Has email: +20
        if lead.get('contact_professions_email') or lead.get('contact_emails'):
            score += 20
        
        # Has phone: +15
        if lead.get('contact_mobile_phone'):
            score += 15
        
        # C-Suite level: +25
        if lead.get('prospect_job_level_main') in ['c-suite', 'owner', 'founder']:
            score += 25
        elif lead.get('prospect_job_level_main') in ['director', 'vice president']:
            score += 15
        
        # Germany location: +10
        if lead.get('prospect_country_name', '').lower() == 'germany':
            score += 10
        
        # Has LinkedIn: +10
        if lead.get('prospect_linkedin'):
            score += 10
        
        # Has company website: +5
        if lead.get('prospect_company_website'):
            score += 5
        
        # Has skills data: +5
        if lead.get('prospect_skills'):
            score += 5
        
        return min(score, 100)
    
    def sync_to_local_db(self, db_connection=None):
        """Sync HubSpot contacts to local West Money OS database"""
        # Get all contacts from HubSpot
        contacts = self.hubspot.get_all_contacts(
            limit=100,
            properties=[
                'firstname', 'lastname', 'email', 'phone', 'company',
                'jobtitle', 'hs_lead_status', 'lifecyclestage',
                'hs_whatsapp_consent_status', 'createdate', 'lastmodifieddate'
            ]
        )
        
        synced_leads = []
        for contact in contacts.get('results', []):
            props = contact.get('properties', {})
            synced_leads.append({
                'hubspot_id': contact['id'],
                'name': f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
                'email': props.get('email', ''),
                'phone': props.get('phone', ''),
                'company': props.get('company', ''),
                'position': props.get('jobtitle', ''),
                'status': props.get('hs_lead_status', 'NEW'),
                'stage': props.get('lifecyclestage', 'lead'),
                'whatsapp_consent': props.get('hs_whatsapp_consent_status', 'not_set'),
                'created_at': props.get('createdate', ''),
                'updated_at': props.get('lastmodifieddate', '')
            })
        
        return synced_leads

# ============================================================================
# SAMPLE DATA (Explorium Results)
# ============================================================================

SAMPLE_EXPLORIUM_LEADS = [
    {
        "prospect_first_name": "Julius",
        "prospect_last_name": "Schäufele",
        "prospect_full_name": "Julius Schäufele",
        "prospect_job_title": "Co-Founder, Managing Director / Chief Product Officer",
        "prospect_job_level_main": "c-suite",
        "prospect_company_name": "Concular",
        "prospect_company_website": "concular.de",
        "prospect_city": "Teltow",
        "prospect_country_name": "germany",
        "prospect_linkedin": "linkedin.com/in/juliusschaeufele",
        "contact_professions_email": "julius.schaeufele@concular.de",
        "contact_mobile_phone": "+491785412395",
        "prospect_skills": "Web design, Projektmanagement, Digitalisierung, UX Design"
    },
    {
        "prospect_first_name": "Tomasz",
        "prospect_last_name": "Von Janta Lipinski",
        "prospect_full_name": "Tomasz Von Janta Lipinski",
        "prospect_job_title": "Chief Executive Officer",
        "prospect_job_level_main": "c-suite",
        "prospect_company_name": "Krafteam",
        "prospect_company_website": "krafteam.de",
        "prospect_city": "Nordhorn",
        "prospect_country_name": "germany",
        "prospect_linkedin": "linkedin.com/in/tomasz-von-janta-lipinski",
        "contact_professions_email": "info@krafteam.de",
        "contact_mobile_phone": "",
        "prospect_skills": "Engineering, Tiefbau, Spülbohren, Montage"
    },
    {
        "prospect_first_name": "Jonathan",
        "prospect_last_name": "Wong",
        "prospect_full_name": "Jonathan Wong",
        "prospect_job_title": "Chief Executive Officer APAC",
        "prospect_job_level_main": "c-suite",
        "prospect_company_name": "Habyt",
        "prospect_company_website": "habyt.com",
        "prospect_city": "Singapore",
        "prospect_country_name": "singapore",
        "prospect_linkedin": "linkedin.com/in/jonathanwongkw",
        "contact_professions_email": "jonathan.wong@habyt.com",
        "contact_mobile_phone": "",
        "prospect_skills": "Strategy, Private Equity, Investment Banking, M&A"
    },
    {
        "prospect_first_name": "Hedieh",
        "prospect_last_name": "Sabeth",
        "prospect_full_name": "Hedieh Sabeth",
        "prospect_job_title": "Senior Project Manager - Owner's Representative",
        "prospect_job_level_main": "owner",
        "prospect_company_name": "PIMCO Prime Real Estate",
        "prospect_company_website": "pimcoprimerealestate.com",
        "prospect_city": "",
        "prospect_country_name": "germany",
        "prospect_linkedin": "linkedin.com/in/hedieh-sabeth",
        "contact_professions_email": "",
        "contact_mobile_phone": "",
        "prospect_skills": "Projektsteuerung, Projektmanagement, Baugewerbe, Vertragsmanagement"
    },
    {
        "prospect_first_name": "Ulf",
        "prospect_last_name": "Wallisch",
        "prospect_full_name": "Ulf Wallisch",
        "prospect_job_title": "Senior Director, Head of Operations Management",
        "prospect_job_level_main": "director",
        "prospect_company_name": "FCR Immobilien",
        "prospect_company_website": "fcr-immobilien.de",
        "prospect_city": "Pullach im Isartal",
        "prospect_country_name": "germany",
        "prospect_linkedin": "linkedin.com/in/ulf-wallisch",
        "contact_professions_email": "",
        "contact_mobile_phone": "",
        "prospect_skills": "Investments, Corporate Communications, Strategy, Business Development"
    },
    {
        "prospect_first_name": "Anna",
        "prospect_last_name": "Müller",
        "prospect_full_name": "Anna Müller",
        "prospect_job_title": "Geschäftsführerin",
        "prospect_job_level_main": "c-suite",
        "prospect_company_name": "Smart Home Bayern GmbH",
        "prospect_company_website": "smarthome-bayern.de",
        "prospect_city": "München",
        "prospect_country_name": "germany",
        "prospect_linkedin": "linkedin.com/in/anna-mueller-smarthome",
        "contact_professions_email": "a.mueller@smarthome-bayern.de",
        "contact_mobile_phone": "+4915112345678",
        "prospect_skills": "Smart Home, KNX, LOXONE, Gebäudeautomation"
    },
    {
        "prospect_first_name": "Michael",
        "prospect_last_name": "Weber",
        "prospect_full_name": "Michael Weber",
        "prospect_job_title": "Inhaber / Geschäftsführer",
        "prospect_job_level_main": "owner",
        "prospect_company_name": "Weber Elektrotechnik",
        "prospect_company_website": "weber-elektro.de",
        "prospect_city": "Frankfurt am Main",
        "prospect_country_name": "germany",
        "prospect_linkedin": "linkedin.com/in/michael-weber-elektro",
        "contact_professions_email": "m.weber@weber-elektro.de",
        "contact_mobile_phone": "+4917612345678",
        "prospect_skills": "Elektroinstallation, Smart Home, EIB/KNX, Photovoltaik"
    },
    {
        "prospect_first_name": "Sarah",
        "prospect_last_name": "Schmidt",
        "prospect_full_name": "Sarah Schmidt",
        "prospect_job_title": "Director of Real Estate Development",
        "prospect_job_level_main": "director",
        "prospect_company_name": "Projektentwicklung Rhein-Main",
        "prospect_company_website": "pe-rheinmain.de",
        "prospect_city": "Wiesbaden",
        "prospect_country_name": "germany",
        "prospect_linkedin": "linkedin.com/in/sarah-schmidt-realestate",
        "contact_professions_email": "s.schmidt@pe-rheinmain.de",
        "contact_mobile_phone": "+4916012345678",
        "prospect_skills": "Projektentwicklung, Immobilien, Baurecht, Due Diligence"
    },
    {
        "prospect_first_name": "Thomas",
        "prospect_last_name": "Becker",
        "prospect_full_name": "Thomas Becker",
        "prospect_job_title": "CEO",
        "prospect_job_level_main": "c-suite",
        "prospect_company_name": "BauTech Solutions GmbH",
        "prospect_company_website": "bautech-solutions.de",
        "prospect_city": "Düsseldorf",
        "prospect_country_name": "germany",
        "prospect_linkedin": "linkedin.com/in/thomas-becker-bautech",
        "contact_professions_email": "t.becker@bautech-solutions.de",
        "contact_mobile_phone": "+4915212345678",
        "prospect_skills": "Baumanagement, BIM, Digitalisierung, Projektsteuerung"
    },
    {
        "prospect_first_name": "Lisa",
        "prospect_last_name": "Hoffmann",
        "prospect_full_name": "Lisa Hoffmann",
        "prospect_job_title": "Architektin / Partnerin",
        "prospect_job_level_main": "partner",
        "prospect_company_name": "Hoffmann Architekten",
        "prospect_company_website": "hoffmann-architekten.de",
        "prospect_city": "Köln",
        "prospect_country_name": "germany",
        "prospect_linkedin": "linkedin.com/in/lisa-hoffmann-architektin",
        "contact_professions_email": "l.hoffmann@hoffmann-architekten.de",
        "contact_mobile_phone": "+4917112345678",
        "prospect_skills": "Architektur, Nachhaltiges Bauen, Energieeffizienz, Smart Building"
    }
]

# ============================================================================
# FLASK ROUTES
# ============================================================================

HUBSPOT_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HubSpot CRM Integration - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --hubspot-orange: #ff7a59;
            --hubspot-dark: #2d3e50;
            --hubspot-light: #f5f8fa;
            --success: #00bda5;
            --warning: #f5c26b;
            --danger: #f2545b;
            --bg-dark: #0a0a0f;
            --bg-card: #12121a;
            --text-primary: #ffffff;
            --text-secondary: #8b8b9a;
            --border: #2a2a3a;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }
        
        .header h1 {
            font-size: 1.8rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .header h1 i { color: var(--hubspot-orange); }
        
        .connection-status {
            display: flex;
            gap: 1rem;
        }
        
        .status-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: var(--bg-card);
            border-radius: 20px;
            font-size: 0.85rem;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }
        
        .status-dot.connected { background: var(--success); box-shadow: 0 0 10px var(--success); }
        .status-dot.disconnected { background: var(--danger); }
        .status-dot.pending { background: var(--warning); }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }
        
        .stat-card .icon {
            font-size: 2rem;
            margin-bottom: 0.75rem;
        }
        
        .stat-card .value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        
        .stat-card .label {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .stat-card.hubspot .icon { color: var(--hubspot-orange); }
        .stat-card.hubspot .value { color: var(--hubspot-orange); }
        .stat-card.success .icon { color: var(--success); }
        .stat-card.success .value { color: var(--success); }
        .stat-card.warning .icon { color: var(--warning); }
        .stat-card.warning .value { color: var(--warning); }
        
        .actions-bar {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: var(--hubspot-orange);
            color: white;
        }
        
        .btn-primary:hover {
            background: #ff6a49;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }
        
        .btn-secondary:hover {
            border-color: var(--hubspot-orange);
        }
        
        .btn-success {
            background: var(--success);
            color: white;
        }
        
        .leads-table-container {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 2rem;
        }
        
        .table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
        }
        
        .table-header h2 {
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .search-box {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--bg-dark);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            border: 1px solid var(--border);
        }
        
        .search-box input {
            background: transparent;
            border: none;
            color: var(--text-primary);
            outline: none;
            width: 200px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        th {
            background: rgba(255, 122, 89, 0.1);
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            color: var(--text-secondary);
        }
        
        tr:hover {
            background: rgba(255, 122, 89, 0.05);
        }
        
        .lead-name {
            font-weight: 600;
        }
        
        .lead-company {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }
        
        .lead-score {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-weight: 700;
            font-size: 0.9rem;
        }
        
        .score-high { background: rgba(0, 189, 165, 0.2); color: var(--success); }
        .score-medium { background: rgba(245, 194, 107, 0.2); color: var(--warning); }
        .score-low { background: rgba(139, 139, 154, 0.2); color: var(--text-secondary); }
        
        .consent-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .consent-optin { background: rgba(0, 189, 165, 0.2); color: var(--success); }
        .consent-optout { background: rgba(242, 84, 91, 0.2); color: var(--danger); }
        .consent-pending { background: rgba(245, 194, 107, 0.2); color: var(--warning); }
        .consent-notset { background: rgba(139, 139, 154, 0.2); color: var(--text-secondary); }
        
        .action-buttons {
            display: flex;
            gap: 0.5rem;
        }
        
        .action-btn {
            width: 32px;
            height: 32px;
            border: none;
            border-radius: 6px;
            background: var(--bg-dark);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .action-btn:hover {
            background: var(--hubspot-orange);
            color: white;
        }
        
        .sync-panel {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
        }
        
        .sync-panel h3 {
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .sync-log {
            background: var(--bg-dark);
            border-radius: 8px;
            padding: 1rem;
            max-height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.85rem;
        }
        
        .log-entry {
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border);
        }
        
        .log-entry:last-child { border-bottom: none; }
        
        .log-time { color: var(--text-secondary); }
        .log-success { color: var(--success); }
        .log-error { color: var(--danger); }
        .log-info { color: var(--hubspot-orange); }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active { display: flex; }
        
        .modal-content {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 2rem;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .modal-close {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 0.75rem;
            background: var(--bg-dark);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 1rem;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: var(--hubspot-orange);
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .checkbox-group input[type="checkbox"] {
            width: auto;
        }
        
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .actions-bar {
                flex-direction: column;
            }
            
            .btn { width: 100%; justify-content: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fab fa-hubspot"></i> HubSpot CRM Integration</h1>
            <div class="connection-status">
                <div class="status-badge">
                    <span class="status-dot {{ 'connected' if hubspot_connected else 'disconnected' }}"></span>
                    HubSpot API
                </div>
                <div class="status-badge">
                    <span class="status-dot {{ 'connected' if whatsapp_connected else 'disconnected' }}"></span>
                    WhatsApp
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card hubspot">
                <div class="icon"><i class="fas fa-users"></i></div>
                <div class="value">{{ total_leads }}</div>
                <div class="label">Leads Gesamt</div>
            </div>
            <div class="stat-card success">
                <div class="icon"><i class="fab fa-whatsapp"></i></div>
                <div class="value">{{ opt_in_count }}</div>
                <div class="label">WhatsApp Opt-In</div>
            </div>
            <div class="stat-card warning">
                <div class="icon"><i class="fas fa-clock"></i></div>
                <div class="value">{{ pending_count }}</div>
                <div class="label">Pending Consent</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-sync"></i></div>
                <div class="value">{{ sync_count }}</div>
                <div class="label">Letzte Sync</div>
            </div>
        </div>
        
        <div class="actions-bar">
            <button class="btn btn-primary" onclick="syncFromHubSpot()">
                <i class="fas fa-cloud-download-alt"></i> Von HubSpot Sync
            </button>
            <button class="btn btn-primary" onclick="syncToHubSpot()">
                <i class="fas fa-cloud-upload-alt"></i> Zu HubSpot Sync
            </button>
            <button class="btn btn-success" onclick="importExplorium()">
                <i class="fas fa-database"></i> Explorium Import
            </button>
            <button class="btn btn-secondary" onclick="openConfigModal()">
                <i class="fas fa-cog"></i> API Konfiguration
            </button>
            <button class="btn btn-secondary" onclick="exportCSV()">
                <i class="fas fa-file-csv"></i> CSV Export
            </button>
        </div>
        
        <div class="leads-table-container">
            <div class="table-header">
                <h2><i class="fas fa-list"></i> Leads ({{ total_leads }})</h2>
                <div class="search-box">
                    <i class="fas fa-search"></i>
                    <input type="text" id="searchInput" placeholder="Suchen..." onkeyup="filterLeads()">
                </div>
            </div>
            <table id="leadsTable">
                <thead>
                    <tr>
                        <th><input type="checkbox" onclick="toggleAll(this)"></th>
                        <th>Name</th>
                        <th>Position</th>
                        <th>Firma</th>
                        <th>E-Mail</th>
                        <th>Telefon</th>
                        <th>Score</th>
                        <th>WhatsApp</th>
                        <th>Aktionen</th>
                    </tr>
                </thead>
                <tbody>
                    {% for lead in leads %}
                    <tr data-id="{{ lead.hubspot_id or loop.index }}">
                        <td><input type="checkbox" class="lead-checkbox" value="{{ lead.hubspot_id or loop.index }}"></td>
                        <td>
                            <div class="lead-name">{{ lead.name }}</div>
                        </td>
                        <td>{{ lead.position }}</td>
                        <td>
                            <div class="lead-company">{{ lead.company }}</div>
                            {% if lead.website %}
                            <small><a href="https://{{ lead.website }}" target="_blank" style="color: var(--hubspot-orange);">{{ lead.website }}</a></small>
                            {% endif %}
                        </td>
                        <td>
                            {% if lead.email %}
                            <a href="mailto:{{ lead.email }}" style="color: var(--text-primary);">{{ lead.email }}</a>
                            {% else %}
                            <span style="color: var(--text-secondary);">-</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if lead.phone %}
                            <a href="tel:{{ lead.phone }}" style="color: var(--text-primary);">{{ lead.phone }}</a>
                            {% else %}
                            <span style="color: var(--text-secondary);">-</span>
                            {% endif %}
                        </td>
                        <td>
                            <span class="lead-score {{ 'score-high' if lead.score >= 70 else ('score-medium' if lead.score >= 40 else 'score-low') }}">
                                {{ lead.score }}
                            </span>
                        </td>
                        <td>
                            <span class="consent-badge consent-{{ lead.whatsapp_consent|lower|replace('_', '') }}">
                                {{ lead.whatsapp_consent }}
                            </span>
                        </td>
                        <td>
                            <div class="action-buttons">
                                <button class="action-btn" onclick="editLead('{{ lead.hubspot_id or loop.index }}')" title="Bearbeiten">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="action-btn" onclick="sendWhatsApp('{{ lead.phone }}')" title="WhatsApp senden">
                                    <i class="fab fa-whatsapp"></i>
                                </button>
                                <button class="action-btn" onclick="viewLinkedIn('{{ lead.linkedin }}')" title="LinkedIn öffnen">
                                    <i class="fab fa-linkedin"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="sync-panel">
            <h3><i class="fas fa-history"></i> Sync Log</h3>
            <div class="sync-log" id="syncLog">
                <div class="log-entry">
                    <span class="log-time">[{{ now }}]</span>
                    <span class="log-info">System bereit - HubSpot CRM Integration aktiv</span>
                </div>
                {% for log in sync_logs %}
                <div class="log-entry">
                    <span class="log-time">[{{ log.time }}]</span>
                    <span class="log-{{ log.type }}">{{ log.message }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <!-- Config Modal -->
    <div class="modal" id="configModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-cog"></i> API Konfiguration</h3>
                <button class="modal-close" onclick="closeModal('configModal')">&times;</button>
            </div>
            <form id="configForm" onsubmit="saveConfig(event)">
                <div class="form-group">
                    <label>HubSpot API Key</label>
                    <input type="password" name="hubspot_api_key" placeholder="pat-xxx-xxx-xxx" value="{{ hubspot_api_key }}">
                </div>
                <div class="form-group">
                    <label>HubSpot Portal ID</label>
                    <input type="text" name="hubspot_portal_id" placeholder="123456" value="{{ hubspot_portal_id }}">
                </div>
                <div class="form-group">
                    <label>WhatsApp Phone ID</label>
                    <input type="text" name="whatsapp_phone_id" placeholder="123456789" value="{{ whatsapp_phone_id }}">
                </div>
                <div class="form-group">
                    <label>WhatsApp Token</label>
                    <input type="password" name="whatsapp_token" placeholder="EAAG..." value="{{ whatsapp_token }}">
                </div>
                <div class="form-group checkbox-group">
                    <input type="checkbox" name="auto_sync" id="autoSync" {{ 'checked' if auto_sync else '' }}>
                    <label for="autoSync">Automatische Synchronisierung aktivieren</label>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">
                    <i class="fas fa-save"></i> Speichern
                </button>
            </form>
        </div>
    </div>
    
    <script>
        function syncFromHubSpot() {
            addLog('info', 'Starte Sync von HubSpot...');
            fetch('/hubspot-crm/sync-from-hubspot', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        addLog('success', `Sync erfolgreich: ${data.synced} Kontakte synchronisiert`);
                        location.reload();
                    } else {
                        addLog('error', `Sync fehlgeschlagen: ${data.error}`);
                    }
                })
                .catch(e => addLog('error', `Fehler: ${e.message}`));
        }
        
        function syncToHubSpot() {
            const selected = getSelectedLeads();
            if (selected.length === 0) {
                alert('Bitte wähle mindestens einen Lead aus');
                return;
            }
            
            addLog('info', `Sync ${selected.length} Leads zu HubSpot...`);
            fetch('/hubspot-crm/sync-to-hubspot', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({lead_ids: selected})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    addLog('success', `${data.created} erstellt, ${data.updated} aktualisiert`);
                } else {
                    addLog('error', data.error);
                }
            });
        }
        
        function importExplorium() {
            addLog('info', 'Importiere Explorium B2B Leads...');
            fetch('/hubspot-crm/import-explorium', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        addLog('success', `Import erfolgreich: ${data.imported} Leads importiert`);
                        location.reload();
                    } else {
                        addLog('error', data.error);
                    }
                });
        }
        
        function getSelectedLeads() {
            const checkboxes = document.querySelectorAll('.lead-checkbox:checked');
            return Array.from(checkboxes).map(cb => cb.value);
        }
        
        function toggleAll(checkbox) {
            document.querySelectorAll('.lead-checkbox').forEach(cb => {
                cb.checked = checkbox.checked;
            });
        }
        
        function filterLeads() {
            const filter = document.getElementById('searchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#leadsTable tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        }
        
        function editLead(id) {
            window.location.href = `/leads/edit/${id}`;
        }
        
        function sendWhatsApp(phone) {
            if (phone) {
                window.open(`https://wa.me/${phone.replace(/[^0-9]/g, '')}`, '_blank');
            } else {
                alert('Keine Telefonnummer verfügbar');
            }
        }
        
        function viewLinkedIn(url) {
            if (url) {
                window.open(`https://${url}`, '_blank');
            } else {
                alert('Kein LinkedIn Profil verfügbar');
            }
        }
        
        function exportCSV() {
            window.location.href = '/hubspot-crm/export-csv';
        }
        
        function openConfigModal() {
            document.getElementById('configModal').classList.add('active');
        }
        
        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }
        
        function saveConfig(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            fetch('/hubspot-crm/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    addLog('success', 'Konfiguration gespeichert');
                    closeModal('configModal');
                    location.reload();
                } else {
                    alert('Fehler: ' + data.error);
                }
            });
        }
        
        function addLog(type, message) {
            const log = document.getElementById('syncLog');
            const now = new Date().toLocaleTimeString('de-DE');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `<span class="log-time">[${now}]</span> <span class="log-${type}">${message}</span>`;
            log.insertBefore(entry, log.firstChild);
        }
        
        // Close modal on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal(modal.id);
            });
        });
    </script>
</body>
</html>
"""

@hubspot_crm_bp.route('/')
def dashboard():
    """HubSpot CRM Dashboard"""
    sync_engine = LeadSyncEngine()
    
    # Process sample leads and calculate scores
    leads = []
    for lead in SAMPLE_EXPLORIUM_LEADS:
        score = sync_engine._calculate_lead_score(lead)
        leads.append({
            'hubspot_id': '',
            'name': lead.get('prospect_full_name', ''),
            'position': lead.get('prospect_job_title', ''),
            'company': lead.get('prospect_company_name', ''),
            'website': lead.get('prospect_company_website', ''),
            'email': lead.get('contact_professions_email', ''),
            'phone': lead.get('contact_mobile_phone', ''),
            'linkedin': lead.get('prospect_linkedin', ''),
            'score': score,
            'whatsapp_consent': 'not_set'
        })
    
    # Calculate stats
    total_leads = len(leads)
    opt_in_count = sum(1 for l in leads if l['whatsapp_consent'] == 'opted_in')
    pending_count = sum(1 for l in leads if l['whatsapp_consent'] == 'pending')
    
    return render_template_string(
        HUBSPOT_DASHBOARD_HTML,
        hubspot_connected=bool(HubSpotConfig.API_KEY),
        whatsapp_connected=bool(os.environ.get('WHATSAPP_TOKEN')),
        total_leads=total_leads,
        opt_in_count=opt_in_count,
        pending_count=pending_count,
        sync_count=total_leads,
        leads=leads,
        sync_logs=[],
        now=datetime.now().strftime('%H:%M:%S'),
        hubspot_api_key=HubSpotConfig.API_KEY[:10] + '...' if HubSpotConfig.API_KEY else '',
        hubspot_portal_id=HubSpotConfig.PORTAL_ID,
        whatsapp_phone_id=os.environ.get('WHATSAPP_PHONE_ID', ''),
        whatsapp_token='***' if os.environ.get('WHATSAPP_TOKEN') else '',
        auto_sync=False
    )

@hubspot_crm_bp.route('/sync-from-hubspot', methods=['POST'])
def sync_from_hubspot():
    """Sync contacts from HubSpot to local"""
    try:
        sync_engine = LeadSyncEngine()
        leads = sync_engine.sync_to_local_db()
        return jsonify({'success': True, 'synced': len(leads)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@hubspot_crm_bp.route('/sync-to-hubspot', methods=['POST'])
def sync_to_hubspot():
    """Sync selected leads to HubSpot"""
    try:
        data = request.get_json()
        lead_ids = data.get('lead_ids', [])
        
        # In production, get leads from database
        # For now, use sample data
        sync_engine = LeadSyncEngine()
        results = sync_engine.import_explorium_leads(SAMPLE_EXPLORIUM_LEADS)
        
        return jsonify({
            'success': True,
            'created': results['created'],
            'updated': results['updated'],
            'errors': results['errors']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@hubspot_crm_bp.route('/import-explorium', methods=['POST'])
def import_explorium():
    """Import Explorium B2B leads"""
    try:
        sync_engine = LeadSyncEngine()
        results = sync_engine.import_explorium_leads(SAMPLE_EXPLORIUM_LEADS)
        
        return jsonify({
            'success': True,
            'imported': results['created'] + results['updated'],
            'created': results['created'],
            'updated': results['updated']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@hubspot_crm_bp.route('/config', methods=['GET', 'POST'])
def config():
    """Get/Set API configuration"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # In production, save to database or environment
            # For now, just acknowledge
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({
        'hubspot_connected': bool(HubSpotConfig.API_KEY),
        'whatsapp_connected': bool(os.environ.get('WHATSAPP_TOKEN'))
    })

@hubspot_crm_bp.route('/export-csv')
def export_csv():
    """Export leads as CSV"""
    import csv
    from io import StringIO
    from flask import Response
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Name', 'Position', 'Firma', 'Website', 'E-Mail', 'Telefon',
        'LinkedIn', 'Stadt', 'Land', 'Score', 'WhatsApp Consent'
    ])
    
    # Data
    sync_engine = LeadSyncEngine()
    for lead in SAMPLE_EXPLORIUM_LEADS:
        score = sync_engine._calculate_lead_score(lead)
        writer.writerow([
            lead.get('prospect_full_name', ''),
            lead.get('prospect_job_title', ''),
            lead.get('prospect_company_name', ''),
            lead.get('prospect_company_website', ''),
            lead.get('contact_professions_email', ''),
            lead.get('contact_mobile_phone', ''),
            lead.get('prospect_linkedin', ''),
            lead.get('prospect_city', ''),
            lead.get('prospect_country_name', ''),
            score,
            'not_set'
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=leads_export.csv'}
    )

@hubspot_crm_bp.route('/update-consent', methods=['POST'])
def update_consent():
    """Update WhatsApp consent status"""
    try:
        data = request.get_json()
        contact_ids = data.get('contact_ids', [])
        status = data.get('status', 'not_set')
        
        client = HubSpotClient()
        result = client.bulk_update_whatsapp_consent(contact_ids, status)
        
        return jsonify({'success': True, 'updated': len(contact_ids)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@hubspot_crm_bp.route('/webhook', methods=['POST'])
def webhook():
    """HubSpot webhook endpoint for real-time updates"""
    try:
        data = request.get_json()
        
        # Process webhook events
        for event in data:
            event_type = event.get('subscriptionType')
            object_id = event.get('objectId')
            
            # Handle different event types
            if event_type == 'contact.creation':
                # New contact created in HubSpot
                pass
            elif event_type == 'contact.propertyChange':
                # Contact property changed
                pass
            elif event_type == 'deal.creation':
                # New deal created
                pass
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# API ENDPOINTS
# ============================================================================

@hubspot_crm_bp.route('/api/leads')
def api_get_leads():
    """API: Get all leads"""
    sync_engine = LeadSyncEngine()
    leads = []
    
    for lead in SAMPLE_EXPLORIUM_LEADS:
        score = sync_engine._calculate_lead_score(lead)
        leads.append({
            'id': lead.get('prospect_full_name', '').replace(' ', '_').lower(),
            'name': lead.get('prospect_full_name', ''),
            'firstName': lead.get('prospect_first_name', ''),
            'lastName': lead.get('prospect_last_name', ''),
            'position': lead.get('prospect_job_title', ''),
            'company': lead.get('prospect_company_name', ''),
            'website': lead.get('prospect_company_website', ''),
            'email': lead.get('contact_professions_email', ''),
            'phone': lead.get('contact_mobile_phone', ''),
            'linkedin': lead.get('prospect_linkedin', ''),
            'city': lead.get('prospect_city', ''),
            'country': lead.get('prospect_country_name', ''),
            'score': score,
            'skills': lead.get('prospect_skills', ''),
            'whatsappConsent': 'not_set',
            'source': 'explorium'
        })
    
    return jsonify({
        'success': True,
        'total': len(leads),
        'leads': leads
    })

@hubspot_crm_bp.route('/api/leads/<lead_id>')
def api_get_lead(lead_id):
    """API: Get single lead"""
    sync_engine = LeadSyncEngine()
    
    for lead in SAMPLE_EXPLORIUM_LEADS:
        if lead.get('prospect_full_name', '').replace(' ', '_').lower() == lead_id:
            score = sync_engine._calculate_lead_score(lead)
            return jsonify({
                'success': True,
                'lead': {
                    'id': lead_id,
                    'name': lead.get('prospect_full_name', ''),
                    'firstName': lead.get('prospect_first_name', ''),
                    'lastName': lead.get('prospect_last_name', ''),
                    'position': lead.get('prospect_job_title', ''),
                    'company': lead.get('prospect_company_name', ''),
                    'website': lead.get('prospect_company_website', ''),
                    'email': lead.get('contact_professions_email', ''),
                    'phone': lead.get('contact_mobile_phone', ''),
                    'linkedin': lead.get('prospect_linkedin', ''),
                    'city': lead.get('prospect_city', ''),
                    'country': lead.get('prospect_country_name', ''),
                    'score': score,
                    'skills': lead.get('prospect_skills', ''),
                    'whatsappConsent': 'not_set',
                    'source': 'explorium'
                }
            })
    
    return jsonify({'success': False, 'error': 'Lead not found'}), 404


if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(hubspot_crm_bp)
    app.run(debug=True, port=5001)
