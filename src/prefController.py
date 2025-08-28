import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PREF_FILE = os.path.join(SCRIPT_DIR, "pref.json")

def load_pref():
    print(f"[DEBUG] Loading config from: {PREF_FILE}")
    if os.path.exists(PREF_FILE):
        with open(PREF_FILE, "r") as f:
            config = json.load(f)
            print("[DEBUG] Config loaded:", json.dumps(config, indent=2))
            return config
    else:
        print("[DEBUG] Config file not found, creating default config.")
        config = {}
        for i in range(1, 10):
            config[f"BUTTON_{i}"] = {"type": "none", "value": ""}
        config["BUTTON_1"] = {"type": "link", "value": "https://www.youtube.com"}
        return config

def save_pref(config):
    with open(PREF_FILE, "w") as f:
        json.dump(config, f, indent=2)