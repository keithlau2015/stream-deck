@echo off
echo ConsoleDeck Installer Creator
echo =============================
echo.

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ and add it to PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
py -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    py -m pip install pyinstaller
)

REM Set Inno Setup path - check the most common location first
set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist %ISCC_PATH% (
    echo Found Inno Setup at: %ISCC_PATH%
    goto found_inno
)

set ISCC_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
if exist %ISCC_PATH% (
    echo Found Inno Setup at: %ISCC_PATH%
    goto found_inno
)

set ISCC_PATH="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
if exist %ISCC_PATH% (
    echo Found Inno Setup at: %ISCC_PATH%
    goto found_inno
)

set ISCC_PATH="C:\Program Files\Inno Setup 5\ISCC.exe"
if exist %ISCC_PATH% (
    echo Found Inno Setup at: %ISCC_PATH%
    goto found_inno
)

echo.
echo Inno Setup is not installed or not found!
echo Please download and install Inno Setup from:
echo https://jrsoftware.org/isdl.php
echo.
echo Expected installation paths:
echo   C:\Program Files (x86)\Inno Setup 6\
echo   C:\Program Files\Inno Setup 6\
echo.
pause
exit /b 1

:found_inno
echo.

echo Building ConsoleDeck executable...
REM First install dependencies
py -m pip install -r src/requirements.txt

REM Build using PyInstaller
py -m PyInstaller --onefile --windowed --name=ConsoleDeck --add-data="src/gpio_config.json;." --add-data="src/pref.json;." --add-data="console_deck_v2_arduino_code;console_deck_v2_arduino_code" src/main.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo Creating installer...
echo.

REM Compile the installer
%ISCC_PATH% installer_script.iss

if errorlevel 1 (
    echo.
    echo Installer creation failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installer created successfully!
echo ========================================
echo.
echo Generated files:
echo   - installer\ConsoleDeck_Setup.exe (main installer)
echo.
echo The installer includes:
echo   - Modern wizard interface
echo   - GPIO configuration during installation
echo   - Feature toggles (volume, media, debug)
echo   - Desktop and start menu shortcuts
echo   - Startup option
echo   - Proper uninstaller
echo.
echo Users can now run ConsoleDeck_Setup.exe to install ConsoleDeck!
echo.
pause
