@echo off
echo Installing NOVA Auto-Start...
echo.

:: Create shortcut in Windows Startup folder
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set VBS_PATH=C:\code\NOVA\nova_autostart.vbs

:: Copy VBS launcher to Startup folder
copy "%VBS_PATH%" "%STARTUP_DIR%\nova_autostart.vbs" /Y

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: NOVA will now auto-start when Windows boots.
    echo Location: %STARTUP_DIR%\nova_autostart.vbs
    echo.
    echo NOVA will start silently in the background.
    echo You will receive a Telegram message when NOVA is online.
) else (
    echo.
    echo FAILED: Could not install auto-start.
    echo Try running this script as Administrator.
)

echo.
pause
