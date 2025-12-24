"""
West Money OS v12.0 - API INTEGRATION HUB
==========================================
Zentrale Verwaltung aller externen APIs und Datenquellen
Enterprise Universe GmbH - 2025
"""

from flask import Blueprint, render_template_string, jsonify, request, session
import requests
import json
import os
from datetime import datetime, timedelta
from functools import wraps
import hashlib

# ============================================================================
# BLUEPRINT
# ============================================================================
api_hub_bp = Blueprint('api_hub', __name__, url_prefix='/api-hub')

# ============================================================================
# API CONFIGURATION - ALL FREE/FREEMIUM APIs
# ============================================================================
API_CONFIG = {
    # ═══════════════════════════════════════════════════════════════════════
    # 🇩🇪 GERMANY / DACH SPECIFIC
    # ═══════════════════════════════════════════════════════════════════════
    "offene_register": {
        "name": "Offene Register",
        "description": "5M+ Deutsche Firmendaten (Handelsregister)",
        "base_url": "https://db.offeneregister.de/openregister",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "germany",
        "icon": "🇩🇪",
        "endpoints": {
            "search": "/openregister.json?_search={query}",
            "company": "/openregister/{id}.json"
        }
    },
    "govdata": {
        "name": "GovData.de",
        "description": "Deutsches Open Data Portal (120k+ Datensätze)",
        "base_url": "https://ckan.govdata.de/api/3",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "germany",
        "icon": "🏛️",
        "endpoints": {
            "search": "/action/package_search?q={query}",
            "list": "/action/package_list"
        }
    },
    "nominatim": {
        "name": "Nominatim (OSM)",
        "description": "Geocoding & Reverse Geocoding",
        "base_url": "https://nominatim.openstreetmap.org",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "geo",
        "icon": "🗺️",
        "endpoints": {
            "search": "/search?q={query}&format=json",
            "reverse": "/reverse?lat={lat}&lon={lon}&format=json"
        },
        "headers": {"User-Agent": "WestMoneyOS/12.0"}
    },
    "zippopotam": {
        "name": "Zippopotam",
        "description": "PLZ zu Stadt (DE/AT/CH)",
        "base_url": "https://api.zippopotam.us",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "germany",
        "icon": "📮",
        "endpoints": {
            "lookup": "/de/{plz}",
            "lookup_at": "/at/{plz}",
            "lookup_ch": "/ch/{plz}"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🌤️ WEATHER (für Smart Home / LOXONE)
    # ═══════════════════════════════════════════════════════════════════════
    "open_meteo": {
        "name": "Open-Meteo",
        "description": "Wettervorhersage (keine Auth nötig!)",
        "base_url": "https://api.open-meteo.com/v1",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "weather",
        "icon": "🌤️",
        "endpoints": {
            "forecast": "/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,precipitation,windspeed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=Europe/Berlin",
            "historical": "/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&hourly=temperature_2m"
        }
    },
    "openweathermap": {
        "name": "OpenWeatherMap",
        "description": "Wetterdaten weltweit",
        "base_url": "https://api.openweathermap.org/data/2.5",
        "auth_type": "api_key",
        "api_key_param": "appid",
        "free_tier": "1000/day",
        "category": "weather",
        "icon": "⛅",
        "endpoints": {
            "current": "/weather?q={city}&units=metric&lang=de",
            "forecast": "/forecast?q={city}&units=metric&lang=de"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 💰 FINANCE & PAYMENTS
    # ═══════════════════════════════════════════════════════════════════════
    "exchangerate": {
        "name": "ExchangeRate-API",
        "description": "Wechselkurse (1500/Monat frei)",
        "base_url": "https://api.exchangerate-api.com/v4",
        "auth_type": "none",
        "free_tier": "1500/month",
        "category": "finance",
        "icon": "💱",
        "endpoints": {
            "latest": "/latest/{base}",
            "pair": "/latest/{base}"
        }
    },
    "coingecko": {
        "name": "CoinGecko",
        "description": "Kryptowährungen Preise",
        "base_url": "https://api.coingecko.com/api/v3",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "finance",
        "icon": "🪙",
        "endpoints": {
            "price": "/simple/price?ids={coins}&vs_currencies=eur,usd",
            "markets": "/coins/markets?vs_currency=eur&order=market_cap_desc&per_page=100",
            "coin": "/coins/{id}"
        }
    },
    "vatapi": {
        "name": "VIES VAT",
        "description": "EU USt-ID Validierung",
        "base_url": "https://ec.europa.eu/taxation_customs/vies/rest-api",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "finance",
        "icon": "🧾",
        "endpoints": {
            "check": "/check-vat-number"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🤖 AI & MACHINE LEARNING
    # ═══════════════════════════════════════════════════════════════════════
    "gemini": {
        "name": "Google Gemini",
        "description": "AI/LLM (60 req/min FREE)",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "auth_type": "api_key",
        "api_key_param": "key",
        "free_tier": "60/minute",
        "category": "ai",
        "icon": "🤖",
        "endpoints": {
            "generate": "/models/gemini-pro:generateContent"
        }
    },
    "huggingface": {
        "name": "Hugging Face",
        "description": "Open Source AI Models",
        "base_url": "https://api-inference.huggingface.co/models",
        "auth_type": "bearer",
        "free_tier": "rate_limited",
        "category": "ai",
        "icon": "🤗",
        "endpoints": {
            "inference": "/{model}"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📧 EMAIL & COMMUNICATION
    # ═══════════════════════════════════════════════════════════════════════
    "sendgrid": {
        "name": "SendGrid",
        "description": "Transaktions-E-Mails (100/Tag)",
        "base_url": "https://api.sendgrid.com/v3",
        "auth_type": "bearer",
        "free_tier": "100/day",
        "category": "communication",
        "icon": "📧",
        "endpoints": {
            "send": "/mail/send"
        }
    },
    "mailjet": {
        "name": "Mailjet",
        "description": "E-Mail Marketing (6000/Monat)",
        "base_url": "https://api.mailjet.com/v3.1",
        "auth_type": "basic",
        "free_tier": "6000/month",
        "category": "communication",
        "icon": "✉️",
        "endpoints": {
            "send": "/send"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 💼 B2B & BUSINESS DATA
    # ═══════════════════════════════════════════════════════════════════════
    "hunter": {
        "name": "Hunter.io",
        "description": "E-Mail Finder (25/Monat)",
        "base_url": "https://api.hunter.io/v2",
        "auth_type": "api_key",
        "api_key_param": "api_key",
        "free_tier": "25/month",
        "category": "b2b",
        "icon": "🎯",
        "endpoints": {
            "domain": "/domain-search?domain={domain}",
            "verify": "/email-verifier?email={email}",
            "find": "/email-finder?domain={domain}&first_name={first}&last_name={last}"
        }
    },
    "clearbit": {
        "name": "Clearbit Logo",
        "description": "Firmenlogos (unlimited)",
        "base_url": "https://logo.clearbit.com",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "b2b",
        "icon": "🏢",
        "endpoints": {
            "logo": "/{domain}"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🗺️ GEO & LOCATION
    # ═══════════════════════════════════════════════════════════════════════
    "ipapi": {
        "name": "IP-API",
        "description": "IP Geolocation (45/min)",
        "base_url": "http://ip-api.com",
        "auth_type": "none",
        "free_tier": "45/minute",
        "category": "geo",
        "icon": "🌍",
        "endpoints": {
            "lookup": "/json/{ip}",
            "batch": "/batch"
        }
    },
    "ipinfo": {
        "name": "IPinfo",
        "description": "IP Details (50k/Monat)",
        "base_url": "https://ipinfo.io",
        "auth_type": "bearer",
        "free_tier": "50000/month",
        "category": "geo",
        "icon": "📍",
        "endpoints": {
            "lookup": "/{ip}/json"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🔧 UTILITIES
    # ═══════════════════════════════════════════════════════════════════════
    "qrcode": {
        "name": "QR Code Generator",
        "description": "QR Codes erstellen",
        "base_url": "https://api.qrserver.com/v1",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "utility",
        "icon": "📱",
        "endpoints": {
            "create": "/create-qr-code/?size=300x300&data={data}"
        }
    },
    "urlmeta": {
        "name": "URLMeta",
        "description": "URL Metadata Extraction",
        "base_url": "https://api.urlmeta.org",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "utility",
        "icon": "🔗",
        "endpoints": {
            "extract": "/?url={url}"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🎮 GAMING & ENTERTAINMENT (GTzMeta)
    # ═══════════════════════════════════════════════════════════════════════
    "twitch": {
        "name": "Twitch API",
        "description": "Streaming Platform",
        "base_url": "https://api.twitch.tv/helix",
        "auth_type": "oauth",
        "free_tier": "unlimited",
        "category": "gaming",
        "icon": "🎮",
        "endpoints": {
            "users": "/users?login={username}",
            "streams": "/streams?user_login={username}",
            "games": "/games?name={game}"
        }
    },
    "rawg": {
        "name": "RAWG",
        "description": "Video Games Database (20k/Monat)",
        "base_url": "https://api.rawg.io/api",
        "auth_type": "api_key",
        "api_key_param": "key",
        "free_tier": "20000/month",
        "category": "gaming",
        "icon": "🕹️",
        "endpoints": {
            "games": "/games?search={query}",
            "game": "/games/{id}"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📊 ANALYTICS & DATA
    # ═══════════════════════════════════════════════════════════════════════
    "countapi": {
        "name": "CountAPI",
        "description": "Simple Counter Service",
        "base_url": "https://api.countapi.xyz",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "analytics",
        "icon": "📊",
        "endpoints": {
            "hit": "/hit/{namespace}/{key}",
            "get": "/get/{namespace}/{key}",
            "set": "/set/{namespace}/{key}?value={value}"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🔐 SECURITY & AUTH
    # ═══════════════════════════════════════════════════════════════════════
    "haveibeenpwned": {
        "name": "Have I Been Pwned",
        "description": "Breach Check (passwörter)",
        "base_url": "https://api.pwnedpasswords.com",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "security",
        "icon": "🔐",
        "endpoints": {
            "range": "/range/{hash_prefix}"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 📰 NEWS & CONTENT
    # ═══════════════════════════════════════════════════════════════════════
    "newsapi": {
        "name": "NewsAPI",
        "description": "News Headlines",
        "base_url": "https://newsapi.org/v2",
        "auth_type": "api_key",
        "api_key_param": "apiKey",
        "free_tier": "100/day",
        "category": "content",
        "icon": "📰",
        "endpoints": {
            "headlines": "/top-headlines?country=de",
            "everything": "/everything?q={query}&language=de"
        }
    },
    "rss2json": {
        "name": "RSS2JSON",
        "description": "RSS Feed Parser",
        "base_url": "https://api.rss2json.com/v1",
        "auth_type": "none",
        "free_tier": "10000/day",
        "category": "content",
        "icon": "📡",
        "endpoints": {
            "parse": "/api.json?rss_url={url}"
        }
    },
    
    # ═══════════════════════════════════════════════════════════════════════
    # 🖼️ IMAGES & MEDIA
    # ═══════════════════════════════════════════════════════════════════════
    "unsplash": {
        "name": "Unsplash",
        "description": "Kostenlose Fotos",
        "base_url": "https://api.unsplash.com",
        "auth_type": "client_id",
        "free_tier": "50/hour",
        "category": "media",
        "icon": "🖼️",
        "endpoints": {
            "random": "/photos/random",
            "search": "/search/photos?query={query}"
        }
    },
    "placeholder": {
        "name": "Lorem Picsum",
        "description": "Placeholder Images",
        "base_url": "https://picsum.photos",
        "auth_type": "none",
        "free_tier": "unlimited",
        "category": "media",
        "icon": "🎨",
        "endpoints": {
            "random": "/{width}/{height}",
            "specific": "/id/{id}/{width}/{height}"
        }
    },
    "removebg": {
        "name": "Remove.bg",
        "description": "Background Removal (50/Monat)",
        "base_url": "https://api.remove.bg/v1.0",
        "auth_type": "api_key",
        "api_key_header": "X-Api-Key",
        "free_tier": "50/month",
        "category": "media",
        "icon": "✂️",
        "endpoints": {
            "remove": "/removebg"
        }
    }
}

# ============================================================================
# API CREDENTIALS STORAGE (aus Umgebung oder Konfiguration)
# ============================================================================
API_CREDENTIALS = {
    "openweathermap": os.environ.get("OPENWEATHERMAP_API_KEY", ""),
    "gemini": os.environ.get("GEMINI_API_KEY", ""),
    "sendgrid": os.environ.get("SENDGRID_API_KEY", ""),
    "mailjet_key": os.environ.get("MAILJET_API_KEY", ""),
    "mailjet_secret": os.environ.get("MAILJET_SECRET_KEY", ""),
    "hunter": os.environ.get("HUNTER_API_KEY", ""),
    "ipinfo": os.environ.get("IPINFO_TOKEN", ""),
    "twitch_client": os.environ.get("TWITCH_CLIENT_ID", ""),
    "twitch_secret": os.environ.get("TWITCH_CLIENT_SECRET", ""),
    "rawg": os.environ.get("RAWG_API_KEY", ""),
    "newsapi": os.environ.get("NEWSAPI_KEY", ""),
    "unsplash": os.environ.get("UNSPLASH_ACCESS_KEY", ""),
    "removebg": os.environ.get("REMOVEBG_API_KEY", ""),
    "huggingface": os.environ.get("HUGGINGFACE_TOKEN", ""),
    "hubspot": os.environ.get("HUBSPOT_API_KEY", ""),
    "stripe": os.environ.get("STRIPE_SECRET_KEY", ""),
    "whatsapp_token": os.environ.get("WHATSAPP_TOKEN", ""),
    "whatsapp_phone_id": os.environ.get("WHATSAPP_PHONE_ID", ""),
}

# ============================================================================
# API HELPER CLASS
# ============================================================================
class APIConnector:
    """Universal API Connector for all integrated APIs"""
    
    def __init__(self, api_name):
        if api_name not in API_CONFIG:
            raise ValueError(f"Unknown API: {api_name}")
        self.config = API_CONFIG[api_name]
        self.name = api_name
        
    def _get_headers(self):
        """Build request headers based on auth type"""
        headers = {"Content-Type": "application/json"}
        
        # Add custom headers if specified
        if "headers" in self.config:
            headers.update(self.config["headers"])
            
        auth_type = self.config.get("auth_type", "none")
        
        if auth_type == "bearer":
            token = API_CREDENTIALS.get(self.name, "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
                
        elif auth_type == "api_key_header":
            key = API_CREDENTIALS.get(self.name, "")
            header_name = self.config.get("api_key_header", "X-Api-Key")
            if key:
                headers[header_name] = key
                
        return headers
    
    def _build_url(self, endpoint_name, **params):
        """Build full URL with parameters"""
        base = self.config["base_url"]
        endpoint_template = self.config["endpoints"].get(endpoint_name, "")
        endpoint = endpoint_template.format(**params) if params else endpoint_template
        
        url = f"{base}{endpoint}"
        
        # Add API key as query parameter if needed
        auth_type = self.config.get("auth_type", "none")
        if auth_type == "api_key":
            key = API_CREDENTIALS.get(self.name, "")
            param_name = self.config.get("api_key_param", "api_key")
            if key:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}{param_name}={key}"
                
        return url
    
    def get(self, endpoint_name, **params):
        """Make GET request to API"""
        url = self._build_url(endpoint_name, **params)
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "api": self.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "api": self.name
            }
    
    def post(self, endpoint_name, data=None, **params):
        """Make POST request to API"""
        url = self._build_url(endpoint_name, **params)
        headers = self._get_headers()
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            return {
                "success": response.status_code in [200, 201, 202],
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "api": self.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "api": self.name
            }

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_weather(lat=50.1109, lon=8.6821):
    """Get weather for location (default: Frankfurt)"""
    api = APIConnector("open_meteo")
    return api.get("forecast", lat=lat, lon=lon)

def search_german_companies(query):
    """Search German company register"""
    api = APIConnector("offene_register")
    return api.get("search", query=query)

def geocode_address(address):
    """Convert address to coordinates"""
    api = APIConnector("nominatim")
    return api.get("search", query=address)

def get_plz_info(plz, country="de"):
    """Get city info from postal code"""
    api = APIConnector("zippopotam")
    endpoint = f"lookup_{country}" if country != "de" else "lookup"
    return api.get(endpoint, plz=plz)

def get_exchange_rate(base="EUR"):
    """Get current exchange rates"""
    api = APIConnector("exchangerate")
    return api.get("latest", base=base)

def get_crypto_prices(coins="bitcoin,ethereum"):
    """Get cryptocurrency prices"""
    api = APIConnector("coingecko")
    return api.get("price", coins=coins)

def get_ip_location(ip=None):
    """Get location from IP address"""
    api = APIConnector("ipapi")
    return api.get("lookup", ip=ip or "")

def generate_qr_code(data):
    """Generate QR code URL"""
    return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={data}"

def get_company_logo(domain):
    """Get company logo from domain"""
    return f"https://logo.clearbit.com/{domain}"

def check_password_breach(password):
    """Check if password was in data breach (k-anonymity)"""
    import hashlib
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]
    
    api = APIConnector("haveibeenpwned")
    result = api.get("range", hash_prefix=prefix)
    
    if result["success"]:
        hashes = result["data"].split("\n")
        for h in hashes:
            if h.startswith(suffix):
                count = int(h.split(":")[1])
                return {"breached": True, "count": count}
    return {"breached": False, "count": 0}

# ============================================================================
# HTML TEMPLATE - API HUB DASHBOARD
# ============================================================================
API_HUB_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔌 API Integration Hub - West Money OS</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Rajdhani', sans-serif;
            background: linear-gradient(135deg, #0a0a15 0%, #1a0a2e 50%, #0a1628 100%);
            min-height: 100vh;
            color: #ffffff;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid rgba(255, 0, 255, 0.3);
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.5rem;
            background: linear-gradient(90deg, #ff00ff, #00ffff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { filter: drop-shadow(0 0 5px #ff00ff); }
            to { filter: drop-shadow(0 0 20px #00ffff); }
        }
        
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(145deg, rgba(255, 0, 255, 0.1), rgba(0, 255, 255, 0.05));
            border: 1px solid rgba(255, 0, 255, 0.3);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        }
        
        .stat-card .number {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.5rem;
            color: #00ffff;
        }
        
        .stat-card .label {
            color: #888;
            font-size: 0.9rem;
        }
        
        .category-section {
            margin-bottom: 40px;
        }
        
        .category-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.5rem;
            color: #ff00ff;
            margin-bottom: 20px;
            padding-left: 10px;
            border-left: 4px solid #00ffff;
        }
        
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .api-card {
            background: linear-gradient(145deg, rgba(20, 20, 40, 0.9), rgba(30, 15, 45, 0.9));
            border: 1px solid rgba(255, 0, 255, 0.2);
            border-radius: 15px;
            padding: 20px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .api-card:hover {
            border-color: #00ffff;
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0, 255, 255, 0.2);
        }
        
        .api-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #ff00ff, #00ffff);
        }
        
        .api-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .api-icon {
            font-size: 2rem;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 0, 255, 0.1);
            border-radius: 10px;
        }
        
        .api-name {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.1rem;
            color: #fff;
        }
        
        .api-description {
            color: #aaa;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }
        
        .api-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .free-tier {
            background: linear-gradient(90deg, #00ff88, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-size: 0.85rem;
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .status-active {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
            border: 1px solid #00ff88;
        }
        
        .status-config {
            background: rgba(255, 170, 0, 0.2);
            color: #ffaa00;
            border: 1px solid #ffaa00;
        }
        
        .status-free {
            background: rgba(0, 255, 255, 0.2);
            color: #00ffff;
            border: 1px solid #00ffff;
        }
        
        .test-btn {
            background: linear-gradient(90deg, #ff00ff, #00ffff);
            border: none;
            padding: 8px 20px;
            border-radius: 20px;
            color: #000;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .test-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(255, 0, 255, 0.4);
        }
        
        .quick-test {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
        }
        
        .quick-test h3 {
            font-family: 'Orbitron', sans-serif;
            color: #00ffff;
            margin-bottom: 20px;
        }
        
        .test-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .test-item {
            background: rgba(255, 0, 255, 0.05);
            border: 1px solid rgba(255, 0, 255, 0.2);
            border-radius: 10px;
            padding: 15px;
        }
        
        .test-item label {
            display: block;
            color: #888;
            font-size: 0.8rem;
            margin-bottom: 5px;
        }
        
        .test-item input, .test-item select {
            width: 100%;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 0, 255, 0.3);
            border-radius: 8px;
            padding: 10px;
            color: #fff;
            font-size: 1rem;
        }
        
        .result-box {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .result-box pre {
            color: #00ffff;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
            word-break: break-all;
        }
        
        .nav-back {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 0, 255, 0.2);
            border: 1px solid #ff00ff;
            padding: 10px 20px;
            border-radius: 25px;
            color: #fff;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .nav-back:hover {
            background: #ff00ff;
            color: #000;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255, 0, 255, 0.3);
            border-top-color: #00ffff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <a href="/dashboard" class="nav-back">← Dashboard</a>
    
    <div class="container">
        <div class="header">
            <h1>🔌 API INTEGRATION HUB</h1>
            <p style="color: #888; margin-top: 10px;">200+ APIs • Kostenlos & Premium • Sofort einsatzbereit</p>
        </div>
        
        <div class="stats-bar">
            <div class="stat-card">
                <div class="number">{{ total_apis }}</div>
                <div class="label">Integrierte APIs</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ free_apis }}</div>
                <div class="label">100% Kostenlos</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ categories|length }}</div>
                <div class="label">Kategorien</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ configured_apis }}</div>
                <div class="label">Konfiguriert</div>
            </div>
        </div>
        
        <!-- Quick Test Section -->
        <div class="quick-test">
            <h3>⚡ QUICK API TEST</h3>
            <div class="test-grid">
                <div class="test-item">
                    <label>API auswählen</label>
                    <select id="testApi">
                        <option value="open_meteo">🌤️ Wetter (Open-Meteo)</option>
                        <option value="offene_register">🇩🇪 Firmendaten (OffeneRegister)</option>
                        <option value="nominatim">🗺️ Geocoding (Nominatim)</option>
                        <option value="zippopotam">📮 PLZ Lookup</option>
                        <option value="exchangerate">💱 Wechselkurse</option>
                        <option value="coingecko">🪙 Crypto Preise</option>
                        <option value="ipapi">🌍 IP Geolocation</option>
                        <option value="clearbit">🏢 Company Logo</option>
                    </select>
                </div>
                <div class="test-item">
                    <label>Parameter</label>
                    <input type="text" id="testParam" placeholder="z.B. Frankfurt, 60311, bitcoin">
                </div>
                <div class="test-item" style="display: flex; align-items: flex-end;">
                    <button class="test-btn" onclick="testApi()" style="width: 100%;">🚀 TEST</button>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 10px; color: #888;">API wird aufgerufen...</p>
            </div>
            
            <div class="result-box" id="resultBox" style="display: none;">
                <pre id="resultData"></pre>
            </div>
        </div>
        
        <!-- API Categories -->
        {% for category, apis in categories.items() %}
        <div class="category-section">
            <h2 class="category-title">{{ category_icons.get(category, '📦') }} {{ category|upper }}</h2>
            <div class="api-grid">
                {% for api_id, api in apis.items() %}
                <div class="api-card">
                    <div class="api-header">
                        <div class="api-icon">{{ api.icon }}</div>
                        <div>
                            <div class="api-name">{{ api.name }}</div>
                        </div>
                    </div>
                    <div class="api-description">{{ api.description }}</div>
                    <div class="api-meta">
                        <span class="free-tier">{{ api.free_tier }}</span>
                        {% if api.auth_type == 'none' %}
                        <span class="status-badge status-free">NO AUTH</span>
                        {% elif credentials.get(api_id) %}
                        <span class="status-badge status-active">AKTIV</span>
                        {% else %}
                        <span class="status-badge status-config">CONFIG</span>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <script>
        async function testApi() {
            const api = document.getElementById('testApi').value;
            const param = document.getElementById('testParam').value;
            const loading = document.getElementById('loading');
            const resultBox = document.getElementById('resultBox');
            const resultData = document.getElementById('resultData');
            
            loading.classList.add('active');
            resultBox.style.display = 'none';
            
            try {
                const response = await fetch('/api-hub/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({api: api, param: param})
                });
                const data = await response.json();
                
                resultData.textContent = JSON.stringify(data, null, 2);
                resultBox.style.display = 'block';
            } catch (error) {
                resultData.textContent = 'Error: ' + error.message;
                resultBox.style.display = 'block';
            }
            
            loading.classList.remove('active');
        }
    </script>
</body>
</html>
"""

# ============================================================================
# ROUTES
# ============================================================================

@api_hub_bp.route('/')
def api_hub_dashboard():
    """Main API Hub Dashboard"""
    # Group APIs by category
    categories = {}
    for api_id, api in API_CONFIG.items():
        cat = api.get("category", "other")
        if cat not in categories:
            categories[cat] = {}
        categories[cat][api_id] = api
    
    # Count stats
    total_apis = len(API_CONFIG)
    free_apis = len([a for a in API_CONFIG.values() if a.get("auth_type") == "none"])
    configured_apis = len([k for k, v in API_CREDENTIALS.items() if v])
    
    category_icons = {
        "germany": "🇩🇪",
        "weather": "🌤️",
        "finance": "💰",
        "ai": "🤖",
        "communication": "📱",
        "b2b": "💼",
        "geo": "🗺️",
        "utility": "🔧",
        "gaming": "🎮",
        "analytics": "📊",
        "security": "🔐",
        "content": "📰",
        "media": "🖼️"
    }
    
    return render_template_string(
        API_HUB_HTML,
        categories=categories,
        category_icons=category_icons,
        total_apis=total_apis,
        free_apis=free_apis,
        configured_apis=configured_apis,
        credentials=API_CREDENTIALS
    )

@api_hub_bp.route('/test', methods=['POST'])
def test_api():
    """Test an API endpoint"""
    data = request.json
    api_name = data.get('api')
    param = data.get('param', '')
    
    try:
        if api_name == "open_meteo":
            # Default to Frankfurt if no param
            result = get_weather()
            
        elif api_name == "offene_register":
            result = search_german_companies(param or "GmbH")
            
        elif api_name == "nominatim":
            result = geocode_address(param or "Frankfurt am Main")
            
        elif api_name == "zippopotam":
            result = get_plz_info(param or "60311")
            
        elif api_name == "exchangerate":
            result = get_exchange_rate(param or "EUR")
            
        elif api_name == "coingecko":
            result = get_crypto_prices(param or "bitcoin,ethereum")
            
        elif api_name == "ipapi":
            result = get_ip_location(param if param else None)
            
        elif api_name == "clearbit":
            domain = param or "apple.com"
            result = {
                "success": True,
                "logo_url": get_company_logo(domain),
                "domain": domain
            }
            
        else:
            result = {"error": "Unknown API"}
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)})

@api_hub_bp.route('/api/<api_name>/<endpoint>', methods=['GET', 'POST'])
def call_api(api_name, endpoint):
    """Generic API caller"""
    try:
        api = APIConnector(api_name)
        params = request.args.to_dict() if request.method == 'GET' else request.json or {}
        
        if request.method == 'GET':
            result = api.get(endpoint, **params)
        else:
            result = api.post(endpoint, data=params)
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============================================================================
# SPECIALIZED ENDPOINTS
# ============================================================================

@api_hub_bp.route('/weather')
def weather_endpoint():
    """Get weather data"""
    lat = request.args.get('lat', 50.1109, type=float)
    lon = request.args.get('lon', 8.6821, type=float)
    return jsonify(get_weather(lat, lon))

@api_hub_bp.route('/companies/search')
def company_search():
    """Search German companies"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Query parameter 'q' required"}), 400
    return jsonify(search_german_companies(query))

@api_hub_bp.route('/geocode')
def geocode_endpoint():
    """Geocode an address"""
    address = request.args.get('address', '')
    if not address:
        return jsonify({"error": "Address parameter required"}), 400
    return jsonify(geocode_address(address))

@api_hub_bp.route('/plz/<plz>')
def plz_lookup(plz):
    """Lookup postal code"""
    country = request.args.get('country', 'de')
    return jsonify(get_plz_info(plz, country))

@api_hub_bp.route('/exchange-rate')
def exchange_rate_endpoint():
    """Get exchange rates"""
    base = request.args.get('base', 'EUR')
    return jsonify(get_exchange_rate(base))

@api_hub_bp.route('/crypto')
def crypto_endpoint():
    """Get crypto prices"""
    coins = request.args.get('coins', 'bitcoin,ethereum')
    return jsonify(get_crypto_prices(coins))

@api_hub_bp.route('/qrcode')
def qrcode_endpoint():
    """Generate QR code"""
    data = request.args.get('data', '')
    if not data:
        return jsonify({"error": "Data parameter required"}), 400
    return jsonify({"qr_url": generate_qr_code(data)})

@api_hub_bp.route('/logo/<domain>')
def logo_endpoint(domain):
    """Get company logo"""
    return jsonify({"logo_url": get_company_logo(domain)})

@api_hub_bp.route('/password-check', methods=['POST'])
def password_check():
    """Check if password was breached"""
    data = request.json
    password = data.get('password', '')
    if not password:
        return jsonify({"error": "Password required"}), 400
    return jsonify(check_password_breach(password))

@api_hub_bp.route('/config')
def api_config():
    """Get all API configurations (without credentials)"""
    safe_config = {}
    for api_id, api in API_CONFIG.items():
        safe_config[api_id] = {
            "name": api["name"],
            "description": api["description"],
            "category": api.get("category"),
            "free_tier": api.get("free_tier"),
            "auth_type": api.get("auth_type"),
            "icon": api.get("icon"),
            "configured": bool(API_CREDENTIALS.get(api_id))
        }
    return jsonify(safe_config)

# ============================================================================
# EXPORT
# ============================================================================
__all__ = [
    'api_hub_bp',
    'APIConnector',
    'API_CONFIG',
    'get_weather',
    'search_german_companies',
    'geocode_address',
    'get_plz_info',
    'get_exchange_rate',
    'get_crypto_prices',
    'get_ip_location',
    'generate_qr_code',
    'get_company_logo',
    'check_password_breach'
]
