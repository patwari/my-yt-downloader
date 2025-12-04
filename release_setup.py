from setuptools import setup
import sys
import os

APP = ["downloader.py"]

# Include bundled binaries as data files
DATA_FILES = []
if os.path.exists("resources/yt-dlp"):
    DATA_FILES.append(("resources", ["resources/yt-dlp"]))

OPTIONS = {
    "argv_emulation": True,
    "strip": False,  # Don't strip debug symbols
    "optimize": 2,  # Optimize Python bytecode
    "includes": [
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "tkinter.ttk",
        "subprocess",
        "json",
        "os",
        "re",
        "sys",
        "pathlib",
        "shutil",
    ],
    "packages": ["tkinter", "subprocess", "json"],
    "excludes": ["matplotlib", "numpy", "scipy", "PIL", "wx"],
    # Bundle all dependencies
    "site_packages": True,
    "semi_standalone": False,  # Create fully standalone app
    "alias": False,
    "plist": {
        "CFBundleName": "TubeGrabber",
        "CFBundleDisplayName": "TubeGrabber",
        "CFBundleIdentifier": "com.monoloco.tubegrabber",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "LSMinimumSystemVersion": "10.14",
        "NSHighResolutionCapable": True,
    },
}

setup(
    app=APP,
    name="TubeGrabber",
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
