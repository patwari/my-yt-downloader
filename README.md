# MY Youtube Downloader (MacOS) - TubeGrabber

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
1. Open `public/TubeGrabber-xx.app` file.

### To Release
1. `sh release.sh`