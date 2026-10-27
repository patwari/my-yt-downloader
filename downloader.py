import itertools
import json
import os
import queue
import signal
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = 8765
HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}
UI = Path(__file__).with_name("ui.html")

QUALITY = {
    "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "2k": "bestvideo[height<=1440]+bestaudio/best[height<=1440]",
    "4k": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
    "best": "bv*+ba/b",
}
BITRATES = {"best", "192", "128"}  # MP3 kbps, "best" = highest-quality VBR; YouTube audio is ~130 kbps

# One machine-readable line per progress tick; \x1f can't appear in titles, so splitting is safe
SEP = "\x1f"
PROGRESS = "TG " + SEP.join(
    [
        "%(progress.status)s",
        "%(progress.downloaded_bytes)s",
        "%(progress.total_bytes,progress.total_bytes_estimate)s",
        "%(progress.speed)s",
        "%(progress.eta)s",
        "%(info.playlist_index)s",
        "%(info.n_entries,info.playlist_count)s",
        "%(info.playlist_title)s",
        "%(info.title)s",
    ]
)

jobs = {}  # id -> job dict (JSON-safe), insertion ordered
procs = {}  # id -> running Popen
lock = threading.Lock()
work = queue.Queue()
next_id = itertools.count(1)


def build_cmd(job):
    url, folder = job["url"], job["folder"]
    if "list=" in url:
        name = "%(playlist_index)s. %(title)s.%(ext)s" if job["numbering"] else "%(title)s.%(ext)s"
        outtmpl = os.path.join(folder, "%(playlist_title)s", name)
    else:
        outtmpl = os.path.join(folder, "%(title)s.%(ext)s")

    cmd = [
        sys.executable,  # the venv's Python, so it runs the yt-dlp that run.sh keeps updated
        "-m",
        "yt_dlp",
        "--newline",
        "--progress",
        "--progress-template",
        f"download:{PROGRESS}",
        "--print",
        f"after_move:TGFILE %(playlist_index)s{SEP}%(title)s{SEP}%(filepath)s",
        "--js-runtimes",
        "node",  # YouTube needs a JS runtime; deno is the default, node is the fallback
        "-o",
        outtmpl,
    ]
    if job["format"] == "mp3":
        quality = "0" if job["bitrate"] == "best" else f"{job['bitrate']}K"
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", quality, "--embed-metadata", "--embed-thumbnail"]
    else:
        # Prefer plain https over HLS (m3u8): HLS format 616 ("Premium") stalled a playlist with one fragment crawling at ~1 KB/s
        cmd += ["-f", QUALITY.get(job["quality"], QUALITY["best"]), "-S", "proto:https", "--merge-output-format", "mp4"]
        if job["aria"]:
            cmd += ["--external-downloader", "aria2c", "--external-downloader-args", "-x 16 -k 1M"]
    # "--" so a pasted line can never be read as a yt-dlp option
    return cmd + ["--", url]


def reset(job):
    job.update(
        status="queued", stage=None, title=None, playlist=None, index=None, count=None,
        percent=None, speed=None, eta=None, completed=0, file=None, errors=[], items=[],
    )


def current_item(job, index, title):
    # yt-dlp works through a playlist in order, so a new index/title means it moved to the next one.
    # Files that already exist only print TGFILE, so both line types go through here.
    items = job["items"]
    if not items or (items[-1]["index"], items[-1]["title"]) != (index, title):
        if items and items[-1]["status"] != "done":
            items[-1]["status"] = "error"  # moved on without saving it
        items.append({"index": index, "title": title, "status": None, "percent": None})
    return items[-1]


def number(value):
    return None if value == "NA" else float(value)


def run(job):
    with lock:
        if job["status"] != "queued":  # cancelled while waiting
            return
        proc = subprocess.Popen(
            build_cmd(job),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            start_new_session=True,  # own process group, so cancel also kills ffmpeg/aria2c
            env={**os.environ, "PYTHONUNBUFFERED": "1"},  # progress lines arrive live
        )
        procs[job["id"]] = proc
        job["status"] = "running"

    for line in proc.stdout:
        line = line.rstrip("\n")
        with lock:
            if line.startswith("TG "):
                status, done, total, speed, eta, index, count, playlist, title = line[3:].split(SEP, 8)
                done, total = number(done), number(total)
                job.update(
                    stage="processing" if status == "finished" else "downloading",
                    percent=round(100 * done / total, 1) if done and total else None,
                    speed=number(speed),
                    eta=number(eta),
                    index=None if index == "NA" else int(index),
                    count=None if count == "NA" else int(count),
                    playlist=None if playlist == "NA" else playlist,
                    title=title,
                )
                current_item(job, job["index"], title).update(status=job["stage"], percent=job["percent"])
                continue
            if line.startswith("TGFILE "):
                index, title, path = line[7:].split(SEP, 2)
                current_item(job, None if index == "NA" else int(index), title).update(status="done", percent=100)
                job.update(file=path, completed=job["completed"] + 1, stage=None, percent=100)
            elif line.startswith("ERROR:"):
                job["errors"].append(line[6:].strip())
        print(f"[{job['id']}] {line}")

    code = proc.wait()
    with lock:
        procs.pop(job["id"], None)
        if job["status"] == "running":
            job["status"] = "done" if code == 0 else "error"
        job["stage"] = None
        if job["items"] and job["items"][-1]["status"] != "done":
            job["items"][-1]["status"] = "cancelled" if job["status"] == "cancelled" else "error"


def worker():
    while True:
        run(work.get())


def kill(job_id):
    proc = procs.get(job_id)
    if proc:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass


def add_jobs(data):
    folder = os.path.expanduser(str(data.get("folder") or "").strip())
    lines = [l.strip() for l in str(data.get("links") or "").splitlines() if l.strip()]
    if not folder or not lines:
        return {"error": "Add at least one link and a folder."}
    bad = next((l for l in lines if not l.startswith(("http://", "https://"))), None)
    if bad:
        return {"error": f"Not a link: {bad}"}
    for line in lines:
        job = {
            "id": next(next_id),
            "url": line,
            "folder": folder,
            "format": "mp4" if data.get("format") == "mp4" else "mp3",
            "quality": data.get("quality") if data.get("quality") in QUALITY else "best",
            "bitrate": data.get("bitrate") if data.get("bitrate") in BITRATES else "best",
            "numbering": bool(data.get("numbering", True)),
            "aria": bool(data.get("aria")),
        }
        reset(job)
        jobs[job["id"]] = job
        work.put(job)
    return {"added": len(lines)}


def job_action(job_id, action):
    job = jobs.get(job_id)
    if not job:
        return {"error": "No such job."}
    if action == "cancel" and job["status"] in ("queued", "running"):
        job["status"] = "cancelled"
        kill(job_id)
    elif action == "retry" and job["status"] in ("error", "cancelled", "done"):
        reset(job)
        work.put(job)
    elif action == "reveal":
        target = job["file"] if job["file"] and os.path.exists(job["file"]) else job["folder"]
        subprocess.run(["open", "-R", target] if target == job["file"] else ["open", target])
    return {}


def choose_folder():
    result = subprocess.run(
        ["osascript", "-e", "activate", "-e", 'POSIX path of (choose folder with prompt "Download to")'],
        capture_output=True,
        text=True,
    )
    return {"folder": result.stdout.strip()}  # empty when the dialog is cancelled


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # the UI polls every second; keep the terminal for yt-dlp output

    def trusted(self):
        # Only our own page may drive this server: blocks other sites (CSRF) and DNS rebinding
        host = self.headers.get("Host", "")
        origin = self.headers.get("Origin")
        if host in HOSTS and origin in (None, f"http://{host}"):
            return True
        self.reply(403, {"error": "forbidden"})
        return False

    def reply(self, code, body, content_type="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self.trusted():
            return
        if self.path == "/":
            self.reply(200, UI.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/jobs":
            with lock:
                body = json.dumps(list(jobs.values())).encode()
            self.reply(200, body)
        else:
            self.reply(404, {"error": "not found"})

    def do_POST(self):
        if not self.trusted():
            return
        if self.headers.get("Content-Type") != "application/json":
            return self.reply(415, {"error": "JSON only"})
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except ValueError:
            return self.reply(400, {"error": "bad JSON"})

        parts = self.path.strip("/").split("/")  # e.g. api/jobs/3/cancel
        if parts == ["api", "browse"]:
            return self.reply(200, choose_folder())
        with lock:
            if parts == ["api", "jobs"]:
                result = add_jobs(data)
            elif parts == ["api", "clear"]:
                for job_id in [i for i, j in jobs.items() if j["status"] in ("done", "error", "cancelled")]:
                    del jobs[job_id]
                result = {}
            elif len(parts) == 4 and parts[:2] == ["api", "jobs"] and parts[2].isdigit():
                result = job_action(int(parts[2]), parts[3])
            else:
                return self.reply(404, {"error": "not found"})
        self.reply(400 if "error" in result else 200, result)


if __name__ == "__main__":
    url = f"http://127.0.0.1:{PORT}"
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:  # port taken: most likely TubeGrabber is already running
        print(f"Port {PORT} in use, opening the existing instance at {url}")
        webbrowser.open(url)
        sys.exit()

    threading.Thread(target=worker, daemon=True).start()
    print(f"TubeGrabber running at {url}  (Ctrl+C to quit)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for job_id in list(procs):
            kill(job_id)
