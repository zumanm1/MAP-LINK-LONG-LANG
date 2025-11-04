#!/bin/bash
# Cross-platform Flask startup script for macOS/Linux

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗺️  Excel Map Coordinates Converter - Flask Version${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

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
pip install -q -r requirements.txt

# Create required directories
mkdir -p uploads processed

# Run Flask app
echo ""
echo -e "${GREEN}✅ Starting Flask server...${NC}"
echo "🌐 Access the app at: http://localhost:5000"
echo "⏹️  Press Ctrl+C to stop"
echo ""

python flask_app.py
