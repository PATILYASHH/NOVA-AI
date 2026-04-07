"""
NOVA - Habit Tracker
Learn user patterns and predict needs
"""

import os
import json
import logging
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HABITS_FILE = os.path.join(BASE_DIR, "intelligence", "data", "habits.json")


class HabitTracker:
    """
    Track user habits and patterns to predict needs
    """

    def __init__(self):
        self.data = self._load()

    def _load(self) -> Dict:
        """Load habit data"""
        try:
            if os.path.exists(HABITS_FILE):
                with open(HABITS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass

        return {
            "commands": [],           # Command history with timestamps
            "patterns": {             # Detected patterns
                "hourly": {},         # What user does at each hour
                "daily": {},          # What user does each day
                "sequences": [],      # Common command sequences
            },
            "projects": {},           # Project work patterns
            "apps": {},               # App usage patterns
            "files": {},              # File access patterns
            "predictions": [],        # Generated predictions
            "last_analysis": None
        }

    def _save(self):
        """Save habit data"""
        try:
            os.makedirs(os.path.dirname(HABITS_FILE), exist_ok=True)
            with open(HABITS_FILE, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save habits: {e}")

    def record_command(self, command: str, category: str = "general"):
        """Record a command execution"""
        now = datetime.now()

        entry = {
            "command": command,
            "category": category,
            "timestamp": now.isoformat(),
            "hour": now.hour,
            "day": now.strftime("%A").lower(),
            "date": now.strftime("%Y-%m-%d")
        }

        self.data["commands"].append(entry)

        # Keep only last 1000 commands
        self.data["commands"] = self.data["commands"][-1000:]

        self._save()

    def record_app_usage(self, app_name: str):
        """Record app usage"""
        now = datetime.now()
        hour = now.hour
        day = now.strftime("%A").lower()

        if app_name not in self.data["apps"]:
            self.data["apps"][app_name] = {"count": 0, "hours": {}, "days": {}}

        self.data["apps"][app_name]["count"] += 1

        hour_str = str(hour)
        if hour_str not in self.data["apps"][app_name]["hours"]:
            self.data["apps"][app_name]["hours"][hour_str] = 0
        self.data["apps"][app_name]["hours"][hour_str] += 1

        if day not in self.data["apps"][app_name]["days"]:
            self.data["apps"][app_name]["days"][day] = 0
        self.data["apps"][app_name]["days"][day] += 1

        self._save()

    def record_project_work(self, project_name: str):
        """Record work on a project"""
        now = datetime.now()
        hour = now.hour
        day = now.strftime("%A").lower()

        if project_name not in self.data["projects"]:
            self.data["projects"][project_name] = {
                "total_sessions": 0,
                "hours": {},
                "days": {},
                "last_worked": None
            }

        self.data["projects"][project_name]["total_sessions"] += 1
        self.data["projects"][project_name]["last_worked"] = now.isoformat()

        hour_str = str(hour)
        if hour_str not in self.data["projects"][project_name]["hours"]:
            self.data["projects"][project_name]["hours"][hour_str] = 0
        self.data["projects"][project_name]["hours"][hour_str] += 1

        if day not in self.data["projects"][project_name]["days"]:
            self.data["projects"][project_name]["days"][day] = 0
        self.data["projects"][project_name]["days"][day] += 1

        self._save()

    def record_file_access(self, file_path: str, action: str = "read"):
        """Record file access"""
        if file_path not in self.data["files"]:
            self.data["files"][file_path] = {"count": 0, "actions": {}}

        self.data["files"][file_path]["count"] += 1

        if action not in self.data["files"][file_path]["actions"]:
            self.data["files"][file_path]["actions"][action] = 0
        self.data["files"][file_path]["actions"][action] += 1

        self._save()

    def analyze_patterns(self) -> Dict:
        """Analyze recorded data for patterns"""
        commands = self.data["commands"]

        if len(commands) < 10:
            return {"message": "Not enough data for analysis"}

        # Hourly patterns
        hourly_commands = defaultdict(list)
        for cmd in commands:
            hour = cmd.get("hour", 0)
            hourly_commands[hour].append(cmd["command"])

        hourly_patterns = {}
        for hour, cmds in hourly_commands.items():
            counter = Counter(cmds)
            most_common = counter.most_common(3)
            if most_common:
                hourly_patterns[hour] = [{"command": c, "count": n} for c, n in most_common]

        # Daily patterns
        daily_commands = defaultdict(list)
        for cmd in commands:
            day = cmd.get("day", "monday")
            daily_commands[day].append(cmd["command"])

        daily_patterns = {}
        for day, cmds in daily_commands.items():
            counter = Counter(cmds)
            most_common = counter.most_common(3)
            if most_common:
                daily_patterns[day] = [{"command": c, "count": n} for c, n in most_common]

        # Command sequences (what follows what)
        sequences = []
        for i in range(len(commands) - 1):
            seq = (commands[i]["command"], commands[i + 1]["command"])
            sequences.append(seq)

        seq_counter = Counter(sequences)
        common_sequences = [
            {"first": s[0], "then": s[1], "count": c}
            for s, c in seq_counter.most_common(10)
            if c >= 2
        ]

        # Update patterns
        self.data["patterns"]["hourly"] = hourly_patterns
        self.data["patterns"]["daily"] = daily_patterns
        self.data["patterns"]["sequences"] = common_sequences
        self.data["last_analysis"] = datetime.now().isoformat()

        self._save()

        return {
            "hourly_patterns": hourly_patterns,
            "daily_patterns": daily_patterns,
            "common_sequences": common_sequences,
            "total_commands_analyzed": len(commands)
        }

    def get_predictions(self) -> List[Dict]:
        """Get predictions based on current time and patterns"""
        now = datetime.now()
        hour = now.hour
        day = now.strftime("%A").lower()

        predictions = []

        # Hour-based predictions
        hourly = self.data["patterns"].get("hourly", {})
        if str(hour) in hourly:
            for cmd_data in hourly[str(hour)][:2]:
                predictions.append({
                    "type": "hourly",
                    "suggestion": cmd_data["command"],
                    "reason": f"You often run this at {hour}:00",
                    "confidence": min(cmd_data["count"] * 10, 90)
                })

        # Day-based predictions
        daily = self.data["patterns"].get("daily", {})
        if day in daily:
            for cmd_data in daily[day][:2]:
                if cmd_data["command"] not in [p["suggestion"] for p in predictions]:
                    predictions.append({
                        "type": "daily",
                        "suggestion": cmd_data["command"],
                        "reason": f"You often do this on {day.capitalize()}s",
                        "confidence": min(cmd_data["count"] * 10, 85)
                    })

        # App suggestions based on time
        for app, data in self.data["apps"].items():
            hour_count = data["hours"].get(str(hour), 0)
            if hour_count >= 3:
                predictions.append({
                    "type": "app",
                    "suggestion": f"Open {app}",
                    "reason": f"You usually use {app} around this time",
                    "confidence": min(hour_count * 15, 80)
                })

        # Project suggestions
        for project, data in self.data["projects"].items():
            hour_count = data["hours"].get(str(hour), 0)
            day_count = data["days"].get(day, 0)
            if hour_count >= 2 or day_count >= 3:
                predictions.append({
                    "type": "project",
                    "suggestion": f"Work on {project}",
                    "reason": f"You often work on {project} at this time",
                    "confidence": min((hour_count + day_count) * 10, 75)
                })

        # Sort by confidence
        predictions.sort(key=lambda x: x["confidence"], reverse=True)

        return predictions[:5]

    def get_next_likely_command(self, current_command: str) -> Optional[Dict]:
        """Predict next command based on sequences"""
        sequences = self.data["patterns"].get("sequences", [])

        for seq in sequences:
            if seq["first"] == current_command:
                return {
                    "prediction": seq["then"],
                    "confidence": min(seq["count"] * 20, 80),
                    "reason": f"You often run '{seq['then']}' after '{current_command}'"
                }

        return None

    def get_most_used(self, category: str = "commands", limit: int = 10) -> List[Dict]:
        """Get most used items"""
        if category == "commands":
            counter = Counter(cmd["command"] for cmd in self.data["commands"])
            return [{"item": c, "count": n} for c, n in counter.most_common(limit)]

        elif category == "apps":
            sorted_apps = sorted(
                self.data["apps"].items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )
            return [{"item": name, "count": data["count"]} for name, data in sorted_apps[:limit]]

        elif category == "projects":
            sorted_projects = sorted(
                self.data["projects"].items(),
                key=lambda x: x[1]["total_sessions"],
                reverse=True
            )
            return [{"item": name, "count": data["total_sessions"]} for name, data in sorted_projects[:limit]]

        return []

    def get_summary(self) -> Dict:
        """Get habit summary"""
        return {
            "total_commands_tracked": len(self.data["commands"]),
            "apps_tracked": len(self.data["apps"]),
            "projects_tracked": len(self.data["projects"]),
            "files_tracked": len(self.data["files"]),
            "patterns_detected": len(self.data["patterns"].get("sequences", [])),
            "last_analysis": self.data.get("last_analysis")
        }
