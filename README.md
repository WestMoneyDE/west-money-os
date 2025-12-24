# 💰 West Money OS v11.0 ULTIMATE GODMODE

> Enterprise Business Platform by Enterprise Universe GmbH

[![Deploy](https://github.com/YOUR_USERNAME/westmoney/actions/workflows/deploy.yml/badge.svg)](https://github.com/YOUR_USERNAME/westmoney/actions/workflows/deploy.yml)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)]()

## 🚀 Features

### Core CRM
- 👥 **Kontakte** - Full CRUD with search & filters
- 🎯 **Leads** - Kanban pipeline (6 stages)
- 📧 **Kampagnen** - Marketing automation
- 📄 **Rechnungen** - Billing & invoicing

### Power Modules
- 🤖 **AI Chat** - Claude AI integration
- 💪 **Broly Taskforce** - LEGENDARY automation engine
- 🧠 **Einstein Agency** - 8 genius AI bots
- 🔐 **DedSec Security** - Enterprise security monitoring
- 🪙 **Token Economy** - GOD, DEDSEC, OG, TOWER tokens

### Communication
- 📱 **WhatsApp Business** - Full API integration + OTP Auth
- 🏠 **LOXONE** - Smart home control

### Compliance (DSGVO)
- ✅ Impressum, Datenschutz, AGB, Widerruf
- ✅ WhatsApp Consent Management
- ✅ HubSpot Consent Sync
- ✅ Data Export (Art. 20)
- ✅ Account Deletion (Art. 17)
- ✅ Cookie Consent Banner

## 📱 WhatsApp Authentication

Login via WhatsApp OTP:
```
/auth/whatsapp → Enter phone → Receive OTP → Verify → Dashboard
```

## 🔧 Installation

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/westmoney.git
cd westmoney

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Environment
cp .env.example .env
# Edit .env with your API keys

# Run
python app.py
```

## ⚙️ Environment Variables

```env
# Required
SECRET_KEY=your-secret-key

# Optional - APIs
ANTHROPIC_API_KEY=sk-ant-xxx
HUBSPOT_API_KEY=pat-xxx
WHATSAPP_TOKEN=xxx
WHATSAPP_PHONE_ID=xxx
WHATSAPP_VERIFY_TOKEN=your_verify_token

# Optional - Payments
STRIPE_SECRET_KEY=sk_xxx
REVOLUT_API_KEY=xxx
```

## 🚀 Deployment

### Automatic (GitHub Actions)

1. Add secrets in GitHub:
   - `SSH_PRIVATE_KEY` - Server SSH key
   
2. Push to main branch → Auto deploy

### Manual

```bash
ssh user@server
cd /var/www/westmoney
git pull origin main
sudo systemctl restart westmoney
```

## 📊 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/whatsapp/send-otp` | Send WhatsApp OTP |
| POST | `/api/auth/whatsapp/verify-otp` | Verify OTP & login |

### Contacts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/contacts` | List all contacts |
| POST | `/api/contacts` | Create contact |
| PUT | `/api/contacts/:id` | Update contact |
| DELETE | `/api/contacts/:id` | Delete contact |
| POST | `/api/contacts/whatsapp-consent/bulk` | Bulk consent update |

### HubSpot Integration
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/hubspot/sync-consent` | Sync consent to HubSpot |
| POST | `/api/hubspot/import-contacts` | Import from HubSpot |

### DSGVO
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/data-export` | Export all user data |
| POST | `/api/user/delete-account` | Delete account & data |
| GET | `/api/contacts/export-consent-log` | Export consent log |

## 🔐 Security

- Password hashing (Werkzeug/bcrypt)
- Session-based authentication (30 days)
- CORS enabled
- Rate limiting on OTP
- SQL injection protected (SQLAlchemy ORM)

## 📁 Project Structure

```
westmoney/
├── app.py              # Main application (2800+ lines)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── .github/
│   └── workflows/
│       └── deploy.yml  # CI/CD pipeline
└── README.md
```

## 🏢 Company

**Enterprise Universe GmbH**
- West Money Bau - Smart Home Construction
- Z Automation - Building Automation
- DedSec World AI - AR/VR Security

## 📄 License

Proprietary - © 2025 Enterprise Universe GmbH

---

Made with 💜 by **Ömer Hüseyin Coşkun**
