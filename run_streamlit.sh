#!/bin/bash
# Cross-platform Streamlit startup script for macOS/Linux

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗺️  Excel Map Coordinates Converter - Streamlit Version${NC}"
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

# Run Streamlit app
echo ""
echo -e "${GREEN}✅ Starting Streamlit server...${NC}"
echo "🌐 The app will open in your browser automatically"
echo "⏹️  Press Ctrl+C to stop"
echo ""

streamlit run app.py
