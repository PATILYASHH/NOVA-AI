"""
NOVA - Context Engine
Memory-driven decision making - pulls relevant memory into every response
Makes NOVA actually USE its memory for intelligent behavior
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ContextEngine:
    """
    Makes NOVA context-aware by:
    1. Pulling relevant past interactions for current query
    2. Remembering user preferences from history
    3. Building situational awareness
    4. Providing context-enriched responses
    """

    def __init__(self, memory_system):
        self.memory = memory_system
        self.user_preferences = {}
        self.session_context = {
            "topics_discussed": [],
            "actions_taken": [],
            "errors_encountered": [],
            "files_touched": [],
            "projects_active": [],
            "mood_trajectory": [],
            "start_time": datetime.now().isoformat(),
        }
        self._load_preferences()
        logger.info("Context Engine initialized")

    def _prefs_file(self):
        return os.path.join(BASE_DIR, "intelligence", "data", "user_preferences.json")

    def _load_preferences(self):
        """Load learned user preferences"""
        try:
            path = self._prefs_file()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")

    def _save_preferences(self):
        """Save user preferences"""
        try:
            os.makedirs(os.path.dirname(self._prefs_file()), exist_ok=True)
            with open(self._prefs_file(), 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")

    def build_context(self, user_message: str, nlp_result: Dict) -> Dict:
        """
        Build rich context for the current interaction
        This is called before every response to make NOVA context-aware
        """
        context = {
            "user_message": user_message,
            "timestamp": datetime.now().isoformat(),
            "time_of_day": self._get_time_period(),
            "session_duration_minutes": self._get_session_duration(),
        }

        # 1. Get relevant past interactions
        context["relevant_history"] = self._find_relevant_history(
            user_message, nlp_result.get("primary_intent", "general")
        )

        # 2. Get current session context
        context["session"] = self.session_context.copy()

        # 3. Get user preferences relevant to this intent
        intent = nlp_result.get("primary_intent", "general")
        context["preferences"] = self._get_relevant_preferences(intent)

        # 4. Get active project context
        context["active_project"] = self._get_project_context()

        # 5. Get conversation continuity
        context["conversation_topic"] = nlp_result.get("conversation_context", {}).get("current_topic")
        context["is_followup"] = self._is_followup(user_message, nlp_result)

        # 6. Get system state awareness
        context["system_state"] = self._get_system_state_summary()

        # 7. Error context - if user seems frustrated
        if nlp_result.get("sentiment", {}).get("sentiment") == "negative":
            context["user_frustrated"] = True
            context["recent_errors"] = self.session_context["errors_encountered"][-5:]

        # 8. Time-aware context
        context["work_pattern"] = self._get_work_pattern_context()

        return context

    def update_session(self, action: str, result: str, success: bool, category: str = "general"):
        """Update session context after each action"""
        self.session_context["actions_taken"].append({
            "action": action,
            "success": success,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })

        if not success:
            self.session_context["errors_encountered"].append({
                "action": action,
                "error": result[:200],
                "timestamp": datetime.now().isoformat()
            })

        # Track topics
        if category not in self.session_context["topics_discussed"]:
            self.session_context["topics_discussed"].append(category)

    def learn_preference(self, category: str, preference: str, value: Any):
        """Learn a user preference from behavior"""
        if category not in self.user_preferences:
            self.user_preferences[category] = {}

        self.user_preferences[category][preference] = {
            "value": value,
            "learned_at": datetime.now().isoformat(),
            "confidence": self.user_preferences.get(category, {}).get(preference, {}).get("confidence", 0) + 10
        }
        self._save_preferences()

    def _find_relevant_history(self, message: str, intent: str) -> List[Dict]:
        """Find past interactions relevant to current query"""
        relevant = []

        # Search ROM for similar past commands
        try:
            words = message.strip().split()
            search_term = words[0] if words else message
            results = self.memory.rom.search_history(search_term, 10)
            for r in results:
                similarity = SequenceMatcher(None, message.lower(), r.get("command", "").lower()).ratio()
                if similarity > 0.3:
                    relevant.append({
                        "command": r["command"],
                        "result": r.get("result", "")[:100],
                        "success": r.get("success"),
                        "similarity": round(similarity, 2),
                        "when": r.get("timestamp", "")
                    })
        except Exception:
            pass

        # Sort by similarity
        relevant.sort(key=lambda x: x["similarity"], reverse=True)
        return relevant[:5]

    def _get_relevant_preferences(self, intent: str) -> Dict:
        """Get preferences relevant to current intent"""
        prefs = {}

        # Direct category match
        if intent in self.user_preferences:
            prefs.update(self.user_preferences[intent])

        # General preferences
        if "general" in self.user_preferences:
            prefs.update(self.user_preferences["general"])

        return prefs

    def _get_project_context(self) -> Optional[Dict]:
        """Get active project context"""
        try:
            if not self.memory or not hasattr(self.memory, 'rm'):
                return None
            active = self.memory.rm.context.get("active_project")
            if active:
                return {
                    "name": active,
                    "recent_commands": self.memory.rm.context.get("recent_commands", [])[-3:],
                    "task": self.memory.rm.context.get("current_task"),
                }
        except Exception:
            pass
        return None

    def _is_followup(self, message: str, nlp_result: Dict) -> bool:
        """Detect if this is a follow-up to previous conversation"""
        followup_indicators = [
            "also", "and", "too", "what about", "how about",
            "another", "next", "then", "now", "again",
            "it", "that", "this", "same"
        ]
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in followup_indicators)

    def _get_time_period(self) -> str:
        """Get current time period"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def _get_session_duration(self) -> int:
        """Get current session duration in minutes"""
        try:
            start = datetime.fromisoformat(self.session_context["start_time"])
            return int((datetime.now() - start).total_seconds() / 60)
        except Exception:
            return 0

    def _get_system_state_summary(self) -> Dict:
        """Get a quick system state summary"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(interval=0),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('C:').percent,
            }
        except Exception:
            return {}

    def _get_work_pattern_context(self) -> Dict:
        """Get work pattern insights for current time"""
        now = datetime.now()
        return {
            "is_work_hours": 9 <= now.hour <= 18,
            "is_weekend": now.weekday() >= 5,
            "day_of_week": now.strftime("%A"),
        }

    def get_smart_greeting(self) -> str:
        """Generate context-aware greeting"""
        period = self._get_time_period()
        greetings = {
            "morning": "Good morning, Yash. Ready to start the day.",
            "afternoon": "Good afternoon, Yash. How can I help?",
            "evening": "Good evening, Yash. Still working?",
            "night": "Working late, Yash. Let me know what you need.",
        }

        greeting = greetings.get(period, "Hello, Yash.")

        # Add session context if continuing
        actions = self.session_context["actions_taken"]
        if actions:
            last_category = actions[-1].get("category", "general")
            greeting += f"\nWe were working on {last_category} tasks."

        # Add project context
        try:
            active = self.memory.rm.context.get("active_project")
            if active:
                greeting += f"\nActive project: {active}"
        except Exception:
            pass

        return greeting

    def generate_response_prefix(self, nlp_result: Dict, context: Dict) -> Optional[str]:
        """
        Generate a smart prefix for responses based on context
        Returns None if no special prefix needed
        """
        prefixes = []

        # If user is frustrated, acknowledge it
        if context.get("user_frustrated"):
            prefixes.append("I see there have been some issues.")

        # If this is a repeated action that failed before
        history = context.get("relevant_history", [])
        failed_similar = [h for h in history if not h.get("success") and h.get("similarity", 0) > 0.7]
        if failed_similar:
            prefixes.append(f"Note: A similar command failed before. Let me try carefully.")

        # If switching topics
        current_topic = context.get("conversation_topic")
        new_intent = nlp_result.get("primary_intent")
        if current_topic and new_intent and current_topic != new_intent:
            pass  # Don't mention topic switches, just handle smoothly

        return " ".join(prefixes) if prefixes else None

    def get_context_summary(self) -> str:
        """Get a formatted summary of current context"""
        duration = self._get_session_duration()
        actions = len(self.session_context["actions_taken"])
        errors = len(self.session_context["errors_encountered"])
        topics = self.session_context["topics_discussed"]

        return (
            f"Session: {duration}min | Actions: {actions} | "
            f"Errors: {errors} | Topics: {', '.join(topics[:5]) if topics else 'None'}"
        )
