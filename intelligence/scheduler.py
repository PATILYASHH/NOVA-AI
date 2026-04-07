"""
NOVA - Task Scheduler
Schedule commands and tasks to run at specific times
"""

import os
import json
import logging
import threading
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
from enum import Enum

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULES_DIR = os.path.join(BASE_DIR, "schedules")
SCHEDULES_FILE = os.path.join(SCHEDULES_DIR, "tasks.json")


class ScheduleType(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    INTERVAL = "interval"  # Every X minutes
    CRON = "cron"


class TaskScheduler:
    """
    Schedule and run tasks automatically
    """

    def __init__(self, task_callback: Callable[[str, str], None] = None):
        self.task_callback = task_callback  # Callback when task runs
        self.tasks = {}
        self.running = False
        self.scheduler_thread = None
        self.load_tasks()

    def load_tasks(self):
        """Load scheduled tasks"""
        try:
            os.makedirs(SCHEDULES_DIR, exist_ok=True)
            if os.path.exists(SCHEDULES_FILE):
                with open(SCHEDULES_FILE, 'r') as f:
                    self.tasks = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schedules: {e}")
            self.tasks = {}

    def save_tasks(self):
        """Save scheduled tasks"""
        try:
            with open(SCHEDULES_FILE, 'w') as f:
                json.dump(self.tasks, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save schedules: {e}")

    def add_task(self, name: str, command: str, schedule_type: str,
                 schedule_time: str = None, interval_minutes: int = None,
                 days: List[str] = None, enabled: bool = True) -> Dict:
        """
        Add a scheduled task

        Args:
            name: Task name (unique identifier)
            command: Command to execute
            schedule_type: once, daily, weekly, interval
            schedule_time: Time in HH:MM format (for once, daily, weekly)
            interval_minutes: Minutes between runs (for interval type)
            days: List of days for weekly (mon, tue, wed, thu, fri, sat, sun)
            enabled: Whether task is active
        """
        task_id = name.lower().replace(" ", "_")

        task = {
            "id": task_id,
            "name": name,
            "command": command,
            "type": schedule_type,
            "time": schedule_time,
            "interval_minutes": interval_minutes,
            "days": days or [],
            "enabled": enabled,
            "created": datetime.now().isoformat(),
            "last_run": None,
            "next_run": None,
            "run_count": 0,
            "last_result": None
        }

        # Calculate next run
        task["next_run"] = self._calculate_next_run(task)

        self.tasks[task_id] = task
        self.save_tasks()

        return {"success": True, "task": task}

    def remove_task(self, task_id: str) -> Dict:
        """Remove a scheduled task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.save_tasks()
            return {"success": True, "message": f"Task {task_id} removed"}
        return {"success": False, "error": f"Task {task_id} not found"}

    def enable_task(self, task_id: str, enabled: bool = True) -> Dict:
        """Enable or disable a task"""
        if task_id in self.tasks:
            self.tasks[task_id]["enabled"] = enabled
            if enabled:
                self.tasks[task_id]["next_run"] = self._calculate_next_run(self.tasks[task_id])
            self.save_tasks()
            return {"success": True, "enabled": enabled}
        return {"success": False, "error": f"Task {task_id} not found"}

    def _calculate_next_run(self, task: Dict) -> Optional[str]:
        """Calculate next run time for a task"""
        now = datetime.now()
        task_type = task.get("type", "once")
        schedule_time = task.get("time")

        try:
            if task_type == "once":
                if schedule_time:
                    # Parse date time: YYYY-MM-DD HH:MM or just HH:MM (today)
                    if len(schedule_time) > 5:
                        next_run = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
                    else:
                        time_parts = schedule_time.split(":")
                        next_run = now.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=0)
                        if next_run <= now:
                            next_run += timedelta(days=1)
                    return next_run.isoformat()

            elif task_type == "daily":
                if schedule_time:
                    time_parts = schedule_time.split(":")
                    next_run = now.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=0)
                    if next_run <= now:
                        next_run += timedelta(days=1)
                    return next_run.isoformat()

            elif task_type == "weekly":
                if schedule_time and task.get("days"):
                    day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
                    target_days = [day_map.get(d.lower()[:3], 0) for d in task["days"]]

                    time_parts = schedule_time.split(":")
                    base_time = now.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=0)

                    # Find next valid day
                    for i in range(7):
                        check_date = base_time + timedelta(days=i)
                        if check_date.weekday() in target_days and check_date > now:
                            return check_date.isoformat()

            elif task_type == "interval":
                interval = task.get("interval_minutes", 60)
                last_run = task.get("last_run")
                if last_run:
                    last = datetime.fromisoformat(last_run)
                    next_run = last + timedelta(minutes=interval)
                else:
                    next_run = now + timedelta(minutes=interval)
                return next_run.isoformat()

        except Exception as e:
            logger.error(f"Error calculating next run: {e}")

        return None

    def _run_task(self, task: Dict) -> Dict:
        """Execute a task"""
        command = task.get("command", "")
        result = {
            "success": False,
            "output": "",
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Execute command
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )

            result["success"] = proc.returncode == 0
            result["output"] = proc.stdout or proc.stderr or "Completed"
            result["return_code"] = proc.returncode

        except subprocess.TimeoutExpired:
            result["error"] = "Command timed out"
        except Exception as e:
            result["error"] = str(e)

        # Update task
        task["last_run"] = datetime.now().isoformat()
        task["last_result"] = result
        task["run_count"] = task.get("run_count", 0) + 1

        # Calculate next run (unless it's a one-time task)
        if task["type"] != "once":
            task["next_run"] = self._calculate_next_run(task)
        else:
            task["enabled"] = False  # Disable one-time tasks after run

        self.save_tasks()

        # Callback
        if self.task_callback:
            self.task_callback(task["name"], result.get("output", result.get("error", ""))[:500])

        return result

    def _scheduler_loop(self):
        """Background scheduler loop"""
        while self.running:
            now = datetime.now()

            for task_id, task in list(self.tasks.items()):
                if not task.get("enabled", True):
                    continue

                next_run = task.get("next_run")
                if not next_run:
                    continue

                try:
                    next_run_time = datetime.fromisoformat(next_run)
                    if now >= next_run_time:
                        logger.info(f"Running scheduled task: {task['name']}")
                        self._run_task(task)
                except Exception as e:
                    logger.error(f"Error checking task {task_id}: {e}")

            time.sleep(30)  # Check every 30 seconds

    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            logger.info("Task scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Task scheduler stopped")

    def list_tasks(self) -> List[Dict]:
        """List all scheduled tasks"""
        return list(self.tasks.values())

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a specific task"""
        return self.tasks.get(task_id)

    def run_now(self, task_id: str) -> Dict:
        """Run a task immediately"""
        if task_id in self.tasks:
            return self._run_task(self.tasks[task_id])
        return {"success": False, "error": f"Task {task_id} not found"}
