#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Set the version number
VERSION="0.1"

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Run the release setup with py2app
python3 release_setup.py py2app

# Recreate the staging directory to avoid conflicts
rm -rf dmg-staging
mkdir -p dmg-staging

# Copy the built app into the staging directory
cp -R "dist/TubeGrabber.app" dmg-staging/

# Create a symbolic link to Applications
ln -s /Applications dmg-staging/Applications

# Make sure the output directory exists
mkdir -p public

# Create a compressed disk image using the version
hdiutil create -volname "TubeGrabber" -srcfolder "dmg-staging" -ov -format UDZO "public/TubeGrabber-${VERSION}.dmg"
