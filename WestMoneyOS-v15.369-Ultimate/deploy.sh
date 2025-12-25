#!/bin/bash
# West Money OS v15.369 Deployment Script

SERVER="81.88.26.204"
USER="administrator"
APP_DIR="/var/www/west-money-os"

echo "🚀 West Money OS v15.369 Deployment"
echo "===================================="

# Create app directory
ssh $USER@$SERVER "mkdir -p $APP_DIR"

# Copy files
scp westmoney_ultimate.py $USER@$SERVER:$APP_DIR/
scp requirements.txt $USER@$SERVER:$APP_DIR/
scp .env $USER@$SERVER:$APP_DIR/

# Setup venv and install
ssh $USER@$SERVER "cd $APP_DIR && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

# Create systemd service
ssh $USER@$SERVER "cat > /etc/systemd/system/westmoney.service << 'EOF'
[Unit]
Description=West Money OS v15.369
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python westmoney_ultimate.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

# Start service
ssh $USER@$SERVER "systemctl daemon-reload && systemctl enable westmoney && systemctl restart westmoney"

echo "✅ Deployment complete!"
echo "🌐 Access: http://west-money.com"
echo "👤 Login: admin / 663724!"
