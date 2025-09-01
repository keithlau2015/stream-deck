import os
import json
import sys
from functools import lru_cache

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

# Cache for configuration with file modification time
_config_cache = {}
_config_mtime = 0

def load_pref():
    global _config_cache, _config_mtime
    
    print(f"[DEBUG] Loading config from: {PREF_FILE}")
    
    # Check if file exists and get modification time
    if os.path.exists(PREF_FILE):
        current_mtime = os.path.getmtime(PREF_FILE)
        
        # Return cached config if file hasn't changed
        if current_mtime == _config_mtime and _config_cache:
            print("[DEBUG] Using cached config (no file changes)")
            return _config_cache
        
        # Load and cache new config
        try:
            with open(PREF_FILE, "r") as f:
                config = json.load(f)
                _config_cache = config
                _config_mtime = current_mtime
                print("[DEBUG] Config loaded and cached:", json.dumps(config, indent=2))
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"[DEBUG ERROR] Failed to load config: {e}")
            # Fall through to default config
    
    # Create default config
    print("[DEBUG] Config file not found, creating default config.")
    config = {}
    for i in range(1, 10):
        config[f"BUTTON_{i}"] = {"type": "none", "value": ""}
    config["BUTTON_1"] = {"type": "link", "value": "https://www.youtube.com"}
    
    # Cache the default config
    _config_cache = config
    _config_mtime = 0
    return config

def save_pref(config):
    global _config_cache, _config_mtime
    
    try:
        print(f"[DEBUG] Saving config to: {PREF_FILE}")
        print(f"[DEBUG] App data directory: {get_app_data_dir()}")
        print(f"[DEBUG] Config being saved:", json.dumps(config, indent=2))
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(PREF_FILE), exist_ok=True)
        
        with open(PREF_FILE, "w") as f:
            json.dump(config, f, indent=2)
        
        # Update cache with new config and modification time
        _config_cache = config.copy()
        _config_mtime = os.path.getmtime(PREF_FILE) if os.path.exists(PREF_FILE) else 0
        
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