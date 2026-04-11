"""
NOVA - Self-Coding System
Collects errors throughout the day, at 6 PM proposes fixes to itself,
asks Yash for approval, then applies fixes using Claude Code.

NOVA literally rewrites its own code to fix bugs it encountered.
"""

import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Callable, Optional

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DailyErrorCollector:
    """Collects all errors and issues NOVA encounters during the day"""

    def __init__(self):
        self.data_dir = os.path.join(BASE_DIR, "self", "daily_errors")
        os.makedirs(self.data_dir, exist_ok=True)
        self.today_file = os.path.join(self.data_dir, f"{datetime.now().strftime('%Y-%m-%d')}.json")
        self.errors = self._load()

    def _load(self) -> list:
        try:
            if os.path.exists(self.today_file):
                with open(self.today_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save(self):
        try:
            with open(self.today_file, 'w', encoding='utf-8') as f:
                json.dump(self.errors, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save errors: {e}")

    def record_error(self, error_type: str, error_msg: str, context: str = "",
                     source_file: str = "", traceback: str = ""):
        """Record an error that occurred during operation"""
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_msg[:500],
            "context": context[:300],
            "source_file": source_file,
            "traceback": traceback[:1000],
        })
        self._save()

    def record_failed_command(self, command: str, error: str, user_message: str = ""):
        """Record a command that failed"""
        self.record_error(
            error_type="command_failure",
            error_msg=f"Command '{command}' failed: {error}",
            context=f"User said: {user_message}",
        )

    def record_classification_miss(self, message: str, expected: str = "", got: str = ""):
        """Record when NOVA misclassified a message"""
        self.record_error(
            error_type="classification_miss",
            error_msg=f"Misclassified: expected '{expected}', got '{got}'",
            context=f"Message: {message}",
            source_file="core/personality.py",
        )

    def record_crash(self, error: str, traceback_str: str = ""):
        """Record a crash/exception"""
        self.record_error(
            error_type="crash",
            error_msg=error,
            traceback=traceback_str,
        )

    def get_today_summary(self) -> dict:
        """Get summary of today's errors"""
        if not self.errors:
            return {"total": 0, "types": {}, "errors": []}

        type_counts = {}
        for e in self.errors:
            t = e["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total": len(self.errors),
            "types": type_counts,
            "errors": self.errors,
        }

    def clear_today(self):
        """Clear today's errors after they've been reviewed"""
        self.errors = []
        self._save()


class SelfCoder:
    """
    NOVA's self-coding brain.
    Analyzes errors, proposes code fixes, and applies them after approval.
    """

    def __init__(self, error_collector: DailyErrorCollector = None):
        self.errors = error_collector or DailyErrorCollector()
        self.proposals_dir = os.path.join(BASE_DIR, "self", "fix_proposals")
        self.pending_proposals = []
        os.makedirs(self.proposals_dir, exist_ok=True)

    def generate_fix_proposals(self) -> List[Dict]:
        """
        Analyze today's errors and generate fix proposals using Claude.
        Called at 6 PM by the proactive monitor.
        """
        summary = self.errors.get_today_summary()
        if summary["total"] == 0:
            return []

        # Group similar errors
        grouped = self._group_errors(summary["errors"])
        proposals = []

        for group_name, errors in grouped.items():
            if len(errors) == 0:
                continue

            # Ask Claude to analyze and propose a fix
            proposal = self._generate_single_proposal(group_name, errors)
            if proposal:
                proposals.append(proposal)

        # Save proposals
        self.pending_proposals = proposals
        self._save_proposals(proposals)

        return proposals

    def _group_errors(self, errors: list) -> dict:
        """Group similar errors together"""
        groups = {}
        for error in errors:
            key = error["type"]
            if error.get("source_file"):
                key += f"_{error['source_file']}"
            if key not in groups:
                groups[key] = []
            groups[key].append(error)
        return groups

    def _generate_single_proposal(self, group_name: str, errors: list) -> Optional[Dict]:
        """Generate a fix proposal for a group of related errors"""
        error_details = "\n".join([
            f"  - [{e['timestamp'][:19]}] {e['message']}"
            + (f"\n    Context: {e['context']}" if e.get('context') else "")
            + (f"\n    File: {e['source_file']}" if e.get('source_file') else "")
            for e in errors[:5]  # Limit to 5 examples
        ])

        prompt = f"""I am NOVA, an AI assistant bot. I encountered these errors today:

Error type: {group_name}
Occurrences: {len(errors)}

Error details:
{error_details}

My codebase is at C:\\code\\NOVA. Key files:
- telegram_bot.py - Main bot handler
- core/personality.py - Claude-powered chat
- core/agent_executor.py - Autonomous task execution
- actions/code_handler.py - Code & GitHub operations
- actions/system_control.py - System commands
- actions/file_ops.py - File operations
- intelligence/powers.py - OCR, PDF, web search

Analyze these errors and propose a specific code fix. Respond in this exact format:

PROBLEM: (one line describing the root cause)
FILE: (which file to fix, relative path)
FIX_DESCRIPTION: (what the fix does, 1-2 sentences)
SEVERITY: (low/medium/high)
RISK: (safe/moderate/risky)

If you can't determine a good fix, respond with: NO_FIX_NEEDED"""

        try:
            result = subprocess.run(
                ["claude", "-p", "--system-prompt",
                 "You are a code debugging expert. Analyze errors and propose specific, safe fixes. Be concise."],
                input=prompt,
                capture_output=True, text=True,
                cwd=BASE_DIR, timeout=30
            )

            if result.returncode == 0 and result.stdout.strip():
                response = result.stdout.strip()

                if "NO_FIX_NEEDED" in response:
                    return None

                return self._parse_proposal(response, group_name, errors)
        except Exception as e:
            logger.error(f"Failed to generate proposal: {e}")

        return None

    def _parse_proposal(self, response: str, group_name: str, errors: list) -> Optional[Dict]:
        """Parse Claude's response into a structured proposal"""
        proposal = {
            "id": f"fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{group_name[:20]}",
            "timestamp": datetime.now().isoformat(),
            "error_group": group_name,
            "error_count": len(errors),
            "problem": "",
            "file": "",
            "fix_description": "",
            "severity": "medium",
            "risk": "safe",
            "status": "pending",  # pending, approved, rejected, applied
            "raw_analysis": response[:2000],
        }

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("PROBLEM:"):
                proposal["problem"] = line[8:].strip()
            elif line.startswith("FILE:"):
                proposal["file"] = line[5:].strip()
            elif line.startswith("FIX_DESCRIPTION:"):
                proposal["fix_description"] = line[16:].strip()
            elif line.startswith("SEVERITY:"):
                sev = line[9:].strip().lower()
                if sev in ("low", "medium", "high"):
                    proposal["severity"] = sev
            elif line.startswith("RISK:"):
                risk = line[5:].strip().lower()
                if risk in ("safe", "moderate", "risky"):
                    proposal["risk"] = risk

        # Must have at least problem and file
        if proposal["problem"] and proposal["file"]:
            return proposal
        return None

    def apply_fix(self, proposal_id: str) -> dict:
        """
        Apply a fix proposal using Claude Code.
        This is the actual self-coding - Claude Code modifies NOVA's own files.
        """
        proposal = None
        for p in self.pending_proposals:
            if p["id"] == proposal_id:
                proposal = p
                break

        if not proposal:
            return {"success": False, "error": "Proposal not found"}

        # Build a targeted prompt for Claude Code to fix the specific issue
        prompt = f"""Fix this specific issue in the NOVA codebase:

Problem: {proposal['problem']}
File to fix: {proposal['file']}
What to do: {proposal['fix_description']}

Error context from today:
{proposal.get('raw_analysis', '')[:1000]}

IMPORTANT:
- Make the MINIMUM change needed to fix this issue
- Do NOT refactor or change anything else
- Do NOT add comments explaining the fix
- Keep the existing code style
- Test that the fix makes sense before applying"""

        try:
            result = subprocess.run(
                ["claude", "-p", "--dangerously-skip-permissions", prompt],
                capture_output=True, text=True,
                cwd=BASE_DIR, timeout=120
            )

            if result.returncode == 0:
                proposal["status"] = "applied"
                proposal["applied_at"] = datetime.now().isoformat()
                proposal["claude_output"] = result.stdout[:2000]
                self._save_proposals(self.pending_proposals)

                return {
                    "success": True,
                    "output": result.stdout[:2000],
                    "proposal": proposal
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr[:500] or "Claude Code failed",
                    "proposal": proposal
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Fix timed out after 120s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def reject_fix(self, proposal_id: str) -> dict:
        """Reject a fix proposal"""
        for p in self.pending_proposals:
            if p["id"] == proposal_id:
                p["status"] = "rejected"
                self._save_proposals(self.pending_proposals)
                return {"success": True}
        return {"success": False, "error": "Proposal not found"}

    def get_pending_proposals(self) -> List[Dict]:
        """Get all pending (unapproved) proposals"""
        return [p for p in self.pending_proposals if p["status"] == "pending"]

    def format_proposal_message(self, proposal: Dict) -> str:
        """Format a proposal for Telegram display"""
        severity_icon = {"low": "Low", "medium": "Medium", "high": "High"}.get(proposal["severity"], "?")
        risk_icon = {"safe": "Safe", "moderate": "Moderate", "risky": "Risky"}.get(proposal["risk"], "?")

        msg = f"**Self-Fix Proposal** [{severity_icon}]\n\n"
        msg += f"**Problem:** {proposal['problem']}\n"
        msg += f"**File:** `{proposal['file']}`\n"
        msg += f"**Fix:** {proposal['fix_description']}\n"
        msg += f"**Errors today:** {proposal['error_count']}\n"
        msg += f"**Risk:** {risk_icon}\n"

        return msg

    def _save_proposals(self, proposals: list):
        """Save proposals to disk"""
        try:
            date = datetime.now().strftime("%Y-%m-%d")
            path = os.path.join(self.proposals_dir, f"{date}_proposals.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(proposals, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save proposals: {e}")
