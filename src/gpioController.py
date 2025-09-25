import os
import json
import copy
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import serial.tools.list_ports

def get_resource_path(relative_path):
    """Get the absolute path to a resource, works for PyInstaller bundles and source"""
    try:
        # If running from PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        
        # If running from source
        if __file__:
            return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative_path)
        
        # If running from installed app
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    except:
        return relative_path

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
                print(f"[GPIO CONFIG] Configuration loaded from {GPIO_CONFIG_FILE}")
                return config
        else:
            # Create default config file
            with open(GPIO_CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
                print(f"[GPIO CONFIG] Created default configuration file: {GPIO_CONFIG_FILE}")
                return DEFAULT_CONFIG
    except Exception as e:
        print(f"[GPIO CONFIG ERROR] Failed to load configuration: {e}")
        print(f"[GPIO CONFIG] Using default configuration")
        return DEFAULT_CONFIG

def save_gpio_config(config):
    """Save GPIO configuration to file"""
    try:
        with open(GPIO_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"[GPIO CONFIG] Configuration saved to {GPIO_CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"[GPIO CONFIG ERROR] Failed to save configuration: {e}")
        return False

def validate_com_port(port):
    """Validate COM port format"""
    if not port.upper().startswith('COM'):
        return False
    try:
        port_num = int(port[3:])
        return 1 <= port_num <= 99
    except ValueError:
        return False

def get_available_ports():
    """Get list of available COM ports"""
    try:
        ports = serial.tools.list_ports.comports()
        available_ports = []
        for port in ports:
            available_ports.append(port.device)
        return available_ports if available_ports else ["COM1", "COM3", "COM7"]  # Fallback ports
    except Exception as e:
        print(f"[GPIO] Warning: Could not detect COM ports: {e}")
        return ["COM1", "COM3", "COM7"]  # Fallback ports

def validate_baudrate(baudrate):
    """Validate baudrate value"""
    valid_rates = [9600, 19200, 38400, 57600, 115200]
    try:
        rate = int(baudrate)
        return rate in valid_rates
    except ValueError:
        return False

class GPIOConfigGUI:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("StreamDeck - GPIO Settings")
        self.root.geometry("620x480")
        self.root.resizable(False, False)
        
        # Set window icon (if available)
        try:
            from icon_utils import set_tkinter_window_icon
            set_tkinter_window_icon(self.root)
        except ImportError:
            print("[GPIO] Icon utils not available, using fallback")
            # Fallback if icon_utils is not available
            try:
                icon_path = get_resource_path(os.path.join('assets', 'icon.ico'))
                if os.path.exists(icon_path):
                    self.root.iconbitmap(default=icon_path)
                    print(f"[GPIO] Window icon set from: {icon_path}")
            except Exception as e:
                print(f"[GPIO WARNING] Failed to set window icon: {e}")
        
        # Configure dark theme colors
        self.bg_color = "#282828"
        self.panel_color = "#3c3c3c"
        self.button_color = "#505050"
        self.text_color = "#ffffff"
        self.accent_color = "#ff7700"
        
        self.root.configure(bg=self.bg_color)
        
        # Load current configuration
        self.config = load_gpio_config()
        self.original_config = copy.deepcopy(self.config)
        
        # Create StringVar for input fields
        self.port_var = tk.StringVar(value=str(self.config['arduino']['port']))
        self.baudrate_var = tk.StringVar(value=str(self.config['arduino']['baudrate']))
        self.timeout_var = tk.StringVar(value=str(self.config['arduino']['timeout']))
        
        # Create BooleanVar for checkboxes
        self.volume_var = tk.BooleanVar(value=self.config['volume']['enabled'])
        self.media_var = tk.BooleanVar(value=self.config['media']['enabled'])
        self.debug_var = tk.BooleanVar(value=self.config['debug']['enabled'])
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the tkinter UI"""
        # Configure style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles for dark theme
        style.configure('Title.TLabel', 
                       background=self.bg_color, 
                       foreground=self.text_color, 
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Section.TLabel',
                       background=self.panel_color,
                       foreground=self.text_color,
                       font=('Segoe UI', 11, 'bold'))
        
        style.configure('Hint.TLabel',
                       background=self.panel_color,
                       foreground='#aaaaaa',
                       font=('Segoe UI', 8))
        
        style.configure('Dark.TFrame',
                       background=self.panel_color,
                       borderwidth=1,
                       relief='solid',
                       bordercolor='#555555')
        
        # Frame without border for input containers
        style.configure('Clean.TFrame',
                       background=self.panel_color,
                       borderwidth=0,
                       relief='flat')
        
        style.configure('Main.TFrame',
                       background=self.bg_color)
        
        style.configure('Dark.TEntry',
                       fieldbackground='#505050',
                       background='#505050',
                       foreground=self.text_color,
                       borderwidth=1,
                       insertcolor=self.text_color,
                       selectbackground=self.accent_color,
                       selectforeground='white')
        
        style.configure('Dark.TCombobox',
                       fieldbackground='#505050',
                       background='#505050',
                       foreground=self.text_color,
                       borderwidth=1,
                       selectbackground=self.accent_color,
                       selectforeground='white',
                       arrowcolor=self.text_color,
                       insertcolor=self.text_color)
        
        # Configure the dropdown part of combobox
        style.map('Dark.TCombobox',
                 fieldbackground=[('readonly', '#505050')],
                 selectbackground=[('readonly', '#505050')],
                 focuscolor=[('!focus', 'none')],
                 bordercolor=[('focus', self.accent_color)])
        
        style.configure('Dark.TCheckbutton',
                       background=self.panel_color,
                       foreground=self.text_color,
                       focuscolor='none',
                       indicatorcolor='#505050',
                       indicatorbackground='#505050',
                       indicatorforeground=self.text_color)
        
        style.configure('Save.TButton',
                       background=self.accent_color,
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none')
        
        style.configure('Cancel.TButton',
                       background='#666666',
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none')
        
        style.configure('Dark.TButton',
                       background='#404040',
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none')
        
        style.map('Dark.TEntry',
                 focuscolor=[('!focus', 'none')],
                 bordercolor=[('focus', self.accent_color)])
        
        style.map('Dark.TCombobox',
                 focuscolor=[('!focus', 'none')],
                 bordercolor=[('focus', self.accent_color)])
        
        style.map('Save.TButton',
                 background=[('active', '#ff8800')],
                 relief=[('pressed', 'flat')])
        
        style.map('Cancel.TButton',
                 background=[('active', '#777777')],
                 relief=[('pressed', 'flat')])
        
        style.map('Dark.TButton',
                 background=[('active', '#555555')],
                 relief=[('pressed', 'flat')])
        
        # Main container with proper background
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Main title
        title_label = ttk.Label(main_frame, text="GPIO Configuration", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Arduino Connection Frame
        arduino_frame = ttk.Frame(main_frame, style='Dark.TFrame', padding=15)
        arduino_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(arduino_frame, text="Arduino Connection", style='Section.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Use grid layout for better control - no border to avoid double borders
        inputs_frame = ttk.Frame(arduino_frame, style='Clean.TFrame')
        inputs_frame.pack(fill='x', pady=10)
        
        # Configure grid columns with proper weights
        inputs_frame.grid_columnconfigure(0, weight=1, minsize=160)
        inputs_frame.grid_columnconfigure(1, weight=1, minsize=120)
        inputs_frame.grid_columnconfigure(2, weight=1, minsize=120)
        
        # COM Port (Column 0)
        port_frame = ttk.Frame(inputs_frame, style='Clean.TFrame')
        port_frame.grid(row=0, column=0, padx=(0, 15), sticky='ew')
        
        # Port label with more spacing
        ttk.Label(port_frame, text="COM Port:", style='Section.TLabel').pack(anchor='w', pady=(0, 3))
        
        # Port combobox and refresh button container
        port_input_frame = ttk.Frame(port_frame, style='Clean.TFrame')
        port_input_frame.pack(fill='x', pady=(0, 3))
        
        # Get available ports
        self.available_ports = get_available_ports()
        current_port = self.port_var.get()
        if current_port and current_port not in self.available_ports:
            self.available_ports.append(current_port)
        
        self.port_combo = ttk.Combobox(port_input_frame, textvariable=self.port_var, width=10,
                                      values=self.available_ports, style='Dark.TCombobox')
        self.port_combo.pack(side='left', fill='x', expand=True)
        
        refresh_btn = ttk.Button(port_input_frame, text="🔄", width=2, 
                                command=self.refresh_ports, style='Dark.TButton')
        refresh_btn.pack(side='right', padx=(3, 0))
        
        ttk.Label(port_frame, text="Auto-detected ports", style='Hint.TLabel').pack(anchor='w')
        
        # Baud Rate (Column 1)
        baud_frame = ttk.Frame(inputs_frame, style='Clean.TFrame')
        baud_frame.grid(row=0, column=1, padx=(0, 15), sticky='ew')
        
        ttk.Label(baud_frame, text="Baud Rate:", style='Section.TLabel').pack(anchor='w', pady=(0, 3))
        self.baud_combo = ttk.Combobox(baud_frame, textvariable=self.baudrate_var, width=10,
                                      values=['9600', '19200', '38400', '57600', '115200'],
                                      state='readonly', style='Dark.TCombobox')
        self.baud_combo.pack(pady=(0, 3), fill='x')
        ttk.Label(baud_frame, text="Standard rates", style='Hint.TLabel').pack(anchor='w')
        
        # Timeout (Column 2)
        timeout_frame = ttk.Frame(inputs_frame, style='Clean.TFrame')
        timeout_frame.grid(row=0, column=2, sticky='ew')
        
        ttk.Label(timeout_frame, text="Timeout (s):", style='Section.TLabel').pack(anchor='w', pady=(0, 3))
        self.timeout_entry = ttk.Entry(timeout_frame, textvariable=self.timeout_var, width=10, style='Dark.TEntry')
        self.timeout_entry.pack(pady=(0, 3), fill='x')
        ttk.Label(timeout_frame, text="0.1 - 10 seconds", style='Hint.TLabel').pack(anchor='w')
        
        # Features Frame
        features_frame = ttk.Frame(main_frame, style='Dark.TFrame', padding=15)
        features_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(features_frame, text="Features", style='Section.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Checkboxes with better spacing - no border to avoid double borders
        checkbox_frame = ttk.Frame(features_frame, style='Clean.TFrame')
        checkbox_frame.pack(fill='x')
        
        self.volume_check = ttk.Checkbutton(checkbox_frame, text="Volume Control", 
                                           variable=self.volume_var, style='Dark.TCheckbutton')
        self.volume_check.pack(anchor='w', pady=3)
        
        self.media_check = ttk.Checkbutton(checkbox_frame, text="Media Control",
                                          variable=self.media_var, style='Dark.TCheckbutton')
        self.media_check.pack(anchor='w', pady=3)
        
        self.debug_check = ttk.Checkbutton(checkbox_frame, text="Debug Logging",
                                          variable=self.debug_var, style='Dark.TCheckbutton')
        self.debug_check.pack(anchor='w', pady=3)
        
        # Buttons Frame
        buttons_frame = ttk.Frame(main_frame, style='Main.TFrame')
        buttons_frame.pack(fill='x', pady=(15, 0))
        
        # Save and Cancel buttons with custom styles
        ttk.Button(buttons_frame, text="Cancel", command=self.cancel, 
                  style='Cancel.TButton', width=10).pack(side='right', padx=(10, 0))
        ttk.Button(buttons_frame, text="Save", command=self.save_config, 
                  style='Save.TButton', width=10).pack(side='right')
    
    def refresh_ports(self):
        """Refresh the list of available COM ports"""
        try:
            # Get updated list of ports
            self.available_ports = get_available_ports()
            current_port = self.port_var.get()
            
            # Ensure current port is still in the list
            if current_port and current_port not in self.available_ports:
                self.available_ports.append(current_port)
            
            # Update combobox values
            self.port_combo['values'] = self.available_ports
            
            print(f"[GPIO] Refreshed COM ports: {self.available_ports}")
        except Exception as e:
            print(f"[GPIO] Error refreshing ports: {e}")
            messagebox.showerror("Error", f"Failed to refresh COM ports: {e}")
    
    def validate_inputs(self):
        """Validate all input fields"""
        errors = []
        
        # Validate COM port
        if not validate_com_port(self.port_var.get()):
            errors.append("Invalid COM port format")
        
        # Validate baud rate
        if not validate_baudrate(self.baudrate_var.get()):
            errors.append("Invalid baud rate")
        
        # Validate timeout
        try:
            timeout = float(self.timeout_var.get())
            if timeout < 0.1 or timeout > 10:
                errors.append("Timeout must be between 0.1 and 10 seconds")
        except ValueError:
            errors.append("Invalid timeout value")
        
        return errors
    
    def save_config(self):
        """Save the current configuration"""
        errors = self.validate_inputs()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return False
        
        # Update configuration
        self.config['arduino']['port'] = self.port_var.get().upper()
        self.config['arduino']['baudrate'] = int(self.baudrate_var.get())
        self.config['arduino']['timeout'] = float(self.timeout_var.get())
        
        self.config['volume']['enabled'] = self.volume_var.get()
        self.config['media']['enabled'] = self.media_var.get()
        self.config['debug']['enabled'] = self.debug_var.get()
        
        # Save to file
        if save_gpio_config(self.config):
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
            # Trigger immediate GPIO config reload
            try:
                from gpio import signal_gpio_reload, get_current_gpio_settings
                print(f"[GPIO CONFIG] Triggering GPIO reload...")
                signal_gpio_reload()
                print("[GPIO CONFIG] GPIO reload signal sent to GPIO system")
                
                # Print current settings for verification
                settings = get_current_gpio_settings()
                print(f"[GPIO CONFIG] Current settings: {settings}")
            except Exception as e:
                print(f"[GPIO CONFIG] Warning: Could not signal GPIO reload: {e}")
                import traceback
                traceback.print_exc()
            
            self.root.destroy()
            return True
        else:
            messagebox.showerror("Error", "Failed to save configuration!")
            return False
    
    def cancel(self):
        """Cancel and close the configuration window"""
        self.root.destroy()
    
    def run(self):
        """Main GUI loop"""
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Start the tkinter main loop
        self.root.mainloop()

def open_gpio_config_gui():
    """Open the GPIO configuration GUI"""
    try:
        gui = GPIOConfigGUI()
        gui.run()
    except Exception as e:
        print(f"[GPIO CONFIG ERROR] Failed to open GUI: {e}")
