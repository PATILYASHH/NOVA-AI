"""
NOVA - System Control Module
Handles system commands, apps, and PC control
"""

import os
import subprocess
import logging
import time
import glob as glob_mod
import winreg
import psutil
from typing import Optional, List

logger = logging.getLogger(__name__)


class SystemControl:
    """Handle system-level operations"""

    # Common applications mapped to executable names and known install paths
    APPS = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "files": "explorer.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "powershell": "powershell.exe",
        "vscode": "code",
        "vs code": "code",
        "visual studio code": "code",
        "code": "code",
        "chrome": "chrome",
        "google chrome": "chrome",
        "firefox": "firefox",
        "edge": "msedge",
        "microsoft edge": "msedge",
        "brave": "brave",
        "word": "winword",
        "microsoft word": "winword",
        "excel": "excel",
        "microsoft excel": "excel",
        "outlook": "outlook",
        "teams": "teams",
        "microsoft teams": "teams",
        "slack": "slack",
        "discord": "discord",
        "spotify": "spotify",
        "vlc": "vlc",
        "terminal": "wt.exe",
        "windows terminal": "wt.exe",
        "task manager": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "paint": "mspaint.exe",
        "snipping tool": "SnippingTool.exe",
        "settings": "ms-settings:",
        "control panel": "control.exe",
        "tally": "tally",
        "whatsapp": "whatsapp",
        "telegram": "telegram",
        "postman": "postman",
    }

    # Known install locations for apps not typically in PATH
    APP_SEARCH_PATHS = {
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ],
        "firefox": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ],
        "brave": [
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        ],
        "msedge": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],
        "discord": [
            os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe"),
        ],
        "spotify": [
            os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
        ],
        "slack": [
            os.path.expandvars(r"%LOCALAPPDATA%\slack\slack.exe"),
        ],
        "teams": [
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Teams\current\Teams.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Teams\Update.exe --processStart ms-teams.exe"),
        ],
        "postman": [
            os.path.expandvars(r"%LOCALAPPDATA%\Postman\Postman.exe"),
        ],
        "telegram": [
            os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe"),
        ],
        "vlc": [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ],
        "whatsapp": [
            os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe"),
        ],
        "tally": [
            r"C:\Program Files\TallyPrime\tally.exe",
            r"C:\Tally\tally.exe",
            r"C:\TallyPrime\tally.exe",
        ],
        "code": [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
        ],
    }

    @staticmethod
    def run_command(command: str, cwd: Optional[str] = None, timeout: int = 60) -> dict:
        """Execute a shell command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout
            )

            output = result.stdout or result.stderr or "Command executed (no output)"

            # Truncate long output
            if len(output) > 4000:
                output = output[:4000] + "\n\n... [truncated]"

            return {
                "success": result.returncode == 0,
                "output": output,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def _find_exe_path(cls, command: str) -> Optional[str]:
        """Find the full path to an executable using multiple strategies."""
        # Strategy 1: Check if command is already a full path that exists
        if os.path.isfile(command):
            return command

        # Strategy 2: Use 'where' command (Windows equivalent of 'which')
        try:
            result = subprocess.run(
                f'where {command}',
                shell=True, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0].strip()
        except Exception:
            pass

        # Strategy 3: Check known install paths
        search_key = command.lower().replace('.exe', '')
        if search_key in cls.APP_SEARCH_PATHS:
            for path in cls.APP_SEARCH_PATHS[search_key]:
                # Handle special cases like Discord's Update.exe --processStart
                actual_path = path.split(' ')[0] if ' --' in path else path
                if os.path.isfile(actual_path):
                    return path  # Return full string including args

        # Strategy 4: Search common directories (depth-limited - a recursive
        # glob over Program Files/AppData can block for minutes)
        search_dirs = [
            os.path.expandvars(r"%PROGRAMFILES%"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%"),
            os.path.expandvars(r"%LOCALAPPDATA%"),
            os.path.expandvars(r"%APPDATA%"),
        ]
        exe_name = command if command.endswith('.exe') else f"{command}.exe"
        for base_dir in search_dirs:
            for depth in (exe_name,
                          os.path.join('*', exe_name),
                          os.path.join('*', '*', exe_name)):
                matches = glob_mod.glob(os.path.join(base_dir, depth))
                if matches:
                    return matches[0]

        # Strategy 5: Check Windows registry for installed apps
        try:
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
            ]
            for hive, reg_path in reg_paths:
                try:
                    key = winreg.OpenKey(hive, f"{reg_path}\\{exe_name}")
                    value, _ = winreg.QueryValueEx(key, "")
                    winreg.CloseKey(key)
                    if value and os.path.isfile(value.strip('"')):
                        return value.strip('"')
                except FileNotFoundError:
                    continue
        except Exception:
            pass

        return None

    @classmethod
    def find_start_menu_app(cls, name: str) -> Optional[dict]:
        """
        Find an installed app's Start Menu shortcut by fuzzy name match.
        Returns {"name": <shortcut name>, "path": <.lnk path>} or None.
        """
        import difflib
        roots = [
            os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        ]
        shortcuts = {}
        for root in roots:
            if not os.path.isdir(root):
                continue
            for dirpath, _dirs, files in os.walk(root):
                for f in files:
                    if f.lower().endswith(".lnk"):
                        shortcuts.setdefault(os.path.splitext(f)[0].lower(),
                                             os.path.join(dirpath, f))
        if not shortcuts:
            return None

        key = name.lower().strip().replace(".exe", "")
        if key in shortcuts:
            return {"name": key, "path": shortcuts[key]}
        # Substring match (shortest wins: "anydesk" -> "AnyDesk" not "AnyDesk Uninstaller")
        subs = [k for k in shortcuts if key in k or k in key]
        if subs:
            best = min(subs, key=len)
            return {"name": best, "path": shortcuts[best]}
        close = difflib.get_close_matches(key, list(shortcuts.keys()), n=1, cutoff=0.75)
        if close:
            return {"name": close[0], "path": shortcuts[close[0]]}
        return None

    @classmethod
    def open_app(cls, app_name: str) -> dict:
        """Open an application: resolved exe -> Start Menu shortcut -> shell start"""
        try:
            app_lower = app_name.lower().strip()

            # Resolve the command name from known apps
            command = cls.APPS.get(app_lower, app_name)

            # Handle special URI schemes (ms-settings:, etc.)
            if ':' in command and not os.path.isabs(command):
                subprocess.Popen(f'cmd /c start "" "{command}"', shell=True,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"success": True, "message": f"Opened {app_name}"}

            # Try to find the executable
            exe_path = cls._find_exe_path(command)
            launched_via = None

            if exe_path:
                logger.info(f"Opening {app_name} via resolved path: {exe_path}")
                subprocess.Popen(f'cmd /c start "" "{exe_path}"', shell=True,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                launched_via = "exe"
            else:
                # Exe not found - check Start Menu shortcuts (fuzzy match).
                # Covers apps whose exe name differs from what Yash calls them.
                shortcut = cls.find_start_menu_app(app_name) or cls.find_start_menu_app(command)
                if shortcut:
                    logger.info(f"Opening {app_name} via Start Menu shortcut: {shortcut['path']}")
                    subprocess.Popen(f'cmd /c start "" "{shortcut["path"]}"', shell=True,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    launched_via = f"shortcut '{shortcut['name']}'"
                else:
                    # Last resort: shell start (apps registered in PATH or App Paths)
                    logger.info(f"Opening {app_name} via direct start command: {command}")
                    quoted = f'"{command}"' if " " in command else command
                    proc = subprocess.run(f'cmd /c start "" {quoted}', shell=True,
                                          capture_output=True, text=True, timeout=10)
                    if proc.returncode != 0 and proc.stderr:
                        return {"success": False,
                                "error": f"Couldn't find '{app_name}' on this PC - no exe, "
                                         f"no Start Menu entry. It doesn't look installed."}
                    launched_via = "shell"

            # Verify the app actually launched (check twice - some apps start slow)
            time.sleep(1.5)
            if cls._is_app_running(command, app_name):
                return {"success": True, "message": f"Opened {app_name}"}
            time.sleep(2.5)
            if cls._is_app_running(command, app_name):
                return {"success": True, "message": f"Opened {app_name}"}

            if launched_via == "shell":
                # Nothing resolved AND no process appeared - report honestly
                return {"success": False,
                        "error": f"Ran start for '{app_name}' but no matching process "
                                 f"appeared. It's probably not installed."}
            return {"success": True,
                    "message": f"Launched {app_name} via {launched_via} - process not "
                               f"visible yet, it may still be starting"}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Timed out trying to open {app_name}"}
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return {"success": False, "error": f"Failed to open {app_name}: {str(e)}"}

    @classmethod
    def _is_app_running(cls, command: str, app_name: str) -> bool:
        """Check if an application is currently running."""
        search_terms = [
            command.lower().replace('.exe', ''),
            app_name.lower().replace('.exe', ''),
        ]
        try:
            for proc in psutil.process_iter(['name']):
                proc_name = proc.info['name'].lower()
                for term in search_terms:
                    if term in proc_name:
                        return True
        except Exception:
            pass
        return False

    @classmethod
    def close_app(cls, app_name: str) -> dict:
        """Close an application by name"""
        try:
            app_lower = app_name.lower().strip()

            # Build search terms from both the display name and the executable name
            search_terms = {app_lower}
            if app_lower in cls.APPS:
                exe = cls.APPS[app_lower].lower().replace('.exe', '')
                search_terms.add(exe)

            # Find and terminate processes matching any search term
            killed = 0
            for proc in psutil.process_iter(['name', 'pid']):
                proc_name = proc.info['name'].lower()
                for term in search_terms:
                    if term in proc_name:
                        try:
                            proc.terminate()
                            killed += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                        break

            if killed > 0:
                return {"success": True, "message": f"Closed {killed} instance(s) of {app_name}"}

            # Fallback: use taskkill via cmd for stubborn processes
            for term in search_terms:
                exe_name = term if term.endswith('.exe') else f"{term}.exe"
                result = subprocess.run(
                    f'taskkill /IM "{exe_name}" /F',
                    shell=True, capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    return {"success": True, "message": f"Force-closed {app_name}"}

            return {"success": False, "error": f"No running process found for: {app_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_system_info() -> dict:
        """Get system status information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')

            # Get running processes count
            process_count = len(list(psutil.process_iter()))

            # Get top processes by memory
            processes = []
            for proc in sorted(psutil.process_iter(['name', 'memory_percent']),
                               key=lambda x: x.info['memory_percent'] or 0,
                               reverse=True)[:5]:
                processes.append(f"  - {proc.info['name']}: {proc.info['memory_percent']:.1f}%")

            info = f"""**System Status**

**CPU:** {cpu_percent}%
**Memory:** {memory.percent}% ({memory.used // (1024**3)}/{memory.total // (1024**3)} GB)
**Disk (C:):** {disk.percent}% ({disk.used // (1024**3)}/{disk.total // (1024**3)} GB)
**Processes:** {process_count} running

**Top Memory Usage:**
{chr(10).join(processes)}"""

            return {"success": True, "info": info}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def list_processes(filter_name: Optional[str] = None) -> dict:
        """List running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                if filter_name and filter_name.lower() not in proc.info['name'].lower():
                    continue
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "memory": f"{proc.info['memory_percent']:.1f}%"
                })

            # Sort by memory and limit
            processes = sorted(processes, key=lambda x: float(x['memory'].rstrip('%')), reverse=True)[:20]

            output = "**Running Processes:**\n"
            for p in processes:
                output += f"  [{p['pid']}] {p['name']} - {p['memory']}\n"

            return {"success": True, "output": output, "count": len(processes)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def shutdown(action: str = "shutdown", delay: int = 60) -> dict:
        """Shutdown, restart, or sleep the PC"""
        try:
            commands = {
                "shutdown": f"shutdown /s /t {delay}",
                "restart": f"shutdown /r /t {delay}",
                "cancel": "shutdown /a",
                "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                "lock": "rundll32.exe user32.dll,LockWorkStation"
            }

            if action not in commands:
                return {"success": False, "error": f"Unknown action: {action}. Use: {list(commands.keys())}"}

            os.system(commands[action])
            return {"success": True, "message": f"System {action} initiated" + (f" in {delay}s" if action in ["shutdown", "restart"] else "")}
        except Exception as e:
            return {"success": False, "error": str(e)}
