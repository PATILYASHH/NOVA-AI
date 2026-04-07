"""
NOVA - Utilities Module
Clipboard, screenshot, browser, and other utilities
"""

import os
import subprocess
import webbrowser
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

try:
    import pyautogui
    from PIL import ImageGrab
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False


class Utilities:
    """Utility operations for NOVA"""

    @staticmethod
    def clipboard_read() -> dict:
        """Read from clipboard"""
        if not CLIPBOARD_AVAILABLE:
            return {"success": False, "error": "Clipboard module not available"}
        try:
            content = pyperclip.paste()
            if len(content) > 4000:
                content = content[:4000] + "\n\n... [truncated]"
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def clipboard_write(text: str) -> dict:
        """Write to clipboard"""
        if not CLIPBOARD_AVAILABLE:
            return {"success": False, "error": "Clipboard module not available"}
        try:
            pyperclip.copy(text)
            return {"success": True, "message": "Text copied to clipboard"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def take_screenshot(save_path: Optional[str] = None) -> dict:
        """Take a screenshot"""
        if not SCREENSHOT_AVAILABLE:
            return {"success": False, "error": "Screenshot modules not available"}
        try:
            screenshot = ImageGrab.grab()

            if not save_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(os.path.expanduser("~"), "Desktop", f"screenshot_{timestamp}.png")

            screenshot.save(save_path)
            return {"success": True, "path": save_path, "message": f"Screenshot saved to {save_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def open_url(url: str) -> dict:
        """Open URL in default browser"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            return {"success": True, "message": f"Opened {url}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def search_google(query: str) -> dict:
        """Search Google"""
        try:
            import urllib.parse
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(url)
            return {"success": True, "message": f"Searching Google for: {query}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_current_time() -> dict:
        """Get current date and time"""
        now = datetime.now()
        return {
            "success": True,
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day": now.strftime("%A")
        }

    @staticmethod
    def set_reminder(message: str, minutes: int) -> dict:
        """Set a reminder (creates a scheduled task)"""
        try:
            trigger_time = datetime.now()
            trigger_time = trigger_time.replace(minute=trigger_time.minute + minutes)
            time_str = trigger_time.strftime("%H:%M")

            # Create a simple PowerShell reminder
            ps_command = f'''
            $trigger = New-ScheduledTaskTrigger -Once -At "{time_str}"
            $action = New-ScheduledTaskAction -Execute "msg" -Argument "* {message}"
            Register-ScheduledTask -TaskName "NOVA_Reminder_{int(datetime.now().timestamp())}" -Trigger $trigger -Action $action -Force
            '''

            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {"success": True, "message": f"Reminder set for {time_str}: {message}"}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
