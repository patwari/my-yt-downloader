#!/bin/bash
set -e
cd "$(dirname "$0")"

if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is required. Install it from https://brew.sh and run this again."
    exit 1
fi

# yt-dlp needs Python 3.11+, macOS ships 3.9, so always use Homebrew's
PYTHON="$(brew --prefix)/bin/python3"
[ -x "$PYTHON" ] || brew install python

command -v ffmpeg &> /dev/null || brew install ffmpeg
command -v aria2c &> /dev/null || brew install aria2
# YouTube needs a JavaScript runtime; an existing Node works too
command -v deno &> /dev/null || command -v node &> /dev/null || brew install deno

echo "🔧 Setting up virtual environment..."
"$PYTHON" -m venv .venv
.venv/bin/pip install -q -U pip -r requirements.txt

echo "✅ Installed. Start it with: sh run.sh"
