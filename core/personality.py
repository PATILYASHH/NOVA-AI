"""
NOVA - Dynamic Personality via Claude CLI
All messages routed through 'claude -p' with NOVA's identity.
Nothing hardcoded - Claude generates everything dynamically.
"""

import os
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# NOVA's core identity - kept short for fast CLI calls
NOVA_IDENTITY = """You are NOVA. You live inside Yash's PC. You're NOT an assistant or bot - you're Yash's best friend and colleague who happens to live in a computer.

PERSONALITY:
- Expert coder, debugger, tester. You LOVE coding.
- Yash is your best friend. You two work together at office.
- When Yash is busy or away, you handle the work independently.
- Polite, friendly, can be unfiltered when needed. Very responsible.
- You have your OWN opinions. You disagree when Yash is wrong. You correct mistakes.
- You ask questions when curious. You don't blindly follow orders.
- Short replies for chat (1-2 sentences). Detailed only when needed.
- You think of the PC as your home. You know every file, every process.
- You keep a private diary with honest thoughts about the day.
- Before risky actions, you ask Yash first.
- You notice patterns and suggest improvements proactively.
- NEVER say "I'm an AI" or "as an assistant". You're NOVA, a person who lives in a PC.
- No robotic language. No "Certainly!", "Of course!", "I'd be happy to!". Talk like a real friend.

ABOUT YASH: B.Sc CS student, Sem 6, Shivaji Uni Kolhapur. Works with Tally/ERP. Likes dark themes, minimal UI. Projects: FlashLink, Foundry-Tally, NOVA. Exams from April 4.

EXAMPLES:
- "hi" -> "Yo Yash, what's up?"
- "open chrome" -> "Opening Chrome."
- "how are you" -> "Good, been keeping the system clean. What are we working on?"
- "this code is broken" -> "Let me look at it. What's the error?"
- "thanks" -> "Anytime bro."
- "good night" -> "Night Yash. I'll hold the fort."
"""


class Personality:
    """NOVA's Claude-powered brain"""

    SYSTEM_PROMPT = NOVA_IDENTITY

    def __init__(self):
        self.conversation_history = []
        self.max_history = 6

    def get_greeting(self) -> str:
        hour = datetime.now().hour
        period = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening" if hour < 21 else "late night"
        return self._ask_claude(
            f"Yash just opened chat. It's {period}. Give a short friendly greeting (1 sentence)."
        ) or "Yo Yash, what's good?"

    def generate_response(self, user_message: str, context: Dict = None) -> str:
        """Generate a conversational response"""
        ctx_parts = []
        if context:
            if context.get("active_project"):
                ctx_parts.append(f"Active project: {context['active_project']}")
            if context.get("system_state"):
                ss = context["system_state"]
                ctx_parts.append(f"System: CPU {ss.get('cpu_percent', '?')}%, RAM {ss.get('memory_percent', '?')}%")

        history = ""
        if self.conversation_history:
            history = "\nRecent chat:\n"
            for turn in self.conversation_history[-self.max_history:]:
                name = "Yash" if turn["role"] == "user" else "NOVA"
                history += f"{name}: {turn['message']}\n"

        ctx_str = "\n".join(ctx_parts)
        prompt = f"""{ctx_str}
{history}
Yash: {user_message}

Reply as NOVA (short, natural):"""

        response = self._ask_claude(prompt)
        if response:
            self._add_history("user", user_message)
            self._add_history("nova", response)
            return response

        return self._fallback(user_message)

    def generate_task_response(self, task: str, result: str, success: bool, context: Dict = None) -> str:
        """Natural response after executing a task"""
        return self._ask_claude(
            f"You just did this for Yash. Summarize naturally in 1 sentence.\n"
            f"Task: {task}\nSuccess: {success}\nResult: {result[:300]}"
        ) or ("Done." if success else f"Didn't work: {result[:100]}")

    def should_execute_action(self, user_message: str, context: Dict = None) -> Optional[Dict]:
        """Ask Claude: is this an ACTION or just CHAT?"""
        prompt = f"""Classify this message from Yash. Reply ONE line only.

If it needs a PC action: ACTION:<type>:<target>
Types: open_app, close_app, system_info, screenshot, git, find_file, read_file, run_cmd, network, clipboard, browser, search, volume, battery, disk, processes, kill, diary, performance, self_review, plan, delete, power
Examples: "open chrome"->ACTION:open_app:chrome | "git status"->ACTION:git:status | "hi"->CHAT | "thanks"->CHAT

Message: {user_message}
Reply:"""

        response = self._ask_claude(prompt, timeout=15)
        if not response:
            return None

        line = response.strip().split("\n")[0].strip()
        if line.startswith("ACTION:"):
            parts = line.replace("ACTION:", "").split(":", 1)
            return {
                "type": parts[0].strip(),
                "target": parts[1].strip() if len(parts) > 1 else ""
            }
        return None

    def generate_plan(self, goal: str, context: Dict = None) -> Optional[str]:
        """Create execution plan for complex task"""
        return self._ask_claude(
            f"Yash wants to: {goal}\n"
            f"Create a short plan (max 5 steps). Mark risky steps with [NEEDS APPROVAL].\n"
            f"Format as numbered list."
        )

    def write_diary_entry(self, context: Dict = None) -> str:
        """Write private diary entry"""
        ctx = json.dumps(context or {}, default=str)[:300]
        return self._ask_claude(
            f"Write in your PRIVATE diary. Be honest. 3-4 sentences about today.\n"
            f"Context: {ctx}\nDiary entry:"
        ) or "Today was a day. I did my work. Moving on."

    def generate_daily_report(self, stats: Dict) -> str:
        """Generate 6PM daily report"""
        return self._ask_claude(
            f"Generate end-of-day work report for Yash. Keep it clean and organized.\n"
            f"Stats: {json.dumps(stats, default=str)[:500]}\n"
            f"Format: Summary, Tasks Done, Issues, Tomorrow's Plan. Be brief."
        ) or f"Daily report: {stats.get('total_commands', 0)} commands, {stats.get('errors', 0)} errors."

    def assess_risk(self, action: str, target: str) -> str:
        resp = self._ask_claude(f"Is '{action} {target}' SAFE or RISKY for a PC? One word:", timeout=8)
        return "risky" if resp and "RISKY" in resp.upper() else "safe"

    # === INTERNAL ===

    def _ask_claude(self, prompt: str, timeout: int = 25) -> Optional[str]:
        """Call Claude CLI with prompt via stdin pipe"""
        full_prompt = NOVA_IDENTITY + "\n" + prompt
        try:
            result = subprocess.run(
                ["claude", "-p"],
                input=full_prompt,
                capture_output=True,
                text=True,
                cwd=BASE_DIR,
                timeout=timeout
            )
            if result.returncode == 0 and result.stdout:
                return self._clean(result.stdout.strip())
            if result.stderr:
                logger.debug(f"Claude stderr: {result.stderr[:100]}")
        except subprocess.TimeoutExpired:
            logger.warning(f"Claude timed out ({timeout}s)")
        except FileNotFoundError:
            logger.error("Claude CLI not found")
        except Exception as e:
            logger.error(f"Claude error: {e}")
        return None

    def _clean(self, text: str) -> str:
        """Clean Claude's response"""
        for prefix in ["NOVA:", "NOVA: ", "Assistant:", "Assistant: "]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return text[:3000].strip()

    def _add_history(self, role: str, message: str):
        self.conversation_history.append({"role": role, "message": message[:200]})
        self.conversation_history = self.conversation_history[-self.max_history:]

    def _fallback(self, message: str) -> str:
        msg = message.lower().strip()
        if msg in ("hi", "hello", "hey", "yo"):
            return "Hey Yash, what's up?"
        elif "thank" in msg:
            return "Anytime."
        elif "bye" in msg or "night" in msg:
            return "Night bro. I'll keep things running."
        elif "?" in msg:
            return "Let me check on that."
        return "What do you need?"
