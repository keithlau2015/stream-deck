# 🚀 ConsoleDeck Build Guide

This guide explains how to build ConsoleDeck into a standalone executable and create an installer using PyInstaller.

## 📋 Prerequisites

- Python 3.11 or higher
- Windows 10/11 (for the installer)
- All project dependencies installed

## 🔨 Quick Build

### Option 1: Automatic Build (Recommended)

1. **Run the build script:**
   ```bash
   build.bat
   ```

2. **The script will:**
   - Install PyInstaller
   - Build the executable
   - Create installer files

### Option 2: Manual Build

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build using the spec file:**
   ```bash
   pyinstaller ConsoleDeck.spec
   ```

3. **Or build with custom options:**
   ```bash
   pyinstaller --onefile --windowed --name=ConsoleDeck main.py
   ```

## 📁 Generated Files

After building, you'll find:

- **`dist/ConsoleDeck.exe`** - Main executable
- **`build/`** - Build cache (can be deleted)
- **`ConsoleDeck.spec`** - Build specification

## 🎯 Creating an Installer

### Option 1: Professional Installer (Inno Setup)

1. **Install Inno Setup:**
   - Download from: https://jrsoftware.org/isdl.php
   - Install with default settings

2. **Run the installer builder:**
   ```bash
   python build_installer.py
   ```

3. **Compile the installer:**
   - Open `installer_script.iss` in Inno Setup Compiler
   - Click "Build" → "Compile"
   - Find the installer in the `installer/` folder

### Option 2: Simple Batch Installer

1. **Run the simple installer:**
   ```bash
   install.bat
   ```

2. **The installer will:**
   - Copy files to user's ConsoleDeck folder
   - Configure GPIO settings interactively
   - Create desktop and start menu shortcuts

## ⚙️ Build Configuration

### PyInstaller Options

The `ConsoleDeck.spec` file includes:

- **One-file executable** - Single .exe file
- **Windowed mode** - No console window (use `--console` for debugging)
- **Data files** - Includes config files and Arduino code
- **Hidden imports** - All required Python modules
- **Icon support** - Add `icon.ico` for custom icon

### Customizing the Build

Edit `ConsoleDeck.spec` to modify:

- **Console output** - Change `console=False` to `True`
- **File inclusion** - Modify the `datas` list
- **Dependencies** - Add/remove from `hiddenimports`
- **Compression** - Enable/disable UPX compression

## 🔧 GPIO Configuration During Installation

The installer automatically:

1. **Prompts for Arduino settings:**
   - COM port (e.g., COM3, COM7)
   - Baud rate (default: 9600)

2. **Creates `gpio_config.json`:**
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

## 🚀 Distribution

### What to Include

- **ConsoleDeck.exe** - Main executable
- **gpio_config.json** - GPIO configuration
- **config.json** - Button configuration
- **arduino_code/** - Arduino sketch files
- **README.md** - User documentation

### What NOT to Include

- **Python source files** (.py)
- **Build artifacts** (build/, dist/, __pycache__/)
- **Development files** (.spec, build scripts)

## 🐛 Troubleshooting

### Build Issues

**"Module not found" errors:**
- Add missing modules to `hiddenimports` in the spec file
- Check that all dependencies are installed

**Large executable size:**
- Use `--onefile` instead of `--onedir`
- Enable UPX compression
- Exclude unnecessary modules

**Missing data files:**
- Verify all files are listed in the `datas` section
- Check file paths are correct

### Runtime Issues

**"File not found" errors:**
- Ensure data files are included in the build
- Check file paths in the spec file

**GPIO configuration not loading:**
- Verify `gpio_config.json` exists
- Check file permissions
- Use `--config-gpio` flag to debug

## 📝 Advanced Configuration

### Environment Variables

Set these before building for custom behavior:

```bash
set PYTHONPATH=.
set PYTHONHASHSEED=0
```

### Custom Icons

1. **Create an icon file:**
   - Use .ico format for Windows
   - Recommended size: 256x256 pixels

2. **Update the spec file:**
   ```python
   icon='path/to/your/icon.ico'
   ```

### Code Signing

For production releases:

1. **Obtain a code signing certificate**
2. **Sign the executable:**
   ```bash
   signtool sign /f certificate.pfx /p password ConsoleDeck.exe
   ```

## 🎉 Success!

After building, users can:

1. **Run the installer** to set up ConsoleDeck
2. **Configure GPIO settings** during installation
3. **Launch ConsoleDeck** from desktop/start menu
4. **Modify settings** by editing config files

The executable will work on any Windows machine without Python installed!
