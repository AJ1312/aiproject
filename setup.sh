#!/bin/bash

echo "================================="
echo "🚀 CLI-TOP + AI Setup Wizard"
echo "================================="
echo ""

# Check if cli-top binary exists
if [ ! -f "./cli-top" ]; then
    echo "⚠️  CLI-TOP binary not found!"
    echo "   Building CLI-TOP..."
    go build -o cli-top main.go
    if [ $? -ne 0 ]; then
        echo "❌ Build failed. Please install Go and try again."
        exit 1
    fi
    echo "✅ CLI-TOP built successfully!"
    echo ""
fi

# Check credentials
echo "📋 Checking credentials..."
if [ ! -f "./cli-top-config.env" ] || grep -q 'REGNO=""' ./cli-top-config.env; then
    echo ""
    echo "🔐 No credentials found. Let's set them up!"
    echo ""
    echo "VTOP Credentials Setup:"
    echo "----------------------"
    
    # Run CLI-TOP to login (it will create the config file)
    echo "Please enter your VTOP credentials when prompted..."
    echo ""
    ./cli-top profile
    
    if [ $? -ne 0 ]; then
        echo "❌ Login failed. Please check your credentials and try again."
        exit 1
    fi
    
    echo ""
    echo "✅ Credentials saved successfully!"
else
    echo "✅ Credentials already configured!"
fi

echo ""
echo "================================="
echo "🤖 AI Features Setup"
echo "================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3 first."
    exit 1
fi

echo "📦 Installing AI dependencies..."
cd ai
pip3 install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Some dependencies may have failed to install."
    echo "   You can continue, but some AI features may not work."
else
    echo "✅ Dependencies installed!"
fi

echo ""
echo "📊 Generating AI Context..."
echo "   (Exporting VTOP data and creating current_semester_data.json)"
echo ""

# Export AI data
cd ..
./cli-top ai export -o /tmp/all_data.txt

if [ ! -f "/tmp/all_data.txt" ]; then
    echo "⚠️  Warning: Failed to export VTOP data."
    echo "   AI features may not work correctly."
else
    echo "✅ VTOP data exported!"
    
    # Parse current semester
    echo "   Parsing current semester data..."
    cd ai
    python3 parse_current_semester.py
    
    if [ -f "./current_semester_data.json" ]; then
        echo "✅ AI context created successfully!"
    else
        echo "⚠️  Warning: Failed to create AI context."
    fi
    cd ..
fi

echo ""
echo "================================="
echo "🎉 Setup Complete!"
echo "================================="
echo ""
echo "Next steps:"
echo "  1. Start the web interface:"
echo "     cd website && python3 server.py"
echo ""
echo "  2. Open in browser:"
echo "     http://localhost:5555"
echo ""
echo "  3. Or use CLI directly:"
echo "     ./cli-top marks"
echo "     ./cli-top attendance"
echo "     cd ai && python3 chatbot.py"
echo ""
echo "Happy learning! 🚀"
echo ""
