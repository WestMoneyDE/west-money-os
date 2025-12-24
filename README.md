# 🔥 WEST MONEY OS v15.369 - ULTIMATE EDITION

**Enterprise Universe GmbH** | CEO: Ömer Hüseyin Coşkun  
**Launch Date:** 01.01.2026

---

## 📋 Features

### Main Modules
- **Dashboard** - Live KPIs, Pipeline Overview, Activity Feed
- **Lead Management** - HubSpot Sync, Scoring, Stages
- **Contacts** - CRM Integration, WhatsApp Consent
- **Projects** - Bauprojekte, Smart Home, LOXONE/KNX
- **Invoices** - SevDesk Integration

### Einstein AI
- **Predictions** - ML-basierte Lead Scoring
- **Analytics** - Deep Learning Datenanalyse  
- **Insights** - Automatische Empfehlungen

### Photovoltaik ☀️
- **PV Home** - Solar Dashboard
- **Partner** - 1Komma5°, Enpal, Zolar, Solarwatt
- **PV Rechner** - ROI & Amortisation

### DedSec Security 🛡️
- **Security Hub** - System Status
- **Command Tower** - Zentrale Überwachung
- **Drone Control** - Patrol Drones
- **CCTV Network** - 24 Kameras

### Tools
- **WhatsApp Business** - Kommunikation & Kampagnen
- **Consent Manager** - Bulk-Update Einwilligungen
- **GOD BOT AI** - Claude-powered Assistant
- **Private Locker** - Dokumenten-Ablage

---

## 🚀 Quick Start

```bash
# Clone/Copy files
cd /var/www/west-money-os

# Setup Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add your API keys

# Run
python app.py
```

---

## ⚙️ Configuration

Edit `.env` file:

```env
HUBSPOT_API_KEY=pat-eu1-xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx
SEVDESK_API_KEY=xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
WHATSAPP_TOKEN=xxxxx
```

---

## 🖥️ Server Deployment

```bash
# Copy service file
sudo cp westmoney.service /etc/systemd/system/

# Enable & Start
sudo systemctl daemon-reload
sudo systemctl enable westmoney
sudo systemctl start westmoney

# Check status
sudo systemctl status westmoney
```

---

## 🔐 Default Login

- **Username:** admin
- **Password:** admin123

---

## 📡 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/v1/health` | Health Check |
| `/api/v1/stats` | System Stats |
| `/api/sync/hubspot` | Sync HubSpot |
| `/api/sync/stripe` | Sync Stripe |
| `/api/sync/sevdesk` | Sync SevDesk |
| `/api/whatsapp/consent/bulk` | Bulk Consent Update |
| `/api/godbot/chat` | GOD BOT AI Chat |

---

## 🏗️ Tech Stack

- **Backend:** Python Flask
- **Database:** SQLite
- **Frontend:** Vanilla JS, Chart.js
- **APIs:** HubSpot, Stripe, SevDesk, Claude AI, WhatsApp

---

## 📞 Support

**West Money Bau**  
Enterprise Universe GmbH  
CEO: Ömer Hüseyin Coşkun

---

*Powered by GOD MODE ∞ Ultra Instinct* 🤖
