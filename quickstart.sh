#!/bin/bash
# Quick start script for Account Plan Agent
# This script sets up and runs the application

echo "=================================="
echo "Account Plan Agent - Quick Start"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python version is 3.8-3.11
if ! python -c "import sys; exit(0 if (3,8) <= sys.version_info[:2] <= (3,11) else 1)" 2>/dev/null; then
    echo "⚠️  Warning: Python 3.8-3.11 is recommended. You have $python_version"
    echo "Python 3.12+ may have dependency issues."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Creating from env.example..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Created .env file"
        echo "⚠️  Please edit .env and add your OpenAI API key before continuing"
        read -p "Press Enter when ready..."
    else
        echo "❌ env.example not found!"
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"

# Initialize database
if [ ! -f "account_plan_agent.db" ]; then
    echo ""
    echo "Initializing database..."
    python init_database.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to initialize database"
        exit 1
    fi
    echo "✅ Database initialized"
    echo ""
    echo "Default admin credentials:"
    echo "  Username: admin"
    echo "  Password: admin"
    echo "  ⚠️  Please change the password after first login!"
else
    echo ""
    echo "Database already exists, skipping initialization"
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Starting the application..."
echo ""
echo "Backend (FastAPI) will start on: http://localhost:8000"
echo "Frontend (Streamlit) will start on: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
echo "Starting backend..."
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
streamlit run app.py

# When frontend is closed, also close backend
kill $BACKEND_PID 2>/dev/null

echo ""
echo "Application stopped."

