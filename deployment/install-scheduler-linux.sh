#!/bin/bash
# Install ETF Data Scheduler as systemd service (Linux)

set -e

echo "=========================================="
echo "ETF Data Scheduler - Linux Installation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

echo "Installing for user: $ACTUAL_USER"
echo "Home directory: $ACTUAL_HOME"
echo ""

# Detect UltraCore directory
if [ -d "$ACTUAL_HOME/ultracore-fix" ]; then
    ULTRACORE_DIR="$ACTUAL_HOME/ultracore-fix"
elif [ -d "$ACTUAL_HOME/UltraCore" ]; then
    ULTRACORE_DIR="$ACTUAL_HOME/UltraCore"
else
    echo "❌ Cannot find UltraCore directory"
    echo "Please specify the path:"
    read -p "UltraCore directory: " ULTRACORE_DIR
fi

echo "UltraCore directory: $ULTRACORE_DIR"
echo ""

# Check if service file exists
SERVICE_FILE="$ULTRACORE_DIR/deployment/etf-data-scheduler.service"
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

# Update service file with correct paths
echo "📝 Updating service file with correct paths..."
sed -i "s|User=ubuntu|User=$ACTUAL_USER|g" "$SERVICE_FILE"
sed -i "s|Group=ubuntu|Group=$ACTUAL_USER|g" "$SERVICE_FILE"
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$ULTRACORE_DIR|g" "$SERVICE_FILE"
sed -i "s|Environment=\"PYTHONPATH=.*\"|Environment=\"PYTHONPATH=$ULTRACORE_DIR/src\"|g" "$SERVICE_FILE"

# Copy service file to systemd
echo "📋 Installing systemd service..."
cp "$SERVICE_FILE" /etc/systemd/system/etf-data-scheduler.service

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# Enable service
echo "✅ Enabling service..."
systemctl enable etf-data-scheduler.service

# Start service
echo "🚀 Starting service..."
systemctl start etf-data-scheduler.service

# Check status
echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Service Status:"
systemctl status etf-data-scheduler.service --no-pager
echo ""
echo "📊 Useful Commands:"
echo "   Check status:  sudo systemctl status etf-data-scheduler"
echo "   View logs:     sudo journalctl -u etf-data-scheduler -f"
echo "   Stop service:  sudo systemctl stop etf-data-scheduler"
echo "   Start service: sudo systemctl start etf-data-scheduler"
echo "   Restart:       sudo systemctl restart etf-data-scheduler"
echo ""
echo "✅ ETF data will update daily at 6:00 PM AEST"
