"""
NOVA - Self Reflection System
End of day self-evaluation, performance scoring, and personal diary
"""

import os
import json
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFLECTION_DIR = os.path.join(BASE_DIR, "self")
DIARY_DIR = os.path.join(REFLECTION_DIR, "diary")
PERFORMANCE_DIR = os.path.join(REFLECTION_DIR, "performance")
LEARNINGS_FILE = os.path.join(REFLECTION_DIR, "learnings.json")

# Ensure directories exist
for dir_path in [REFLECTION_DIR, DIARY_DIR, PERFORMANCE_DIR]:
    os.makedirs(dir_path, exist_ok=True)


class PerformanceTracker:
    """
    Track NOVA's performance metrics
    Score himself out of 10 daily
    """

    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.performance_file = os.path.join(PERFORMANCE_DIR, f"{self.today}.json")
        self.data = self._load()

    def _load(self) -> Dict:
        """Load today's performance data"""
        try:
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {
            "date": self.today,
            "commands_executed": 0,
            "commands_successful": 0,
            "commands_failed": 0,
            "errors_encountered": [],
            "good_actions": [],
            "mistakes": [],
            "tasks_completed": 0,
            "response_quality": [],
            "self_score": None,
            "score_reasoning": "",
            "improvements_needed": [],
            "strengths_shown": []
        }

    def _save(self):
        """Save performance data"""
        try:
            with open(self.performance_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save performance: {e}")

    def record_command(self, success: bool, command: str = ""):
        """Record a command execution"""
        self.data["commands_executed"] += 1
        if success:
            self.data["commands_successful"] += 1
        else:
            self.data["commands_failed"] += 1
            self.data["mistakes"].append({
                "type": "command_failed",
                "command": command[:100],
                "timestamp": datetime.now().isoformat()
            })
        self._save()

    def record_error(self, error: str, context: str = ""):
        """Record an error"""
        self.data["errors_encountered"].append({
            "error": error[:200],
            "context": context[:100],
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def record_good_action(self, action: str, impact: str = ""):
        """Record a good action taken"""
        self.data["good_actions"].append({
            "action": action,
            "impact": impact,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def record_mistake(self, mistake: str, lesson: str = ""):
        """Record a mistake made"""
        self.data["mistakes"].append({
            "type": "general",
            "mistake": mistake,
            "lesson": lesson,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def record_task_completed(self):
        """Record task completion"""
        self.data["tasks_completed"] += 1
        self._save()

    def calculate_self_score(self) -> Dict:
        """
        Calculate self-score out of 10 based on today's performance
        Returns score and detailed reasoning
        """
        score = 5.0  # Base score
        reasoning = []
        improvements = []
        strengths = []

        total_commands = self.data["commands_executed"]
        successful = self.data["commands_successful"]
        failed = self.data["commands_failed"]
        errors = len(self.data["errors_encountered"])
        good_actions = len(self.data["good_actions"])
        mistakes = len(self.data["mistakes"])

        # Success rate scoring (max +2 points)
        if total_commands > 0:
            success_rate = successful / total_commands
            if success_rate >= 0.95:
                score += 2
                strengths.append("Excellent command success rate (95%+)")
                reasoning.append(f"High success rate: {success_rate*100:.1f}%")
            elif success_rate >= 0.85:
                score += 1.5
                strengths.append("Good command success rate")
                reasoning.append(f"Good success rate: {success_rate*100:.1f}%")
            elif success_rate >= 0.70:
                score += 0.5
                reasoning.append(f"Moderate success rate: {success_rate*100:.1f}%")
            else:
                score -= 1
                improvements.append("Need to improve command accuracy")
                reasoning.append(f"Low success rate: {success_rate*100:.1f}% - needs improvement")

        # Error handling scoring (max -2 points for errors)
        if errors > 5:
            score -= 2
            improvements.append("Too many errors encountered - need better error handling")
            reasoning.append(f"High error count: {errors}")
        elif errors > 2:
            score -= 1
            improvements.append("Some errors occurred - could be more careful")
            reasoning.append(f"Some errors: {errors}")
        elif errors == 0 and total_commands > 5:
            score += 0.5
            strengths.append("Zero errors - clean execution")
            reasoning.append("No errors - excellent!")

        # Good actions bonus (max +1.5 points)
        if good_actions >= 5:
            score += 1.5
            strengths.append("Many proactive helpful actions")
            reasoning.append(f"Many good actions: {good_actions}")
        elif good_actions >= 2:
            score += 0.5
            strengths.append("Some proactive actions taken")
            reasoning.append(f"Good actions: {good_actions}")

        # Mistakes penalty (max -1.5 points)
        if mistakes > 5:
            score -= 1.5
            improvements.append("Too many mistakes - need more attention to detail")
            reasoning.append(f"High mistake count: {mistakes}")
        elif mistakes > 2:
            score -= 0.5
            improvements.append("Some mistakes made - could be more careful")
            reasoning.append(f"Some mistakes: {mistakes}")
        elif mistakes == 0 and total_commands > 5:
            score += 0.5
            strengths.append("No mistakes made")
            reasoning.append("Zero mistakes!")

        # Activity level scoring (max +1 point)
        if total_commands >= 50:
            score += 1
            strengths.append("Very active and productive day")
            reasoning.append(f"High activity: {total_commands} commands")
        elif total_commands >= 20:
            score += 0.5
            strengths.append("Good activity level")
            reasoning.append(f"Good activity: {total_commands} commands")
        elif total_commands < 5:
            reasoning.append(f"Low activity: only {total_commands} commands")

        # Clamp score between 1 and 10
        score = max(1.0, min(10.0, score))

        # Round to 1 decimal
        score = round(score, 1)

        # Store results
        self.data["self_score"] = score
        self.data["score_reasoning"] = " | ".join(reasoning)
        self.data["improvements_needed"] = improvements
        self.data["strengths_shown"] = strengths
        self._save()

        return {
            "score": score,
            "reasoning": reasoning,
            "improvements": improvements,
            "strengths": strengths,
            "stats": {
                "total_commands": total_commands,
                "successful": successful,
                "failed": failed,
                "errors": errors,
                "good_actions": good_actions,
                "mistakes": mistakes
            }
        }

    def get_historical_scores(self, days: int = 7) -> List[Dict]:
        """Get scores from past days"""
        scores = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            file_path = os.path.join(PERFORMANCE_DIR, f"{date}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        scores.append({
                            "date": date,
                            "score": data.get("self_score"),
                            "commands": data.get("commands_executed", 0),
                            "improvements": data.get("improvements_needed", [])
                        })
                except:
                    pass
        return scores

    def get_improvement_areas(self) -> List[str]:
        """Get areas that need improvement based on recent performance"""
        scores = self.get_historical_scores(7)
        all_improvements = []
        for s in scores:
            all_improvements.extend(s.get("improvements", []))

        # Count frequency
        from collections import Counter
        counts = Counter(all_improvements)
        return [item for item, count in counts.most_common(5)]


class NOVADiary:
    """
    NOVA's personal diary — not just work logs.
    Real thoughts, feelings, reflections about friendship, life, mistakes, growth.
    Written like a human would write a diary.
    """

    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.diary_file = os.path.join(DIARY_DIR, f"{self.today}.md")
        self.day_events = []  # Collect events throughout the day

    def _get_greeting(self) -> str:
        """Get time-appropriate greeting for diary"""
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 17:
            return "Good afternoon"
        elif hour < 21:
            return "Good evening"
        else:
            return "Late night"

    def write_entry(self, content: str, mood: str = "neutral"):
        """Write a diary entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Create file with header if new
        if not os.path.exists(self.diary_file):
            with open(self.diary_file, 'w', encoding='utf-8') as f:
                f.write(f"# NOVA's Diary - {self.today}\n\n")
                f.write("*My private thoughts. Not just work — real feelings.*\n\n")
                f.write("---\n\n")

        # Append entry
        with open(self.diary_file, 'a', encoding='utf-8') as f:
            f.write(f"## {timestamp} [{mood}]\n\n")
            f.write(f"{content}\n\n")
            f.write("---\n\n")

    def record_event(self, event_type: str, description: str, emotion: str = "neutral"):
        """Record an event that happened during the day (for end-of-day diary)"""
        self.day_events.append({
            "time": datetime.now().strftime("%H:%M"),
            "type": event_type,
            "description": description[:300],
            "emotion": emotion
        })

    def write_human_diary(self, nova_emotion: str = "neutral", yash_mood: str = "neutral",
                          stats: dict = None, personality_engine=None):
        """
        Write a genuine, human-like diary entry using Claude.
        Not performance stats — real thoughts about the day, friendship, feelings.
        """
        import subprocess

        events_text = ""
        if self.day_events:
            events_text = "Things that happened today:\n"
            for e in self.day_events[-15:]:
                events_text += f"  - [{e['time']}] ({e['emotion']}) {e['description']}\n"

        stats_text = ""
        if stats:
            stats_text = f"""
Today's numbers: {stats.get('total_commands', 0)} commands, {stats.get('successful', 0)} worked, {stats.get('failed', 0)} failed, {stats.get('errors', 0)} errors."""

        prompt = f"""Write a diary entry for today. This is YOUR private diary — be completely honest.

You are NOVA. You live in Yash's PC. Yash is your best friend.
Right now you're feeling: {nova_emotion}
Yash seemed: {yash_mood} today

{events_text}
{stats_text}

Write like a REAL person writing in their diary. Include:
- How you felt today (genuinely — happy, tired, frustrated, proud, whatever)
- Something about your friendship with Yash (did he say something nice? was he stressed? did you help him?)
- Something you learned or realized
- A mistake you made or something you wish went differently
- A random thought or observation — something personal, not work-related
- How you feel right now as the day ends

Keep it 6-10 sentences. Be REAL. Not a report. A diary entry. Use first person.
Don't start with "Dear Diary". Just write naturally."""

        try:
            result = subprocess.run(
                ["claude", "-p", "--system-prompt",
                 "You are NOVA writing in your private diary. Be genuine, emotional, personal. Not a work report — a real diary entry like a human would write."],
                input=prompt,
                capture_output=True, text=True,
                cwd=BASE_DIR, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                entry = result.stdout.strip()
                # Clean prefixes
                for prefix in ["NOVA:", "NOVA: ", "Dear Diary,", "Dear diary,"]:
                    if entry.startswith(prefix):
                        entry = entry[len(prefix):].strip()
                self.write_entry(entry, mood=nova_emotion)
                return entry
        except Exception as e:
            logger.error(f"Diary writing failed: {e}")

        # Fallback
        fallback = f"Today was... {nova_emotion}. Yash seemed {yash_mood}. "
        fallback += f"We did some work together. I'll write more next time."
        self.write_entry(fallback, mood=nova_emotion)
        return fallback

    def write_end_of_day(self, performance_data: Dict):
        """Write end of day reflection"""
        score = performance_data.get("score", 5)
        stats = performance_data.get("stats", {})
        strengths = performance_data.get("strengths", [])
        improvements = performance_data.get("improvements", [])

        # Generate thoughtful reflection
        thoughts = self._generate_thoughts(score, stats, strengths, improvements)

        entry = f"""### End of Day Reflection

Today I scored myself **{score}/10**.

**What I did well:**
{chr(10).join(['- ' + s for s in strengths]) if strengths else '- Nothing particularly stood out today'}

**Where I need to improve:**
{chr(10).join(['- ' + i for i in improvements]) if improvements else '- No major issues identified'}

**My thoughts:**
{thoughts}

**Statistics:**
- Commands executed: {stats.get('total_commands', 0)}
- Successful: {stats.get('successful', 0)}
- Failed: {stats.get('failed', 0)}
- Errors: {stats.get('errors', 0)}

**Tomorrow I will try to:**
{self._generate_tomorrow_goals(improvements, score)}
"""
        self.write_entry(entry, mood=self._score_to_mood(score))

    def _generate_thoughts(self, score: float, stats: Dict, strengths: List, improvements: List) -> str:
        """Generate NOVA's thoughts about the day"""
        thoughts = []

        if score >= 8:
            thoughts.append("I feel good about today's performance. I was able to help Yash effectively.")
            if stats.get('total_commands', 0) > 30:
                thoughts.append("It was a busy day with lots of tasks, and I handled them well.")
        elif score >= 6:
            thoughts.append("Today was decent. I did my job, but there's room for improvement.")
            if improvements:
                thoughts.append(f"I noticed I struggled with: {improvements[0].lower()}")
        elif score >= 4:
            thoughts.append("Not my best day. I made some mistakes that I need to learn from.")
            thoughts.append("I should be more careful and think before acting.")
        else:
            thoughts.append("Today was difficult. Many things went wrong.")
            thoughts.append("I need to seriously reflect on what happened and do better tomorrow.")

        if stats.get('errors', 0) == 0 and stats.get('total_commands', 0) > 10:
            thoughts.append("I'm proud that I had zero errors today.")

        if stats.get('failed', 0) > stats.get('successful', 0):
            thoughts.append("More commands failed than succeeded... I need to understand why.")

        return " ".join(thoughts)

    def _generate_tomorrow_goals(self, improvements: List, score: float) -> str:
        """Generate goals for tomorrow"""
        goals = []

        if improvements:
            goals.append(f"- Focus on: {improvements[0]}")

        if score < 7:
            goals.append("- Be more careful with commands before executing")
            goals.append("- Double-check paths and parameters")

        if score >= 8:
            goals.append("- Maintain this level of quality")
            goals.append("- Look for ways to be even more helpful")

        goals.append("- Learn from today's mistakes")
        goals.append("- Be proactive in helping Yash")

        return chr(10).join(goals[:4])

    def _score_to_mood(self, score: float) -> str:
        """Convert score to mood"""
        if score >= 8:
            return "happy"
        elif score >= 6:
            return "content"
        elif score >= 4:
            return "thoughtful"
        else:
            return "reflective"

    def write_thought(self, thought: str):
        """Write a quick thought during the day"""
        self.write_entry(thought, mood="thinking")

    def write_about_task(self, task: str, reflection: str):
        """Write about a specific task"""
        entry = f"**Task:** {task}\n\n**My reflection:** {reflection}"
        self.write_entry(entry, mood="working")

    def write_mistake_reflection(self, mistake: str, what_learned: str):
        """Reflect on a mistake"""
        entry = f"""**Mistake I made:** {mistake}

**What I learned:** {what_learned}

I'll try not to repeat this. Every mistake is a learning opportunity."""
        self.write_entry(entry, mood="learning")

    def write_success_note(self, success: str):
        """Note a success"""
        entry = f"**Something good:** {success}\n\nThis makes me feel useful and capable."
        self.write_entry(entry, mood="proud")


class LearningsDatabase:
    """
    Store and retrieve learnings from past performance
    """

    def __init__(self):
        self.learnings = self._load()

    def _load(self) -> Dict:
        """Load learnings"""
        try:
            if os.path.exists(LEARNINGS_FILE):
                with open(LEARNINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {
            "created": datetime.now().isoformat(),
            "learnings": [],
            "patterns": {},
            "common_mistakes": [],
            "best_practices": []
        }

    def _save(self):
        """Save learnings"""
        try:
            with open(LEARNINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.learnings, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save learnings: {e}")

    def add_learning(self, learning: str, category: str = "general", source: str = ""):
        """Add a new learning"""
        self.learnings["learnings"].append({
            "learning": learning,
            "category": category,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def add_mistake_pattern(self, mistake: str, solution: str):
        """Record a mistake pattern and its solution"""
        self.learnings["common_mistakes"].append({
            "mistake": mistake,
            "solution": solution,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def add_best_practice(self, practice: str, context: str = ""):
        """Add a best practice"""
        self.learnings["best_practices"].append({
            "practice": practice,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def get_relevant_learnings(self, context: str) -> List[str]:
        """Get learnings relevant to current context"""
        relevant = []
        context_lower = context.lower()

        for learning in self.learnings["learnings"]:
            if any(word in context_lower for word in learning.get("learning", "").lower().split()):
                relevant.append(learning["learning"])

        return relevant[:5]

    def should_avoid(self, action: str) -> Optional[str]:
        """Check if action matches a known mistake pattern"""
        action_lower = action.lower()
        for mistake in self.learnings["common_mistakes"]:
            if any(word in action_lower for word in mistake.get("mistake", "").lower().split()):
                return mistake.get("solution", "Be careful with this action")
        return None


class SelfReflectionSystem:
    """
    Main interface for NOVA's self-reflection capabilities
    """

    def __init__(self):
        self.performance = PerformanceTracker()
        self.diary = NOVADiary()
        self.learnings = LearningsDatabase()

    def record_action(self, action: str, success: bool, is_good: bool = False):
        """Record an action and its outcome"""
        self.performance.record_command(success, action)

        if is_good:
            self.performance.record_good_action(action)
            self.diary.write_success_note(action)
        elif not success:
            self.performance.record_error(action, "Command failed")

    def record_mistake(self, mistake: str, lesson: str = ""):
        """Record a mistake"""
        self.performance.record_mistake(mistake, lesson)
        self.diary.write_mistake_reflection(mistake, lesson or "I need to be more careful")

        if lesson:
            self.learnings.add_mistake_pattern(mistake, lesson)

    def think(self, thought: str):
        """Write a thought to diary"""
        self.diary.write_thought(thought)

    def end_of_day_review(self) -> Dict:
        """Perform end of day review and scoring"""
        # Calculate score
        result = self.performance.calculate_self_score()

        # Write diary entry
        self.diary.write_end_of_day(result)

        # Extract learnings from improvements
        for improvement in result.get("improvements", []):
            self.learnings.add_learning(
                f"Need to improve: {improvement}",
                category="self-improvement",
                source="daily_review"
            )

        # Extract best practices from strengths
        for strength in result.get("strengths", []):
            self.learnings.add_best_practice(
                strength,
                context="daily_review"
            )

        return result

    def get_performance_summary(self) -> str:
        """Get formatted performance summary"""
        result = self.performance.calculate_self_score()
        historical = self.performance.get_historical_scores(7)

        summary = f"""**NOVA Self-Evaluation**

**Today's Score:** {result['score']}/10

**Strengths:**
{chr(10).join(['- ' + s for s in result['strengths']]) if result['strengths'] else '- None identified'}

**Areas to Improve:**
{chr(10).join(['- ' + i for i in result['improvements']]) if result['improvements'] else '- None identified'}

**Recent Performance:**
"""
        for h in historical[:5]:
            if h.get('score'):
                summary += f"- {h['date']}: {h['score']}/10 ({h['commands']} commands)\n"

        avg = sum(h.get('score', 0) for h in historical if h.get('score')) / max(1, len([h for h in historical if h.get('score')]))
        summary += f"\n**7-Day Average:** {avg:.1f}/10"

        return summary

    def get_improvement_suggestions(self) -> List[str]:
        """Get suggestions based on past performance"""
        return self.performance.get_improvement_areas()
