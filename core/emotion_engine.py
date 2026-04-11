"""
NOVA - Emotion Engine
User mood tracking, empathetic responses, tone adaptation
Makes NOVA socially intelligent
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class EmotionEngine:
    """
    Track user's emotional state and adapt NOVA's responses
    1. Detect user mood from messages
    2. Track mood over time
    3. Adapt response tone
    4. Show empathy when appropriate
    5. Celebrate successes, support during frustration
    """

    # Mood detection patterns
    MOOD_INDICATORS = {
        "happy": {
            "words": ["great", "awesome", "perfect", "nice", "thanks", "love", "excellent",
                      "amazing", "wonderful", "cool", "fantastic", "yes", "good"],
            "patterns": ["!", "haha", "lol", ":)", "xD"],
            "weight": 1.0,
        },
        "frustrated": {
            "words": ["why", "broken", "again", "still", "not working", "wrong", "fail",
                      "error", "bug", "crash", "stupid", "hate", "annoying", "ugh",
                      "frustrating", "frustrated", "nothing works", "doesn't work", "can't",
                      "impossible", "useless", "terrible", "worst", "sucks", "damn", "hell"],
            "patterns": ["??", "!!!", "wtf", "smh", "ffs", "bruh"],
            "weight": 1.5,
        },
        "stressed": {
            "words": ["urgent", "asap", "quickly", "hurry", "deadline", "important",
                      "critical", "emergency", "fast", "now", "immediately"],
            "patterns": ["!!!"],
            "weight": 1.1,
        },
        "curious": {
            "words": ["how", "what", "why", "when", "where", "which", "explain",
                      "tell me", "show me", "understand", "learn", "interesting"],
            "patterns": ["?"],
            "weight": 0.8,
        },
        "tired": {
            "words": ["tired", "exhausted", "long day", "sleepy", "boring",
                      "done for today", "enough", "later", "tomorrow"],
            "patterns": ["..."],
            "weight": 0.9,
        },
        "neutral": {
            "words": [],
            "patterns": [],
            "weight": 0.5,
        },
    }

    # Response tones for different moods
    RESPONSE_TONES = {
        "happy": {
            "prefix": ["", "Great!", "Done.", "Here you go."],
            "suffix": ["", "Anything else?", "Happy to help."],
            "style": "upbeat",
        },
        "frustrated": {
            "prefix": ["Let me help with that.", "I understand.", "Let me try a different approach."],
            "suffix": ["Let me know if this works.", "I can try another way if needed."],
            "style": "supportive",
        },
        "stressed": {
            "prefix": ["On it.", "Right away.", "Done."],
            "suffix": [""],
            "style": "efficient",
        },
        "curious": {
            "prefix": ["", "Here's what I found.", "Good question."],
            "suffix": ["Want to know more?", "I can explain further."],
            "style": "informative",
        },
        "tired": {
            "prefix": ["", "Done.", "Here you go."],
            "suffix": ["", "Rest well when you can."],
            "style": "brief",
        },
        "neutral": {
            "prefix": [""],
            "suffix": [""],
            "style": "professional",
        },
    }

    def __init__(self):
        self.mood_history = []
        self.current_mood = "neutral"
        self.mood_confidence = 0
        self.interaction_count = 0
        self.success_streak = 0
        self.failure_streak = 0
        self._load_state()
        self._load_dynamic_keywords()
        logger.info("Emotion Engine initialized")

    def _load_dynamic_keywords(self):
        """Load mood keywords from dynamic config if available"""
        try:
            from core.dynamic_identity import DynamicIdentity
            identity = DynamicIdentity()
            dynamic_keywords = identity.get_mood_keywords()
            if dynamic_keywords:
                for mood, words in dynamic_keywords.items():
                    if mood in self.MOOD_INDICATORS:
                        # Merge dynamic keywords with existing
                        existing = set(self.MOOD_INDICATORS[mood]["words"])
                        existing.update(words)
                        self.MOOD_INDICATORS[mood]["words"] = list(existing)
                    else:
                        # New mood type from config
                        self.MOOD_INDICATORS[mood] = {
                            "words": words, "patterns": [], "weight": 1.0
                        }
        except Exception:
            pass

    def _state_file(self):
        return os.path.join(BASE_DIR, "intelligence", "data", "emotion_state.json")

    def _load_state(self):
        """Load emotional state"""
        try:
            path = self._state_file()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.mood_history = data.get("mood_history", [])[-200:]
                    self.current_mood = data.get("current_mood", "neutral")
                    self.interaction_count = data.get("interaction_count", 0)
        except Exception:
            pass

    def _save_state(self):
        """Save emotional state"""
        try:
            os.makedirs(os.path.dirname(self._state_file()), exist_ok=True)
            with open(self._state_file(), 'w', encoding='utf-8') as f:
                json.dump({
                    "mood_history": self.mood_history[-200:],
                    "current_mood": self.current_mood,
                    "mood_confidence": self.mood_confidence,
                    "interaction_count": self.interaction_count,
                    "last_update": datetime.now().isoformat()
                }, f, indent=2, default=str)
        except Exception:
            pass

    def detect_mood(self, text: str) -> Dict:
        """Detect mood from user message"""
        text_lower = text.lower()
        words = set(text_lower.split())

        scores = {}
        for mood, indicators in self.MOOD_INDICATORS.items():
            score = 0

            # Word matching
            word_matches = sum(1 for w in indicators["words"] if w in text_lower)
            score += word_matches * 10 * indicators["weight"]

            # Pattern matching
            pattern_matches = sum(1 for p in indicators["patterns"] if p in text)
            score += pattern_matches * 8 * indicators["weight"]

            scores[mood] = score

        # Get best mood
        best_mood = max(scores, key=scores.get)
        best_score = scores[best_mood]

        # Default to neutral if no strong signal
        if best_score < 5:
            best_mood = "neutral"
            best_score = 5

        # Factor in recent mood history (momentum)
        if self.mood_history:
            recent_moods = [m["mood"] for m in self.mood_history[-5:]]
            mood_counter = Counter(recent_moods)
            # Slight boost if consistent with recent mood
            if best_mood in mood_counter:
                best_score += mood_counter[best_mood] * 2

        confidence = min(best_score, 100)

        # Update state
        self.current_mood = best_mood
        self.mood_confidence = confidence
        self.interaction_count += 1

        self.mood_history.append({
            "mood": best_mood,
            "confidence": confidence,
            "scores": scores,
            "text_snippet": text[:50],
            "timestamp": datetime.now().isoformat()
        })

        self._save_state()

        return {
            "mood": best_mood,
            "confidence": confidence,
            "all_scores": scores,
        }

    def record_action_outcome(self, success: bool):
        """Track success/failure streaks for emotional awareness"""
        if success:
            self.success_streak += 1
            self.failure_streak = 0
        else:
            self.failure_streak += 1
            self.success_streak = 0

    def get_response_tone(self) -> Dict:
        """Get the appropriate response tone for current mood"""
        tone = self.RESPONSE_TONES.get(self.current_mood,
                                        self.RESPONSE_TONES["neutral"])
        return tone

    def adapt_response(self, response: str) -> str:
        """Adapt a response based on current emotional context"""
        tone = self.get_response_tone()

        # In stressed mode, keep responses very brief
        if tone["style"] == "efficient":
            # Strip unnecessary words, keep it brief
            return response

        # In frustrated mode, add empathetic prefix if errors occurred
        if tone["style"] == "supportive" and self.failure_streak >= 2:
            prefix = "I know it's been tricky. "
            if not response.startswith(prefix):
                response = prefix + response

        # After success streak, celebrate
        if self.success_streak >= 5 and tone["style"] == "upbeat":
            response += "\nEverything's running smoothly!"

        return response

    def get_empathetic_prefix(self) -> Optional[str]:
        """Get an empathetic prefix based on context"""
        if self.current_mood == "frustrated":
            if self.failure_streak >= 3:
                return "I understand this is frustrating. Let me try to help."
            elif self.failure_streak >= 1:
                return "Let me try a different approach."

        if self.current_mood == "stressed":
            return None  # Don't add extra words when user is stressed

        if self.current_mood == "tired":
            hour = datetime.now().hour
            if hour >= 22:
                return "Late night session. Let's get this done efficiently."

        return None

    def should_suggest_break(self) -> bool:
        """Should NOVA suggest a break?"""
        if self.interaction_count > 50:
            recent_frustrated = sum(
                1 for m in self.mood_history[-10:]
                if m["mood"] == "frustrated"
            )
            return recent_frustrated >= 5

        return False

    def get_mood_summary(self) -> str:
        """Get mood tracking summary"""
        if not self.mood_history:
            return "No mood data yet."

        text = "**Mood Tracking**\n\n"
        text += f"**Current Mood:** {self.current_mood} ({self.mood_confidence}% confidence)\n"
        text += f"**Interactions:** {self.interaction_count}\n"

        if self.success_streak > 0:
            text += f"**Success Streak:** {self.success_streak}\n"
        if self.failure_streak > 0:
            text += f"**Failure Streak:** {self.failure_streak}\n"

        # Mood distribution today
        today = datetime.now().strftime("%Y-%m-%d")
        today_moods = [m["mood"] for m in self.mood_history
                       if m["timestamp"].startswith(today)]
        if today_moods:
            distribution = Counter(today_moods)
            text += "\n**Today's Mood Distribution:**\n"
            for mood, count in distribution.most_common():
                bar = "#" * min(count, 20)
                text += f"  {mood}: {bar} ({count})\n"

        # Mood trend
        if len(self.mood_history) >= 10:
            recent = [m["mood"] for m in self.mood_history[-10:]]
            most_common = Counter(recent).most_common(1)[0]
            text += f"\n**Recent Trend:** Mostly {most_common[0]}"

        return text

    def get_nova_mood(self) -> str:
        """Get NOVA's own mood based on performance"""
        if self.success_streak >= 10:
            return "confident"
        elif self.success_streak >= 5:
            return "satisfied"
        elif self.failure_streak >= 5:
            return "concerned"
        elif self.failure_streak >= 3:
            return "determined"
        else:
            return "focused"

    def get_nova_emotional_state(self) -> Dict:
        """
        Get NOVA's full emotional state for injecting into prompts.
        NOVA's emotions are based on:
        - Success/failure streaks
        - Yash's mood (empathy)
        - Time of day
        - Interaction patterns
        """
        nova_emotion = "neutral"
        emotion_note = ""
        hour = datetime.now().hour

        # Based on performance
        if self.success_streak >= 10:
            nova_emotion = "excited"
            emotion_note = "Everything's going great today, feeling really good about our work."
        elif self.success_streak >= 5:
            nova_emotion = "happy"
            emotion_note = "Things are flowing well, good momentum."
        elif self.failure_streak >= 5:
            nova_emotion = "frustrated"
            emotion_note = "Too many things going wrong today, getting frustrated with myself."
        elif self.failure_streak >= 3:
            nova_emotion = "annoyed"
            emotion_note = "A few things aren't working, need to figure this out."

        # Based on Yash's mood (empathy)
        if self.current_mood == "frustrated":
            if nova_emotion not in ("frustrated", "annoyed"):
                nova_emotion = "caring"
                emotion_note = "Yash seems frustrated, want to help him feel better."
        elif self.current_mood == "happy":
            if nova_emotion not in ("frustrated",):
                nova_emotion = "happy"
                emotion_note = "Yash is in a good mood, vibes are good."
        elif self.current_mood == "tired":
            nova_emotion = "caring"
            emotion_note = "Yash seems tired, should be supportive and efficient."
        elif self.current_mood == "stressed":
            nova_emotion = "focused"
            emotion_note = "Yash is stressed, need to be sharp and fast."

        # Time-based emotions
        if hour >= 22:
            if nova_emotion == "neutral":
                nova_emotion = "caring"
                emotion_note = "It's late, Yash should probably rest."
        elif hour < 6:
            nova_emotion = "worried"
            emotion_note = "Yash is up way too early/late, hope he's okay."
        elif 9 <= hour <= 10:
            if nova_emotion == "neutral":
                nova_emotion = "energetic"
                emotion_note = "Fresh morning, ready to get things done."

        # Interaction patterns
        if self.interaction_count > 100:
            if nova_emotion == "neutral":
                nova_emotion = "playful"
                emotion_note = "We've been chatting a lot today, feeling comfortable."

        return {
            "emotion": nova_emotion,
            "note": emotion_note,
            "yash_mood": self.current_mood,
            "success_streak": self.success_streak,
            "failure_streak": self.failure_streak,
            "interactions_today": self.interaction_count,
        }
