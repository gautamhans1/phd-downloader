import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog
import os
import subprocess
import sys
from queue import Queue
import threading

class VideoDownloaderGUI:
    def __init__(self, app, download_video_func):
        self.app = app
        self.message_queue = Queue()
        self.download_video_func = download_video_func
        self.setup_ui()

    def setup_ui(self):
        self.app.title("Video Downloader")
        self.app.geometry("800x600")

        self.app.lift()
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 14), padding="0.5em")
        style.configure("TEntry", font=("Helvetica", 14), padding="0.5em")
        style.configure("TButton", font=("Helvetica", 14), padding="0.5em 1em")
        style.configure("TText", font=("Helvetica", 14), padding="0.5em")
        style.configure("TFrame", background="white", padding="1em")
        style.configure("TLabelframe", background="white", padding="1em")

        self.frame = ttk.Frame(self.app)
        self.frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_rowconfigure(3, weight=3)
        self.frame.grid_rowconfigure(4, weight=5)
        self.frame.grid_columnconfigure(0, weight=1)

        self.default_download_path_label = ttk.Label(self.frame, text="Default Download Path:")
        self.default_download_path_label.grid(row=0, column=0, sticky="w")

        self.default_download_path = ttk.Entry(self.frame, width=70)
        self.default_download_path.insert(tk.END, os.path.expanduser("~/Downloads/jellyfin/phd/"))
        self.default_download_path.grid(row=1, column=0, columnspan=3, sticky="ew")

        self.browse_button = ttk.Button(self.frame, text="Browse", command=self.browse_download_path)
        self.browse_button.grid(row=1, column=3, padx=5, pady=5)

        self.open_button = ttk.Button(self.frame, text="Open Download Path", command=self.open_download_path)
        self.open_button.grid(row=1, column=4, padx=5, pady=5)

        self.url_label = ttk.Label(self.frame, text="Enter the video URL(s), each on a new line:")
        self.url_label.grid(row=2, column=0, sticky="w")

        self.url_text = scrolledtext.ScrolledText(self.frame, height=5, wrap=tk.WORD)
        self.url_text.grid(row=3, column=0, columnspan=5, sticky="nsew")

        self.terminal_label = ttk.Label(self.frame, text="Terminal Output:")
        self.terminal_label.grid(row=4, column=0, sticky="w")

        self.terminal_text = scrolledtext.ScrolledText(self.frame, height=15, bg='black', fg='white', wrap=tk.WORD)
        self.terminal_text.grid(row=5, column=0, columnspan=5, sticky="nsew")
        self.terminal_text.config(state=tk.DISABLED, font=("Courier", 12))

        self.terminal_text.tag_config('DEBUG', foreground='cyan')
        self.terminal_text.tag_config('WARNING', foreground='yellow')
        self.terminal_text.tag_config('ERROR', foreground='red')
        self.terminal_text.tag_config('CRITICAL', foreground='red', background='white')

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.grid(row=6, column=0, columnspan=5, pady=(10, 0))

        self.download_button = ttk.Button(self.button_frame, text="Download", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = ttk.Button(self.button_frame, text="Clear Logs", command=self.clear_terminal)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))

    def append_to_terminal(self, message, level='INFO'):
        self.terminal_text.config(state=tk.NORMAL)
        self.terminal_text.insert(tk.END, f"{message}", level.upper())
        self.terminal_text.insert(tk.END, "\n")
        self.terminal_text.config(state=tk.DISABLED)
        self.terminal_text.see(tk.END)

    def clear_terminal(self):
        self.terminal_text.config(state=tk.NORMAL)
        self.terminal_text.delete(1.0, tk.END)
        self.terminal_text.config(state=tk.DISABLED)

    def browse_download_path(self):
        path = filedialog.askdirectory()
        if path:
            self.default_download_path.delete(0, tk.END)
            self.default_download_path.insert(tk.END, path)

    def open_download_path(self):
        download_path = self.default_download_path.get()
        if os.path.exists(download_path):
            if sys.platform == "win32":
                os.startfile(download_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", download_path])
            else:  # Assume Unix-like
                subprocess.Popen(["xdg-open", download_path])
        else:
            self.append_to_terminal(f"Download path does not exist: {download_path}", 'ERROR')

    def start_download(self):
        try:
            urls = [url.strip() for url in self.url_text.get("1.0", tk.END).splitlines() if url.strip()]
            if not urls:
                raise ValueError("No valid URLs provided.")
            download_path = self.default_download_path.get()
            self.download_video_func(urls, download_path, self.message_queue)
        except Exception as e:
            self.append_to_terminal(f"Error starting download: {e}", 'ERROR')

    def process_messages(self):
        while not self.message_queue.empty():
            message, level = self.message_queue.get()
            self.append_to_terminal(message, level)
        self.app.after(100, self.process_messages)