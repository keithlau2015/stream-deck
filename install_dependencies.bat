@echo off
title ConsoleDeck V2 - Install Dependencies
echo ConsoleDeck V2 - Installing Dependencies
echo =====================================
echo.
echo This will install all required Python packages for ConsoleDeck V2:
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
    echo You can now run ConsoleDeck V2 with:
    echo    python main.py
) else (
    echo ❌ There was an error installing dependencies.
    echo Please check your Python installation and try again.
)
echo.
pause
