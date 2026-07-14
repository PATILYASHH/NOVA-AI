# Graph Report - .  (2026-07-12)

## Corpus Check
- 46 files · ~79,112 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1631 nodes · 5734 edges · 171 communities detected
- Extraction: 39% EXTRACTED · 61% INFERRED · 0% AMBIGUOUS · INFERRED: 3476 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `Personality` - 128 edges
2. `is_authorized()` - 120 edges
3. `NovaMemorySystem` - 108 edges
4. `SelfReflectionSystem` - 104 edges
5. `AgentExecutor` - 80 edges
6. `ContextEngine` - 80 edges
7. `CodeHandler` - 79 edges
8. `FileOperations` - 79 edges
9. `SystemControl` - 79 edges
10. `ProactiveMonitor` - 79 edges

## Surprising Connections (you probably didn't know these)
- `NOVA - Emotion Engine User mood tracking, empathetic responses, tone adaptation` --uses--> `DynamicIdentity`  [INFERRED]
  core\emotion_engine.py → core\dynamic_identity.py
- `Load mood keywords from dynamic config if available` --uses--> `DynamicIdentity`  [INFERRED]
  core\emotion_engine.py → core\dynamic_identity.py
- `Detect mood from user message` --uses--> `DynamicIdentity`  [INFERRED]
  core\emotion_engine.py → core\dynamic_identity.py
- `_TypingKeeper` --uses--> `NovaMemorySystem`  [INFERRED]
  telegram_bot.py → core\memory_system.py
- `_TypingKeeper` --uses--> `SelfReflectionSystem`  [INFERRED]
  telegram_bot.py → core\self_reflection.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.14
Nodes (154): AdvancedControl, Advanced system control operations, AgentExecutor, AgentStep, NOVA - Autonomous Agent Executor Chains Claude Code + Git + GitHub CLI to execu, A single step in an autonomous execution plan, Autonomous agent that can execute multi-step tasks:     - Create full projects, Get status of all active/recent tasks (+146 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (104): can_edit_with_approval(), can_freely_edit(), check_action(), DynamicIdentity, NOVA - Dynamic Identity System Loads personality, emotions, knowledge from edit, Get current emotion configuration, Get mood detection keywords from dynamic config, Get expressions for a specific emotion (+96 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (132): about(), addrule_cmd(), addstartup_cmd(), alias_cmd(), anomalies_cmd(), apps_cmd(), _auto_diary_on_event(), autokill_cmd() (+124 more)

### Community 3 - "Community 3"
Cohesion: 0.02
Nodes (45): NOVA - Advanced Control Module Window management, volume, network, downloads, a, NOVA - Anomaly Detector Detect unusual system behavior, security threats, patt, _get_gh_username(), github_create_repo(), NOVA - Code Handler Module Handles code execution, editing, Claude Code integra, Get authenticated GitHub username from gh cli, NOVA - Command Logger Automatic logging of all commands and activities, Decorator to automatically track command execution     Use on telegram command (+37 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (48): DailyReviewer, ProjectTracker, RandomAccessMemory, NOVA - 3-Tier Memory System  Memory Architecture: 1. RM (Register Memory) - C, Set currently active project, Set current task being worked on, Get summary of current context for NOVA, Clear register memory (new session) (+40 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (33): LearningsDatabase, NOVADiary, PerformanceTracker, NOVA - Self Reflection System End of day self-evaluation, performance scoring,, Record a mistake made, Record task completion, Calculate self-score out of 10 based on today's performance         Returns sco, Get scores from past days (+25 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (27): CodePatcher, NOVA - Self-Improvement Engine NOVA reviews its own performance, identifies wea, Safely apply code patches to NOVA's own files, Create backup before modification, Restore file from backup, Apply a text replacement patch to a file, Add content to a file (end, start, or after a marker), Generate a readable diff (+19 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (20): AdaptiveStrategy, BehaviorProfile, from_dict(), NOVA - Learning Loop Actual feedback loop where past learnings influence future, Predict what user will do next based on workflow patterns, Record an action and its outcome - the core learning input, Tracks and learns from behavioral patterns, Record when user corrects NOVA's behavior (+12 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (19): Enum, Plan, NOVA - Goal Planner Autonomous task decomposition, multi-step execution, plann, Check if plan is fully executed, Format plan status for display, Create an execution plan for a goal         Either from templates or custom tas, Match a goal to a template, A single task in a plan (+11 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (24): best_match(), ConversationTracker, EntityExtractor, FuzzyMatcher, IntentClassifier, NOVA - Natural Language Processing Engine Advanced NLU without external APIs -, Extract all entities from text, Extract primary action verb and its category (+16 more)

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (19): CausalChain, DecisionNode, NOVA - Reasoning Engine Rule-based logic, decision trees, cause-effect analysis, Predict causes of an effect, Load persistent reasoning state, Save persistent reasoning state, Register built-in reasoning rules, A node in a decision tree (+11 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (12): CommandChain, from_dict(), Macro, NOVA - Smart Automation Command chaining, macros, workflow automation, and int, Start recording a macro, Record a command during macro recording, Stop recording and save macro, A recorded macro - sequence of commands (+4 more)

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (13): AutoBackup, NOVA - Auto Backup System Automatically backup important files and projects, Check if path should be excluded from backup, Backup a specific path, Backup all configured targets, Keep only the last N backups for a name, Automatic backup system for files and projects, Get backup system status (+5 more)

### Community 13 - "Community 13"
Cohesion: 0.09
Nodes (11): Auto stage, commit, and push all changes, Create a new GitHub repo and optionally link to local directory, Execute any arbitrary task autonomously using Claude Code.         This is the, Extract project name, language, type from description, Build a specific, actionable prompt for Claude Code to generate the project, Create a .gitignore file based on language, Generate a simple commit message from changes, Send progress notification (+3 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (11): Find past interactions relevant to current query, Get preferences relevant to current intent, Get active project context, Detect if this is a follow-up to previous conversation, Get current time period, Get current session duration in minutes, Get a quick system state summary, Get work pattern insights for current time (+3 more)

### Community 15 - "Community 15"
Cohesion: 0.1
Nodes (10): Scan all repos under a base path, Collect relevant files from repo, Analyze naming conventions, Extract color schemes and theme preferences, Detect tech stack from files, Analyze commonly used packages, Learn project structure patterns, Learn code patterns: error handling, imports, etc. (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.11
Nodes (8): Run all anomaly checks, Check for CPU usage anomaly, Check for memory usage anomaly, Check for new/unknown processes, Check for disk space anomalies, Check for network anomalies, Load baselines and state, Update baseline measurements of normal behavior

### Community 17 - "Community 17"
Cohesion: 0.12
Nodes (7): ProjectSetup, NOVA - Work Setup System When user says "I'm going to work on FlashLink", NOVA:, Full workspace setup for a project         Returns step-by-step results, Configuration for setting up a project workspace, Generate a work briefing, Add or update project setup config, Get project setup config

### Community 18 - "Community 18"
Cohesion: 0.12
Nodes (8): Analyze today's errors and generate fix proposals using Claude.         Called, Group similar errors together, Generate a fix proposal for a group of related errors, Parse Claude's response into a structured proposal, Apply a fix proposal using Claude Code.         This is the actual self-coding, Reject a fix proposal, Save proposals to disk, Get summary of today's errors

### Community 19 - "Community 19"
Cohesion: 0.14
Nodes (8): NOVA - Smart Task Planner Breaks big tasks into steps, shows live-updating prog, Extract JSON from Claude's response, Execute a plan step by step with live Telegram updates, Update the live progress message on Telegram, A plan with steps that can be tracked, Format the plan as a live-updating progress message, Use Claude to break a task into steps, TaskPlan

### Community 20 - "Community 20"
Cohesion: 0.14
Nodes (6): Ensure log file exists, Update date if day changed, Log a command execution, Get all commands from today, Get today's command count, Get commands by category

### Community 21 - "Community 21"
Cohesion: 0.18
Nodes (7): Search file operation history, Search project change history, Search today's session memory, Format recall results for display, Search memory and return relevant past interactions, Extract meaningful search terms from query, Calculate relevance score

### Community 22 - "Community 22"
Cohesion: 0.19
Nodes (7): Get suggestions based on user habits, Get suggestions based on system state, Get work pattern suggestions, Get workflow continuation suggestions, Get time-aware suggestions, Check if we can make a suggestion in this category, Get current proactive suggestions         Called periodically or on user intera

### Community 23 - "Community 23"
Cohesion: 0.16
Nodes (6): Remove a scheduled task, Enable or disable a task, Calculate next run time for a task, Background scheduler loop, Run a task immediately, Add a scheduled task          Args:             name: Task name (unique ident

### Community 24 - "Community 24"
Cohesion: 0.18
Nodes (7): BotStatus, NOVA - Bot Status Manager Updates NOVA's Telegram name and bio based on what it, Reset to online status immediately, Manages NOVA's Telegram display name and short description (bio).     Uses styl, Set the bot instance (called after bot is created), Update NOVA's status on Telegram., Reset status to online after delay

### Community 25 - "Community 25"
Cohesion: 0.17
Nodes (1): batch_delete()

### Community 26 - "Community 26"
Cohesion: 0.18
Nodes (5): Clear today's errors after they've been reviewed, Record an error that occurred during operation, Record a command that failed, Record when NOVA misclassified a message, Record a crash/exception

### Community 27 - "Community 27"
Cohesion: 0.24
Nodes (5): Background monitoring loop with morning briefing, Send a morning briefing to Yash, Send evening summary + self-coding proposals, Get current system status, Send alert only for important things, no spam

### Community 28 - "Community 28"
Cohesion: 0.31
Nodes (9): append_global_md(), extract_last_messages(), load_env(), main(), NOVA Claude Reporter - Stop Hook Registered as a global Claude Code Stop hook. F, Return (last_user_text, last_assistant_text) from a session transcript., Send a message, return message_id or None., record_session() (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.22
Nodes (3): Record work on a project, Analyze recorded data for patterns, Record a command execution

### Community 30 - "Community 30"
Cohesion: 0.25
Nodes (3): Learn a user preference from behavior, Load learned user preferences, Save user preferences

### Community 31 - "Community 31"
Cohesion: 0.25
Nodes (2): Load mood keywords from dynamic config if available, Detect mood from user message

### Community 32 - "Community 32"
Cohesion: 0.36
Nodes (6): _escape_html_safe(), _make_final_text(), make_progress_bar(), NOVA - Smart Response System Advanced Telegram chat features: - Native "typing, send_progress_bar(), send_typing_response()

### Community 33 - "Community 33"
Cohesion: 0.29
Nodes (3): Load NOVA's persistent memory, Save to NOVA's persistent memory, Append an entry to memory

### Community 34 - "Community 34"
Cohesion: 0.29
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 0.29
Nodes (3): Get a quick answer by searching and summarizing, Search for text inside files, Find function/class definition

### Community 36 - "Community 36"
Cohesion: 0.29
Nodes (1): Dismiss a category of suggestions

### Community 37 - "Community 37"
Cohesion: 0.33
Nodes (1): Record current running apps

### Community 38 - "Community 38"
Cohesion: 0.5
Nodes (4): main(), NOVA Watchdog - Keeps NOVA always running. Restarts NOVA if it crashes. Run thi, Run NOVA and return when it exits, run_nova()

### Community 39 - "Community 39"
Cohesion: 0.5
Nodes (3): auto_push(), NOVA - Auto Push to GitHub Runs daily at 5PM to commit and push all changes to, Commit all changes and push to GitHub

### Community 40 - "Community 40"
Cohesion: 0.5
Nodes (2): Legacy intent parsing - used as fallback (matches NLP engine intent names), Full intelligence pipeline for processing a message         Returns structured

### Community 41 - "Community 41"
Cohesion: 0.5
Nodes (0): 

### Community 42 - "Community 42"
Cohesion: 0.5
Nodes (2): Generate commit message from current diff, Stage all, generate message, commit

### Community 43 - "Community 43"
Cohesion: 0.5
Nodes (2): Take screenshot and read all text from it, Check if specific text is visible on screen

### Community 44 - "Community 44"
Cohesion: 0.67
Nodes (1): Ensure activity file exists

### Community 45 - "Community 45"
Cohesion: 0.67
Nodes (1): Review code changes using Claude

### Community 46 - "Community 46"
Cohesion: 0.67
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Get recent activities

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Update session context after each action

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Generate a smart prefix for responses based on context         Returns None if

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Register an action handler

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Cancel an active plan

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Suggest a plan based on intent and entities

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Get summary of what NOVA has learned

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Format NOVA's response with personality and emotional awareness

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Initialize intelligence modules (called after all modules are created)

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Called after an action is executed - feeds back into learning

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Get context-aware greeting

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Return NOVA's capabilities

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Get status of all intelligence modules

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Get historical success rate for an action

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Get summary of recent decisions

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Get a human-readable message for a reasoning action

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (0): 

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Format a proposal for Telegram display

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Get all pending (unapproved) proposals

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Get changelog of recent improvements

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Cancel a running plan

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Format a plan message with Accept/Reject/Changes buttons

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Start background anomaly detection

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): Check if a command is anomalous based on history

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Stop background detection

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): Get entry by index (1-based, newest first)

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (0): 

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): Predict next command based on sequences

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): Get predictions based on current time and patterns

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): NOVA - Conversation Memory Recall Search past interactions: "remember that file

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): Check if user is asking about past interactions

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): Read text from an image file

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): Search the web using DuckDuckGo HTML

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): Fetch and extract text from a webpage

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (0): 

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): Read text from a specific screen area

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): Stop background checking

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (1): Start background suggestion checking

### Community 85 - "Community 85"
Cohesion: 1.0
Nodes (1): Get suggestion summary

### Community 86 - "Community 86"
Cohesion: 1.0
Nodes (0): 

### Community 87 - "Community 87"
Cohesion: 1.0
Nodes (0): 

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (1): Stop background monitoring

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (1): Check for processes using excessive resources (only alert for extreme cases)

### Community 90 - "Community 90"
Cohesion: 1.0
Nodes (1): Start background monitoring

### Community 91 - "Community 91"
Cohesion: 1.0
Nodes (0): 

### Community 92 - "Community 92"
Cohesion: 1.0
Nodes (1): List all scheduled tasks

### Community 93 - "Community 93"
Cohesion: 1.0
Nodes (1): Set the command executor function

### Community 94 - "Community 94"
Cohesion: 1.0
Nodes (1): Get predefined quick action chains

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (1): Parse a chain of commands from natural language

### Community 96 - "Community 96"
Cohesion: 1.0
Nodes (1): Get automation summary

### Community 97 - "Community 97"
Cohesion: 1.0
Nodes (1): NOVA - Style Learner Learns user's coding style, UI preferences, naming pattern

### Community 98 - "Community 98"
Cohesion: 1.0
Nodes (0): 

### Community 99 - "Community 99"
Cohesion: 1.0
Nodes (1): Generate a style guide from learned patterns

### Community 100 - "Community 100"
Cohesion: 1.0
Nodes (1): Get style recommendations for a new project

### Community 101 - "Community 101"
Cohesion: 1.0
Nodes (1): Check if user is requesting work setup

### Community 102 - "Community 102"
Cohesion: 1.0
Nodes (1): Extract project name from work request

### Community 103 - "Community 103"
Cohesion: 1.0
Nodes (1): Set system volume (0-100)

### Community 104 - "Community 104"
Cohesion: 1.0
Nodes (1): Get network information

### Community 105 - "Community 105"
Cohesion: 1.0
Nodes (1): Get WiFi connection info

### Community 106 - "Community 106"
Cohesion: 1.0
Nodes (1): List available WiFi networks

### Community 107 - "Community 107"
Cohesion: 1.0
Nodes (1): Download file from URL

### Community 108 - "Community 108"
Cohesion: 1.0
Nodes (1): List installed programs

### Community 109 - "Community 109"
Cohesion: 1.0
Nodes (1): List startup programs

### Community 110 - "Community 110"
Cohesion: 1.0
Nodes (1): List Windows services

### Community 111 - "Community 111"
Cohesion: 1.0
Nodes (1): Start/stop/restart a service

### Community 112 - "Community 112"
Cohesion: 1.0
Nodes (1): Minimize all windows (show desktop)

### Community 113 - "Community 113"
Cohesion: 1.0
Nodes (1): Get environment variable

### Community 114 - "Community 114"
Cohesion: 1.0
Nodes (1): List all environment variables

### Community 115 - "Community 115"
Cohesion: 1.0
Nodes (1): Get detailed disk information

### Community 116 - "Community 116"
Cohesion: 1.0
Nodes (1): Empty the recycle bin

### Community 117 - "Community 117"
Cohesion: 1.0
Nodes (1): Clear temporary files

### Community 118 - "Community 118"
Cohesion: 1.0
Nodes (1): Execute code in the specified language

### Community 119 - "Community 119"
Cohesion: 1.0
Nodes (1): Execute a task using Claude Code CLI via stdin pipe

### Community 120 - "Community 120"
Cohesion: 1.0
Nodes (1): Execute git operations

### Community 121 - "Community 121"
Cohesion: 1.0
Nodes (1): Open a file in code editor

### Community 122 - "Community 122"
Cohesion: 1.0
Nodes (1): Build a knowledge graph of a codebase using Graphify

### Community 123 - "Community 123"
Cohesion: 1.0
Nodes (1): Query a project's knowledge graph and return relevant context

### Community 124 - "Community 124"
Cohesion: 1.0
Nodes (1): Check which projects have been indexed with Graphify

### Community 125 - "Community 125"
Cohesion: 1.0
Nodes (1): Create a new GitHub repository and link it to a local folder

### Community 126 - "Community 126"
Cohesion: 1.0
Nodes (1): Create a pull request

### Community 127 - "Community 127"
Cohesion: 1.0
Nodes (1): List user's GitHub repositories

### Community 128 - "Community 128"
Cohesion: 1.0
Nodes (1): Get info about a specific repo

### Community 129 - "Community 129"
Cohesion: 1.0
Nodes (1): Auto stage all changes, commit with message, and push

### Community 130 - "Community 130"
Cohesion: 1.0
Nodes (1): Read contents of a file

### Community 131 - "Community 131"
Cohesion: 1.0
Nodes (1): Write content to a file

### Community 132 - "Community 132"
Cohesion: 1.0
Nodes (1): Delete a file or directory

### Community 133 - "Community 133"
Cohesion: 1.0
Nodes (1): List contents of a directory

### Community 134 - "Community 134"
Cohesion: 1.0
Nodes (1): Find files matching a pattern

### Community 135 - "Community 135"
Cohesion: 1.0
Nodes (1): Copy file or directory

### Community 136 - "Community 136"
Cohesion: 1.0
Nodes (1): Move file or directory

### Community 137 - "Community 137"
Cohesion: 1.0
Nodes (1): Execute a shell command

### Community 138 - "Community 138"
Cohesion: 1.0
Nodes (1): Find the full path to an executable using multiple strategies.

### Community 139 - "Community 139"
Cohesion: 1.0
Nodes (1): Find an installed app's Start Menu shortcut by fuzzy name match.         Return

### Community 140 - "Community 140"
Cohesion: 1.0
Nodes (1): Open an application: resolved exe -> Start Menu shortcut -> shell start

### Community 141 - "Community 141"
Cohesion: 1.0
Nodes (1): Check if an application is currently running.

### Community 142 - "Community 142"
Cohesion: 1.0
Nodes (1): Close an application by name

### Community 143 - "Community 143"
Cohesion: 1.0
Nodes (1): Get system status information

### Community 144 - "Community 144"
Cohesion: 1.0
Nodes (1): List running processes

### Community 145 - "Community 145"
Cohesion: 1.0
Nodes (1): Shutdown, restart, or sleep the PC

### Community 146 - "Community 146"
Cohesion: 1.0
Nodes (1): Open URL in default browser

### Community 147 - "Community 147"
Cohesion: 1.0
Nodes (1): Check if a WhatsApp app handles the whatsapp:// protocol

### Community 148 - "Community 148"
Cohesion: 1.0
Nodes (1): Share a file to Yash's WhatsApp:         1. Copy the file to the clipboard (as

### Community 149 - "Community 149"
Cohesion: 1.0
Nodes (1): Get current date and time

### Community 150 - "Community 150"
Cohesion: 1.0
Nodes (1): Set a reminder (creates a scheduled task)

### Community 151 - "Community 151"
Cohesion: 1.0
Nodes (1): Check if NOVA can edit this file without permission

### Community 152 - "Community 152"
Cohesion: 1.0
Nodes (1): Check if NOVA can edit this file with Yash's approval

### Community 153 - "Community 153"
Cohesion: 1.0
Nodes (1): NOVA cannot delete files without explicit permission

### Community 154 - "Community 154"
Cohesion: 1.0
Nodes (1): Check if an action is allowed

### Community 155 - "Community 155"
Cohesion: 1.0
Nodes (1): Calculate similarity ratio between two strings

### Community 156 - "Community 156"
Cohesion: 1.0
Nodes (1): Find best matching candidate

### Community 157 - "Community 157"
Cohesion: 1.0
Nodes (1): Get close matches from candidates

### Community 158 - "Community 158"
Cohesion: 1.0
Nodes (1): Show Telegram's native "typing..." indicator while generating,         then sen

### Community 159 - "Community 159"
Cohesion: 1.0
Nodes (1): Create the final response with optional thinking spoiler.         Uses HTML for

### Community 160 - "Community 160"
Cohesion: 1.0
Nodes (1): Escape HTML chars but preserve code blocks and formatting.         Converts mar

### Community 161 - "Community 161"
Cohesion: 1.0
Nodes (1): Send a message with quick-action buttons at the bottom.         actions: [{"lab

### Community 162 - "Community 162"
Cohesion: 1.0
Nodes (1): Send a text-based progress bar

### Community 163 - "Community 163"
Cohesion: 1.0
Nodes (1): Create a text progress bar

### Community 164 - "Community 164"
Cohesion: 1.0
Nodes (1): Analyze an image:         1. Extract text with OCR (if available)         2. S

### Community 165 - "Community 165"
Cohesion: 1.0
Nodes (1): Let Claude actually SEE an image via its Read tool (real vision).         This

### Community 166 - "Community 166"
Cohesion: 1.0
Nodes (1): Capture the current screen and let NOVA genuinely SEE it.         Returns {"suc

### Community 167 - "Community 167"
Cohesion: 1.0
Nodes (1): Take a screenshot and analyze it (delegates to real-vision see_screen).

### Community 168 - "Community 168"
Cohesion: 1.0
Nodes (1): Extract text from a PDF file

### Community 169 - "Community 169"
Cohesion: 1.0
Nodes (1): Read a PDF and summarize it using Claude

### Community 170 - "Community 170"
Cohesion: 1.0
Nodes (1): Send online notification to all authorized users

## Knowledge Gaps
- **516 isolated node(s):** `NOVA - Auto Push to GitHub Runs daily at 5PM to commit and push all changes to`, `Commit all changes and push to GitHub`, `NOVA - Configuration Your Professional AI Office Assistant`, `NOVA - Main Entry Point (AGI-Enhanced) Professional AI Office Assistant for Rem`, `Print NOVA startup banner` (+511 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 47`** (2 nodes): `.get_recent()`, `Get recent activities`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (2 nodes): `.update_session()`, `Update session context after each action`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (2 nodes): `.generate_response_prefix()`, `Generate a smart prefix for responses based on context         Returns None if`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (2 nodes): `.register_handler()`, `Register an action handler`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (2 nodes): `.cancel_plan()`, `Cancel an active plan`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (2 nodes): `.suggest_plan()`, `Suggest a plan based on intent and entities`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (2 nodes): `.get_learning_summary()`, `Get summary of what NOVA has learned`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (2 nodes): `.format_response()`, `Format NOVA's response with personality and emotional awareness`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (2 nodes): `.init_intelligence()`, `Initialize intelligence modules (called after all modules are created)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (2 nodes): `.post_process()`, `Called after an action is executed - feeds back into learning`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (2 nodes): `.get_greeting()`, `Get context-aware greeting`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (2 nodes): `.get_help_message()`, `Return NOVA's capabilities`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (2 nodes): `.get_intelligence_status()`, `Get status of all intelligence modules`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (2 nodes): `Get historical success rate for an action`, `.get_success_rate()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (2 nodes): `Get summary of recent decisions`, `.get_decision_summary()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (2 nodes): `Get a human-readable message for a reasoning action`, `.get_action_message()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (2 nodes): `.__init__()`, `._load()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (2 nodes): `Format a proposal for Telegram display`, `.format_proposal_message()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (2 nodes): `Get all pending (unapproved) proposals`, `.get_pending_proposals()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (2 nodes): `Get changelog of recent improvements`, `.get_changelog()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (2 nodes): `Cancel a running plan`, `.cancel_plan()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (2 nodes): `Format a plan message with Accept/Reject/Changes buttons`, `.get_plan_message_with_buttons()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (2 nodes): `.start_background()`, `Start background anomaly detection`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (2 nodes): `.check_command_anomaly()`, `Check if a command is anomalous based on history`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (2 nodes): `.stop()`, `Stop background detection`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (2 nodes): `.get_entry()`, `Get entry by index (1-based, newest first)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (2 nodes): `.__init__()`, `._load()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (2 nodes): `.get_next_likely_command()`, `Predict next command based on sequences`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (2 nodes): `.get_predictions()`, `Get predictions based on current time and patterns`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (2 nodes): `memory_recall.py`, `NOVA - Conversation Memory Recall Search past interactions: "remember that file`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (2 nodes): `.is_recall_query()`, `Check if user is asking about past interactions`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (2 nodes): `Read text from an image file`, `.read_image()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (2 nodes): `Search the web using DuckDuckGo HTML`, `.search()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (2 nodes): `Fetch and extract text from a webpage`, `.fetch_page()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (2 nodes): `._bar()`, `.generate()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (2 nodes): `Read text from a specific screen area`, `.read_area()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (2 nodes): `.stop()`, `Stop background checking`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (2 nodes): `.start_background()`, `Start background suggestion checking`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 85`** (2 nodes): `.get_summary()`, `Get suggestion summary`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 86`** (2 nodes): `.__init__()`, `.load_state()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 87`** (2 nodes): `.save_state()`, `.set_threshold()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (2 nodes): `.stop()`, `Stop background monitoring`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (2 nodes): `.check_large_processes()`, `Check for processes using excessive resources (only alert for extreme cases)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 90`** (2 nodes): `.start()`, `Start background monitoring`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 91`** (2 nodes): `.__init__()`, `.load_tasks()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 92`** (2 nodes): `List all scheduled tasks`, `.list_tasks()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 93`** (2 nodes): `Set the command executor function`, `.set_executor()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 94`** (2 nodes): `Get predefined quick action chains`, `.get_quick_actions()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (2 nodes): `Parse a chain of commands from natural language`, `.parse_chain_from_text()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 96`** (2 nodes): `Get automation summary`, `.get_summary()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 97`** (2 nodes): `style_learner.py`, `NOVA - Style Learner Learns user's coding style, UI preferences, naming pattern`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 98`** (2 nodes): `.__init__()`, `._load()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 99`** (2 nodes): `Generate a style guide from learned patterns`, `.get_style_guide()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 100`** (2 nodes): `Get style recommendations for a new project`, `.get_recommendations_for()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 101`** (2 nodes): `Check if user is requesting work setup`, `.is_work_request()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 102`** (2 nodes): `Extract project name from work request`, `.extract_project_name()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 103`** (1 nodes): `Set system volume (0-100)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 104`** (1 nodes): `Get network information`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 105`** (1 nodes): `Get WiFi connection info`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 106`** (1 nodes): `List available WiFi networks`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 107`** (1 nodes): `Download file from URL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 108`** (1 nodes): `List installed programs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 109`** (1 nodes): `List startup programs`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 110`** (1 nodes): `List Windows services`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 111`** (1 nodes): `Start/stop/restart a service`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 112`** (1 nodes): `Minimize all windows (show desktop)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 113`** (1 nodes): `Get environment variable`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 114`** (1 nodes): `List all environment variables`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 115`** (1 nodes): `Get detailed disk information`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 116`** (1 nodes): `Empty the recycle bin`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 117`** (1 nodes): `Clear temporary files`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 118`** (1 nodes): `Execute code in the specified language`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 119`** (1 nodes): `Execute a task using Claude Code CLI via stdin pipe`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 120`** (1 nodes): `Execute git operations`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 121`** (1 nodes): `Open a file in code editor`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 122`** (1 nodes): `Build a knowledge graph of a codebase using Graphify`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 123`** (1 nodes): `Query a project's knowledge graph and return relevant context`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 124`** (1 nodes): `Check which projects have been indexed with Graphify`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 125`** (1 nodes): `Create a new GitHub repository and link it to a local folder`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 126`** (1 nodes): `Create a pull request`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 127`** (1 nodes): `List user's GitHub repositories`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 128`** (1 nodes): `Get info about a specific repo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 129`** (1 nodes): `Auto stage all changes, commit with message, and push`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 130`** (1 nodes): `Read contents of a file`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 131`** (1 nodes): `Write content to a file`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 132`** (1 nodes): `Delete a file or directory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 133`** (1 nodes): `List contents of a directory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 134`** (1 nodes): `Find files matching a pattern`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 135`** (1 nodes): `Copy file or directory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 136`** (1 nodes): `Move file or directory`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 137`** (1 nodes): `Execute a shell command`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 138`** (1 nodes): `Find the full path to an executable using multiple strategies.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 139`** (1 nodes): `Find an installed app's Start Menu shortcut by fuzzy name match.         Return`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 140`** (1 nodes): `Open an application: resolved exe -> Start Menu shortcut -> shell start`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 141`** (1 nodes): `Check if an application is currently running.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 142`** (1 nodes): `Close an application by name`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 143`** (1 nodes): `Get system status information`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 144`** (1 nodes): `List running processes`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 145`** (1 nodes): `Shutdown, restart, or sleep the PC`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 146`** (1 nodes): `Open URL in default browser`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 147`** (1 nodes): `Check if a WhatsApp app handles the whatsapp:// protocol`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 148`** (1 nodes): `Share a file to Yash's WhatsApp:         1. Copy the file to the clipboard (as`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 149`** (1 nodes): `Get current date and time`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 150`** (1 nodes): `Set a reminder (creates a scheduled task)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 151`** (1 nodes): `Check if NOVA can edit this file without permission`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 152`** (1 nodes): `Check if NOVA can edit this file with Yash's approval`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 153`** (1 nodes): `NOVA cannot delete files without explicit permission`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 154`** (1 nodes): `Check if an action is allowed`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 155`** (1 nodes): `Calculate similarity ratio between two strings`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 156`** (1 nodes): `Find best matching candidate`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 157`** (1 nodes): `Get close matches from candidates`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 158`** (1 nodes): `Show Telegram's native "typing..." indicator while generating,         then sen`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 159`** (1 nodes): `Create the final response with optional thinking spoiler.         Uses HTML for`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 160`** (1 nodes): `Escape HTML chars but preserve code blocks and formatting.         Converts mar`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 161`** (1 nodes): `Send a message with quick-action buttons at the bottom.         actions: [{"lab`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 162`** (1 nodes): `Send a text-based progress bar`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 163`** (1 nodes): `Create a text progress bar`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 164`** (1 nodes): `Analyze an image:         1. Extract text with OCR (if available)         2. S`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 165`** (1 nodes): `Let Claude actually SEE an image via its Read tool (real vision).         This`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 166`** (1 nodes): `Capture the current screen and let NOVA genuinely SEE it.         Returns {"suc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 167`** (1 nodes): `Take a screenshot and analyze it (delegates to real-vision see_screen).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 168`** (1 nodes): `Extract text from a PDF file`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 169`** (1 nodes): `Read a PDF and summarize it using Claude`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 170`** (1 nodes): `Send online notification to all authorized users`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Personality` connect `Community 1` to `Community 0`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Why does `NovaMemorySystem` connect `Community 1` to `Community 0`, `Community 4`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `SelfReflectionSystem` connect `Community 1` to `Community 0`, `Community 5`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 103 inferred relationships involving `Personality` (e.g. with `NOVA - Terminal Interface Talk to NOVA directly from your terminal. No Telegram` and `Check if NOVA is properly set up`) actually correct?**
  _`Personality` has 103 INFERRED edges - model-reasoned connections that need verification._
- **Are the 95 inferred relationships involving `NovaMemorySystem` (e.g. with `_TypingKeeper` and `NOVA - Telegram Bot Handler (AGI-Enhanced) Full-featured Telegram interface wit`) actually correct?**
  _`NovaMemorySystem` has 95 INFERRED edges - model-reasoned connections that need verification._
- **Are the 95 inferred relationships involving `SelfReflectionSystem` (e.g. with `_TypingKeeper` and `NOVA - Telegram Bot Handler (AGI-Enhanced) Full-featured Telegram interface wit`) actually correct?**
  _`SelfReflectionSystem` has 95 INFERRED edges - model-reasoned connections that need verification._
- **Are the 63 inferred relationships involving `AgentExecutor` (e.g. with `_TypingKeeper` and `NOVA - Telegram Bot Handler (AGI-Enhanced) Full-featured Telegram interface wit`) actually correct?**
  _`AgentExecutor` has 63 INFERRED edges - model-reasoned connections that need verification._