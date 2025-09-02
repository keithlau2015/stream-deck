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
        self.root.geometry("520x450")
        self.root.resizable(True, False)  # Allow horizontal resizing
        
        # Dark theme colors (unified with application theme)
        self.bg_color = "#1e1e1e"          # Main background
        self.panel_color = "#2d2d30"        # Panel background  
        self.button_color = "#404040"       # Button background
        self.text_color = "#cccccc"         # Main text
        self.accent_color = "#0078d4"       # Accent blue
        self.success_color = "#28a745"      # Success green
        self.warning_color = "#f48771"      # Warning orange-red
        self.info_color = "#17a2b8"         # Info blue
        self.border_color = "#555555"       # Border color
        
        # Apply dark theme to root window
        self.root.configure(bg=self.bg_color)
        
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
        """Setup the update settings UI with dark theme"""
        # Configure dark theme styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles for dark theme
        style.configure('Dark.TFrame',
                       background=self.bg_color)
        
        style.configure('Panel.TFrame',
                       background=self.panel_color,
                       borderwidth=0,
                       relief='flat')
        
        style.configure('Title.TLabel',
                       background=self.bg_color,
                       foreground=self.text_color,
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Heading.TLabel',
                       background=self.panel_color,
                       foreground=self.text_color,
                       font=('Segoe UI', 11, 'bold'))
        
        style.configure('Dark.TLabel',
                       background=self.panel_color,
                       foreground=self.text_color,
                       font=('Segoe UI', 10))
        
        style.configure('Info.TLabel',
                       background=self.panel_color,
                       foreground=self.info_color,
                       font=('Segoe UI', 9))
        
        style.configure('Warning.TLabel',
                       background=self.panel_color,
                       foreground=self.warning_color,
                       font=('Segoe UI', 9))
        
        style.configure('Dark.TCheckbutton',
                       background=self.panel_color,
                       foreground=self.text_color,
                       focuscolor='none',
                       indicatorbackground=self.button_color,
                       indicatorforeground=self.text_color)
        
        style.configure('Dark.TCombobox',
                       fieldbackground=self.button_color,
                       background=self.button_color,
                       foreground=self.text_color,
                       borderwidth=1,
                       arrowcolor=self.text_color)
        
        style.configure('Accent.TButton',
                       background=self.accent_color,
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none',
                       font=('Segoe UI', 10))
        
        style.configure('Dark.TButton',
                       background=self.button_color,
                       foreground=self.text_color,
                       borderwidth=1,
                       focuscolor='none',
                       font=('Segoe UI', 10))
        
        style.map('Dark.TCheckbutton',
                 background=[('active', self.panel_color)])
        
        style.map('Dark.TCombobox',
                 focuscolor=[('!focus', 'none')],
                 bordercolor=[('focus', self.accent_color)])
        
        style.map('Accent.TButton',
                 background=[('active', '#ff8800')],
                 relief=[('pressed', 'flat')])
        
        style.map('Dark.TButton',
                 background=[('active', '#606060')],
                 relief=[('pressed', 'flat')])
        
        # Main frame with dark background
        main_frame = ttk.Frame(self.root, style='Dark.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Update Settings", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Current version info with dark theme
        info_frame = ttk.LabelFrame(main_frame, text="Current Version", style='Panel.TFrame', padding="15")
        info_frame.pack(fill='x', pady=(0, 15))
        
        current_version = get_current_version()
        version_label = ttk.Label(info_frame, text=f"Version: {current_version}", style='Dark.TLabel')
        version_label.pack(anchor='w')
        
        # Check for updates button
        check_frame = ttk.Frame(info_frame, style='Panel.TFrame')
        check_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(check_frame, text="Check for Updates Now", 
                  command=self.check_updates_now, style='Accent.TButton').pack(side='left')
        
        self.status_label = ttk.Label(check_frame, text="", style='Info.TLabel')
        self.status_label.pack(side='left', padx=(10, 0))
        
        # Auto-update settings with dark theme
        settings_frame = ttk.LabelFrame(main_frame, text="Automatic Update Settings", style='Panel.TFrame', padding="15")
        settings_frame.pack(fill='x', pady=(0, 15))
        
        # Auto-check setting
        ttk.Checkbutton(settings_frame, text="Automatically check for updates", 
                       variable=self.auto_check_var,
                       command=self.on_auto_check_changed, style='Dark.TCheckbutton').pack(anchor='w', pady=5)
        
        # Check interval
        interval_frame = ttk.Frame(settings_frame, style='Panel.TFrame')
        interval_frame.pack(fill='x', pady=(10, 15))
        
        ttk.Label(interval_frame, text="Check interval:", style='Dark.TLabel').pack(side='left')
        
        self.interval_combo = ttk.Combobox(interval_frame, textvariable=self.interval_var,
                                          values=list(self.interval_options.keys()),
                                          state='readonly', width=15, style='Dark.TCombobox')
        self.interval_combo.pack(side='left', padx=(10, 0))
        
        # Auto-download setting
        ttk.Checkbutton(settings_frame, text="Automatically download updates", 
                       variable=self.auto_download_var, style='Dark.TCheckbutton').pack(anchor='w', pady=5)
        
        # Auto-install setting
        ttk.Checkbutton(settings_frame, text="自动安装更新 (完全自动化)", 
                       variable=self.auto_install_var, 
                       command=self.on_auto_install_changed,
                       style='Dark.TCheckbutton').pack(anchor='w', pady=5)
        
        # Auto-install prompt setting (子选项)
        self.auto_install_prompt_frame = ttk.Frame(settings_frame, style='Panel.TFrame')
        self.auto_install_prompt_frame.pack(fill='x', padx=(20, 0), pady=(5, 5))
        
        self.auto_install_prompt_var = tk.BooleanVar(value=self.update_manager.config.get("auto_install_prompt", True))
        ttk.Checkbutton(self.auto_install_prompt_frame, text="安装前显示5秒倒计时提示", 
                       variable=self.auto_install_prompt_var,
                       style='Dark.TCheckbutton').pack(anchor='w')
        
        # Install delay setting
        delay_frame = ttk.Frame(self.auto_install_prompt_frame, style='Panel.TFrame')
        delay_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(delay_frame, text="安装延迟时间:", style='Dark.TLabel').pack(side='left')
        
        self.install_delay_var = tk.StringVar(value=str(self.update_manager.config.get("install_delay", 5)))
        install_delay_combo = ttk.Combobox(delay_frame, textvariable=self.install_delay_var,
                                         values=["0", "3", "5", "10", "15", "30"],
                                         state='readonly', width=10, style='Dark.TCombobox')
        install_delay_combo.pack(side='left', padx=(10, 5))
        ttk.Label(delay_frame, text="秒", style='Dark.TLabel').pack(side='left')
        
        # Warning note with proper wrapping and dark theme
        warning_frame = ttk.Frame(settings_frame, style='Panel.TFrame')
        warning_frame.pack(fill='x', pady=(10, 5))
        
        warning_label = ttk.Label(warning_frame, 
                                 text="⚠️ 警告: 自动安装会在发现更新后立即下载并安装，应用可能会突然重启。",
                                 style='Warning.TLabel', wraplength=450, justify='left')
        warning_label.pack(anchor='w', fill='x')
        
        # Additional warning info
        warning_label2 = ttk.Label(warning_frame,
                                  text="建议在工作时间使用手动安装模式，避免工作中断。",
                                  style='Warning.TLabel', wraplength=450, justify='left')
        warning_label2.pack(anchor='w', fill='x')
        
        # Update the prompt frame visibility based on auto_install setting
        self.on_auto_install_changed()
        
        # Download location with dark theme
        location_frame = ttk.LabelFrame(main_frame, text="Download Location", style='Panel.TFrame', padding="15")
        location_frame.pack(fill='x', pady=(0, 15))
        
        download_path = self.update_manager.config.get("download_path", "")
        ttk.Label(location_frame, text="Updates downloaded to:", style='Dark.TLabel').pack(anchor='w')
        
        # Path display with wrapping for long paths
        path_label = ttk.Label(location_frame, text=download_path, 
                              style='Info.TLabel', wraplength=480, justify='left')
        path_label.pack(anchor='w', fill='x', pady=(5, 0))
        
        # Buttons with dark theme
        button_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        button_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel, style='Dark.TButton').pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings, style='Accent.TButton').pack(side='right')
        
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
        
        # Create new window for release notes with dark theme
        notes_window = tk.Toplevel(self.root)
        notes_window.title(f"Release Notes - v{self.update_manager.latest_version}")
        notes_window.geometry("700x500")
        notes_window.resizable(True, True)  # Allow resizing for long release notes
        notes_window.configure(bg=self.bg_color)
        
        # Text widget with scrollbar and dark theme
        frame = ttk.Frame(notes_window, style='Dark.TFrame')
        frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Dark themed text widget
        text_widget = tk.Text(frame, wrap='word', font=('Segoe UI', 10),
                             bg=self.panel_color, fg=self.text_color,
                             insertbackground=self.text_color,
                             selectbackground=self.accent_color,
                             selectforeground='white',
                             borderwidth=1, relief='solid')
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
        
        # Download button with dark theme
        button_frame = ttk.Frame(notes_window, style='Dark.TFrame')
        button_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        ttk.Button(button_frame, text="Download Update", 
                  command=lambda: self.download_update(notes_window), style='Accent.TButton').pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Close", 
                  command=notes_window.destroy, style='Dark.TButton').pack(side='right')
    
    def download_update(self, parent_window=None):
        """Download the available update"""
        if not self.update_manager.update_available:
            messagebox.showinfo("No Update", "No update available to download.")
            return
        
        def download_thread():
            try:
                if parent_window:
                    parent_window.destroy()
                
                # Show progress dialog with dark theme
                progress_window = tk.Toplevel(self.root)
                progress_window.title("Downloading Update")
                progress_window.geometry("400x150")
                progress_window.resizable(False, False)
                progress_window.configure(bg=self.bg_color)
                
                # Main frame
                main_frame = ttk.Frame(progress_window, style='Dark.TFrame', padding="20")
                main_frame.pack(fill='both', expand=True)
                
                ttk.Label(main_frame, text="Downloading update...", 
                         font=('Segoe UI', 12), style='Title.TLabel').pack(pady=(0, 15))
                
                progress_var = tk.DoubleVar()
                progress_bar = ttk.Progressbar(main_frame, variable=progress_var, 
                                             maximum=100, length=300)
                progress_bar.pack(pady=10)
                
                status_label = ttk.Label(main_frame, text="Preparing...", style='Info.TLabel')
                status_label.pack(pady=(10, 0))
                
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
    
    def on_auto_install_changed(self):
        """Handle auto-install checkbox change"""
        try:
            # 如果禁用自动安装，隐藏相关的子选项
            if hasattr(self, 'auto_install_prompt_frame'):
                if self.auto_install_var.get():
                    # 显示子选项
                    for child in self.auto_install_prompt_frame.winfo_children():
                        child.configure(state='normal')
                else:
                    # 隐藏/禁用子选项
                    for child in self.auto_install_prompt_frame.winfo_children():
                        if hasattr(child, 'configure'):
                            child.configure(state='disabled')
        except Exception as e:
            print(f"[UPDATE GUI] Error in auto_install_changed: {e}")
    
    def save_settings(self):
        """Save the update settings"""
        try:
            # Update configuration
            self.update_manager.config["auto_check"] = self.auto_check_var.get()
            self.update_manager.config["auto_download"] = self.auto_download_var.get()
            self.update_manager.config["auto_install"] = self.auto_install_var.get()
            
            # Update new auto-install settings
            if hasattr(self, 'auto_install_prompt_var'):
                self.update_manager.config["auto_install_prompt"] = self.auto_install_prompt_var.get()
            if hasattr(self, 'install_delay_var'):
                try:
                    self.update_manager.config["install_delay"] = int(self.install_delay_var.get())
                except:
                    self.update_manager.config["install_delay"] = 5
            
            # Update check interval
            interval_name = self.interval_var.get()
            self.update_manager.config["check_interval"] = self.interval_options.get(interval_name, 3600)
            
            # Save configuration
            self.update_manager.save_config()
            
            messagebox.showinfo("Settings Saved", "更新设置已保存成功！\n\n自动更新功能已启用，系统将在检测到新版本时自动下载并安装。")
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"保存设置失败:\n{e}")
    
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
