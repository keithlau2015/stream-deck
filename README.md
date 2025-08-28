# 🎮 StreamDeck
> **Note**: This is a fork of the original [ConsoleDeck project](https://github.com/LucaDiLorenzo98/cd_v2_script) by [@LucaDiLorenzo98](https://github.com/LucaDiLorenzo98), enhanced with additional features and improvements.

StreamDeck is an enhanced version of the original ConsoleDeck - a simple graphical interface that allows you to configure up to 9 buttons to launch websites or executable files with a click.  
Ideal for creating your own customizable macro deck or personal launcher.

## ✨ What's New

- **System Tray Integration**: Runs in the background with a system tray icon
- **Enhanced Serial Communication**: Improved Arduino integration with volume control, mute toggle, and media controls
- **Better Configuration Management**: More robust config handling with reload capabilities
- **Improved GUI**: Enhanced user interface with better button states and visual feedback
- **Clipboard Integration**: Support for Ctrl+V to paste URLs and Ctrl+A/C for text selection
- **Background Operation**: Can run without keeping the GUI window open
- **Professional Installer**: Windows installer with GPIO configuration during installation
- **Standalone Executable**: No Python required for end users

---

## ✅ Requirements

### For End Users (Installer)
- Windows 10/11 (64-bit)
- Arduino board (optional, for hardware button support)

### For Developers (Source Code)
- Windows PC
- Python 3.11 or higher
- Internet connection (for dependency installation)
- Inno Setup 6 (for creating installers)

---

## 🐍 Step 1 – Install Python

1. Go to the [official Python website](https://www.python.org/downloads/)
2. Download **Python 3.11** or higher
3. During installation, **check the box** ✅ **"Add Python to PATH"**
4. Click **Install Now**

---

## 🚀 Quick Start

### Option 1: Use Pre-built Installer (Recommended for Users)
1. Download `StreamDeck_Setup.exe` from the releases page
2. Run the installer and follow the setup wizard
3. Configure your Arduino COM port during installation
4. Launch StreamDeck from the desktop shortcut

### Option 2: Build from Source (For Developers)

#### Step 1: Install Dependencies
```bash
pip install -r src/requirements.txt
```

#### Step 2: Run from Source
```bash
python src/main.py
```

---

## 🛠️ Building and Distribution

### Creating a Standalone Executable

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable:**
   ```bash
   pyinstaller --onefile --windowed --name=StreamDeck --add-data="src/gpio_config.json;." --add-data="src/pref.json;." --add-data="console_deck_v2_arduino_code;console_deck_v2_arduino_code" src/main.py
   ```

3. **Find the executable:**
   The built executable will be in the `dist/` folder.

### Creating a Professional Installer

1. **Install Inno Setup:**
   Download and install from: https://jrsoftware.org/isdl.php

2. **Create installer assets:**
   ```bash
   python create_installer_assets.py
   ```

3. **Build the installer:**
```bash
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

4. **Find the installer:**
   The installer will be created as `installer/StreamDeck_Setup.exe`

---

## ⚙️ Features

### Core Functionality
- Click one of the 9 buttons to assign an action
- **Type**: Choose between 'none', 'website', 'executable', or 'text'
  - **Website**: Enter a URL (e.g., `https://youtube.com`)
  - **Executable**: Browse and select a program to launch
  - **Text**: Enter text to display on the button
- **Value**: The URL, file path, or text content
- Click "Save Config" to save your settings

### Advanced Features
- **Serial Communication**: Arduino integration for hardware buttons
- **Volume Controls**: Hardware volume up/down and mute toggle
- **Media Controls**: Play/pause, next/previous track support
- **System Tray**: Minimize to system tray and run in background
- **Hotkeys**: Keyboard shortcuts for common actions
- **Clipboard Support**: Ctrl+V to paste URLs, Ctrl+A/C for text manipulation

### Hardware Support
- Arduino integration via serial communication
- Configurable COM port (default: COM7)
- Hardware button support for all 9 programmable buttons

Settings are stored in local configuration files:
- `gpio_config.json` - Arduino connection and feature settings
- `pref.json` - Button configurations and preferences

---

## 🔧 Configuration

### GPIO Settings
Configure Arduino connection in `gpio_config.json`:
```json
{
    "arduino": {
        "port": "COM7",
        "baudrate": 9600,
        "timeout": 1
    },
    "volume": {
        "enabled": true,
        "default_value": 0
    },
    "media": {
        "enabled": true
    },
    "debug": {
        "enabled": true,
        "log_level": "INFO"
    }
}
```

### Button Configuration
Button settings are stored in `pref.json`:
```json
{
    "1": {"type": "website", "value": "https://youtube.com"},
    "2": {"type": "executable", "value": "C:\\Path\\To\\Program.exe"},
    "3": {"type": "text", "value": "Custom Text"},
    "4": {"type": "none", "value": ""},
    ...
}
```

---

## 🎯 Arduino Integration

### Hardware Setup
1. Connect your Arduino to your PC
2. Upload the provided Arduino sketch from `console_deck_v2_arduino_code/`
3. Note the COM port (check Device Manager)
4. Configure the port in `gpio_config.json` or during installation

### Features
- **Hardware Buttons**: Physical buttons trigger the same actions as GUI buttons
- **Volume Control**: Dedicated volume up/down buttons
- **Media Control**: Play/pause and track navigation
- **Mute Toggle**: Quick mute/unmute functionality

---

## 🚨 Troubleshooting

### Common Issues

**"Python is not recognized"**
- Reinstall Python and check ✅ "Add Python to PATH"

**"No module named pygame"**
```bash
pip install pygame
```

**"Serial port not found"**
- Check Device Manager for correct COM port
- Update `gpio_config.json` with the correct port
- Ensure Arduino drivers are installed

**"Permission denied" errors**
- Run terminal as Administrator
- Check antivirus software settings

**Arduino not responding**
- Verify correct COM port in configuration
- Check USB cable connection
- Ensure Arduino sketch is uploaded correctly

### Build Issues

**PyInstaller errors**
```bash
pip install --upgrade pyinstaller
```

**Missing dependencies**
```bash
pip install -r src/requirements.txt
```

---

## 🙏 Acknowledgments

This project is based on the excellent work by [@LucaDiLorenzo98](https://github.com/LucaDiLorenzo98) and the original [ConsoleDeck project](https://github.com/LucaDiLorenzo98/cd_v2_script). Thank you for creating such a useful tool!

## 📁 Project Structure

```
stream-deck/
├── src/                          # Source code
│   ├── main.py                   # Main application entry point
│   ├── gpio.py                   # Arduino communication and GPIO handling
│   ├── gui.py                    # Pygame-based GUI interface
│   ├── tray.py                   # System tray integration
│   ├── prefController.py         # Button configuration management
│   ├── gpio_config.json          # GPIO settings (template)
│   ├── pref.json                 # Button configurations (template)
│   └── requirements.txt          # Python dependencies
├── console_deck_v2_arduino_code/ # Arduino sketch
│   └── console_deck_v2.ino       # Arduino firmware
├── installer/                    # Generated installer files
│   └── StreamDeck_Setup.exe      # Professional Windows installer
├── dist/                         # Built executables (generated)
├── build/                        # Build artifacts (generated)
├── installer_script.iss          # Inno Setup installer script
├── create_installer_assets.py    # Script to generate installer assets
├── LICENSE.txt                   # MIT License
├── README.md                     # This file
├── INSTALLER_GUIDE.md            # Detailed installer creation guide
└── .gitignore                    # Git ignore file
```
