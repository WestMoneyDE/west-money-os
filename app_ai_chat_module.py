"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🤖 AI CHAT MODUL - WEST MONEY OS v12.0                                       ║
║  Claude AI Integration, Chat History, Knowledge Base, Auto-Responses         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from flask import Blueprint, render_template_string, request, jsonify, session
from datetime import datetime
import json
import os

ai_chat_bp = Blueprint('ai_chat', __name__)

AI_CHAT_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI Chat - West Money OS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a15 0%, #150a1a 50%, #0a0510 100%);
            min-height: 100vh;
            color: #fff;
        }
        .container { display: flex; min-height: 100vh; }
        .sidebar {
            width: 280px;
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(139,92,246,0.2);
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        .logo {
            display: flex; align-items: center; gap: 12px;
            padding: 15px 0;
            border-bottom: 1px solid rgba(139,92,246,0.2);
            margin-bottom: 20px;
        }
        .logo-icon { font-size: 1.8rem; }
        .logo-text {
            font-size: 1.2rem; font-weight: 700;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav a {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 16px; color: #888; text-decoration: none;
            border-radius: 10px; margin-bottom: 5px; transition: all 0.3s;
        }
        .nav a:hover, .nav a.active { background: rgba(139,92,246,0.1); color: #ff00ff; }
        
        .chat-history {
            flex: 1;
            overflow-y: auto;
            margin-top: 20px;
        }
        .chat-history-title {
            font-size: 0.85rem;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .history-item {
            padding: 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .history-item:hover { background: rgba(139,92,246,0.1); }
        .history-item-title { font-size: 0.9rem; font-weight: 500; }
        .history-item-date { font-size: 0.75rem; color: #666; }
        
        .main { flex: 1; display: flex; flex-direction: column; }
        
        .chat-header {
            padding: 20px 30px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-title { font-size: 1.5rem; font-weight: 600; }
        
        .chat-messages {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }
        
        .message {
            max-width: 80%;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
        }
        .message.user { flex-direction: row-reverse; margin-left: auto; }
        
        .message-avatar {
            width: 40px; height: 40px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem;
            flex-shrink: 0;
        }
        .message.assistant .message-avatar {
            background: linear-gradient(135deg, #ff00ff, #00ffff);
        }
        .message.user .message-avatar {
            background: rgba(255,255,255,0.1);
        }
        
        .message-content {
            background: rgba(255,255,255,0.05);
            padding: 16px 20px;
            border-radius: 16px;
            line-height: 1.6;
        }
        .message.user .message-content {
            background: linear-gradient(135deg, rgba(139,92,246,0.3), rgba(236,72,153,0.3));
        }
        .message-time {
            font-size: 0.75rem;
            color: #666;
            margin-top: 8px;
        }
        
        .typing-indicator {
            display: none;
            padding: 20px 30px;
        }
        .typing-indicator.active { display: flex; }
        .typing-dot {
            width: 8px; height: 8px;
            background: #ff00ff;
            border-radius: 50%;
            margin-right: 5px;
            animation: typing 1.4s infinite;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        
        .chat-input-container {
            padding: 20px 30px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .chat-input-wrapper {
            display: flex;
            gap: 15px;
            align-items: flex-end;
        }
        .chat-input {
            flex: 1;
            padding: 16px 20px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 16px;
            color: #fff;
            font-size: 1rem;
            resize: none;
            min-height: 56px;
            max-height: 200px;
        }
        .chat-input:focus { outline: none; border-color: #ff00ff; }
        .chat-input::placeholder { color: #666; }
        
        .send-btn {
            width: 56px; height: 56px;
            background: linear-gradient(135deg, #ff00ff, #00ffff);
            border: none;
            border-radius: 16px;
            color: #fff;
            font-size: 1.3rem;
            cursor: pointer;
            transition: all 0.3s;
        }
        .send-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 25px rgba(139,92,246,0.4);
        }
        
        .quick-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .quick-action {
            padding: 8px 16px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            color: #888;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.3s;
        }
        .quick-action:hover {
            background: rgba(139,92,246,0.1);
            border-color: rgba(139,92,246,0.3);
            color: #ff00ff;
        }
        
        .btn {
            padding: 10px 20px; border: none; border-radius: 10px;
            font-size: 0.9rem; font-weight: 600; cursor: pointer;
            transition: all 0.3s;
        }
        .btn-secondary {
            background: rgba(255,255,255,0.1); color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .btn-primary {
            background: linear-gradient(135deg, #ff00ff, #00ffff); color: #fff;
        }
        
        /* Code blocks */
        .message-content pre {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 10px 0;
        }
        .message-content code {
            font-family: 'Fira Code', monospace;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <nav class="sidebar">
            <div class="logo">
                <span class="logo-icon">🤖</span>
                <span class="logo-text">AI Assistant</span>
            </div>
            <div class="nav">
                <a href="/dashboard"><span>📊</span> Dashboard</a>
                <a href="/dashboard/ai-chat" class="active"><span>🤖</span> AI Chat</a>
                <a href="/broly"><span>🐉</span> Broly</a>
                <a href="/einstein"><span>🧠</span> Einstein</a>
            </div>
            
            <button class="btn btn-primary" style="margin-top: 20px; width: 100%;" onclick="newChat()">
                ➕ Neuer Chat
            </button>
            
            <div class="chat-history">
                <div class="chat-history-title">Letzte Chats</div>
                <div class="history-item">
                    <div class="history-item-title">Lead Scoring optimieren</div>
                    <div class="history-item-date">Heute, 14:30</div>
                </div>
                <div class="history-item">
                    <div class="history-item-title">E-Mail Template erstellen</div>
                    <div class="history-item-date">Heute, 10:15</div>
                </div>
                <div class="history-item">
                    <div class="history-item-title">Kampagnen-Analyse</div>
                    <div class="history-item-date">Gestern</div>
                </div>
                <div class="history-item">
                    <div class="history-item-title">LOXONE Angebot</div>
                    <div class="history-item-date">23.12.2024</div>
                </div>
            </div>
        </nav>
        
        <main class="main">
            <div class="chat-header">
                <div class="chat-title">💬 West Money AI Assistant</div>
                <div>
                    <button class="btn btn-secondary" onclick="exportChat()">📥 Export</button>
                </div>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message assistant">
                    <div class="message-avatar">🤖</div>
                    <div>
                        <div class="message-content">
                            Hallo! Ich bin dein West Money AI Assistant. 👋
                            
                            Ich kann dir helfen bei:
                            <ul style="margin: 10px 0 10px 20px;">
                                <li>📧 E-Mail & WhatsApp Templates erstellen</li>
                                <li>🎯 Lead Scoring optimieren</li>
                                <li>📊 Kampagnen analysieren</li>
                                <li>💼 Angebote & Rechnungen erstellen</li>
                                <li>🏠 LOXONE Smart Home Beratung</li>
                                <li>🔄 Automatisierungen einrichten</li>
                            </ul>
                            
                            Wie kann ich dir heute helfen?
                        </div>
                        <div class="message-time">Gerade eben</div>
                    </div>
                </div>
            </div>
            
            <div class="typing-indicator" id="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <span style="margin-left: 10px; color: #888;">AI denkt nach...</span>
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input-wrapper">
                    <textarea class="chat-input" id="chat-input" placeholder="Schreibe eine Nachricht..." rows="1"></textarea>
                    <button class="send-btn" onclick="sendMessage()">📤</button>
                </div>
                <div class="quick-actions">
                    <span class="quick-action" onclick="quickAction('email')">📧 E-Mail Template</span>
                    <span class="quick-action" onclick="quickAction('whatsapp')">💬 WhatsApp Nachricht</span>
                    <span class="quick-action" onclick="quickAction('offer')">📋 Angebot erstellen</span>
                    <span class="quick-action" onclick="quickAction('analysis')">📊 Kampagnen-Analyse</span>
                    <span class="quick-action" onclick="quickAction('loxone')">🏠 LOXONE Beratung</span>
                </div>
            </div>
        </main>
    </div>
    
    <script>
        const chatMessages = document.getElementById('chat-messages');
        const chatInput = document.getElementById('chat-input');
        const typingIndicator = document.getElementById('typing-indicator');
        
        // Auto-resize textarea
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
        
        // Send on Enter (Shift+Enter for new line)
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            chatInput.value = '';
            chatInput.style.height = 'auto';
            
            // Show typing indicator
            typingIndicator.classList.add('active');
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            try {
                const response = await fetch('/api/ai-chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                typingIndicator.classList.remove('active');
                addMessage(data.response, 'assistant');
                
            } catch (error) {
                typingIndicator.classList.remove('active');
                addMessage('Entschuldigung, es gab einen Fehler. Bitte versuche es erneut.', 'assistant');
            }
        }
        
        function addMessage(content, type) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + type;
            
            const avatar = type === 'assistant' ? '🤖' : '👤';
            const time = new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
            
            messageDiv.innerHTML = `
                <div class="message-avatar">${avatar}</div>
                <div>
                    <div class="message-content">${formatMessage(content)}</div>
                    <div class="message-time">${time}</div>
                </div>
            `;
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function formatMessage(content) {
            // Basic markdown-like formatting
            content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
            content = content.replace(/`(.*?)`/g, '<code>$1</code>');
            content = content.replace(/\n/g, '<br>');
            return content;
        }
        
        function quickAction(type) {
            const prompts = {
                'email': 'Erstelle ein professionelles E-Mail Template für eine Smart Home Beratungsanfrage',
                'whatsapp': 'Schreibe eine freundliche WhatsApp Follow-Up Nachricht für einen potenziellen Kunden',
                'offer': 'Hilf mir ein Angebot für eine LOXONE Smart Home Installation zu erstellen',
                'analysis': 'Analysiere meine aktuellen Kampagnen-Performance und gib Verbesserungsvorschläge',
                'loxone': 'Erkläre die Vorteile von LOXONE für ein Smart Home Projekt'
            };
            
            chatInput.value = prompts[type];
            chatInput.focus();
        }
        
        function newChat() {
            chatMessages.innerHTML = '';
            addMessage('Neuer Chat gestartet! Wie kann ich dir helfen?', 'assistant');
        }
        
        function exportChat() {
            alert('Chat wird exportiert...');
        }
    </script>
</body>
</html>
"""


@ai_chat_bp.route('/dashboard/ai-chat')
def ai_chat_page():
    """AI Chat page"""
    return render_template_string(AI_CHAT_HTML)


@ai_chat_bp.route('/api/ai-chat', methods=['POST'])
def chat_with_ai():
    """Chat with AI"""
    data = request.json
    user_message = data.get('message', '')
    
    # Knowledge base for West Money
    knowledge = {
        'loxone': 'LOXONE ist ein führendes Smart Home System aus Österreich. West Money Bau ist zertifizierter LOXONE Partner und bietet Installation, Programmierung und Wartung.',
        'smart_home': 'Smart Home Lösungen von West Money Bau umfassen: Lichtsteuerung, Heizungssteuerung, Beschattung, Sicherheitssysteme, Multiroom-Audio und Energiemanagement.',
        'preise': 'Die Preise für Smart Home Installationen beginnen bei ca. €15.000 für ein Einfamilienhaus. Genaue Preise hängen vom Umfang und den gewünschten Funktionen ab.',
        'kontakt': 'West Money Bau GmbH - Telefon: +49 1234 567890 - E-Mail: info@west-money.com - www.west-money.com'
    }
    
    # Simple AI response logic (in production: use Claude API)
    response = generate_ai_response(user_message, knowledge)
    
    return jsonify({
        'success': True,
        'response': response,
        'timestamp': datetime.now().isoformat()
    })


def generate_ai_response(message: str, knowledge: dict) -> str:
    """Generate AI response based on message"""
    message_lower = message.lower()
    
    # Check for keywords
    if any(word in message_lower for word in ['email', 'e-mail', 'template', 'nachricht']):
        return """Hier ist ein professionelles E-Mail Template:

**Betreff:** Ihre Smart Home Beratung - Persönliches Angebot

---

Sehr geehrte(r) {{first_name}} {{last_name}},

vielen Dank für Ihr Interesse an unseren Smart Home Lösungen!

Als zertifizierter LOXONE Partner bieten wir Ihnen:
✅ Individuelle Beratung vor Ort
✅ Maßgeschneiderte Lösungen
✅ Professionelle Installation
✅ 24/7 Support

Gerne würde ich Ihnen unsere Möglichkeiten in einem persönlichen Gespräch vorstellen.

Wann passt es Ihnen am besten?

Mit freundlichen Grüßen,
Ömer Coşkun
West Money Bau GmbH

---

*Sie können die Variablen {{first_name}} und {{last_name}} verwenden, die automatisch ersetzt werden.*"""

    elif any(word in message_lower for word in ['whatsapp', 'follow-up', 'nachfassen']):
        return """Hier ist eine WhatsApp Follow-Up Nachricht:

---

Hallo {{first_name}}! 👋

Ich hoffe, es geht Ihnen gut!

Ich wollte kurz nachfragen, ob Sie Zeit hatten, sich unser Smart Home Angebot anzuschauen? 🏠

Falls Sie Fragen haben oder einen Beratungstermin wünschen, bin ich gerne für Sie da!

Beste Grüße,
Ömer von West Money Bau 💼

---

*Tipp: Personalisierte Nachrichten haben 40% höhere Antwortrate!*"""

    elif any(word in message_lower for word in ['loxone', 'smart home', 'automation']):
        return """**LOXONE Smart Home - Vorteile:**

🏠 **All-in-One Lösung**
- Beleuchtung, Beschattung, Heizung, Sicherheit
- Ein System für alles

💡 **Energieeffizienz**
- Bis zu 30% Energieeinsparung
- Intelligente Steuerung

🔒 **Sicherheit**
- Integrierte Alarmanlage
- Kameraüberwachung
- Anwesenheitssimulation

🎵 **Komfort**
- Multiroom Audio
- Sprachsteuerung
- App-Steuerung von überall

💰 **Investition**
- Wertsteigerung der Immobilie
- Langfristige Einsparungen

Als zertifizierter LOXONE Partner beraten wir Sie gerne!"""

    elif any(word in message_lower for word in ['angebot', 'preis', 'kosten']):
        return """**Angebotserstellung für Smart Home:**

Um ein passendes Angebot zu erstellen, benötige ich folgende Informationen:

📏 **Objektdaten:**
- Wohnfläche (m²)
- Anzahl der Räume
- Neubau oder Bestandsgebäude?

🎯 **Gewünschte Funktionen:**
- [ ] Lichtsteuerung
- [ ] Beschattung
- [ ] Heizung/Klima
- [ ] Sicherheitssystem
- [ ] Multiroom Audio
- [ ] Türsprechanlage

💰 **Budget-Orientierung:**
- Basic: ab €15.000
- Comfort: €25.000 - €40.000
- Premium: €40.000+

Soll ich ein konkretes Angebot vorbereiten?"""

    elif any(word in message_lower for word in ['kampagne', 'analyse', 'performance']):
        return """**📊 Kampagnen-Analyse:**

Basierend auf Ihren aktuellen Kampagnen:

**E-Mail Kampagnen:**
- Öffnungsrate: 45.2% ✅ (Branchendurchschnitt: 22%)
- Klickrate: 12.8% ✅
- Beste Betreffzeile: "Smart Home ROI Analyse"

**WhatsApp:**
- Delivery Rate: 94% ✅
- Response Rate: 34%
- Beste Zeit: Di-Do, 10-12 Uhr

**Empfehlungen:**
1. 🎯 A/B Tests für Betreffzeilen
2. 📅 Versand zwischen 10-11 Uhr optimieren
3. 🔄 Follow-Up Sequenz nach 3 Tagen
4. 💬 Mehr personalisierte WhatsApp nutzen

Soll ich eine spezifische Kampagne analysieren?"""

    else:
        return f"""Danke für deine Nachricht!

Ich kann dir bei folgenden Themen helfen:

📧 **Marketing & Kommunikation**
- E-Mail Templates erstellen
- WhatsApp Nachrichten formulieren
- Kampagnen optimieren

💼 **Vertrieb**
- Angebote erstellen
- Lead Scoring verbessern
- Follow-Up Strategien

🏠 **Smart Home**
- LOXONE Beratung
- Technische Fragen
- Preiskalkulation

🤖 **Automatisierung**
- Workflows einrichten
- Trigger definieren
- Sequenzen planen

Was möchtest du als nächstes tun?"""


def register_ai_chat_blueprint(app):
    """Register AI Chat blueprint"""
    app.register_blueprint(ai_chat_bp)
    print("🤖 AI CHAT MODULE loaded!")


__all__ = ['ai_chat_bp', 'register_ai_chat_blueprint']
