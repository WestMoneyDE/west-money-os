#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# 神 WEST MONEY OS – WHATSAPP MESSAGE TEMPLATES ∞
# ═══════════════════════════════════════════════════════════════════════════════
# Run this script to create message templates in your WhatsApp Business Account
# Usage: ./templates.sh
# ═══════════════════════════════════════════════════════════════════════════════

# Load environment variables
source .env 2>/dev/null || true

# Configuration
WABA_ID="${WHATSAPP_BUSINESS_ACCOUNT_ID:-412747065246901}"
ACCESS_TOKEN="${WHATSAPP_ACCESS_TOKEN}"
API_VERSION="v21.0"
BASE_URL="https://graph.facebook.com/${API_VERSION}"

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "  神 WEST MONEY OS – Creating WhatsApp Templates"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Check if token is set
if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Error: WHATSAPP_ACCESS_TOKEN is not set"
    echo "Please set the token in your .env file or environment"
    exit 1
fi

# Function to create template
create_template() {
    local name=$1
    local category=$2
    local language=$3
    local body=$4
    
    echo "📝 Creating template: $name..."
    
    response=$(curl -s -X POST "${BASE_URL}/${WABA_ID}/message_templates" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"${name}\",
            \"category\": \"${category}\",
            \"language\": \"${language}\",
            \"components\": [
                {
                    \"type\": \"BODY\",
                    \"text\": \"${body}\"
                }
            ]
        }")
    
    if echo "$response" | grep -q "id"; then
        echo "✅ Template '$name' created successfully"
    else
        echo "❌ Failed to create '$name': $response"
    fi
    echo ""
}

# Function to create template with buttons
create_template_with_buttons() {
    local name=$1
    local category=$2
    local language=$3
    local body=$4
    local button1=$5
    local button2=$6
    
    echo "📝 Creating template with buttons: $name..."
    
    response=$(curl -s -X POST "${BASE_URL}/${WABA_ID}/message_templates" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"${name}\",
            \"category\": \"${category}\",
            \"language\": \"${language}\",
            \"components\": [
                {
                    \"type\": \"BODY\",
                    \"text\": \"${body}\"
                },
                {
                    \"type\": \"BUTTONS\",
                    \"buttons\": [
                        {
                            \"type\": \"QUICK_REPLY\",
                            \"text\": \"${button1}\"
                        },
                        {
                            \"type\": \"QUICK_REPLY\",
                            \"text\": \"${button2}\"
                        }
                    ]
                }
            ]
        }")
    
    if echo "$response" | grep -q "id"; then
        echo "✅ Template '$name' created successfully"
    else
        echo "❌ Failed to create '$name': $response"
    fi
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════════
# CREATE TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

# 1. Welcome Template
create_template \
    "westmoney_welcome" \
    "MARKETING" \
    "de" \
    "Willkommen bei West Money! 🏠\n\nWir freuen uns, dass Sie sich für unsere Smart Home und Bauservices interessieren.\n\nAntworten Sie mit 'Menü' um unsere Services zu sehen."

# 2. DSGVO Consent Request
create_template_with_buttons \
    "dsgvo_consent_request" \
    "UTILITY" \
    "de" \
    "Hallo {{1}}!\n\nUm Sie über unsere Services bei {{2}} zu informieren, benötigen wir Ihre Einwilligung gemäß DSGVO.\n\nMöchten Sie WhatsApp-Nachrichten von uns erhalten?" \
    "Ja, ich stimme zu" \
    "Nein, danke"

# 3. Appointment Reminder
create_template \
    "termin_erinnerung" \
    "UTILITY" \
    "de" \
    "Hallo {{1}}! 📅\n\nErinnerung an Ihren Termin:\n📆 {{2}}\n⏰ {{3}}\n📍 {{4}}\n\nBei Fragen erreichen Sie uns unter +49 177 454 7727"

# 4. Quote Confirmation
create_template \
    "angebot_bestaetigung" \
    "UTILITY" \
    "de" \
    "Vielen Dank für Ihre Anfrage, {{1}}! ✅\n\nWir haben Ihre Angebotsanfrage erhalten und melden uns innerhalb von 24 Stunden bei Ihnen.\n\nIhre Anfrage:\n{{2}}\n\nMit freundlichen Grüßen\nIhr West Money Team"

# 5. Smart Home Promotion
create_template \
    "smarthome_promo" \
    "MARKETING" \
    "de" \
    "🏡 *Smart Home Aktion* bei West Money!\n\nSparen Sie bis zu 50% Energiekosten mit unseren LOXONE Smart Home Lösungen.\n\n✅ Kostenlose Beratung\n✅ Professionelle Installation\n✅ 5 Jahre Garantie\n\nJetzt Termin vereinbaren!"

# 6. Project Update
create_template \
    "projekt_update" \
    "UTILITY" \
    "de" \
    "Hallo {{1}}! 🏗️\n\n*Update zu Ihrem Projekt:*\n{{2}}\n\n*Status:* {{3}}\n\nBei Fragen sind wir für Sie da.\n\nIhr West Money Team"

# 7. Service Complete
create_template \
    "service_abgeschlossen" \
    "UTILITY" \
    "de" \
    "Hallo {{1}}! ✅\n\nIhr Projekt wurde erfolgreich abgeschlossen!\n\nWir würden uns über Ihr Feedback freuen. Wie zufrieden waren Sie mit unserem Service?\n\n⭐⭐⭐⭐⭐"

# ═══════════════════════════════════════════════════════════════════════════════
# LIST EXISTING TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "  📋 Existing Templates"
echo "═══════════════════════════════════════════════════════════════════════════════"

curl -s -X GET "${BASE_URL}/${WABA_ID}/message_templates" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" | python3 -m json.tool 2>/dev/null || \
curl -s -X GET "${BASE_URL}/${WABA_ID}/message_templates" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "  ✅ Template creation complete!"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Note: Templates need to be approved by Meta before use."
echo "This usually takes 24-48 hours."
echo ""
