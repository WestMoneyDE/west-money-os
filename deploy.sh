#!/bin/bash
# West Money OS v15.369 - Deployment Script
# Server: 81.88.26.204 (one.com Cloud Server L)

set -e

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║   🚀 WEST MONEY OS v15.369 - DEPLOYMENT                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"

# Variables
APP_DIR="/var/www/west-money-os"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="westmoney"

echo ""
echo "📁 Creating directories..."
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

echo ""
echo "📋 Copying files..."
cp app.py $APP_DIR/
cp requirements.txt $APP_DIR/
cp .env $APP_DIR/ 2>/dev/null || cp .env.example $APP_DIR/.env

echo ""
echo "🐍 Setting up Python environment..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=West Money OS v15.369
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "🔄 Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service status:"
sudo systemctl status $SERVICE_NAME --no-pager

echo ""
echo "🌐 Access: http://$(hostname -I | awk '{print $1}'):5000"
echo "🔐 Login: admin / admin123"
echo ""
