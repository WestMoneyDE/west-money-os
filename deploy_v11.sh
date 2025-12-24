#!/bin/bash
# =============================================================================
# WEST MONEY OS v11.0 ULTIMATE DEPLOYMENT
# Enterprise Universe GmbH © 2025
# =============================================================================

echo "🚀 West Money OS v11.0 GODMODE ULTIMATE Deployment"
echo "=================================================="

# Backup current version
echo "📦 Creating backup..."
cp /var/www/westmoney/app.py /var/www/westmoney/app_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null

# Copy new version
echo "📝 Deploying new app.py..."
cp westmoney_v11_app.py /var/www/westmoney/app.py

# Set permissions
echo "🔐 Setting permissions..."
chown www-data:www-data /var/www/westmoney/app.py
chmod 644 /var/www/westmoney/app.py

# Restart service
echo "🔄 Restarting service..."
systemctl restart westmoney

# Wait for startup
sleep 3

# Check status
echo "✅ Checking status..."
systemctl status westmoney --no-pager | head -15

echo ""
echo "=================================================="
echo "✅ Deployment complete!"
echo ""
echo "🌐 Website: https://west-money.com"
echo "📱 Login: admin / 663724"
echo ""
echo "📚 New Legal Pages:"
echo "   - /impressum"
echo "   - /datenschutz"
echo "   - /agb"
echo "   - /widerruf"
echo ""
echo "🔐 DSGVO APIs:"
echo "   - POST /api/contacts/whatsapp-consent/bulk"
echo "   - GET /api/contacts/export-consent-log"
echo "   - GET /api/user/data-export"
echo "   - POST /api/user/delete-account"
echo ""
