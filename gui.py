import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
import subprocess
import sys
from queue import Queue
import threading
import config

class VideoDownloaderGUI:
    def __init__(self, app, download_video_func):
        self.app = app
        self.message_queue = Queue()
        self.download_video_func = download_video_func
        self.setup_ui()
        
    def save_download_path(self):
        config.set_default_download_path(self.default_download_path.get())

    def setup_ui(self):
        self.app.title("Video Downloader")
        self.app.geometry("800x600")
        self.app.minsize(600, 400)

        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(0, weight=1)

        self.frame = ttk.Frame(self.app, padding="10")
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_rowconfigure(4, weight=3)

        # Download Path
        path_frame = ttk.Frame(self.frame)
        path_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        path_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(path_frame, text="Default Download Path:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.default_download_path = ttk.Entry(path_frame)
        # self.default_download_path.insert(tk.END, os.path.expanduser("~/Downloads/jellyfin/phd/"))
        self.default_download_path.insert(tk.END, config.get_default_download_path())
        self.default_download_path.grid(row=0, column=1, sticky="ew")
        self.default_download_path.bind("<FocusOut>", lambda e: self.save_download_path())
        ttk.Button(path_frame, text="Browse", command=self.browse_download_path).grid(row=0, column=2, padx=5)
        ttk.Button(path_frame, text="Open Download Path", command=self.open_download_path).grid(row=0, column=3)

        # URL Input
        ttk.Label(self.frame, text="Enter the video URL(s), each on a new line:").grid(row=1, column=0, sticky="w", pady=(10, 5))
        
        # Create a frame to hold the Text widget and scrollbar
        url_frame = ttk.Frame(self.frame)
        url_frame.grid(row=2, column=0, sticky="nsew")
        url_frame.grid_columnconfigure(0, weight=1)
        url_frame.grid_rowconfigure(0, weight=1)

        # Create Text widget and scrollbar
        self.url_text = tk.Text(url_frame, height=5, wrap=tk.WORD)
        self.url_text.grid(row=0, column=0, sticky="nsew")
        url_scrollbar = ttk.Scrollbar(url_frame, orient="vertical", command=self.url_text.yview)
        url_scrollbar.grid(row=0, column=1, sticky="ns")
        self.url_text.config(yscrollcommand=url_scrollbar.set)

        # Bind right-click event
        self.url_text.bind("<Button-3>", self.show_context_menu)

        # Create context menu
        self.context_menu = tk.Menu(self.url_text, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.url_text.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copy", command=lambda: self.url_text.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Paste", command=lambda: self.url_text.event_generate("<<Paste>>"))

        # Terminal Output
        ttk.Label(self.frame, text="Terminal Output:").grid(row=3, column=0, sticky="w", pady=(10, 5))
        self.terminal_text = scrolledtext.ScrolledText(self.frame, height=15, bg='black', fg='white', wrap=tk.WORD)
        self.terminal_text.grid(row=4, column=0, sticky="nsew")
        self.terminal_text.config(state=tk.DISABLED, font=("Courier", 12))

        # Configure tags for different message levels
        self.terminal_text.tag_config('DEBUG', foreground='cyan')
        self.terminal_text.tag_config('WARNING', foreground='yellow')
        self.terminal_text.tag_config('ERROR', foreground='red')
        self.terminal_text.tag_config('CRITICAL', foreground='red', background='white')

        # Buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=5, column=0, pady=(10, 0), sticky="e")
        ttk.Button(button_frame, text="Download", command=self.start_download).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear Logs", command=self.clear_terminal).pack(side=tk.LEFT)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def browse_download_path(self):
        path = filedialog.askdirectory()
        if path:
            self.default_download_path.delete(0, tk.END)
            self.default_download_path.insert(tk.END, path)
            self.save_download_path()

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
            download_path = self.default_download_path.get()
            self.download_video_func(urls, download_path, self.message_queue)
        except Exception as e:
            self.append_to_terminal(f"Error starting download: {e}", 'ERROR')

    def append_to_terminal(self, message, level='INFO'):
        self.terminal_text.config(state=tk.NORMAL)
        self.terminal_text.insert(tk.END, f"{message}\n", level.upper())
        self.terminal_text.config(state=tk.DISABLED)
        self.terminal_text.see(tk.END)

    def clear_terminal(self):
        self.terminal_text.config(state=tk.NORMAL)
        self.terminal_text.delete(1.0, tk.END)
        self.terminal_text.config(state=tk.DISABLED)

    def process_messages(self):
        while not self.message_queue.empty():
            message, level = self.message_queue.get()
            self.append_to_terminal(message, level)
        self.app.after(100, self.process_messages)