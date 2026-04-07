"""
NOVA - Reasoning Engine
Rule-based logic, decision trees, cause-effect analysis,
and intelligent decision making without external APIs
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DecisionNode:
    """A node in a decision tree"""

    def __init__(self, condition_fn, true_branch=None, false_branch=None,
                 action=None, description=""):
        self.condition_fn = condition_fn
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.action = action  # Leaf node action
        self.description = description

    def evaluate(self, context: Dict) -> Any:
        """Evaluate this node"""
        if self.action is not None:
            return self.action

        result = self.condition_fn(context)
        if result:
            return self.true_branch.evaluate(context) if self.true_branch else None
        else:
            return self.false_branch.evaluate(context) if self.false_branch else None


class Rule:
    """A single rule in the reasoning engine"""

    def __init__(self, name: str, conditions: List[callable], action: str,
                 priority: int = 5, description: str = ""):
        self.name = name
        self.conditions = conditions
        self.action = action
        self.priority = priority
        self.description = description
        self.fire_count = 0
        self.last_fired = None

    def evaluate(self, context: Dict) -> bool:
        """Check if all conditions are met"""
        try:
            return all(cond(context) for cond in self.conditions)
        except Exception:
            return False

    def fire(self) -> str:
        """Fire the rule and return its action"""
        self.fire_count += 1
        self.last_fired = datetime.now()
        return self.action


class CausalChain:
    """Track cause-effect relationships"""

    def __init__(self):
        self.chains = []  # List of {cause, effect, confidence, count}

    def record(self, cause: str, effect: str):
        """Record a cause-effect pair"""
        for chain in self.chains:
            if chain["cause"] == cause and chain["effect"] == effect:
                chain["count"] += 1
                chain["confidence"] = min(chain["count"] * 10, 95)
                chain["last_seen"] = datetime.now().isoformat()
                return

        self.chains.append({
            "cause": cause,
            "effect": effect,
            "count": 1,
            "confidence": 10,
            "last_seen": datetime.now().isoformat()
        })

    def predict_effect(self, cause: str) -> List[Dict]:
        """Predict effects of a cause"""
        predictions = []
        for chain in self.chains:
            if chain["cause"] == cause and chain["confidence"] >= 30:
                predictions.append({
                    "effect": chain["effect"],
                    "confidence": chain["confidence"],
                    "seen_count": chain["count"]
                })
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        return predictions

    def predict_cause(self, effect: str) -> List[Dict]:
        """Predict causes of an effect"""
        predictions = []
        for chain in self.chains:
            if chain["effect"] == effect and chain["confidence"] >= 30:
                predictions.append({
                    "cause": chain["cause"],
                    "confidence": chain["confidence"],
                    "seen_count": chain["count"]
                })
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        return predictions


class ReasoningEngine:
    """
    NOVA's reasoning engine - makes intelligent decisions
    without needing an external LLM
    """

    def __init__(self):
        self.rules = []
        self.causal = CausalChain()
        self.decision_log = []
        self.knowledge_base = {}
        self._load_state()
        self._register_default_rules()
        logger.info("Reasoning Engine initialized")

    def _state_file(self):
        return os.path.join(BASE_DIR, "intelligence", "data", "reasoning_state.json")

    def _load_state(self):
        """Load persistent reasoning state"""
        try:
            path = self._state_file()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.causal.chains = data.get("causal_chains", [])
                    self.knowledge_base = data.get("knowledge_base", {})
        except Exception as e:
            logger.error(f"Failed to load reasoning state: {e}")

    def _save_state(self):
        """Save persistent reasoning state"""
        try:
            os.makedirs(os.path.dirname(self._state_file()), exist_ok=True)
            with open(self._state_file(), 'w', encoding='utf-8') as f:
                json.dump({
                    "causal_chains": self.causal.chains,
                    "knowledge_base": self.knowledge_base,
                    "last_save": datetime.now().isoformat()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save reasoning state: {e}")

    def _register_default_rules(self):
        """Register built-in reasoning rules"""

        # Rule: High CPU -> suggest checking processes
        self.add_rule(Rule(
            name="high_cpu_check",
            conditions=[
                lambda ctx: ctx.get("system", {}).get("cpu_percent", 0) > 80
            ],
            action="suggest_check_processes",
            priority=8,
            description="When CPU is high, suggest checking what's using it"
        ))

        # Rule: Low disk -> suggest cleanup
        self.add_rule(Rule(
            name="low_disk_cleanup",
            conditions=[
                lambda ctx: ctx.get("system", {}).get("disk_percent", 0) > 85
            ],
            action="suggest_disk_cleanup",
            priority=7,
            description="When disk is almost full, suggest cleanup"
        ))

        # Rule: Repeated errors -> suggest different approach
        self.add_rule(Rule(
            name="repeated_errors",
            conditions=[
                lambda ctx: ctx.get("recent_error_count", 0) >= 3,
                lambda ctx: ctx.get("same_command_failed", False)
            ],
            action="suggest_alternative_approach",
            priority=9,
            description="When same command fails repeatedly, suggest alternatives"
        ))

        # Rule: Late night work -> suggest break
        self.add_rule(Rule(
            name="late_night_work",
            conditions=[
                lambda ctx: datetime.now().hour >= 23 or datetime.now().hour < 5,
                lambda ctx: ctx.get("session_duration_minutes", 0) > 60
            ],
            action="suggest_rest",
            priority=4,
            description="Late night + long session -> suggest rest"
        ))

        # Rule: Multiple file edits without git commit
        self.add_rule(Rule(
            name="uncommitted_changes",
            conditions=[
                lambda ctx: ctx.get("files_modified_since_commit", 0) >= 5,
                lambda ctx: ctx.get("active_project") is not None
            ],
            action="suggest_git_commit",
            priority=6,
            description="Many file changes without commit -> suggest committing"
        ))

        # Rule: Error after install -> suggest restart
        self.add_rule(Rule(
            name="post_install_error",
            conditions=[
                lambda ctx: ctx.get("last_action_category") == "install",
                lambda ctx: ctx.get("current_action_failed", False)
            ],
            action="suggest_restart_app",
            priority=7,
            description="Error after install -> suggest restarting the application"
        ))

        # Rule: Same search repeated -> remember it
        self.add_rule(Rule(
            name="repeated_search",
            conditions=[
                lambda ctx: ctx.get("search_repeat_count", 0) >= 2
            ],
            action="offer_bookmark",
            priority=3,
            description="Repeated searches -> offer to create shortcut"
        ))

        # Rule: Battery low + not plugged -> urgent warning
        self.add_rule(Rule(
            name="battery_critical",
            conditions=[
                lambda ctx: ctx.get("system", {}).get("battery_percent", 100) < 15,
                lambda ctx: not ctx.get("system", {}).get("battery_plugged", True)
            ],
            action="urgent_battery_warning",
            priority=10,
            description="Critical battery level"
        ))

    def add_rule(self, rule: Rule):
        """Add a rule to the engine"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def reason(self, context: Dict) -> List[Dict]:
        """
        Run reasoning engine on current context
        Returns list of triggered actions with reasoning
        """
        triggered = []

        for rule in self.rules:
            if rule.evaluate(context):
                action = rule.fire()
                triggered.append({
                    "rule": rule.name,
                    "action": action,
                    "priority": rule.priority,
                    "description": rule.description,
                    "reasoning": f"Rule '{rule.name}' triggered: {rule.description}"
                })

        # Log decisions
        if triggered:
            self.decision_log.append({
                "timestamp": datetime.now().isoformat(),
                "triggered_rules": [t["rule"] for t in triggered],
                "context_snapshot": {k: str(v)[:100] for k, v in context.items()}
            })
            self.decision_log = self.decision_log[-100:]

        return triggered

    def analyze_situation(self, intent: str, entities: Dict, history: List[Dict]) -> Dict:
        """
        Analyze current situation and provide intelligent response guidance
        """
        analysis = {
            "recommended_action": None,
            "warnings": [],
            "suggestions": [],
            "confidence": 0,
            "reasoning": []
        }

        # Check causal predictions
        predictions = self.causal.predict_effect(intent)
        if predictions:
            analysis["reasoning"].append(
                f"Based on past patterns, '{intent}' usually leads to: "
                f"{predictions[0]['effect']} (confidence: {predictions[0]['confidence']}%)"
            )

        # Check for dangerous operations
        dangerous_ops = {"file_delete", "power_shutdown", "power_restart", "kill"}
        if intent in dangerous_ops:
            analysis["warnings"].append(f"This is a potentially destructive operation: {intent}")
            analysis["confidence"] = max(analysis["confidence"], 30)

        # Check for repeated failures
        recent_failures = [h for h in history[-10:] if not h.get("success", True)]
        if len(recent_failures) >= 3:
            last_cmds = [f["command"] for f in recent_failures[-3:]]
            analysis["warnings"].append(f"Recent failures detected: {', '.join(last_cmds[:3])}")
            analysis["suggestions"].append("Consider trying a different approach")

        # File operation safety checks
        if intent == "file_delete" and entities.get("file_path"):
            for path in entities["file_path"]:
                if any(critical in path.lower() for critical in
                       ["system32", "windows", "program files", ".env", ".git"]):
                    analysis["warnings"].append(f"CRITICAL: Attempting to delete protected path: {path}")
                    analysis["confidence"] = 100

        # Provide smart suggestions based on intent
        intent_suggestions = {
            "file_operation": ["Use /find first to locate the exact file",
                               "Check file permissions if operation fails"],
            "git_operation": ["Run git status first to check current state",
                              "Make sure you're in the right branch"],
            "code_execution": ["Backup code before making changes",
                               "Test in a safe environment first"],
            "system_info": ["For detailed info, try specific commands like /cpu, /memory"],
        }
        if intent in intent_suggestions:
            analysis["suggestions"].extend(intent_suggestions[intent])

        return analysis

    def learn_from_outcome(self, action: str, outcome: str, success: bool):
        """Learn from action outcomes for better future decisions"""
        # Record cause-effect
        self.causal.record(action, f"{'success' if success else 'failure'}:{outcome[:50]}")

        # Update knowledge base
        if action not in self.knowledge_base:
            self.knowledge_base[action] = {
                "total": 0, "success": 0, "failure": 0,
                "common_errors": [], "best_practices": []
            }

        kb = self.knowledge_base[action]
        kb["total"] += 1
        if success:
            kb["success"] += 1
        else:
            kb["failure"] += 1
            if outcome and outcome not in kb["common_errors"]:
                kb["common_errors"].append(outcome[:100])
                kb["common_errors"] = kb["common_errors"][-10:]

        self._save_state()

    def get_success_rate(self, action: str) -> Optional[float]:
        """Get historical success rate for an action"""
        if action in self.knowledge_base:
            kb = self.knowledge_base[action]
            if kb["total"] > 0:
                return kb["success"] / kb["total"]
        return None

    def get_decision_summary(self) -> str:
        """Get summary of recent decisions"""
        if not self.decision_log:
            return "No decisions logged yet."

        summary = "**Recent Reasoning Decisions:**\n\n"
        for log in self.decision_log[-10:]:
            summary += f"- {log['timestamp'][:19]}: Rules fired: {', '.join(log['triggered_rules'])}\n"

        # Knowledge base stats
        if self.knowledge_base:
            summary += "\n**Knowledge Base:**\n"
            for action, data in list(self.knowledge_base.items())[:10]:
                rate = (data["success"] / data["total"] * 100) if data["total"] > 0 else 0
                summary += f"- {action}: {data['total']} attempts, {rate:.0f}% success\n"

        return summary

    def get_action_message(self, action: str) -> str:
        """Get a human-readable message for a reasoning action"""
        messages = {
            "suggest_check_processes": "CPU usage is high. Would you like me to show running processes so we can identify what's consuming resources?",
            "suggest_disk_cleanup": "Disk space is running low. Consider running /cleantemp or /emptybin to free up space.",
            "suggest_alternative_approach": "I've noticed the same operation has failed multiple times. Would you like me to try a different approach?",
            "suggest_rest": "It's quite late and you've been working for a while. Consider taking a break.",
            "suggest_git_commit": "You've modified several files without committing. Would you like me to do a git commit?",
            "suggest_restart_app": "Since you just installed something, a restart might help resolve the error.",
            "offer_bookmark": "I notice you search for this frequently. Would you like me to create a shortcut?",
            "urgent_battery_warning": "Battery is critically low! Please plug in your charger immediately.",
        }
        return messages.get(action, f"Reasoning action: {action}")
