#!/bin/bash

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE=Linux;;
esac

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
    if [ $? -ne 0 ]; then
        echo "Setup failed. Please fix the errors above."
        exit 1
    fi
fi

# Kill any existing Flask processes on port 5000
if [ "$MACHINE" = "Mac" ]; then
    # macOS: Use lsof to find process using port 5000
    PID=$(lsof -ti:5000)
    if [ ! -z "$PID" ]; then
        echo "Stopping existing Flask app on port 5000..."
        kill -9 $PID 2>/dev/null
        sleep 1
    fi
else
    # Linux: Use fuser
    if command -v fuser &> /dev/null; then
        fuser -k 5000/tcp 2>/dev/null
        sleep 1
    fi
fi

# Activate venv and run the app
echo "Starting NearbyNomad..."
echo "The app will be available at http://127.0.0.1:5000"
echo ""
source venv/bin/activate
python app.py
