"""Simple YouTube video downloader with a Tkinter UI, powered by yt-dlp.

Only download videos you have the right to download (your own content,
Creative Commons, or with the owner's permission).
"""

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import yt_dlp


class DownloaderApp:
    def __init__(self, root):
        self.root = root
        root.title("YouTube Downloader")
        root.geometry("560x220")
        root.resizable(False, False)

        self.url_var = tk.StringVar()
        self.dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.status_var = tk.StringVar(value="Paste a video link and click Download.")

        frm = ttk.Frame(root, padding=12)
        frm.pack(fill="both", expand=True)
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="Video URL:").grid(row=0, column=0, sticky="w")
        url_entry = ttk.Entry(frm, textvariable=self.url_var)
        url_entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=4)
        url_entry.focus()

        ttk.Label(frm, text="Save to:").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.dir_var).grid(row=1, column=1, sticky="ew", pady=4)
        ttk.Button(frm, text="Browse…", command=self.choose_dir).grid(row=1, column=2, padx=(6, 0))

        self.progress = ttk.Progressbar(frm, mode="determinate", maximum=100)
        self.progress.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(12, 4))

        ttk.Label(frm, textvariable=self.status_var).grid(row=3, column=0, columnspan=3, sticky="w")

        self.download_btn = ttk.Button(frm, text="Download", command=self.start_download)
        self.download_btn.grid(row=4, column=0, columnspan=3, pady=(12, 0))

        root.bind("<Return>", lambda _e: self.start_download())

    def choose_dir(self):
        path = filedialog.askdirectory(initialdir=self.dir_var.get())
        if path:
            self.dir_var.set(path)

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please paste a video link.")
            return
        if str(self.download_btn["state"]) == "disabled":
            return
        self.download_btn.config(state="disabled")
        self.progress["value"] = 0
        self.status_var.set("Starting…")
        threading.Thread(target=self.download, args=(url, self.dir_var.get()), daemon=True).start()

    def download(self, url, out_dir):
        opts = {
            "outtmpl": str(Path(out_dir) / "%(title)s.%(ext)s"),
            # Best single file with audio+video so ffmpeg isn't required.
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "progress_hooks": [self.on_progress],
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            title = info.get("title", "video")
            self.ui(lambda: self.finish(f"Done: {title}", ok=True))
        except Exception as exc:  # yt-dlp raises various error types
            msg = str(exc)
            self.ui(lambda: self.finish(f"Error: {msg}", ok=False))

    def on_progress(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            done = d.get("downloaded_bytes", 0)
            pct = done / total * 100 if total else 0
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            self.ui(lambda: self.update_progress(pct, f"Downloading… {pct:.1f}%  {speed}  ETA {eta}"))
        elif d["status"] == "finished":
            self.ui(lambda: self.update_progress(100, "Finalizing…"))

    def ui(self, fn):
        # Tkinter isn't thread-safe; schedule UI updates on the main loop.
        self.root.after(0, fn)

    def update_progress(self, pct, text):
        self.progress["value"] = pct
        self.status_var.set(text)

    def finish(self, text, ok):
        self.status_var.set(text)
        self.download_btn.config(state="normal")
        if ok:
            self.progress["value"] = 100
        else:
            messagebox.showerror("Download failed", text)


if __name__ == "__main__":
    root = tk.Tk()
    DownloaderApp(root)
    root.mainloop()
