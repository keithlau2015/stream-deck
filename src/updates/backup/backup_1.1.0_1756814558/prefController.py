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
        
        # Validate config structure before saving
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Ensure all button configurations have required fields
        cleaned_config = {}
        for button_key, button_config in config.items():
            if isinstance(button_config, dict):
                cleaned_config[button_key] = {
                    "type": button_config.get("type", "none"),
                    "value": str(button_config.get("value", "")).strip()
                }
            else:
                # Handle malformed button config
                print(f"[DEBUG WARNING] Invalid config for {button_key}, resetting to default")
                cleaned_config[button_key] = {"type": "none", "value": ""}
        
        print(f"[DEBUG] Cleaned config being saved:", json.dumps(cleaned_config, indent=2))
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(PREF_FILE), exist_ok=True)
        
        # Write to temporary file first, then move to ensure atomic write
        temp_file = PREF_FILE + ".tmp"
        with open(temp_file, "w", encoding='utf-8') as f:
            json.dump(cleaned_config, f, indent=2, ensure_ascii=False)
        
        # Move temp file to final location (atomic operation on most systems)
        if os.path.exists(temp_file):
            if os.path.exists(PREF_FILE):
                os.remove(PREF_FILE)
            os.rename(temp_file, PREF_FILE)
        
        # Update cache with new config and modification time
        _config_cache = cleaned_config.copy()
        _config_mtime = os.path.getmtime(PREF_FILE) if os.path.exists(PREF_FILE) else 0
        
        print(f"[DEBUG] Config saved successfully to: {PREF_FILE}")
        
        # Verify the file was created and has content
        if os.path.exists(PREF_FILE):
            file_size = os.path.getsize(PREF_FILE)
            print(f"[DEBUG] File verification: {PREF_FILE} exists, size: {file_size} bytes")
            
            # Verify file can be read back
            with open(PREF_FILE, "r", encoding='utf-8') as f:
                verification_config = json.load(f)
                print(f"[DEBUG] File verification: Successfully read back {len(verification_config)} button configs")
        else:
            print(f"[DEBUG ERROR] File was not created: {PREF_FILE}")
            
    except Exception as e:
        print(f"[DEBUG ERROR] Failed to save config: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up temp file if it exists
        temp_file = PREF_FILE + ".tmp"
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass