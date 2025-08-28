#!/usr/bin/env python3
"""
StreamDeck Installer Builder
This script builds the StreamDeck executable using PyInstaller and creates an installer.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_gpio_config_template():
    """Create a template GPIO configuration file"""
    template = {
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
    
    with open("gpio_config_template.json", "w") as f:
        json.dump(template, f, indent=4)
    
    print("✓ GPIO configuration template created")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n🔨 Building StreamDeck executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=StreamDeck",
        "--add-data=src/gpio_config.json;.",
        "--add-data=src/pref.json;.",
        "--add-data=console_deck_v2_arduino_code;console_deck_v2_arduino_code",
        "--icon=icon.ico",  # You can add an icon file later
        "src/main.py"
    ]
    
    # Remove --windowed if you want console output
    if "--console" in sys.argv:
        cmd.remove("--windowed")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Executable built successfully")
        return True
    else:
        print("✗ Build failed:")
        print(result.stderr)
        return False

def find_inno_setup():
    """Find Inno Setup installation"""
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Try to find via registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1")
        install_location = winreg.QueryValueEx(key, "InstallLocation")[0]
        iscc_path = os.path.join(install_location, "ISCC.exe")
        if os.path.exists(iscc_path):
            return iscc_path
    except:
        pass
    
    return None

def create_installer_script():
    """Create Inno Setup script for the installer"""
    script = """[Setup]
AppName=StreamDeck
AppVersion=2.0
AppPublisher=StreamDeck Team
AppPublisherURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppSupportURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppUpdatesURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
DefaultDirName={autopf}\\StreamDeck
DefaultGroupName=StreamDeck
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=StreamDeck_Setup
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardImageFile=installer_image.bmp
WizardSmallImageFile=installer_small.bmp
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
DisableDirPage=no
DisableReadyPage=no
DisableFinishedPage=no
ShowLanguageDialog=no
UninstallDisplayIcon={app}\\StreamDeck.exe
UninstallDisplayName=StreamDeck
VersionInfoVersion=2.0.0.0
VersionInfoCompany=StreamDeck Team
VersionInfoDescription=StreamDeck - Customizable Macro Deck
VersionInfoCopyright=© 2024 StreamDeck Team

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "startup"; Description: "Start StreamDeck when Windows starts"; GroupDescription: "Startup Options"; Flags: unchecked

[Files]
Source: "dist\\StreamDeck.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "gpio_config_template.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\\pref.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "console_deck_v2_arduino_code\\*"; DestDir: "{app}\\arduino_code"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\StreamDeck"; Filename: "{app}\\StreamDeck.exe"
Name: "{group}\\Configure GPIO"; Filename: "{app}\\StreamDeck.exe"; Parameters: "--config-gpio"
Name: "{group}\\Uninstall StreamDeck"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\StreamDeck"; Filename: "{app}\\StreamDeck.exe"; Tasks: desktopicon
Name: "{userappdata}\\Microsoft\\Internet Explorer\\Quick Launch\\StreamDeck"; Filename: "{app}\\StreamDeck.exe"; Tasks: quicklaunchicon

[Registry]
Root: HKCU; Subkey: "Software\\Microsoft\\Windows\\CurrentVersion\\Run"; ValueType: string; ValueName: "StreamDeck"; ValueData: """{app}\\StreamDeck.exe"""; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\\StreamDeck.exe"; Description: "{cm:LaunchProgram,StreamDeck}"; Flags: nowait postinstall skipifsilent
Filename: "{app}\\StreamDeck.exe"; Parameters: "--config-gpio"; Description: "Configure GPIO Settings"; Flags: nowait postinstall skipifsilent

[Code]
var
  ConfigPage: TInputQueryWizardPage;
  ArduinoPort: String;
  BaudRate: String;

procedure InitializeWizard;
begin
  ConfigPage := CreateInputQueryPage(wpWelcome,
    'GPIO Configuration', 'Configure your Arduino connection settings',
    'Please specify the Arduino connection settings. You can change these later by running StreamDeck with --config-gpio parameter.');
    
  ConfigPage.Add('Arduino COM Port (e.g., COM3, COM7):', False);
  ConfigPage.Add('Baud Rate (default: 9600):', False);
  
  // Set default values
  ConfigPage.Values[0] := 'COM7';
  ConfigPage.Values[1] := '9600';
end;

procedure NextButtonClick(CurPageID: Integer);
var
  ConfigFile: String;
  ConfigContent: String;
begin
  if CurPageID = ConfigPage.ID then
  begin
    ArduinoPort := ConfigPage.Values[0];
    BaudRate := ConfigPage.Values[1];
    
    // Create gpio_config.json
    ConfigFile := ExpandConstant('{app}\\gpio_config.json');
    ConfigContent := '{\\n' +
      '    "arduino": {\\n' +
      '        "port": "' + ArduinoPort + '",\\n' +
      '        "baudrate": ' + BaudRate + ',\\n' +
      '        "timeout": 1\\n' +
      '    },\\n' +
      '    "volume": {\\n' +
      '        "enabled": true,\\n' +
      '        "default_value": 0\\n' +
      '    },\\n' +
      '    "media": {\\n' +
      '        "enabled": true\\n' +
      '    },\\n' +
      '    "debug": {\\n' +
      '        "enabled": true,\\n' +
      '        "log_level": "INFO"\\n' +
      '    }\\n' +
      '}';
    
    SaveStringToFile(ConfigFile, ConfigContent, False);
  end;
end;
"""
    
    with open("installer_script.iss", "w") as f:
        f.write(script)
    
    print("✓ Inno Setup script created")

def create_simple_installer():
    """Create a simple batch file installer as fallback"""
    installer_bat = """@echo off
echo StreamDeck Installer
echo ====================
echo.

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\\StreamDeck
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Installing to: %INSTALL_DIR%
echo.

REM Copy files
copy "dist\\StreamDeck.exe" "%INSTALL_DIR%\\"
copy "gpio_config_template.json" "%INSTALL_DIR%\\"
copy "src\\pref.json" "%INSTALL_DIR%\\"
if exist "console_deck_v2_arduino_code" xcopy "console_deck_v2_arduino_code" "%INSTALL_DIR%\\arduino_code\\" /E /I /Y
copy "README.md" "%INSTALL_DIR%\\"

REM Create gpio_config.json with user input
echo.
echo GPIO Configuration
echo ==================
set /p ARDUINO_PORT="Enter Arduino COM port (e.g., COM3, COM7) [COM7]: "
if "%ARDUINO_PORT%"=="" set ARDUINO_PORT=COM7

set /p BAUD_RATE="Enter baud rate [9600]: "
if "%BAUD_RATE%"=="" set BAUD_RATE=9600

echo Creating gpio_config.json...
echo {> "%INSTALL_DIR%\\gpio_config.json"
echo     "arduino": {>> "%INSTALL_DIR%\\gpio_config.json"
echo         "port": "%ARDUINO_PORT%",>> "%INSTALL_DIR%\\gpio_config.json"
echo         "baudrate": %BAUD_RATE%,>> "%INSTALL_DIR%\\gpio_config.json"
echo         "timeout": 1>> "%INSTALL_DIR%\\gpio_config.json"
echo     },>> "%INSTALL_DIR%\\gpio_config.json"
echo     "volume": {>> "%INSTALL_DIR%\\gpio_config.json"
echo         "enabled": true,>> "%INSTALL_DIR%\\gpio_config.json"
echo         "default_value": 0>> "%INSTALL_DIR%\\gpio_config.json"
echo     },>> "%INSTALL_DIR%\\gpio_config.json"
echo     "media": {>> "%INSTALL_DIR%\\gpio_config.json"
echo         "enabled": true>> "%INSTALL_DIR%\\gpio_config.json"
echo     },>> "%INSTALL_DIR%\\gpio_config.json"
echo     "debug": {>> "%INSTALL_DIR%\\gpio_config.json"
echo         "enabled": true,>> "%INSTALL_DIR%\\gpio_config.json"
echo         "log_level": "INFO">> "%INSTALL_DIR%\\gpio_config.json"
echo     }>> "%INSTALL_DIR%\\gpio_config.json"
echo }>> "%INSTALL_DIR%\\gpio_config.json"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\StreamDeck.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\StreamDeck.exe'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\StreamDeck" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\StreamDeck"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\StreamDeck\\StreamDeck.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\StreamDeck.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo StreamDeck has been installed to: %INSTALL_DIR%
echo Desktop shortcut created.
echo Start menu shortcut created.
echo.
echo To run StreamDeck, double-click the desktop shortcut or use the start menu.
echo.
pause
"""
    
    with open("install.bat", "w") as f:
        f.write(installer_bat)
    
    print("✓ Simple batch installer created")

def main():
    """Main build process"""
    print("🎮 StreamDeck Installer Builder")
    print("=" * 40)
    
    # Check dependencies
    check_dependencies()
    
    # Create GPIO config template
    create_gpio_config_template()
    
    # Build executable
    if not build_executable():
        print("✗ Build failed. Exiting.")
        return
    
    # Create installer scripts
    create_installer_script()
    create_simple_installer()
    
    # Try to create professional installer
    iscc_path = find_inno_setup()
    if iscc_path:
        print(f"\n🔨 Creating professional installer with Inno Setup...")
        print(f"Found Inno Setup at: {iscc_path}")
        
        result = subprocess.run([iscc_path, "installer_script.iss"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Professional installer created successfully!")
            print("  - installer/StreamDeck_Setup.exe")
        else:
            print("✗ Professional installer creation failed:")
            print(result.stderr)
            print("\nUsing simple batch installer instead...")
    else:
        print("\n⚠️  Inno Setup not found. Using simple batch installer.")
        print("To create a professional installer, install Inno Setup from:")
        print("https://jrsoftware.org/isdl.php")
    
    print("\n🎉 Build completed successfully!")
    print("\nGenerated files:")
    print("  - dist/StreamDeck.exe (main executable)")
    print("  - installer_script.iss (Inno Setup script)")
    print("  - install.bat (simple batch installer)")
    print("  - gpio_config_template.json (configuration template)")
    
    if iscc_path:
        print("\nProfessional installer created:")
        print("  - installer/StreamDeck_Setup.exe")
        print("\nUsers can run StreamDeck_Setup.exe for a professional installation experience!")
    else:
        print("\nSimple installer available:")
        print("  - install.bat")
        print("\nUsers can run install.bat for a simple installation.")

if __name__ == "__main__":
    main()
