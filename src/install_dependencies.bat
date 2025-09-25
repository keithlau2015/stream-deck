@echo off
title StreamDeck - Install Dependencies
echo StreamDeck - Installing Dependencies
echo =====================================
echo.
echo This will install all required Python packages for StreamDeck:
echo  * pygame (GUI and graphics)
echo  * pystray (system tray support)
echo  * Pillow (image processing)
echo  * pyperclip (clipboard operations)
echo  * pyserial (Arduino communication)
echo.
echo Installing packages...
echo.

pip install -r requirements.txt

echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ All dependencies installed successfully!
    echo.
    echo You can now run StreamDeck with:
    echo    python main.py
) else (
    echo ❌ There was an error installing dependencies.
    echo Please check your Python installation and try again.
)
echo.
pause
