import json
import os

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"default_download_path": os.path.expanduser("~/Downloads/jellyfin/phd/")}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def get_default_download_path():
    return load_config()["default_download_path"]

def set_default_download_path(path):
    config = load_config()
    config["default_download_path"] = path
    save_config(config)