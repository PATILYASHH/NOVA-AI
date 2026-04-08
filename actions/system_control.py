"""
NOVA - System Control Module
Handles system commands, apps, and PC control
"""

import os
import subprocess
import logging
import psutil
from typing import Optional

logger = logging.getLogger(__name__)


class SystemControl:
    """Handle system-level operations"""

    # Common applications and their paths/commands
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
    def open_app(cls, app_name: str) -> dict:
        """Open an application"""
        try:
            app_lower = app_name.lower()

            # Check if it's a known app
            if app_lower in cls.APPS:
                command = cls.APPS[app_lower]
            else:
                command = app_name

            # Use start command for Windows
            # Only quote if command contains spaces (quoting breaks PATH lookup for short names)
            if " " in command:
                cmd_str = f'start "" "{command}"'
            else:
                cmd_str = f'start "" {command}'

            subprocess.Popen(
                cmd_str,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return {"success": True, "message": f"Opened {app_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def close_app(app_name: str) -> dict:
        """Close an application by name"""
        try:
            # Find and terminate processes matching the name
            killed = 0
            for proc in psutil.process_iter(['name', 'pid']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    killed += 1

            if killed > 0:
                return {"success": True, "message": f"Closed {killed} instance(s) of {app_name}"}
            else:
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
