# MY Youtube Downloader (MacOS) - TubeGrabber

- uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) tool. This is just a UI for it.
- This project is primarily for myself. And I haven't tested it on other devices.

## Features

- Local web UI (opens in your browser at http://127.0.0.1:8765), light and dark mode.
- Paste several links at once, one per line.
- Queue with live progress, speed, ETA, playlist item `x of N`, cancel, retry and "Show in Finder".
- MP3 (best quality, metadata + cover art embedded) or MP4 with a max quality.
- Playlists go into their own folder, optionally numbered (`01. Title.mp3`).
- Resume: re-running a playlist skips files that already exist and continues partial downloads.
- Optional aria2c external downloader for MP4.
- yt-dlp is updated on every launch, since YouTube breaks old versions.

## Setup

Needs [Homebrew](https://brew.sh). Then, from this folder:

1. `sh install.sh` (once). Installs Python, ffmpeg, aria2 and Deno via Homebrew if missing (an existing Node.js is used instead of Deno), and sets up `.venv`.
1. `sh run.sh` (every time). Updates yt-dlp and opens the app in your browser. Quit with Ctrl+C.
