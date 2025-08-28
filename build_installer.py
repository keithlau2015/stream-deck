#!/usr/bin/env python3
"""
ConsoleDeck Installer Builder
This script builds the ConsoleDeck executable using PyInstaller and creates an installer.
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
    
    try:
        import inno_setup_compiler
        print("✓ Inno Setup Compiler found")
    except ImportError:
        print("✗ Inno Setup Compiler not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "inno-setup-compiler"])

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
    print("\n🔨 Building ConsoleDeck executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=ConsoleDeck",
        "--add-data=gpio_config_template.json;.",
        "--add-data=config.json;.",
        "--icon=icon.ico",  # You can add an icon file later
        "main.py"
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

def create_installer_script():
    """Create Inno Setup script for the installer"""
    script = """[Setup]
AppName=ConsoleDeck
AppVersion=2.0
AppPublisher=ConsoleDeck Team
AppPublisherURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppSupportURL=https://github.com/LucaDiLorenzo98/cd_v2_script
AppUpdatesURL=https://github.com/LucaDiLorenzo98/cd_v2_script
DefaultDirName={autopf}\\ConsoleDeck
DefaultGroupName=ConsoleDeck
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=ConsoleDeck_Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\\ConsoleDeck.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "gpio_config_template.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "console_deck_v2_arduino_code\\*"; DestDir: "{app}\\arduino_code"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\ConsoleDeck"; Filename: "{app}\\ConsoleDeck.exe"
Name: "{group}\\Configure GPIO"; Filename: "{app}\\ConsoleDeck.exe"; Parameters: "--config-gpio"
Name: "{group}\\Uninstall ConsoleDeck"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\ConsoleDeck"; Filename: "{app}\\ConsoleDeck.exe"; Tasks: desktopicon
Name: "{userappdata}\\Microsoft\\Internet Explorer\\Quick Launch\\ConsoleDeck"; Filename: "{app}\\ConsoleDeck.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\\ConsoleDeck.exe"; Description: "{cm:LaunchProgram,ConsoleDeck}"; Flags: nowait postinstall skipifsilent
Filename: "{app}\\ConsoleDeck.exe"; Parameters: "--config-gpio"; Description: "Configure GPIO Settings"; Flags: nowait postinstall skipifsilent

[Code]
var
  ConfigPage: TInputQueryWizardPage;
  ArduinoPort: String;
  BaudRate: String;

procedure InitializeWizard;
begin
  ConfigPage := CreateInputQueryPage(wpWelcome,
    'GPIO Configuration', 'Configure your Arduino connection settings',
    'Please specify the Arduino connection settings. You can change these later by running ConsoleDeck with --config-gpio parameter.');
    
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
    ConfigContent := '{\n' +
      '    "arduino": {\n' +
      '        "port": "' + ArduinoPort + '",\n' +
      '        "baudrate": ' + BaudRate + ',\n' +
      '        "timeout": 1\n' +
      '    },\n' +
      '    "volume": {\n' +
      '        "enabled": true,\n' +
      '        "default_value": 0\n' +
      '    },\n' +
      '    "media": {\n' +
      '        "enabled": true\n' +
      '    },\n' +
      '    "debug": {\n' +
      '        "enabled": true,\n' +
      '        "log_level": "INFO"\n' +
      '    }\n' +
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
echo ConsoleDeck Installer
echo ====================
echo.

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\\ConsoleDeck
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Installing to: %INSTALL_DIR%
echo.

REM Copy files
copy "dist\\ConsoleDeck.exe" "%INSTALL_DIR%\\"
copy "gpio_config_template.json" "%INSTALL_DIR%\\"
copy "config.json" "%INSTALL_DIR%\\"
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
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\ConsoleDeck.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\ConsoleDeck.exe'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ConsoleDeck" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ConsoleDeck"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ConsoleDeck\\ConsoleDeck.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\ConsoleDeck.exe'; $Shortcut.Save()"

echo.
echo Installation complete!
echo ConsoleDeck has been installed to: %INSTALL_DIR%
echo Desktop shortcut created.
echo Start menu shortcut created.
echo.
echo To run ConsoleDeck, double-click the desktop shortcut or use the start menu.
echo.
pause
"""
    
    with open("install.bat", "w") as f:
        f.write(installer_bat)
    
    print("✓ Simple batch installer created")

def main():
    """Main build process"""
    print("🎮 ConsoleDeck Installer Builder")
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
    
    print("\n🎉 Build completed successfully!")
    print("\nGenerated files:")
    print("  - dist/ConsoleDeck.exe (main executable)")
    print("  - installer_script.iss (Inno Setup script)")
    print("  - install.bat (simple batch installer)")
    print("  - gpio_config_template.json (configuration template)")
    
    print("\nNext steps:")
    print("1. Install Inno Setup from: https://jrsoftware.org/isdl.php")
    print("2. Compile installer_script.iss with Inno Setup Compiler")
    print("3. Or use install.bat for simple installation")
    
    print("\nThe installer will:")
    print("  - Install ConsoleDeck to Program Files")
    print("  - Create desktop and start menu shortcuts")
    print("  - Configure GPIO settings during installation")
    print("  - Allow users to customize Arduino connection")

if __name__ == "__main__":
    main()
