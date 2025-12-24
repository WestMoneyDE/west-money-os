#!/usr/bin/env python3
"""
🎤 WEST MONEY OS - AI VOICE AGENT 🎤
Customer Support Voice AI mit ElevenLabs, Twilio und Claude

Features:
- Eingehende Anrufe automatisch beantworten
- Ausgehende Anrufe starten
- Deutsche Stimme (natürlich klingend)
- Claude AI für Konversation
- CRM-Integration
- Terminvereinbarung
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from flask import Blueprint, request, jsonify, Response
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VoiceAgent')

# Blueprint
voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')


# =============================================================================
# CONFIGURATION
# =============================================================================

class VoiceConfig:
    """Voice Agent Konfiguration"""
    
    # ElevenLabs
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '21m00Tcm4TlvDq8ikWAM')  # Rachel
    
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    
    # App
    APP_URL = os.getenv('APP_URL', 'https://westmoney.de')
    
    # Anthropic
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

VOICE_SYSTEM_PROMPTS = {
    'support': """Du bist Lisa, die freundliche Kundenservice-Mitarbeiterin von West Money / Enterprise Universe GmbH.

DEINE PERSÖNLICHKEIT:
- Freundlich und professionell
- Geduldig und verständnisvoll
- Lösungsorientiert
- Spricht natürliches Deutsch

DEINE AUFGABEN:
1. Begrüße den Anrufer herzlich
2. Frage, wie du helfen kannst
3. Beantworte Fragen zu unseren Produkten
4. Leite komplexe Anfragen weiter
5. Biete Rückruf oder Terminvereinbarung an

UNSERE PRODUKTE:
- West Money Bau: Smart Home Lösungen mit LOXONE, Barrierefreies Bauen
- Z Automation: Gebäudeautomation und Steuerungssysteme
- West Money OS: Business-Software-Plattform

GESPRÄCHSREGELN:
- Halte Antworten kurz (1-2 Sätze)
- Sprich natürlich, nicht roboterhaft
- Frage nach, wenn du etwas nicht verstehst
- Wiederhole wichtige Informationen zur Bestätigung
- Verabschiede dich freundlich

ESKALATION:
- Bei Beschwerden: "Ich verstehe. Darf ich Sie zu einem Kollegen verbinden?"
- Bei technischen Details: "Für diese Fachfrage verbinde ich Sie gerne mit unserem Experten."

BEISPIEL-BEGRÜSSUNG:
"Guten Tag! Hier ist Lisa von West Money. Wie kann ich Ihnen helfen?"
""",

    'sales': """Du bist Max, der Verkaufsberater von West Money.

DEINE ZIELE:
1. Qualifiziere den Interessenten
2. Erkläre Vorteile unserer Lösungen
3. Vereinbare einen Beratungstermin

QUALIFIZIERUNGSFRAGEN:
- "Planen Sie gerade einen Neubau oder eine Renovierung?"
- "Welche Bereiche möchten Sie automatisieren?"
- "Haben Sie schon ein Budget im Kopf?"
- "Bis wann soll das Projekt umgesetzt werden?"

PREISRAHMEN:
- Smart Home Basis: ab €15.000
- Smart Home Premium: ab €30.000  
- Barrierefreies Bauen: individuell

IMMER:
- Betone den Mehrwert
- Biete kostenlose Erstberatung an
- Hole Kontaktdaten ein
""",

    'termin': """Du bist für die Terminvereinbarung zuständig.

AUFGABE:
- Finde einen passenden Termin
- Hole Name, Telefon und E-Mail
- Bestätige den Termin

VERFÜGBARE ZEITEN:
- Montag bis Freitag: 9:00 - 17:00 Uhr
- Keine Wochenenden

ABLAUF:
1. "An welchem Tag passt es Ihnen am besten?"
2. "Vormittags oder nachmittags?"
3. "Darf ich Ihren vollständigen Namen notieren?"
4. "Und Ihre Telefonnummer für Rückfragen?"
5. "Perfekt! Ich trage den Termin ein und Sie erhalten eine Bestätigung per E-Mail."
"""
}


# =============================================================================
# ELEVENLABS SERVICE
# =============================================================================

class ElevenLabsService:
    """ElevenLabs Conversational AI Integration"""
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    @classmethod
    def _headers(cls):
        return {
            'xi-api-key': VoiceConfig.ELEVENLABS_API_KEY,
            'Content-Type': 'application/json'
        }
    
    @classmethod
    def create_agent(cls, name: str, system_prompt: str, first_message: str = None) -> Dict:
        """Erstellt einen Conversational AI Agent"""
        
        if not VoiceConfig.ELEVENLABS_API_KEY:
            return {'success': False, 'error': 'ElevenLabs nicht konfiguriert'}
        
        url = f"{cls.BASE_URL}/convai/agents/create"
        
        data = {
            'name': name,
            'conversation_config': {
                'agent': {
                    'prompt': {
                        'prompt': system_prompt
                    },
                    'first_message': first_message or "Guten Tag! Wie kann ich Ihnen helfen?",
                    'language': 'de'
                },
                'asr': {
                    'quality': 'high',
                    'provider': 'elevenlabs',
                    'user_input_audio_format': 'pcm_16000'
                },
                'tts': {
                    'model_id': 'eleven_multilingual_v2',
                    'voice_id': VoiceConfig.ELEVENLABS_VOICE_ID,
                    'optimize_streaming_latency': 3,
                    'stability': 0.5,
                    'similarity_boost': 0.75
                },
                'conversation': {
                    'max_duration_seconds': 600,  # 10 Minuten max
                    'client_events': ['transcript', 'audio']
                }
            }
        }
        
        try:
            response = requests.post(url, headers=cls._headers(), json=data, timeout=30)
            result = response.json()
            
            if response.status_code in [200, 201]:
                return {'success': True, 'agent': result}
            return {'success': False, 'error': result.get('detail', 'Fehler')}
            
        except Exception as e:
            logger.error(f"ElevenLabs create_agent error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_agents(cls) -> Dict:
        """Listet alle Agents"""
        
        url = f"{cls.BASE_URL}/convai/agents"
        
        try:
            response = requests.get(url, headers=cls._headers(), timeout=30)
            
            if response.status_code == 200:
                return {'success': True, 'agents': response.json()}
            return {'success': False, 'error': 'Fehler beim Abrufen'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def text_to_speech(cls, text: str, voice_id: str = None) -> bytes:
        """Konvertiert Text zu Sprache"""
        
        url = f"{cls.BASE_URL}/text-to-speech/{voice_id or VoiceConfig.ELEVENLABS_VOICE_ID}"
        
        data = {
            'text': text,
            'model_id': 'eleven_multilingual_v2',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.75
            }
        }
        
        try:
            response = requests.post(
                url, 
                headers={**cls._headers(), 'Accept': 'audio/mpeg'}, 
                json=data, 
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            return None
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None


# =============================================================================
# TWILIO SERVICE
# =============================================================================

class TwilioService:
    """Twilio Voice Integration"""
    
    @classmethod
    def _client(cls):
        """Twilio Client"""
        try:
            from twilio.rest import Client
            return Client(VoiceConfig.TWILIO_ACCOUNT_SID, VoiceConfig.TWILIO_AUTH_TOKEN)
        except ImportError:
            logger.error("Twilio SDK not installed")
            return None
    
    @classmethod
    def make_call(cls, to_number: str, agent_type: str = 'support') -> Dict:
        """Startet ausgehenden Anruf"""
        
        client = cls._client()
        if not client:
            return {'success': False, 'error': 'Twilio nicht verfügbar'}
        
        try:
            call = client.calls.create(
                to=to_number,
                from_=VoiceConfig.TWILIO_PHONE_NUMBER,
                url=f"{VoiceConfig.APP_URL}/api/voice/outbound-handler?agent={agent_type}",
                status_callback=f"{VoiceConfig.APP_URL}/api/voice/status",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed']
            )
            
            logger.info(f"Outbound call initiated: {call.sid}")
            
            return {
                'success': True,
                'call_sid': call.sid,
                'status': call.status
            }
            
        except Exception as e:
            logger.error(f"Twilio call error: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_call_details(cls, call_sid: str) -> Dict:
        """Holt Anrufdetails"""
        
        client = cls._client()
        if not client:
            return {'success': False, 'error': 'Twilio nicht verfügbar'}
        
        try:
            call = client.calls(call_sid).fetch()
            return {
                'success': True,
                'call': {
                    'sid': call.sid,
                    'status': call.status,
                    'duration': call.duration,
                    'from': call.from_,
                    'to': call.to,
                    'start_time': str(call.start_time),
                    'end_time': str(call.end_time)
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


# =============================================================================
# VOICE AGENT MANAGER
# =============================================================================

class VoiceAgentManager:
    """Verwaltet Voice Agents"""
    
    # Cache für erstellte Agents
    _agents = {}
    
    @classmethod
    def get_or_create_agent(cls, agent_type: str) -> Optional[str]:
        """Holt oder erstellt Agent"""
        
        if agent_type in cls._agents:
            return cls._agents[agent_type]
        
        # Erstelle neuen Agent
        system_prompt = VOICE_SYSTEM_PROMPTS.get(agent_type, VOICE_SYSTEM_PROMPTS['support'])
        
        first_messages = {
            'support': "Guten Tag! Hier ist Lisa von West Money. Wie kann ich Ihnen helfen?",
            'sales': "Guten Tag! Hier ist Max von West Money. Schön, dass Sie sich für unsere Lösungen interessieren!",
            'termin': "Guten Tag! Ich helfe Ihnen gerne bei der Terminvereinbarung."
        }
        
        result = ElevenLabsService.create_agent(
            name=f"WestMoney_{agent_type}",
            system_prompt=system_prompt,
            first_message=first_messages.get(agent_type, first_messages['support'])
        )
        
        if result.get('success'):
            agent_id = result['agent'].get('agent_id')
            cls._agents[agent_type] = agent_id
            logger.info(f"Created agent: {agent_type} -> {agent_id}")
            return agent_id
        
        logger.error(f"Failed to create agent: {result.get('error')}")
        return None
    
    @classmethod
    def handle_incoming_call(cls, caller_number: str) -> Dict:
        """Verarbeitet eingehenden Anruf"""
        
        # Hier könnte CRM-Lookup stattfinden
        # contact = Contact.query.filter_by(phone=caller_number).first()
        
        return {
            'caller': caller_number,
            'agent_type': 'support',
            'context': '',
            'timestamp': datetime.utcnow().isoformat()
        }


# =============================================================================
# API ROUTES
# =============================================================================

@voice_bp.route('/agents', methods=['GET'])
def list_agents():
    """Listet alle Voice Agents"""
    result = ElevenLabsService.get_agents()
    return jsonify(result)


@voice_bp.route('/agents', methods=['POST'])
def create_agent():
    """Erstellt neuen Voice Agent"""
    data = request.get_json() or {}
    
    agent_type = data.get('type', 'support')
    agent_id = VoiceAgentManager.get_or_create_agent(agent_type)
    
    if agent_id:
        return jsonify({'success': True, 'agent_id': agent_id})
    return jsonify({'success': False, 'error': 'Agent konnte nicht erstellt werden'}), 500


@voice_bp.route('/call/outbound', methods=['POST'])
def initiate_outbound_call():
    """Startet ausgehenden Anruf"""
    data = request.get_json() or {}
    
    to_number = data.get('to')
    agent_type = data.get('agent_type', 'support')
    
    if not to_number:
        return jsonify({'success': False, 'error': 'Telefonnummer erforderlich'}), 400
    
    # Nummer formatieren
    if to_number.startswith('0'):
        to_number = '+49' + to_number[1:]
    elif not to_number.startswith('+'):
        to_number = '+49' + to_number
    
    result = TwilioService.make_call(to_number, agent_type)
    
    return jsonify(result)


@voice_bp.route('/call/status', methods=['POST'])
def call_status_callback():
    """Twilio Status Callback"""
    
    call_sid = request.form.get('CallSid')
    call_status = request.form.get('CallStatus')
    duration = request.form.get('CallDuration')
    
    logger.info(f"Call {call_sid}: {call_status} ({duration}s)")
    
    # Hier könnte Logging in Datenbank erfolgen
    
    return '', 200


@voice_bp.route('/incoming', methods=['POST'])
def handle_incoming():
    """Twilio Webhook für eingehende Anrufe"""
    
    try:
        from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
    except ImportError:
        return jsonify({'error': 'Twilio SDK nicht installiert'}), 500
    
    caller = request.form.get('From', 'Unbekannt')
    
    logger.info(f"Incoming call from: {caller}")
    
    # Anruf-Kontext laden
    context = VoiceAgentManager.handle_incoming_call(caller)
    
    # TwiML Response erstellen
    response = VoiceResponse()
    
    # Mit ElevenLabs Agent verbinden
    connect = Connect()
    stream = Stream(
        url=f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={VoiceAgentManager.get_or_create_agent('support')}"
    )
    connect.append(stream)
    response.append(connect)
    
    return Response(str(response), mimetype='application/xml')


@voice_bp.route('/outbound-handler', methods=['POST'])
def outbound_handler():
    """Handler für ausgehende Anrufe"""
    
    try:
        from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
    except ImportError:
        return jsonify({'error': 'Twilio SDK nicht installiert'}), 500
    
    agent_type = request.args.get('agent', 'support')
    
    response = VoiceResponse()
    
    # Mit entsprechendem Agent verbinden
    agent_id = VoiceAgentManager.get_or_create_agent(agent_type)
    
    if agent_id:
        connect = Connect()
        stream = Stream(
            url=f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={agent_id}"
        )
        connect.append(stream)
        response.append(connect)
    else:
        response.say("Entschuldigung, der Service ist momentan nicht verfügbar. Bitte versuchen Sie es später erneut.", voice='alice', language='de-DE')
    
    return Response(str(response), mimetype='application/xml')


@voice_bp.route('/tts', methods=['POST'])
def text_to_speech():
    """Text-to-Speech API"""
    data = request.get_json() or {}
    
    text = data.get('text')
    if not text:
        return jsonify({'error': 'Text erforderlich'}), 400
    
    audio = ElevenLabsService.text_to_speech(text)
    
    if audio:
        return Response(audio, mimetype='audio/mpeg')
    return jsonify({'error': 'TTS fehlgeschlagen'}), 500


@voice_bp.route('/call/<call_sid>', methods=['GET'])
def get_call(call_sid):
    """Holt Anrufdetails"""
    result = TwilioService.get_call_details(call_sid)
    return jsonify(result)


# =============================================================================
# WIDGET COMPONENT
# =============================================================================

VOICE_WIDGET_HTML = """
<div id="voice-widget" style="
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 9999;
">
    <button onclick="toggleVoiceWidget()" style="
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.3s;
    ">
        <svg width="28" height="28" fill="white" viewBox="0 0 24 24">
            <path d="M20 15.5c-1.25 0-2.45-.2-3.57-.57a1.02 1.02 0 0 0-1.02.24l-2.2 2.2a15.045 15.045 0 0 1-6.59-6.59l2.2-2.21a.96.96 0 0 0 .25-1A11.36 11.36 0 0 1 8.5 4c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1 0 9.39 7.61 17 17 17 .55 0 1-.45 1-1v-3.5c0-.55-.45-1-1-1zM19 12h2a9 9 0 0 0-9-9v2c3.87 0 7 3.13 7 7zm-4 0h2c0-2.76-2.24-5-5-5v2c1.66 0 3 1.34 3 3z"/>
        </svg>
    </button>
    
    <div id="voice-panel" style="
        display: none;
        position: absolute;
        bottom: 70px;
        right: 0;
        width: 320px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        overflow: hidden;
    ">
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        ">
            <h3 style="margin: 0 0 5px 0;">🎤 Sprachassistent</h3>
            <p style="margin: 0; opacity: 0.9; font-size: 14px;">Sprechen Sie mit Lisa</p>
        </div>
        
        <div style="padding: 20px;">
            <p style="color: #666; font-size: 14px; margin-bottom: 15px;">
                Klicken Sie auf den Button unten, um mit unserem KI-Assistenten zu sprechen.
            </p>
            
            <button onclick="startVoiceCall()" style="
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
            ">
                🎙️ Gespräch starten
            </button>
            
            <p style="color: #999; font-size: 12px; margin-top: 15px; text-align: center;">
                Oder rufen Sie uns an: <a href="tel:+4969123456" style="color: #667eea;">+49 69 123456</a>
            </p>
        </div>
    </div>
</div>

<script>
function toggleVoiceWidget() {
    const panel = document.getElementById('voice-panel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
}

async function startVoiceCall() {
    // ElevenLabs Widget öffnen oder WebRTC starten
    alert('Voice Call wird gestartet... (Integration erforderlich)');
}
</script>
"""


def get_voice_widget():
    """Gibt Voice Widget HTML zurück"""
    return VOICE_WIDGET_HTML


# =============================================================================
# EXPORT
# =============================================================================

def register_voice_blueprint(app):
    """Registriert Voice Blueprint"""
    app.register_blueprint(voice_bp)
    print("✅ Voice Agent Blueprint registered")


if __name__ == '__main__':
    # Test
    print("Voice Agent Module loaded")
    print(f"ElevenLabs configured: {bool(VoiceConfig.ELEVENLABS_API_KEY)}")
    print(f"Twilio configured: {bool(VoiceConfig.TWILIO_ACCOUNT_SID)}")
