#!/bin/bash

echo "Setting up NearbyNomad..."

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "Detected OS: $MACHINE"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    if [ "$MACHINE" = "Mac" ]; then
        echo "Please install Python 3:"
        echo "  brew install python3"
        echo "Or download from: https://www.python.org/downloads/"
    else
        echo "Please install Python 3:"
        echo "  sudo apt install python3 python3-venv"
    fi
    exit 1
fi

# Check if venv module is available
if ! python3 -m venv --help &> /dev/null; then
    echo "❌ python3-venv is not available."
    if [ "$MACHINE" = "Mac" ]; then
        echo "Python venv should be included with Python 3."
        echo "Try reinstalling Python 3 from https://www.python.org/downloads/"
    else
        echo "Please install it with: sudo apt install python3-venv"
    fi
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
if [ "$MACHINE" = "Mac" ]; then
    source venv/bin/activate && pip install --upgrade pip && pip install Flask python-dotenv
else
    source venv/bin/activate && pip install Flask python-dotenv
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "The app will be available at http://127.0.0.1:5000"
