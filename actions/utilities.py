"""
NOVA - Utilities Module
Clipboard, screenshot, browser, and other utilities
"""

import os
import time
import subprocess
import webbrowser
import logging
from datetime import datetime
from typing import Optional

from config import WHATSAPP_PHONE

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
    def _whatsapp_app_available() -> bool:
        """Check if a WhatsApp app handles the whatsapp:// protocol"""
        try:
            import winreg
            winreg.CloseKey(winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "whatsapp"))
            return True
        except Exception:
            return False

    @staticmethod
    def share_file_whatsapp(file_path: str, phone: str = None, wait_load: int = 15) -> dict:
        """
        Share a file to Yash's WhatsApp:
        1. Copy the file to the clipboard (as a file, not text)
        2. Open the direct chat (app if installed, else WhatsApp Web)
        3. Paste and send

        GUI automation - requires WhatsApp app or a logged-in WhatsApp Web
        session in the default browser. Delivery cannot be verified.
        """
        if not SCREENSHOT_AVAILABLE:
            return {"success": False, "error": "pyautogui not available - can't automate the paste"}

        phone = phone or WHATSAPP_PHONE
        if not phone:
            return {"success": False, "error": "WHATSAPP_PHONE is not set in .env"}

        path = os.path.abspath(os.path.expanduser(file_path))
        if not os.path.isfile(path):
            return {"success": False, "error": f"File not found: {path}"}

        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > 95:
            return {"success": False,
                    "error": f"File is {size_mb:.0f}MB - over WhatsApp's ~100MB media limit"}

        # 1. Put the file on the clipboard as a file drop (pyperclip only does text)
        try:
            ps = subprocess.run(
                ["powershell", "-NoProfile", "-Command", f'Set-Clipboard -Path "{path}"'],
                capture_output=True, text=True, timeout=20
            )
            if ps.returncode != 0:
                return {"success": False,
                        "error": f"Couldn't copy file to clipboard: {(ps.stderr or '')[:200]}"}
        except Exception as e:
            return {"success": False, "error": f"Clipboard copy failed: {e}"}

        # 2. Open the direct chat
        if Utilities._whatsapp_app_available():
            subprocess.Popen(f'cmd /c start "" "whatsapp://send?phone={phone}"', shell=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            opened_in = "WhatsApp app"
            time.sleep(8)
        else:
            webbrowser.open(f"https://web.whatsapp.com/send?phone={phone}")
            opened_in = "WhatsApp Web"
            time.sleep(wait_load)

        # 3. Paste the file and send
        try:
            pyautogui.hotkey("ctrl", "v")
            time.sleep(4)  # wait for the attachment preview to appear
            pyautogui.press("enter")
            time.sleep(2)
        except Exception as e:
            return {"success": False, "error": f"Paste/send automation failed: {e}"}

        return {
            "success": True,
            "message": (f"Copied {os.path.basename(path)} ({size_mb:.1f}MB), opened the chat "
                        f"with +{phone} in {opened_in}, pasted and hit send. "
                        f"Check WhatsApp to confirm - I can't verify delivery from here.")
        }

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
