// ═══════════════════════════════════════════════════════════════════════════════
// 神 WEST MONEY OS – WHATSAPP BUSINESS BOT ∞
// Based on: fbsamples/whatsapp-business-jaspers-market (Apache 2.0)
// Enterprise Universe GmbH | Founder & CEO: Ömer Hüseyin Coşkun
// ═══════════════════════════════════════════════════════════════════════════════
// Version: 3.2.0 | Last Updated: 2025-12-23
// Original: https://github.com/fbsamples/whatsapp-business-jaspers-market
// ═══════════════════════════════════════════════════════════════════════════════

const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const redis = require('redis');

const app = express();
app.use(bodyParser.json());

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION – WEST MONEY OS
// ═══════════════════════════════════════════════════════════════════════════════

const config = {
    // WhatsApp API Configuration
    whatsapp: {
        accessToken: process.env.WHATSAPP_ACCESS_TOKEN || 'EAAM2opyyz94BQb6iRbyhmRxC1k7IBmSZAHqxho3nNDcQLfLSeW2J51tSKXYCFPSVnZBxLQuWUefJpDGdQySJKgIswR0OrQA86YX7CQnSzE9WuxriiNFq8T7sMYY4ikE20p4X0zPTGB2RGVAg6DjyTENalYL9alFUAYPe2ZBMf7Fj8ZAZBWh3hJqWJaKE1SiuhiHYugmbGWKAhqxgTFsOZBNtXZAC5pxCvOKTWbZBRQJUWDXKISB2MKjeLG4Htf4zFD8h7LybzdkZCq6hzH7PfB9kChV9lbzzOLVYZD',
        phoneNumberId: process.env.WHATSAPP_PHONE_NUMBER_ID || '423598467493680',
        businessAccountId: process.env.WHATSAPP_BUSINESS_ACCOUNT_ID || '412747065246901',
        appId: process.env.WHATSAPP_APP_ID || '904496971698142',
        apiVersion: 'v21.0',
        verifyToken: process.env.WHATSAPP_WEBHOOK_VERIFY_TOKEN || 'westmoney_webhook_2025'
    },
    
    // HubSpot CRM Configuration
    hubspot: {
        apiKey: process.env.HUBSPOT_API_KEY,
        baseUrl: 'https://api.hubapi.com'
    },
    
    // Explorium B2B Data
    explorium: {
        apiKey: process.env.EXPLORIUM_API_KEY || '1121ab737ecf41edaea2570899a8f90b',
        baseUrl: 'https://api.explorium.ai/v1'
    },
    
    // Server Configuration
    server: {
        port: process.env.PORT || 3000,
        baseUrl: process.env.APP_URL || 'https://west-money.com'
    },
    
    // Redis Configuration
    redis: {
        url: process.env.REDIS_URL || 'redis://localhost:6379'
    }
};

// ═══════════════════════════════════════════════════════════════════════════════
// REDIS CLIENT – SESSION MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════════

let redisClient;

async function initRedis() {
    redisClient = redis.createClient({ url: config.redis.url });
    redisClient.on('error', (err) => console.log('Redis Client Error', err));
    await redisClient.connect();
    console.log('✅ Redis connected');
}

// User session management
async function getSession(phoneNumber) {
    const session = await redisClient.get(`session:${phoneNumber}`);
    return session ? JSON.parse(session) : null;
}

async function setSession(phoneNumber, data, ttl = 3600) {
    await redisClient.setEx(`session:${phoneNumber}`, ttl, JSON.stringify(data));
}

async function clearSession(phoneNumber) {
    await redisClient.del(`session:${phoneNumber}`);
}

// ═══════════════════════════════════════════════════════════════════════════════
// WHATSAPP API CLIENT
// ═══════════════════════════════════════════════════════════════════════════════

const whatsappAPI = axios.create({
    baseURL: `https://graph.facebook.com/${config.whatsapp.apiVersion}`,
    headers: {
        'Authorization': `Bearer ${config.whatsapp.accessToken}`,
        'Content-Type': 'application/json'
    }
});

// Send text message
async function sendTextMessage(to, text) {
    try {
        const response = await whatsappAPI.post(`/${config.whatsapp.phoneNumberId}/messages`, {
            messaging_product: 'whatsapp',
            recipient_type: 'individual',
            to: to,
            type: 'text',
            text: { body: text }
        });
        console.log(`✅ Message sent to ${to}`);
        return response.data;
    } catch (error) {
        console.error('❌ Error sending message:', error.response?.data || error.message);
        throw error;
    }
}

// Send template message
async function sendTemplateMessage(to, templateName, languageCode = 'de', components = []) {
    try {
        const response = await whatsappAPI.post(`/${config.whatsapp.phoneNumberId}/messages`, {
            messaging_product: 'whatsapp',
            recipient_type: 'individual',
            to: to,
            type: 'template',
            template: {
                name: templateName,
                language: { code: languageCode },
                components: components
            }
        });
        console.log(`✅ Template "${templateName}" sent to ${to}`);
        return response.data;
    } catch (error) {
        console.error('❌ Error sending template:', error.response?.data || error.message);
        throw error;
    }
}

// Send interactive message with buttons
async function sendInteractiveButtons(to, bodyText, buttons) {
    try {
        const response = await whatsappAPI.post(`/${config.whatsapp.phoneNumberId}/messages`, {
            messaging_product: 'whatsapp',
            recipient_type: 'individual',
            to: to,
            type: 'interactive',
            interactive: {
                type: 'button',
                body: { text: bodyText },
                action: {
                    buttons: buttons.map((btn, index) => ({
                        type: 'reply',
                        reply: {
                            id: btn.id || `btn_${index}`,
                            title: btn.title.substring(0, 20) // Max 20 chars
                        }
                    }))
                }
            }
        });
        console.log(`✅ Interactive buttons sent to ${to}`);
        return response.data;
    } catch (error) {
        console.error('❌ Error sending interactive:', error.response?.data || error.message);
        throw error;
    }
}

// Send interactive list
async function sendInteractiveList(to, bodyText, buttonText, sections) {
    try {
        const response = await whatsappAPI.post(`/${config.whatsapp.phoneNumberId}/messages`, {
            messaging_product: 'whatsapp',
            recipient_type: 'individual',
            to: to,
            type: 'interactive',
            interactive: {
                type: 'list',
                body: { text: bodyText },
                action: {
                    button: buttonText,
                    sections: sections
                }
            }
        });
        console.log(`✅ Interactive list sent to ${to}`);
        return response.data;
    } catch (error) {
        console.error('❌ Error sending list:', error.response?.data || error.message);
        throw error;
    }
}

// Mark message as read
async function markAsRead(messageId) {
    try {
        await whatsappAPI.post(`/${config.whatsapp.phoneNumberId}/messages`, {
            messaging_product: 'whatsapp',
            status: 'read',
            message_id: messageId
        });
    } catch (error) {
        console.error('❌ Error marking as read:', error.response?.data || error.message);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// HUBSPOT CRM INTEGRATION
// ═══════════════════════════════════════════════════════════════════════════════

const hubspotAPI = axios.create({
    baseURL: config.hubspot.baseUrl,
    headers: {
        'Authorization': `Bearer ${config.hubspot.apiKey}`,
        'Content-Type': 'application/json'
    }
});

// Find or create contact
async function findOrCreateContact(phoneNumber, additionalProps = {}) {
    try {
        // Search for existing contact
        const searchResponse = await hubspotAPI.post('/crm/v3/objects/contacts/search', {
            filterGroups: [{
                filters: [{
                    propertyName: 'phone',
                    operator: 'EQ',
                    value: phoneNumber
                }]
            }]
        });

        if (searchResponse.data.total > 0) {
            return searchResponse.data.results[0];
        }

        // Create new contact
        const createResponse = await hubspotAPI.post('/crm/v3/objects/contacts', {
            properties: {
                phone: phoneNumber,
                whatsapp_number: phoneNumber,
                whatsapp_consent: 'true',
                whatsapp_consent_date: new Date().toISOString(),
                lifecyclestage: 'lead',
                hs_lead_status: 'NEW',
                lead_source: 'WhatsApp',
                ...additionalProps
            }
        });
        
        console.log(`✅ Contact created: ${createResponse.data.id}`);
        return createResponse.data;
    } catch (error) {
        console.error('❌ HubSpot Error:', error.response?.data || error.message);
        return null;
    }
}

// Update contact consent
async function updateContactConsent(contactId, consent, legalBasis) {
    try {
        await hubspotAPI.patch(`/crm/v3/objects/contacts/${contactId}`, {
            properties: {
                whatsapp_consent: consent ? 'true' : 'false',
                whatsapp_consent_date: new Date().toISOString(),
                whatsapp_consent_legal_basis: legalBasis
            }
        });
        console.log(`✅ Consent updated for contact ${contactId}`);
    } catch (error) {
        console.error('❌ Error updating consent:', error.response?.data || error.message);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// WEST MONEY BOT – CONVERSATION FLOWS
// ═══════════════════════════════════════════════════════════════════════════════

const MENU_OPTIONS = {
    MAIN: 'main_menu',
    SERVICES: 'services',
    SMART_HOME: 'smart_home',
    BAU: 'bau',
    AUTOMATION: 'automation',
    CONTACT: 'contact',
    QUOTE: 'quote'
};

// Main menu
async function sendMainMenu(to) {
    await sendInteractiveList(
        to,
        '🏠 *Willkommen bei West Money!*\n\nWie können wir Ihnen helfen? Wählen Sie eine Option:',
        'Menü öffnen',
        [{
            title: 'Unsere Services',
            rows: [
                { id: 'smart_home', title: '🏡 Smart Home', description: 'LOXONE Integration & Automation' },
                { id: 'bau', title: '🏗️ Bauservice', description: 'Barrierefrei & Energieeffizient' },
                { id: 'automation', title: '⚡ Z Automation', description: 'Gebäudeautomation' }
            ]
        }, {
            title: 'Kontakt',
            rows: [
                { id: 'quote', title: '📋 Angebot anfordern', description: 'Kostenloses Angebot' },
                { id: 'contact', title: '📞 Kontakt', description: 'Sprechen Sie mit uns' },
                { id: 'website', title: '🌐 Website', description: 'west-money.com' }
            ]
        }]
    );
}

// Service details
async function sendServiceDetails(to, service) {
    const services = {
        smart_home: {
            title: '🏡 Smart Home Lösungen',
            text: `*LOXONE Smart Home Partner*

✅ Intelligente Lichtsteuerung
✅ Heizung & Klima Automation
✅ Sicherheit & Überwachung
✅ Multiroom Audio
✅ Jalousien & Beschattung

*Vorteile:*
• Bis zu 50% Energieersparnis
• Komfort auf Knopfdruck
• Wertsteigerung Ihrer Immobilie

Möchten Sie ein kostenloses Angebot?`
        },
        bau: {
            title: '🏗️ West Money Bau',
            text: `*Barrierefrei & Energieeffizient*

✅ Barrierefreies Bauen
✅ Energetische Sanierung
✅ Umbau & Renovierung
✅ Neubau-Projekte

*Spezialisierungen:*
• KfW-förderfähige Maßnahmen
• Altersgerechte Umbauten
• Smart Home Integration

Interesse an einer Beratung?`
        },
        automation: {
            title: '⚡ Z Automation',
            text: `*Gebäudeautomation Experten*

✅ ComfortClick Integration
✅ KNX Systeme
✅ BACnet & Modbus
✅ Industrieautomation

*Für:*
• Bürogebäude
• Hotels
• Industrieanlagen
• Wohnkomplexe

Sollen wir Sie beraten?`
        }
    };

    const serviceInfo = services[service];
    if (serviceInfo) {
        await sendInteractiveButtons(to, serviceInfo.text, [
            { id: 'quote', title: '📋 Angebot' },
            { id: 'contact', title: '📞 Anrufen' },
            { id: 'main_menu', title: '↩️ Zurück' }
        ]);
    }
}

// Quote request flow
async function startQuoteFlow(to) {
    await setSession(to, { flow: 'quote', step: 'name' });
    await sendTextMessage(to, '📋 *Angebot anfordern*\n\nGerne erstellen wir Ihnen ein kostenloses Angebot.\n\nWie ist Ihr Name?');
}

async function handleQuoteFlow(to, message, session) {
    switch (session.step) {
        case 'name':
            session.name = message;
            session.step = 'service';
            await setSession(to, session);
            await sendInteractiveButtons(to, `Danke, ${message}! Für welchen Service möchten Sie ein Angebot?`, [
                { id: 'quote_smart_home', title: '🏡 Smart Home' },
                { id: 'quote_bau', title: '🏗️ Bauservice' },
                { id: 'quote_automation', title: '⚡ Automation' }
            ]);
            break;
        
        case 'service':
            session.service = message;
            session.step = 'email';
            await setSession(to, session);
            await sendTextMessage(to, 'Perfekt! Bitte geben Sie Ihre E-Mail-Adresse an:');
            break;
        
        case 'email':
            session.email = message;
            session.step = 'details';
            await setSession(to, session);
            await sendTextMessage(to, 'Fast fertig! Beschreiben Sie kurz Ihr Projekt:');
            break;
        
        case 'details':
            session.details = message;
            await clearSession(to);
            
            // Save to HubSpot
            await findOrCreateContact(to, {
                firstname: session.name,
                email: session.email,
                hs_lead_status: 'QUOTE_REQUESTED',
                service_interest: session.service,
                project_details: session.details
            });
            
            await sendTextMessage(to, `✅ *Vielen Dank, ${session.name}!*\n\nIhre Anfrage wurde erfolgreich übermittelt.\n\n📧 Wir senden Ihnen das Angebot an: ${session.email}\n\n⏰ Sie erhalten innerhalb von 24 Stunden eine Rückmeldung.\n\nBei Fragen erreichen Sie uns unter:\n📞 +49 177 454 7727`);
            
            // Notify team (could integrate with Slack/Email)
            console.log('📋 New quote request:', session);
            break;
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// MESSAGE HANDLER – MAIN LOGIC
// ═══════════════════════════════════════════════════════════════════════════════

async function handleIncomingMessage(message, metadata) {
    const from = message.from;
    const messageId = message.id;
    
    // Mark as read
    await markAsRead(messageId);
    
    // Find or create contact in HubSpot
    await findOrCreateContact(from);
    
    // Get user session
    const session = await getSession(from);
    
    // Handle different message types
    let userInput = '';
    
    if (message.type === 'text') {
        userInput = message.text.body.toLowerCase().trim();
    } else if (message.type === 'interactive') {
        if (message.interactive.type === 'button_reply') {
            userInput = message.interactive.button_reply.id;
        } else if (message.interactive.type === 'list_reply') {
            userInput = message.interactive.list_reply.id;
        }
    } else if (message.type === 'button') {
        userInput = message.button.text.toLowerCase();
    }
    
    console.log(`📩 Message from ${from}: ${userInput}`);
    
    // Check if in a flow
    if (session && session.flow === 'quote') {
        if (userInput.startsWith('quote_')) {
            session.service = userInput.replace('quote_', '');
            session.step = 'email';
            await setSession(from, session);
            await sendTextMessage(from, 'Perfekt! Bitte geben Sie Ihre E-Mail-Adresse an:');
        } else {
            await handleQuoteFlow(from, message.text?.body || userInput, session);
        }
        return;
    }
    
    // Route based on input
    switch (userInput) {
        // Greetings
        case 'hi':
        case 'hallo':
        case 'hello':
        case 'hey':
        case 'moin':
        case 'servus':
        case 'guten tag':
            await sendMainMenu(from);
            break;
        
        // Main menu
        case 'menu':
        case 'menü':
        case 'main_menu':
        case 'start':
            await sendMainMenu(from);
            break;
        
        // Services
        case 'smart_home':
        case 'smarthome':
            await sendServiceDetails(from, 'smart_home');
            break;
        
        case 'bau':
        case 'bauservice':
            await sendServiceDetails(from, 'bau');
            break;
        
        case 'automation':
        case 'z automation':
            await sendServiceDetails(from, 'automation');
            break;
        
        // Quote
        case 'quote':
        case 'angebot':
        case '📋 angebot':
            await startQuoteFlow(from);
            break;
        
        // Contact
        case 'contact':
        case 'kontakt':
        case '📞 anrufen':
            await sendTextMessage(from, `📞 *Kontakt*\n\n*West Money Bau*\nEnterprise Universe GmbH\n\n📱 +49 177 454 7727\n📧 info@west-money.com\n🌐 west-money.com\n\n📍 Deutschland\n\n⏰ Mo-Fr: 8:00 - 18:00 Uhr`);
            break;
        
        // Website
        case 'website':
            await sendTextMessage(from, '🌐 Besuchen Sie unsere Website:\n\nhttps://west-money.com');
            break;
        
        // DSGVO Consent
        case 'dsgvo':
        case 'datenschutz':
            await sendInteractiveButtons(from, '🔐 *Datenschutz*\n\nMöchten Sie Ihre Einwilligung zum Erhalt von WhatsApp-Nachrichten aktualisieren?', [
                { id: 'consent_yes', title: '✅ Zustimmen' },
                { id: 'consent_no', title: '❌ Ablehnen' }
            ]);
            break;
        
        case 'consent_yes':
            const contact = await findOrCreateContact(from);
            if (contact) {
                await updateContactConsent(contact.id, true, 'Consent - WhatsApp opt-in');
            }
            await sendTextMessage(from, '✅ Vielen Dank! Sie haben der WhatsApp-Kommunikation zugestimmt.');
            break;
        
        case 'consent_no':
            const contactNo = await findOrCreateContact(from);
            if (contactNo) {
                await updateContactConsent(contactNo.id, false, 'Consent - WhatsApp opt-out');
            }
            await sendTextMessage(from, '✅ Verstanden. Sie erhalten keine weiteren Marketing-Nachrichten von uns.');
            break;
        
        // Default
        default:
            await sendTextMessage(from, `👋 Hallo! Ich bin der West Money Bot.\n\nTippen Sie *"Menü"* um unsere Services zu sehen oder stellen Sie mir eine Frage.`);
            break;
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// EXPRESS ROUTES
// ═══════════════════════════════════════════════════════════════════════════════

// Webhook verification (GET)
app.get('/api/whatsapp/webhook', (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];

    if (mode === 'subscribe' && token === config.whatsapp.verifyToken) {
        console.log('✅ Webhook verified');
        res.status(200).send(challenge);
    } else {
        console.error('❌ Webhook verification failed');
        res.sendStatus(403);
    }
});

// Webhook handler (POST)
app.post('/api/whatsapp/webhook', async (req, res) => {
    try {
        const body = req.body;

        if (body.object === 'whatsapp_business_account') {
            for (const entry of body.entry) {
                for (const change of entry.changes) {
                    if (change.field === 'messages') {
                        const value = change.value;
                        
                        if (value.messages) {
                            for (const message of value.messages) {
                                await handleIncomingMessage(message, value.metadata);
                            }
                        }
                        
                        if (value.statuses) {
                            for (const status of value.statuses) {
                                console.log(`📊 Status update: ${status.id} - ${status.status}`);
                            }
                        }
                    }
                }
            }
        }
        
        res.sendStatus(200);
    } catch (error) {
        console.error('❌ Webhook error:', error);
        res.sendStatus(500);
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', app: 'West Money WhatsApp Bot', version: '3.2.0' });
});

// Send message API
app.post('/api/whatsapp/send', async (req, res) => {
    try {
        const { to, message, type = 'text' } = req.body;
        
        if (type === 'text') {
            const result = await sendTextMessage(to, message);
            res.json({ success: true, data: result });
        } else {
            res.status(400).json({ error: 'Invalid message type' });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ═══════════════════════════════════════════════════════════════════════════════
// SERVER START
// ═══════════════════════════════════════════════════════════════════════════════

async function startServer() {
    try {
        await initRedis();
        
        app.listen(config.server.port, () => {
            console.log('═══════════════════════════════════════════════════════');
            console.log('  神 WEST MONEY OS – WhatsApp Bot ∞');
            console.log('═══════════════════════════════════════════════════════');
            console.log(`  🚀 Server running on port ${config.server.port}`);
            console.log(`  📱 WhatsApp Phone ID: ${config.whatsapp.phoneNumberId}`);
            console.log(`  🔗 Webhook URL: ${config.server.baseUrl}/api/whatsapp/webhook`);
            console.log('═══════════════════════════════════════════════════════');
        });
    } catch (error) {
        console.error('❌ Failed to start server:', error);
        process.exit(1);
    }
}

startServer();

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════════

module.exports = {
    app,
    sendTextMessage,
    sendTemplateMessage,
    sendInteractiveButtons,
    sendInteractiveList,
    findOrCreateContact,
    config
};
