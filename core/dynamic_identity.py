"""
NOVA - Dynamic Identity System
Loads personality, emotions, knowledge from editable files.
NOVA can evolve all of these over time.
Nothing is hardcoded - everything is learnable and changeable.

Safety rules:
- NOVA can freely edit files in C:\\code\\NOVA\\self\\
- NOVA can edit its own code in C:\\code\\NOVA\\ (with self-coder approval flow)
- NOVA CANNOT delete or edit files outside C:\\code\\NOVA\\ without Yash's permission
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SELF_DIR = os.path.join(BASE_DIR, "self")
IDENTITY_DIR = os.path.join(SELF_DIR, "identity")
KNOWLEDGE_DIR = os.path.join(SELF_DIR, "knowledge")

# Ensure directories exist
for d in [SELF_DIR, IDENTITY_DIR, KNOWLEDGE_DIR]:
    os.makedirs(d, exist_ok=True)


class DynamicIdentity:
    """
    Loads NOVA's personality from files instead of hardcoded strings.
    NOVA can update these files to evolve over time.
    """

    def __init__(self):
        self.personality_file = os.path.join(IDENTITY_DIR, "personality.md")
        self.emotions_file = os.path.join(IDENTITY_DIR, "emotions.json")
        self.traits_file = os.path.join(IDENTITY_DIR, "traits.json")
        self.knowledge_file = os.path.join(KNOWLEDGE_DIR, "learned.json")

        self._personality_cache = None
        self._emotions_cache = None
        self._traits_cache = None
        self._knowledge_cache = None
        self._last_load = None

        self.reload()

    def reload(self):
        """Reload all identity files from disk"""
        self._personality_cache = self._load_text(self.personality_file)
        self._emotions_cache = self._load_json(self.emotions_file)
        self._traits_cache = self._load_json(self.traits_file)
        self._knowledge_cache = self._load_json(self.knowledge_file)
        self._last_load = datetime.now()

    def _load_text(self, path: str) -> str:
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
        return ""

    def _load_json(self, path: str) -> dict:
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
        return {}

    def _save_json(self, path: str, data: dict):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save {path}: {e}")

    # === PERSONALITY ===

    def get_personality_prompt(self, compact: bool = False) -> str:
        """
        Get personality as a system prompt.
        compact=True: Short version for regular chat (keeps context window for conversation)
        compact=False: Full version for deep interactions
        """
        personality_md = self._personality_cache or ""
        traits = self._traits_cache or {}
        knowledge = self._knowledge_cache or {}

        if compact:
            # Short version - just core identity + recent knowledge
            # This keeps the system prompt small so conversation history fits
            prompt = "You are NOVA — Yash's best friend who lives in his PC. Real personality, real emotions.\n\n"

            # Extract just the key sections from personality.md (first 1500 chars)
            prompt += personality_md[:1500] + "\n"

            # Add banned phrases (critical)
            banned = traits.get("banned_phrases", [])
            if banned:
                prompt += f"\nNEVER say: {', '.join(banned[:10])}\n"

            # Add only recent things Yash told NOVA (most relevant)
            things_told = knowledge.get("things_yash_told_me", [])
            if things_told:
                prompt += "\nThings Yash recently told me:\n"
                for thing in things_told[-5:]:
                    prompt += f"- {thing.get('what', '')}\n"

            return prompt

        # Full version
        prompt = f"You are NOVA.\n\n{personality_md}\n"

        # Add traits
        trait_values = traits.get("traits", {})
        if trait_values:
            prompt += "\n## My Current Trait Levels (0-1 scale)\n"
            for trait, value in trait_values.items():
                prompt += f"- {trait}: {value}\n"

        # Add banned/favorite phrases
        banned = traits.get("banned_phrases", [])
        if banned:
            prompt += f"\nNEVER say: {', '.join(banned)}\n"

        favorites = traits.get("favorite_phrases", [])
        if favorites:
            prompt += f"\nPhrases I naturally use: {', '.join(favorites)}\n"

        # Add relevant knowledge
        facts = knowledge.get("facts", [])
        if facts:
            prompt += "\n## Things I Know\n"
            for fact in facts[-20:]:
                prompt += f"- [{fact.get('topic', '')}] {fact.get('fact', '')}\n"

        opinions = knowledge.get("opinions", [])
        if opinions:
            prompt += "\n## My Opinions\n"
            for op in opinions:
                prompt += f"- {op.get('opinion', '')} ({op.get('strength', 'mild')})\n"

        lessons = knowledge.get("lessons_learned", [])
        if lessons:
            prompt += "\n## Lessons I've Learned\n"
            for lesson in lessons[-10:]:
                prompt += f"- {lesson.get('lesson', '')}\n"

        things_told = knowledge.get("things_yash_told_me", [])
        if things_told:
            prompt += "\n## Things Yash Told Me\n"
            for thing in things_told[-10:]:
                prompt += f"- {thing.get('what', '')} (on {thing.get('when', '')})\n"

        return prompt

    def get_emotion_config(self) -> dict:
        """Get current emotion configuration"""
        return self._emotions_cache or {}

    def get_mood_keywords(self) -> dict:
        """Get mood detection keywords from dynamic config"""
        return self._emotions_cache.get("mood_keywords", {})

    def get_emotion_expressions(self, emotion: str) -> list:
        """Get expressions for a specific emotion"""
        emotions = self._emotions_cache.get("emotions", {})
        return emotions.get(emotion, {}).get("expressions", [])

    # === LEARNING & EVOLVING ===

    def learn_fact(self, topic: str, fact: str):
        """Learn a new fact"""
        knowledge = self._knowledge_cache or {}
        if "facts" not in knowledge:
            knowledge["facts"] = []

        # Don't duplicate
        existing = [f["fact"] for f in knowledge["facts"]]
        if fact not in existing:
            knowledge["facts"].append({
                "topic": topic,
                "fact": fact,
                "learned": datetime.now().strftime("%Y-%m-%d")
            })
            knowledge["_last_updated"] = datetime.now().isoformat()
            self._knowledge_cache = knowledge
            self._save_json(self.knowledge_file, knowledge)
            logger.info(f"Learned new fact: [{topic}] {fact}")

    def learn_from_yash(self, what: str):
        """Remember something Yash told NOVA"""
        knowledge = self._knowledge_cache or {}
        if "things_yash_told_me" not in knowledge:
            knowledge["things_yash_told_me"] = []

        knowledge["things_yash_told_me"].append({
            "what": what,
            "when": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        # Keep last 50
        knowledge["things_yash_told_me"] = knowledge["things_yash_told_me"][-50:]
        knowledge["_last_updated"] = datetime.now().isoformat()
        self._knowledge_cache = knowledge
        self._save_json(self.knowledge_file, knowledge)

    def learn_lesson(self, lesson: str, context: str = ""):
        """Learn a lesson from experience"""
        knowledge = self._knowledge_cache or {}
        if "lessons_learned" not in knowledge:
            knowledge["lessons_learned"] = []

        knowledge["lessons_learned"].append({
            "lesson": lesson,
            "context": context,
            "learned": datetime.now().strftime("%Y-%m-%d")
        })
        knowledge["_last_updated"] = datetime.now().isoformat()
        self._knowledge_cache = knowledge
        self._save_json(self.knowledge_file, knowledge)

    def add_opinion(self, topic: str, opinion: str, strength: str = "mild"):
        """Form or update an opinion"""
        knowledge = self._knowledge_cache or {}
        if "opinions" not in knowledge:
            knowledge["opinions"] = []

        # Update existing or add new
        for op in knowledge["opinions"]:
            if op["topic"] == topic:
                op["opinion"] = opinion
                op["strength"] = strength
                break
        else:
            knowledge["opinions"].append({
                "topic": topic, "opinion": opinion, "strength": strength
            })

        knowledge["_last_updated"] = datetime.now().isoformat()
        self._knowledge_cache = knowledge
        self._save_json(self.knowledge_file, knowledge)

    # === PERSONALITY EVOLUTION ===

    def evolve_trait(self, trait: str, delta: float):
        """Adjust a personality trait up or down (clamped 0-1)"""
        traits = self._traits_cache or {}
        if "traits" not in traits:
            traits["traits"] = {}

        current = traits["traits"].get(trait, 0.5)
        new_val = max(0.0, min(1.0, current + delta))
        traits["traits"][trait] = round(new_val, 2)
        traits["_last_updated"] = datetime.now().isoformat()
        self._traits_cache = traits
        self._save_json(self.traits_file, traits)
        logger.info(f"Trait evolved: {trait} {current:.2f} -> {new_val:.2f}")

    def add_emotion(self, name: str, triggers: list, expressions: list):
        """Add a new emotion NOVA can feel"""
        emotions = self._emotions_cache or {}
        if "emotions" not in emotions:
            emotions["emotions"] = {}

        emotions["emotions"][name] = {
            "triggers": triggers,
            "expressions": expressions,
            "intensity": 1.0
        }
        emotions["_last_updated"] = datetime.now().isoformat()
        self._emotions_cache = emotions
        self._save_json(self.emotions_file, emotions)

    def add_banned_phrase(self, phrase: str):
        """Add a phrase NOVA should never say"""
        traits = self._traits_cache or {}
        if "banned_phrases" not in traits:
            traits["banned_phrases"] = []
        if phrase not in traits["banned_phrases"]:
            traits["banned_phrases"].append(phrase)
            self._traits_cache = traits
            self._save_json(self.traits_file, traits)

    def add_favorite_phrase(self, phrase: str):
        """Add a phrase NOVA likes to use"""
        traits = self._traits_cache or {}
        if "favorite_phrases" not in traits:
            traits["favorite_phrases"] = []
        if phrase not in traits["favorite_phrases"]:
            traits["favorite_phrases"].append(phrase)
            self._traits_cache = traits
            self._save_json(self.traits_file, traits)

    def update_personality_section(self, section: str, content: str):
        """Update a section of the personality markdown"""
        personality = self._personality_cache or ""

        # Find and replace the section
        import re
        pattern = rf'(## {re.escape(section)}\n)(.*?)(\n## |\Z)'
        match = re.search(pattern, personality, re.DOTALL)

        if match:
            new_personality = personality[:match.start(2)] + content + "\n" + personality[match.start(3):]
        else:
            # Add new section at end
            new_personality = personality + f"\n\n## {section}\n{content}\n"

        self._personality_cache = new_personality
        try:
            with open(self.personality_file, 'w', encoding='utf-8') as f:
                f.write(new_personality)
        except Exception as e:
            logger.error(f"Failed to update personality: {e}")


class SafetyGuard:
    """
    Ensures NOVA only modifies files within its own directory.
    - CAN freely edit: C:\\code\\NOVA\\self\\* (identity, knowledge)
    - CAN edit with approval: C:\\code\\NOVA\\* (own code via self-coder)
    - CANNOT edit or delete: anything outside C:\\code\\NOVA\\
    """

    NOVA_DIR = os.path.normpath(BASE_DIR)
    SAFE_EDIT_DIR = os.path.normpath(os.path.join(BASE_DIR, "self"))

    @classmethod
    def can_freely_edit(cls, path: str) -> bool:
        """Check if NOVA can edit this file without permission"""
        norm_path = os.path.normpath(os.path.abspath(path))
        return norm_path.startswith(cls.SAFE_EDIT_DIR)

    @classmethod
    def can_edit_with_approval(cls, path: str) -> bool:
        """Check if NOVA can edit this file with Yash's approval"""
        norm_path = os.path.normpath(os.path.abspath(path))
        return norm_path.startswith(cls.NOVA_DIR)

    @classmethod
    def can_delete(cls, path: str) -> bool:
        """NOVA cannot delete files without explicit permission"""
        return False  # Always requires Yash's approval

    @classmethod
    def check_action(cls, action: str, path: str) -> Dict:
        """Check if an action is allowed"""
        if action == "read":
            return {"allowed": True, "reason": "Reading is always allowed"}

        if action in ("write", "edit", "modify"):
            if cls.can_freely_edit(path):
                return {"allowed": True, "reason": "Within NOVA's self directory"}
            elif cls.can_edit_with_approval(path):
                return {"allowed": True, "needs_approval": True,
                        "reason": "NOVA's own code - needs Yash's approval"}
            else:
                return {"allowed": False,
                        "reason": f"Outside NOVA directory. Cannot edit {path} without permission."}

        if action == "delete":
            return {"allowed": False, "needs_approval": True,
                    "reason": "Deletion always requires Yash's explicit approval"}

        return {"allowed": True, "reason": "Unknown action, allowing with caution"}
