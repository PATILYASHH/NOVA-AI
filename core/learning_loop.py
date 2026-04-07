"""
NOVA - Learning Loop
Actual feedback loop where past learnings influence future behavior
Closes the gap between recording data and using it
"""

import os
import json
import logging
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BehaviorProfile:
    """Tracks and learns from behavioral patterns"""

    def __init__(self):
        self.command_success_rates = {}  # command -> {success, total}
        self.error_patterns = {}  # error_type -> {count, solutions}
        self.user_corrections = []  # When user corrects NOVA
        self.effective_responses = []  # Responses that worked well
        self.timing_patterns = {}  # command -> typical execution times
        self.path_preferences = {}  # Which paths user accesses most
        self.workflow_patterns = []  # Detected multi-step workflows

    def to_dict(self) -> Dict:
        return {
            "command_success_rates": self.command_success_rates,
            "error_patterns": self.error_patterns,
            "user_corrections": self.user_corrections[-50:],
            "effective_responses": self.effective_responses[-50:],
            "timing_patterns": self.timing_patterns,
            "path_preferences": self.path_preferences,
            "workflow_patterns": self.workflow_patterns[-20:],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'BehaviorProfile':
        profile = cls()
        profile.command_success_rates = data.get("command_success_rates", {})
        profile.error_patterns = data.get("error_patterns", {})
        profile.user_corrections = data.get("user_corrections", [])
        profile.effective_responses = data.get("effective_responses", [])
        profile.timing_patterns = data.get("timing_patterns", {})
        profile.path_preferences = data.get("path_preferences", {})
        profile.workflow_patterns = data.get("workflow_patterns", [])
        return profile


class AdaptiveStrategy:
    """Strategies that adapt based on learned behavior"""

    def __init__(self, profile: BehaviorProfile):
        self.profile = profile

    def should_confirm_before_execute(self, command: str) -> Tuple[bool, str]:
        """Decide if we should ask for confirmation based on history"""
        rates = self.profile.command_success_rates.get(command, {})
        total = rates.get("total", 0)
        success = rates.get("success", 0)

        if total >= 3:
            rate = success / total
            if rate < 0.5:
                return True, f"This command has a {rate*100:.0f}% success rate. Want me to proceed?"

        # Check if it's in error patterns
        for error_type, data in self.profile.error_patterns.items():
            if command in str(data.get("triggers", [])):
                return True, f"This command has caused '{error_type}' errors before. Proceed carefully?"

        return False, ""

    def get_alternative_command(self, failed_command: str) -> Optional[str]:
        """Suggest alternative when a command fails"""
        # Look for corrections that followed similar failures
        for correction in reversed(self.profile.user_corrections):
            if correction.get("original_intent") == failed_command:
                return correction.get("corrected_to")

        # Look for error patterns with solutions
        for error_type, data in self.profile.error_patterns.items():
            if failed_command in str(data.get("triggers", [])):
                solutions = data.get("solutions", [])
                if solutions:
                    return solutions[-1]

        return None

    def get_preferred_path(self, context: str) -> Optional[str]:
        """Get user's preferred path for a given context"""
        prefs = self.profile.path_preferences
        if context in prefs:
            # Return most frequently used path
            paths = prefs[context]
            if isinstance(paths, dict):
                return max(paths, key=paths.get, default=None)
        return None

    def predict_next_action(self, current_action: str) -> Optional[Dict]:
        """Predict what user will do next based on workflow patterns"""
        for workflow in self.profile.workflow_patterns:
            steps = workflow.get("steps", [])
            for i, step in enumerate(steps):
                if step == current_action and i + 1 < len(steps):
                    return {
                        "prediction": steps[i + 1],
                        "workflow": workflow.get("name", "unnamed"),
                        "confidence": workflow.get("confidence", 50)
                    }
        return None


class LearningLoop:
    """
    Main learning loop system
    Records outcomes, detects patterns, and adapts behavior
    """

    def __init__(self):
        self.profile = BehaviorProfile()
        self.strategy = AdaptiveStrategy(self.profile)
        self.pending_feedback = None
        self.session_actions = []  # Actions in current session for pattern detection
        self._load()
        logger.info("Learning Loop initialized")

    def _data_file(self):
        return os.path.join(BASE_DIR, "intelligence", "data", "learning_loop.json")

    def _load(self):
        """Load learned data"""
        try:
            path = self._data_file()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.profile = BehaviorProfile.from_dict(data.get("profile", {}))
                    self.strategy = AdaptiveStrategy(self.profile)
        except Exception as e:
            logger.error(f"Failed to load learning data: {e}")

    def _save(self):
        """Save learned data"""
        try:
            os.makedirs(os.path.dirname(self._data_file()), exist_ok=True)
            with open(self._data_file(), 'w', encoding='utf-8') as f:
                json.dump({
                    "profile": self.profile.to_dict(),
                    "last_save": datetime.now().isoformat()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save learning data: {e}")

    def record_action(self, command: str, result: str, success: bool,
                      execution_time: float = 0, category: str = "general"):
        """Record an action and its outcome - the core learning input"""

        # Update command success rates
        if command not in self.profile.command_success_rates:
            self.profile.command_success_rates[command] = {"success": 0, "total": 0}

        rates = self.profile.command_success_rates[command]
        rates["total"] += 1
        if success:
            rates["success"] += 1

        # Track timing
        if execution_time > 0:
            if command not in self.profile.timing_patterns:
                self.profile.timing_patterns[command] = {"times": [], "avg": 0}
            tp = self.profile.timing_patterns[command]
            tp["times"].append(execution_time)
            tp["times"] = tp["times"][-20:]  # Keep last 20
            tp["avg"] = sum(tp["times"]) / len(tp["times"])

        # Record error patterns
        if not success and result:
            self._learn_from_error(command, result)

        # Track session actions for workflow detection
        self.session_actions.append({
            "command": command,
            "category": category,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

        # Detect workflows every 10 actions
        if len(self.session_actions) % 10 == 0:
            self._detect_workflows()

        self._save()

    def record_user_correction(self, original_intent: str, corrected_to: str,
                                context: str = ""):
        """Record when user corrects NOVA's behavior"""
        self.profile.user_corrections.append({
            "original_intent": original_intent,
            "corrected_to": corrected_to,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def record_effective_response(self, response_type: str, context: str):
        """Record a response that worked well (user didn't correct it)"""
        self.profile.effective_responses.append({
            "type": response_type,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def record_path_access(self, path: str, context: str = "general"):
        """Track file path access patterns"""
        if context not in self.profile.path_preferences:
            self.profile.path_preferences[context] = {}

        prefs = self.profile.path_preferences[context]
        prefs[path] = prefs.get(path, 0) + 1
        self._save()

    def _learn_from_error(self, command: str, error_message: str):
        """Learn from errors to avoid them in future"""
        # Categorize the error
        error_type = self._categorize_error(error_message)

        if error_type not in self.profile.error_patterns:
            self.profile.error_patterns[error_type] = {
                "count": 0,
                "triggers": [],
                "solutions": [],
                "last_seen": None
            }

        pattern = self.profile.error_patterns[error_type]
        pattern["count"] += 1
        pattern["last_seen"] = datetime.now().isoformat()

        if command not in pattern["triggers"]:
            pattern["triggers"].append(command)
            pattern["triggers"] = pattern["triggers"][-10:]

    def _categorize_error(self, error_message: str) -> str:
        """Categorize an error message"""
        error_lower = error_message.lower()

        categories = {
            "permission_denied": ["permission", "access denied", "not authorized", "forbidden"],
            "not_found": ["not found", "no such file", "does not exist", "404", "missing"],
            "timeout": ["timeout", "timed out", "took too long"],
            "connection_error": ["connection", "network", "dns", "unreachable", "refused"],
            "syntax_error": ["syntax", "unexpected", "parse error", "invalid"],
            "memory_error": ["memory", "out of memory", "heap", "stack overflow"],
            "disk_error": ["disk full", "no space", "quota exceeded"],
            "process_error": ["process", "pid", "zombie", "defunct"],
        }

        for category, keywords in categories.items():
            if any(kw in error_lower for kw in keywords):
                return category

        return "unknown_error"

    def _detect_workflows(self):
        """Detect repeated sequences of actions"""
        if len(self.session_actions) < 5:
            return

        # Look for 2-4 step patterns
        actions = [a["command"] for a in self.session_actions[-50:]]

        for window_size in [2, 3, 4]:
            sequences = []
            for i in range(len(actions) - window_size + 1):
                seq = tuple(actions[i:i + window_size])
                sequences.append(seq)

            # Find repeated sequences
            counter = Counter(sequences)
            for seq, count in counter.most_common(5):
                if count >= 2:
                    workflow = {
                        "steps": list(seq),
                        "name": f"workflow_{len(self.profile.workflow_patterns)}",
                        "count": count,
                        "confidence": min(count * 15, 80),
                        "detected_at": datetime.now().isoformat()
                    }
                    # Don't add duplicates
                    existing = [w for w in self.profile.workflow_patterns
                                if w["steps"] == workflow["steps"]]
                    if existing:
                        existing[0]["count"] = max(existing[0]["count"], count)
                        existing[0]["confidence"] = min(count * 15, 80)
                    else:
                        self.profile.workflow_patterns.append(workflow)

    def provide_solution(self, error_type: str) -> Optional[str]:
        """Provide solution for a known error type"""
        solutions = {
            "permission_denied": "Try running with administrator privileges, or check file permissions.",
            "not_found": "The file or resource doesn't exist. Check the path or name.",
            "timeout": "The operation timed out. Check your connection or try again.",
            "connection_error": "Network issue detected. Check your internet connection.",
            "syntax_error": "There's a syntax error. Review the command or code.",
            "memory_error": "System is low on memory. Close some applications.",
            "disk_error": "Disk is full. Free up space with /cleantemp or /emptybin.",
            "process_error": "Process issue. Try /processes to see what's running.",
        }

        return solutions.get(error_type)

    def get_learning_summary(self) -> str:
        """Get summary of what NOVA has learned"""
        summary = "**NOVA Learning Summary**\n\n"

        # Command success rates
        if self.profile.command_success_rates:
            summary += "**Command Reliability:**\n"
            sorted_cmds = sorted(
                self.profile.command_success_rates.items(),
                key=lambda x: x[1]["total"],
                reverse=True
            )[:10]
            for cmd, data in sorted_cmds:
                rate = (data["success"] / data["total"] * 100) if data["total"] > 0 else 0
                summary += f"- `{cmd[:30]}`: {rate:.0f}% success ({data['total']} runs)\n"

        # Error patterns
        if self.profile.error_patterns:
            summary += "\n**Known Error Patterns:**\n"
            for error_type, data in list(self.profile.error_patterns.items())[:5]:
                summary += f"- {error_type}: seen {data['count']} times\n"

        # Detected workflows
        if self.profile.workflow_patterns:
            summary += "\n**Detected Workflows:**\n"
            for wf in self.profile.workflow_patterns[:5]:
                summary += f"- {' -> '.join(wf['steps'][:4])} (seen {wf['count']}x)\n"

        # User corrections
        corrections = len(self.profile.user_corrections)
        if corrections:
            summary += f"\n**User Corrections:** {corrections} recorded\n"

        return summary

    def before_action(self, command: str) -> Dict:
        """
        Called BEFORE executing an action
        Returns guidance based on learned behavior
        """
        guidance = {
            "proceed": True,
            "confirm": False,
            "warnings": [],
            "suggestions": [],
            "predicted_next": None,
        }

        # Check if we should confirm
        should_confirm, reason = self.strategy.should_confirm_before_execute(command)
        if should_confirm:
            guidance["confirm"] = True
            guidance["warnings"].append(reason)

        # Predict next action
        prediction = self.strategy.predict_next_action(command)
        if prediction:
            guidance["predicted_next"] = prediction

        # Check for known error patterns
        for error_type, data in self.profile.error_patterns.items():
            if command in str(data.get("triggers", [])):
                solution = self.provide_solution(error_type)
                if solution:
                    guidance["warnings"].append(
                        f"This command has triggered '{error_type}' errors before. {solution}"
                    )

        return guidance

    def after_action(self, command: str, result: str, success: bool) -> Dict:
        """
        Called AFTER executing an action
        Returns suggestions based on outcome
        """
        feedback = {
            "suggestion": None,
            "alternative": None,
            "next_action": None,
        }

        if not success:
            # Suggest alternative
            alt = self.strategy.get_alternative_command(command)
            if alt:
                feedback["alternative"] = alt
                feedback["suggestion"] = f"Try this instead: {alt}"

            # Provide error-specific solution
            error_type = self._categorize_error(result)
            solution = self.provide_solution(error_type)
            if solution:
                feedback["suggestion"] = solution

        else:
            # Predict next action
            prediction = self.strategy.predict_next_action(command)
            if prediction and prediction["confidence"] >= 50:
                feedback["next_action"] = prediction

        return feedback
