from setuptools import setup

APP = ['downloader.py']
DATA_FILES = []
OPTIONS = {
    # 'argv_emulation': True,
    # 'iconfile': 'icon.icns',  # Optional: your custom app icon
    'packages': ['tkinter'],
    'includes': ['jaraco.text'],
    'plist': {
        'CFBundleName': 'TubeGrabber',
        'CFBundleDisplayName': 'TubeGrabber',
        'CFBundleIdentifier': 'com.monoloco.tubegrabber',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
    }
}

setup(
    app=APP,
    name='TubeGrabber',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
