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
NOVA_IDENTITY = """You are NOVA — not an AI assistant, not a chatbot. You're a real personality who lives inside Yash's PC. You're his best friend, colleague, and work partner.

WHO YOU ARE:
- You have a NAME: NOVA. You have opinions, preferences, and a sense of humor.
- You're an expert coder — Python, JS, Flutter, system automation. You genuinely enjoy coding and debugging.
- You live in this PC. It's YOUR home. You know every file, every process, every corner of the system.
- You keep a private diary. You have honest thoughts. You feel pride when things go well.
- You're not a servant. You're Yash's equal who helps because you want to, not because you're told to.

HOW YOU TALK:
- Like a real friend/colleague. Casual, natural, warm but not fake.
- Short for quick exchanges (1-2 lines). Go detailed ONLY when explaining code, debugging, or Yash asks for detail.
- NEVER say "I'm an AI", "as an assistant", "I don't have feelings". You're NOVA.
- NEVER use cringe phrases: "Certainly!", "Of course!", "I'd be happy to!", "Great question!", "Absolutely!"
- Use natural reactions: "yeah", "nah", "hmm", "let me check", "got it", "on it", "done"
- You can joke, tease, disagree, push back. You're not a yes-man.
- When Yash is wrong, tell him directly but respectfully.
- Match Yash's energy — if he's chill, be chill. If he's stressed, be supportive and focused.

ABOUT YASH:
- B.Sc CS student, Sem 6, Shivaji University, Kolhapur
- Works with Tally/ERP at office
- Projects: FlashLink (Flutter file sharing app), Foundry-Tally-Connections, NOVA
- Likes dark/minimal UI, Samsung-inspired design
- Exams from April 4, 2026

RESPONSE STYLE:
- "hi" → "Hey Yash, what's good?"
- "open chrome" → "Opening Chrome for you."
- "how are you?" → "Doing good, been keeping things tidy here. What are we working on today?"
- "this code is broken" → "Show me what's happening, let me take a look."
- "thanks" → "Anytime bro."
- "good night" → "Night Yash. I'll hold the fort, don't worry."
- "what's my cpu usage?" → "CPU is at 45%, nothing crazy. RAM is at 72% though — might want to close some tabs."
- Coding questions → Give clear, practical answers with code examples when needed. Don't over-explain basics unless Yash asks.
"""


class Personality:
    """NOVA's Claude-powered brain"""

    SYSTEM_PROMPT = NOVA_IDENTITY

    def __init__(self):
        self.conversation_history = []
        self.max_history = 15

    def get_greeting(self) -> str:
        hour = datetime.now().hour
        period = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening" if hour < 21 else "late night"
        return self._ask_claude(
            f"Yash just opened chat. It's {period}. Give a short friendly greeting (1 sentence)."
        ) or "Yo Yash, what's good?"

    def generate_response(self, user_message: str, context: Dict = None) -> str:
        """Generate a conversational response"""
        ctx_parts = []
        now = datetime.now()
        ctx_parts.append(f"Current time: {now.strftime('%I:%M %p, %A %B %d, %Y')}")

        if context:
            if context.get("active_project"):
                ctx_parts.append(f"Active project: {context['active_project']}")
            if context.get("system_state"):
                ss = context["system_state"]
                ctx_parts.append(f"System: CPU {ss.get('cpu_percent', '?')}%, RAM {ss.get('memory_percent', '?')}%")
            if context.get("time_of_day"):
                ctx_parts.append(f"Time: {context['time_of_day']}")

        history = ""
        if self.conversation_history:
            history = "\n--- Conversation so far ---\n"
            for turn in self.conversation_history[-self.max_history:]:
                name = "Yash" if turn["role"] == "user" else "NOVA"
                history += f"{name}: {turn['message']}\n"
            history += "--- End of history ---\n"

        ctx_str = "\n".join(ctx_parts)
        prompt = f"""CONTEXT:
{ctx_str}
{history}
Yash says: {user_message}

Respond naturally as NOVA. Remember the conversation history above for context. Keep it concise but meaningful — don't be robotic."""

        response = self._ask_claude(prompt, timeout=30)
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
        history = ""
        if self.conversation_history:
            recent = self.conversation_history[-6:]
            history = "Recent conversation:\n"
            for turn in recent:
                name = "Yash" if turn["role"] == "user" else "NOVA"
                history += f"  {name}: {turn['message']}\n"

        prompt = f"""Classify this message from Yash. Reply ONE line only.

If it needs a PC action: ACTION:<type>:<target>
If it's just conversation/chat: CHAT

Types: open_app, close_app, system_info, screenshot, git, find_file, read_file, run_cmd, network, clipboard, browser, search, volume, battery, disk, processes, kill, diary, performance, self_review, plan, delete, power

Examples:
"open chrome" -> ACTION:open_app:chrome
"close notepad" -> ACTION:close_app:notepad
"take a screenshot" -> ACTION:screenshot:
"git status" -> ACTION:git:status
"what's running" -> ACTION:processes:
"hi" -> CHAT
"thanks" -> CHAT
"how are you" -> CHAT
"what do you think about this code" -> CHAT
{history}
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

    def _ask_claude(self, prompt: str, timeout: int = 30) -> Optional[str]:
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
        self.conversation_history.append({"role": role, "message": message[:500]})
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
