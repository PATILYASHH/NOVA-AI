@echo off
echo Removing NOVA Auto-Start...
echo.

set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

del "%STARTUP_DIR%\nova_autostart.vbs" 2>nul

echo NOVA auto-start removed.
echo.
pause
