"""
NOVA - Natural Language Processing Engine
Advanced NLU without external APIs - fuzzy matching, entity extraction,
sentiment analysis, context-aware intent parsing
"""

import re
import os
import json
import logging
from datetime import datetime
from difflib import SequenceMatcher, get_close_matches
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class FuzzyMatcher:
    """Fuzzy string matching for commands and entities"""

    @staticmethod
    def similarity(a: str, b: str) -> float:
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    @staticmethod
    def best_match(query: str, candidates: List[str], threshold: float = 0.6) -> Optional[Tuple[str, float]]:
        """Find best matching candidate"""
        best = None
        best_score = 0
        for candidate in candidates:
            score = SequenceMatcher(None, query.lower(), candidate.lower()).ratio()
            if score > best_score and score >= threshold:
                best = candidate
                best_score = score
        return (best, best_score) if best else None

    @staticmethod
    def close_matches(query: str, candidates: List[str], n: int = 3, cutoff: float = 0.5) -> List[str]:
        """Get close matches from candidates"""
        return get_close_matches(query.lower(), [c.lower() for c in candidates], n=n, cutoff=cutoff)


class EntityExtractor:
    """Extract entities from natural language text"""

    # Patterns for common entities
    PATTERNS = {
        "file_path": [
            r'[A-Za-z]:\\(?:[^\s\\/:*?"<>|]+\\)*[^\s\\/:*?"<>|]+',  # Windows path
            r'/(?:[^\s/]+/)*[^\s/]+\.[a-zA-Z0-9]+',  # Unix path
            r'[a-zA-Z0-9_-]+\.[a-zA-Z0-9]+',  # filename.ext
        ],
        "url": [
            r'https?://[^\s<>"{}|\\^`\[\]]+',
            r'www\.[^\s<>"{}|\\^`\[\]]+',
        ],
        "ip_address": [
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        ],
        "email": [
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        ],
        "number": [
            r'\b\d+(?:\.\d+)?\b',
        ],
        "time_expression": [
            r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b',
            r'\b(?:today|tomorrow|yesterday|next\s+\w+|last\s+\w+)\b',
            r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\bin\s+\d+\s+(?:minutes?|hours?|days?|weeks?|months?)\b',
        ],
        "app_name": [
            r'\b(?:chrome|firefox|edge|vscode|vs\s*code|visual\s*studio|notepad|word|excel|'
            r'powerpoint|outlook|teams|slack|discord|telegram|spotify|vlc|'
            r'cmd|terminal|powershell|explorer|task\s*manager|calculator|'
            r'paint|photoshop|git|python|node|npm|pip)\b',
        ],
        "git_operation": [
            r'\b(?:commit|push|pull|merge|branch|checkout|stash|rebase|log|diff|status|clone|fetch|reset)\b',
        ],
        "programming_language": [
            r'\b(?:python|javascript|js|typescript|ts|java|c\+\+|cpp|csharp|c#|'
            r'ruby|go|rust|php|swift|kotlin|dart|powershell|bash|batch|sql|html|css)\b',
        ],
    }

    # Action verbs and their categories
    ACTION_VERBS = {
        "open": "launch", "start": "launch", "launch": "launch", "run": "launch",
        "close": "terminate", "stop": "terminate", "kill": "terminate", "quit": "terminate", "exit": "terminate",
        "read": "file_read", "show": "file_read", "display": "file_read", "cat": "file_read", "view": "file_read",
        "write": "file_write", "create": "file_write", "save": "file_write", "make": "file_write",
        "delete": "file_delete", "remove": "file_delete", "erase": "file_delete",
        "find": "search", "search": "search", "look": "search", "locate": "search", "where": "search",
        "copy": "file_copy", "move": "file_move", "rename": "file_move",
        "install": "install", "setup": "install", "configure": "install",
        "update": "update", "upgrade": "update",
        "download": "download", "fetch": "download", "get": "download",
        "upload": "upload", "send": "upload",
        "screenshot": "capture", "capture": "capture", "snap": "capture",
        "commit": "git", "push": "git", "pull": "git", "merge": "git", "branch": "git",
        "help": "help", "assist": "help",
        "status": "info", "info": "info", "check": "info",
        "schedule": "schedule", "remind": "schedule", "alarm": "schedule", "timer": "schedule",
        "analyze": "analyze", "scan": "analyze", "inspect": "analyze",
        "backup": "backup", "restore": "backup",
        "connect": "network", "ping": "network", "network": "network",
    }

    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extract all entities from text"""
        entities = {}
        for entity_type, patterns in self.PATTERNS.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                matches.extend(found)
            if matches:
                entities[entity_type] = list(set(matches))
        return entities

    def extract_action(self, text: str) -> Optional[Dict]:
        """Extract primary action verb and its category"""
        words = text.lower().split()
        for i, word in enumerate(words):
            if word in self.ACTION_VERBS:
                return {
                    "verb": word,
                    "category": self.ACTION_VERBS[word],
                    "position": i
                }
        return None

    def extract_target(self, text: str, action_pos: int = 0) -> Optional[str]:
        """Extract the target/object of an action"""
        words = text.split()
        if action_pos + 1 < len(words):
            # Skip common prepositions/articles
            skip_words = {"the", "a", "an", "to", "in", "on", "at", "for", "my", "this", "that"}
            target_parts = []
            for word in words[action_pos + 1:]:
                if word.lower() in skip_words and not target_parts:
                    continue
                target_parts.append(word)
            return " ".join(target_parts) if target_parts else None
        return None


class SentimentAnalyzer:
    """Simple rule-based sentiment analysis"""

    POSITIVE_WORDS = {
        "good", "great", "excellent", "awesome", "perfect", "nice", "thanks",
        "thank", "wonderful", "amazing", "love", "like", "helpful", "cool",
        "brilliant", "fantastic", "superb", "well", "done", "yes", "correct",
        "right", "exactly", "please", "appreciate", "happy", "glad", "satisfied"
    }

    NEGATIVE_WORDS = {
        "bad", "wrong", "error", "fail", "hate", "terrible", "awful", "poor",
        "broken", "bug", "crash", "slow", "useless", "stupid", "no", "not",
        "never", "annoying", "frustrated", "angry", "disappointed", "worse",
        "worst", "ugly", "fix", "problem", "issue", "complaint"
    }

    URGENCY_WORDS = {
        "urgent", "asap", "immediately", "now", "quickly", "fast", "hurry",
        "critical", "emergency", "important", "priority", "rush"
    }

    QUESTION_PATTERNS = [
        r'^(?:what|where|when|who|why|how|which|is|are|do|does|can|could|would|will|shall|should)\b',
        r'\?$',
    ]

    def analyze(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        words = set(text.lower().split())

        positive_count = len(words & self.POSITIVE_WORDS)
        negative_count = len(words & self.NEGATIVE_WORDS)
        urgency_count = len(words & self.URGENCY_WORDS)

        # Determine overall sentiment
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(positive_count / max(len(words), 1), 1.0)
        elif negative_count > positive_count:
            sentiment = "negative"
            score = -min(negative_count / max(len(words), 1), 1.0)
        else:
            sentiment = "neutral"
            score = 0.0

        # Check if it's a question
        is_question = any(re.search(p, text.strip(), re.IGNORECASE) for p in self.QUESTION_PATTERNS)

        # Determine urgency
        if urgency_count > 0:
            urgency = "high"
        elif any(c == '!' for c in text):
            urgency = "medium"
        else:
            urgency = "normal"

        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "is_question": is_question,
            "urgency": urgency,
            "positive_words": list(words & self.POSITIVE_WORDS),
            "negative_words": list(words & self.NEGATIVE_WORDS),
        }


class IntentClassifier:
    """Advanced intent classification using pattern matching and scoring"""

    INTENT_PATTERNS = {
        "file_operation": {
            "keywords": ["file", "folder", "directory", "read", "write", "create", "delete",
                         "copy", "move", "rename", "find", "search", "list", "ls", "cat",
                         "open file", "save", "path", "content"],
            "patterns": [r'(?:read|write|create|delete|find|show|list|copy|move)\s+(?:file|folder|dir)',
                         r'(?:what|show).*(?:in|inside)\s+(?:the\s+)?(?:folder|directory)',
                         r'(?:cat|ls|find)\s+'],
            "weight": 1.0,
        },
        "app_control": {
            "keywords": ["open", "close", "start", "stop", "launch", "run", "kill",
                         "application", "app", "program", "software"],
            "patterns": [r'(?:open|close|start|stop|launch|kill)\s+\w+',
                         r'(?:is|are)\s+\w+\s+(?:running|open)'],
            "weight": 1.0,
        },
        "system_info": {
            "keywords": ["status", "cpu", "memory", "ram", "disk", "battery", "system",
                         "performance", "usage", "info", "temperature", "processes"],
            "patterns": [r'(?:how|what).*(?:cpu|memory|ram|disk|battery|system)',
                         r'(?:system|pc|computer)\s+(?:status|info|health)'],
            "weight": 1.0,
        },
        "code_execution": {
            "keywords": ["code", "script", "execute", "compile", "debug", "python",
                         "javascript", "powershell", "program", "function"],
            "patterns": [r'(?:run|execute|write)\s+(?:code|script|program)',
                         r'(?:python|js|javascript|powershell|batch)\s+(?:code|script)'],
            "weight": 1.0,
        },
        "git_operation": {
            "keywords": ["git", "commit", "push", "pull", "merge", "branch", "repository",
                         "repo", "clone", "checkout", "stash", "diff", "log"],
            "patterns": [r'git\s+\w+', r'(?:commit|push|pull|merge|branch|checkout)\s+'],
            "weight": 1.0,
        },
        "network": {
            "keywords": ["network", "wifi", "internet", "ip", "dns", "ping", "connection",
                         "download", "upload", "bandwidth", "speed"],
            "patterns": [r'(?:network|wifi|internet|connection)\s+(?:status|info|speed)',
                         r'(?:ip|dns)\s+(?:address|info)'],
            "weight": 1.0,
        },
        "clipboard": {
            "keywords": ["clipboard", "copy", "paste", "copied"],
            "patterns": [r'(?:what|show).*clipboard', r'(?:copy|paste)\s+'],
            "weight": 1.0,
        },
        "screenshot": {
            "keywords": ["screenshot", "screen", "capture", "snap", "screen shot"],
            "patterns": [r'(?:take|capture|get)\s+(?:a\s+)?screenshot'],
            "weight": 1.2,
        },
        "browser": {
            "keywords": ["browse", "browser", "website", "url", "web", "google", "search online"],
            "patterns": [r'(?:open|go\s+to|browse)\s+(?:website|url|http)',
                         r'(?:google|search\s+for|look\s+up)\s+'],
            "weight": 1.0,
        },
        "schedule": {
            "keywords": ["schedule", "remind", "reminder", "alarm", "timer", "later",
                         "at", "every", "daily", "weekly", "cron"],
            "patterns": [r'(?:remind|schedule|set\s+(?:alarm|timer|reminder))',
                         r'(?:at|every|in)\s+\d+\s+(?:minutes?|hours?|days?)'],
            "weight": 1.0,
        },
        "greeting": {
            "keywords": ["hello", "hi", "hey", "good morning", "good afternoon",
                         "good evening", "howdy", "sup", "yo", "greetings"],
            "patterns": [r'^(?:hi|hello|hey|howdy|yo|greetings)\b'],
            "weight": 0.8,
        },
        "gratitude": {
            "keywords": ["thanks", "thank you", "appreciate", "grateful", "thx"],
            "patterns": [r'^(?:thanks?|thank\s+you|thx|appreciate)'],
            "weight": 0.8,
        },
        "help": {
            "keywords": ["help", "how to", "what can", "guide", "tutorial", "explain",
                         "how do", "commands", "features"],
            "patterns": [r'(?:help|how\s+(?:to|do|can))', r'what\s+can\s+you\s+do'],
            "weight": 0.9,
        },
        "automation": {
            "keywords": ["automate", "macro", "workflow", "chain", "sequence", "batch",
                         "repeat", "loop", "then", "after that", "and then"],
            "patterns": [r'(?:automate|create\s+(?:macro|workflow))',
                         r'(?:first|then|after\s+that|and\s+then|next)\s+'],
            "weight": 1.1,
        },
        "analysis": {
            "keywords": ["analyze", "report", "summary", "statistics", "trends",
                         "patterns", "insights", "review", "evaluate"],
            "patterns": [r'(?:analyze|report|summarize|show\s+(?:stats|trends|patterns))'],
            "weight": 1.0,
        },
    }

    def classify(self, text: str, context: Dict = None) -> List[Dict]:
        """Classify text into intents with confidence scores"""
        text_lower = text.lower()
        words = set(text_lower.split())
        scored_intents = []

        for intent_name, intent_data in self.INTENT_PATTERNS.items():
            score = 0.0

            # Keyword matching (weighted)
            keyword_matches = sum(1 for kw in intent_data["keywords"]
                                  if kw in text_lower)
            if keyword_matches:
                score += (keyword_matches / len(intent_data["keywords"])) * 50

            # Pattern matching (higher weight)
            pattern_matches = sum(1 for p in intent_data["patterns"]
                                  if re.search(p, text_lower))
            if pattern_matches:
                score += (pattern_matches / len(intent_data["patterns"])) * 40

            # Apply intent weight
            score *= intent_data["weight"]

            # Context bonus - if this intent matches recent context
            if context and context.get("last_intent") == intent_name:
                score += 10

            if score > 5:  # Minimum threshold
                scored_intents.append({
                    "intent": intent_name,
                    "confidence": min(round(score, 1), 100),
                    "keyword_hits": keyword_matches,
                    "pattern_hits": pattern_matches,
                })

        # Sort by confidence
        scored_intents.sort(key=lambda x: x["confidence"], reverse=True)
        return scored_intents[:5] if scored_intents else [{"intent": "general", "confidence": 10, "keyword_hits": 0, "pattern_hits": 0}]


class ConversationTracker:
    """Track conversation context and multi-turn dialogue"""

    def __init__(self):
        self.turns = []
        self.topic_stack = []  # Stack of active topics
        self.pending_clarification = None
        self.slot_filling = {}  # For multi-turn slot filling

    def add_turn(self, role: str, message: str, intent: str = None, entities: Dict = None):
        """Add a conversation turn"""
        self.turns.append({
            "role": role,
            "message": message,
            "intent": intent,
            "entities": entities or {},
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 20 turns
        self.turns = self.turns[-20:]

        if intent and intent != "general":
            self.topic_stack.append(intent)
            self.topic_stack = self.topic_stack[-5:]

    def get_current_topic(self) -> Optional[str]:
        """Get the current conversation topic"""
        return self.topic_stack[-1] if self.topic_stack else None

    def get_context_for_response(self) -> Dict:
        """Get relevant context for generating response"""
        recent = self.turns[-5:] if self.turns else []
        return {
            "recent_turns": recent,
            "current_topic": self.get_current_topic(),
            "turn_count": len(self.turns),
            "pending_clarification": self.pending_clarification,
            "slot_filling": self.slot_filling,
        }

    def needs_clarification(self, intent: str, entities: Dict, required_entities: List[str]) -> Optional[str]:
        """Check if we need to ask for clarification"""
        missing = [e for e in required_entities if e not in entities]
        if missing:
            self.pending_clarification = {
                "intent": intent,
                "missing": missing,
                "collected": entities
            }
            return missing[0]
        self.pending_clarification = None
        return None

    def resolve_pronoun(self, text: str) -> str:
        """Resolve pronouns like 'it', 'that', 'this' to their referents"""
        pronouns = {"it", "that", "this", "those", "these", "them"}
        words = text.lower().split()

        if not any(p in words for p in pronouns):
            return text

        # Look back for the most recent entity mentioned
        for turn in reversed(self.turns):
            if turn["role"] == "user" and turn.get("entities"):
                for entity_type, values in turn["entities"].items():
                    if values:
                        # Replace first pronoun with the entity
                        for pronoun in pronouns:
                            if pronoun in text.lower():
                                return text.replace(pronoun, values[0], 1)
        return text


class NLPEngine:
    """
    Main NLP Engine - integrates all NLP components
    This is NOVA's language understanding core
    """

    def __init__(self):
        self.fuzzy = FuzzyMatcher()
        self.entity_extractor = EntityExtractor()
        self.sentiment = SentimentAnalyzer()
        self.intent_classifier = IntentClassifier()
        self.conversation = ConversationTracker()
        logger.info("NLP Engine initialized")

    def process(self, text: str, context: Dict = None) -> Dict:
        """
        Full NLP pipeline - process user input
        Returns structured understanding of the message
        """
        # Step 1: Resolve pronouns from conversation context
        resolved_text = self.conversation.resolve_pronoun(text)

        # Step 2: Extract entities
        entities = self.entity_extractor.extract(resolved_text)

        # Step 3: Extract action
        action = self.entity_extractor.extract_action(resolved_text)

        # Step 4: Extract target
        target = None
        if action:
            target = self.entity_extractor.extract_target(resolved_text, action["position"])

        # Step 5: Classify intent
        intents = self.intent_classifier.classify(resolved_text, context)
        primary_intent = intents[0] if intents else {"intent": "general", "confidence": 0}

        # Step 6: Analyze sentiment
        sentiment = self.sentiment.analyze(text)

        # Step 7: Check for pending clarifications
        clarification_context = None
        if self.conversation.pending_clarification:
            pc = self.conversation.pending_clarification
            if pc["intent"] == primary_intent["intent"]:
                # User might be providing missing info
                clarification_context = pc

        # Step 8: Track conversation
        self.conversation.add_turn("user", text, primary_intent["intent"], entities)

        return {
            "original_text": text,
            "resolved_text": resolved_text,
            "intents": intents,
            "primary_intent": primary_intent["intent"],
            "intent_confidence": primary_intent["confidence"],
            "entities": entities,
            "action": action,
            "target": target,
            "sentiment": sentiment,
            "is_question": sentiment["is_question"],
            "urgency": sentiment["urgency"],
            "conversation_context": self.conversation.get_context_for_response(),
            "clarification_context": clarification_context,
            "timestamp": datetime.now().isoformat()
        }

    def get_did_you_mean(self, text: str, known_commands: List[str]) -> Optional[str]:
        """Suggest corrections for misspelled commands"""
        words = text.strip().split()
        first_word = words[0] if words else text
        match = self.fuzzy.best_match(first_word, known_commands, 0.5)
        if match:
            return f"Did you mean '{match[0]}'? (confidence: {match[1]*100:.0f}%)"
        return None
