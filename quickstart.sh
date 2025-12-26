#!/bin/bash

# Debate Agent Quick Start Script
# This script helps you get started with the Debate Agent system

set -e  # Exit on error

echo "=================================="
echo "  Debate Agent Quick Start"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found."
    echo "Please run this script from the debateAgent project root directory."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found."
    echo ""
    echo "Creating .env file template..."
    cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Optional LLM Configuration
MODEL_NAME=gpt-4
TEMPERATURE=0.7
EOF
    echo "✅ Created .env file template"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY before continuing."
    echo ""
    read -p "Press Enter once you've added your API key to .env..."
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Show menu
echo "=================================="
echo "  What would you like to run?"
echo "=================================="
echo ""
echo "1) React Client (Modern UI)"
echo "2) Gradio Web UI (Legacy Interface)"
echo "3) REST API Server (API Endpoints)"
echo "4) API Test Client (Demo)"
echo "5) Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting React Client..."
        
        # Check if npm is installed
        if ! command -v npm &> /dev/null; then
            echo "❌ Error: npm is not installed. Please install Node.js and npm to run the React client."
            exit 1
        fi
        
        echo "⚠️  Note: The API server must be running for the client to work."
        echo ""
        read -p "Is the API server running in another terminal? (y/n): " api_running
        
        if [ "$api_running" = "y" ] || [ "$api_running" = "Y" ]; then
            echo ""
            echo "📦 Installing client dependencies..."
            cd client
            npm install
            echo ""
            echo "🌐 Starting development server..."
            npm run dev
        else
            echo ""
            echo "Please start the API server first:"
            echo "  1. Open a new terminal"
            echo "  2. cd to the project directory"
            echo "  3. Run: source .venv/bin/activate"
            echo "  4. Run: cd serve && python debate_api.py"
            echo "  5. Then run this script again and choose option 1"
        fi
        ;;
    2)
        echo ""
        echo "🚀 Starting Gradio Web UI..."
        echo "📍 Access the UI at: http://localhost:7860"
        echo ""
        cd serve
        python main.py
        ;;
    3)
        echo ""
        echo "🚀 Starting REST API Server..."
        echo "📍 API Base: http://localhost:8000"
        echo "📍 API Docs: http://localhost:8000/docs"
        echo "📍 ReDoc: http://localhost:8000/redoc"
        echo ""
        cd serve
        python debate_api.py
        ;;
    4)
        echo ""
        echo "⚠️  Note: The API server must be running for the test client to work."
        echo ""
        read -p "Is the API server running in another terminal? (y/n): " api_running
        
        if [ "$api_running" = "y" ] || [ "$api_running" = "Y" ]; then
            echo ""
            echo "🧪 Running API Test Client..."
            echo ""
            cd serve
            python test_api_client.py
        else
            echo ""
            echo "Please start the API server first:"
            echo "  1. Open a new terminal"
            echo "  2. cd to the project directory"
            echo "  3. Run: source .venv/bin/activate"
            echo "  4. Run: cd serve && python debate_api.py"
            echo "  5. Then run this script again and choose option 4"
        fi
        ;;
    5)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "=================================="
echo "  Session Complete"
echo "=================================="
