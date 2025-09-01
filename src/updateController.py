"""
StreamDeck V2 - Update Settings Controller
更新设置控制器
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from version import get_update_manager, get_current_version

class UpdateSettingsGUI:
    def __init__(self):
        self.update_manager = get_update_manager()
        self.root = tk.Tk()
        self.root.title("StreamDeck V2 - Update Settings")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Variables for settings
        self.auto_check_var = tk.BooleanVar(value=self.update_manager.config.get("auto_check", True))
        self.auto_download_var = tk.BooleanVar(value=self.update_manager.config.get("auto_download", True))
        self.auto_install_var = tk.BooleanVar(value=self.update_manager.config.get("auto_install", False))
        
        # Interval options (in seconds)
        self.interval_options = {
            "Every 30 minutes": 1800,
            "Every hour": 3600,
            "Every 2 hours": 7200,
            "Every 6 hours": 21600,
            "Every 12 hours": 43200,
            "Daily": 86400
        }
        
        current_interval = self.update_manager.config.get("check_interval", 3600)
        self.interval_var = tk.StringVar()
        
        # Find the closest match for current interval
        for name, value in self.interval_options.items():
            if value == current_interval:
                self.interval_var.set(name)
                break
        else:
            self.interval_var.set("Every hour")  # Default
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the update settings UI"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Update Settings", font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Current version info
        info_frame = ttk.LabelFrame(main_frame, text="Current Version", padding="10")
        info_frame.pack(fill='x', pady=(0, 15))
        
        current_version = get_current_version()
        version_label = ttk.Label(info_frame, text=f"Version: {current_version}")
        version_label.pack(anchor='w')
        
        # Check for updates button
        check_frame = ttk.Frame(info_frame)
        check_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(check_frame, text="Check for Updates Now", 
                  command=self.check_updates_now).pack(side='left')
        
        self.status_label = ttk.Label(check_frame, text="")
        self.status_label.pack(side='left', padx=(10, 0))
        
        # Auto-update settings
        settings_frame = ttk.LabelFrame(main_frame, text="Automatic Update Settings", padding="10")
        settings_frame.pack(fill='x', pady=(0, 15))
        
        # Auto-check setting
        ttk.Checkbutton(settings_frame, text="Automatically check for updates", 
                       variable=self.auto_check_var,
                       command=self.on_auto_check_changed).pack(anchor='w', pady=2)
        
        # Check interval
        interval_frame = ttk.Frame(settings_frame)
        interval_frame.pack(fill='x', pady=(5, 10))
        
        ttk.Label(interval_frame, text="Check interval:").pack(side='left')
        
        self.interval_combo = ttk.Combobox(interval_frame, textvariable=self.interval_var,
                                          values=list(self.interval_options.keys()),
                                          state='readonly', width=15)
        self.interval_combo.pack(side='left', padx=(10, 0))
        
        # Auto-download setting
        ttk.Checkbutton(settings_frame, text="Automatically download updates", 
                       variable=self.auto_download_var).pack(anchor='w', pady=2)
        
        # Auto-install setting
        ttk.Checkbutton(settings_frame, text="Automatically install updates (Not recommended)", 
                       variable=self.auto_install_var).pack(anchor='w', pady=2)
        
        # Warning note
        warning_label = ttk.Label(settings_frame, 
                                 text="Note: Automatic installation will restart the application without warning.",
                                 font=('Segoe UI', 8), foreground='red')
        warning_label.pack(anchor='w', pady=(0, 5))
        
        # Download location
        location_frame = ttk.LabelFrame(main_frame, text="Download Location", padding="10")
        location_frame.pack(fill='x', pady=(0, 15))
        
        download_path = self.update_manager.config.get("download_path", "")
        ttk.Label(location_frame, text=f"Updates downloaded to:").pack(anchor='w')
        ttk.Label(location_frame, text=download_path, font=('Segoe UI', 8), foreground='blue').pack(anchor='w')
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side='right')
        
        # Update the state of interval combo based on auto_check
        self.on_auto_check_changed()
        
    def on_auto_check_changed(self):
        """Handle auto-check checkbox state change"""
        if self.auto_check_var.get():
            self.interval_combo.configure(state='readonly')
        else:
            self.interval_combo.configure(state='disabled')
    
    def check_updates_now(self):
        """Check for updates manually"""
        def check_thread():
            try:
                self.status_label.configure(text="Checking...")
                self.root.update()
                
                has_update = self.update_manager.check_for_updates(manual=True)
                
                if has_update:
                    latest_version = self.update_manager.latest_version
                    self.status_label.configure(text=f"Update available: v{latest_version}")
                    
                    # Ask if user wants to see details
                    if messagebox.askyesno("Update Available", 
                                         f"Version {latest_version} is available!\n\nWould you like to see the release notes?"):
                        self.show_release_notes()
                else:
                    self.status_label.configure(text="You're up to date!")
                    
            except Exception as e:
                self.status_label.configure(text="Check failed")
                messagebox.showerror("Error", f"Failed to check for updates:\n{e}")
        
        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()
    
    def show_release_notes(self):
        """Show release notes in a new window"""
        if not self.update_manager.latest_release_info:
            messagebox.showinfo("No Information", "No release information available.")
            return
        
        # Create new window for release notes
        notes_window = tk.Toplevel(self.root)
        notes_window.title(f"Release Notes - v{self.update_manager.latest_version}")
        notes_window.geometry("600x400")
        
        # Text widget with scrollbar
        frame = ttk.Frame(notes_window)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, wrap='word', font=('Segoe UI', 10))
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Release information
        release_info = self.update_manager.latest_release_info
        content = f"Version: {release_info.get('tag_name', 'Unknown')}\n"
        content += f"Published: {release_info.get('published_at', 'Unknown')}\n"
        content += f"Author: {release_info.get('author', {}).get('login', 'Unknown')}\n\n"
        content += "Release Notes:\n"
        content += "=" * 50 + "\n"
        content += release_info.get('body', 'No release notes available.')
        
        text_widget.insert('1.0', content)
        text_widget.configure(state='disabled')
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Download button
        button_frame = ttk.Frame(notes_window)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Download Update", 
                  command=lambda: self.download_update(notes_window)).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Close", 
                  command=notes_window.destroy).pack(side='right')
    
    def download_update(self, parent_window=None):
        """Download the available update"""
        if not self.update_manager.update_available:
            messagebox.showinfo("No Update", "No update available to download.")
            return
        
        def download_thread():
            try:
                if parent_window:
                    parent_window.destroy()
                
                # Show progress dialog
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Downloading Update")
                progress_window.geometry("400x150")
                progress_window.resizable(False, False)
                
                ttk.Label(progress_window, text="Downloading update...", 
                         font=('Segoe UI', 12)).pack(pady=20)
                
                progress_var = tk.DoubleVar()
                progress_bar = ttk.Progressbar(progress_window, variable=progress_var, 
                                             maximum=100, length=300)
                progress_bar.pack(pady=10)
                
                status_label = ttk.Label(progress_window, text="Preparing...")
                status_label.pack()
                
                # Download update
                file_path = self.update_manager.download_update()
                
                progress_window.destroy()
                
                if file_path:
                    messagebox.showinfo("Download Complete", 
                                      f"Update downloaded successfully!\n\nLocation: {file_path}")
                else:
                    messagebox.showerror("Download Failed", "Failed to download update.")
                    
            except Exception as e:
                if 'progress_window' in locals():
                    progress_window.destroy()
                messagebox.showerror("Error", f"Download failed:\n{e}")
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def save_settings(self):
        """Save the update settings"""
        try:
            # Update configuration
            self.update_manager.config["auto_check"] = self.auto_check_var.get()
            self.update_manager.config["auto_download"] = self.auto_download_var.get()
            self.update_manager.config["auto_install"] = self.auto_install_var.get()
            
            # Update check interval
            interval_name = self.interval_var.get()
            self.update_manager.config["check_interval"] = self.interval_options.get(interval_name, 3600)
            
            # Save configuration
            self.update_manager.save_config()
            
            messagebox.showinfo("Settings Saved", "Update settings have been saved successfully!")
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")
    
    def cancel(self):
        """Cancel and close the settings window"""
        self.root.destroy()
    
    def run(self):
        """Run the settings GUI"""
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Start the tkinter main loop
        self.root.mainloop()

def open_update_settings_gui():
    """Open the update settings GUI"""
    try:
        gui = UpdateSettingsGUI()
        gui.run()
    except Exception as e:
        print(f"[UPDATE SETTINGS ERROR] Failed to open GUI: {e}")
        import traceback
        traceback.print_exc()
