import subprocess
import threading
from queue import Queue
import colorlog
import logging
import os
import glob

def setup_logger():
    logger = colorlog.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)s:%(name)s:%(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    logger.addHandler(handler)
    return logger

logger = setup_logger()

def start_aria2c():
    try:
        subprocess.Popen(["aria2c", "--enable-rpc", "--rpc-listen-all", "--summary-interval=1", "--log-level=notice", "--log=/dev/null"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("aria2c server started")
    except Exception as e:
        logger.error(f"Error starting aria2c server: {e}")
        raise RuntimeError("Failed to start aria2c server. Please check your system configuration.")

def cleanup_php_files(download_path):
    php_files = glob.glob(os.path.join(download_path, '*.php'))
    for file in php_files:
        try:
            os.remove(file)
            logger.info(f"Removed unwanted file: {file}")
        except Exception as e:
            logger.error(f"Error removing file {file}: {e}")

def run_command(command, message_queue, retry_failed=False):
    try:
        command.extend(["--match-filter", "!is_live & !playlist & ext!='php'"])
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in process.stdout:
            logger.info(line.strip())
            message_queue.put((line.strip(), 'info'))

        for line in process.stderr:
            logger.error(line.strip())
            message_queue.put((line.strip(), 'error'))

        process.wait()

        if process.returncode != 0 and retry_failed:
            logger.warning(f"Command failed, retrying: {' '.join(command)}")
            message_queue.put((f"Command failed, retrying: {' '.join(command)}", 'warning'))
            run_command(command, message_queue, retry_failed)
        elif process.returncode != 0:
            logger.error(f"Command failed: {' '.join(command)}")
            message_queue.put((f"Command failed: {' '.join(command)}", 'error'))
            raise subprocess.CalledProcessError(process.returncode, command)

    except Exception as e:
        logger.error(f"Error running command: {e}")
        message_queue.put((f"Error running command: {e}", 'error'))
        raise e

def download_video(urls, download_path, message_queue):
    def run_download_command():
        try:
            start_aria2c()
        except RuntimeError as e:
            logger.error(str(e))
            message_queue.put((str(e), 'error'))
            return

        total_videos = len(urls)
        for index, url in enumerate(urls, start=1):
            logger.info(f"Downloading video {index} of {total_videos} from URL: {url}")
            message_queue.put((f"Downloading video {index} of {total_videos} from URL: {url}", 'info'))
            command = [
                "yt-dlp",
                "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--output", f"{os.path.join(download_path, '%(title)s.%(ext)s')}",
                "--merge-output-format", "mp4",
                "--external-downloader", "aria2c",
                "--external-downloader-args", "aria2c:--max-connection-per-server=16 --min-split-size=1M --summary-interval=1",
                url
            ]
            try:
                run_command(command, message_queue, retry_failed=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Error downloading video {index} of {total_videos}: {url}")
                message_queue.put((f"Error downloading video {index} of {total_videos}: {url}", 'error'))
            except Exception as e:
                logger.error(f"Unexpected error downloading video {index} of {total_videos}: {url}")
                message_queue.put((f"Unexpected error downloading video {index} of {total_videos}: {url}", 'error'))
            else:
                logger.info(f"Successfully downloaded video {index} of {total_videos}: {url}")
                message_queue.put((f"Successfully downloaded video {index} of {total_videos}: {url}", 'info'))

        cleanup_php_files(download_path)

    download_thread = threading.Thread(target=run_download_command)
    download_thread.start()