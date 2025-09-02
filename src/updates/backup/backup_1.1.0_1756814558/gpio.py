import subprocess
import webbrowser
import serial
import time
import ctypes
import os
import json
import threading
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

# Configuration file path
GPIO_CONFIG_FILE = os.path.join(get_app_data_dir(), "gpio_config.json")

# Default configuration values
DEFAULT_CONFIG = {
    "arduino": {
        "port": "COM7",
        "baudrate": 9600,
        "timeout": 1
    },
    "volume": {
        "enabled": True,
        "default_value": 0
    },
    "media": {
        "enabled": True
    },
    "debug": {
        "enabled": True,
        "log_level": "INFO"
    }
}

def load_gpio_config():
    """Load GPIO configuration from file or create default if not exists"""
    try:
        if os.path.exists(GPIO_CONFIG_FILE):
            with open(GPIO_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                print(f"[GPIO] Configuration loaded from {GPIO_CONFIG_FILE}")
                return config
        else:
            # Create default config file
            with open(GPIO_CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
                print(f"[GPIO] Created default configuration file: {GPIO_CONFIG_FILE}")
                print(f"[GPIO] Please edit {GPIO_CONFIG_FILE} to configure your Arduino settings")
                return DEFAULT_CONFIG
    except Exception as e:
        print(f"[GPIO ERROR] Failed to load configuration: {e}")
        print(f"[GPIO] Using default configuration")
        return DEFAULT_CONFIG

# Load configuration
gpio_config = load_gpio_config()

# Extract Arduino settings from config
ARDUINO_PORT = gpio_config["arduino"]["port"]
BAUDRATE = gpio_config["arduino"]["baudrate"]
SERIAL_TIMEOUT = gpio_config["arduino"]["timeout"]

# Extract other settings
VOLUME_ENABLED = gpio_config["volume"]["enabled"]
VOLUME_DEFAULT = gpio_config["volume"]["default_value"]
MEDIA_ENABLED = gpio_config["media"]["enabled"]
DEBUG_ENABLED = gpio_config["debug"]["enabled"]

# Selected button state
selected_button = None

# Internal state for VOLUME
last_volume_value = VOLUME_DEFAULT
is_muted = False

# Config reload mechanism
config_reload_event = threading.Event()
gpio_reload_event = threading.Event()
current_config = None

def reload_gpio_config():
    """Reload GPIO configuration from file"""
    global gpio_config, ARDUINO_PORT, BAUDRATE, SERIAL_TIMEOUT, VOLUME_ENABLED, VOLUME_DEFAULT, MEDIA_ENABLED, DEBUG_ENABLED, gpio_reload_event
    
    try:
        if os.path.exists(GPIO_CONFIG_FILE):
            with open(GPIO_CONFIG_FILE, 'r') as f:
                new_config = json.load(f)
                
                # Check if Arduino connection settings changed
                old_port = ARDUINO_PORT
                old_baudrate = BAUDRATE
                old_timeout = SERIAL_TIMEOUT
                
                gpio_config = new_config
                
                # Update all configuration variables
                ARDUINO_PORT = gpio_config["arduino"]["port"]
                BAUDRATE = gpio_config["arduino"]["baudrate"]
                SERIAL_TIMEOUT = gpio_config["arduino"]["timeout"]
                VOLUME_ENABLED = gpio_config["volume"]["enabled"]
                VOLUME_DEFAULT = gpio_config["volume"]["default_value"]
                MEDIA_ENABLED = gpio_config["media"]["enabled"]
                DEBUG_ENABLED = gpio_config["debug"]["enabled"]
                
                print(f"[GPIO] Configuration reloaded from {GPIO_CONFIG_FILE}")
                print(f"[GPIO] Arduino: {ARDUINO_PORT} @ {BAUDRATE} baud")
                
                # Signal GPIO reload if connection settings changed
                if old_port != ARDUINO_PORT or old_baudrate != BAUDRATE or old_timeout != SERIAL_TIMEOUT:
                    gpio_reload_event.set()
                    print(f"[GPIO] Arduino connection settings changed - forcing reconnection")
                
                return True
        else:
            print(f"[GPIO ERROR] Configuration file {GPIO_CONFIG_FILE} not found")
            return False
    except Exception as e:
        print(f"[GPIO ERROR] Failed to reload configuration: {e}")
        return False

def execute_action(action):
    if action["type"] == "link" and action["value"]:
        webbrowser.open(action["value"])
    elif action["type"] == "exe" and action["value"]:
        try:
            subprocess.Popen(action["value"])
        except Exception as e:
            print("Error opening executable:", e)
    else:
        print("No action defined")

def listen_serial(config):
    try:
        with serial.Serial(ARDUINO_PORT, BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
            print(f"Connected to {ARDUINO_PORT}")
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print("Received:", line)
                    if line.startswith("VOLUME_") and VOLUME_ENABLED:
                        value = line.replace("VOLUME_", "")
                        handle_volume(value)
                    elif line == "MUTE" and VOLUME_ENABLED:
                        handle_mute()
                    elif line == "MEDIA" and MEDIA_ENABLED:
                        handle_media()
                    elif line in config:
                        execute_action(config[line])
    except Exception as e:
        print(f"[ERROR] Serial port: {e}")
        time.sleep(5)
        listen_serial(config)

def simulate_keypress(vk_code):
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)

def handle_volume(value):
    global last_volume_value
    if not VOLUME_ENABLED:
        print("[GPIO] Volume control is disabled in configuration")
        return
        
    try:
        volume_value = int(value)
        delta = volume_value - last_volume_value
        if delta != 0:
            vk = 0xAF if delta > 0 else 0xAE  # VK_VOLUME_UP / VK_VOLUME_DOWN
            for _ in range(abs(delta)):
                simulate_keypress(vk)
            if DEBUG_ENABLED:
                print(f"[DEBUG] Volume adjusted by {delta}")
        last_volume_value = volume_value
    except ValueError:
        print("[ERROR] Invalid volume value:", value)

def handle_mute():
    global is_muted
    if not VOLUME_ENABLED:
        print("[GPIO] Volume control is disabled in configuration")
        return
        
    simulate_keypress(0xAD)  # VK_VOLUME_MUTE
    is_muted = not is_muted
    if DEBUG_ENABLED:
        print(f"[DEBUG] Mute toggled -> {'ON' if is_muted else 'OFF'}")

def handle_media():
    if not MEDIA_ENABLED:
        print("[GPIO] Media control is disabled in configuration")
        return
        
    simulate_keypress(0xB3)  # VK_MEDIA_PLAY_PAUSE
    if DEBUG_ENABLED:
        print("[DEBUG] Media play/pause triggered")

def select_button(btn):
    global selected_button
    selected_button = btn
    print(f"[DEBUG] Button selected: BUTTON_{btn}")

def deselect_button():
    global selected_button
    selected_button = None    

def get_selected_button():
    return selected_button

def signal_config_reload():
    """Signal the serial thread to reload configuration"""
    global config_reload_event
    config_reload_event.set()
    print("[GPIO] Config reload signal sent")

def signal_gpio_reload():
    """Signal the serial thread to reload GPIO configuration immediately"""
    global gpio_reload_event
    print("[GPIO] signal_gpio_reload() called")
    
    # Print current settings before reload
    print(f"[GPIO] Before reload - Debug: {DEBUG_ENABLED}, Volume: {VOLUME_ENABLED}, Media: {MEDIA_ENABLED}")
    
    # First reload the GPIO config in this thread to update global variables
    if reload_gpio_config():
        print("[GPIO] GPIO configuration reloaded immediately")
        # Print current settings after reload
        print(f"[GPIO] After reload - Debug: {DEBUG_ENABLED}, Volume: {VOLUME_ENABLED}, Media: {MEDIA_ENABLED}")
        # Only signal reconnection if Arduino settings actually changed
        # (gpio_reload_event will be set by reload_gpio_config if needed)
    else:
        # If reload failed, still try to signal
        print("[GPIO] GPIO config reload failed, signaling anyway")
        gpio_reload_event.set()
    print("[GPIO] GPIO reload signal sent")

def get_current_gpio_settings():
    """Get current GPIO settings (for debugging/status)"""
    return {
        "arduino_port": ARDUINO_PORT,
        "arduino_baudrate": BAUDRATE,
        "volume_enabled": VOLUME_ENABLED,
        "media_enabled": MEDIA_ENABLED,
        "debug_enabled": DEBUG_ENABLED
    }

def listen_serial_with_reload():
    """Enhanced serial listener that can reload config when signaled"""
    global current_config, config_reload_event, gpio_reload_event
    from prefController import load_pref
    
    # Load initial config
    current_config = load_pref()
    print(f"[GPIO] Initial config loaded with {len(current_config)} buttons")
    print(f"[GPIO] Arduino: {ARDUINO_PORT} @ {BAUDRATE} baud")
    
    while True:
        try:
            with serial.Serial(ARDUINO_PORT, BAUDRATE, timeout=SERIAL_TIMEOUT) as ser:
                print(f"[GPIO] Connected to {ARDUINO_PORT}")
                
                while True:
                    # Check if GPIO reload was requested (Arduino connection settings changed)
                    if gpio_reload_event.is_set():
                        gpio_reload_event.clear()
                        print(f"[GPIO] GPIO settings changed - reconnecting...")
                        break  # Break out of serial loop to reconnect with new settings
                    
                    # Check if button config reload was requested (from GUI)
                    if config_reload_event.is_set():
                        current_config = load_pref()
                        config_reload_event.clear()
                        print(f"[GPIO] Button config reloaded! {len(current_config)} buttons configured")
                        
                        # Note: GPIO config should already be reloaded by signal_gpio_reload()
                        # when GPIO settings are saved, so we don't need to reload it here
                    
                    # Read serial data with timeout
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        # Cache current GPIO settings to avoid repeated dict lookups
                        current_debug = DEBUG_ENABLED
                        current_volume = VOLUME_ENABLED
                        current_media = MEDIA_ENABLED
                        
                        if current_debug:
                            print("[GPIO] Received:", line)
                        if line.startswith("VOLUME_") and current_volume:
                            value = line.replace("VOLUME_", "")
                            handle_volume(value)
                        elif line == "MUTE" and current_volume:
                            handle_mute()
                        elif line == "MEDIA" and current_media:
                            handle_media()
                        elif line in current_config:
                            if current_debug:
                                print(f"[GPIO] Executing action for {line}")
                            execute_action(current_config[line])
                        else:
                            if current_debug:
                                print(f"[GPIO] No action configured for: {line}")
                            
        except Exception as e:
            print(f"[GPIO ERROR] Serial port: {e}")
            time.sleep(5)
            # Continue the loop to reconnect