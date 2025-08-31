import pystray
from PIL import Image, ImageDraw
import threading
import sys

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
    
    # Create the icon image
    image = create_icon_image()
    
    # Create the menu
    menu = pystray.Menu(
        pystray.MenuItem("Button Preferences", run_preferences),
        pystray.MenuItem("GPIO Settings", open_gpio_settings),
        #pystray.Menu.SEPARATOR,
        #pystray.MenuItem("Reload Configuration", reload_configurations),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_application)
    )
    
    # Create and run the tray icon
    icon = pystray.Icon("StreamDeck", image, "StreamDeck V2", menu)
    
    print("[TRAY] StreamDeck V2 started in system tray")
    try:
        icon.notify("StreamDeck V2 is running", "Right-click the tray icon for options")
    except:
        pass  # Notifications might not be supported on all systems
    
    # This will block until the icon is stopped
    icon.run()
