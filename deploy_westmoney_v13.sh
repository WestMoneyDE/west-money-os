#!/bin/bash
# ============================================================================
# WEST MONEY OS v13.0 - DEPLOYMENT SCRIPT
# ============================================================================
# Server: 81.88.26.204 (west-money.com)
# Datum: 24.12.2024
# ============================================================================

echo "🚀 WEST MONEY OS v13.0 DEPLOYMENT"
echo "=================================="

# 1. Backup erstellen
echo "📦 Creating backup..."
sudo cp /var/www/westmoney/app.py /var/www/westmoney/app.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# 2. Neue Datei kopieren
echo "📁 Deploying new version..."
sudo cp westmoney_complete_v13.py /var/www/westmoney/app.py

# 3. Berechtigungen setzen
echo "🔐 Setting permissions..."
sudo chown www-data:www-data /var/www/westmoney/app.py
sudo chmod 644 /var/www/westmoney/app.py

# 4. Service neustarten
echo "🔄 Restarting service..."
sudo systemctl restart westmoney

# 5. Status prüfen
echo "✅ Checking status..."
sudo systemctl status westmoney --no-pager -l

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================"
echo "🌐 Landing Page: https://west-money.com/"
echo "🔐 Login: https://west-money.com/login"
echo "📊 Dashboard: https://west-money.com/dashboard"
echo "🧠 Einstein: https://west-money.com/einstein"
echo "🔮 Predictions: https://west-money.com/einstein/predictions"
echo "🛡️ DedSec: https://west-money.com/dedsec"
echo "🗼 Tower: https://west-money.com/dedsec/tower"
echo "🚁 Drones: https://west-money.com/dedsec/drones"
echo "📹 CCTV: https://west-money.com/dedsec/cctv"
echo "💬 WhatsApp: https://west-money.com/whatsapp"
echo "🤖 GOD BOT: https://west-money.com/godbot"
echo "🔐 Locker: https://west-money.com/locker"
echo ""
echo "Login: admin / 663724"
