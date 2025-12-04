#!/usr/bin/env python3
"""
Script to bundle external dependencies like yt-dlp binary with the macOS app.
"""

import os
import urllib.request
import stat
import platform
import sys


def download_yt_dlp():
    """Download the yt-dlp binary for macOS."""

    # Determine the correct binary for the platform
    if platform.system() != "Darwin":
        print("This script is designed for macOS only.")
        return False

    # Check if we're on Apple Silicon or Intel
    machine = platform.machine()
    if machine == "arm64":
        # Apple Silicon
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"
    else:
        # Intel Mac
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"

    # Create resources directory
    resources_dir = "resources"
    os.makedirs(resources_dir, exist_ok=True)

    binary_path = os.path.join(resources_dir, "yt-dlp")

    try:
        print(f"Downloading yt-dlp from {url}...")
        urllib.request.urlretrieve(url, binary_path)

        # Make it executable
        os.chmod(
            binary_path,
            stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH,
        )

        print(f"yt-dlp downloaded successfully to {binary_path}")
        return True

    except Exception as e:
        print(f"Error downloading yt-dlp: {e}")
        return False


def download_aria2c():
    """Download aria2c binary (optional, for faster downloads)."""
    print(
        "Note: aria2c support is optional. Install via homebrew if needed: brew install aria2"
    )


if __name__ == "__main__":
    success = download_yt_dlp()
    download_aria2c()

    if success:
        print("Dependencies downloaded successfully!")
        sys.exit(0)
    else:
        print("Failed to download dependencies!")
        sys.exit(1)
