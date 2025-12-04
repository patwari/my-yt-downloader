#!/usr/bin/env python3
"""
Alternative build script using PyInstaller for better standalone app creation.
"""

import subprocess
import sys
import os
from pathlib import Path


def build_with_pyinstaller():
    """Build the app using PyInstaller."""

    # Install PyInstaller if not available
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Download dependencies
    print("Downloading dependencies...")
    subprocess.run([sys.executable, "bundle_dependencies.py"])

    # PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=TubeGrabber",
        "--windowed",
        "--onefile",
        "--add-data=resources/yt-dlp:resources",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.ttk",
        "--clean",
        "downloader.py",
    ]

    print("Building app with PyInstaller...")
    print(" ".join(cmd))

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("Build successful!")
        print("App created at: dist/TubeGrabber")
        return True
    else:
        print("Build failed!")
        return False


if __name__ == "__main__":
    success = build_with_pyinstaller()
    sys.exit(0 if success else 1)
