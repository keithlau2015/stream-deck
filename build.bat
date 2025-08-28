@echo off
echo ConsoleDeck Build Script
echo ========================
echo.

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ and add it to PATH
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
py -m pip install -r requirements.txt

echo.
echo Installing PyInstaller...
py -m pip install pyinstaller

echo.
echo Building ConsoleDeck executable...
pyinstaller ConsoleDeck.spec

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo.
echo Generated files:
echo   - dist\ConsoleDeck.exe (main executable)
echo   - build\ (build cache - can be deleted)
echo   - ConsoleDeck.spec (build specification)
echo.
echo To create an installer, run:
echo   python build_installer.py
echo.
echo Or use the simple installer:
echo   install.bat
echo.
pause
