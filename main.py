import tkinter as tk
from gui import VideoDownloaderGUI
from downloader import download_video

def main():
    app = tk.Tk()
    gui = VideoDownloaderGUI(app, download_video)
    app.after(100, gui.process_messages)
    app.mainloop()

if __name__ == "__main__":
    main()