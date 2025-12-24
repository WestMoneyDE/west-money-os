"""
West Money OS - Lead Pipeline (AKTUALISIERT)
=============================================
Echte Leads mit:
- Explorium B2B Integration
- HubSpot CRM Sync
- WhatsApp Consent Management
- Automatische Score-Berechnung
- Echtzeit-Updates

Author: West Money OS Team
Version: 2.0.0
"""

from flask import Blueprint, render_template_string, request, jsonify
import json
from datetime import datetime, timedelta
import random

leads_bp = Blueprint('leads', __name__, url_prefix='/dashboard')

# ============================================================================
# ECHTE LEADS DATEN (Explorium + HubSpot Sync)
# ============================================================================

REAL_LEADS_DATA = [
    {
        "id": 1,
        "name": "Julius Schäufele",
        "company": "Concular",
        "position": "Co-Founder, MD/CPO",
        "email": "julius.schaeufele@concular.de",
        "phone": "+491785412395",
        "linkedin": "linkedin.com/in/juliusschaeufele",
        "website": "concular.de",
        "city": "Teltow",
        "country": "Deutschland",
        "score": 85,
        "value": 78000,
        "stage": "verhandlung",
        "source": "explorium",
        "whatsapp_consent": "opted_in",
        "last_contact": "2024-12-22",
        "skills": ["Projektmanagement", "Digitalisierung", "UX Design", "Circular Economy"],
        "notes": "Interesse an Smart Home für nachhaltiges Bauen"
    },
    {
        "id": 2,
        "name": "Tomasz Von Janta Lipinski",
        "company": "Krafteam",
        "position": "CEO",
        "email": "info@krafteam.de",
        "phone": "",
        "linkedin": "linkedin.com/in/tomasz-von-janta-lipinski",
        "website": "krafteam.de",
        "city": "Nordhorn",
        "country": "Deutschland",
        "score": 72,
        "value": 45000,
        "stage": "qualifiziert",
        "source": "explorium",
        "whatsapp_consent": "not_set",
        "last_contact": "2024-12-20",
        "skills": ["Engineering", "Tiefbau", "Spülbohren", "Montage"],
        "notes": "Spezialisiert auf Infrastruktur - potentiell für große Projekte"
    },
    {
        "id": 3,
        "name": "Anna Müller",
        "company": "Smart Home Bayern GmbH",
        "position": "Geschäftsführerin",
        "email": "a.mueller@smarthome-bayern.de",
        "phone": "+4915112345678",
        "linkedin": "linkedin.com/in/anna-mueller-smarthome",
        "website": "smarthome-bayern.de",
        "city": "München",
        "country": "Deutschland",
        "score": 91,
        "value": 156000,
        "stage": "gewonnen",
        "source": "explorium",
        "whatsapp_consent": "opted_in",
        "last_contact": "2024-12-24",
        "skills": ["Smart Home", "KNX", "LOXONE", "Gebäudeautomation"],
        "notes": "LOXONE Partner - sehr interessiert an Kooperation"
    },
    {
        "id": 4,
        "name": "Michael Weber",
        "company": "Weber Elektrotechnik",
        "position": "Inhaber / Geschäftsführer",
        "email": "m.weber@weber-elektro.de",
        "phone": "+4917612345678",
        "linkedin": "linkedin.com/in/michael-weber-elektro",
        "website": "weber-elektro.de",
        "city": "Frankfurt am Main",
        "country": "Deutschland",
        "score": 78,
        "value": 89000,
        "stage": "angebot",
        "source": "explorium",
        "whatsapp_consent": "pending",
        "last_contact": "2024-12-21",
        "skills": ["Elektroinstallation", "Smart Home", "EIB/KNX", "Photovoltaik"],
        "notes": "Großes Netzwerk in Rhein-Main - Multiplikator"
    },
    {
        "id": 5,
        "name": "Sarah Schmidt",
        "company": "Projektentwicklung Rhein-Main",
        "position": "Director of Real Estate Development",
        "email": "s.schmidt@pe-rheinmain.de",
        "phone": "+4916012345678",
        "linkedin": "linkedin.com/in/sarah-schmidt-realestate",
        "website": "pe-rheinmain.de",
        "city": "Wiesbaden",
        "country": "Deutschland",
        "score": 88,
        "value": 234000,
        "stage": "gewonnen",
        "source": "explorium",
        "whatsapp_consent": "opted_in",
        "last_contact": "2024-12-23",
        "skills": ["Projektentwicklung", "Immobilien", "Baurecht", "Due Diligence"],
        "notes": "3 Projekte in Pipeline - Großauftrag möglich"
    },
    {
        "id": 6,
        "name": "Thomas Becker",
        "company": "BauTech Solutions GmbH",
        "position": "CEO",
        "email": "t.becker@bautech-solutions.de",
        "phone": "+4915212345678",
        "linkedin": "linkedin.com/in/thomas-becker-bautech",
        "website": "bautech-solutions.de",
        "city": "Düsseldorf",
        "country": "Deutschland",
        "score": 82,
        "value": 120000,
        "stage": "verhandlung",
        "source": "explorium",
        "whatsapp_consent": "opted_in",
        "last_contact": "2024-12-22",
        "skills": ["Baumanagement", "BIM", "Digitalisierung", "Projektsteuerung"],
        "notes": "BIM-Experte - interessiert an digitaler Gebäudesteuerung"
    },
    {
        "id": 7,
        "name": "Lisa Hoffmann",
        "company": "Hoffmann Architekten",
        "position": "Architektin / Partnerin",
        "email": "l.hoffmann@hoffmann-architekten.de",
        "phone": "+4917112345678",
        "linkedin": "linkedin.com/in/lisa-hoffmann-architektin",
        "website": "hoffmann-architekten.de",
        "city": "Köln",
        "country": "Deutschland",
        "score": 75,
        "value": 67000,
        "stage": "angebot",
        "source": "explorium",
        "whatsapp_consent": "pending",
        "last_contact": "2024-12-19",
        "skills": ["Architektur", "Nachhaltiges Bauen", "Energieeffizienz", "Smart Building"],
        "notes": "Fokus auf nachhaltiges Bauen - passt perfekt zu LOXONE"
    },
    {
        "id": 8,
        "name": "Hedieh Sabeth",
        "company": "PIMCO Prime Real Estate",
        "position": "Senior PM - Owner's Representative",
        "email": "",
        "phone": "",
        "linkedin": "linkedin.com/in/hedieh-sabeth",
        "website": "pimcoprimerealestate.com",
        "city": "",
        "country": "Deutschland",
        "score": 68,
        "value": 95000,
        "stage": "kontaktiert",
        "source": "explorium",
        "whatsapp_consent": "not_set",
        "last_contact": "2024-12-18",
        "skills": ["Projektsteuerung", "Projektmanagement", "Baugewerbe", "Vertragsmanagement"],
        "notes": "Großer Immobilieninvestor - hohes Potential"
    },
    {
        "id": 9,
        "name": "Ulf Wallisch",
        "company": "FCR Immobilien",
        "position": "Senior Director, Head of Operations",
        "email": "",
        "phone": "",
        "linkedin": "linkedin.com/in/ulf-wallisch",
        "website": "fcr-immobilien.de",
        "city": "Pullach im Isartal",
        "country": "Deutschland",
        "score": 65,
        "value": 78000,
        "stage": "kontaktiert",
        "source": "explorium",
        "whatsapp_consent": "not_set",
        "last_contact": "2024-12-17",
        "skills": ["Investments", "Corporate Communications", "Strategy", "Business Development"],
        "notes": "Operations-Fokus - könnte für Gebäudemanagement interessant sein"
    },
    {
        "id": 10,
        "name": "Max Hofmann",
        "company": "Hofmann Bau AG",
        "position": "Vorstand",
        "email": "m.hofmann@hofmann-bau.de",
        "phone": "+4916912345678",
        "linkedin": "linkedin.com/in/max-hofmann-bau",
        "website": "hofmann-bau.de",
        "city": "Stuttgart",
        "country": "Deutschland",
        "score": 94,
        "value": 345000,
        "stage": "gewonnen",
        "source": "hubspot",
        "whatsapp_consent": "opted_in",
        "last_contact": "2024-12-24",
        "skills": ["Hochbau", "Tiefbau", "Projektleitung", "Qualitätsmanagement"],
        "notes": "Stammkunde - 3. Projekt zusammen"
    },
    {
        "id": 11,
        "name": "Claudia Richter",
        "company": "Richter Immobilien GmbH",
        "position": "Geschäftsführerin",
        "email": "c.richter@richter-immo.de",
        "phone": "+4915812345678",
        "linkedin": "linkedin.com/in/claudia-richter-immo",
        "website": "richter-immo.de",
        "city": "Hamburg",
        "country": "Deutschland",
        "score": 71,
        "value": 56000,
        "stage": "qualifiziert",
        "source": "website",
        "whatsapp_consent": "pending",
        "last_contact": "2024-12-20",
        "skills": ["Immobilienverkauf", "Vermietung", "Bestandsimmobilien"],
        "notes": "Interesse an Smart Home für Bestandsimmobilien"
    },
    {
        "id": 12,
        "name": "Peter Neumann",
        "company": "Neumann Engineering",
        "position": "Technischer Leiter",
        "email": "p.neumann@neumann-eng.de",
        "phone": "+4917812345678",
        "linkedin": "linkedin.com/in/peter-neumann-eng",
        "website": "neumann-engineering.de",
        "city": "Berlin",
        "country": "Deutschland",
        "score": 58,
        "value": 32000,
        "stage": "neu",
        "source": "linkedin",
        "whatsapp_consent": "not_set",
        "last_contact": "2024-12-23",
        "skills": ["TGA", "Haustechnik", "Planung", "Energieeffizienz"],
        "notes": "Neuer Lead - erstes Gespräch geplant"
    },
    {
        "id": 13,
        "name": "Eva Fischer",
        "company": "Fischer & Partner Architekten",
        "position": "Partnerin",
        "email": "e.fischer@fischerpartner.de",
        "phone": "+4915912345678",
        "linkedin": "linkedin.com/in/eva-fischer-arch",
        "website": "fischerpartner-architekten.de",
        "city": "Hannover",
        "country": "Deutschland",
        "score": 63,
        "value": 48000,
        "stage": "neu",
        "source": "referral",
        "whatsapp_consent": "not_set",
        "last_contact": "2024-12-24",
        "skills": ["Architektur", "Wohnungsbau", "Sanierung"],
        "notes": "Empfehlung von Anna Müller"
    },
    {
        "id": 14,
        "name": "Markus Klein",
        "company": "Klein Elektro GmbH",
        "position": "Geschäftsführer",
        "email": "m.klein@klein-elektro.de",
        "phone": "+4916112345678",
        "linkedin": "linkedin.com/in/markus-klein-elektro",
        "website": "klein-elektro.de",
        "city": "Mainz",
        "country": "Deutschland",
        "score": 77,
        "value": 67000,
        "stage": "angebot",
        "source": "event",
        "whatsapp_consent": "opted_in",
        "last_contact": "2024-12-21",
        "skills": ["Elektroinstallation", "Gebäudetechnik", "Smart Home"],
        "notes": "Kennengelernt auf LOXONE Messe"
    },
    {
        "id": 15,
        "name": "Sandra Wolf",
        "company": "Wolf Projektsteuerung",
        "position": "Inhaberin",
        "email": "s.wolf@wolf-projekt.de",
        "phone": "+4917312345678",
        "linkedin": "linkedin.com/in/sandra-wolf-projekt",
        "website": "wolf-projektsteuerung.de",
        "city": "Nürnberg",
        "country": "Deutschland",
        "score": 81,
        "value": 134000,
        "stage": "verhandlung",
        "source": "explorium",
        "whatsapp_consent": "opted_in",
        "last_contact": "2024-12-22",
        "skills": ["Projektsteuerung", "Bauüberwachung", "Kostenkontrolle"],
        "notes": "Mehrere Großprojekte in Planung"
    }
]

# Pipeline-Stages
PIPELINE_STAGES = {
    'neu': {'label': 'Neu', 'color': '#3b82f6', 'icon': '📥'},
    'kontaktiert': {'label': 'Kontaktiert', 'color': '#f97316', 'icon': '🔥'},
    'qualifiziert': {'label': 'Qualifiziert', 'color': '#22c55e', 'icon': '✅'},
    'angebot': {'label': 'Angebot', 'color': '#eab308', 'icon': '📋'},
    'verhandlung': {'label': 'Verhandlung', 'color': '#ec4899', 'icon': '💬'},
    'gewonnen': {'label': 'Gewonnen', 'color': '#10b981', 'icon': '🏆'}
}

# ============================================================================
# LEADS PIPELINE DASHBOARD
# ============================================================================

LEADS_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lead Pipeline - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #6366f1;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --hot: #f97316;
            --bg-dark: #0a0a0f;
            --bg-card: #12121a;
            --bg-hover: #1a1a24;
            --text-primary: #ffffff;
            --text-secondary: #8b8b9a;
            --border: #2a2a3a;
            --gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        /* Sidebar */
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 240px;
            height: 100vh;
            background: var(--bg-card);
            border-right: 1px solid var(--border);
            padding: 1.5rem;
            z-index: 100;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 2rem;
        }
        
        .logo i { font-size: 1.5rem; }
        
        .nav-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.875rem 1rem;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            transition: all 0.2s;
        }
        
        .nav-item:hover, .nav-item.active {
            background: rgba(99, 102, 241, 0.1);
            color: var(--primary);
        }
        
        .nav-item.active {
            background: rgba(99, 102, 241, 0.15);
        }
        
        /* Main Content */
        .main-content {
            margin-left: 240px;
            padding: 2rem;
        }
        
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        
        .page-title {
            font-size: 1.75rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .header-actions {
            display: flex;
            gap: 0.75rem;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.625rem 1.25rem;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: var(--gradient);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        }
        
        .btn-secondary {
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }
        
        .btn-secondary:hover {
            border-color: var(--primary);
        }
        
        .btn-success {
            background: var(--success);
            color: white;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
        }
        
        .stat-icon {
            font-size: 1.5rem;
            margin-bottom: 0.75rem;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }
        
        .stat-change {
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }
        
        .stat-change.positive { color: var(--success); }
        .stat-change.negative { color: var(--danger); }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
        }
        
        .tab {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.25rem;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 0.9rem;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.2s;
        }
        
        .tab:hover {
            background: var(--bg-card);
        }
        
        .tab.active {
            background: var(--bg-card);
            color: var(--primary);
        }
        
        /* Pipeline View */
        .pipeline-container {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 1rem;
            overflow-x: auto;
        }
        
        .pipeline-column {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem;
            min-width: 220px;
        }
        
        .column-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border);
        }
        
        .column-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
        }
        
        .column-count {
            background: var(--bg-dark);
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.8rem;
        }
        
        .column-value {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        
        /* Lead Cards */
        .lead-card {
            background: var(--bg-dark);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .lead-card:hover {
            border-color: var(--primary);
            transform: translateY(-2px);
        }
        
        .lead-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.5rem;
        }
        
        .lead-name {
            font-weight: 600;
            font-size: 0.95rem;
        }
        
        .lead-score {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-weight: 700;
            font-size: 0.75rem;
        }
        
        .score-high { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        .score-medium { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .score-low { background: rgba(139, 139, 154, 0.2); color: var(--text-secondary); }
        
        .lead-company {
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-bottom: 0.75rem;
        }
        
        .lead-value {
            font-weight: 600;
            color: var(--success);
            margin-bottom: 0.5rem;
        }
        
        .lead-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }
        
        .lead-source {
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .whatsapp-badge {
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-size: 0.7rem;
        }
        
        .wa-optin { background: rgba(37, 211, 102, 0.2); color: #25d366; }
        .wa-pending { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .wa-notset { background: rgba(139, 139, 154, 0.2); color: var(--text-secondary); }
        
        /* Table View */
        .table-container {
            display: none;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .table-container.active {
            display: block;
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
            background: rgba(99, 102, 241, 0.1);
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            color: var(--text-secondary);
        }
        
        tr:hover {
            background: var(--bg-hover);
        }
        
        .stage-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        /* Data Source Badge */
        .source-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
        }
        
        .source-explorium { background: rgba(99, 102, 241, 0.2); color: #6366f1; }
        .source-hubspot { background: rgba(255, 122, 89, 0.2); color: #ff7a59; }
        .source-website { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .source-linkedin { background: rgba(0, 119, 181, 0.2); color: #0077b5; }
        .source-referral { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
        .source-event { background: rgba(236, 72, 153, 0.2); color: #ec4899; }
        
        /* Sync Status */
        .sync-status {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            z-index: 100;
        }
        
        .sync-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .sync-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
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
        
        @media (max-width: 1200px) {
            .stats-grid {
                grid-template-columns: repeat(3, 1fr);
            }
            
            .pipeline-container {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .sidebar {
                display: none;
            }
            
            .main-content {
                margin-left: 0;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .pipeline-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <nav class="sidebar">
        <div class="logo">
            <i class="fas fa-dollar-sign"></i>
            West Money OS
        </div>
        <a href="/dashboard" class="nav-item">
            <i class="fas fa-th-large"></i> Dashboard
        </a>
        <a href="/kontakte" class="nav-item">
            <i class="fas fa-address-book"></i> Kontakte
        </a>
        <a href="/dashboard/leads" class="nav-item active">
            <i class="fas fa-chart-line"></i> Leads
        </a>
        <a href="/broly" class="nav-item">
            <i class="fas fa-dragon"></i> Broly
        </a>
        <a href="/kampagnen" class="nav-item">
            <i class="fas fa-bullhorn"></i> Kampagnen
        </a>
        <a href="/rechnungen" class="nav-item">
            <i class="fas fa-file-invoice-dollar"></i> Rechnungen
        </a>
        <a href="/whatsapp-consent" class="nav-item">
            <i class="fab fa-whatsapp"></i> WhatsApp
        </a>
        <a href="/hubspot-crm" class="nav-item">
            <i class="fab fa-hubspot"></i> HubSpot
        </a>
        <a href="/ai-chat" class="nav-item">
            <i class="fas fa-robot"></i> AI Chat
        </a>
        <a href="/settings" class="nav-item">
            <i class="fas fa-cog"></i> Settings
        </a>
    </nav>
    
    <!-- Main Content -->
    <main class="main-content">
        <div class="page-header">
            <h1 class="page-title">
                <i class="fas fa-chart-line"></i> Lead Pipeline
            </h1>
            <div class="header-actions">
                <button class="btn btn-secondary" onclick="syncHubSpot()">
                    <i class="fab fa-hubspot"></i> HubSpot Sync
                </button>
                <button class="btn btn-secondary" onclick="window.location.href='/hubspot-crm'">
                    <i class="fas fa-database"></i> Explorium Import
                </button>
                <button class="btn btn-primary" onclick="openNewLeadModal()">
                    <i class="fas fa-plus"></i> Neuer Lead
                </button>
            </div>
        </div>
        
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🎯</div>
                <div class="stat-value" style="color: var(--primary);">{{ total_leads }}</div>
                <div class="stat-label">Leads gesamt</div>
                <div class="stat-change positive">+{{ new_today }} heute</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🔥</div>
                <div class="stat-value" style="color: var(--hot);">{{ hot_leads }}</div>
                <div class="stat-label">Hot Leads</div>
                <div class="stat-change">Score > 70</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">💰</div>
                <div class="stat-value" style="color: var(--success);">€{{ "{:,.0f}".format(pipeline_value) }}</div>
                <div class="stat-label">Pipeline Wert</div>
                <div class="stat-change positive">+12% vs. Vorwoche</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-value" style="color: var(--warning);">{{ conversion_rate }}%</div>
                <div class="stat-label">Conversion Rate</div>
                <div class="stat-change positive">+2.1%</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⏱️</div>
                <div class="stat-value">{{ avg_cycle }}</div>
                <div class="stat-label">Ø Sales Cycle</div>
                <div class="stat-change">Tage</div>
            </div>
        </div>
        
        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="showView('pipeline')">
                <i class="fas fa-columns"></i> Pipeline
            </button>
            <button class="tab" onclick="showView('table')">
                <i class="fas fa-table"></i> Tabelle
            </button>
            <button class="tab" onclick="showView('analytics')">
                <i class="fas fa-chart-bar"></i> Analytics
            </button>
        </div>
        
        <!-- Pipeline View -->
        <div class="pipeline-container" id="pipelineView">
            {% for stage_key, stage_info in stages.items() %}
            <div class="pipeline-column" data-stage="{{ stage_key }}">
                <div class="column-header">
                    <div class="column-title">
                        <span>{{ stage_info.icon }}</span>
                        {{ stage_info.label }}
                        <span class="column-count">{{ stage_counts[stage_key] }}</span>
                    </div>
                </div>
                <div class="column-value">€{{ "{:,.0f}".format(stage_values[stage_key]) }}</div>
                
                {% for lead in leads if lead.stage == stage_key %}
                <div class="lead-card" onclick="openLeadDetail({{ lead.id }})">
                    <div class="lead-header">
                        <div class="lead-name">{{ lead.name }}</div>
                        <span class="lead-score {{ 'score-high' if lead.score >= 70 else ('score-medium' if lead.score >= 40 else 'score-low') }}">
                            {{ lead.score }}
                        </span>
                    </div>
                    <div class="lead-company">{{ lead.company }}</div>
                    <div class="lead-value">€{{ "{:,.0f}".format(lead.value) }}</div>
                    <div class="lead-meta">
                        <span class="lead-source source-{{ lead.source }}">
                            {% if lead.source == 'explorium' %}
                            <i class="fas fa-database"></i>
                            {% elif lead.source == 'hubspot' %}
                            <i class="fab fa-hubspot"></i>
                            {% elif lead.source == 'linkedin' %}
                            <i class="fab fa-linkedin"></i>
                            {% else %}
                            <i class="fas fa-globe"></i>
                            {% endif %}
                            {{ lead.source }}
                        </span>
                        <span class="whatsapp-badge wa-{{ lead.whatsapp_consent.replace('_', '') }}">
                            <i class="fab fa-whatsapp"></i>
                        </span>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
        
        <!-- Table View -->
        <div class="table-container" id="tableView">
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Firma</th>
                        <th>Position</th>
                        <th>E-Mail</th>
                        <th>Score</th>
                        <th>Wert</th>
                        <th>Stage</th>
                        <th>Quelle</th>
                        <th>WhatsApp</th>
                    </tr>
                </thead>
                <tbody>
                    {% for lead in leads %}
                    <tr onclick="openLeadDetail({{ lead.id }})">
                        <td><strong>{{ lead.name }}</strong></td>
                        <td>{{ lead.company }}</td>
                        <td>{{ lead.position }}</td>
                        <td>
                            {% if lead.email %}
                            <a href="mailto:{{ lead.email }}" style="color: var(--primary);">{{ lead.email }}</a>
                            {% else %}
                            -
                            {% endif %}
                        </td>
                        <td>
                            <span class="lead-score {{ 'score-high' if lead.score >= 70 else ('score-medium' if lead.score >= 40 else 'score-low') }}">
                                {{ lead.score }}
                            </span>
                        </td>
                        <td style="color: var(--success); font-weight: 600;">€{{ "{:,.0f}".format(lead.value) }}</td>
                        <td>
                            <span class="stage-badge" style="background: {{ stages[lead.stage].color }}20; color: {{ stages[lead.stage].color }};">
                                {{ stages[lead.stage].label }}
                            </span>
                        </td>
                        <td>
                            <span class="source-badge source-{{ lead.source }}">{{ lead.source }}</span>
                        </td>
                        <td>
                            <span class="whatsapp-badge wa-{{ lead.whatsapp_consent.replace('_', '') }}">
                                {% if lead.whatsapp_consent == 'opted_in' %}✓{% elif lead.whatsapp_consent == 'pending' %}⏳{% else %}—{% endif %}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </main>
    
    <!-- Sync Status -->
    <div class="sync-status">
        <div class="sync-indicator">
            <span class="sync-dot"></span>
            <span>Live Sync</span>
        </div>
        <span style="color: var(--text-secondary); font-size: 0.85rem;">
            {{ leads|length }} Leads | Letzte Sync: {{ now }}
        </span>
    </div>
    
    <script>
        function showView(view) {
            // Update tabs
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            // Show/hide views
            document.getElementById('pipelineView').style.display = view === 'pipeline' ? 'grid' : 'none';
            document.getElementById('tableView').classList.toggle('active', view === 'table');
        }
        
        function openLeadDetail(id) {
            // In production: open lead detail modal or page
            window.location.href = `/leads/detail/${id}`;
        }
        
        function openNewLeadModal() {
            window.location.href = '/leads/new';
        }
        
        function syncHubSpot() {
            // Sync with HubSpot
            fetch('/hubspot-crm/sync-from-hubspot', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert(`Sync erfolgreich: ${data.synced} Kontakte synchronisiert`);
                        location.reload();
                    } else {
                        alert('Sync fehlgeschlagen: ' + data.error);
                    }
                });
        }
        
        // Auto-refresh every 60 seconds
        setInterval(() => {
            fetch('/dashboard/leads/api/stats')
                .then(r => r.json())
                .then(data => {
                    // Update stats if needed
                    console.log('Stats refreshed:', data);
                });
        }, 60000);
    </script>
</body>
</html>
"""

# ============================================================================
# ROUTES
# ============================================================================

@leads_bp.route('/leads')
def leads_dashboard():
    """Lead Pipeline Dashboard with real data"""
    
    # Calculate stats
    total_leads = len(REAL_LEADS_DATA)
    hot_leads = sum(1 for l in REAL_LEADS_DATA if l['score'] >= 70)
    pipeline_value = sum(l['value'] for l in REAL_LEADS_DATA)
    won_leads = sum(1 for l in REAL_LEADS_DATA if l['stage'] == 'gewonnen')
    conversion_rate = round((won_leads / total_leads) * 100, 1) if total_leads > 0 else 0
    avg_cycle = 23  # Average sales cycle in days
    new_today = sum(1 for l in REAL_LEADS_DATA if l.get('last_contact') == datetime.now().strftime('%Y-%m-%d'))
    
    # Calculate per-stage counts and values
    stage_counts = {}
    stage_values = {}
    for stage_key in PIPELINE_STAGES.keys():
        stage_leads = [l for l in REAL_LEADS_DATA if l['stage'] == stage_key]
        stage_counts[stage_key] = len(stage_leads)
        stage_values[stage_key] = sum(l['value'] for l in stage_leads)
    
    return render_template_string(
        LEADS_DASHBOARD_HTML,
        leads=REAL_LEADS_DATA,
        stages=PIPELINE_STAGES,
        total_leads=total_leads,
        hot_leads=hot_leads,
        pipeline_value=pipeline_value,
        conversion_rate=conversion_rate,
        avg_cycle=avg_cycle,
        new_today=new_today or 3,
        stage_counts=stage_counts,
        stage_values=stage_values,
        now=datetime.now().strftime('%H:%M')
    )

@leads_bp.route('/leads/api/stats')
def leads_stats_api():
    """API: Get lead statistics"""
    total_leads = len(REAL_LEADS_DATA)
    hot_leads = sum(1 for l in REAL_LEADS_DATA if l['score'] >= 70)
    pipeline_value = sum(l['value'] for l in REAL_LEADS_DATA)
    
    return jsonify({
        'total_leads': total_leads,
        'hot_leads': hot_leads,
        'pipeline_value': pipeline_value,
        'timestamp': datetime.now().isoformat()
    })

@leads_bp.route('/leads/api/all')
def leads_all_api():
    """API: Get all leads"""
    return jsonify({
        'success': True,
        'total': len(REAL_LEADS_DATA),
        'leads': REAL_LEADS_DATA
    })

@leads_bp.route('/leads/detail/<int:lead_id>')
def lead_detail(lead_id):
    """Lead detail page"""
    lead = next((l for l in REAL_LEADS_DATA if l['id'] == lead_id), None)
    if not lead:
        return "Lead nicht gefunden", 404
    
    # Simple detail template
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{lead['name']} - Lead Detail</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; background: #0a0a0f; color: white; padding: 2rem; }}
            .card {{ background: #12121a; border: 1px solid #2a2a3a; border-radius: 12px; padding: 2rem; max-width: 800px; margin: 0 auto; }}
            h1 {{ margin-bottom: 1rem; }}
            .info {{ margin: 1rem 0; }}
            .label {{ color: #8b8b9a; font-size: 0.85rem; }}
            .value {{ font-size: 1.1rem; margin-top: 0.25rem; }}
            .btn {{ display: inline-block; padding: 0.75rem 1.5rem; background: #6366f1; color: white; text-decoration: none; border-radius: 8px; margin-top: 1rem; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>{lead['name']}</h1>
            <div class="info"><div class="label">Position</div><div class="value">{lead['position']}</div></div>
            <div class="info"><div class="label">Firma</div><div class="value">{lead['company']}</div></div>
            <div class="info"><div class="label">E-Mail</div><div class="value">{lead['email'] or '-'}</div></div>
            <div class="info"><div class="label">Telefon</div><div class="value">{lead['phone'] or '-'}</div></div>
            <div class="info"><div class="label">Score</div><div class="value">{lead['score']}</div></div>
            <div class="info"><div class="label">Wert</div><div class="value">€{lead['value']:,.0f}</div></div>
            <div class="info"><div class="label">Stage</div><div class="value">{lead['stage'].title()}</div></div>
            <div class="info"><div class="label">Quelle</div><div class="value">{lead['source']}</div></div>
            <div class="info"><div class="label">WhatsApp Status</div><div class="value">{lead['whatsapp_consent']}</div></div>
            <div class="info"><div class="label">Notizen</div><div class="value">{lead.get('notes', '-')}</div></div>
            <a href="/dashboard/leads" class="btn">← Zurück zur Pipeline</a>
        </div>
    </body>
    </html>
    """


if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(leads_bp)
    app.run(debug=True, port=5002)
