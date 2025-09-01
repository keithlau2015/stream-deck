"""
StreamDeck V2 - Version Management and Auto-Update System
版本管理和自动更新系统
"""

import os
import sys
import json
import requests
import threading
import time
from packaging import version
import zipfile
import shutil
import subprocess
from datetime import datetime, timedelta

# Current version of the application
CURRENT_VERSION = "1.2.0"  # This should match the latest release
GITHUB_REPO = "keithlau2015/stream-deck"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
UPDATE_CHECK_INTERVAL = 3600  # Check for updates every hour (in seconds)

def get_app_data_dir():
    """Get the directory where the application should store its data files"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    return app_dir

# Update configuration file
UPDATE_CONFIG_FILE = os.path.join(get_app_data_dir(), "update_config.json")

# Default update configuration
DEFAULT_UPDATE_CONFIG = {
    "auto_check": True,
    "auto_download": True,
    "auto_install": False,  # Require user confirmation
    "last_check": None,
    "ignored_version": None,
    "check_interval": UPDATE_CHECK_INTERVAL,
    "download_path": os.path.join(get_app_data_dir(), "updates")
}

class UpdateManager:
    def __init__(self):
        self.config = self.load_config()
        self.current_version = CURRENT_VERSION
        self.latest_version = None
        self.latest_release_info = None
        self.update_available = False
        self.downloading = False
        self.download_progress = 0
        self.update_callbacks = []
        
        # Ensure download directory exists
        os.makedirs(self.config["download_path"], exist_ok=True)
        
        print(f"[UPDATE] UpdateManager initialized - Current version: {self.current_version}")
    
    def load_config(self):
        """Load update configuration from file"""
        try:
            if os.path.exists(UPDATE_CONFIG_FILE):
                with open(UPDATE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged_config = DEFAULT_UPDATE_CONFIG.copy()
                    merged_config.update(config)
                    return merged_config
            else:
                self.save_config(DEFAULT_UPDATE_CONFIG)
                return DEFAULT_UPDATE_CONFIG.copy()
        except Exception as e:
            print(f"[UPDATE ERROR] Failed to load update config: {e}")
            return DEFAULT_UPDATE_CONFIG.copy()
    
    def save_config(self, config=None):
        """Save update configuration to file"""
        try:
            if config is None:
                config = self.config
            
            with open(UPDATE_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"[UPDATE] Configuration saved to: {UPDATE_CONFIG_FILE}")
        except Exception as e:
            print(f"[UPDATE ERROR] Failed to save update config: {e}")
    
    def add_update_callback(self, callback):
        """Add callback function to be called when update status changes"""
        self.update_callbacks.append(callback)
    
    def notify_callbacks(self, event_type, data=None):
        """Notify all registered callbacks about update events"""
        for callback in self.update_callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"[UPDATE ERROR] Callback error: {e}")
    
    def check_for_updates(self, manual=False):
        """Check for available updates from GitHub releases"""
        try:
            print(f"[UPDATE] Checking for updates... (manual: {manual})")
            
            # Make API request to GitHub
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': f'StreamDeck-V2/{self.current_version}'
            }
            
            response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            self.latest_release_info = release_data
            self.latest_version = release_data['tag_name'].lstrip('v')
            
            # Update last check time
            self.config["last_check"] = datetime.now().isoformat()
            self.save_config()
            
            # Compare versions
            if version.parse(self.latest_version) > version.parse(self.current_version):
                # Check if this version was ignored
                if self.config["ignored_version"] != self.latest_version:
                    self.update_available = True
                    print(f"[UPDATE] New version available: {self.latest_version} (current: {self.current_version})")
                    self.notify_callbacks("update_available", {
                        "current_version": self.current_version,
                        "latest_version": self.latest_version,
                        "release_info": self.latest_release_info
                    })
                    return True
                else:
                    print(f"[UPDATE] Version {self.latest_version} is ignored by user")
            else:
                print(f"[UPDATE] No updates available (latest: {self.latest_version}, current: {self.current_version})")
                if manual:
                    self.notify_callbacks("no_update", {
                        "current_version": self.current_version,
                        "latest_version": self.latest_version
                    })
            
            return False
            
        except requests.RequestException as e:
            error_msg = f"Network error while checking for updates: {e}"
            print(f"[UPDATE ERROR] {error_msg}")
            if manual:
                self.notify_callbacks("check_error", {"error": error_msg})
            return False
        except Exception as e:
            error_msg = f"Unexpected error while checking for updates: {e}"
            print(f"[UPDATE ERROR] {error_msg}")
            if manual:
                self.notify_callbacks("check_error", {"error": error_msg})
            return False
    
    def download_update(self):
        """Download the latest update"""
        if not self.update_available or not self.latest_release_info:
            print("[UPDATE ERROR] No update available to download")
            return False
        
        if self.downloading:
            print("[UPDATE] Download already in progress")
            return False
        
        try:
            self.downloading = True
            self.download_progress = 0
            self.notify_callbacks("download_started", {
                "version": self.latest_version
            })
            
            # Find the appropriate asset (assuming it's a zip file)
            assets = self.latest_release_info.get('assets', [])
            download_asset = None
            
            for asset in assets:
                if asset['name'].endswith('.zip') or asset['name'].endswith('.exe'):
                    download_asset = asset
                    break
            
            if not download_asset:
                raise Exception("No suitable download asset found")
            
            download_url = download_asset['browser_download_url']
            filename = download_asset['name']
            file_path = os.path.join(self.config["download_path"], filename)
            
            print(f"[UPDATE] Downloading {filename} from {download_url}")
            
            # Download with progress tracking
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Update progress
                        if total_size > 0:
                            self.download_progress = (downloaded_size / total_size) * 100
                            self.notify_callbacks("download_progress", {
                                "progress": self.download_progress,
                                "downloaded": downloaded_size,
                                "total": total_size
                            })
            
            self.downloading = False
            self.download_progress = 100
            
            print(f"[UPDATE] Download completed: {file_path}")
            self.notify_callbacks("download_completed", {
                "file_path": file_path,
                "version": self.latest_version
            })
            
            return file_path
            
        except Exception as e:
            self.downloading = False
            self.download_progress = 0
            error_msg = f"Failed to download update: {e}"
            print(f"[UPDATE ERROR] {error_msg}")
            self.notify_callbacks("download_error", {"error": error_msg})
            return False
    
    def install_update(self, update_file_path):
        """Install the downloaded update"""
        try:
            print(f"[UPDATE] Installing update from: {update_file_path}")
            
            if not os.path.exists(update_file_path):
                raise Exception("Update file not found")
            
            # Create backup of current version
            backup_dir = os.path.join(self.config["download_path"], "backup")
            os.makedirs(backup_dir, exist_ok=True)
            
            current_dir = get_app_data_dir()
            backup_path = os.path.join(backup_dir, f"backup_{self.current_version}_{int(time.time())}")
            
            print(f"[UPDATE] Creating backup at: {backup_path}")
            shutil.copytree(current_dir, backup_path, ignore=shutil.ignore_patterns('*.log', '*.tmp', '__pycache__'))
            
            # If it's a zip file, extract it
            if update_file_path.endswith('.zip'):
                print("[UPDATE] Extracting update archive...")
                with zipfile.ZipFile(update_file_path, 'r') as zip_ref:
                    extract_path = os.path.join(self.config["download_path"], "extracted")
                    os.makedirs(extract_path, exist_ok=True)
                    zip_ref.extractall(extract_path)
                
                # Copy extracted files to current directory
                for root, dirs, files in os.walk(extract_path):
                    for file in files:
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, extract_path)
                        dst_path = os.path.join(current_dir, rel_path)
                        
                        # Ensure destination directory exists
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)
                        print(f"[UPDATE] Updated: {rel_path}")
                
                # Clean up extracted files
                shutil.rmtree(extract_path)
            
            elif update_file_path.endswith('.exe'):
                # If it's an executable installer, run it
                print("[UPDATE] Running installer...")
                subprocess.run([update_file_path], check=True)
            
            print("[UPDATE] Installation completed successfully")
            self.notify_callbacks("install_completed", {
                "version": self.latest_version,
                "backup_path": backup_path
            })
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to install update: {e}"
            print(f"[UPDATE ERROR] {error_msg}")
            self.notify_callbacks("install_error", {"error": error_msg})
            return False
    
    def ignore_version(self, version_to_ignore=None):
        """Mark a version as ignored"""
        if version_to_ignore is None:
            version_to_ignore = self.latest_version
        
        self.config["ignored_version"] = version_to_ignore
        self.save_config()
        self.update_available = False
        print(f"[UPDATE] Version {version_to_ignore} will be ignored")
        self.notify_callbacks("version_ignored", {"version": version_to_ignore})
    
    def should_check_now(self):
        """Check if it's time to check for updates"""
        if not self.config["auto_check"]:
            return False
        
        last_check_str = self.config["last_check"]
        if not last_check_str:
            return True
        
        try:
            last_check = datetime.fromisoformat(last_check_str)
            time_since_check = datetime.now() - last_check
            return time_since_check.total_seconds() >= self.config["check_interval"]
        except:
            return True
    
    def start_background_checker(self):
        """Start background thread to periodically check for updates"""
        def background_check():
            while True:
                try:
                    if self.should_check_now():
                        self.check_for_updates(manual=False)
                    time.sleep(300)  # Check every 5 minutes whether it's time to check
                except Exception as e:
                    print(f"[UPDATE ERROR] Background check error: {e}")
                    time.sleep(600)  # Wait 10 minutes on error
        
        if self.config["auto_check"]:
            thread = threading.Thread(target=background_check, daemon=True)
            thread.start()
            print("[UPDATE] Background update checker started")

# Global update manager instance
update_manager = UpdateManager()

def get_update_manager():
    """Get the global update manager instance"""
    return update_manager

def check_for_updates_manually():
    """Manually check for updates (called from UI)"""
    return update_manager.check_for_updates(manual=True)

def get_current_version():
    """Get the current application version"""
    return CURRENT_VERSION

def is_update_available():
    """Check if an update is available"""
    return update_manager.update_available

def get_latest_version_info():
    """Get information about the latest version"""
    return {
        "current": update_manager.current_version,
        "latest": update_manager.latest_version,
        "available": update_manager.update_available,
        "release_info": update_manager.latest_release_info
    }
