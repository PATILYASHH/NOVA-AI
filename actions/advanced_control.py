"""
NOVA - Advanced Control Module
Window management, volume, network, downloads, and more
"""

import os
import subprocess
import socket
import urllib.request
import logging
import ctypes
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class AdvancedControl:
    """Advanced system control operations"""

    # ============ VOLUME CONTROL ============

    @staticmethod
    def set_volume(level: int) -> dict:
        """Set system volume (0-100)"""
        try:
            # Use PowerShell to set volume
            level = max(0, min(100, level))
            ps_command = f'''
            $obj = New-Object -ComObject WScript.Shell
            1..50 | ForEach-Object {{ $obj.SendKeys([char]174) }}
            1..{level // 2} | ForEach-Object {{ $obj.SendKeys([char]175) }}
            '''
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
            return {"success": True, "message": f"Volume set to approximately {level}%"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def mute_volume() -> dict:
        """Toggle mute"""
        try:
            ps_command = '(New-Object -ComObject WScript.Shell).SendKeys([char]173)'
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
            return {"success": True, "message": "Volume mute toggled"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ NETWORK INFO ============

    @staticmethod
    def get_network_info() -> dict:
        """Get network information"""
        try:
            # Get hostname and IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            # Get public IP
            try:
                public_ip = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode('utf8')
            except:
                public_ip = "Could not fetch"

            # Get network interfaces
            interfaces = []
            if PSUTIL_AVAILABLE:
                for name, addrs in psutil.net_if_addrs().items():
                    for addr in addrs:
                        if addr.family == socket.AF_INET:
                            interfaces.append(f"  - {name}: {addr.address}")

            info = f"""**Network Information**

**Hostname:** {hostname}
**Local IP:** {local_ip}
**Public IP:** {public_ip}

**Interfaces:**
{chr(10).join(interfaces) if interfaces else 'N/A'}"""

            return {"success": True, "info": info}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_wifi_info() -> dict:
        """Get WiFi connection info"""
        try:
            result = subprocess.run(
                'netsh wlan show interfaces',
                shell=True,
                capture_output=True,
                text=True
            )
            return {"success": True, "info": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def list_wifi_networks() -> dict:
        """List available WiFi networks"""
        try:
            result = subprocess.run(
                'netsh wlan show networks mode=Bssid',
                shell=True,
                capture_output=True,
                text=True
            )
            return {"success": True, "networks": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ DOWNLOAD ============

    @staticmethod
    def download_file(url: str, save_path: Optional[str] = None) -> dict:
        """Download file from URL"""
        try:
            if not save_path:
                filename = url.split('/')[-1].split('?')[0] or "download"
                save_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            urllib.request.urlretrieve(url, save_path)

            size = os.path.getsize(save_path)
            return {
                "success": True,
                "message": f"Downloaded to {save_path}",
                "path": save_path,
                "size": f"{size / 1024:.1f} KB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ BATTERY ============

    @staticmethod
    def get_battery_status() -> dict:
        """Get battery status"""
        try:
            if not PSUTIL_AVAILABLE:
                return {"success": False, "error": "psutil not available"}

            battery = psutil.sensors_battery()
            if battery is None:
                return {"success": True, "info": "No battery detected (desktop PC)"}

            status = "Charging" if battery.power_plugged else "On Battery"
            time_left = ""
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                hours = battery.secsleft // 3600
                minutes = (battery.secsleft % 3600) // 60
                time_left = f"\n**Time Remaining:** {hours}h {minutes}m"

            info = f"""**Battery Status**

**Level:** {battery.percent}%
**Status:** {status}{time_left}"""

            return {"success": True, "info": info}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ INSTALLED PROGRAMS ============

    @staticmethod
    def list_installed_programs(search: Optional[str] = None) -> dict:
        """List installed programs"""
        try:
            ps_command = '''
            Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*,
            HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
            Select-Object DisplayName, DisplayVersion |
            Where-Object { $_.DisplayName -ne $null } |
            Sort-Object DisplayName |
            Format-Table -AutoSize
            '''
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )

            output = result.stdout
            if search:
                lines = output.split('\n')
                filtered = [l for l in lines if search.lower() in l.lower()]
                output = '\n'.join(filtered) if filtered else f"No programs matching '{search}'"

            if len(output) > 4000:
                output = output[:4000] + "\n... [truncated]"

            return {"success": True, "programs": output}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ STARTUP PROGRAMS ============

    @staticmethod
    def list_startup_programs() -> dict:
        """List startup programs"""
        try:
            ps_command = '''
            Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | Format-Table -AutoSize
            '''
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )
            return {"success": True, "programs": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ SERVICES ============

    @staticmethod
    def list_services(filter_name: Optional[str] = None, running_only: bool = False) -> dict:
        """List Windows services"""
        try:
            ps_command = 'Get-Service'
            if running_only:
                ps_command += ' | Where-Object {$_.Status -eq "Running"}'
            if filter_name:
                ps_command += f' | Where-Object {{$_.Name -like "*{filter_name}*" -or $_.DisplayName -like "*{filter_name}*"}}'
            ps_command += ' | Select-Object Name, DisplayName, Status | Format-Table -AutoSize'

            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )

            output = result.stdout
            if len(output) > 4000:
                output = output[:4000] + "\n... [truncated]"

            return {"success": True, "services": output}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def control_service(service_name: str, action: str) -> dict:
        """Start/stop/restart a service"""
        try:
            valid_actions = ["start", "stop", "restart"]
            if action.lower() not in valid_actions:
                return {"success": False, "error": f"Invalid action. Use: {valid_actions}"}

            if action.lower() == "restart":
                ps_command = f'Restart-Service -Name "{service_name}" -Force'
            elif action.lower() == "start":
                ps_command = f'Start-Service -Name "{service_name}"'
            else:
                ps_command = f'Stop-Service -Name "{service_name}" -Force'

            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {"success": True, "message": f"Service {service_name} {action}ed successfully"}
            else:
                return {"success": False, "error": result.stderr or "Failed to control service"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ WINDOW MANAGEMENT ============

    @staticmethod
    def list_windows() -> dict:
        """List open windows"""
        try:
            ps_command = '''
            Get-Process | Where-Object {$_.MainWindowTitle -ne ""} |
            Select-Object Id, ProcessName, MainWindowTitle |
            Format-Table -AutoSize
            '''
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )
            return {"success": True, "windows": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def minimize_all_windows() -> dict:
        """Minimize all windows (show desktop)"""
        try:
            ps_command = '(New-Object -ComObject Shell.Application).MinimizeAll()'
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
            return {"success": True, "message": "All windows minimized"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def restore_all_windows() -> dict:
        """Restore all windows"""
        try:
            ps_command = '(New-Object -ComObject Shell.Application).UndoMinimizeAll()'
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
            return {"success": True, "message": "All windows restored"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ ENVIRONMENT VARIABLES ============

    @staticmethod
    def get_env_variable(name: str) -> dict:
        """Get environment variable"""
        try:
            value = os.environ.get(name)
            if value:
                return {"success": True, "name": name, "value": value}
            else:
                return {"success": False, "error": f"Variable '{name}' not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def list_env_variables() -> dict:
        """List all environment variables"""
        try:
            env_list = [f"{k}={v}" for k, v in sorted(os.environ.items())]
            output = "\n".join(env_list)
            if len(output) > 4000:
                output = output[:4000] + "\n... [truncated]"
            return {"success": True, "variables": output}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ DISK INFO ============

    @staticmethod
    def get_disk_info() -> dict:
        """Get detailed disk information"""
        try:
            if not PSUTIL_AVAILABLE:
                return {"success": False, "error": "psutil not available"}

            info = "**Disk Information**\n\n"
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    info += f"**{partition.device}** ({partition.mountpoint})\n"
                    info += f"  Type: {partition.fstype}\n"
                    info += f"  Total: {usage.total // (1024**3)} GB\n"
                    info += f"  Used: {usage.used // (1024**3)} GB ({usage.percent}%)\n"
                    info += f"  Free: {usage.free // (1024**3)} GB\n\n"
                except:
                    continue

            return {"success": True, "info": info}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ SCHEDULED TASKS ============

    @staticmethod
    def list_scheduled_tasks(folder: str = "\\") -> dict:
        """List scheduled tasks"""
        try:
            ps_command = f'Get-ScheduledTask -TaskPath "{folder}*" | Select-Object TaskName, State | Format-Table -AutoSize'
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )

            output = result.stdout
            if len(output) > 4000:
                output = output[:4000] + "\n... [truncated]"

            return {"success": True, "tasks": output}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ============ QUICK ACTIONS ============

    @staticmethod
    def empty_recycle_bin() -> dict:
        """Empty the recycle bin"""
        try:
            ps_command = 'Clear-RecycleBin -Force -ErrorAction SilentlyContinue'
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
            return {"success": True, "message": "Recycle bin emptied"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def clear_temp_files() -> dict:
        """Clear temporary files"""
        try:
            temp_paths = [
                os.environ.get('TEMP', ''),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Temp')
            ]

            deleted = 0
            for temp_path in temp_paths:
                if temp_path and os.path.exists(temp_path):
                    for item in os.listdir(temp_path):
                        try:
                            item_path = os.path.join(temp_path, item)
                            if os.path.isfile(item_path):
                                os.unlink(item_path)
                                deleted += 1
                        except:
                            continue

            return {"success": True, "message": f"Cleared {deleted} temp files"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def flush_dns() -> dict:
        """Flush DNS cache"""
        try:
            result = subprocess.run(
                'ipconfig /flushdns',
                shell=True,
                capture_output=True,
                text=True
            )
            return {"success": True, "message": "DNS cache flushed", "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
