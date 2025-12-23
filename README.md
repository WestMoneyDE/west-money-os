# 🏛️ West Money OS - Handelsregister Live

**Echte Handelsregister-Daten** für deutsche Unternehmen via OpenCorporates API.

## 🚀 Deploy auf Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

1. Fork dieses Repository
2. Verbinde mit Railway
3. Domain hinzufügen (z.B. west-money.com)
4. Fertig!

## 🔧 Lokal starten

```bash
pip install -r requirements.txt
python app.py
# Öffne http://localhost:5000
```

## 📊 API Endpoints

| Endpoint | Beschreibung |
|----------|-------------|
| `GET /` | Frontend |
| `GET /api/hr/search?q=FIRMA` | Firmensuche |
| `GET /api/hr/company/ID` | Firmendetails |
| `GET /api/hr/officers/search?q=NAME` | Personensuche |
| `GET /api/health` | Health Check |

## 🔑 Umgebungsvariablen

| Variable | Beschreibung | Required |
|----------|-------------|----------|
| `PORT` | Server Port (default: 5000) | Nein |
| `OPENCORPORATES_API_KEY` | API Key für mehr Requests | Nein |

## 📝 Beispiel-Suchen

- Deutsche Bahn
- Siemens AG
- BMW
- Volkswagen
- SAP SE
- Allianz

## 📄 Lizenz

MIT License - Daten unter OpenCorporates Lizenz

---

**West Money OS** © 2025 Enterprise Universe GmbH
