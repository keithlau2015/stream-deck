import pystray
from PIL import Image, ImageDraw
import threading
import sys
import os
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
                    # Update menu to show install option
                    try:
                        new_menu = create_menu()
                        icon.menu = new_menu
                    except:
                        pass
                else:
                    icon.notify("Download Failed", "Failed to download update. Please try again.")
            except Exception as e:
                print(f"[TRAY ERROR] Failed to download update: {e}")
                icon.notify("Download Error", "Failed to download update.")
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def install_update():
        """Install downloaded update"""
        if not update_manager or not update_manager.update_available:
            print("[TRAY] No update available to install")
            return
        
        # Check if update has been downloaded
        if not hasattr(update_manager, 'downloaded_file_path'):
            # Try to find downloaded file
            download_path = update_manager.config.get("download_path", "")
            if update_manager.latest_release_info:
                assets = update_manager.latest_release_info.get('assets', [])
                for asset in assets:
                    filename = asset['name']
                    file_path = os.path.join(download_path, filename)
                    if os.path.exists(file_path):
                        update_manager.downloaded_file_path = file_path
                        break
        
        if not hasattr(update_manager, 'downloaded_file_path') or not os.path.exists(update_manager.downloaded_file_path):
            icon.notify("Download Required", "Please download the update first.")
            return
        
        def install_thread():
            try:
                print("[TRAY] Installing update...")
                icon.notify("Installing Update", "Installing update. Please wait...")
                
                result = update_manager.install_update(update_manager.downloaded_file_path)
                
                if result == "restart_required":
                    icon.notify("Restart Required", "Update installer will run after the application closes.")
                    # Give user a moment to see the notification, then exit
                    time.sleep(2)
                    quit_application(icon)
                elif result:
                    icon.notify("Update Complete", "Update installed successfully!")
                else:
                    icon.notify("Install Failed", "Failed to install update.")
                    
            except Exception as e:
                print(f"[TRAY ERROR] Failed to install update: {e}")
                icon.notify("Install Error", "Failed to install update.")
        
        thread = threading.Thread(target=install_thread, daemon=True)
        thread.start()
    
    def show_update_info():
        """Show information about available update"""
        if not update_manager or not update_manager.update_available:
            print("[TRAY] No update information available")
            return
        
        try:
            import tkinter as tk
            from tkinter import ttk, scrolledtext
            
            # Dark theme colors
            bg_color = "#282828"
            panel_color = "#3c3c3c"
            button_color = "#505050"
            text_color = "#ffffff"
            accent_color = "#ff7700"
            info_color = "#2196F3"
            
            # Create info window with dark theme
            info_window = tk.Tk()
            info_window.title("Update Information")
            info_window.geometry("600x450")
            info_window.resizable(True, True)
            info_window.configure(bg=bg_color)
            
            # Configure dark theme styles
            style = ttk.Style()
            style.theme_use('clam')
            
            style.configure('Dark.TFrame', background=bg_color)
            style.configure('Panel.TFrame', background=panel_color, borderwidth=0, relief='flat')
            style.configure('Title.TLabel', background=bg_color, foreground=text_color, font=('Segoe UI', 14, 'bold'))
            style.configure('Dark.TLabel', background=bg_color, foreground=text_color, font=('Segoe UI', 10))
            style.configure('Info.TLabel', background=bg_color, foreground=info_color, font=('Segoe UI', 10, 'bold'))
            style.configure('Accent.TButton', background=accent_color, foreground='white', font=('Segoe UI', 10))
            style.configure('Dark.TButton', background=button_color, foreground=text_color, font=('Segoe UI', 10))
            
            style.map('Accent.TButton', background=[('active', '#ff8800')])
            style.map('Dark.TButton', background=[('active', '#606060')])
            
            # Main frame
            main_frame = ttk.Frame(info_window, style='Dark.TFrame', padding="15")
            main_frame.pack(fill='both', expand=True)
            
            release_info = update_manager.latest_release_info
            current_ver = update_manager.current_version
            latest_ver = update_manager.latest_version
            
            # Version info with dark theme
            ttk.Label(main_frame, text="Update Available", style='Title.TLabel').pack(pady=(0, 10))
            
            info_text = f"Current Version: {current_ver}\nLatest Version: {latest_ver}\n"
            if release_info.get('published_at'):
                info_text += f"Published: {release_info['published_at']}\n"
            
            ttk.Label(main_frame, text=info_text, style='Dark.TLabel').pack(anchor='w', pady=(0, 10))
            
            # Release notes
            ttk.Label(main_frame, text="Release Notes:", style='Info.TLabel').pack(anchor='w')
            
            # Scrollable text area for release notes with dark theme
            notes_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                                  width=70, height=15, 
                                                  font=('Segoe UI', 9),
                                                  bg=panel_color, fg=text_color,
                                                  insertbackground=text_color,
                                                  selectbackground=accent_color,
                                                  selectforeground='white',
                                                  borderwidth=1, relief='solid')
            notes_text.pack(fill='both', expand=True, pady=(5, 10))
            
            # Insert release notes
            body = release_info.get('body', 'No release notes available.')
            notes_text.insert('1.0', body)
            notes_text.configure(state='disabled')  # Make read-only
            
            # Buttons with dark theme
            button_frame = ttk.Frame(main_frame, style='Dark.TFrame')
            button_frame.pack(fill='x', pady=(10, 0))
            
            ttk.Button(button_frame, text="Download Update", 
                      command=lambda: [download_update(), info_window.destroy()], style='Accent.TButton').pack(side='right', padx=(5, 0))
            ttk.Button(button_frame, text="Close", 
                      command=info_window.destroy, style='Dark.TButton').pack(side='right')
            
            # Center the window
            info_window.update_idletasks()
            x = (info_window.winfo_screenwidth() // 2) - (info_window.winfo_width() // 2)
            y = (info_window.winfo_screenheight() // 2) - (info_window.winfo_height() // 2)
            info_window.geometry(f"+{x}+{y}")
            
            info_window.mainloop()
            
        except Exception as e:
            print(f"[TRAY ERROR] Failed to show update info: {e}")
            # Fallback to simple message
            try:
                from tkinter import messagebox
                messagebox.showinfo("Update Available", 
                                  f"Version {update_manager.latest_version} is available!")
            except:
                pass
    
    def update_callback(event_type, data):
        """Handle update manager callbacks"""
        try:
            if event_type == "update_available":
                update_available["value"] = True
                version = data.get("latest_version", "unknown")
                print(f"[TRAY] Update available: {version}")
                
                # Show notification
                try:
                    icon.notify("Update Available", f"StreamDeck V2 version {version} is available!")
                except Exception as notify_error:
                    print(f"[TRAY WARNING] Notification failed: {notify_error}")
                
                # Update menu to reflect new status
                try:
                    new_menu = create_menu()
                    icon.menu = new_menu
                    print("[TRAY] Menu updated to show available update")
                except Exception as menu_error:
                    print(f"[TRAY WARNING] Menu update failed: {menu_error}")
                    
            elif event_type == "download_completed":
                version = data.get("version", "unknown")
                try:
                    icon.notify("Download Complete", f"Version {version} downloaded successfully!")
                except:
                    pass
            elif event_type == "install_completed":
                version = data.get("version", "unknown")
                try:
                    icon.notify("Update Installed", f"Version {version} installed! Please restart the application.")
                except:
                    pass
            elif event_type == "no_update":
                print("[TRAY] No update available")
                # Update menu to show up-to-date status
                try:
                    new_menu = create_menu()
                    icon.menu = new_menu
                except:
                    pass
            
            # 新的自动更新事件处理
            elif event_type == "auto_update_started":
                version = data.get("version", "unknown")
                try:
                    icon.notify("🔄 Auto-Update Started", f"自动下载版本 {version}...")
                    print(f"[TRAY] Auto-update started for version {version}")
                except:
                    pass
            
            elif event_type == "auto_download_completed":
                version = data.get("version", "unknown")
                try:
                    icon.notify("📥 Auto-Download Complete", f"版本 {version} 下载完成")
                    print(f"[TRAY] Auto-download completed for version {version}")
                except:
                    pass
            
            elif event_type == "auto_install_countdown":
                version = data.get("version", "unknown")
                delay = data.get("delay", 5)
                try:
                    icon.notify("⏰ Auto-Install Starting", f"版本 {version} 将在 {delay} 秒后自动安装...")
                    print(f"[TRAY] Auto-install countdown: {delay} seconds for version {version}")
                except:
                    pass
            
            elif event_type == "auto_install_started":
                version = data.get("version", "unknown")
                try:
                    icon.notify("🚀 Auto-Installing", f"正在自动安装版本 {version}...")
                    print(f"[TRAY] Auto-install started for version {version}")
                except:
                    pass
            
            elif event_type == "auto_install_restart":
                version = data.get("version", "unknown")
                try:
                    icon.notify("✅ Update Complete", f"版本 {version} 安装完成，应用将重启")
                    print(f"[TRAY] Auto-install completed, restart required for version {version}")
                except:
                    pass
            
            elif event_type == "auto_install_completed":
                version = data.get("version", "unknown")
                try:
                    icon.notify("🎉 Update Complete", f"版本 {version} 安装成功！")
                    print(f"[TRAY] Auto-install completed successfully for version {version}")
                except:
                    pass
            
            elif event_type == "auto_install_failed":
                version = data.get("version", "unknown")
                try:
                    icon.notify("❌ Update Failed", f"版本 {version} 安装失败")
                    print(f"[TRAY] Auto-install failed for version {version}")
                except:
                    pass
            
            elif event_type == "auto_download_failed":
                version = data.get("version", "unknown")
                try:
                    icon.notify("❌ Download Failed", f"版本 {version} 下载失败")
                    print(f"[TRAY] Auto-download failed for version {version}")
                except:
                    pass
            
            elif event_type == "auto_update_error":
                error = data.get("error", "Unknown error")
                try:
                    icon.notify("❌ Update Error", f"自动更新失败: {error}")
                    print(f"[TRAY] Auto-update error: {error}")
                except:
                    pass
                    
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
        
        # Check current update status
        has_update = update_manager.update_available
        latest_ver = getattr(update_manager, 'latest_version', None)
        
        items = []
        
        # Always show check for updates
        items.append(pystray.MenuItem("Check for Updates", check_for_updates_manual))
        
        # Show update available status
        if has_update and latest_ver:
            items.extend([
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(f"⚠️ Update Available: v{latest_ver}", show_update_info),
                pystray.MenuItem("📥 Download Update", download_update),
                pystray.MenuItem("🚀 Install Update", install_update),
                pystray.MenuItem("ℹ️ Release Notes", show_update_info),
            ])
        else:
            items.extend([
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("✅ Up to Date", lambda: None),  # Disabled item
            ])
        
        items.extend([
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙️ Update Settings", open_update_settings),
        ])
        
        return pystray.MenuItem("🔄 Updates", pystray.Menu(*items))
    
    # Create the menu with dynamic update submenu
    def create_menu():
        return pystray.Menu(
        pystray.MenuItem("Button Preferences", run_preferences),
        pystray.MenuItem("GPIO Settings", open_gpio_settings),
            pystray.Menu.SEPARATOR,
            create_update_menu(),
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
