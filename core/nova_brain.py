"""
NOVA - Core Intelligence Module (AGI-Enhanced)
Integrates all intelligence engines into a unified brain
Handles personality, reasoning, context-awareness, and decision making
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import NOVA_PERSONALITY, MEMORY_FILE

logger = logging.getLogger(__name__)


class NovaBrain:
    """
    NOVA's core brain - integrates all intelligence modules
    NLP -> Context -> Reasoning -> Emotion -> Response
    """

    def __init__(self):
        self.name = NOVA_PERSONALITY["name"]
        self.owner = NOVA_PERSONALITY["owner"]
        self.personality = NOVA_PERSONALITY
        self.context = []
        self.load_memory()

        # Intelligence modules (initialized externally to avoid circular imports)
        self.nlp = None
        self.reasoning = None
        self.context_engine = None
        self.emotion = None
        self.learning = None
        self.planner = None

    def init_intelligence(self, nlp, reasoning, context_engine, emotion, learning, planner):
        """Initialize intelligence modules (called after all modules are created)"""
        self.nlp = nlp
        self.reasoning = reasoning
        self.context_engine = context_engine
        self.emotion = emotion
        self.learning = learning
        self.planner = planner
        logger.info("NOVA Brain: All intelligence modules connected")

    def load_memory(self):
        """Load NOVA's persistent memory"""
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                self.memory = f.read()
        except FileNotFoundError:
            self.memory = ""
            self.save_memory("# NOVA Memory\n\nInitialized: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def save_memory(self, content: str):
        """Save to NOVA's persistent memory"""
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                f.write(content)
            self.memory = content
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def append_memory(self, entry: str):
        """Append an entry to memory"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = f"\n\n## {timestamp}\n{entry}"
        self.save_memory(self.memory + new_entry)

    def process_message(self, message: str) -> Dict:
        """
        Full intelligence pipeline for processing a message
        Returns structured understanding + response guidance
        """
        result = {
            "original_message": message,
            "timestamp": datetime.now().isoformat(),
        }

        # Step 1: NLP Processing
        if self.nlp:
            nlp_result = self.nlp.process(message)
            result["nlp"] = nlp_result
            result["intent"] = nlp_result["primary_intent"]
            result["confidence"] = nlp_result["intent_confidence"]
            result["entities"] = nlp_result["entities"]
            result["action"] = nlp_result["action"]
            result["target"] = nlp_result["target"]
            result["is_question"] = nlp_result["is_question"]
            result["urgency"] = nlp_result["urgency"]
        else:
            # Fallback to basic intent parsing
            basic = self.parse_intent(message)
            result["nlp"] = None
            result["intent"] = basic["intents"][0] if basic["intents"] else "general"
            result["confidence"] = 30
            result["entities"] = {}
            result["action"] = None
            result["target"] = None
            result["is_question"] = "?" in message
            result["urgency"] = "normal"

        # Step 2: Emotion Detection
        if self.emotion:
            mood = self.emotion.detect_mood(message)
            result["mood"] = mood
            result["user_mood"] = mood["mood"]
        else:
            result["mood"] = None
            result["user_mood"] = "neutral"

        # Step 3: Context Building
        if self.context_engine:
            context = self.context_engine.build_context(message, result.get("nlp", {}))
            result["context"] = context
            result["is_followup"] = context.get("is_followup", False)
        else:
            result["context"] = {}
            result["is_followup"] = False

        # Step 4: Reasoning
        if self.reasoning:
            reasoning_context = {
                "intent": result["intent"],
                "entities": result["entities"],
                "user_mood": result["user_mood"],
                "session_duration_minutes": result.get("context", {}).get("session_duration_minutes", 0),
                "system": result.get("context", {}).get("system_state", {}),
            }
            triggered_rules = self.reasoning.reason(reasoning_context)
            result["reasoning"] = triggered_rules

            # Situation analysis
            history = result.get("context", {}).get("relevant_history", [])
            analysis = self.reasoning.analyze_situation(
                result["intent"], result["entities"], history
            )
            result["analysis"] = analysis
        else:
            result["reasoning"] = []
            result["analysis"] = {}

        # Step 5: Learning guidance
        if self.learning:
            before_guidance = self.learning.before_action(message)
            result["learning_guidance"] = before_guidance
        else:
            result["learning_guidance"] = {}

        # Step 6: Generate response prefix if needed
        if self.context_engine and result.get("nlp"):
            prefix = self.context_engine.generate_response_prefix(
                result["nlp"], result.get("context", {})
            )
            result["response_prefix"] = prefix
        else:
            result["response_prefix"] = None

        # Step 7: Emotional prefix
        if self.emotion:
            empathetic_prefix = self.emotion.get_empathetic_prefix()
            if empathetic_prefix and not result.get("response_prefix"):
                result["response_prefix"] = empathetic_prefix

        return result

    def post_process(self, action: str, result_text: str, success: bool):
        """
        Called after an action is executed - feeds back into learning
        """
        # Update emotion
        if self.emotion:
            self.emotion.record_action_outcome(success)

        # Update learning
        if self.learning:
            self.learning.record_action(action, result_text, success)
            feedback = self.learning.after_action(action, result_text, success)
            return feedback

        # Update reasoning
        if self.reasoning:
            self.reasoning.learn_from_outcome(action, result_text, success)

        # Update context
        if self.context_engine:
            self.context_engine.update_session(action, result_text, success)

        return {}

    def format_response(self, message: str, status: str = "success") -> str:
        """Format NOVA's response with personality and emotional awareness"""
        if status == "error":
            if self.emotion and self.emotion.failure_streak >= 3:
                return f"I apologize for the repeated issues. Error: {message}\n\nLet me try a different approach."
            return f"I encountered an issue: {message}\n\nLet me know if you'd like me to try a different approach."
        elif status == "working":
            return f"Working on it... {message}"
        elif status == "confirm":
            return f"Just to confirm before I proceed: {message}"
        else:
            # Apply emotion-based adaptation
            if self.emotion:
                message = self.emotion.adapt_response(message)
            return message

    def get_greeting(self) -> str:
        """Get context-aware greeting"""
        if self.context_engine:
            return self.context_engine.get_smart_greeting()

        hour = datetime.now().hour
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"

        return f"{time_greeting}, {self.owner}. NOVA online and ready. What can I handle for you?"

    def parse_intent(self, message: str) -> dict:
        """Legacy intent parsing - used as fallback (matches NLP engine intent names)"""
        message_lower = message.lower()

        intents = {
            "file_operation": ["open file", "read file", "create file", "delete file", "find file", "show file"],
            "code_execution": ["write code", "edit code", "run code", "debug", "fix bug", "create script"],
            "app_control": ["open", "close", "start", "stop", "run", "execute", "launch"],
            "system_info": ["status", "info", "show", "list", "what", "how", "check"],
            "clipboard": ["copy", "paste", "clipboard"],
            "git_operation": ["git", "commit", "push", "pull", "branch"],
            "browser": ["browse", "search", "google", "open url", "website"],
            "screenshot": ["screenshot", "capture screen", "screen capture"],
            "greeting": ["hello", "hi", "hey", "good morning", "good evening"],
            "help": ["help", "what can you do", "commands"]
        }

        detected_intents = []
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_intents.append(intent)

        return {
            "raw_message": message,
            "intents": detected_intents if detected_intents else ["general"],
            "timestamp": datetime.now().isoformat()
        }

    def get_help_message(self) -> str:
        """Return NOVA's capabilities"""
        return """**NOVA - AI Office Assistant (AGI-Enhanced)**

**Intelligence Features:**
- Natural language understanding
- Context-aware responses
- Mood detection & empathetic responses
- Pattern learning & predictions
- Anomaly detection
- Smart automation & macros
- Goal planning & multi-step execution
- Self-reflection & performance tracking

**Commands:** Use /help for full command list.

**Smart Features:**
- Just talk to me naturally - I understand context
- I learn from patterns and adapt
- I'll proactively suggest when I notice something
- I remember what works and what doesn't

*Your intelligent office assistant.*"""

    def get_intelligence_status(self) -> str:
        """Get status of all intelligence modules"""
        status = "**NOVA Intelligence Status**\n\n"

        modules = {
            "NLP Engine": self.nlp,
            "Reasoning Engine": self.reasoning,
            "Context Engine": self.context_engine,
            "Emotion Engine": self.emotion,
            "Learning Loop": self.learning,
            "Goal Planner": self.planner,
        }

        for name, module in modules.items():
            state = "Online" if module else "Offline"
            status += f"- **{name}:** {state}\n"

        return status
