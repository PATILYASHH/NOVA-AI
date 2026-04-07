"""
NOVA - Command Logger
Automatic logging of all commands and activities
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMANDS_LOG_DIR = os.path.join(BASE_DIR, "logs", "commands")


class CommandLogger:
    """
    Automatic command logging system
    Tracks every command executed through NOVA
    """

    def __init__(self, memory_system=None):
        self.memory = memory_system
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = os.path.join(COMMANDS_LOG_DIR, f"{self.today}.json")
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Ensure log file exists"""
        os.makedirs(COMMANDS_LOG_DIR, exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump({"date": self.today, "commands": []}, f)

    def _update_date(self):
        """Update date if day changed"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self.today:
            self.today = current_date
            self.log_file = os.path.join(COMMANDS_LOG_DIR, f"{self.today}.json")
            self._ensure_log_file()

    def log(self, command: str, result: str, success: bool,
            category: str = "general", user_id: int = None,
            project: str = None, execution_time: float = None):
        """Log a command execution"""
        self._update_date()

        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result[:2000] if result else "",
            "success": success,
            "category": category,
            "user_id": user_id,
            "project": project,
            "execution_time_ms": execution_time
        }

        # Append to daily log
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data["commands"].append(entry)

            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to log command: {e}")

        # Also log to memory system if available
        if self.memory:
            self.memory.log_command(command, result, success, category, project)

    def get_today_commands(self) -> list:
        """Get all commands from today"""
        self._update_date()
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("commands", [])
        except:
            return []

    def get_command_count(self) -> int:
        """Get today's command count"""
        return len(self.get_today_commands())

    def get_commands_by_category(self, category: str) -> list:
        """Get commands by category"""
        commands = self.get_today_commands()
        return [c for c in commands if c.get("category") == category]

    def get_failed_commands(self) -> list:
        """Get failed commands"""
        commands = self.get_today_commands()
        return [c for c in commands if not c.get("success")]


def track_command(category: str = "general"):
    """
    Decorator to automatically track command execution
    Use on telegram command handlers
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import time
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000

                # Log success
                # Note: Actual logging done in the handler with access to command_logger

                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                logger.error(f"Command {func.__name__} failed: {e}")
                raise

        return wrapper
    return decorator


class ActivityTracker:
    """
    Tracks all PC activity through NOVA
    """

    def __init__(self, memory_system=None):
        self.memory = memory_system
        self.activity_file = os.path.join(BASE_DIR, "logs", "activity.json")
        self._ensure_file()

    def _ensure_file(self):
        """Ensure activity file exists"""
        if not os.path.exists(self.activity_file):
            with open(self.activity_file, 'w', encoding='utf-8') as f:
                json.dump({"activities": []}, f)

    def track(self, activity_type: str, description: str, metadata: dict = None):
        """Track an activity"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "description": description,
            "metadata": metadata or {}
        }

        try:
            with open(self.activity_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data["activities"].append(entry)

            # Keep only last 1000 activities
            data["activities"] = data["activities"][-1000:]

            with open(self.activity_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to track activity: {e}")

    def get_recent(self, count: int = 50) -> list:
        """Get recent activities"""
        try:
            with open(self.activity_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("activities", [])[-count:]
        except:
            return []
