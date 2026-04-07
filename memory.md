# NOVA Complete System Architecture (AGI-Enhanced)

## Overview

NOVA is an AGI-Enhanced AI office assistant with:
1. **3-Tier Memory System** - RM, RAM, ROM
2. **NLP Engine** - Natural language understanding, entity extraction, sentiment analysis
3. **Reasoning Engine** - Rule-based logic, cause-effect learning, decision trees
4. **Context Engine** - Memory-driven responses, situational awareness
5. **Emotion Engine** - User mood tracking, empathetic responses, tone adaptation
6. **Learning Loop** - Actual feedback loop, behavior adaptation, workflow detection
7. **Goal Planner** - Task decomposition, multi-step execution, templates
8. **Proactive Assistant** - Time-based suggestions, pattern-driven recommendations
9. **Anomaly Detector** - System monitoring, security awareness, baseline tracking
10. **Smart Automation** - Macros, command chaining, quick actions
11. **Self-Reflection** - Performance scoring, private diary, learnings database
12. **Project Tracking** - Per-project logging and change tracking

---

## Intelligence Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NOVA BRAIN (AGI-Enhanced)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User Message                                                        │
│       │                                                              │
│       ▼                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │   NLP    │───▶│ Context  │───▶│Reasoning │───▶│ Emotion  │      │
│  │ Engine   │    │ Engine   │    │ Engine   │    │ Engine   │      │
│  │          │    │          │    │          │    │          │      │
│  │-Fuzzy    │    │-Memory   │    │-Rules    │    │-Mood     │      │
│  │ Match    │    │ Lookup   │    │-Causal   │    │-Empathy  │      │
│  │-Entities │    │-Prefs    │    │-Analysis │    │-Tone     │      │
│  │-Sentiment│    │-History  │    │-Safety   │    │-Adapt    │      │
│  │-Intent   │    │-Project  │    │-Predict  │    │          │      │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘      │
│       │               │               │               │              │
│       └───────────────┼───────────────┼───────────────┘              │
│                       ▼                                              │
│              ┌──────────────┐                                        │
│              │   Response   │                                        │
│              │  Generation  │                                        │
│              └──────┬───────┘                                        │
│                     │                                                │
│                     ▼                                                │
│              ┌──────────────┐                                        │
│              │   Learning   │◀── Outcome Feedback                    │
│              │    Loop      │                                        │
│              └──────────────┘                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NOVA MEMORY SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │     RM      │  │     RAM     │  │     ROM     │         │
│  │  Register   │  │   Random    │  │  Read Only  │         │
│  │   Memory    │  │   Access    │  │   Memory    │         │
│  │             │  │   Memory    │  │             │         │
│  │ - Current   │  │ - Session   │  │ - Permanent │         │
│  │   context   │  │   data      │  │   storage   │         │
│  │ - Fast      │  │ - Day-wise  │  │ - SQLite DB │         │
│  │ - Volatile  │  │ - JSON      │  │ - Historical│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Intelligence Modules

### NLP Engine (`core/nlp_engine.py`)
- **FuzzyMatcher** - Typo-tolerant command matching
- **EntityExtractor** - Files, URLs, IPs, apps, languages, git ops
- **SentimentAnalyzer** - Positive/negative/urgent detection
- **IntentClassifier** - 15+ intent categories with confidence scores
- **ConversationTracker** - Multi-turn dialogue, pronoun resolution

### Reasoning Engine (`core/reasoning_engine.py`)
- **Rule System** - 8+ built-in rules (CPU, disk, errors, battery, etc.)
- **CausalChain** - Learns cause-effect relationships over time
- **Situation Analysis** - Safety checks, smart suggestions
- **Knowledge Base** - Success rates per action, common errors

### Context Engine (`core/context_engine.py`)
- Pulls relevant history before every response
- Tracks user preferences from behavior
- Session awareness (topics, actions, errors)
- Project context injection
- Work pattern detection

### Emotion Engine (`core/emotion_engine.py`)
- 6 mood states: happy, frustrated, stressed, curious, tired, neutral
- Mood history tracking with trends
- Response tone adaptation per mood
- Empathetic prefixes when user is frustrated
- NOVA's own mood based on performance

### Learning Loop (`core/learning_loop.py`)
- **BehaviorProfile** - Command success rates, error patterns, workflows
- **AdaptiveStrategy** - Confirms risky commands, suggests alternatives
- **Workflow Detection** - Finds repeated command sequences
- **Pre/Post Action** - Guidance before, feedback after

### Goal Planner (`core/goal_planner.py`)
- 6 built-in plan templates (git, cleanup, morning, backup, etc.)
- Task decomposition from natural language
- Sequential execution with retry logic
- Progress tracking and reporting

### Proactive Assistant (`intelligence/proactive_assistant.py`)
- Time-based suggestions from habits
- System health warnings
- Break reminders for long sessions
- Workflow continuation suggestions
- End-of-day reminders

### Anomaly Detector (`intelligence/anomaly_detector.py`)
- CPU/memory usage anomaly detection (statistical baselines)
- New/unknown process detection
- Network connection monitoring
- Dangerous command detection
- Disk space alerts

### Smart Automation (`intelligence/smart_automation.py`)
- Macro recording and playback
- Command chaining with "then" syntax
- Quick actions (morning, cleanup, git_save, dev_start)
- Natural language chain parsing

---

## New Commands

### Intelligence
| Command | Description |
|---------|-------------|
| `/brain` | Intelligence module status |
| `/mood` | Mood tracking summary |
| `/reasoning` | Reasoning decisions log |
| `/learnings` | What NOVA has learned |
| `/suggestions` | Proactive suggestions |
| `/anomalies` | Anomaly detection report |

### Automation
| Command | Description |
|---------|-------------|
| `/macros` | List saved macros |
| `/recordmacro <name>` | Start recording a macro |
| `/stopmacro` | Stop recording |
| `/runmacro <name>` | Execute a macro |
| `/delmacro <name>` | Delete a macro |
| `/chain <cmd1> then <cmd2>` | Chain commands |
| `/plan <goal>` | Create execution plan |
| `/quickaction [name]` | Run/list quick actions |

---

## Directory Structure

```
C:\code\NOVA\
├── core/
│   ├── nova_brain.py          # Main brain (AGI-enhanced)
│   ├── nlp_engine.py          # NLP processing
│   ├── reasoning_engine.py    # Rule-based reasoning
│   ├── context_engine.py      # Memory-driven context
│   ├── emotion_engine.py      # Mood tracking & empathy
│   ├── learning_loop.py       # Feedback & adaptation
│   ├── goal_planner.py        # Task decomposition
│   ├── memory_system.py       # 3-tier memory
│   ├── self_reflection.py     # Performance & diary
│   └── command_logger.py      # Command logging
├── intelligence/
│   ├── proactive_assistant.py # Smart suggestions
│   ├── anomaly_detector.py    # Anomaly detection
│   ├── smart_automation.py    # Macros & chains
│   ├── proactive_monitor.py   # System monitoring
│   ├── habit_tracker.py       # Pattern learning
│   ├── scheduler.py           # Task scheduling
│   ├── auto_backup.py         # Auto backups
│   └── data/                  # Intelligence state files
├── actions/                   # File, system, code, etc.
├── memory/                    # RM, RAM, ROM storage
├── projects/                  # Project tracking
├── self/                      # Diary & performance
├── logs/                      # Activity logs
├── telegram_bot.py            # Telegram interface
├── main.py                    # Entry point
└── config.py                  # Configuration
```

---

**Created:** 2026-04-07
**Owner:** Yash
**System:** NOVA - AGI-Enhanced AI Office Assistant
