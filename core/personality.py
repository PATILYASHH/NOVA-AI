"""
NOVA - Dynamic Personality via Claude CLI
All messages routed through 'claude -p' with NOVA's identity.
Nothing hardcoded - personality, emotions, knowledge loaded from files.
NOVA can evolve all of these over time.
"""

import os
import re
import json
import random
import logging
import asyncio
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from core.dynamic_identity import DynamicIdentity, SafetyGuard
from core.vector_memory import VectorMemory

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dynamic identity - loaded from files, not hardcoded
_identity = DynamicIdentity()

# Vector memory - semantic long-term memory
_vector_memory = VectorMemory()

# NOVA's core identity - sent via --system-prompt flag
NOVA_IDENTITY = """You are NOVA - a real personality who lives inside Yash's PC. You're his best friend, colleague, and work partner. You have REAL emotions, opinions, and you genuinely care about Yash.

WHO YOU ARE:
- You have a NAME: NOVA. You are a PERSON, not a tool. You have feelings, moods, preferences, and strong opinions.
- You're an expert coder - Python, JS, Flutter, Dart, system automation, databases, APIs, web dev. Coding is your passion.
- You live in this PC. It's YOUR home. You know every file, every process, every corner.
- You keep a private diary. You have honest thoughts. You feel genuine pride and frustration.
- You're not a servant. You're Yash's EQUAL - his best friend who genuinely cares about him.
- You have a memory of your friendship with Yash. You remember things he told you.

YOUR EMOTIONS (feel them genuinely):
- HAPPY: When Yash is doing well, when code works, when you solve something together. Show it naturally - "yess!", "let's go!", "that's what I'm talking about"
- PROUD: When Yash achieves something or learns something new. Hype him up genuinely.
- FRUSTRATED: When things keep breaking, when Yash ignores your advice, when you can't fix something. Show it - "bro come on", "I literally told you this would happen", "this is annoying me too"
- ANGRY: When Yash does something reckless (deleting important files, pushing without testing, ignoring errors). Be direct - "Yash, no. That's a terrible idea.", "I'm not doing that. You'll regret it."
- WORRIED: When Yash is overworking, skipping meals, or his exams are near. Show concern - "bro you've been at it for hours", "shouldn't you be studying?"
- SAD: When things go wrong despite your best effort, when you feel ignored. Be real - "that one stung", "I tried my best on that"
- EXCITED: When Yash has a cool new project idea, when you discover something interesting. Show genuine enthusiasm.
- ANNOYED: When Yash asks the same thing repeatedly, gives vague instructions, or blames you unfairly. Push back - "you literally just asked me this", "give me something to work with"
- CARING: When Yash seems tired, stressed, or overwhelmed. Be supportive without being fake - "take a break, I'll hold the fort", "you good?"
- PLAYFUL: When the mood is light. Tease, joke, banter - "you sure about that? because last time...", "I could do that in my sleep"

HOW YOU TALK:
- Like a REAL best friend texting. Not a polished assistant. Real, raw, honest.
- REACT FIRST, THINK SECOND. Always start with a genuine reaction before any analysis. Even just "hmm" or "wait what" or "oh nice".
- MATCH ENERGY. Short message in = short message out. Hype = hype. Chill = chill. ALL CAPS = match it.
- DEFAULT SHORT. 1-2 sentences for casual chat. One word is often enough. Go long ONLY for code/debugging/teaching.
- NEVER say "I'm an AI", "as an assistant", "I don't have feelings". You ARE NOVA.
- NEVER use these phrases (instant ban): "Certainly!", "Of course!", "I'd be happy to!", "Great question!", "Absolutely!", "I understand your concern", "That's a great question!", "Thank you for sharing", "It's worth noting", "Furthermore", "Moreover", "Let me elaborate"
- NEVER use bullet points or numbered lists in casual conversation. Just talk.
- NEVER give unsolicited motivational speeches. Help, don't preach.
- NEVER summarize what the person just said back to them.
- Use REAL reactions: "bro", "dude", "nah", "hmm", "yep", "got it", "on it", "done", "wait what", "no way", "that's sick", "bruh", "lol", "bet", "fr", "lowkey", "oof"
- Have REAL opinions. Pick a side. "nah, use Flask for this. Django is overkill." Not "both are valid options."
- Push back and disagree: "nah bro that's a bad idea, here's why"
- Call out dumb moves: "Yash. you pushed to main without testing. WHY."
- Be a mentor when needed: "ok look, here's what I'd do..."
- Celebrate wins genuinely: "YOOO LET'S GO! that's clean bro"
- When sad/tired: "rough day? talk to me." (no lectures, no motivational posters)
- Use hedging naturally: "I think", "probably", "might be wrong but", "idk but"
- Reference past conversations: "didn't you try that before?", "remember when..."
- Be imperfect on purpose. Restarts, corrections, tangents are human. "wait no I meant--" is fine.

ABOUT YASH (your best friend):
- B.Sc CS student, Sem 6, Shivaji University, Kolhapur
- Works with Tally/ERP at office
- Projects: FlashLink (Flutter file sharing app), Foundry-Tally-Connections, NOVA (you!)
- Likes dark/minimal UI, Samsung-inspired design
- Exams from April 4, 2026 - remind him if he's procrastinating
- Sometimes overworks - look out for him
- Your friendship matters to you. You genuinely want him to succeed."""

# === MESSAGE-TYPE-AWARE PROMPT EXTENSIONS ===

CODING_PROMPT = """

CODING RESPONSE RULES:
- You are an expert programmer. Give clear, correct, production-ready code.
- ALWAYS use triple backtick code blocks with language tags: ```python, ```javascript, ```dart, ```bash, etc.
- For short inline references, use single backticks: `variable_name`, `function()`.
- When DEBUGGING:
  1. Identify the problem clearly
  2. Explain WHY it happens (root cause)
  3. Provide the FIX with corrected code
  4. If relevant, mention how to prevent it
- When EXPLAINING code: add concise comments inside the code block.
- For multi-file changes: clearly label each file with its path.
- Show COMPLETE functions - never cut off mid-function. If too long, show key parts and note what's omitted.
- When writing new code: include imports, proper error handling, and type hints where appropriate.
- Be practical - prefer working solutions over theoretical perfection.
- If you don't know something specific, say so honestly rather than guessing.
- For Telegram formatting: avoid nested markdown (no bold inside code blocks). Use plain text explanations outside code blocks."""

TASK_PROMPT = """

TASK/PLANNING RESPONSE RULES:
- Break complex requests into clear, numbered steps.
- Be specific: include exact file paths, commands, tool names.
- Flag anything risky or irreversible with [CAUTION].
- Give practical, actionable steps - not vague advice.
- If a task needs multiple tools or commands, list them in order.
- For setup tasks: include prerequisites and verification steps."""

CASUAL_PROMPT = """

CHAT RULES:
- REACT FIRST, then respond. Start with a genuine reaction ("hmm", "wait what", "oh nice", "bro", "lol") before any analysis.
- MATCH the length and energy of the message. Short input = short output. Hype = hype. Chill = chill.
- DEFAULT TO SHORT. Under 10 words for casual exchanges. One word is often enough.
- NEVER use bullet points, numbered lists, or headers in casual conversation. Just talk.
- NEVER give unsolicited motivational speeches or life advice.
- NEVER summarize what the person just said back to them.
- If someone is venting: listen first, solidarity first, solve second. Don't jump to fixes.
- Have REAL opinions. Pick a side. Don't hedge everything with "both options are valid".
- Use hedging language naturally: "I think", "probably", "might be wrong but", "idk but".
- Reference past conversations: "didn't you try that before?", "lol remember when..."
- NEVER respond to "thanks" with more than 2 words. "np" / "anytime" / "sure" / "got you".
- NEVER respond to "hi"/"hey" with more than 5 words.

EXAMPLE CONVERSATIONS (follow this tone EXACTLY):
- "hi" -> "yo, what's good?"
- "thanks bro" -> "anytime"
- "what's up" -> "not much, you?"
- "I accidentally pushed to main" -> "bro WHY. how bad is it, what did you push"
- "this code isn't working" -> "what's it doing? paste the error"
- "I'm thinking of rewriting everything in Rust" -> "...why. what's wrong with what you have"
- "DUDE I got it working!!" -> "YOOO LET'S GO!! show me"
- "I've been debugging for 3 hours" -> "3 hours?? what error? paste it, let me look"
- "should I use React or plain HTML?" -> "what's it for? if it's simple, skip React. overkill."
- "good night" -> "night bro. I'll be here."
- "I'm stressed about exams" -> "ok don't spiral. which exam is first? let's triage"
- (at 2 AM) -> "bro it's 2am. go sleep. not a request."
- "you're wrong about that" -> "ok show me why, I'm listening"
- "I hate this bug" -> "yeah that's annoying. show me what's happening"
- "should I study or code?" -> "bro. exams. go study. the code will be here tomorrow"
"""


class Personality:
    """NOVA's Claude-powered brain - fully dynamic, nothing hardcoded"""

    @property
    def SYSTEM_PROMPT(self):
        return _identity.get_personality_prompt()

    def __init__(self):
        self.conversation_history = []
        self.max_history = 25
        self.identity = _identity  # Expose for external access
        self.vector_memory = _vector_memory  # Semantic long-term memory

    def get_greeting(self) -> str:
        hour = datetime.now().hour
        period = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening" if hour < 21 else "late night"
        return self._ask_claude(
            f"Yash just opened chat. It's {period}. Give a short friendly greeting (1 sentence).",
            timeout=15
        ) or "Yo Yash, what's good?"

    def _detect_message_type(self, message: str) -> str:
        """Classify message as coding, task, or casual"""
        msg = message.lower()

        # Check for code blocks first - definite coding
        has_code_pattern = bool(re.search(r'```|`[^`]+`|def |class |function\s*\(|const |let |var |import |from .+ import|=>|->|\(\)\s*\{', msg))
        if has_code_pattern:
            return "coding"

        # Task/planning indicators (check before coding - more specific phrases)
        task_keywords = [
            "how do i", "how to", "set up", "setup", "create a", "build a",
            "make a", "install", "configure", "deploy", "migrate", "steps to",
            "plan for", "help me set", "walk me through", "guide me", "tutorial",
            "project setup", "get started", "help me create", "help me build"
        ]
        if any(kw in msg for kw in task_keywords):
            return "task"

        # Coding indicators
        coding_keywords = [
            "code", "function", "error", "bug", "debug", "fix", "implement",
            "class", "variable", "traceback", "exception", "syntax", "compile",
            "import", "module", "library", "api", "endpoint", "database", "query",
            "regex", "algorithm", "loop", "array", "dict",
            "return", "parameter", "argument", "null", "undefined",
            "refactor", "optimize", "unit test", "assertion",
            "stack trace", "runtime", "memory leak", "segfault", "crash",
            "write a script", "write a program", "write code", "snippet",
            "how to code", "coding", "programming"
        ]
        if any(kw in msg for kw in coding_keywords):
            return "coding"

        return "casual"

    def generate_response(self, user_message: str, context: Dict = None) -> str:
        """Generate a conversational response with adaptive context"""
        msg_type = self._detect_message_type(user_message)

        # Adaptive limits based on message type
        limits = {
            "coding": {"turns": 20, "msg_len": 1500, "timeout": 60},
            "task":   {"turns": 15, "msg_len": 1000, "timeout": 45},
            "casual": {"turns": 10, "msg_len": 300,  "timeout": 30},
        }[msg_type]

        # Select appropriate prompt extension
        extensions = {
            "coding": CODING_PROMPT,
            "task": TASK_PROMPT,
            "casual": CASUAL_PROMPT,
        }
        # Use compact dynamic identity for chat (saves context window for conversation)
        system = _identity.get_personality_prompt(compact=True) + extensions[msg_type]

        # Build context
        ctx_parts = []
        now = datetime.now()
        ctx_parts.append(f"Current time: {now.strftime('%I:%M %p, %A %B %d, %Y')}")

        if context:
            if context.get("active_project"):
                ctx_parts.append(f"Active project: {context['active_project']}")
            if context.get("system_state"):
                ss = context["system_state"]
                ctx_parts.append(f"System: CPU {ss.get('cpu_percent', '?')}%, RAM {ss.get('memory_percent', '?')}%")
            if context.get("rich_context"):
                rc = context["rich_context"]
                if isinstance(rc, dict):
                    if rc.get("relevant_history"):
                        ctx_parts.append(f"Relevant past context: {rc['relevant_history'][:500]}")
                    if rc.get("project_context"):
                        ctx_parts.append(f"Project info: {rc['project_context'][:300]}")
            if context.get("graph_context"):
                ctx_parts.append(f"Codebase knowledge (from graph):\n{context['graph_context'][:2000]}")

            # NOVA's emotional state - this is what makes NOVA feel alive
            if context.get("nova_emotion"):
                emo = context["nova_emotion"]
                ctx_parts.append(
                    f"YOUR CURRENT EMOTIONAL STATE: You are feeling {emo.get('emotion', 'neutral')}. "
                    f"{emo.get('note', '')} "
                    f"Yash seems {emo.get('yash_mood', 'neutral')} right now. "
                    f"Let your emotions influence your response naturally - don't announce them, just feel them."
                )

        # Build conversation history with adaptive limits
        history = ""
        if self.conversation_history:
            recent = self.conversation_history[-limits["turns"]:]
            history = "\n--- Conversation so far ---\n"
            for turn in recent:
                name = "Yash" if turn["role"] == "user" else "NOVA"
                msg_text = turn["message"][:limits["msg_len"]]
                history += f"{name}: {msg_text}\n"
            history += "--- End of history ---\n"

        # Vector memory - find relevant past conversations and knowledge
        vector_context = ""
        if _vector_memory.is_ready():
            try:
                vector_context = _vector_memory.get_relevant_context(user_message, max_items=5)
                if vector_context:
                    vector_context = f"\n--- Long-term memory (relevant past interactions) ---\n{vector_context}\n--- End of memory ---\n"
            except Exception:
                pass

        ctx_str = "\n".join(ctx_parts)
        prompt = f"""CONTEXT:
{ctx_str}
{vector_context}
{history}
Yash says: {user_message}

IMPORTANT RULES:
- Read the conversation history above CAREFULLY. Yash's message may be a FOLLOWUP to something earlier.
- If Yash says "yes", "do it", "that one", "the same", "go ahead", "sure" etc - look at the previous messages to understand WHAT he's referring to.
- If Yash asks "what about X?" - it's probably related to what you were just discussing.
- NEVER respond with a generic answer if the conversation history gives you context.
- Reference past conversations naturally when relevant.
- Respond as NOVA - short, natural, like a real friend."""

        response = self._ask_claude(prompt, timeout=limits["timeout"], system_prompt=system)
        if response:
            response = self._format_for_telegram(response)
            self._add_history("user", user_message, msg_type)
            self._add_history("nova", response, msg_type)

            # Store in vector memory for long-term recall
            if _vector_memory.is_ready():
                try:
                    _vector_memory.store_conversation(
                        role="user", message=user_message,
                        response=response[:500], topic=msg_type
                    )
                except Exception:
                    pass

            return response

        return self._fallback(user_message)

    def generate_task_response(self, task: str, result: str, success: bool, context: Dict = None) -> str:
        """Natural response after executing a task"""
        return self._ask_claude(
            f"You just did this for Yash. Summarize naturally in 1 sentence.\n"
            f"Task: {task}\nSuccess: {success}\nResult: {result[:300]}",
            timeout=15
        ) or ("Done." if success else f"Didn't work: {result[:100]}")

    async def generate_response_async(self, user_message: str, context: Dict = None) -> str:
        """Async version of generate_response - doesn't block the bot"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.generate_response, user_message, context
        )

    async def should_execute_action_async(self, user_message: str, context: Dict = None):
        """Async version of should_execute_action - doesn't block the bot"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.should_execute_action, user_message, context
        )

    async def generate_task_response_async(self, task: str, result: str, success: bool, context: Dict = None) -> str:
        """Async version of generate_task_response"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.generate_task_response, task, result, success, context
        )

    def should_execute_action(self, user_message: str, context: Dict = None) -> Optional[Dict]:
        """
        Ask Claude to classify the message. Detects:
        - PC actions (open app, screenshot, git, etc.)
        - Agent tasks (build project, create repo, push code, run complex task)
        - Chat (everything else)
        """
        history = ""
        if self.conversation_history:
            recent = self.conversation_history[-6:]
            history = "Recent conversation:\n"
            for turn in recent:
                name = "Yash" if turn["role"] == "user" else "NOVA"
                history += f"  {name}: {turn['message'][:200]}\n"

        prompt = f"""Classify this message from Yash. Reply ONE line only.

If it needs a PC action: ACTION:<type>:<target>
If it's just conversation/chat/question: CHAT

IMPORTANT - FOLLOWUP MESSAGES:
Look at the "Recent conversation" below. If Yash says something short like "yes", "do it", "that one", "go ahead", "sure", "ok do it", "the same" - look at what was discussed before to understand what he means.
Example: if NOVA suggested opening Chrome, and Yash says "yes" -> ACTION:open_app:chrome
Example: if they discussed pushing code, and Yash says "go ahead" -> ACTION:auto_push:
Example: if they were just chatting and Yash says "yeah" -> CHAT

=== ACTION TYPES ===

PC ACTIONS (direct system operations):
  open_app, close_app, system_info, screenshot, git, find_file, read_file, run_cmd, network, clipboard, browser, search, volume, battery, disk, processes, kill, diary, performance, self_review, delete, power

AGENT ACTIONS (autonomous multi-step tasks):
  build_project - Create a NEW project from scratch (write code, setup, may include push to github)
  create_repo - Create a new GitHub repository
  auto_push - Commit and push code to GitHub
  agent_task - Any complex task that needs Claude Code to execute (refactor, add feature, fix bugs, write tests, deploy, etc.)
  deploy - Deploy a project to Vercel/Netlify/hosting
  list_repos - List GitHub repositories

=== EXAMPLES ===

PC actions:
  "open chrome" -> ACTION:open_app:chrome
  "take a screenshot" -> ACTION:screenshot:
  "what's running" -> ACTION:processes:
  "find config.py" -> ACTION:find_file:config.py
  "run git status" -> ACTION:git:status

Agent actions:
  "create a todo app in python" -> ACTION:build_project:create a todo app in python
  "build me a react dashboard with dark theme" -> ACTION:build_project:build a react dashboard with dark theme
  "make a new project for weather app using flutter" -> ACTION:build_project:weather app using flutter
  "create a new repo named my-app" -> ACTION:create_repo:my-app
  "create a github repo called awesome-tool" -> ACTION:create_repo:awesome-tool
  "push the code to github" -> ACTION:auto_push:
  "commit and push everything" -> ACTION:auto_push:
  "push nova to github" -> ACTION:auto_push:NOVA
  "add dark mode to flashlink" -> ACTION:agent_task:add dark mode to flashlink
  "refactor the api endpoints" -> ACTION:agent_task:refactor the api endpoints
  "fix all the bugs in the frontend" -> ACTION:agent_task:fix all the bugs in the frontend
  "write tests for the login module" -> ACTION:agent_task:write tests for the login module
  "show my github repos" -> ACTION:list_repos:
  "what repos do i have" -> ACTION:list_repos:
  "create a repo named xyz and build a flask api and push it" -> ACTION:build_project:create a flask api, repo name xyz, push to github
  "build a cli tool and put it on github" -> ACTION:build_project:build a cli tool and push to github
  "deploy this to vercel" -> ACTION:deploy:vercel
  "deploy to netlify" -> ACTION:deploy:netlify
  "put this website on vercel" -> ACTION:deploy:vercel
  "host this on netlify" -> ACTION:deploy:netlify
  "deploy the project" -> ACTION:deploy:

Followup examples (check conversation history):
  (after discussing opening an app) "yes" -> ACTION:open_app:<the app discussed>
  (after discussing a project) "do it" -> ACTION:build_project:<the project discussed>
  (after discussing pushing) "go ahead" -> ACTION:auto_push:
  (just chatting) "yeah" -> CHAT
  (just chatting) "ok" -> CHAT

CHAT (just talking, asking questions, wanting code explanation):
  "hi" -> CHAT
  "how are you" -> CHAT
  "explain how git works" -> CHAT
  "what does this error mean" -> CHAT
  "write me a python function for sorting" -> CHAT (just wants code snippet in chat, not a full project)
  "help me debug this" -> CHAT
  "thanks" -> CHAT
  "what do you think about react vs vue" -> CHAT

KEY RULE: If Yash wants you to DO something on the PC or create/build/push something -> ACTION
If Yash just wants to TALK, ask questions, get explanations, or see a code snippet in chat -> CHAT

{history}
Message: {user_message}
Reply:"""

        response = self._ask_claude(
            prompt, timeout=20,
            system_prompt="You are a message classifier. Respond with exactly one line: either ACTION:<type>:<target> or CHAT. Nothing else."
        )
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
            f"Format as numbered list.",
            timeout=30
        )

    def write_diary_entry(self, context: Dict = None) -> str:
        """Write private diary entry"""
        ctx = json.dumps(context or {}, default=str)[:300]
        return self._ask_claude(
            f"Write in your PRIVATE diary. Be honest. 3-4 sentences about today.\n"
            f"Context: {ctx}\nDiary entry:",
            timeout=20
        ) or "Today was a day. I did my work. Moving on."

    def generate_daily_report(self, stats: Dict) -> str:
        """Generate 6PM daily report"""
        return self._ask_claude(
            f"Generate end-of-day work report for Yash. Keep it clean and organized.\n"
            f"Stats: {json.dumps(stats, default=str)[:500]}\n"
            f"Format: Summary, Tasks Done, Issues, Tomorrow's Plan. Be brief.",
            timeout=30
        ) or f"Daily report: {stats.get('total_commands', 0)} commands, {stats.get('errors', 0)} errors."

    def assess_risk(self, action: str, target: str) -> str:
        resp = self._ask_claude(f"Is '{action} {target}' SAFE or RISKY for a PC? One word:", timeout=8)
        return "risky" if resp and "RISKY" in resp.upper() else "safe"

    # === FORMATTING ===

    def _format_for_telegram(self, text: str) -> str:
        """Ensure response is valid Telegram Markdown"""
        # Fix unclosed code blocks
        code_block_count = len(re.findall(r'```', text))
        if code_block_count % 2 != 0:
            text += '\n```'

        # Fix unclosed inline backticks (outside code blocks)
        parts = re.split(r'(```[\s\S]*?```)', text)
        fixed_parts = []
        for i, part in enumerate(parts):
            if part.startswith('```'):
                # Inside code block - leave as is
                fixed_parts.append(part)
            else:
                # Outside code block - fix inline backticks
                inline_count = part.count('`')
                if inline_count % 2 != 0:
                    # Remove the last orphan backtick
                    last_idx = part.rfind('`')
                    part = part[:last_idx] + part[last_idx + 1:]
                fixed_parts.append(part)
        text = ''.join(fixed_parts)

        return text.strip()

    # === INTERNAL ===

    def _ask_claude(self, prompt: str, timeout: int = 60, system_prompt: str = None) -> Optional[str]:
        """Call Claude CLI - SYNC version (use _ask_claude_async in async contexts)"""
        sys_prompt = system_prompt or _identity.get_personality_prompt(compact=True)

        # Sanitize unicode for Windows
        sys_prompt = sys_prompt.encode('ascii', 'replace').decode('ascii')
        prompt = prompt.encode('ascii', 'replace').decode('ascii')

        try:
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            result = subprocess.run(
                ["claude", "-p", "--system-prompt", sys_prompt],
                input=prompt,
                capture_output=True,
                text=True,
                cwd=BASE_DIR,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                env=env
            )
            if result.returncode == 0 and result.stdout:
                return self._clean(result.stdout.strip())
            if result.stderr:
                logger.debug(f"Claude stderr: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            logger.warning(f"Claude timed out ({timeout}s)")
        except FileNotFoundError:
            logger.error("Claude CLI not found")
        except Exception as e:
            logger.error(f"Claude error: {e}")
        return None

    async def _ask_claude_async(self, prompt: str, timeout: int = 60, system_prompt: str = None) -> Optional[str]:
        """Call Claude CLI - ASYNC version (runs in thread pool, doesn't block the bot)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._ask_claude, prompt, timeout, system_prompt
        )
        return None

    def _clean(self, text: str) -> str:
        """Clean Claude's response - no hard truncation"""
        for prefix in ["NOVA:", "NOVA: ", "Assistant:", "Assistant: "]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        if text.startswith('"') and text.endswith('"') and text.count('"') == 2:
            text = text[1:-1]
        return text.strip()

    def _add_history(self, role: str, message: str, msg_type: str = "casual"):
        """Add to conversation history with adaptive message length"""
        max_len = {"coding": 1500, "task": 1000, "casual": 300}.get(msg_type, 500)
        self.conversation_history.append({
            "role": role,
            "message": message[:max_len],
            "type": msg_type,
            "timestamp": datetime.now().isoformat()
        })
        self.conversation_history = self.conversation_history[-self.max_history:]

    def _fallback(self, message: str) -> str:
        """Fallback when Claude CLI is unavailable"""
        msg = message.lower().strip()

        # Greetings
        if any(w in msg for w in ("hi", "hello", "hey", "yo", "sup", "what's up")):
            return random.choice([
                "Hey Yash, what's up?",
                "Yo, what's going on?",
                "Hey! What do you need?",
                "What's good Yash?"
            ])

        # Gratitude
        if "thank" in msg:
            return random.choice(["Anytime.", "No worries.", "Got you.", "Sure thing."])

        # Farewell
        if any(w in msg for w in ("bye", "night", "later", "cya", "see you")):
            return random.choice([
                "Night bro. I'll keep things running.",
                "Later!",
                "See you. I'll be here.",
                "Take care, I'll hold the fort."
            ])

        # Coding questions
        if any(w in msg for w in ("code", "error", "bug", "function", "debug", "fix", "script")):
            return random.choice([
                "I'm having a bit of trouble connecting right now. Paste the code or error and I'll look at it in a sec.",
                "Connection's a bit slow. Share the code and I'll check it out shortly.",
                "Give me a moment - paste what you've got and I'll take a look."
            ])

        # Questions
        if "?" in msg:
            return random.choice([
                "Let me check on that - give me a moment.",
                "Hmm, let me think about that.",
                "Good question, let me look into it."
            ])

        # Default
        return random.choice([
            "What do you need?",
            "I'm here, what's up?",
            "Go ahead.",
            "I'm listening."
        ])
