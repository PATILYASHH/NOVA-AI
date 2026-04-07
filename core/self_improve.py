"""
NOVA - Self-Improvement Engine
NOVA reviews its own performance, identifies weaknesses,
generates code patches, applies them, and tracks all changes.

This is the core AGI feature: NOVA improves itself.
"""

import os
import re
import json
import logging
import shutil
import difflib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SelfImprovementLog:
    """Track every self-improvement change NOVA makes"""

    def __init__(self):
        self.log_dir = os.path.join(BASE_DIR, "self", "improvements")
        self.log_file = os.path.join(self.log_dir, "changelog.json")
        self.entries = []
        os.makedirs(self.log_dir, exist_ok=True)
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.entries = json.load(f)
        except Exception:
            self.entries = []

    def _save(self):
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save improvement log: {e}")

    def add_entry(self, change_type: str, file_path: str, description: str,
                  reason: str, before: str = "", after: str = "",
                  performance_impact: str = "", success: bool = True):
        """Log a self-improvement change"""
        entry = {
            "id": len(self.entries) + 1,
            "timestamp": datetime.now().isoformat(),
            "type": change_type,
            "file": file_path,
            "description": description,
            "reason": reason,
            "before_snippet": before[:500] if before else "",
            "after_snippet": after[:500] if after else "",
            "performance_impact": performance_impact,
            "success": success,
            "reverted": False,
        }
        self.entries.append(entry)
        self._save()

        # Also write human-readable log
        self._write_readable_log(entry)
        return entry

    def _write_readable_log(self, entry: Dict):
        """Write human-readable improvement log"""
        date = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"{date}_improvements.md")

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## Improvement #{entry['id']} - {entry['timestamp'][:19]}\n\n")
            f.write(f"**Type:** {entry['type']}\n")
            f.write(f"**File:** `{entry['file']}`\n")
            f.write(f"**What changed:** {entry['description']}\n")
            f.write(f"**Why:** {entry['reason']}\n")
            if entry['performance_impact']:
                f.write(f"**Expected impact:** {entry['performance_impact']}\n")
            if entry['before_snippet']:
                f.write(f"\n**Before:**\n```\n{entry['before_snippet']}\n```\n")
            if entry['after_snippet']:
                f.write(f"\n**After:**\n```\n{entry['after_snippet']}\n```\n")
            f.write(f"\n**Success:** {'Yes' if entry['success'] else 'No'}\n")
            f.write("\n---\n")

    def revert_entry(self, entry_id: int) -> bool:
        """Mark an entry as reverted"""
        for entry in self.entries:
            if entry["id"] == entry_id:
                entry["reverted"] = True
                self._save()
                return True
        return False

    def get_recent(self, count: int = 10) -> List[Dict]:
        return self.entries[-count:]

    def get_stats(self) -> Dict:
        total = len(self.entries)
        successful = sum(1 for e in self.entries if e["success"])
        reverted = sum(1 for e in self.entries if e.get("reverted"))
        types = Counter(e["type"] for e in self.entries)
        return {
            "total_improvements": total,
            "successful": successful,
            "failed": total - successful,
            "reverted": reverted,
            "by_type": dict(types),
        }


class CodePatcher:
    """Safely apply code patches to NOVA's own files"""

    def __init__(self):
        self.backup_dir = os.path.join(BASE_DIR, "self", "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def backup_file(self, file_path: str) -> str:
        """Create backup before modification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_path = os.path.join(self.backup_dir, f"{filename}.{timestamp}.bak")
        shutil.copy2(file_path, backup_path)
        return backup_path

    def restore_file(self, file_path: str, backup_path: str) -> bool:
        """Restore file from backup"""
        try:
            shutil.copy2(backup_path, file_path)
            return True
        except Exception as e:
            logger.error(f"Failed to restore {file_path}: {e}")
            return False

    def apply_patch(self, file_path: str, old_text: str, new_text: str) -> Dict:
        """Apply a text replacement patch to a file"""
        result = {"success": False, "backup": None, "error": None}

        full_path = file_path if os.path.isabs(file_path) else os.path.join(BASE_DIR, file_path)

        if not os.path.exists(full_path):
            result["error"] = f"File not found: {full_path}"
            return result

        try:
            # Read current content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Verify old_text exists
            if old_text not in content:
                result["error"] = "Target text not found in file"
                return result

            # Count occurrences - only replace if exactly one match
            count = content.count(old_text)
            if count > 1:
                result["error"] = f"Target text found {count} times, need exactly 1 for safe patching"
                return result

            # Create backup
            result["backup"] = self.backup_file(full_path)

            # Apply patch
            new_content = content.replace(old_text, new_text, 1)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            result["success"] = True
            return result

        except Exception as e:
            result["error"] = str(e)
            # Try to restore from backup
            if result.get("backup"):
                self.restore_file(full_path, result["backup"])
            return result

    def add_to_file(self, file_path: str, content: str, position: str = "end") -> Dict:
        """Add content to a file (end, start, or after a marker)"""
        result = {"success": False, "backup": None, "error": None}

        full_path = file_path if os.path.isabs(file_path) else os.path.join(BASE_DIR, file_path)

        if not os.path.exists(full_path):
            result["error"] = f"File not found: {full_path}"
            return result

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                existing = f.read()

            result["backup"] = self.backup_file(full_path)

            if position == "end":
                new_content = existing + "\n" + content
            elif position == "start":
                new_content = content + "\n" + existing
            else:
                # position is a marker string - add after it
                if position in existing:
                    new_content = existing.replace(position, position + "\n" + content, 1)
                else:
                    new_content = existing + "\n" + content

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            result["success"] = True
            return result

        except Exception as e:
            result["error"] = str(e)
            if result.get("backup"):
                self.restore_file(full_path, result["backup"])
            return result

    def get_diff(self, old_text: str, new_text: str) -> str:
        """Generate a readable diff"""
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)
        diff = difflib.unified_diff(old_lines, new_lines, fromfile='before', tofile='after')
        return ''.join(diff)


class SelfReviewAnalyzer:
    """Analyze NOVA's performance to find areas for self-improvement"""

    def __init__(self):
        self.analysis_file = os.path.join(BASE_DIR, "self", "improvements", "analysis.json")

    def analyze_performance(self, performance_data: Dict, learnings_data: Dict,
                            error_patterns: Dict, command_stats: Dict) -> List[Dict]:
        """
        Analyze performance data and identify improvement opportunities
        Returns list of improvement actions
        """
        improvements = []

        # 1. Analyze error patterns - find recurring errors
        for error_type, data in error_patterns.items():
            if data.get("count", 0) >= 3:
                improvements.append({
                    "type": "error_pattern",
                    "severity": "high" if data["count"] >= 5 else "medium",
                    "description": f"Recurring error: {error_type} ({data['count']} times)",
                    "suggestion": self._suggest_error_fix(error_type, data),
                    "auto_fixable": self._is_auto_fixable(error_type),
                    "target_module": self._identify_target_module(error_type, data),
                })

        # 2. Analyze command success rates
        for cmd, stats in command_stats.items():
            total = stats.get("total", 0)
            success = stats.get("success", 0)
            if total >= 5 and (success / total) < 0.7:
                improvements.append({
                    "type": "low_success_rate",
                    "severity": "medium",
                    "description": f"Command '{cmd}' has {success/total*100:.0f}% success rate",
                    "suggestion": f"Add better validation or error handling for '{cmd}'",
                    "auto_fixable": True,
                    "target_module": "core/learning_loop.py",
                })

        # 3. Analyze response quality
        if performance_data.get("commands_failed", 0) > performance_data.get("commands_successful", 0):
            improvements.append({
                "type": "overall_quality",
                "severity": "high",
                "description": "More commands failing than succeeding today",
                "suggestion": "Review error handling and add better pre-validation",
                "auto_fixable": False,
                "target_module": "core/nova_brain.py",
            })

        # 4. Check for missing intent handling
        # If many messages fall to "general" intent, NLP needs improvement
        improvements.append({
            "type": "nlp_coverage",
            "severity": "low",
            "description": "Check NLP intent coverage",
            "suggestion": "Add new keywords/patterns for commonly missed intents",
            "auto_fixable": True,
            "target_module": "core/nlp_engine.py",
        })

        return improvements

    def _suggest_error_fix(self, error_type: str, data: Dict) -> str:
        fixes = {
            "permission_denied": "Add permission check before file/system operations",
            "not_found": "Add path validation and suggest alternatives when file not found",
            "timeout": "Increase timeout or add progress feedback for long operations",
            "connection_error": "Add retry logic with exponential backoff for network operations",
            "syntax_error": "Add input validation before executing commands",
            "memory_error": "Add memory check before large operations",
            "disk_error": "Check disk space before write operations",
            "process_error": "Add process existence check before kill/interact operations",
        }
        return fixes.get(error_type, f"Add error handling for {error_type}")

    def _is_auto_fixable(self, error_type: str) -> bool:
        auto_fixable = {"not_found", "timeout", "connection_error"}
        return error_type in auto_fixable

    def _identify_target_module(self, error_type: str, data: Dict) -> str:
        """Identify which module needs fixing"""
        triggers = data.get("triggers", [])
        trigger_str = " ".join(str(t) for t in triggers).lower()

        if "file" in trigger_str or "cat" in trigger_str or "ls" in trigger_str:
            return "actions/file_ops.py"
        elif "git" in trigger_str:
            return "actions/code_handler.py"
        elif "open" in trigger_str or "close" in trigger_str:
            return "actions/system_control.py"
        elif "network" in trigger_str or "wifi" in trigger_str:
            return "actions/advanced_control.py"
        return "telegram_bot.py"


class SelfImproveEngine:
    """
    NOVA's self-improvement engine
    Reviews performance -> identifies weaknesses -> generates fixes -> applies them
    """

    def __init__(self, reflection_system=None, learning_loop=None):
        self.reflection = reflection_system
        self.learning = learning_loop
        self.log = SelfImprovementLog()
        self.patcher = CodePatcher()
        self.analyzer = SelfReviewAnalyzer()
        self.pending_improvements = []
        self.applied_today = []
        logger.info("Self-Improvement Engine initialized")

    def run_self_review(self) -> Dict:
        """
        Run a complete self-review cycle
        1. Gather performance data
        2. Analyze for weaknesses
        3. Generate improvement suggestions
        4. Apply auto-fixable improvements
        5. Log everything
        """
        review = {
            "timestamp": datetime.now().isoformat(),
            "analysis": [],
            "improvements_found": 0,
            "auto_applied": 0,
            "manual_needed": 0,
            "details": [],
        }

        # Gather data
        performance = {}
        error_patterns = {}
        command_stats = {}
        learnings = {}

        if self.reflection:
            perf = self.reflection.performance
            performance = {
                "commands_executed": perf.data.get("commands_executed", 0),
                "commands_successful": perf.data.get("commands_successful", 0),
                "commands_failed": perf.data.get("commands_failed", 0),
                "errors": len(perf.data.get("errors_encountered", [])),
                "mistakes": len(perf.data.get("mistakes", [])),
            }

        if self.learning:
            error_patterns = self.learning.profile.error_patterns
            command_stats = self.learning.profile.command_success_rates

        # Analyze
        improvements = self.analyzer.analyze_performance(
            performance, learnings, error_patterns, command_stats
        )

        review["improvements_found"] = len(improvements)
        self.pending_improvements = improvements

        # Apply auto-fixable improvements
        for imp in improvements:
            if imp.get("auto_fixable"):
                result = self._apply_improvement(imp)
                if result["applied"]:
                    review["auto_applied"] += 1
                    review["details"].append(result)
                    self.applied_today.append(result)
            else:
                review["manual_needed"] += 1

        # Write review to diary
        if self.reflection:
            self.reflection.diary.write_entry(
                f"Self-review completed. Found {review['improvements_found']} areas. "
                f"Auto-applied {review['auto_applied']} fixes. "
                f"{review['manual_needed']} need manual review.",
                mood="analytical"
            )

        return review

    def _apply_improvement(self, improvement: Dict) -> Dict:
        """Apply a single improvement"""
        result = {
            "improvement": improvement,
            "applied": False,
            "change_description": "",
            "error": None,
        }

        imp_type = improvement["type"]
        target = improvement.get("target_module", "")

        try:
            if imp_type == "error_pattern":
                result = self._fix_error_pattern(improvement, target)
            elif imp_type == "low_success_rate":
                result = self._fix_low_success(improvement)
            elif imp_type == "nlp_coverage":
                result = self._improve_nlp_coverage()
            else:
                result["error"] = f"No auto-fix handler for type: {imp_type}"

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Self-improvement failed: {e}")

        return result

    def _fix_error_pattern(self, improvement: Dict, target_module: str) -> Dict:
        """Fix a recurring error pattern by adding better error handling"""
        result = {"improvement": improvement, "applied": False, "change_description": "", "error": None}

        error_type = improvement["description"].split(":")[0].replace("Recurring error", "").strip()

        # Generate a new error solution entry in learning loop
        if self.learning:
            solution = self.analyzer._suggest_error_fix(error_type,
                self.learning.profile.error_patterns.get(error_type, {}))

            # Add the solution to known solutions
            if error_type in self.learning.profile.error_patterns:
                patterns = self.learning.profile.error_patterns[error_type]
                if solution not in patterns.get("solutions", []):
                    if "solutions" not in patterns:
                        patterns["solutions"] = []
                    patterns["solutions"].append(solution)
                    self.learning._save()

                    result["applied"] = True
                    result["change_description"] = f"Added solution for {error_type}: {solution}"

                    self.log.add_entry(
                        change_type="error_solution",
                        file_path="intelligence/data/learning_loop.json",
                        description=f"Added automatic solution for recurring error: {error_type}",
                        reason=f"Error occurred {patterns.get('count', 0)} times without solution",
                        performance_impact="NOVA will now suggest fix when this error recurs",
                    )

        return result

    def _fix_low_success(self, improvement: Dict) -> Dict:
        """Fix low success rate by adding pre-validation"""
        result = {"improvement": improvement, "applied": False, "change_description": "", "error": None}

        # Extract command from description
        desc = improvement["description"]
        cmd_match = re.search(r"Command '(.+?)' has", desc)
        if not cmd_match:
            return result

        cmd = cmd_match.group(1)

        # Add to learning loop's known problematic commands
        if self.learning:
            profile = self.learning.profile
            if cmd in profile.command_success_rates:
                stats = profile.command_success_rates[cmd]
                # Add a warning flag
                stats["needs_confirmation"] = True
                self.learning._save()

                result["applied"] = True
                result["change_description"] = f"Flagged '{cmd}' for confirmation before execution"

                self.log.add_entry(
                    change_type="command_flag",
                    file_path="intelligence/data/learning_loop.json",
                    description=f"Flagged unreliable command for user confirmation: {cmd}",
                    reason=f"Success rate below 70% after 5+ attempts",
                    performance_impact="User will be warned before running this command",
                )

        return result

    def _improve_nlp_coverage(self) -> Dict:
        """Analyze missed intents and add new patterns"""
        result = {"improvement": {"type": "nlp_coverage"}, "applied": False,
                  "change_description": "", "error": None}

        # Check if we have enough data to improve NLP
        if not self.learning:
            return result

        # Look at commands that were categorized as "general"
        general_commands = []
        for cmd, stats in self.learning.profile.command_success_rates.items():
            if stats.get("total", 0) >= 3:
                general_commands.append(cmd)

        if not general_commands:
            return result

        # Record that we analyzed NLP coverage
        self.log.add_entry(
            change_type="nlp_analysis",
            file_path="core/nlp_engine.py",
            description=f"Analyzed NLP coverage: {len(general_commands)} frequently used commands tracked",
            reason="Periodic NLP coverage check",
            performance_impact="Better intent detection over time",
        )

        result["applied"] = True
        result["change_description"] = f"Analyzed {len(general_commands)} command patterns"
        return result

    def add_new_intent_keywords(self, intent: str, new_keywords: List[str]) -> Dict:
        """Add new keywords to NLP engine for better intent detection"""
        target_file = os.path.join(BASE_DIR, "core", "nlp_engine.py")

        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find the intent in INTENT_PATTERNS
            pattern = f'"{intent}": {{'
            if pattern not in content:
                return {"success": False, "error": f"Intent '{intent}' not found in NLP engine"}

            # Find the keywords list for this intent
            import ast
            # Simple approach: find the keywords line and add to it
            lines = content.split('\n')
            in_intent = False
            keywords_line_idx = None

            for i, line in enumerate(lines):
                if f'"{intent}"' in line and '{' in line:
                    in_intent = True
                elif in_intent and '"keywords"' in line:
                    keywords_line_idx = i
                    break
                elif in_intent and '}' in line and '"' not in line:
                    in_intent = False

            if keywords_line_idx is None:
                return {"success": False, "error": "Could not find keywords line"}

            old_line = lines[keywords_line_idx]
            # Add new keywords before the closing bracket
            for kw in new_keywords:
                if f'"{kw}"' not in old_line:
                    old_line = old_line.rstrip().rstrip('],')
                    old_line += f', "{kw}"],'

            backup = self.patcher.backup_file(target_file)
            lines[keywords_line_idx] = old_line

            with open(target_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            self.log.add_entry(
                change_type="nlp_keywords",
                file_path="core/nlp_engine.py",
                description=f"Added keywords to '{intent}': {new_keywords}",
                reason="Self-improvement: detected frequently used words not in NLP patterns",
                before=lines[keywords_line_idx],
                after=old_line,
                performance_impact=f"Better detection of {intent} intent",
            )

            return {"success": True, "added": new_keywords, "backup": backup}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_custom_response(self, trigger: str, response: str) -> Dict:
        """Add a custom response pattern"""
        responses_file = os.path.join(BASE_DIR, "intelligence", "data", "custom_responses.json")

        try:
            responses = {}
            if os.path.exists(responses_file):
                with open(responses_file, 'r', encoding='utf-8') as f:
                    responses = json.load(f)

            responses[trigger.lower()] = {
                "response": response,
                "added_at": datetime.now().isoformat(),
                "use_count": 0,
            }

            os.makedirs(os.path.dirname(responses_file), exist_ok=True)
            with open(responses_file, 'w', encoding='utf-8') as f:
                json.dump(responses, f, indent=2)

            self.log.add_entry(
                change_type="custom_response",
                file_path="intelligence/data/custom_responses.json",
                description=f"Added custom response for trigger: '{trigger}'",
                reason="Self-improvement or user request",
                performance_impact="Better response matching",
            )

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_reasoning_rule(self, name: str, condition_desc: str,
                           action: str, priority: int = 5) -> Dict:
        """Add a new reasoning rule (saved to data file for persistence)"""
        rules_file = os.path.join(BASE_DIR, "intelligence", "data", "custom_rules.json")

        try:
            rules = []
            if os.path.exists(rules_file):
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rules = json.load(f)

            rules.append({
                "name": name,
                "condition": condition_desc,
                "action": action,
                "priority": priority,
                "added_at": datetime.now().isoformat(),
                "added_by": "self_improvement",
                "fire_count": 0,
            })

            os.makedirs(os.path.dirname(rules_file), exist_ok=True)
            with open(rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules, f, indent=2)

            self.log.add_entry(
                change_type="reasoning_rule",
                file_path="intelligence/data/custom_rules.json",
                description=f"Added reasoning rule: {name} -> {action}",
                reason=condition_desc,
                performance_impact=f"NOVA will now react when: {condition_desc}",
            )

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def revert_last_change(self) -> Dict:
        """Revert the most recent self-improvement change"""
        recent = self.log.get_recent(1)
        if not recent:
            return {"success": False, "error": "No changes to revert"}

        entry = recent[0]
        # We can only revert file patches that have backups
        backup_dir = self.patcher.backup_dir
        if not os.path.exists(backup_dir):
            return {"success": False, "error": "No backups found"}

        # Find most recent backup
        backups = sorted(os.listdir(backup_dir), reverse=True)
        if backups:
            latest_backup = os.path.join(backup_dir, backups[0])
            original_name = backups[0].split('.')[0] + '.py'
            # Find the original file
            for root, dirs, files in os.walk(BASE_DIR):
                if original_name in files:
                    original_path = os.path.join(root, original_name)
                    if self.patcher.restore_file(original_path, latest_backup):
                        self.log.revert_entry(entry["id"])
                        return {"success": True, "reverted": entry["description"]}

        return {"success": False, "error": "Could not find matching backup"}

    def get_improvement_report(self) -> str:
        """Get formatted improvement report"""
        stats = self.log.get_stats()
        recent = self.log.get_recent(10)

        text = "**NOVA Self-Improvement Report**\n\n"
        text += f"**Total Improvements:** {stats['total_improvements']}\n"
        text += f"**Successful:** {stats['successful']}\n"
        text += f"**Failed:** {stats['failed']}\n"
        text += f"**Reverted:** {stats['reverted']}\n\n"

        if stats['by_type']:
            text += "**By Type:**\n"
            for t, count in stats['by_type'].items():
                text += f"  - {t}: {count}\n"

        if recent:
            text += "\n**Recent Changes:**\n"
            for entry in recent:
                status = "Reverted" if entry.get("reverted") else ("OK" if entry["success"] else "FAIL")
                text += f"\n[{status}] #{entry['id']} - {entry['description'][:60]}\n"
                text += f"  Reason: {entry['reason'][:60]}\n"
                text += f"  File: `{entry['file']}`\n"

        if self.pending_improvements:
            text += f"\n**Pending Improvements:** {len(self.pending_improvements)}\n"
            for imp in self.pending_improvements[:5]:
                text += f"  - [{imp['severity']}] {imp['description'][:60]}\n"

        return text

    def get_changelog(self, days: int = 7) -> str:
        """Get changelog of recent improvements"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        recent = [e for e in self.log.entries if e["timestamp"] >= cutoff]

        if not recent:
            return f"No self-improvements in the last {days} days."

        text = f"**NOVA Self-Improvement Changelog (Last {days} Days)**\n\n"
        for entry in recent:
            text += f"**#{entry['id']}** [{entry['type']}] {entry['timestamp'][:10]}\n"
            text += f"  {entry['description']}\n"
            text += f"  Why: {entry['reason']}\n\n"

        return text
