"""
NOVA - Proactive Assistant
Time-based suggestions, pattern-driven recommendations,
anticipates user needs based on learned behavior
"""

import os
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ProactiveAssistant:
    """
    Proactively suggests actions based on:
    1. Time patterns (what user usually does at this time)
    2. Habit patterns (what usually comes next)
    3. System state (preemptive warnings)
    4. Calendar/schedule awareness
    5. Idle detection (suggest things when user is idle)
    """

    def __init__(self, habit_tracker=None, learning_loop=None, alert_callback=None):
        self.habit_tracker = habit_tracker
        self.learning_loop = learning_loop
        self.alert_callback = alert_callback
        self.running = False
        self.thread = None
        self.last_suggestion_time = {}  # category -> last suggestion time
        self.suggestion_cooldown = 300  # 5 minutes between suggestions
        self.dismissed_suggestions = set()  # Track dismissed suggestions
        self.suggestion_history = []
        self._load_state()
        logger.info("Proactive Assistant initialized")

    def _state_file(self):
        return os.path.join(BASE_DIR, "intelligence", "data", "proactive_state.json")

    def _load_state(self):
        """Load state"""
        try:
            path = self._state_file()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.dismissed_suggestions = set(data.get("dismissed", []))
                    self.suggestion_history = data.get("history", [])
        except Exception:
            pass

    def _save_state(self):
        """Save state"""
        try:
            os.makedirs(os.path.dirname(self._state_file()), exist_ok=True)
            with open(self._state_file(), 'w', encoding='utf-8') as f:
                json.dump({
                    "dismissed": list(self.dismissed_suggestions),
                    "history": self.suggestion_history[-100:],
                }, f, indent=2, default=str)
        except Exception:
            pass

    def _can_suggest(self, category: str) -> bool:
        """Check if we can make a suggestion in this category"""
        if category in self.dismissed_suggestions:
            return False
        last = self.last_suggestion_time.get(category)
        if last:
            elapsed = (datetime.now() - last).total_seconds()
            return elapsed >= self.suggestion_cooldown
        return True

    def _record_suggestion(self, suggestion: Dict):
        """Record a suggestion"""
        self.last_suggestion_time[suggestion["category"]] = datetime.now()
        self.suggestion_history.append({
            **suggestion,
            "timestamp": datetime.now().isoformat()
        })
        self._save_state()

    def dismiss_suggestion(self, category: str):
        """Dismiss a category of suggestions"""
        self.dismissed_suggestions.add(category)
        self._save_state()

    def get_suggestions(self) -> List[Dict]:
        """
        Get current proactive suggestions
        Called periodically or on user interaction
        """
        suggestions = []

        # 1. Time-based suggestions from habit tracker
        if self.habit_tracker:
            habit_suggestions = self._get_habit_suggestions()
            suggestions.extend(habit_suggestions)

        # 2. System-aware suggestions
        system_suggestions = self._get_system_suggestions()
        suggestions.extend(system_suggestions)

        # 3. Work pattern suggestions
        work_suggestions = self._get_work_suggestions()
        suggestions.extend(work_suggestions)

        # 4. Workflow continuation suggestions
        if self.learning_loop:
            workflow_suggestions = self._get_workflow_suggestions()
            suggestions.extend(workflow_suggestions)

        # 5. Time-aware reminders
        time_suggestions = self._get_time_suggestions()
        suggestions.extend(time_suggestions)

        # Filter by cooldown and dismissed
        filtered = [s for s in suggestions
                     if self._can_suggest(s["category"])]

        # Sort by priority
        filtered.sort(key=lambda x: x.get("priority", 5), reverse=True)

        return filtered[:5]

    def _get_habit_suggestions(self) -> List[Dict]:
        """Get suggestions based on user habits"""
        suggestions = []

        if not self.habit_tracker:
            return suggestions

        predictions = self.habit_tracker.get_predictions()
        for pred in predictions[:3]:
            if pred["confidence"] >= 40:
                suggestions.append({
                    "category": f"habit_{pred['type']}",
                    "message": f"{pred['suggestion']}",
                    "reason": pred["reason"],
                    "confidence": pred["confidence"],
                    "priority": pred["confidence"] // 20,
                    "action": pred["suggestion"],
                })

        return suggestions

    def _get_system_suggestions(self) -> List[Dict]:
        """Get suggestions based on system state"""
        suggestions = []

        try:
            import psutil

            # Memory check
            mem = psutil.virtual_memory()
            if mem.percent > 93 and self._can_suggest("system_memory"):
                # Find top memory consumers
                top_procs = []
                for proc in psutil.process_iter(['name', 'memory_percent']):
                    try:
                        if proc.info['memory_percent'] and proc.info['memory_percent'] > 5:
                            top_procs.append(f"{proc.info['name']} ({proc.info['memory_percent']:.1f}%)")
                    except Exception:
                        pass

                msg = f"Memory is at {mem.percent}%."
                if top_procs:
                    msg += f" Top consumers: {', '.join(top_procs[:3])}"

                suggestions.append({
                    "category": "system_memory",
                    "message": msg,
                    "reason": "High memory usage detected",
                    "priority": 7,
                    "action": "check_memory",
                })

            # Disk check
            disk = psutil.disk_usage('C:')
            free_gb = disk.free / (1024**3)
            if free_gb < 10 and self._can_suggest("system_disk"):
                suggestions.append({
                    "category": "system_disk",
                    "message": f"Only {free_gb:.1f}GB free on C: drive. Consider cleanup.",
                    "reason": "Low disk space",
                    "priority": 6,
                    "action": "disk_cleanup",
                })

            # Battery check
            try:
                battery = psutil.sensors_battery()
                if battery and not battery.power_plugged and battery.percent < 15:
                    suggestions.append({
                        "category": "system_battery",
                        "message": f"Battery at {battery.percent}%. Consider plugging in.",
                        "reason": "Low battery",
                        "priority": 8 if battery.percent < 15 else 5,
                        "action": "battery_warning",
                    })
            except Exception:
                pass

        except Exception as e:
            logger.debug(f"System suggestion error: {e}")

        return suggestions

    def _get_work_suggestions(self) -> List[Dict]:
        """Get work pattern suggestions"""
        suggestions = []
        now = datetime.now()

        # Break reminder after long session
        # Check if user has been active for > 2 hours
        if self._can_suggest("break_reminder"):
            suggestions.append({
                "category": "break_reminder",
                "message": "You've been working for a while. Consider a short break.",
                "reason": "Long work session detected",
                "priority": 2,
                "action": "break_reminder",
            })

        # End of day reminder
        if now.hour == 17 and now.minute < 30 and self._can_suggest("eod_reminder"):
            suggestions.append({
                "category": "eod_reminder",
                "message": "It's almost end of day. Run /endofday for a review?",
                "reason": "End of work day approaching",
                "priority": 3,
                "action": "end_of_day",
            })

        return suggestions

    def _get_workflow_suggestions(self) -> List[Dict]:
        """Get workflow continuation suggestions"""
        suggestions = []

        if not self.learning_loop:
            return suggestions

        # Check if there are detected workflows we can suggest
        for wf in self.learning_loop.profile.workflow_patterns:
            if wf["confidence"] >= 60:
                wf_key = f"workflow_{'_'.join(wf['steps'][:2])}"
                if self._can_suggest(wf_key):
                    suggestions.append({
                        "category": wf_key,
                        "message": f"Common workflow detected: {' -> '.join(wf['steps'])}. Execute it?",
                        "reason": f"You've done this {wf['count']} times before",
                        "priority": 4,
                        "action": "execute_workflow",
                        "workflow_steps": wf["steps"],
                    })

        return suggestions

    def _get_time_suggestions(self) -> List[Dict]:
        """Get time-aware suggestions"""
        suggestions = []
        now = datetime.now()

        # Morning routine suggestion
        if 8 <= now.hour <= 10 and self._can_suggest("morning_routine"):
            suggestions.append({
                "category": "morning_routine",
                "message": "Good morning! Want me to run a system health check?",
                "reason": "Start of work day",
                "priority": 3,
                "action": "morning_check",
            })

        return suggestions

    def start_background(self, interval: int = 300):
        """Start background suggestion checking"""
        if self.running:
            return

        self.running = True

        def _loop():
            while self.running:
                try:
                    suggestions = self.get_suggestions()
                    for s in suggestions:
                        if s["priority"] >= 6 and self.alert_callback:
                            self.alert_callback(s["category"], s["message"])
                            self._record_suggestion(s)
                except Exception as e:
                    logger.error(f"Proactive assistant error: {e}")
                time.sleep(interval)

        self.thread = threading.Thread(target=_loop, daemon=True)
        self.thread.start()
        logger.info("Proactive assistant started in background")

    def stop(self):
        """Stop background checking"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def get_summary(self) -> str:
        """Get suggestion summary"""
        recent = self.suggestion_history[-20:]
        if not recent:
            return "No suggestions generated yet."

        text = "**Proactive Suggestions History:**\n\n"
        for s in recent[-10:]:
            text += f"- [{s.get('timestamp', '')[:16]}] {s.get('message', '')[:60]}\n"
        return text
