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
    print("[TRAY] Shutting down ConsoleDeck...")
    icon.stop()
    sys.exit(0)

def create_tray_icon(config_callback):
    """Create and run the system tray icon"""
    def run_config():
        """Run the config GUI in a separate thread"""
        config_thread = threading.Thread(target=config_callback, daemon=True)
        config_thread.start()
    
    def reload_pref():
        """Manually reload configuration"""
        try:
            from gpio import signal_config_reload
            signal_config_reload()
            print("[TRAY] Manual config reload requested")
        except Exception as e:
            print(f"[TRAY ERROR] Failed to reload config: {e}")
    
    # Create the icon image
    image = create_icon_image()
    
    # Create the menu
    menu = pystray.Menu(
        pystray.MenuItem("Open Configuration", run_config),
        pystray.MenuItem("Reload Config", reload_pref),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_application)
    )
    
    # Create and run the tray icon
    icon = pystray.Icon("ConsoleDeck", image, "ConsoleDeck V2", menu)
    
    print("[TRAY] ConsoleDeck V2 started in system tray")
    try:
        icon.notify("ConsoleDeck V2 is running", "Right-click the tray icon for options")
    except:
        pass  # Notifications might not be supported on all systems
    
    # This will block until the icon is stopped
    icon.run()
