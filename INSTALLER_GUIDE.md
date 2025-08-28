# 🚀 ConsoleDeck Professional Installer Guide

This guide explains how to create a professional Windows installer for ConsoleDeck using Inno Setup with automated GPIO configuration.

## 📋 Prerequisites

1. **Python 3.11+** - For building the executable
2. **Inno Setup 6** - For creating the installer
3. **All dependencies installed** - Run `pip install -r src/requirements.txt`

## 🔧 Step-by-Step Installation Creation

### Step 1: Install Inno Setup

1. Download Inno Setup from: https://jrsoftware.org/isdl.php
2. Install with default settings
3. Verify installation by checking if `ISCC.exe` is in the Inno Setup directory

### Step 2: Create Installer Assets

Run the asset creation script:
```bash
python create_installer_assets.py
```

This creates:
- `icon.ico` - Application icon
- `installer_image.bmp` - Wizard image
- `installer_small.bmp` - Small wizard image
- `LICENSE.txt` - License file

### Step 3: Build the Executable

Build the standalone executable:
```bash
pyinstaller --onefile --windowed --name=ConsoleDeck --add-data="src/gpio_config.json;." --add-data="src/pref.json;." --add-data="console_deck_v2_arduino_code;console_deck_v2_arduino_code" src/main.py
```

### Step 4: Create the Installer

Build the professional installer:
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

This generates `installer/ConsoleDeck_Setup.exe`

## 🎯 Installer Features

### Modern Wizard Interface
- Professional welcome page with feature overview
- GPIO configuration during installation
- Feature toggles (volume, media, debug controls)
- Input validation for COM port and baud rate

### Installation Options
- **Install Location**: Program Files (default) or custom location
- **Desktop Shortcut**: Optional desktop icon
- **Start Menu**: Automatic start menu integration
- **Startup**: Optional Windows startup registration
- **Quick Launch**: Optional quick launch bar icon

### GPIO Configuration
The installer prompts users to configure:
- **Arduino COM Port** (e.g., COM3, COM7) with validation
- **Baud Rate** (9600, 19200, 38400, 57600, or 115200) with validation
- All features (volume, media, debug) are enabled by default

### Post-Installation
- Automatic creation of `gpio_config.json` with user's settings
- Default `pref.json` with empty button configuration
- Option to launch ConsoleDeck immediately
- Desktop and start menu shortcuts created
- Optional Windows startup registration

## 📁 Generated Files

After running the installer creation:

```
installer/
└── ConsoleDeck_Setup.exe    # Professional installer
```

## 🎮 User Installation Experience

### Installation Process
1. **Welcome Screen** - Overview of ConsoleDeck features
2. **License Agreement** - MIT License acceptance
3. **Installation Directory** - Choose install location
4. **GPIO Configuration** - Configure Arduino settings
5. **Additional Tasks** - Desktop shortcut, startup, etc.
6. **Installation** - File copying and setup
7. **Completion** - Launch options and finish

### GPIO Configuration Screen
Users see a professional interface with:
- Text fields for COM port and baud rate
- Checkboxes for feature toggles
- Input validation with error messages
- Default values pre-filled

## 🔧 Customization Options

### Modify Installer Script
Edit `installer_script.iss` to customize:

```pascal
[Setup]
AppName=ConsoleDeck                    # Application name
AppVersion=2.0                         # Version number
AppPublisher=ConsoleDeck Team          # Publisher name
DefaultDirName={autopf}\ConsoleDeck    # Install directory
```

### Add Custom Pages
Add additional configuration pages:

```pascal
procedure InitializeWizard;
begin
  // Add custom pages here
  CustomPage := CreateInputQueryPage(wpWelcome,
    'Custom Configuration', 'Configure additional settings',
    'Add your custom configuration here.');
end;
```

### Modify File Installation
Add or remove files from installation:

```pascal
[Files]
Source: "your_file.txt"; DestDir: "{app}"; Flags: ignoreversion
```

## 🐛 Troubleshooting

### Build Issues

**"PyInstaller not found"**
```bash
pip install pyinstaller
```

**"Inno Setup not found"**
- Download and install Inno Setup from: https://jrsoftware.org/isdl.php
- Ensure ISCC.exe is located at: `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`

**"Missing assets"**
```bash
python create_installer_assets.py
```

**"Runtime error: app constant not initialized"**
- This has been fixed by moving GPIO config creation to post-install step
- The installer now creates configuration files after installation is complete

### Installer Issues

**"Invalid COM port"**
- The installer validates COM port format
- Must start with "COM" followed by a number

**"Invalid baud rate"**
- Must be a positive integer
- Common values: 9600, 115200, 57600

**"Permission denied"**
- Run installer as administrator if needed
- Check antivirus software interference

## 📦 Distribution

### What to Distribute
- `ConsoleDeck_Setup.exe` - The complete installer
- `README.md` - User documentation
- `arduino_code/` - Arduino sketch files (optional)

### What NOT to Distribute
- Source code files (.py)
- Build artifacts (build/, dist/)
- Development files (.spec, scripts)

## 🎉 Success!

After installation, users get:

1. **Professional Installation** - Standard Windows installer experience
2. **Automatic Configuration** - GPIO settings configured during install
3. **Desktop Integration** - Shortcuts and start menu entries
4. **Easy Uninstallation** - Proper Windows uninstaller
5. **Startup Option** - Automatic launch with Windows

## 🔄 Updates and Maintenance

### Version Updates
1. Update version numbers in `installer_script.iss`
2. Rebuild executable with PyInstaller
3. Recreate installer with `create_installer.bat`

### Configuration Changes
1. Modify `installer_script.iss` for new options
2. Update GPIO configuration logic
3. Test installer with different scenarios

## 📞 Support

For installer issues:
1. Check the Inno Setup documentation
2. Verify all prerequisites are installed
3. Test on clean Windows installations
4. Check Windows Event Viewer for errors

The professional installer provides a complete, user-friendly installation experience that matches commercial software standards!
