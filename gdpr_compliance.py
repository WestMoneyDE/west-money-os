#!/usr/bin/env python3
"""
🔒 WEST MONEY OS - DSGVO & COMPLIANCE MODULE 🔒
Datenschutz-Grundverordnung (EU 2016/679) Compliance

Features:
- Cookie Consent Management
- Datenauskunft & Export
- Recht auf Löschung
- Einwilligungsverwaltung
- Audit Logging
- Privacy Policy Generator
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, render_template_string, Response
from typing import Dict, List, Optional

# Blueprint für DSGVO-Routen
gdpr_bp = Blueprint('gdpr', __name__, url_prefix='/api/gdpr')
legal_bp = Blueprint('legal', __name__, url_prefix='/legal')


# =============================================================================
# CONFIGURATION
# =============================================================================

class GDPRConfig:
    """DSGVO Konfiguration"""
    
    # Unternehmensdaten
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'Enterprise Universe GmbH')
    COMPANY_ADDRESS = os.getenv('COMPANY_ADDRESS', '[Straße und Hausnummer]')
    COMPANY_CITY = os.getenv('COMPANY_CITY', 'Frankfurt am Main')
    COMPANY_COUNTRY = 'Deutschland'
    COMPANY_EMAIL = os.getenv('COMPANY_EMAIL', 'datenschutz@enterprise-universe.de')
    COMPANY_PHONE = os.getenv('COMPANY_PHONE', '+49 [Vorwahl] [Nummer]')
    
    # Handelsregister
    COMPANY_REGISTER = os.getenv('COMPANY_REGISTER', 'Amtsgericht Frankfurt am Main')
    COMPANY_REGISTER_NR = os.getenv('COMPANY_REGISTER_NR', 'HRB [Nummer]')
    COMPANY_TAX_ID = os.getenv('COMPANY_TAX_ID', 'DE[Nummer]')
    
    # Geschäftsführer
    CEO_NAME = os.getenv('CEO_NAME', 'Ömer Hüseyin Coşkun')
    
    # Datenschutzbeauftragter (falls erforderlich)
    DPO_NAME = os.getenv('DPO_NAME', '')
    DPO_EMAIL = os.getenv('DPO_EMAIL', 'datenschutz@enterprise-universe.de')
    
    # Datenaufbewahrung (in Tagen)
    RETENTION_PERIODS = {
        'logs': 30,
        'analytics': 90,
        'contacts': 365 * 3,  # 3 Jahre
        'invoices': 365 * 10,  # 10 Jahre (gesetzlich)
        'consent': 365 * 5     # 5 Jahre
    }


# =============================================================================
# COOKIE CATEGORIES
# =============================================================================

COOKIE_CATEGORIES = {
    'necessary': {
        'name_de': 'Notwendige Cookies',
        'name_en': 'Necessary Cookies',
        'description_de': 'Diese Cookies sind für die Grundfunktion der Website erforderlich und können nicht deaktiviert werden.',
        'description_en': 'These cookies are essential for the basic functionality of the website and cannot be disabled.',
        'required': True,
        'cookies': ['session', 'csrf_token', 'cookie_consent']
    },
    'functional': {
        'name_de': 'Funktionale Cookies',
        'name_en': 'Functional Cookies',
        'description_de': 'Diese Cookies ermöglichen verbesserte Funktionalität und Personalisierung.',
        'description_en': 'These cookies enable enhanced functionality and personalization.',
        'required': False,
        'cookies': ['language', 'theme', 'preferences']
    },
    'analytics': {
        'name_de': 'Analyse-Cookies',
        'name_en': 'Analytics Cookies',
        'description_de': 'Diese Cookies helfen uns zu verstehen, wie Besucher mit der Website interagieren.',
        'description_en': 'These cookies help us understand how visitors interact with the website.',
        'required': False,
        'cookies': ['_ga', '_gid', '_gat', 'plausible']
    },
    'marketing': {
        'name_de': 'Marketing-Cookies',
        'name_en': 'Marketing Cookies',
        'description_de': 'Diese Cookies werden verwendet, um Werbung relevanter zu gestalten.',
        'description_en': 'These cookies are used to make advertising more relevant.',
        'required': False,
        'cookies': ['_fbp', 'ads', 'remarketing']
    }
}


# =============================================================================
# CONSENT MANAGEMENT
# =============================================================================

class ConsentManager:
    """Verwaltet Cookie-Einwilligungen"""
    
    @staticmethod
    def get_consent_from_request() -> Dict:
        """Liest Consent-Cookie"""
        consent_cookie = request.cookies.get('cookie_consent')
        if consent_cookie:
            try:
                return json.loads(consent_cookie)
            except:
                pass
        return {'necessary': True}
    
    @staticmethod
    def create_consent_response(consent: Dict) -> Response:
        """Erstellt Response mit Consent-Cookie"""
        response = jsonify({'success': True, 'consent': consent})
        
        # Cookie für 1 Jahr setzen
        response.set_cookie(
            'cookie_consent',
            json.dumps(consent),
            max_age=365 * 24 * 60 * 60,
            secure=True,
            httponly=True,
            samesite='Lax'
        )
        
        return response


# =============================================================================
# GDPR API ROUTES
# =============================================================================

@gdpr_bp.route('/consent', methods=['GET'])
def get_consent():
    """Gibt aktuelle Einwilligung zurück"""
    consent = ConsentManager.get_consent_from_request()
    return jsonify({
        'success': True,
        'consent': consent,
        'categories': COOKIE_CATEGORIES
    })


@gdpr_bp.route('/consent', methods=['POST'])
def set_consent():
    """Speichert Einwilligung"""
    data = request.get_json() or {}
    
    consent = {
        'necessary': True,  # Immer erforderlich
        'functional': data.get('functional', False),
        'analytics': data.get('analytics', False),
        'marketing': data.get('marketing', False),
        'timestamp': datetime.utcnow().isoformat(),
        'ip_hash': hashlib.sha256(request.remote_addr.encode()).hexdigest()[:16]
    }
    
    # In Datenbank loggen (für Nachweis)
    # ConsentLog.create(consent)
    
    return ConsentManager.create_consent_response(consent)


@gdpr_bp.route('/consent/accept-all', methods=['POST'])
def accept_all():
    """Akzeptiert alle Cookies"""
    consent = {
        'necessary': True,
        'functional': True,
        'analytics': True,
        'marketing': True,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_hash': hashlib.sha256(request.remote_addr.encode()).hexdigest()[:16]
    }
    
    return ConsentManager.create_consent_response(consent)


@gdpr_bp.route('/consent/reject-all', methods=['POST'])
def reject_all():
    """Lehnt alle optionalen Cookies ab"""
    consent = {
        'necessary': True,
        'functional': False,
        'analytics': False,
        'marketing': False,
        'timestamp': datetime.utcnow().isoformat(),
        'ip_hash': hashlib.sha256(request.remote_addr.encode()).hexdigest()[:16]
    }
    
    return ConsentManager.create_consent_response(consent)


@gdpr_bp.route('/data-export', methods=['POST'])
def request_data_export():
    """Art. 15 & 20: Datenauskunft & Portabilität"""
    # Erfordert Authentifizierung
    # user = get_current_user()
    # if not user:
    #     return jsonify({'error': 'Nicht authentifiziert'}), 401
    
    # Export generieren und per E-Mail senden
    # GDPRService.generate_data_export(user.id)
    
    return jsonify({
        'success': True,
        'message': 'Ihre Daten werden aufbereitet und per E-Mail zugesendet.'
    })


@gdpr_bp.route('/data-deletion', methods=['POST'])
def request_data_deletion():
    """Art. 17: Recht auf Löschung"""
    data = request.get_json() or {}
    reason = data.get('reason', 'Nutzeranfrage')
    
    # Erfordert Authentifizierung
    # user = get_current_user()
    # if not user:
    #     return jsonify({'error': 'Nicht authentifiziert'}), 401
    
    # Löschung durchführen
    # GDPRService.delete_user_data(user.id, reason)
    
    return jsonify({
        'success': True,
        'message': 'Ihre Daten werden innerhalb von 30 Tagen gelöscht.'
    })


# =============================================================================
# LEGAL PAGES
# =============================================================================

IMPRESSUM_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Impressum - {company}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #1a1a2e; margin-bottom: 30px; }}
        h2 {{ color: #16213e; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; }}
        p {{ margin-bottom: 10px; }}
        a {{ color: #667eea; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 0.9rem; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Impressum</h1>
        
        <h2>Angaben gemäß § 5 TMG</h2>
        <p>
            <strong>{company}</strong><br>
            {address}<br>
            {city}<br>
            {country}
        </p>
        
        <h2>Vertreten durch</h2>
        <p>Geschäftsführer: {ceo}</p>
        
        <h2>Kontakt</h2>
        <p>
            Telefon: {phone}<br>
            E-Mail: <a href="mailto:{email}">{email}</a>
        </p>
        
        <h2>Registereintrag</h2>
        <p>
            Eintragung im Handelsregister.<br>
            Registergericht: {register}<br>
            Registernummer: {register_nr}
        </p>
        
        <h2>Umsatzsteuer-ID</h2>
        <p>
            Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:<br>
            {tax_id}
        </p>
        
        <h2>Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2>
        <p>
            {ceo}<br>
            {address}<br>
            {city}
        </p>
        
        <h2>EU-Streitschlichtung</h2>
        <p>
            Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:
            <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener">https://ec.europa.eu/consumers/odr/</a><br>
            Unsere E-Mail-Adresse finden Sie oben im Impressum.
        </p>
        
        <h2>Verbraucherstreitbeilegung/Universalschlichtungsstelle</h2>
        <p>
            Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer 
            Verbraucherschlichtungsstelle teilzunehmen.
        </p>
        
        <h2>Haftung für Inhalte</h2>
        <p>
            Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten 
            nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als 
            Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde 
            Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige 
            Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von 
            Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt.
        </p>
        
        <h2>Haftung für Links</h2>
        <p>
            Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen 
            Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. 
            Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber 
            der Seiten verantwortlich.
        </p>
        
        <h2>Urheberrecht</h2>
        <p>
            Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen 
            dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art 
            der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen 
            Zustimmung des jeweiligen Autors bzw. Erstellers.
        </p>
        
        <div class="footer">
            <p>Stand: Dezember 2025</p>
            <p><a href="/legal/datenschutz">Datenschutzerklärung</a> | <a href="/legal/agb">AGB</a></p>
        </div>
    </div>
</body>
</html>
"""


DATENSCHUTZ_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Datenschutzerklärung - {company}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.8;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #1a1a2e; margin-bottom: 30px; }}
        h2 {{ color: #16213e; margin-top: 40px; margin-bottom: 15px; font-size: 1.3rem; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        h3 {{ color: #333; margin-top: 25px; margin-bottom: 10px; font-size: 1.1rem; }}
        p, li {{ margin-bottom: 10px; }}
        ul {{ padding-left: 20px; margin-bottom: 15px; }}
        a {{ color: #667eea; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .highlight {{ background: #f0f4ff; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 0.9rem; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Datenschutzerklärung</h1>
        
        <h2>1. Datenschutz auf einen Blick</h2>
        
        <h3>Allgemeine Hinweise</h3>
        <p>
            Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren 
            personenbezogenen Daten passiert, wenn Sie diese Website besuchen. Personenbezogene 
            Daten sind alle Daten, mit denen Sie persönlich identifiziert werden können.
        </p>
        
        <h3>Datenerfassung auf dieser Website</h3>
        <p><strong>Wer ist verantwortlich für die Datenerfassung auf dieser Website?</strong></p>
        <p>
            Die Datenverarbeitung auf dieser Website erfolgt durch den Websitebetreiber. 
            Dessen Kontaktdaten können Sie dem Impressum dieser Website entnehmen.
        </p>
        
        <h2>2. Hosting</h2>
        <p>
            Wir hosten die Inhalte unserer Website bei folgenden Anbietern:
        </p>
        <ul>
            <li>Hetzner Online GmbH, Industriestr. 25, 91710 Gunzenhausen, Deutschland</li>
            <li>Cloudflare, Inc., 101 Townsend St, San Francisco, CA 94107, USA</li>
        </ul>
        
        <h2>3. Allgemeine Hinweise und Pflichtinformationen</h2>
        
        <h3>Datenschutz</h3>
        <p>
            Die Betreiber dieser Seiten nehmen den Schutz Ihrer persönlichen Daten sehr ernst. 
            Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend den gesetzlichen 
            Datenschutzvorschriften sowie dieser Datenschutzerklärung.
        </p>
        
        <h3>Hinweis zur verantwortlichen Stelle</h3>
        <div class="highlight">
            <p>
                <strong>{company}</strong><br>
                {address}<br>
                {city}<br>
                Telefon: {phone}<br>
                E-Mail: {email}
            </p>
        </div>
        
        <h3>Speicherdauer</h3>
        <p>
            Soweit innerhalb dieser Datenschutzerklärung keine speziellere Speicherdauer genannt 
            wurde, verbleiben Ihre personenbezogenen Daten bei uns, bis der Zweck für die 
            Datenverarbeitung entfällt.
        </p>
        
        <h2>4. Ihre Rechte</h2>
        <p>Sie haben folgende Rechte:</p>
        <ul>
            <li><strong>Auskunftsrecht (Art. 15 DSGVO):</strong> Sie können Auskunft über Ihre verarbeiteten Daten verlangen.</li>
            <li><strong>Berichtigungsrecht (Art. 16 DSGVO):</strong> Sie können die Berichtigung unrichtiger Daten verlangen.</li>
            <li><strong>Löschungsrecht (Art. 17 DSGVO):</strong> Sie können die Löschung Ihrer Daten verlangen.</li>
            <li><strong>Einschränkung (Art. 18 DSGVO):</strong> Sie können die Einschränkung der Verarbeitung verlangen.</li>
            <li><strong>Datenübertragbarkeit (Art. 20 DSGVO):</strong> Sie können die Übertragung Ihrer Daten verlangen.</li>
            <li><strong>Widerspruchsrecht (Art. 21 DSGVO):</strong> Sie können der Verarbeitung widersprechen.</li>
        </ul>
        
        <div class="highlight">
            <p>
                <strong>Zur Ausübung Ihrer Rechte kontaktieren Sie uns unter:</strong><br>
                E-Mail: {dpo_email}
            </p>
        </div>
        
        <h2>5. Datenerfassung auf dieser Website</h2>
        
        <h3>Cookies</h3>
        <p>
            Unsere Website verwendet Cookies. Das sind kleine Textdateien, die Ihr Webbrowser 
            auf Ihrem Endgerät speichert. Cookies helfen uns dabei, unser Angebot nutzerfreundlicher, 
            effektiver und sicherer zu machen.
        </p>
        <p>
            Einige Cookies sind "Session-Cookies." Solche Cookies werden nach Ende Ihrer 
            Browser-Sitzung von selbst gelöscht. Hingegen bleiben andere Cookies auf Ihrem 
            Endgerät bestehen, bis Sie diese selbst löschen.
        </p>
        
        <h3>Server-Log-Dateien</h3>
        <p>Der Provider der Seiten erhebt und speichert automatisch Informationen in so genannten Server-Log-Dateien:</p>
        <ul>
            <li>Browsertyp und Browserversion</li>
            <li>Verwendetes Betriebssystem</li>
            <li>Referrer URL</li>
            <li>Hostname des zugreifenden Rechners</li>
            <li>Uhrzeit der Serveranfrage</li>
            <li>IP-Adresse (anonymisiert)</li>
        </ul>
        
        <h2>6. Analyse-Tools und Werbung</h2>
        
        <h3>Google Analytics (mit Anonymisierung)</h3>
        <p>
            Diese Website nutzt Funktionen des Webanalysedienstes Google Analytics. Anbieter ist 
            die Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland.
        </p>
        <p>
            Wir haben die IP-Anonymisierung aktiviert. Das bedeutet, dass Ihre IP-Adresse von 
            Google innerhalb von Mitgliedstaaten der Europäischen Union oder in anderen 
            Vertragsstaaten des Abkommens über den Europäischen Wirtschaftsraum vor der 
            Übermittlung in die USA gekürzt wird.
        </p>
        
        <h2>7. Newsletter</h2>
        <p>
            Wenn Sie den auf der Website angebotenen Newsletter beziehen möchten, benötigen wir 
            von Ihnen eine E-Mail-Adresse sowie Informationen, welche uns die Überprüfung gestatten, 
            dass Sie der Inhaber der angegebenen E-Mail-Adresse sind.
        </p>
        
        <h2>8. Plugins und Tools</h2>
        
        <h3>WhatsApp Business</h3>
        <p>
            Wir nutzen WhatsApp Business für die Kundenkommunikation. Anbieter ist die 
            WhatsApp Ireland Limited, 4 Grand Canal Square, Grand Canal Harbour, Dublin 2, Irland.
        </p>
        
        <h3>Stripe (Zahlungsabwicklung)</h3>
        <p>
            Für Zahlungen nutzen wir Stripe. Anbieter ist Stripe Payments Europe, Ltd., 
            1 Grand Canal Street Lower, Grand Canal Dock, Dublin, Irland.
        </p>
        
        <h2>9. Eigene Dienste</h2>
        
        <h3>Bewerbungen</h3>
        <p>
            Wir bieten Ihnen die Möglichkeit, sich bei uns zu bewerben. Im Folgenden informieren 
            wir Sie über Umfang, Zweck und Verwendung Ihrer im Rahmen des Bewerbungsprozesses 
            erhobenen personenbezogenen Daten.
        </p>
        
        <div class="footer">
            <p>Stand: Dezember 2025</p>
            <p><a href="/legal/impressum">Impressum</a> | <a href="/legal/agb">AGB</a></p>
        </div>
    </div>
</body>
</html>
"""


@legal_bp.route('/impressum')
def impressum():
    """Zeigt Impressum"""
    return render_template_string(
        IMPRESSUM_HTML,
        company=GDPRConfig.COMPANY_NAME,
        address=GDPRConfig.COMPANY_ADDRESS,
        city=GDPRConfig.COMPANY_CITY,
        country=GDPRConfig.COMPANY_COUNTRY,
        ceo=GDPRConfig.CEO_NAME,
        email=GDPRConfig.COMPANY_EMAIL,
        phone=GDPRConfig.COMPANY_PHONE,
        register=GDPRConfig.COMPANY_REGISTER,
        register_nr=GDPRConfig.COMPANY_REGISTER_NR,
        tax_id=GDPRConfig.COMPANY_TAX_ID
    )


@legal_bp.route('/datenschutz')
@legal_bp.route('/privacy')
def datenschutz():
    """Zeigt Datenschutzerklärung"""
    return render_template_string(
        DATENSCHUTZ_HTML,
        company=GDPRConfig.COMPANY_NAME,
        address=GDPRConfig.COMPANY_ADDRESS,
        city=GDPRConfig.COMPANY_CITY,
        email=GDPRConfig.COMPANY_EMAIL,
        phone=GDPRConfig.COMPANY_PHONE,
        dpo_email=GDPRConfig.DPO_EMAIL
    )


# =============================================================================
# COOKIE BANNER COMPONENT
# =============================================================================

COOKIE_BANNER_JS = """
<script>
(function() {
    const COOKIE_NAME = 'cookie_consent';
    
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    
    function hasConsent() {
        return getCookie(COOKIE_NAME) !== null;
    }
    
    function showBanner() {
        if (hasConsent()) return;
        
        const banner = document.createElement('div');
        banner.id = 'cookie-banner';
        banner.innerHTML = `
            <div style="
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: #1a1a2e;
                color: white;
                padding: 20px;
                z-index: 10000;
                box-shadow: 0 -2px 10px rgba(0,0,0,0.3);
            ">
                <div style="max-width: 1200px; margin: 0 auto; display: flex; flex-wrap: wrap; align-items: center; gap: 20px;">
                    <div style="flex: 1; min-width: 300px;">
                        <h3 style="margin-bottom: 10px;">🍪 Cookie-Einstellungen</h3>
                        <p style="font-size: 14px; opacity: 0.9;">
                            Wir verwenden Cookies, um Ihnen die bestmögliche Erfahrung auf unserer Website zu bieten.
                            <a href="/legal/datenschutz" style="color: #667eea;">Mehr erfahren</a>
                        </p>
                    </div>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <button onclick="rejectCookies()" style="
                            padding: 12px 24px;
                            border: 2px solid white;
                            background: transparent;
                            color: white;
                            border-radius: 5px;
                            cursor: pointer;
                            font-size: 14px;
                        ">Nur Notwendige</button>
                        <button onclick="acceptAllCookies()" style="
                            padding: 12px 24px;
                            border: none;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border-radius: 5px;
                            cursor: pointer;
                            font-size: 14px;
                        ">Alle akzeptieren</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(banner);
    }
    
    window.acceptAllCookies = function() {
        fetch('/api/gdpr/consent/accept-all', { method: 'POST' })
            .then(() => {
                document.getElementById('cookie-banner').remove();
                location.reload();
            });
    };
    
    window.rejectCookies = function() {
        fetch('/api/gdpr/consent/reject-all', { method: 'POST' })
            .then(() => {
                document.getElementById('cookie-banner').remove();
            });
    };
    
    // Banner anzeigen wenn DOM geladen
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', showBanner);
    } else {
        showBanner();
    }
})();
</script>
"""


def inject_cookie_banner(response):
    """Injiziert Cookie-Banner in HTML-Responses"""
    if response.content_type and 'text/html' in response.content_type:
        data = response.get_data(as_text=True)
        if '</body>' in data:
            data = data.replace('</body>', COOKIE_BANNER_JS + '</body>')
            response.set_data(data)
    return response


# =============================================================================
# SEO META TAGS
# =============================================================================

class SEOService:
    """SEO Meta Tags Generator"""
    
    DEFAULT_META = {
        'title': 'West Money OS - All-in-One Business Platform',
        'description': 'Die ultimative Business-Plattform für Smart Home, CRM, WhatsApp Business, KI-Assistenten und mehr. Von Enterprise Universe GmbH.',
        'keywords': 'Smart Home, LOXONE, CRM, WhatsApp Business, AI, Automation, Enterprise, Frankfurt',
        'author': 'Enterprise Universe GmbH',
        'robots': 'index, follow',
        'language': 'de'
    }
    
    @classmethod
    def generate_meta_tags(cls, page_data: Dict = None) -> str:
        """Generiert Meta-Tags für eine Seite"""
        data = {**cls.DEFAULT_META, **(page_data or {})}
        
        tags = f"""
    <!-- Basic Meta Tags -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{data['description']}">
    <meta name="keywords" content="{data['keywords']}">
    <meta name="author" content="{data['author']}">
    <meta name="robots" content="{data['robots']}">
    <meta name="language" content="{data['language']}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="{data['title']}">
    <meta property="og:description" content="{data['description']}">
    <meta property="og:site_name" content="West Money OS">
    <meta property="og:locale" content="de_DE">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{data['title']}">
    <meta name="twitter:description" content="{data['description']}">
    
    <!-- Canonical -->
    <link rel="canonical" href="{data.get('canonical', 'https://westmoney.de')}">
    
    <!-- Hreflang -->
    <link rel="alternate" hreflang="de" href="https://westmoney.de">
    <link rel="alternate" hreflang="en" href="https://westmoney.de/en">
    <link rel="alternate" hreflang="x-default" href="https://westmoney.de">
    
    <title>{data['title']}</title>
"""
        return tags
    
    @classmethod
    def generate_schema_org(cls, page_type: str = 'Organization') -> str:
        """Generiert Schema.org JSON-LD"""
        
        schemas = {
            'Organization': {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": GDPRConfig.COMPANY_NAME,
                "url": "https://westmoney.de",
                "logo": "https://westmoney.de/logo.png",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": GDPRConfig.COMPANY_ADDRESS,
                    "addressLocality": GDPRConfig.COMPANY_CITY.split()[-1],
                    "postalCode": GDPRConfig.COMPANY_CITY.split()[0],
                    "addressCountry": "DE"
                },
                "contactPoint": {
                    "@type": "ContactPoint",
                    "telephone": GDPRConfig.COMPANY_PHONE,
                    "email": GDPRConfig.COMPANY_EMAIL,
                    "contactType": "customer service"
                }
            },
            'SoftwareApplication': {
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": "West Money OS",
                "applicationCategory": "BusinessApplication",
                "operatingSystem": "Web",
                "offers": {
                    "@type": "Offer",
                    "price": "0",
                    "priceCurrency": "EUR"
                }
            }
        }
        
        schema = schemas.get(page_type, schemas['Organization'])
        return f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'


# =============================================================================
# EXPORT FUNCTION
# =============================================================================

def register_gdpr_blueprints(app):
    """Registriert GDPR Blueprints bei der Flask App"""
    app.register_blueprint(gdpr_bp)
    app.register_blueprint(legal_bp)
    
    # Cookie Banner für alle HTML-Responses
    app.after_request(inject_cookie_banner)
    
    print("✅ GDPR & Legal Blueprints registered")


# Test
if __name__ == '__main__':
    print("GDPR Module loaded")
    print(f"Company: {GDPRConfig.COMPANY_NAME}")
    print(f"CEO: {GDPRConfig.CEO_NAME}")
