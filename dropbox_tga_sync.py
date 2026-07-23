"""
Dropbox TGA Sync
-----------------
Downloads a Dropbox *shared folder* link as a zip, extracts every .tga file
found anywhere inside it (including subfolders), and copies them into one
flat destination folder on your PC.

Run it, pick your destination folder once (it's remembered), then click
"Sync Now" any time you want fresh files.

Requirements:
    pip install requests

Run:
    python dropbox_tga_sync.py
"""

import io
import json
import os
import shutil
import threading
import zipfile
from pathlib import Path

import requests

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ImportError:
    raise SystemExit(
        "tkinter isn't installed. On Windows/Mac it normally ships with "
        "Python. On Linux, install it with: sudo apt install python3-tk"
    )

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Paste your Dropbox shared folder link here (the dl=0/dl=1 part is handled
# automatically, don't worry about it).
DROPBOX_SHARE_LINK = (
    "https://www.dropbox.com/scl/fo/kdzc0x3xplbj3srgv1370/"
    "ADjYBXy_RIGPf9VXvEsS9nY?rlkey=rg7vr8bngppst5klsz0qiinfo"
    "&st=nco1gyvm&dl=0"
)

CONFIG_PATH = Path.home() / ".dropbox_tga_sync_config.json"
DEFAULT_DESTINATION = Path.home() / "Documents" / "Neverwinter Nights" / "portraits"


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def to_zip_download_url(share_link: str) -> str:
    """Convert a Dropbox shared-folder link into one that downloads a zip."""
    if "dl=1" in share_link:
        return share_link
    if "dl=0" in share_link:
        return share_link.replace("dl=0", "dl=1")
    sep = "&" if "?" in share_link else "?"
    return f"{share_link}{sep}dl=1"


def load_last_destination() -> str:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text()).get("destination", "")
        except Exception:
            return ""
    return str(DEFAULT_DESTINATION)


def save_last_destination(path: str) -> None:
    CONFIG_PATH.write_text(json.dumps({"destination": path}))


def sync(destination: str, log) -> int:
    """Download the folder, pull out .tga files, copy to destination.
    Returns the number of files copied/updated."""
    os.makedirs(destination, exist_ok=True)

    url = to_zip_download_url(DROPBOX_SHARE_LINK)
    log(f"Downloading from Dropbox...")

    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, stream=True, timeout=120)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    buf = io.BytesIO()
    downloaded = 0
    chunk_size = 1024 * 256
    for chunk in resp.iter_content(chunk_size=chunk_size):
        if not chunk:
            continue
        buf.write(chunk)
        downloaded += len(chunk)
        if total:
            log(f"Downloading... {downloaded / 1_048_576:.1f} / {total / 1_048_576:.1f} MB", replace=True)
        else:
            log(f"Downloading... {downloaded / 1_048_576:.1f} MB", replace=True)

    log("Download complete. Extracting .tga files (including inside nested .zips)...")

    buf.seek(0)
    copied = 0
    skipped = 0

    def handle_zip_bytes(zip_bytes, depth=0):
        nonlocal copied, skipped
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue

                lower_name = info.filename.lower()

                if lower_name.endswith(".tga"):
                    filename = os.path.basename(info.filename)
                    dest_path = os.path.join(destination, filename)

                    with zf.open(info) as src:
                        data = src.read()

                    # Skip rewriting identical files to keep re-syncs fast.
                    if os.path.exists(dest_path) and os.path.getsize(dest_path) == len(data):
                        with open(dest_path, "rb") as existing:
                            if existing.read() == data:
                                skipped += 1
                                continue

                    with open(dest_path, "wb") as out:
                        out.write(data)
                    copied += 1
                    log(f"Saved: {filename}")

                elif lower_name.endswith(".zip") and depth < 5:
                    # Recurse into nested zip files, wherever they are found.
                    with zf.open(info) as nested_src:
                        nested_bytes = nested_src.read()
                    log(f"Opening nested zip: {os.path.basename(info.filename)}")
                    try:
                        handle_zip_bytes(nested_bytes, depth=depth + 1)
                    except zipfile.BadZipFile:
                        log(f"Warning: could not open nested zip {info.filename} (corrupt or not a zip)")

    handle_zip_bytes(buf.read())

    log(f"Done. {copied} file(s) copied/updated, {skipped} already up to date.")
    return copied


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class App:
    def __init__(self, root):
        self.root = root
        root.title("Dropbox TGA Sync")
        root.geometry("560x420")
        root.resizable(False, False)

        self.destination = tk.StringVar(value=load_last_destination())

        tk.Label(root, text="Destination folder for .tga files:", anchor="w").pack(
            fill="x", padx=12, pady=(12, 2)
        )

        frame = tk.Frame(root)
        frame.pack(fill="x", padx=12)
        tk.Entry(frame, textvariable=self.destination).pack(
            side="left", fill="x", expand=True
        )
        tk.Button(frame, text="Browse...", command=self.browse).pack(
            side="left", padx=(6, 0)
        )

        self.sync_button = tk.Button(
            root, text="Sync Now", command=self.start_sync, height=2, bg="#0061FF", fg="white"
        )
        self.sync_button.pack(fill="x", padx=12, pady=12)

        tk.Label(root, text="Log:", anchor="w").pack(fill="x", padx=12)
        self.log_box = tk.Text(root, height=14, state="disabled", wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination.set(folder)

    def log(self, message, replace=False):
        def update():
            self.log_box.config(state="normal")
            if replace:
                # Replace the last line instead of adding a new one
                last_line_start = self.log_box.index("end-2l")
                self.log_box.delete(last_line_start, "end-1l")
                self.log_box.insert(last_line_start, message + "\n")
            else:
                self.log_box.insert("end", message + "\n")
            self.log_box.see("end")
            self.log_box.config(state="disabled")
        self.root.after(0, update)

    def start_sync(self):
        dest = self.destination.get().strip()
        if not dest:
            messagebox.showwarning("No destination", "Please choose a destination folder first.")
            return

        save_last_destination(dest)
        self.sync_button.config(state="disabled", text="Syncing...")
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

        def worker():
            try:
                self.log(f"Syncing to: {dest}")
                self.sync(dest)
            except Exception as e:
                self.log(f"Error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Sync failed", str(e)))
            finally:
                self.root.after(0, lambda: self.sync_button.config(state="normal", text="Sync Now"))

        threading.Thread(target=worker, daemon=True).start()

    def sync(self, dest):
        sync(dest, self.log)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
