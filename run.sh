#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    echo "❌ Not installed yet. Run: sh install.sh"
    exit 1
fi

# YouTube breaks old yt-dlp versions often, so update on every launch
echo "📦 Updating yt-dlp..."
.venv/bin/pip install -q -U -r requirements.txt || echo "⚠️  Could not update yt-dlp (offline?), using the installed one."

echo "🎉 Starting TubeGrabber..."
exec .venv/bin/python -u downloader.py
