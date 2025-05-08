#!/bin/bash

# Check if virtual environment exists, otherwise create it
if [ ! -d "venv" ]; then
    echo "🔧 Virtual environment not found. Setting up..."
    python3 -m venv venv
    source venv/bin/activate

    echo "📦 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt

    # Check for yt-dlp
    if ! command -v yt-dlp &> /dev/null
    then
        echo "❌ yt-dlp not found. Installing via Homebrew..."
        brew install yt-dlp
    else
        echo "✅ yt-dlp is already installed."
    fi

    # Check for aria2c
    if ! command -v aria2c &> /dev/null
    then
        echo "❌ aria2c not found. Installing via Homebrew..."
        brew install aria2
    else
        echo "✅ aria2c is already installed."
    fi
else
    # If venv exists, activate it
    echo "✅ Virtual environment found. Activating..."
    source venv/bin/activate
fi

# Start the GUI
echo "🎉 Starting the GUI..."
python downloader.py
