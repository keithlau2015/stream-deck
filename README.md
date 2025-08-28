# 🎮 ConsoleDeck

> **Note**: This is a fork of the original [ConsoleDeck project](https://github.com/LucaDiLorenzo98/cd_v2_script) by [@LucaDiLorenzo98](https://github.com/LucaDiLorenzo98), enhanced with additional features and improvements.

ConsoleDeck is an enhanced version of the original ConsoleDeck - a simple graphical interface that allows you to configure up to 9 buttons to launch websites or executable files with a click.  
Ideal for creating your own customizable macro deck or personal launcher.

## ✨ What's New

- **System Tray Integration**: Runs in the background with a system tray icon
- **Enhanced Serial Communication**: Improved Arduino integration with volume control, mute toggle, and media controls
- **Better Configuration Management**: More robust config handling with reload capabilities
- **Improved GUI**: Enhanced user interface with better button states and visual feedback
- **Clipboard Integration**: Support for Ctrl+V to paste URLs and Ctrl+A/C for text selection
- **Background Operation**: Can run without keeping the GUI window open

---

## ✅ Requirements

- A Windows PC
- Python 3.11 or higher
- Internet connection (only for the initial setup)
- Arduino board (optional, for hardware button support)

---

## 🐍 Step 1 – Install Python

1. Go to 👉 [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest version of Python 3
3. During installation, **check the box** ✅ **"Add Python to PATH"**
4. Click **Install Now**

---

## 📦 Step 2 – Install required libraries

### Option 1: Automatic Installation (Recommended)
Run the provided batch file:
```bash
install_dependencies.bat
```

### Option 2: Manual Installation
1. Open the Start menu
2. Type `cmd` and press Enter
3. In the terminal window, paste the following command:

```bash
pip install -r requirements.txt
```

If you get an error like `'pip' is not recognized`, try restarting your PC.

---

## ▶️ Step 3 – Run ConsoleDeck

```bash
python main.py
```
---

## ⚙️ Features

### Core Functionality
- Click one of the 9 buttons to assign an action
- Choose between:
  - a website URL (e.g. `https://youtube.com`)
  - a `.exe` file on your PC
  - or no action
- Modify the fields directly inside the app
- Use the "Browse" button to select `.exe` files
- Save your changes only when you're ready

### Enhanced Features
- **System Tray Operation**: Right-click the tray icon for quick access
- **Serial Communication**: Full Arduino integration with:
  - Volume control (VOLUME_UP/DOWN)
  - Mute toggle
  - Media play/pause controls
- **Clipboard Support**: Ctrl+V to paste URLs, Ctrl+A/C for text operations
- **Configuration Reload**: Hot-reload config changes without restarting
- **Background Operation**: Runs silently in the background
- **Easy Configuration**: Interactive GPIO configuration utility
- **Flexible Settings**: Enable/disable features and configure Arduino connection

### Hardware Support
- Arduino integration via serial communication
- Configurable COM port (default: COM7)
- Hardware button support for all 9 programmable buttons

Settings are stored in a local file called `config.json`.

---

## 🔧 Configuration

### GPIO Configuration (Arduino Settings)
ConsoleDeck now uses a configuration file for Arduino settings.

Edit `gpio_config.json`:
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

### Configuration Options
- **Arduino Port**: COM port for Arduino connection (e.g., COM3, COM7)
- **Baud Rate**: Serial communication speed (default: 9600)
- **Serial Timeout**: Connection timeout in seconds
- **Volume Control**: Enable/disable volume and mute controls
- **Media Controls**: Enable/disable media play/pause
- **Debug Logging**: Enable/disable detailed logging

### Button Actions
Each button can be configured with:
- **Type**: `link`, `exe`, or `none`
- **Value**: URL for links, file path for executables

---

## ❓ Troubleshooting

**🟡 Nothing happens when I click a button?**  
Make sure you launched the app using: `python main.py`

**🔗 Can I use YouTube or other links?**  
Yes, any valid `https://` link will work.

**🧩 Can I assign programs like `.exe` files?**  
Yes! Use the "Browse" button to pick an executable file.

**💾 It says 'pip' is not recognized**  
Restart your computer or reinstall Python and ensure "Add Python to PATH" is selected during setup.

**🔌 Arduino not connecting?**  
Check your COM port in Device Manager and run `python configure_gpio.py` to update your Arduino settings

---

## 🧼 How to uninstall

- You can delete the project folder at any time
- To uninstall Python, go to **Apps & Features** in Windows

---

## 📬 Need help?

If you get stuck or the app doesn't behave as expected:
- Check the original project: [ConsoleDeck Script](https://github.com/LucaDiLorenzo98/cd_v2_script)
- Open an issue on this repository

---

## 🙏 Acknowledgments

This project is based on the excellent work by [@LucaDiLorenzo98](https://github.com/LucaDiLorenzo98) and the original [ConsoleDeck project](https://github.com/LucaDiLorenzo98/cd_v2_script). Thank you for creating such a useful tool!
