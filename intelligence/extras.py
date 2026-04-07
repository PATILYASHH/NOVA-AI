"""
NOVA - Extra Features Module
Command Aliases, Clipboard History, Startup Scripts,
Project Auto-Detection, Daily Auto-Report, File Watcher,
Resource History, Process Auto-Kill, Error Recovery,
Multi-File Batch Operations, Natural Language Router
"""

import os
import json
import logging
import threading
import time
import psutil
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "intelligence", "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ============ COMMAND ALIASES ============

class CommandAliases:
    """User-defined command shortcuts"""

    def __init__(self):
        self.aliases_file = os.path.join(DATA_DIR, "aliases.json")
        self.aliases = self._load()

    def _load(self) -> Dict:
        try:
            if os.path.exists(self.aliases_file):
                with open(self.aliases_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save(self):
        try:
            with open(self.aliases_file, 'w', encoding='utf-8') as f:
                json.dump(self.aliases, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save aliases: {e}")

    def add(self, alias: str, command: str) -> str:
        self.aliases[alias.lower()] = command
        self._save()
        return f"Alias added: `{alias}` -> `{command}`"

    def remove(self, alias: str) -> str:
        if alias.lower() in self.aliases:
            del self.aliases[alias.lower()]
            self._save()
            return f"Alias '{alias}' removed."
        return f"Alias '{alias}' not found."

    def resolve(self, text: str) -> Optional[str]:
        """Check if text starts with an alias, return resolved command"""
        parts = text.strip().split(maxsplit=1)
        if parts and parts[0].lower() in self.aliases:
            resolved = self.aliases[parts[0].lower()]
            if len(parts) > 1:
                resolved += " " + parts[1]
            return resolved
        return None

    def list_all(self) -> str:
        if not self.aliases:
            return "No aliases defined. Use /alias <name> = <command>"
        text = "**Command Aliases:**\n\n"
        for alias, cmd in sorted(self.aliases.items()):
            text += f"  `{alias}` -> `{cmd}`\n"
        return text


# ============ CLIPBOARD HISTORY ============

class ClipboardHistory:
    """Keep last N clipboard entries"""

    def __init__(self, max_entries: int = 20):
        self.max_entries = max_entries
        self.history_file = os.path.join(DATA_DIR, "clipboard_history.json")
        self.history = self._load()

    def _load(self) -> List[Dict]:
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history[-self.max_entries:], f, indent=2, default=str)
        except Exception:
            pass

    def add(self, content: str, action: str = "copy"):
        self.history.append({
            "content": content[:500],
            "action": action,
            "timestamp": datetime.now().isoformat(),
        })
        self.history = self.history[-self.max_entries:]
        self._save()

    def get_recent(self, count: int = 10) -> str:
        if not self.history:
            return "Clipboard history is empty."
        text = "**Clipboard History:**\n\n"
        for i, entry in enumerate(reversed(self.history[-count:]), 1):
            preview = entry["content"][:60].replace("\n", " ")
            text += f"{i}. `{preview}`\n   {entry['timestamp'][:19]}\n\n"
        return text

    def get_entry(self, index: int) -> Optional[str]:
        """Get entry by index (1-based, newest first)"""
        if 1 <= index <= len(self.history):
            return self.history[-index]["content"]
        return None


# ============ STARTUP SCRIPTS ============

class StartupScripts:
    """Auto-run commands when NOVA starts"""

    def __init__(self):
        self.scripts_file = os.path.join(DATA_DIR, "startup_scripts.json")
        self.scripts = self._load()

    def _load(self) -> List[Dict]:
        try:
            if os.path.exists(self.scripts_file):
                with open(self.scripts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save(self):
        try:
            with open(self.scripts_file, 'w', encoding='utf-8') as f:
                json.dump(self.scripts, f, indent=2)
        except Exception:
            pass

    def add(self, name: str, command: str, delay: int = 0) -> str:
        self.scripts.append({
            "name": name,
            "command": command,
            "delay": delay,
            "enabled": True,
            "added": datetime.now().isoformat(),
        })
        self._save()
        return f"Startup script '{name}' added: `{command}`"

    def remove(self, name: str) -> str:
        self.scripts = [s for s in self.scripts if s["name"] != name]
        self._save()
        return f"Startup script '{name}' removed."

    def list_all(self) -> str:
        if not self.scripts:
            return "No startup scripts. Use /addstartup <name> <command>"
        text = "**Startup Scripts:**\n\n"
        for s in self.scripts:
            status = "ON" if s.get("enabled", True) else "OFF"
            text += f"[{status}] **{s['name']}**: `{s['command']}`\n"
            if s.get("delay"):
                text += f"  Delay: {s['delay']}s\n"
        return text

    def get_enabled(self) -> List[Dict]:
        return [s for s in self.scripts if s.get("enabled", True)]


# ============ PROJECT AUTO-DETECTION ============

class ProjectAutoDetect:
    """Auto-detect and set active project from git repos"""

    def detect_from_path(self, path: str) -> Optional[Dict]:
        """Detect project from a file/directory path"""
        check_path = path
        for _ in range(10):  # Walk up max 10 levels
            git_dir = os.path.join(check_path, ".git")
            if os.path.exists(git_dir):
                return {
                    "name": os.path.basename(check_path),
                    "path": check_path,
                    "detected_from": path,
                }
            parent = os.path.dirname(check_path)
            if parent == check_path:
                break
            check_path = parent
        return None

    def detect_from_command(self, command: str) -> Optional[Dict]:
        """Detect project from a command that references a path"""
        # Extract paths from command
        import re
        paths = re.findall(r'[A-Za-z]:\\[^\s"]+|/[^\s"]+', command)
        for path in paths:
            if os.path.exists(path):
                result = self.detect_from_path(path)
                if result:
                    return result
        return None


# ============ DAILY AUTO-REPORT ============

class DailyAutoReport:
    """Auto-send end-of-day report"""

    def __init__(self, alert_callback=None):
        self.alert_callback = alert_callback
        self.running = False
        self.thread = None
        self.report_hour = 18  # 6 PM
        self.report_minute = 0
        self.sent_today = False

    def start(self):
        if self.running:
            return
        self.running = True

        def _loop():
            while self.running:
                now = datetime.now()
                if (now.hour == self.report_hour and
                    now.minute == self.report_minute and
                    not self.sent_today):
                    self._send_report()
                    self.sent_today = True

                # Reset flag at midnight
                if now.hour == 0 and now.minute == 0:
                    self.sent_today = False

                time.sleep(30)

        self.thread = threading.Thread(target=_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _send_report(self):
        if self.alert_callback:
            try:
                # Generate proper daily report
                from core.personality import Personality
                from core.memory_system import NovaMemorySystem
                from core.self_reflection import SelfReflectionSystem

                mem = NovaMemorySystem()
                reflection = SelfReflectionSystem()
                p = Personality()

                # Gather stats
                stats = mem.ram.get_daily_summary()
                perf = reflection.end_of_day_review()
                stats["performance_score"] = perf.get("score", "N/A")
                stats["strengths"] = perf.get("strengths", [])
                stats["improvements"] = perf.get("improvements", [])

                # Claude generates the report
                report = p.generate_daily_report(stats)

                # Write diary
                p.write_diary_entry({"event": "end_of_day", "stats": stats})

                self.alert_callback("daily_report", report or f"Day done. {stats.get('total_commands', 0)} commands, score: {perf.get('score', '?')}/10")

            except Exception as e:
                self.alert_callback("daily_report", f"End of day. Couldn't generate full report: {str(e)[:50]}")

    def set_time(self, hour: int, minute: int = 0):
        self.report_hour = hour
        self.report_minute = minute


# ============ SMART FILE WATCHER ============

class FileWatcher:
    """Monitor folders for changes"""

    def __init__(self, alert_callback=None):
        self.alert_callback = alert_callback
        self.watch_paths = {}  # path -> {last_scan, files}
        self.running = False
        self.thread = None
        self.config_file = os.path.join(DATA_DIR, "file_watcher.json")
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for path, config in data.items():
                        self.watch_paths[path] = {
                            "last_scan": {},
                            "patterns": config.get("patterns", ["*"]),
                            "name": config.get("name", os.path.basename(path)),
                        }
        except Exception:
            pass

    def _save(self):
        try:
            data = {}
            for path, info in self.watch_paths.items():
                data[path] = {
                    "patterns": info.get("patterns", ["*"]),
                    "name": info.get("name", ""),
                }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def add_watch(self, path: str, name: str = "", patterns: List[str] = None) -> str:
        if not os.path.exists(path):
            return f"Path not found: {path}"

        self.watch_paths[path] = {
            "last_scan": self._scan_directory(path),
            "patterns": patterns or ["*"],
            "name": name or os.path.basename(path),
        }
        self._save()
        return f"Now watching: {path}"

    def remove_watch(self, path: str) -> str:
        if path in self.watch_paths:
            del self.watch_paths[path]
            self._save()
            return f"Stopped watching: {path}"
        return f"Not watching: {path}"

    def _scan_directory(self, path: str) -> Dict:
        """Scan directory and return file state"""
        state = {}
        try:
            for item in Path(path).iterdir():
                try:
                    stat = item.stat()
                    state[str(item)] = {
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                    }
                except Exception:
                    pass
        except Exception:
            pass
        return state

    def check_changes(self) -> List[Dict]:
        """Check all watched paths for changes"""
        all_changes = []

        for path, info in self.watch_paths.items():
            if not os.path.exists(path):
                continue

            current = self._scan_directory(path)
            previous = info.get("last_scan", {})
            changes = []

            # New files
            for f in set(current.keys()) - set(previous.keys()):
                changes.append({"type": "created", "file": f})

            # Deleted files
            for f in set(previous.keys()) - set(current.keys()):
                changes.append({"type": "deleted", "file": f})

            # Modified files
            for f in set(current.keys()) & set(previous.keys()):
                if current[f]["modified"] != previous[f]["modified"]:
                    changes.append({"type": "modified", "file": f})

            if changes:
                all_changes.append({
                    "path": path,
                    "name": info.get("name", ""),
                    "changes": changes,
                })

            info["last_scan"] = current

        return all_changes

    def start(self, interval: int = 60):
        if self.running:
            return
        self.running = True

        def _loop():
            while self.running:
                try:
                    changes = self.check_changes()
                    for change_group in changes:
                        if self.alert_callback:
                            msg = f"Changes in {change_group['name']}:\n"
                            for c in change_group['changes'][:5]:
                                msg += f"  [{c['type']}] {os.path.basename(c['file'])}\n"
                            self.alert_callback("file_change", msg)
                except Exception as e:
                    logger.debug(f"File watcher error: {e}")
                time.sleep(interval)

        self.thread = threading.Thread(target=_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def list_watches(self) -> str:
        if not self.watch_paths:
            return "No folders being watched. Use /watch <path>"
        text = "**Watched Folders:**\n\n"
        for path, info in self.watch_paths.items():
            text += f"**{info.get('name', 'unknown')}**\n"
            text += f"  Path: `{path}`\n"
            text += f"  Files: {len(info.get('last_scan', {}))}\n\n"
        return text


# ============ RESOURCE HISTORY & GRAPHS ============

class ResourceHistory:
    """Track CPU/memory/disk over time, generate text graphs"""

    def __init__(self):
        self.history_file = os.path.join(DATA_DIR, "resource_history.json")
        self.history = self._load()
        self.running = False
        self.thread = None

    def _load(self) -> List[Dict]:
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save(self):
        try:
            # Keep last 1440 entries (24 hours at 1-min intervals)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history[-1440:], f, default=str)
        except Exception:
            pass

    def record(self):
        """Record current resource usage"""
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "cpu": psutil.cpu_percent(interval=0),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('C:').percent,
            }
            try:
                battery = psutil.sensors_battery()
                if battery:
                    entry["battery"] = battery.percent
            except Exception:
                pass
            self.history.append(entry)
            self.history = self.history[-1440:]
        except Exception:
            pass

    def start(self, interval: int = 60):
        if self.running:
            return
        self.running = True

        def _loop():
            while self.running:
                self.record()
                if len(self.history) % 10 == 0:
                    self._save()
                time.sleep(interval)

        self.thread = threading.Thread(target=_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self._save()

    def get_graph(self, metric: str = "cpu", hours: int = 1) -> str:
        """Generate text-based graph"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        data = [e for e in self.history if e["timestamp"] >= cutoff]

        if not data:
            return f"No {metric} data available for the last {hours} hour(s)."

        values = [e.get(metric, 0) for e in data]

        # Downsample to ~30 points
        step = max(1, len(values) // 30)
        sampled = values[::step]

        # Build text graph
        height = 8
        max_val = max(sampled) if sampled else 100
        min_val = min(sampled) if sampled else 0
        val_range = max(max_val - min_val, 1)

        text = f"**{metric.upper()} - Last {hours}h** (min: {min_val:.0f}%, max: {max_val:.0f}%)\n```\n"

        for row in range(height, -1, -1):
            threshold = min_val + (row / height) * val_range
            label = f"{threshold:5.0f}% |"
            line = ""
            for val in sampled:
                if val >= threshold:
                    line += "#"
                else:
                    line += " "
            text += label + line + "\n"

        text += "       " + "-" * len(sampled) + "\n"
        text += f"       {'Now':>{len(sampled)}}\n"
        text += "```\n"
        text += f"Current: {values[-1]:.0f}% | Avg: {sum(values)/len(values):.0f}%\n"

        return text


# ============ PROCESS AUTO-KILL ============

class ProcessAutoKill:
    """Auto-kill processes exceeding memory threshold"""

    def __init__(self, alert_callback=None):
        self.alert_callback = alert_callback
        self.config_file = os.path.join(DATA_DIR, "autokill_config.json")
        self.config = self._load()
        self.running = False
        self.thread = None
        self.kill_log = []

    def _load(self) -> Dict:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "enabled": False,
            "memory_threshold_percent": 40,
            "protected": ["explorer.exe", "csrss.exe", "svchost.exe", "dwm.exe",
                          "System", "smss.exe", "lsass.exe", "winlogon.exe",
                          "python.exe", "nova"],
            "whitelist": [],
        }

    def _save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def enable(self, threshold: int = 40) -> str:
        self.config["enabled"] = True
        self.config["memory_threshold_percent"] = threshold
        self._save()
        return f"Process auto-kill enabled. Threshold: {threshold}% memory per process."

    def disable(self) -> str:
        self.config["enabled"] = False
        self._save()
        return "Process auto-kill disabled."

    def add_protected(self, name: str) -> str:
        if name not in self.config["protected"]:
            self.config["protected"].append(name)
            self._save()
        return f"Protected: {name}"

    def check_and_kill(self) -> List[Dict]:
        """Check for processes exceeding threshold"""
        if not self.config.get("enabled"):
            return []

        killed = []
        threshold = self.config.get("memory_threshold_percent", 40)

        for proc in psutil.process_iter(['name', 'pid', 'memory_percent']):
            try:
                mem = proc.info.get('memory_percent', 0)
                name = proc.info.get('name', '')

                if mem and mem > threshold:
                    # Check if protected
                    if any(p.lower() in name.lower() for p in self.config["protected"]):
                        continue

                    proc.kill()
                    entry = {
                        "name": name,
                        "pid": proc.info['pid'],
                        "memory_percent": mem,
                        "timestamp": datetime.now().isoformat(),
                    }
                    killed.append(entry)
                    self.kill_log.append(entry)

                    if self.alert_callback:
                        self.alert_callback("process_killed",
                            f"Auto-killed {name} (PID: {proc.info['pid']}) using {mem:.1f}% memory")

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return killed

    def start(self, interval: int = 120):
        if self.running:
            return
        self.running = True

        def _loop():
            while self.running:
                try:
                    self.check_and_kill()
                except Exception as e:
                    logger.debug(f"Auto-kill error: {e}")
                time.sleep(interval)

        self.thread = threading.Thread(target=_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def get_status(self) -> str:
        text = f"**Process Auto-Kill**\n"
        text += f"Status: {'Enabled' if self.config.get('enabled') else 'Disabled'}\n"
        text += f"Threshold: {self.config.get('memory_threshold_percent', 40)}% memory\n"
        text += f"Protected: {len(self.config.get('protected', []))} processes\n"
        text += f"Killed today: {len(self.kill_log)}\n"
        return text


# ============ ERROR RECOVERY ============

class ErrorRecovery:
    """Auto-try alternatives when commands fail"""

    RECOVERY_MAP = {
        "not_found": {
            "alternatives": [
                ("Try with full path", lambda cmd: cmd),
                ("Search for file first", lambda cmd: f"find {cmd.split()[-1]} ." if cmd.split() else cmd),
            ]
        },
        "permission_denied": {
            "alternatives": [
                ("Run as admin", lambda cmd: f"powershell Start-Process cmd -ArgumentList '/c {cmd}' -Verb RunAs"),
            ]
        },
        "timeout": {
            "alternatives": [
                ("Retry with longer timeout", lambda cmd: cmd),
            ]
        },
    }

    def __init__(self, learning_loop=None):
        self.learning = learning_loop

    def suggest_recovery(self, command: str, error: str) -> List[Dict]:
        """Suggest recovery actions for a failed command"""
        suggestions = []
        error_lower = error.lower()

        # Check known patterns
        for error_type, recovery in self.RECOVERY_MAP.items():
            if error_type.replace("_", " ") in error_lower or error_type in error_lower:
                for desc, transform in recovery["alternatives"]:
                    suggestions.append({
                        "description": desc,
                        "command": transform(command),
                        "error_type": error_type,
                    })

        # Check learning loop for past solutions
        if self.learning:
            alt = self.learning.strategy.get_alternative_command(command)
            if alt:
                suggestions.append({
                    "description": "Previously successful alternative",
                    "command": alt,
                    "error_type": "learned",
                })

        return suggestions


# ============ MULTI-FILE BATCH OPS ============

class BatchFileOps:
    """Batch file operations"""

    @staticmethod
    def batch_rename(directory: str, pattern: str, replacement: str, dry_run: bool = True) -> Dict:
        """Rename files matching pattern"""
        import re
        results = {"renamed": [], "errors": [], "dry_run": dry_run}

        if not os.path.exists(directory):
            return {"error": f"Directory not found: {directory}"}

        for item in os.listdir(directory):
            if re.search(pattern, item):
                new_name = re.sub(pattern, replacement, item)
                if new_name != item:
                    old_path = os.path.join(directory, item)
                    new_path = os.path.join(directory, new_name)
                    if dry_run:
                        results["renamed"].append(f"{item} -> {new_name}")
                    else:
                        try:
                            os.rename(old_path, new_path)
                            results["renamed"].append(f"{item} -> {new_name}")
                        except Exception as e:
                            results["errors"].append(f"{item}: {e}")

        return results

    @staticmethod
    def batch_delete(directory: str, pattern: str, dry_run: bool = True) -> Dict:
        """Delete files matching pattern"""
        import re
        results = {"deleted": [], "errors": [], "dry_run": dry_run}

        if not os.path.exists(directory):
            return {"error": f"Directory not found: {directory}"}

        for item in os.listdir(directory):
            if re.search(pattern, item):
                file_path = os.path.join(directory, item)
                if os.path.isfile(file_path):
                    if dry_run:
                        results["deleted"].append(item)
                    else:
                        try:
                            os.remove(file_path)
                            results["deleted"].append(item)
                        except Exception as e:
                            results["errors"].append(f"{item}: {e}")

        return results

    @staticmethod
    def find_large_files(directory: str, min_size_mb: int = 100, limit: int = 20) -> List[Dict]:
        """Find large files"""
        large_files = []
        min_bytes = min_size_mb * 1024 * 1024

        try:
            for root, dirs, files in os.walk(directory):
                # Skip common dirs
                dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', '.venv'}]
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        size = os.path.getsize(fp)
                        if size >= min_bytes:
                            large_files.append({
                                "path": fp,
                                "size_mb": round(size / (1024 * 1024), 1),
                            })
                    except Exception:
                        pass
        except Exception:
            pass

        large_files.sort(key=lambda x: x["size_mb"], reverse=True)
        return large_files[:limit]


# ============ NATURAL LANGUAGE ROUTER ============

class NLCommandRouter:
    """Route natural language to actual command execution"""

    # Maps intent+entities to executable commands
    ROUTE_MAP = {
        ("file_operation", "file_read"): "/cat {file_path}",
        ("file_operation", "search"): "/find {target}",
        ("file_operation", "file_delete"): "/delete {file_path}",
        ("app_control", "launch"): "/open {target}",
        ("app_control", "terminate"): "/close {target}",
        ("system_info", None): "/status",
        ("screenshot", None): "/screenshot",
        ("clipboard", None): "/clipboard",
        ("git_operation", None): "/git . {git_operation}",
        ("network", None): "/network",
        ("browser", None): "/browse {url}",
    }

    def route(self, intent: str, action: Dict, entities: Dict, target: str) -> Optional[str]:
        """Convert NLP result to an executable command"""
        action_category = action.get("category") if action else None

        # Try exact match
        cmd_template = self.ROUTE_MAP.get((intent, action_category))
        if not cmd_template:
            cmd_template = self.ROUTE_MAP.get((intent, None))

        if not cmd_template:
            return None

        # Fill template with entities
        try:
            fill = {
                "file_path": (entities.get("file_path", [""])[0] if entities.get("file_path") else target or ""),
                "target": target or "",
                "git_operation": (entities.get("git_operation", ["status"])[0] if entities.get("git_operation") else "status"),
                "url": (entities.get("url", [""])[0] if entities.get("url") else target or ""),
            }
            return cmd_template.format(**fill).strip()
        except Exception:
            return None
