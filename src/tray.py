import pystray
from PIL import Image, ImageDraw
import threading
import sys
import time
from datetime import datetime

def create_icon_image():
    """Create a simple icon for the system tray"""
    # Create a 64x64 image with a simple design
    image = Image.new('RGB', (64, 64), color=(30, 30, 30))
    draw = ImageDraw.Draw(image)
    
    # Draw a simple grid pattern representing buttons
    for i in range(3):
        for j in range(3):
            x1 = 8 + i * 16
            y1 = 8 + j * 16
            x2 = x1 + 12
            y2 = y1 + 12
            draw.rectangle([x1, y1, x2, y2], fill=(200, 120, 40), outline=(255, 255, 255))
            
    return image

def quit_application(icon):
    """Quit the application properly"""
    print("[TRAY] Shutting down StreamDeck...")
    icon.stop()
    sys.exit(0)

def create_tray_icon(config_callback):
    """Create and run the system tray icon"""
    # Track if GUI is currently running to prevent multiple instances
    gui_running = {"value": False}
    
    # Initialize update manager
    update_manager = None
    update_available = {"value": False}
    
    try:
        from version import get_update_manager, get_current_version
        update_manager = get_update_manager()
        print(f"[TRAY] Update manager initialized - Current version: {get_current_version()}")
    except ImportError:
        print("[TRAY WARNING] Update manager not available - auto-update disabled")
    except Exception as e:
        print(f"[TRAY ERROR] Failed to initialize update manager: {e}")
    
    def run_preferences():
        """Run the button preferences GUI in a separate thread"""
        if gui_running["value"]:
            print("[TRAY] Button preferences GUI is already running")
            return
            
        gui_running["value"] = True
        try:
            def run_gui_with_cleanup():
                try:
                    config_callback()
                except Exception as e:
                    print(f"[TRAY ERROR] Failed to run button preferences GUI: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    gui_running["value"] = False
                    print("[TRAY] Button preferences GUI closed")
            
            config_thread = threading.Thread(target=run_gui_with_cleanup, daemon=False)
            config_thread.start()
        except Exception as e:
            gui_running["value"] = False
            print(f"[TRAY ERROR] Failed to start button preferences GUI thread: {e}")
    
    def open_gpio_settings():
        """Open GPIO configuration GUI in a separate thread"""
        def run_gpio_gui():
            try:
                from gpioController import open_gpio_config_gui
                open_gpio_config_gui()
            except Exception as e:
                print(f"[TRAY ERROR] Failed to open GPIO settings GUI: {e}")
        
        gpio_thread = threading.Thread(target=run_gpio_gui, daemon=True)
        gpio_thread.start()
        print("[TRAY] Opening GPIO settings GUI...")
    
    def reload_configurations():
        """Manually reload both button preferences and GPIO configuration"""
        try:
            from gpio import signal_config_reload
            signal_config_reload()
            print("[TRAY] Configuration reload requested")
        except Exception as e:
            print(f"[TRAY ERROR] Failed to reload configuration: {e}")
    
    def check_for_updates_manual():
        """Manually check for updates"""
        if not update_manager:
            print("[TRAY] Update manager not available")
            return
        
        def check_thread():
            try:
                print("[TRAY] Checking for updates...")
                has_update = update_manager.check_for_updates(manual=True)
                if has_update:
                    icon.notify("Update Available", f"Version {update_manager.latest_version} is available!")
                else:
                    icon.notify("No Updates", "You are running the latest version.")
            except Exception as e:
                print(f"[TRAY ERROR] Failed to check for updates: {e}")
                icon.notify("Update Check Failed", "Failed to check for updates. Please try again later.")
        
        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()
    
    def download_update():
        """Download available update"""
        if not update_manager or not update_manager.update_available:
            print("[TRAY] No update available to download")
            return
        
        def download_thread():
            try:
                print("[TRAY] Downloading update...")
                icon.notify("Download Started", f"Downloading version {update_manager.latest_version}...")
                
                file_path = update_manager.download_update()
                if file_path:
                    icon.notify("Download Complete", "Update downloaded successfully. Check the menu to install.")
                else:
                    icon.notify("Download Failed", "Failed to download update. Please try again.")
            except Exception as e:
                print(f"[TRAY ERROR] Failed to download update: {e}")
                icon.notify("Download Error", "Failed to download update.")
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def show_update_info():
        """Show information about available update"""
        if not update_manager or not update_manager.update_available:
            print("[TRAY] No update information available")
            return
        
        try:
            from tkinter import messagebox
            import tkinter as tk
            
            root = tk.Tk()
            root.withdraw()
            
            release_info = update_manager.latest_release_info
            current_ver = update_manager.current_version
            latest_ver = update_manager.latest_version
            
            message = f"""Current Version: {current_ver}
Latest Version: {latest_ver}

Release Notes:
{release_info.get('body', 'No release notes available')}

Published: {release_info.get('published_at', 'Unknown')}"""
            
            messagebox.showinfo("Update Information", message)
            root.destroy()
            
        except Exception as e:
            print(f"[TRAY ERROR] Failed to show update info: {e}")
    
    def update_callback(event_type, data):
        """Handle update manager callbacks"""
        try:
            if event_type == "update_available":
                update_available["value"] = True
                version = data.get("latest_version", "unknown")
                icon.notify("Update Available", f"StreamDeck V2 version {version} is available!")
                print(f"[TRAY] Update available: {version}")
            elif event_type == "download_completed":
                version = data.get("version", "unknown")
                icon.notify("Download Complete", f"Version {version} downloaded successfully!")
            elif event_type == "install_completed":
                version = data.get("version", "unknown")
                icon.notify("Update Installed", f"Version {version} installed! Please restart the application.")
        except Exception as e:
            print(f"[TRAY ERROR] Update callback error: {e}")
    
    # Register update callback
    if update_manager:
        update_manager.add_update_callback(update_callback)
        # Start background checker
        update_manager.start_background_checker()
    
    # Create the icon image
    image = create_icon_image()
    
    def open_update_settings():
        """Open update settings GUI"""
        def run_update_settings():
            try:
                from updateController import open_update_settings_gui
                open_update_settings_gui()
            except Exception as e:
                print(f"[TRAY ERROR] Failed to open update settings GUI: {e}")
        
        settings_thread = threading.Thread(target=run_update_settings, daemon=True)
        settings_thread.start()
        print("[TRAY] Opening update settings GUI...")
    
    def create_update_menu():
        """Create update submenu dynamically"""
        if not update_manager:
            return pystray.MenuItem("Check for Updates", check_for_updates_manual)
        
        items = [
            pystray.MenuItem("Check for Updates", check_for_updates_manual),
            pystray.MenuItem("Update Settings", open_update_settings),
        ]
        
        if update_manager.update_available:
            items.extend([
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Update Information", show_update_info),
                pystray.MenuItem("Download Update", download_update),
            ])
        
        return pystray.MenuItem("Updates", pystray.Menu(*items))
    
    # Create the menu with dynamic update submenu
    def create_menu():
        return pystray.Menu(
            pystray.MenuItem("Button Preferences", run_preferences),
            pystray.MenuItem("GPIO Settings", open_gpio_settings),
            pystray.Menu.SEPARATOR,
            create_update_menu(),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Reload Configuration", reload_configurations),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", quit_application)
        )
    
    menu = create_menu()
    
    # Create and run the tray icon
    icon = pystray.Icon("StreamDeck", image, "StreamDeck V2", menu)
    
    print("[TRAY] StreamDeck V2 started in system tray")
    try:
        icon.notify("StreamDeck V2 is running", "Right-click the tray icon for options")
    except:
        pass  # Notifications might not be supported on all systems
    
    # This will block until the icon is stopped
    icon.run()
