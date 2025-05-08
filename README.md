# MY Youtube Downloader (MacOS)

- uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) tool. This is just a UI for it. 
- This project is primarily for myself. And I haven't tested it on other devices.

## Additional Features:
- Opens a new terminal instance each time, so that the UI is not blocked.
- Ability to resume downloads for playlists. Resumes from x/Total and not from the start.
- Ability to download via external downloader = aria, which is a bit faster.

## Packages Used
- `brew install yt-dlp`
- `brew install ffmpeg`
- `brew install python-tk`
- `brew install aria2`

### To Install
1. From terminal
- Clone the repository.
- Install above dependencies
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip3 install -r requirements.txt`
- While running, if some issue comes install above packages.


### To Run
1. `sh run.sh` OR
1. Open `public/YouTubeDownloader.app` file.

### To Release
1. Create the .app.
    - `python3 release_setup.py py2app`
2. Prepare a temporary Staging folder.
    - `mkdir -p dmg-staging`
    - `cp -R "dist/TubeGrabber.app" dmg-staging/`
    - `ln -s /Applications dmg-staging/Applications`
2. Create the .dmg file.
    - `mkdir -p public`
    - `hdiutil create -volname "TubeGrabber" -srcfolder "dmg-staging" -ov -format UDZO "public/TubeGrabber-0.1.dmg"`