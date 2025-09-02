#!/bin/bash

# Astral Assessment Setup Script
# This script sets up the development environment

set -e  # Exit on any error

echo "🚀 Setting up Astral Assessment development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION detected. Python $REQUIRED_VERSION+ is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed successfully"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# App Configuration
APP_NAME=astral-assessment
APP_VERSION=1.0.0
ENVIRONMENT=development

# External Services (add your API keys here)
FIRECRAWL_API_KEY=your_firecrawl_key_here
SCRAPINGDOG_API_KEY=your_scrapingdog_key_here
INNGEST_EVENT_KEY=your_inngest_key_here
INNGEST_SERVE_URL=your_inngest_url_here

# Optional: AI Configuration
OPENAI_API_KEY=your_openai_key_here

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
EOF
    echo "✅ .env file created (update with your API keys)"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Run one terminal: export INNGEST_DEV=1 && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
echo "3. Run the other terminal: npx inngest-cli@latest dev"
echo "4. Access API docs: http://localhost:8000/docs"
echo "5. Run tests: python -m pytest"
echo ""
echo "Happy coding! 🚀" 