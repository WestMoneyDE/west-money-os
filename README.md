# 🔥 West Money OS v9.0 - BROLY ULTRA GODMODE Edition

> Die ultimative All-in-One Business Platform für Enterprise Universe GmbH

![Version](https://img.shields.io/badge/version-9.0.0--BROLY-purple)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-Proprietary-red)
![Status](https://img.shields.io/badge/status-GODMODE-orange)

## 🚀 Features

### 📱 WhatsApp Business API
- Vollständige Meta WhatsApp Business API v21.0 Integration
- Template-Nachrichten für Marketing-Kampagnen
- Interaktive Buttons und Quick Replies
- Media-Upload (Bilder, PDFs, Dokumente)
- Webhook-Handler für eingehende Nachrichten
- Status-Tracking (gesendet, zugestellt, gelesen)
- Automatische Welcome-Messages

### 🤖 AI-Powered Chatbots (Claude AI)
- **Support Bot**: Kundenservice & FAQ
- **Sales Bot**: Lead-Qualifizierung & Beratung
- **Concierge Bot**: VIP Premium-Service
- Kontextbewusstes Multi-Turn Conversation
- Automatische Lead-Analyse

### 💼 CRM & Lead Management
- Unbegrenzte Kontakte und Leads
- Kanban-Pipeline (Discovery → Won/Lost)
- Lead-Scoring mit AI
- HubSpot Bidirektionale Synchronisation
- Explorium B2B Data Enrichment
- Handelsregister-Integration (OpenCorporates)

### 💳 Payment & Subscription System
- **Stripe**: Checkout, Subscriptions, Customer Portal
- **Mollie**: EU-optimierte Zahlungen (iDEAL, SOFORT, etc.)
- **SEPA**: Lastschrift für Firmenkunden
- Wiederkehrende Abrechnung
- Automatische Rechnungserstellung
- DATEV-Export für Steuerberater

### 🏦 Banking Integration (Revolut Business)
- Multi-Währungskonten
- Echtzeit-Kontostände
- Transaktionsübersicht
- Überweisungen erstellen
- Wechselkurse
- DATEV-Export für Buchhaltung

### 📊 Analytics & Dashboard
- Echtzeit-Statistiken
- MRR/ARR Berechnung
- Churn-Rate Tracking
- Revenue by Plan
- Pipeline-Analytics
- Security Score

### 🔒 Security (DedSec World AI)
- Session-basierte Authentifizierung
- Passwort-Hashing (SHA-256)
- Security Event Logging
- Rate Limiting
- CSRF Protection
- Security Headers (HSTS, X-Frame-Options, etc.)

### ⚡ Auto Bots (Automatisierung)
- **LeadScoringBot**: Automatische Lead-Bewertung
- **FollowUpBot**: Erstellt Aufgaben für inaktive Kontakte
- **SyncBot**: Synchronisiert mit HubSpot
- **WelcomeBot**: Sendet Willkommensnachrichten

## 🛠️ Installation

### Voraussetzungen
- Python 3.11+
- PostgreSQL (oder SQLite für Development)
- Redis (optional, für Echtzeit-Features)
- Node.js (für Frontend-Entwicklung)

### Setup

```bash
# Repository klonen
git clone https://github.com/enterprise-universe/westmoney-os.git
cd westmoney-os

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: .\venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Environment konfigurieren
cp .env.example .env
# .env mit deinen API-Keys bearbeiten

# Datenbank initialisieren
flask db upgrade

# Server starten
python app.py
```

### Docker Deployment

```bash
# Build
docker build -t westmoney-os:9.0 .

# Run
docker run -d \
  --name westmoney \
  -p 5000:5000 \
  --env-file .env \
  westmoney-os:9.0
```

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/register` | Registrierung |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Current User |

### Contacts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/contacts` | Alle Kontakte |
| POST | `/api/contacts` | Neuer Kontakt |
| GET | `/api/contacts/:id` | Einzelner Kontakt |
| PUT | `/api/contacts/:id` | Kontakt bearbeiten |
| DELETE | `/api/contacts/:id` | Kontakt löschen |
| POST | `/api/contacts/bulk-consent` | Massen-WhatsApp-Consent |

### Leads
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads` | Alle Leads |
| POST | `/api/leads` | Neuer Lead |
| PUT | `/api/leads/:id` | Lead bearbeiten |

### WhatsApp
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/whatsapp/send` | Nachricht senden |
| GET | `/api/whatsapp/templates` | Templates abrufen |
| GET/POST | `/api/whatsapp/webhook` | Webhook Handler |
| GET | `/api/whatsapp/messages/:id` | Nachrichten eines Kontakts |

### AI Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chat` | Chat mit AI Bot |
| POST | `/api/ai/analyze-lead` | Lead-Analyse |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/payments/plans` | Verfügbare Pläne |
| POST | `/api/payments/checkout` | Checkout starten |
| POST | `/api/payments/portal` | Billing Portal |
| GET | `/api/payments/subscription` | Aktuelles Abo |
| POST | `/api/payments/cancel` | Abo kündigen |

### Banking
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/banking/accounts` | Konten |
| POST | `/api/banking/sync` | Revolut Sync |
| GET | `/api/banking/transactions` | Transaktionen |
| POST | `/api/banking/transfer` | Überweisung |
| GET | `/api/banking/balance` | Gesamtsaldo |
| GET | `/api/banking/export/datev` | DATEV Export |

### Invoices
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/invoices` | Alle Rechnungen |
| POST | `/api/invoices` | Neue Rechnung |
| POST | `/api/invoices/:id/send` | Rechnung senden |
| POST | `/api/invoices/:id/paid` | Als bezahlt markieren |

## 💰 Pricing Plans

| Plan | Preis/Monat | Preis/Jahr | Features |
|------|-------------|------------|----------|
| **Free** | €0 | €0 | 3 Kontakte, 2 Leads, Basis Dashboard |
| **Starter** | €29 | €290 | 50 Kontakte, 25 Leads, Handelsregister, Export |
| **Professional** | €99 | €990 | Unbegrenzt, WhatsApp, HubSpot, API, AI |
| **Enterprise** | €299 | €2.990 | Alles + White Label, Custom, SLA 99.9% |

## 🔧 Konfiguration

### WhatsApp Business API
1. Meta Business Suite einrichten
2. WhatsApp Business Account erstellen
3. Phone Number hinzufügen
4. Webhook konfigurieren: `https://your-domain.com/api/whatsapp/webhook`

### Stripe Payments
1. Stripe Account erstellen
2. Produkte und Preise anlegen
3. Webhook konfigurieren: `https://your-domain.com/api/payments/webhook/stripe`
4. Price IDs in .env eintragen

### Revolut Business
1. Revolut Business Account
2. API-Zugang beantragen
3. API Key in .env eintragen

### HubSpot
1. Private App in HubSpot erstellen
2. Scopes: crm.objects.contacts, crm.objects.deals
3. API Token in .env eintragen

## 🏗️ Architektur

```
westmoney_v9/
├── app.py                 # Hauptanwendung (Monolith)
├── requirements.txt       # Python Dependencies
├── .env.example          # Environment Template
├── README.md             # Diese Dokumentation
├── docker-compose.yml    # Docker Setup
├── Dockerfile            # Container Build
└── tests/                # Test Suite
    ├── test_auth.py
    ├── test_contacts.py
    └── test_payments.py
```

### Zukünftige Modularisierung (v10.0)
```
westmoney_v10/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── blueprints/
│   ├── auth/
│   ├── crm/
│   ├── whatsapp/
│   ├── payments/
│   └── banking/
└── ...
```

## 🧪 Testing

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=app --cov-report=html

# Einzelne Tests
pytest tests/test_auth.py -v
```

## 📈 Monitoring

- Health Check: `GET /api/health`
- Metrics: Flask-MonitoringDashboard unter `/dashboard`
- Errors: Sentry Integration

## 🔐 Security Best Practices

1. ✅ HTTPS in Production
2. ✅ Environment Variables für Secrets
3. ✅ Rate Limiting aktiviert
4. ✅ CORS konfiguriert
5. ✅ Security Headers
6. ✅ Input Validation
7. ✅ SQL Injection Prevention (SQLAlchemy ORM)

## 🤝 Support

- **CEO**: Ömer Hüseyin Coşkun
- **Email**: support@westmoney.de
- **Web**: https://westmoney.de

## 📜 Lizenz

Copyright © 2025 Enterprise Universe GmbH. Alle Rechte vorbehalten.

---

<div align="center">
  <h3>🔥 BROLY ULTRA GODMODE - POWER LEVEL OVER 9000! 🔥</h3>
  <p>Built with 💜 by Enterprise Universe GmbH</p>
</div>
