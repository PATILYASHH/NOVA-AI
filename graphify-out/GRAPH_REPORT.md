# Graph Report - .  (2026-04-11)

## Corpus Check
- 42 files · ~54,791 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1408 nodes · 4713 edges · 156 communities detected
- Extraction: 41% EXTRACTED · 59% INFERRED · 0% AMBIGUOUS · INFERRED: 2760 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `is_authorized()` - 115 edges
2. `Personality` - 104 edges
3. `NovaMemorySystem` - 100 edges
4. `SelfReflectionSystem` - 96 edges
5. `ContextEngine` - 72 edges
6. `CodeHandler` - 71 edges
7. `FileOperations` - 71 edges
8. `SystemControl` - 71 edges
9. `AgentExecutor` - 71 edges
10. `ProactiveMonitor` - 71 edges

## Surprising Connections (you probably didn't know these)
- `NOVA - Telegram Bot Handler (AGI-Enhanced) Full-featured Telegram interface with` --uses--> `SmartAutomation`  [INFERRED]
  telegram_bot.py → intelligence\smart_automation.py
- `NOVA - Telegram Bot Handler (AGI-Enhanced) Full-featured Telegram interface with` --uses--> `AgentExecutor`  [INFERRED]
  telegram_bot.py → core\agent_executor.py
- `Command executor for macros and automation` --uses--> `SmartAutomation`  [INFERRED]
  telegram_bot.py → intelligence\smart_automation.py
- `Command executor for macros and automation` --uses--> `AgentExecutor`  [INFERRED]
  telegram_bot.py → core\agent_executor.py
- `NOVA writes private diary on significant events` --uses--> `SmartAutomation`  [INFERRED]
  telegram_bot.py → intelligence\smart_automation.py

## Communities

### Community 0 - "Core Intelligence Hub"
Cohesion: 0.12
Nodes (157): AdvancedControl, Advanced system control operations, AnomalyDetector, Monitors for anomalies:     1. Unusual system resource usage     2. Unexpected p, CodeHandler, Handle code-related operations, ActivityTracker, CommandLogger (+149 more)

### Community 1 - "System Control API"
Cohesion: 0.02
Nodes (48): NOVA - Advanced Control Module Window management, volume, network, downloads, a, NOVA - Anomaly Detector Detect unusual system behavior, security threats, patter, NOVA - Code Handler Module Handles code execution, editing, Claude Code integra, NOVA - Command Logger Automatic logging of all commands and activities, Decorator to automatically track command execution     Use on telegram command, track_command(), NOVA - Configuration Your Professional AI Office Assistant, NOVA - Context Engine Memory-driven decision making - pulls relevant memory into (+40 more)

### Community 2 - "Telegram Command Handlers"
Cohesion: 0.04
Nodes (126): about(), addrule_cmd(), addstartup_cmd(), alias_cmd(), anomalies_cmd(), apps_cmd(), _auto_diary_on_event(), autokill_cmd() (+118 more)

### Community 3 - "Memory System"
Cohesion: 0.03
Nodes (48): DailyReviewer, ProjectTracker, RandomAccessMemory, NOVA - 3-Tier Memory System  Memory Architecture: 1. RM (Register Memory) - C, Set currently active project, Set current task being worked on, Get summary of current context for NOVA, Clear register memory (new session) (+40 more)

### Community 4 - "Self-Reflection Engine"
Cohesion: 0.04
Nodes (31): LearningsDatabase, NOVADiary, PerformanceTracker, NOVA - Self Reflection System End of day self-evaluation, performance scoring,, Record a mistake made, Record task completion, Calculate self-score out of 10 based on today's performance         Returns sco, Get scores from past days (+23 more)

### Community 5 - "Self-Improvement Engine"
Cohesion: 0.05
Nodes (27): CodePatcher, NOVA - Self-Improvement Engine NOVA reviews its own performance, identifies weak, Safely apply code patches to NOVA's own files, Create backup before modification, Restore file from backup, Apply a text replacement patch to a file, Add content to a file (end, start, or after a marker), Generate a readable diff (+19 more)

### Community 6 - "Learning Loop"
Cohesion: 0.06
Nodes (20): AdaptiveStrategy, BehaviorProfile, from_dict(), NOVA - Learning Loop Actual feedback loop where past learnings influence future, Predict what user will do next based on workflow patterns, Record an action and its outcome - the core learning input, Tracks and learns from behavioral patterns, Record when user corrects NOVA's behavior (+12 more)

### Community 7 - "Smart Automation"
Cohesion: 0.07
Nodes (18): CommandChain, from_dict(), Macro, NOVA - Smart Automation Command chaining, macros, workflow automation, and intel, Set the command executor function, Start recording a macro, Record a command during macro recording, Stop recording and save macro (+10 more)

### Community 8 - "NLP Engine"
Cohesion: 0.06
Nodes (24): best_match(), ConversationTracker, EntityExtractor, FuzzyMatcher, IntentClassifier, NOVA - Natural Language Processing Engine Advanced NLU without external APIs - f, Extract all entities from text, Extract primary action verb and its category (+16 more)

### Community 9 - "Reasoning Engine"
Cohesion: 0.06
Nodes (19): CausalChain, DecisionNode, NOVA - Reasoning Engine Rule-based logic, decision trees, cause-effect analysis,, Predict causes of an effect, Load persistent reasoning state, Save persistent reasoning state, Register built-in reasoning rules, A node in a decision tree (+11 more)

### Community 10 - "Agent Executor"
Cohesion: 0.08
Nodes (17): AgentExecutor, AgentStep, NOVA - Autonomous Agent Executor Chains Claude Code + Git + GitHub CLI to execut, Auto stage, commit, and push all changes, A single step in an autonomous execution plan, Create a new GitHub repo and optionally link to local directory, Execute any arbitrary task autonomously using Claude Code.         This is the g, Extract project name, language, type from description (+9 more)

### Community 11 - "Auto Backup"
Cohesion: 0.09
Nodes (13): AutoBackup, NOVA - Auto Backup System Automatically backup important files and projects, Check if path should be excluded from backup, Backup a specific path, Backup all configured targets, Keep only the last N backups for a name, Automatic backup system for files and projects, Get backup system status (+5 more)

### Community 12 - "Personality Response"
Cohesion: 0.08
Nodes (12): Classify message as coding, task, or casual, Generate a conversational response with adaptive context, Natural response after executing a task, Ask Claude to classify the message. Detects:         - PC actions (open app, scr, Create execution plan for complex task, Write private diary entry, Generate 6PM daily report, Ensure response is valid Telegram Markdown (+4 more)

### Community 13 - "Context Engine Methods"
Cohesion: 0.09
Nodes (11): Find past interactions relevant to current query, Get preferences relevant to current intent, Get active project context, Detect if this is a follow-up to previous conversation, Get current time period, Get current session duration in minutes, Get a quick system state summary, Get work pattern insights for current time (+3 more)

### Community 14 - "Style Learner Methods"
Cohesion: 0.1
Nodes (10): Scan all repos under a base path, Collect relevant files from repo, Analyze naming conventions, Extract color schemes and theme preferences, Detect tech stack from files, Analyze commonly used packages, Learn project structure patterns, Learn code patterns: error handling, imports, etc. (+2 more)

### Community 15 - "Anomaly Detection Methods"
Cohesion: 0.11
Nodes (8): Run all anomaly checks, Check for CPU usage anomaly, Check for memory usage anomaly, Check for new/unknown processes, Check for disk space anomalies, Check for network anomalies, Load baselines and state, Update baseline measurements of normal behavior

### Community 16 - "Work Setup"
Cohesion: 0.12
Nodes (7): ProjectSetup, NOVA - Work Setup System When user says "I'm going to work on FlashLink", NOVA:, Full workspace setup for a project         Returns step-by-step results, Configuration for setting up a project workspace, Generate a work briefing, Add or update project setup config, Get project setup config

### Community 17 - "Extras Utilities"
Cohesion: 0.12
Nodes (3): batch_delete(), Scan directory and return file state, Check all watched paths for changes

### Community 18 - "Command Logger Methods"
Cohesion: 0.14
Nodes (6): Ensure log file exists, Update date if day changed, Log a command execution, Get all commands from today, Get today's command count, Get commands by category

### Community 19 - "Memory Recall Methods"
Cohesion: 0.18
Nodes (7): Search file operation history, Search project change history, Search today's session memory, Format recall results for display, Search memory and return relevant past interactions, Extract meaningful search terms from query, Calculate relevance score

### Community 20 - "Proactive Suggestions"
Cohesion: 0.19
Nodes (7): Get suggestions based on user habits, Get suggestions based on system state, Get work pattern suggestions, Get workflow continuation suggestions, Get time-aware suggestions, Check if we can make a suggestion in this category, Get current proactive suggestions         Called periodically or on user interac

### Community 21 - "Task Scheduler Methods"
Cohesion: 0.16
Nodes (6): Remove a scheduled task, Enable or disable a task, Calculate next run time for a task, Background scheduler loop, Run a task immediately, Add a scheduled task          Args:             name: Task name (unique ident

### Community 22 - "Documentation Concepts"
Cohesion: 0.2
Nodes (12): Context Engine, Emotion Engine, Learning Loop, 3-Tier Memory System, NLP Engine, NOVA Brain, Proactive Assistant, RAM (Random Access Memory) (+4 more)

### Community 23 - "Proactive Monitor Methods"
Cohesion: 0.27
Nodes (4): Background monitoring loop with morning briefing, Send a morning briefing to Yash, Get current system status, Send alert if not recently sent

### Community 24 - "Habit Tracker Methods"
Cohesion: 0.22
Nodes (3): Record work on a project, Analyze recorded data for patterns, Record a command execution

### Community 25 - "Context Preferences"
Cohesion: 0.25
Nodes (3): Learn a user preference from behavior, Load learned user preferences, Save user preferences

### Community 26 - "Nova Brain Methods"
Cohesion: 0.29
Nodes (3): Load NOVA's persistent memory, Save to NOVA's persistent memory, Append an entry to memory

### Community 27 - "Extras Init"
Cohesion: 0.29
Nodes (0): 

### Community 28 - "Powers Search"
Cohesion: 0.29
Nodes (3): Get a quick answer by searching and summarizing, Search for text inside files, Find function/class definition

### Community 29 - "Proactive State"
Cohesion: 0.29
Nodes (1): Dismiss a category of suggestions

### Community 30 - "Emotion State"
Cohesion: 0.33
Nodes (1): Detect mood from user message

### Community 31 - "Powers App Tracking"
Cohesion: 0.33
Nodes (1): Record current running apps

### Community 32 - "Powers Core"
Cohesion: 0.47
Nodes (5): analyze_image(), analyze_screenshot(), NOVA - Power Features Screen Vision, Web Search, File Content Search, Code Revie, read_pdf(), summarize_pdf()

### Community 33 - "Self-Reflection Docs"
Cohesion: 0.4
Nodes (5): Self-Reflection System, Learnings Database, Performance Tracker, Private Diary System, Self-Scoring System

### Community 34 - "Auto Push"
Cohesion: 0.5
Nodes (3): auto_push(), NOVA - Auto Push to GitHub Runs daily at 5PM to commit and push all changes to N, Commit all changes and push to GitHub

### Community 35 - "Emotion Response"
Cohesion: 0.5
Nodes (2): Get the appropriate response tone for current mood, Adapt a response based on current emotional context

### Community 36 - "Nova Brain Parse"
Cohesion: 0.5
Nodes (2): Legacy intent parsing - used as fallback (matches NLP engine intent names), Full intelligence pipeline for processing a message         Returns structured u

### Community 37 - "Project Autodetect"
Cohesion: 0.5
Nodes (2): Detect project from a file/directory path, Detect project from a command that references a path

### Community 38 - "Background Services"
Cohesion: 0.5
Nodes (0): 

### Community 39 - "Git Auto Commit"
Cohesion: 0.5
Nodes (2): Generate commit message from current diff, Stage all, generate message, commit

### Community 40 - "Screen Vision"
Cohesion: 0.5
Nodes (2): Take screenshot and read all text from it, Check if specific text is visible on screen

### Community 41 - "Activity Tracker Init"
Cohesion: 0.67
Nodes (1): Ensure activity file exists

### Community 42 - "Powers Init"
Cohesion: 0.67
Nodes (0): 

### Community 43 - "Code Review"
Cohesion: 0.67
Nodes (1): Review code changes using Claude

### Community 44 - "NOVA Origin"
Cohesion: 1.0
Nodes (3): NOVA Creation Event, Yash (Owner), NOVA System Overview

### Community 45 - "Activity Recent"
Cohesion: 1.0
Nodes (1): Get recent activities

### Community 46 - "Session Update"
Cohesion: 1.0
Nodes (1): Update session context after each action

### Community 47 - "Response Prefix"
Cohesion: 1.0
Nodes (1): Generate a smart prefix for responses based on context         Returns None if n

### Community 48 - "Nova Mood"
Cohesion: 1.0
Nodes (1): Get NOVA's own mood based on performance

### Community 49 - "Action Outcome"
Cohesion: 1.0
Nodes (1): Track success/failure streaks for emotional awareness

### Community 50 - "Empathetic Prefix"
Cohesion: 1.0
Nodes (1): Get an empathetic prefix based on context

### Community 51 - "Break Suggestion"
Cohesion: 1.0
Nodes (1): Should NOVA suggest a break?

### Community 52 - "Mood Summary"
Cohesion: 1.0
Nodes (1): Get mood tracking summary

### Community 53 - "Plan Cancel"
Cohesion: 1.0
Nodes (1): Cancel an active plan

### Community 54 - "Handler Register"
Cohesion: 1.0
Nodes (1): Register an action handler

### Community 55 - "Plan Suggest"
Cohesion: 1.0
Nodes (1): Suggest a plan based on intent and entities

### Community 56 - "Learning Summary"
Cohesion: 1.0
Nodes (1): Get summary of what NOVA has learned

### Community 57 - "Intelligence Init"
Cohesion: 1.0
Nodes (1): Initialize intelligence modules (called after all modules are created)

### Community 58 - "Post Process"
Cohesion: 1.0
Nodes (1): Called after an action is executed - feeds back into learning

### Community 59 - "Format Response"
Cohesion: 1.0
Nodes (1): Format NOVA's response with personality and emotional awareness

### Community 60 - "Greeting"
Cohesion: 1.0
Nodes (1): Get context-aware greeting

### Community 61 - "Intelligence Status"
Cohesion: 1.0
Nodes (1): Get status of all intelligence modules

### Community 62 - "Help Message"
Cohesion: 1.0
Nodes (1): Return NOVA's capabilities

### Community 63 - "Personality Core"
Cohesion: 1.0
Nodes (1): NOVA - Dynamic Personality via Claude CLI All messages routed through 'claude -p

### Community 64 - "Action Message"
Cohesion: 1.0
Nodes (1): Get a human-readable message for a reasoning action

### Community 65 - "Success Rate"
Cohesion: 1.0
Nodes (1): Get historical success rate for an action

### Community 66 - "Decision Summary"
Cohesion: 1.0
Nodes (1): Get summary of recent decisions

### Community 67 - "Changelog"
Cohesion: 1.0
Nodes (1): Get changelog of recent improvements

### Community 68 - "Background Anomaly"
Cohesion: 1.0
Nodes (1): Start background anomaly detection

### Community 69 - "Command Anomaly"
Cohesion: 1.0
Nodes (1): Check if a command is anomalous based on history

### Community 70 - "Stop Anomaly"
Cohesion: 1.0
Nodes (1): Stop background detection

### Community 71 - "Clipboard Entry"
Cohesion: 1.0
Nodes (1): Get entry by index (1-based, newest first)

### Community 72 - "Habit Init"
Cohesion: 1.0
Nodes (0): 

### Community 73 - "Habit Predictions"
Cohesion: 1.0
Nodes (1): Get predictions based on current time and patterns

### Community 74 - "Next Command"
Cohesion: 1.0
Nodes (1): Predict next command based on sequences

### Community 75 - "Memory Recall Core"
Cohesion: 1.0
Nodes (1): NOVA - Conversation Memory Recall Search past interactions: "remember that file

### Community 76 - "Recall Query Check"
Cohesion: 1.0
Nodes (1): Check if user is asking about past interactions

### Community 77 - "Image Read"
Cohesion: 1.0
Nodes (1): Read text from an image file

### Community 78 - "System Dashboard"
Cohesion: 1.0
Nodes (0): 

### Community 79 - "Screen Area Read"
Cohesion: 1.0
Nodes (1): Read text from a specific screen area

### Community 80 - "Web Search"
Cohesion: 1.0
Nodes (1): Search the web using DuckDuckGo HTML

### Community 81 - "Page Fetch"
Cohesion: 1.0
Nodes (1): Fetch and extract text from a webpage

### Community 82 - "Proactive Summary"
Cohesion: 1.0
Nodes (1): Get suggestion summary

### Community 83 - "Proactive Background"
Cohesion: 1.0
Nodes (1): Start background suggestion checking

### Community 84 - "Proactive Stop"
Cohesion: 1.0
Nodes (1): Stop background checking

### Community 85 - "Monitor Init"
Cohesion: 1.0
Nodes (0): 

### Community 86 - "Monitor State"
Cohesion: 1.0
Nodes (0): 

### Community 87 - "Monitor Stop"
Cohesion: 1.0
Nodes (1): Stop background monitoring

### Community 88 - "Large Processes"
Cohesion: 1.0
Nodes (1): Check for processes using too much resources

### Community 89 - "Monitor Start"
Cohesion: 1.0
Nodes (1): Start background monitoring

### Community 90 - "Scheduler Init"
Cohesion: 1.0
Nodes (0): 

### Community 91 - "Task List"
Cohesion: 1.0
Nodes (1): List all scheduled tasks

### Community 92 - "Style Init"
Cohesion: 1.0
Nodes (0): 

### Community 93 - "Style Learner Core"
Cohesion: 1.0
Nodes (1): NOVA - Style Learner Learns user's coding style, UI preferences, naming patterns

### Community 94 - "Style Guide"
Cohesion: 1.0
Nodes (1): Generate a style guide from learned patterns

### Community 95 - "Style Recommendations"
Cohesion: 1.0
Nodes (1): Get style recommendations for a new project

### Community 96 - "Project Name Extract"
Cohesion: 1.0
Nodes (1): Extract project name from work request

### Community 97 - "Work Request Check"
Cohesion: 1.0
Nodes (1): Check if user is requesting work setup

### Community 98 - "Advanced Rationale 1"
Cohesion: 1.0
Nodes (1): Set system volume (0-100)

### Community 99 - "Advanced Rationale 2"
Cohesion: 1.0
Nodes (1): Get network information

### Community 100 - "Advanced Rationale 3"
Cohesion: 1.0
Nodes (1): Get WiFi connection info

### Community 101 - "Advanced Rationale 4"
Cohesion: 1.0
Nodes (1): List available WiFi networks

### Community 102 - "Advanced Rationale 5"
Cohesion: 1.0
Nodes (1): Download file from URL

### Community 103 - "Advanced Rationale 6"
Cohesion: 1.0
Nodes (1): List installed programs

### Community 104 - "Advanced Rationale 7"
Cohesion: 1.0
Nodes (1): List startup programs

### Community 105 - "Advanced Rationale 8"
Cohesion: 1.0
Nodes (1): List Windows services

### Community 106 - "Advanced Rationale 9"
Cohesion: 1.0
Nodes (1): Start/stop/restart a service

### Community 107 - "Advanced Rationale 10"
Cohesion: 1.0
Nodes (1): Minimize all windows (show desktop)

### Community 108 - "Advanced Rationale 11"
Cohesion: 1.0
Nodes (1): Get environment variable

### Community 109 - "Advanced Rationale 12"
Cohesion: 1.0
Nodes (1): List all environment variables

### Community 110 - "Advanced Rationale 13"
Cohesion: 1.0
Nodes (1): Get detailed disk information

### Community 111 - "Advanced Rationale 14"
Cohesion: 1.0
Nodes (1): Empty the recycle bin

### Community 112 - "Advanced Rationale 15"
Cohesion: 1.0
Nodes (1): Clear temporary files

### Community 113 - "Code Handler Rationale 1"
Cohesion: 1.0
Nodes (1): Execute code in the specified language

### Community 114 - "Code Handler Rationale 2"
Cohesion: 1.0
Nodes (1): Execute a task using Claude Code CLI

### Community 115 - "Code Handler Rationale 3"
Cohesion: 1.0
Nodes (1): Execute git operations

### Community 116 - "Code Handler Rationale 4"
Cohesion: 1.0
Nodes (1): Open a file in code editor

### Community 117 - "Code Handler Rationale 5"
Cohesion: 1.0
Nodes (1): Build a knowledge graph of a codebase using Graphify

### Community 118 - "Code Handler Rationale 6"
Cohesion: 1.0
Nodes (1): Query a project's knowledge graph and return relevant context

### Community 119 - "Code Handler Rationale 7"
Cohesion: 1.0
Nodes (1): Check which projects have been indexed with Graphify

### Community 120 - "Code Handler Rationale 8"
Cohesion: 1.0
Nodes (1): Create a new GitHub repository and optionally link it to a local folder

### Community 121 - "Code Handler Rationale 9"
Cohesion: 1.0
Nodes (1): Create a pull request

### Community 122 - "Code Handler Rationale 10"
Cohesion: 1.0
Nodes (1): List user's GitHub repositories

### Community 123 - "Code Handler Rationale 11"
Cohesion: 1.0
Nodes (1): Get info about a specific repo

### Community 124 - "Code Handler Rationale 12"
Cohesion: 1.0
Nodes (1): Auto stage all changes, commit with message, and push

### Community 125 - "File Ops Rationale 1"
Cohesion: 1.0
Nodes (1): Read contents of a file

### Community 126 - "File Ops Rationale 2"
Cohesion: 1.0
Nodes (1): Write content to a file

### Community 127 - "File Ops Rationale 3"
Cohesion: 1.0
Nodes (1): Delete a file or directory

### Community 128 - "File Ops Rationale 4"
Cohesion: 1.0
Nodes (1): List contents of a directory

### Community 129 - "File Ops Rationale 5"
Cohesion: 1.0
Nodes (1): Find files matching a pattern

### Community 130 - "File Ops Rationale 6"
Cohesion: 1.0
Nodes (1): Copy file or directory

### Community 131 - "File Ops Rationale 7"
Cohesion: 1.0
Nodes (1): Move file or directory

### Community 132 - "System Control Rationale 1"
Cohesion: 1.0
Nodes (1): Execute a shell command

### Community 133 - "System Control Rationale 2"
Cohesion: 1.0
Nodes (1): Find the full path to an executable using multiple strategies.

### Community 134 - "System Control Rationale 3"
Cohesion: 1.0
Nodes (1): Open an application using cmd terminal

### Community 135 - "System Control Rationale 4"
Cohesion: 1.0
Nodes (1): Check if an application is currently running.

### Community 136 - "System Control Rationale 5"
Cohesion: 1.0
Nodes (1): Close an application by name

### Community 137 - "System Control Rationale 6"
Cohesion: 1.0
Nodes (1): Get system status information

### Community 138 - "System Control Rationale 7"
Cohesion: 1.0
Nodes (1): List running processes

### Community 139 - "System Control Rationale 8"
Cohesion: 1.0
Nodes (1): Shutdown, restart, or sleep the PC

### Community 140 - "Utilities Rationale 1"
Cohesion: 1.0
Nodes (1): Open URL in default browser

### Community 141 - "Utilities Rationale 2"
Cohesion: 1.0
Nodes (1): Get current date and time

### Community 142 - "Utilities Rationale 3"
Cohesion: 1.0
Nodes (1): Set a reminder (creates a scheduled task)

### Community 143 - "NLP Rationale 1"
Cohesion: 1.0
Nodes (1): Calculate similarity ratio between two strings

### Community 144 - "NLP Rationale 2"
Cohesion: 1.0
Nodes (1): Find best matching candidate

### Community 145 - "NLP Rationale 3"
Cohesion: 1.0
Nodes (1): Get close matches from candidates

### Community 146 - "Powers Rationale 1"
Cohesion: 1.0
Nodes (1): Analyze an image:         1. Extract text with OCR (if available)         2. Sen

### Community 147 - "Powers Rationale 2"
Cohesion: 1.0
Nodes (1): Take a screenshot and analyze it

### Community 148 - "Powers Rationale 3"
Cohesion: 1.0
Nodes (1): Extract text from a PDF file

### Community 149 - "Powers Rationale 4"
Cohesion: 1.0
Nodes (1): Read a PDF and summarize it using Claude

### Community 150 - "Work Setup Rationale"
Cohesion: 1.0
Nodes (1): Send online notification to all authorized users

### Community 151 - "Goal Planner Doc"
Cohesion: 1.0
Nodes (1): Goal Planner

### Community 152 - "Anomaly Detector Doc"
Cohesion: 1.0
Nodes (1): Anomaly Detector

### Community 153 - "Smart Automation Doc"
Cohesion: 1.0
Nodes (1): Smart Automation

### Community 154 - "Day 1 Performance"
Cohesion: 1.0
Nodes (1): Day 1 Performance

### Community 155 - "Day 2 Performance"
Cohesion: 1.0
Nodes (1): Day 2 Performance

## Knowledge Gaps
- **463 isolated node(s):** `NOVA - Auto Push to GitHub Runs daily at 5PM to commit and push all changes to N`, `Commit all changes and push to GitHub`, `NOVA - Configuration Your Professional AI Office Assistant`, `NOVA - Main Entry Point (AGI-Enhanced) Professional AI Office Assistant for Remo`, `Print NOVA startup banner` (+458 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Activity Recent`** (2 nodes): `.get_recent()`, `Get recent activities`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Session Update`** (2 nodes): `.update_session()`, `Update session context after each action`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Response Prefix`** (2 nodes): `.generate_response_prefix()`, `Generate a smart prefix for responses based on context         Returns None if n`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Nova Mood`** (2 nodes): `.get_nova_mood()`, `Get NOVA's own mood based on performance`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Action Outcome`** (2 nodes): `.record_action_outcome()`, `Track success/failure streaks for emotional awareness`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Empathetic Prefix`** (2 nodes): `.get_empathetic_prefix()`, `Get an empathetic prefix based on context`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Break Suggestion`** (2 nodes): `.should_suggest_break()`, `Should NOVA suggest a break?`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Mood Summary`** (2 nodes): `.get_mood_summary()`, `Get mood tracking summary`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Plan Cancel`** (2 nodes): `.cancel_plan()`, `Cancel an active plan`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Handler Register`** (2 nodes): `.register_handler()`, `Register an action handler`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Plan Suggest`** (2 nodes): `.suggest_plan()`, `Suggest a plan based on intent and entities`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Learning Summary`** (2 nodes): `.get_learning_summary()`, `Get summary of what NOVA has learned`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Intelligence Init`** (2 nodes): `.init_intelligence()`, `Initialize intelligence modules (called after all modules are created)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Post Process`** (2 nodes): `.post_process()`, `Called after an action is executed - feeds back into learning`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Format Response`** (2 nodes): `.format_response()`, `Format NOVA's response with personality and emotional awareness`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Greeting`** (2 nodes): `.get_greeting()`, `Get context-aware greeting`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Intelligence Status`** (2 nodes): `.get_intelligence_status()`, `Get status of all intelligence modules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Help Message`** (2 nodes): `.get_help_message()`, `Return NOVA's capabilities`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Personality Core`** (2 nodes): `personality.py`, `NOVA - Dynamic Personality via Claude CLI All messages routed through 'claude -p`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Action Message`** (2 nodes): `Get a human-readable message for a reasoning action`, `.get_action_message()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Success Rate`** (2 nodes): `Get historical success rate for an action`, `.get_success_rate()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Decision Summary`** (2 nodes): `Get summary of recent decisions`, `.get_decision_summary()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Changelog`** (2 nodes): `Get changelog of recent improvements`, `.get_changelog()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Background Anomaly`** (2 nodes): `.start_background()`, `Start background anomaly detection`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Command Anomaly`** (2 nodes): `.check_command_anomaly()`, `Check if a command is anomalous based on history`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Stop Anomaly`** (2 nodes): `.stop()`, `Stop background detection`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Clipboard Entry`** (2 nodes): `.get_entry()`, `Get entry by index (1-based, newest first)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Habit Init`** (2 nodes): `.__init__()`, `._load()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Habit Predictions`** (2 nodes): `.get_predictions()`, `Get predictions based on current time and patterns`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Next Command`** (2 nodes): `.get_next_likely_command()`, `Predict next command based on sequences`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Memory Recall Core`** (2 nodes): `memory_recall.py`, `NOVA - Conversation Memory Recall Search past interactions: "remember that file`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Recall Query Check`** (2 nodes): `.is_recall_query()`, `Check if user is asking about past interactions`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Image Read`** (2 nodes): `Read text from an image file`, `.read_image()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Dashboard`** (2 nodes): `._bar()`, `.generate()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Screen Area Read`** (2 nodes): `Read text from a specific screen area`, `.read_area()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Web Search`** (2 nodes): `Search the web using DuckDuckGo HTML`, `.search()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Page Fetch`** (2 nodes): `Fetch and extract text from a webpage`, `.fetch_page()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Proactive Summary`** (2 nodes): `.get_summary()`, `Get suggestion summary`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Proactive Background`** (2 nodes): `.start_background()`, `Start background suggestion checking`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Proactive Stop`** (2 nodes): `.stop()`, `Stop background checking`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Monitor Init`** (2 nodes): `.__init__()`, `.load_state()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Monitor State`** (2 nodes): `.save_state()`, `.set_threshold()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Monitor Stop`** (2 nodes): `.stop()`, `Stop background monitoring`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Large Processes`** (2 nodes): `.check_large_processes()`, `Check for processes using too much resources`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Monitor Start`** (2 nodes): `.start()`, `Start background monitoring`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Scheduler Init`** (2 nodes): `.__init__()`, `.load_tasks()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Task List`** (2 nodes): `List all scheduled tasks`, `.list_tasks()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Style Init`** (2 nodes): `.__init__()`, `._load()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Style Learner Core`** (2 nodes): `style_learner.py`, `NOVA - Style Learner Learns user's coding style, UI preferences, naming patterns`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Style Guide`** (2 nodes): `Generate a style guide from learned patterns`, `.get_style_guide()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Style Recommendations`** (2 nodes): `Get style recommendations for a new project`, `.get_recommendations_for()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Project Name Extract`** (2 nodes): `Extract project name from work request`, `.extract_project_name()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Work Request Check`** (2 nodes): `Check if user is requesting work setup`, `.is_work_request()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 1`** (1 nodes): `Set system volume (0-100)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 2`** (1 nodes): `Get network information`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 3`** (1 nodes): `Get WiFi connection info`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 4`** (1 nodes): `List available WiFi networks`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 5`** (1 nodes): `Download file from URL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 6`** (1 nodes): `List installed programs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 7`** (1 nodes): `List startup programs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 8`** (1 nodes): `List Windows services`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 9`** (1 nodes): `Start/stop/restart a service`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 10`** (1 nodes): `Minimize all windows (show desktop)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 11`** (1 nodes): `Get environment variable`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 12`** (1 nodes): `List all environment variables`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 13`** (1 nodes): `Get detailed disk information`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 14`** (1 nodes): `Empty the recycle bin`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Advanced Rationale 15`** (1 nodes): `Clear temporary files`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 1`** (1 nodes): `Execute code in the specified language`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 2`** (1 nodes): `Execute a task using Claude Code CLI`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 3`** (1 nodes): `Execute git operations`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 4`** (1 nodes): `Open a file in code editor`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 5`** (1 nodes): `Build a knowledge graph of a codebase using Graphify`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 6`** (1 nodes): `Query a project's knowledge graph and return relevant context`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 7`** (1 nodes): `Check which projects have been indexed with Graphify`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 8`** (1 nodes): `Create a new GitHub repository and optionally link it to a local folder`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 9`** (1 nodes): `Create a pull request`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 10`** (1 nodes): `List user's GitHub repositories`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 11`** (1 nodes): `Get info about a specific repo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Code Handler Rationale 12`** (1 nodes): `Auto stage all changes, commit with message, and push`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `File Ops Rationale 1`** (1 nodes): `Read contents of a file`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `File Ops Rationale 2`** (1 nodes): `Write content to a file`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `File Ops Rationale 3`** (1 nodes): `Delete a file or directory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `File Ops Rationale 4`** (1 nodes): `List contents of a directory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `File Ops Rationale 5`** (1 nodes): `Find files matching a pattern`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `File Ops Rationale 6`** (1 nodes): `Copy file or directory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `File Ops Rationale 7`** (1 nodes): `Move file or directory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Control Rationale 1`** (1 nodes): `Execute a shell command`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Control Rationale 2`** (1 nodes): `Find the full path to an executable using multiple strategies.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Control Rationale 3`** (1 nodes): `Open an application using cmd terminal`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Control Rationale 4`** (1 nodes): `Check if an application is currently running.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Control Rationale 5`** (1 nodes): `Close an application by name`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Control Rationale 6`** (1 nodes): `Get system status information`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Control Rationale 7`** (1 nodes): `List running processes`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `System Control Rationale 8`** (1 nodes): `Shutdown, restart, or sleep the PC`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Utilities Rationale 1`** (1 nodes): `Open URL in default browser`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Utilities Rationale 2`** (1 nodes): `Get current date and time`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Utilities Rationale 3`** (1 nodes): `Set a reminder (creates a scheduled task)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `NLP Rationale 1`** (1 nodes): `Calculate similarity ratio between two strings`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `NLP Rationale 2`** (1 nodes): `Find best matching candidate`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `NLP Rationale 3`** (1 nodes): `Get close matches from candidates`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Powers Rationale 1`** (1 nodes): `Analyze an image:         1. Extract text with OCR (if available)         2. Sen`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Powers Rationale 2`** (1 nodes): `Take a screenshot and analyze it`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Powers Rationale 3`** (1 nodes): `Extract text from a PDF file`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Powers Rationale 4`** (1 nodes): `Read a PDF and summarize it using Claude`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Work Setup Rationale`** (1 nodes): `Send online notification to all authorized users`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Goal Planner Doc`** (1 nodes): `Goal Planner`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Anomaly Detector Doc`** (1 nodes): `Anomaly Detector`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Smart Automation Doc`** (1 nodes): `Smart Automation`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Day 1 Performance`** (1 nodes): `Day 1 Performance`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Day 2 Performance`** (1 nodes): `Day 2 Performance`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `NovaMemorySystem` connect `Core Intelligence Hub` to `Extras Utilities`, `Memory System`, `Project Autodetect`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Why does `NOVA - Telegram Bot Handler (AGI-Enhanced) Full-featured Telegram interface with` connect `Core Intelligence Hub` to `Telegram Command Handlers`, `Agent Executor`, `Smart Automation`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `SelfReflectionSystem` connect `Core Intelligence Hub` to `Extras Utilities`, `Self-Reflection Engine`, `Project Autodetect`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 87 inferred relationships involving `Personality` (e.g. with `NOVA - Telegram Bot Handler (AGI-Enhanced) Full-featured Telegram interface with` and `Command executor for macros and automation`) actually correct?**
  _`Personality` has 87 INFERRED edges - model-reasoned connections that need verification._
- **Are the 87 inferred relationships involving `NovaMemorySystem` (e.g. with `NOVA - Telegram Bot Handler (AGI-Enhanced) Full-featured Telegram interface with` and `Command executor for macros and automation`) actually correct?**
  _`NovaMemorySystem` has 87 INFERRED edges - model-reasoned connections that need verification._
- **Are the 87 inferred relationships involving `SelfReflectionSystem` (e.g. with `NOVA - Telegram Bot Handler (AGI-Enhanced) Full-featured Telegram interface with` and `Command executor for macros and automation`) actually correct?**
  _`SelfReflectionSystem` has 87 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `ContextEngine` (e.g. with `NOVA - Telegram Bot Handler (AGI-Enhanced) Full-featured Telegram interface with` and `Command executor for macros and automation`) actually correct?**
  _`ContextEngine` has 52 INFERRED edges - model-reasoned connections that need verification._