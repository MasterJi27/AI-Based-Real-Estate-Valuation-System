#!/bin/bash
# Real Estate AI Application Startup Script
# This script ensures the application starts with all fixes applied

echo "🏠 Starting Real Estate AI Application with Bug Fixes..."

# Navigate to the application directory
cd "/workspaces/AI-Based-Real-Estate-Valuation-System/Milestone 2"

# Clear any Python cache files to ensure fresh imports
echo "🧹 Clearing Python cache..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Set the Google API key if provided as environment variable
if [ ! -z "$GOOGLE_API_KEY" ]; then
    echo "🔑 Google API key found in environment"
    export GOOGLE_API_KEY="$GOOGLE_API_KEY"
elif [ -f ".env" ]; then
    echo "🔑 Loading environment from .env file"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "ℹ️  No Google API key found - Gemini AI features will be limited"
    echo "    Create a .env file with GOOGLE_API_KEY=your_key to enable AI features"
fi

# Check system health
echo "🔍 Running health check..."
python3 final_verification.py

if [ $? -eq 0 ]; then
    echo "✅ All systems verified working!"
    echo ""
    echo "🚀 Starting Streamlit application..."
    echo "The application will be available at http://localhost:8501"
    echo ""
    echo "Note: All previous errors have been fixed:"
    echo "  ✅ ML Model input shape error - FIXED"
    echo "  ✅ Gemini AI model name error - FIXED"  
    echo "  ✅ Database connection handling - IMPROVED"
    echo ""
    
    # Start the Streamlit application
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
else
    echo "❌ Health check failed. Please check the logs above."
    exit 1
fi