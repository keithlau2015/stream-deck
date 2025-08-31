import os
import json
import sys

def get_app_data_dir():
    """Get the directory where the application should store its data files"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    return app_dir

PREF_FILE = os.path.join(get_app_data_dir(), "pref.json")

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
    try:
        print(f"[DEBUG] Saving config to: {PREF_FILE}")
        print(f"[DEBUG] App data directory: {get_app_data_dir()}")
        print(f"[DEBUG] Config being saved:", json.dumps(config, indent=2))
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(PREF_FILE), exist_ok=True)
        
        with open(PREF_FILE, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"[DEBUG] Config saved successfully to: {PREF_FILE}")
        
        # Verify the file was created
        if os.path.exists(PREF_FILE):
            file_size = os.path.getsize(PREF_FILE)
            print(f"[DEBUG] File verification: {PREF_FILE} exists, size: {file_size} bytes")
        else:
            print(f"[DEBUG ERROR] File was not created: {PREF_FILE}")
            
    except Exception as e:
        print(f"[DEBUG ERROR] Failed to save config: {e}")
        import traceback
        traceback.print_exc()