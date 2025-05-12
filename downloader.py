import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import re

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)

def is_playlist(link):
    return "list=" in link

def get_playlist_length(link):
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "%(id)s", link],
            capture_output=True, text=True
        )
        count = len(result.stdout.strip().splitlines())
        return count
    except Exception as e:
        print("Error fetching playlist length:", e)
        return 0

def update_link_type_text(*args):
    link = link_var.get().strip()
    if not link:
        link_type_label.config(text="Link Type: NA")
        return
    
    if is_playlist(link):
        link_type_label.config(text="Link Type: Playlist")
    else:
        link_type_label.config(text="Link Type: Single File")

def update_quality_options(*args):
    fmt = format_var.get()
    if fmt == "mp4":
        quality_menu.config(state="readonly")
        aria_check.config(state="normal")
    else:
        quality_menu.config(state="disabled")
        aria_check.config(state="disabled")

def toggle_concurrent_dropdown():
    if aria_var.get():
        concurrency_menu.config(state="disabled")
    else:
        concurrency_menu.config(state="normal")

def update_concurrent_label_color():
    if aria_var.get():
        concurrent_label.config(foreground="grey")  # Greyed out
    else:
        concurrent_label.config(foreground="white")  # Active

def start_download():
    link = link_var.get().strip()
    folder = folder_var.get().strip()
    fmt = format_var.get()
    quality = quality_var.get()
    use_aria = aria_var.get()
    concurrency = concurrency_var.get()

    if not link or not folder:
        messagebox.showerror("Error", "Please provide both the link and folder.")
        return

    if is_playlist(link):
        count = get_playlist_length(link)
        pad_width = len(str(count)) if count else 2
        outtmpl = f'{folder}/%(playlist_title)s/%(playlist_index)0{pad_width}d. %(title)s.%(ext)s'
    else:
        outtmpl = f'{folder}/%(title)s.%(ext)s'

    if fmt == "mp3":
        base_cmd = f'yt-dlp -x --audio-format mp3 --audio-quality 0 ' \
                   f'--embed-metadata --embed-thumbnail ' \
                   f'-o "{outtmpl}" "{link}"'
    else:
        quality_map = {
            "720p": "bestvideo[height<=720]+bestaudio",
            "1080p": "bestvideo[height<=1080]+bestaudio",
            "2k": "bestvideo[height<=1440]+bestaudio",
            "4k": "bestvideo[height<=2160]+bestaudio",
            "best": "bv*+ba/b"
        }
        format_selector = quality_map.get(quality, "bv*+ba/b")
        base_cmd = f'yt-dlp -f "{format_selector}" --merge-output-format mp4 -o "{outtmpl}" '

        if use_aria:
            base_cmd += '--external-downloader aria2c --external-downloader-args "-x 16 -k 1M" '
        else:
            base_cmd += f'--concurrent-fragments {concurrency} --throttled-rate 0 '

        base_cmd += f'"{link}"'

    # Optional: keep Terminal open after execution
    # base_cmd += f' "; echo "Done!"; read'

    # Escape for AppleScript
    escaped_cmd = base_cmd.replace('"', '\\"')

    print("Command to be executed:\n", base_cmd)

    # Use proper AppleScript line-by-line invocation
    subprocess.run([
        "osascript",
        "-e", 'tell application "Terminal"',
        "-e", 'activate',
        "-e", f'do script "{escaped_cmd}"',
        "-e", 'end tell'
    ])

# GUI Setup
root = tk.Tk()
root.title("Tube Grabber")
root.geometry("1000x600")  # Increase window size

link_var = tk.StringVar()
default_path = os.path.expanduser("~/Downloads/YouTube")
folder_var = tk.StringVar(value=default_path)
format_var = tk.StringVar(value="mp3")
quality_var = tk.StringVar(value="best")
aria_var = tk.BooleanVar(value=False)
concurrency_var = tk.StringVar(value="4")

# Layout
tk.Label(root, text="YouTube Link:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
link_entry = tk.Entry(root, textvariable=link_var, width=65)
link_entry.grid(row=0, column=1, padx=10)
link_var.trace_add("write", update_link_type_text)
# Update link type dynamically when the link changes

# Link Type Display
link_type_label = tk.Label(root, text="Link Type: NA", anchor='w', padx=10, pady=5)
link_type_label.grid(row=1, column=1, sticky='w', padx=10)

# Target Folder
tk.Label(root, text="Target Folder:").grid(row=3, column=0, sticky='w', padx=10, pady=10)
path_frame = tk.Frame(root)
path_frame.grid(row=3, column=1, padx=10, pady=5, sticky='w')
tk.Entry(path_frame, textvariable=folder_var, width=45).pack(side='left')
tk.Button(path_frame, text="Browse", command=browse_folder).pack(side='left', padx=(5, 0))

# Format Dropdown
tk.Label(root, text="Format:").grid(row=4, column=0, sticky='w', padx=10, pady=10)
tt = ttk.Combobox(root, textvariable=format_var, values=["mp3", "mp4"], state="readonly", width=10)
tt.grid(row=4, column=1, padx=10)
tt.bind("<<ComboboxSelected>>", update_quality_options)

# Quality Dropdown
quality_options = ["720p", "1080p", "2k", "4k", "best"]
tk.Label(root, text="Max Video Quality:").grid(row=5, column=0, sticky='w', padx=10, pady=10)
quality_menu = ttk.Combobox(root, textvariable=quality_var, values=quality_options, state="disabled", width=10)
quality_menu.grid(row=5, column=1, padx=10)

# Aria2 checkbox - valid only for mp4
aria_check = tk.Checkbutton(root, text="Use aria2c downloader", variable=aria_var, state="disabled")
aria_check.grid(row=6, column=0, sticky='w', padx=10, pady=10)
aria_check.select()
aria_check.config(command=lambda: [toggle_concurrent_dropdown(), update_concurrent_label_color()])

# Concurrent Fragments label
concurrent_label = tk.Label(root, text="Concurrent Fragments (yt-dlp only):", foreground="grey")
concurrent_label.grid(row=7, column=0, sticky='w', padx=10, pady=10)

# Concurrent Fragments dropdown
concurrency_menu = ttk.Combobox(root, textvariable=concurrency_var, values=[str(i) for i in range(1, 16)], state="disabled", width=5)
concurrency_menu.grid(row=7, column=1, padx=10)

# Add Numbering checkbox
add_numbering_var = tk.BooleanVar(value=True)
add_numbering_check = tk.Checkbutton(root, text="Add Numbering to Playlist", variable=add_numbering_var)
add_numbering_check.grid(row=8, column=1, padx=10, pady=10, sticky='w')

# Download button
download_button = tk.Button(root, text="Download", command=start_download, bg="white", fg="black", width=20, height=2)
download_button.grid(row=9, column=1, pady=20)

root.mainloop()
