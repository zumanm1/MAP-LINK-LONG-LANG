#!/bin/bash
# Fast dependency installation using uv

echo "🚀 Installing dependencies with uv (10-100x faster than pip)..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully"
fi

# Install dependencies
echo "📦 Installing Python dependencies from requirements.txt..."
uv pip install -r requirements.txt

echo ""
echo "✅ All dependencies installed successfully!"
echo ""
echo "🎯 Next steps:"
echo "   1. Run Flask app:      python3 flask_app.py"
echo "   2. Run Streamlit app:  streamlit run app.py"
echo "   3. Run CLI:            python3 map_converter.py input.xlsx output.xlsx"
echo "   4. Interactive menu:   python3 run.py"
