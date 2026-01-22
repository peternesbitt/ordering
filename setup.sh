#!/bin/bash
# Setup script for Apple Reminders to Amazon Ordering automation

set -e

echo "🛒 Setting up Apple Reminders to Amazon Auto-Ordering..."
echo ""

# Check if on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This application requires macOS for Apple Reminders access"
    exit 1
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browser..."
playwright install chromium

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your Amazon credentials!"
    echo ""
else
    echo "✓ .env file already exists"
fi

# Create logs directory
mkdir -p logs

# Make main.py executable
chmod +x main.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Amazon credentials:"
echo "   nano .env"
echo ""
echo "2. Test the application (dry-run mode):"
echo "   source venv/bin/activate"
echo "   python main.py --run-now --dry-run --no-headless"
echo ""
echo "3. Create some reminders in Apple Reminders app"
echo ""
echo "4. Run for real:"
echo "   python main.py --run-now"
echo ""
echo "5. Or schedule daily runs:"
echo "   python main.py"
echo ""
echo "See README.md for full documentation."
