#!/bin/bash

# Reverse USB Platform Startup Script

echo "🚀 Starting Reverse USB Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is too old. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if USB mount directory exists
if [ ! -d "/media/usb" ]; then
    echo "📁 Creating USB mount directory..."
    sudo mkdir -p /media/usb
    sudo chmod 755 /media/usb
fi

# Check if running with sudo (needed for USB mounting)
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Warning: Not running as root. USB mounting may fail."
    echo "   To run with proper permissions, use: sudo ./start.sh"
fi

# Set environment variables
export FLASK_ENV=development
export SECRET_KEY=dev-secret-key-change-in-production

echo "🌐 Starting Flask application..."
echo "📱 Access the application at: http://localhost:55005"
echo "🛑 Press Ctrl+C to stop the server"

# Run the application
python app.py 