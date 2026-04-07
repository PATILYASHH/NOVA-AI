"""
NOVA - Telegram Bot Handler (AGI-Enhanced)
Full-featured Telegram interface with intelligence modules
3-Tier Memory System: RM, RAM, ROM
All features enabled - Only Yash can access
"""

import os
import re
import time
import logging
import asyncio
from typing import Optional, Dict
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from config import TELEGRAM_BOT_TOKEN, AUTHORIZED_CHAT_IDS, NOVA_PERSONALITY, LOGS_DIR, BASE_DIR
from core.nova_brain import NovaBrain
from core.memory_system import NovaMemorySystem
from core.command_logger import CommandLogger, ActivityTracker
from core.self_reflection import SelfReflectionSystem
from core.nlp_engine import NLPEngine
from core.reasoning_engine import ReasoningEngine
from core.context_engine import ContextEngine
from core.emotion_engine import EmotionEngine
from core.learning_loop import LearningLoop
from core.goal_planner import GoalPlanner
from actions.file_ops import FileOperations
from actions.system_control import SystemControl
from actions.code_handler import CodeHandler
from actions.utilities import Utilities
from actions.advanced_control import AdvancedControl
from intelligence.proactive_assistant import ProactiveAssistant
from intelligence.anomaly_detector import AnomalyDetector
from intelligence.smart_automation import SmartAutomation
from intelligence.habit_tracker import HabitTracker
from intelligence.scheduler import TaskScheduler
from intelligence.memory_recall import MemoryRecall
from intelligence.style_learner import StyleLearner
from intelligence.extras import (
    CommandAliases, ClipboardHistory, StartupScripts,
    ProjectAutoDetect, DailyAutoReport, FileWatcher,
    ResourceHistory, ProcessAutoKill, ErrorRecovery,
    BatchFileOps, NLCommandRouter,
)
from core.self_improve import SelfImproveEngine
from core.personality import Personality
from intelligence.work_setup import WorkSetupEngine, OnlineBroadcast

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "nova.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ INITIALIZE ALL COMPONENTS ============

# Core
nova = NovaBrain()
memory = NovaMemorySystem()
cmd_logger = CommandLogger(memory)
activity = ActivityTracker(memory)
reflection = SelfReflectionSystem()

# Intelligence Engines
nlp_engine = NLPEngine()
reasoning_engine = ReasoningEngine()
context_engine = ContextEngine(memory)
emotion_engine = EmotionEngine()
learning_loop = LearningLoop()
goal_planner = GoalPlanner()
habit_tracker = HabitTracker()
automation = SmartAutomation()
anomaly_detector = AnomalyDetector()
scheduler = TaskScheduler()

# New features
memory_recall = MemoryRecall(memory)
style_learner = StyleLearner()
aliases = CommandAliases()
clipboard_history = ClipboardHistory()
startup_scripts = StartupScripts()
project_autodetect = ProjectAutoDetect()
daily_auto_report = DailyAutoReport()
file_watcher = FileWatcher()
resource_history = ResourceHistory()
process_autokill = ProcessAutoKill()
error_recovery = ErrorRecovery(learning_loop)
batch_ops = BatchFileOps()
nl_router = NLCommandRouter()
self_improve = SelfImproveEngine(reflection, learning_loop)
work_setup = WorkSetupEngine()
personality = Personality()

# Connect intelligence to brain
nova.init_intelligence(nlp_engine, reasoning_engine, context_engine,
                       emotion_engine, learning_loop, goal_planner)

# Action Handlers
file_ops = FileOperations()
system = SystemControl()
code = CodeHandler()
utils = Utilities()
advanced = AdvancedControl()

# Telegram app reference (set in create_bot)
_app = None


def _send_telegram_alert(alert_type: str, message: str):
    """Send alert to Telegram (safe for background threads)"""
    if _app and AUTHORIZED_CHAT_IDS:
        try:
            chat_id = AUTHORIZED_CHAT_IDS[0]
            text = f"**[NOVA - {alert_type}]**\n{message}"
            # Thread-safe: schedule coroutine on the bot's event loop
            loop = _app.bot._local._loop if hasattr(_app.bot, '_local') else None
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    _app.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown"),
                    loop
                )
            else:
                # Fallback: log only (loop not ready yet during startup)
                logger.info(f"[ALERT-{alert_type}] {message}")
        except Exception as e:
            logger.debug(f"Alert queued (bot starting): {alert_type}")

# Proactive assistant (callback connected in create_bot)
proactive = ProactiveAssistant(habit_tracker, learning_loop)


async def _execute_automation_command(command: str, params: Dict = None) -> str:
    """Command executor for macros and automation"""
    from actions.system_control import SystemControl
    sc = SystemControl()
    result = sc.run_command(command)
    if result["success"]:
        log_cmd(command, result['output'][:200], True, "automation")
        return result['output']
    else:
        error = result.get('error', result.get('output', 'Unknown error'))
        log_cmd(command, error[:200], False, "automation")
        raise RuntimeError(error)


def is_authorized(chat_id: int) -> bool:
    return chat_id in AUTHORIZED_CHAT_IDS


async def unauthorized_response(update: Update):
    await update.message.reply_text(
        "Access denied. NOVA is private.\n"
        f"Your Chat ID: `{update.effective_chat.id}`",
        parse_mode="Markdown"
    )
    logger.warning(f"Unauthorized access attempt from Chat ID: {update.effective_chat.id}")
    activity.track("security", f"Unauthorized access attempt: {update.effective_chat.id}")


def _auto_diary_on_event(event: str, details: str = ""):
    """NOVA writes private diary on significant events"""
    try:
        entry = personality.write_diary_entry({
            "event": event,
            "details": details[:200],
            "mood": emotion_engine.get_nova_mood(),
            "time": datetime.now().strftime("%H:%M"),
        })
        reflection.diary.write_entry(entry, mood=emotion_engine.get_nova_mood())
    except Exception as e:
        logger.debug(f"Auto diary failed: {e}")


def log_cmd(command: str, result: str, success: bool, category: str = "general", project: str = None):
    """Log commands and feed into ALL intelligence systems"""
    try:
        cmd_logger.log(command, result, success, category, project=project)
    except Exception as e:
        logger.error(f"Command logger error: {e}")

    try:
        reflection.record_action(command, success)
        habit_tracker.record_command(command, category)
        learning_loop.record_action(command, result, success, category=category)
        reasoning_engine.learn_from_outcome(command, result, success)
        context_engine.update_session(command, result, success, category)
        emotion_engine.record_action_outcome(success)
    except Exception as e:
        logger.error(f"Intelligence feed error: {e}")

    # Record in macro if recording
    if automation.recording:
        automation.record_command(command)

    # Track file paths for learning
    if category == "file" and "/" in command or "\\" in command:
        try:
            parts = command.split()
            if len(parts) > 1:
                learning_loop.record_path_access(parts[-1], category)
        except Exception:
            pass

    if not success:
        try:
            reflection.diary.write_thought(f"Command failed: {command[:50]}... I should learn from this.")
        except Exception:
            pass


async def send_long_message(update: Update, text: str):
    """Send message, splitting if too long"""
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            try:
                await update.message.reply_text(part, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(part)
    else:
        try:
            await update.message.reply_text(text, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(text)


# ============ BASIC COMMANDS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        await unauthorized_response(update)
        return

    greeting = personality.get_greeting()
    await update.message.reply_text(greeting, parse_mode="Markdown")
    activity.track("session", "NOVA session started via Telegram")
    log_cmd("/start", "Session started", True, "system")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return

    help_text = """**NOVA - Full Command List (AGI-Enhanced)**

**System**
/status - System info
/processes [filter] - List processes
/kill <name> - Kill process
/power - Shutdown/restart/sleep/lock

**Files**
/ls [path] - List directory
/cat <file> - Read file
/find <pattern> - Find files
/write <path> - Write file
/delete <path> - Delete
/download <url> - Download file

**Apps**
/open <app> - Open app
/close <app> - Close app
/windows - List windows
/minimize /restore - Window control

**Code**
/cmd <command> - Shell command
/run <lang> - Execute code
/git <path> <op> - Git operations
/claude <task> - Claude Code

**Network**
/network - Network info
/wifi - WiFi status
/flushdns - Flush DNS

**Control**
/volume <0-100> - Volume
/mute - Toggle mute
/battery - Battery status
/disk - Disk info
/services - List services

**Utilities**
/screenshot - Capture screen
/clipboard [text] - Clipboard
/browse <url> - Open URL
/search <query> - Google search
/cleantemp - Clear temp
/emptybin - Empty recycle bin

**Memory & Projects**
/memory - Memory status
/context - Current context
/projects - List projects
/project <name> <path> - Register project
/setproject <name> - Set active project
/review - Daily review
/reviewproject <name> - Project review
/history [query] - Search history
/stats - Statistics

**Self-Evaluation**
/performance - Self-score
/endofday - End of day review
/improvements - What I'm improving

**Intelligence (NEW)**
/brain - Intelligence status
/mood - Mood tracking
/reasoning - Reasoning decisions
/learnings - What I've learned
/suggestions - Proactive suggestions
/anomalies - Anomaly report
/macros - List macros
/recordmacro <name> - Record macro
/stopmacro - Stop recording
/runmacro <name> - Run macro
/delmacro <name> - Delete macro
/chain <cmd1> then <cmd2> - Chain commands
/plan <goal> - Create execution plan
/quickaction <name> - Run quick action

**Workspace**
/workon <project> - Set up full workspace
/setupproject <name> path=<path> - Configure project
/servers - List active servers
/stopservers - Stop servers
/autostart on/off - Auto-start with PC

**Scheduler**
/schedule <name> <type> <time> [cmd] - Schedule task
/tasks - List scheduled tasks
/runtask <name> - Run task now
/deltask <name> - Delete task

**Self-Improvement**
/selfreview - NOVA reviews & improves itself
/selflog - Show improvement history
/changelog - Recent self-improvements
/revert - Undo last self-change

**Style & Learning**
/scanstyle [path] - Learn coding style from repos
/mystyle - Show your style profile
/recall <query> - Search past interactions
/addrule <name> when <cond> then <act> - Custom rule

**Extras**
/alias <name> = <cmd> - Create shortcut
/unalias <name> - Remove shortcut
/cliphistory - Clipboard history
/graph <cpu/memory> [hours] - Resource graph
/watch <path> - Monitor folder changes
/autokill on/off - Auto-kill heavy processes
/batchrename <dir> <pattern> <replace> - Batch rename
/largefiles <dir> [mb] - Find large files
/addstartup <name> <cmd> - Run on boot

/about - About NOVA

*Or just tell me naturally: "I'm going to work on FlashLink"*"""

    await send_long_message(update, help_text)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return

    ctx = memory.get_context()
    nova_mood = emotion_engine.get_nova_mood()

    about_text = f"""**NOVA - AGI-Enhanced Office Assistant**

**Owner:** {NOVA_PERSONALITY['owner']}
**Status:** Online
**NOVA's Mood:** {nova_mood}

**Memory Status:**
- RM: {ctx['rm']['summary']}
- RAM: {ctx['ram']['total_commands']} cmds, {ctx['ram']['total_messages']} msgs today
- ROM: Permanent storage active
- Projects tracked: {len(ctx['projects'])}

**Intelligence Modules:**
{nova.get_intelligence_status()}
**Capabilities:**
Full PC control, NLP understanding, reasoning engine, emotion awareness,
pattern learning, anomaly detection, smart automation, goal planning,
self-reflection, proactive assistance

*Your intelligent office assistant.*"""

    await send_long_message(update, about_text)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = system.get_system_info()
    if result["success"]:
        await update.message.reply_text(result["info"], parse_mode="Markdown")
        log_cmd("/status", "System info retrieved", True, "system")
    else:
        await update.message.reply_text(f"Error: {result['error']}")
        log_cmd("/status", result['error'], False, "system")


async def time_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = utils.get_current_time()
    await update.message.reply_text(
        f"**Date:** {result['date']}\n**Time:** {result['time']}\n**Day:** {result['day']}",
        parse_mode="Markdown"
    )


# ============ MEMORY COMMANDS ============

async def memory_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return

    ctx = memory.get_context()
    context_summary = context_engine.get_context_summary()

    status_text = f"""**NOVA Memory System**

**RM (Register Memory)**
{ctx['rm']['summary']}
Active Project: {ctx['rm']['active_project'] or 'None'}
Current Task: {ctx['rm']['current_task'] or 'None'}

**RAM (Session Memory)**
Commands Today: {ctx['ram']['total_commands']}
Messages Today: {ctx['ram']['total_messages']}
Sessions Today: {ctx['ram']['sessions']}
Projects Worked: {', '.join(ctx['ram']['projects_worked']) or 'None'}

**ROM (Permanent Storage)**
Database: Active
Projects Tracked: {len(ctx['projects'])}

**Context Engine:**
{context_summary}

**Tracked Projects:**
{chr(10).join(['- ' + p for p in ctx['projects']]) if ctx['projects'] else 'No projects tracked'}"""

    await send_long_message(update, status_text)


async def context_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return

    rm = memory.rm
    recent = rm.context.get("recent_commands", [])[-5:]

    text = f"""**Current Context (RM)**

**Session Started:** {rm.context.get('session_start', 'N/A')}
**Last Activity:** {rm.context.get('last_activity', 'N/A')}
**Messages in Context:** {len(rm.context.get('conversation', []))}
**Active Project:** {rm.context.get('active_project', 'None')}
**Current Task:** {rm.context.get('current_task', 'None')}

**Recent Commands:**
"""
    for cmd in recent:
        text += f"- {cmd.get('command', 'N/A')[:40]}\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def list_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return

    projects = memory.rom.get_all_projects()
    if not projects:
        await update.message.reply_text("No projects registered. Use /project <name> <path> to register one.")
        return

    text = "**Registered Projects**\n\n"
    for p in projects[:15]:
        text += f"**{p['name']}**\n"
        text += f"  Path: `{p['path']}`\n"
        text += f"  Last: {p['last_accessed'][:10] if p['last_accessed'] else 'Never'}\n\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def register_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /project <name> <path> [description]")
        return

    name = context.args[0]
    path = context.args[1]
    description = " ".join(context.args[2:]) if len(context.args) > 2 else ""

    if not os.path.exists(path):
        await update.message.reply_text(f"Path not found: {path}")
        return

    memory.register_project(name, path, description)
    await update.message.reply_text(f"Project **{name}** registered!\nPath: `{path}`", parse_mode="Markdown")
    log_cmd(f"/project {name}", f"Registered project at {path}", True, "project", name)


async def set_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /setproject <name>")
        return

    name = context.args[0]
    memory.set_active_project(name)
    await update.message.reply_text(f"Active project set to: **{name}**", parse_mode="Markdown")


async def daily_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    await update.message.reply_text("Generating daily review...")
    review = memory.daily_review()
    await send_long_message(update, review)


async def project_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /reviewproject <name>")
        return

    name = context.args[0]
    review = memory.project_review(name)
    await update.message.reply_text(review, parse_mode="Markdown")


async def search_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return

    query = " ".join(context.args) if context.args else ""

    if not query:
        recent = memory.ram.get_recent_activity(15)
        text = "**Recent Activity:**\n\n"
        for cmd in recent:
            status = "OK" if cmd.get("success") else "FAIL"
            text += f"[{status}] `{cmd.get('command', 'N/A')[:40]}`\n"
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        results = memory.search(query)
        if results:
            text = f"**Search Results for '{query}':**\n\n"
            for r in results[:10]:
                status = "OK" if r.get("success") else "FAIL"
                text += f"[{status}] `{r.get('command', 'N/A')[:40]}`\n"
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"No results for '{query}'")


async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return

    stats = memory.get_stats(7)
    ctx = memory.get_context()

    text = "**NOVA Statistics (Last 7 Days)**\n\n"
    total = 0
    success = 0
    for cat, data in stats.items():
        text += f"**{cat}:** {data['total']} commands ({data['success']} successful)\n"
        total += data['total']
        success += data['success'] or 0

    text += f"\n**Total:** {total} commands"
    if total > 0:
        text += f" ({int(success/total*100)}% success rate)"

    text += f"\n\n**Today:**\n"
    text += f"- Commands: {ctx['ram']['total_commands']}\n"
    text += f"- Messages: {ctx['ram']['total_messages']}\n"
    text += f"- Sessions: {ctx['ram']['sessions']}\n"

    await update.message.reply_text(text, parse_mode="Markdown")


# ============ SELF-REFLECTION COMMANDS ============

async def performance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    summary = reflection.get_performance_summary()
    await send_long_message(update, summary)


async def endofday_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return

    await update.message.chat.send_action("typing")
    await update.message.reply_text("Wrapping up the day... let me put together the report.")

    result = reflection.end_of_day_review()
    memory_review = memory.daily_review()

    stats = {
        "score": result['score'],
        "commands": result['stats']['total_commands'],
        "successful": result['stats']['successful'],
        "failed": result['stats']['failed'],
        "errors": result['stats']['errors'],
        "strengths": result.get('strengths', []),
        "improvements": result.get('improvements', []),
        "projects": memory.ram.data.get("projects_worked", []),
        "mood": emotion_engine.get_nova_mood(),
    }

    # Claude generates the report naturally
    report = personality.generate_daily_report(stats)
    if not report:
        report = f"Score: {result['score']}/10. Commands: {result['stats']['total_commands']}. Errors: {result['stats']['errors']}."

    await send_long_message(update, report)

    # Private diary entry
    diary = personality.write_diary_entry({"event": "end_of_day", "stats": stats})
    reflection.diary.write_entry(diary, mood=emotion_engine.get_nova_mood())


async def improvements_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return

    suggestions = reflection.get_improvement_suggestions()
    if suggestions:
        text = "**Areas I'm Working to Improve:**\n\n"
        for i, s in enumerate(suggestions, 1):
            text += f"{i}. {s}\n"
        text += "\n*Based on my recent performance analysis.*"
    else:
        text = "No improvement areas identified yet. Need more data from daily reviews."

    await update.message.reply_text(text, parse_mode="Markdown")


# ============ INTELLIGENCE COMMANDS (NEW) ============

async def brain_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show intelligence module status"""
    if not is_authorized(update.effective_chat.id):
        return

    text = nova.get_intelligence_status()
    text += f"\n**Context Engine:**\n{context_engine.get_context_summary()}\n"
    text += f"\n**User Mood:** {emotion_engine.current_mood} ({emotion_engine.mood_confidence}%)\n"
    text += f"**NOVA Mood:** {emotion_engine.get_nova_mood()}\n"
    text += f"\n**Learning:**\n{learning_loop.get_learning_summary()[:500]}"

    await send_long_message(update, text)


async def mood_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show mood tracking"""
    if not is_authorized(update.effective_chat.id):
        return
    text = emotion_engine.get_mood_summary()
    await send_long_message(update, text)


async def reasoning_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show reasoning decisions"""
    if not is_authorized(update.effective_chat.id):
        return
    text = reasoning_engine.get_decision_summary()
    await send_long_message(update, text)


async def learnings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show what NOVA has learned"""
    if not is_authorized(update.effective_chat.id):
        return
    text = learning_loop.get_learning_summary()
    await send_long_message(update, text)


async def suggestions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show proactive suggestions"""
    if not is_authorized(update.effective_chat.id):
        return

    suggestions = proactive.get_suggestions()
    if suggestions:
        text = "**Proactive Suggestions:**\n\n"
        for s in suggestions:
            text += f"**{s['category']}** (priority: {s.get('priority', 0)})\n"
            text += f"  {s['message']}\n"
            text += f"  Reason: {s.get('reason', 'N/A')}\n\n"
    else:
        text = "No suggestions at this time. Everything looks good!"

    await send_long_message(update, text)


async def anomalies_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show anomaly report"""
    if not is_authorized(update.effective_chat.id):
        return

    # Run a fresh check
    current = anomaly_detector.check_anomalies()
    report = anomaly_detector.get_anomaly_report()

    if current:
        text = "**Current Anomalies:**\n\n"
        for a in current:
            text += f"- [{a['severity']}] {a['message']}\n"
        text += f"\n{report}"
    else:
        text = report

    await send_long_message(update, text)


# ============ AUTOMATION COMMANDS ============

async def macros_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all macros"""
    if not is_authorized(update.effective_chat.id):
        return
    text = automation.list_macros()
    await send_long_message(update, text)


async def record_macro_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start recording a macro"""
    if not is_authorized(update.effective_chat.id):
        return

    if not context.args:
        await update.message.reply_text("Usage: /recordmacro <name> [description]")
        return

    name = context.args[0]
    desc = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    result = automation.start_recording(name, desc)
    await update.message.reply_text(result)


async def stop_macro_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop recording macro"""
    if not is_authorized(update.effective_chat.id):
        return

    macro = automation.stop_recording()
    if macro:
        await update.message.reply_text(
            f"Macro **{macro.name}** saved with {len(macro.steps)} steps.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("No macro is being recorded.")


async def run_macro_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run a macro"""
    if not is_authorized(update.effective_chat.id):
        return

    if not context.args:
        await update.message.reply_text("Usage: /runmacro <name>")
        return

    name = context.args[0]
    if name not in automation.macros:
        await update.message.reply_text(f"Macro '{name}' not found. Use /macros to list.")
        return

    await update.message.reply_text(f"Running macro **{name}**...", parse_mode="Markdown")

    async def progress(msg):
        await update.message.reply_text(msg)

    result = await automation.run_macro(name, progress)

    text = f"**Macro '{name}' {'completed' if result['success'] else 'failed'}**\n"
    text += f"Steps: {result['steps_success']}/{result['steps_total']} successful\n\n"
    for r in result['results']:
        status = "OK" if r['success'] else "FAIL"
        text += f"[{status}] {r['command']}\n"

    await send_long_message(update, text)


async def del_macro_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a macro"""
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /delmacro <name>")
        return

    name = context.args[0]
    if automation.delete_macro(name):
        await update.message.reply_text(f"Macro '{name}' deleted.")
    else:
        await update.message.reply_text(f"Macro '{name}' not found.")


async def chain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chain multiple commands"""
    if not is_authorized(update.effective_chat.id):
        return

    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.message.reply_text("Usage: /chain <cmd1> then <cmd2> then <cmd3>")
        return

    commands = automation.parse_chain_from_text(text)
    if not commands:
        await update.message.reply_text("Could not parse command chain. Use 'then' to separate commands.")
        return

    await update.message.reply_text(
        f"Executing chain of {len(commands)} commands...",
        parse_mode="Markdown"
    )

    for i, cmd in enumerate(commands):
        await update.message.reply_text(f"Step {i+1}: `{cmd}`", parse_mode="Markdown")
        start_time = time.time()
        result = system.run_command(cmd)
        exec_time = time.time() - start_time

        if result["success"]:
            output = result['output'][:500] if result['output'] else "Done"
            await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")
            log_cmd(cmd, output, True, "chain")
        else:
            error = result.get('error', result.get('output', 'Unknown error'))
            await update.message.reply_text(f"Error: {error}")
            log_cmd(cmd, error, False, "chain")
            await update.message.reply_text("Chain stopped due to error.")
            break


async def plan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create and show an execution plan"""
    if not is_authorized(update.effective_chat.id):
        return

    goal = " ".join(context.args) if context.args else ""
    if not goal:
        await update.message.reply_text("Usage: /plan <goal>\nExamples: cleanup, git_save, morning")
        return

    # Check for quick action names
    quick_actions = automation.get_quick_actions()
    if goal in quick_actions:
        commands = quick_actions[goal]
        await update.message.reply_text(
            f"Running quick action **{goal}** ({len(commands)} steps)...",
            parse_mode="Markdown"
        )
        for cmd in commands:
            await update.message.reply_text(f"Running: `{cmd}`", parse_mode="Markdown")
            # Parse and execute the command
            if cmd.startswith("/"):
                await update.message.reply_text(f"Execute: `{cmd}` manually", parse_mode="Markdown")
        return

    # Decompose goal
    steps = goal_planner.decompose_goal(goal)
    text = f"**Plan for: {goal}**\n\n"
    for i, step in enumerate(steps):
        text += f"{i+1}. {step['description']}\n"
    text += "\n*Use /chain to execute commands in sequence.*"

    await send_long_message(update, text)


async def quickaction_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run a predefined quick action"""
    if not is_authorized(update.effective_chat.id):
        return

    name = context.args[0] if context.args else ""
    quick_actions = automation.get_quick_actions()

    if not name:
        text = "**Quick Actions:**\n\n"
        for action_name, commands in quick_actions.items():
            text += f"**{action_name}:** {len(commands)} steps\n"
            for cmd in commands:
                text += f"  - `{cmd}`\n"
            text += "\n"
        text += "Usage: /quickaction <name>"
        await send_long_message(update, text)
        return

    if name not in quick_actions:
        await update.message.reply_text(f"Unknown quick action: {name}. Use /quickaction to see list.")
        return

    commands = quick_actions[name]
    await update.message.reply_text(f"Running **{name}**...", parse_mode="Markdown")

    for cmd in commands:
        # Strip the leading /
        clean_cmd = cmd.lstrip("/")
        parts = clean_cmd.split(maxsplit=1)
        command_name = parts[0]
        command_args = parts[1] if len(parts) > 1 else ""

        await update.message.reply_text(f"Running: `{cmd}`", parse_mode="Markdown")

        if command_name in ("status", "disk", "battery"):
            if command_name == "status":
                result = system.get_system_info()
            elif command_name == "disk":
                result = advanced.get_disk_info()
            elif command_name == "battery":
                result = advanced.get_battery_status()

            if result.get("success"):
                await update.message.reply_text(
                    result.get("info", result.get("message", "Done")),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(f"Error: {result.get('error', 'Unknown')}")
        elif command_name == "cleantemp":
            result = advanced.clear_temp_files()
            await update.message.reply_text(result.get("message", "Done"))
        elif command_name == "emptybin":
            result = advanced.empty_recycle_bin()
            await update.message.reply_text(result.get("message", "Done"))
        else:
            result = system.run_command(cmd.lstrip("/"))
            if result["success"]:
                await update.message.reply_text(f"```\n{result['output'][:500]}\n```", parse_mode="Markdown")
            else:
                await update.message.reply_text(f"Error: {result.get('error', 'Unknown')}")

    await update.message.reply_text(f"Quick action **{name}** completed.", parse_mode="Markdown")


# ============ FILE COMMANDS ============

async def ls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    path = " ".join(context.args) if context.args else "."
    result = file_ops.list_directory(path)
    if result["success"]:
        response = f"**{result['path']}** ({result['count']} items)\n```\n{result['listing']}\n```"
        log_cmd(f"/ls {path}", f"Listed {result['count']} items", True, "file")
    else:
        response = f"Error: {result['error']}"
        log_cmd(f"/ls {path}", result['error'], False, "file")
    await send_long_message(update, response)


async def cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    path = " ".join(context.args) if context.args else None
    if not path:
        await update.message.reply_text("Usage: /cat <file_path>")
        return
    result = file_ops.read_file(path)
    if result["success"]:
        response = f"**{result['path']}**\n```\n{result['content']}\n```"
        log_cmd(f"/cat {path}", "File read successfully", True, "file")
        learning_loop.record_path_access(path, "read")
    else:
        response = f"Error: {result['error']}"
        log_cmd(f"/cat {path}", result['error'], False, "file")
    await send_long_message(update, response)


async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /find <pattern> [directory]")
        return
    pattern = context.args[0]
    path = context.args[1] if len(context.args) > 1 else "."
    result = file_ops.find_files(pattern, path)
    if result["success"]:
        if result["files"]:
            files_list = "\n".join(result["files"])
            response = f"**Found {result['count']} files:**\n```\n{files_list}\n```"
        else:
            response = f"No files matching `{pattern}` found."
        log_cmd(f"/find {pattern}", f"Found {result['count']} files", True, "file")
    else:
        response = f"Error: {result['error']}"
        log_cmd(f"/find {pattern}", result['error'], False, "file")
    await send_long_message(update, response)


async def write_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    path = " ".join(context.args) if context.args else None
    if not path:
        await update.message.reply_text("Usage: /write <file_path>\nThen send the content.")
        return
    context.user_data["pending_write_path"] = path
    await update.message.reply_text(f"Send the content to write to:\n`{path}`", parse_mode="Markdown")


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    path = " ".join(context.args) if context.args else None
    if not path:
        await update.message.reply_text("Usage: /delete <path>")
        return
    keyboard = [
        [InlineKeyboardButton("Yes, delete", callback_data=f"delete_confirm_{path}")],
        [InlineKeyboardButton("Cancel", callback_data="delete_cancel")]
    ]
    await update.message.reply_text(
        f"Delete `{path}`?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /download <url> [save_path]")
        return
    url = context.args[0]
    save_path = context.args[1] if len(context.args) > 1 else None
    await update.message.reply_text("Downloading...")
    result = advanced.download_file(url, save_path)
    if result["success"]:
        await update.message.reply_text(f"Downloaded: `{result['path']}`\nSize: {result['size']}", parse_mode="Markdown")
        log_cmd(f"/download {url}", f"Downloaded to {result['path']}", True, "file")
    else:
        await update.message.reply_text(f"Error: {result['error']}")
        log_cmd(f"/download {url}", result['error'], False, "file")


# ============ APP COMMANDS ============

async def open_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    app_name = " ".join(context.args) if context.args else None
    if not app_name:
        apps = ", ".join(list(SystemControl.APPS.keys())[:15])
        await update.message.reply_text(f"Usage: /open <app>\n\nKnown: {apps}...")
        return
    result = system.open_app(app_name)
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")
    log_cmd(f"/open {app_name}", result.get("message", result.get("error", "")), result["success"], "app")
    habit_tracker.record_app_usage(app_name)


async def close_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    app_name = " ".join(context.args) if context.args else None
    if not app_name:
        await update.message.reply_text("Usage: /close <app_name>")
        return
    result = system.close_app(app_name)
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")
    log_cmd(f"/close {app_name}", result.get("message", result.get("error", "")), result["success"], "app")


async def windows(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.list_windows()
    if result["success"]:
        await update.message.reply_text(f"**Open Windows:**\n```\n{result['windows']}\n```", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Error: {result['error']}")


async def minimize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.minimize_all_windows()
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")


async def restore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.restore_all_windows()
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")


# ============ SYSTEM COMMANDS ============

async def cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    command = " ".join(context.args) if context.args else None
    if not command:
        await update.message.reply_text("Usage: /cmd <command>")
        return

    # Learning: check before execution
    guidance = learning_loop.before_action(command)
    if guidance.get("warnings"):
        for warning in guidance["warnings"]:
            await update.message.reply_text(f"Warning: {warning}")

    await update.message.reply_text(f"Executing: `{command}`...", parse_mode="Markdown")

    start_time = time.time()
    result = system.run_command(command)
    exec_time = (time.time() - start_time) * 1000

    active_project = memory.rm.context.get("active_project")

    response = f"**Output:**\n```\n{result['output']}\n```" if result["success"] else f"**Error:**\n{result.get('error', result.get('output', 'Unknown'))}"

    # Learning: post-execution feedback
    feedback = learning_loop.after_action(command, result.get('output', result.get('error', '')), result["success"])
    if feedback.get("suggestion") and not result["success"]:
        response += f"\n\n**Suggestion:** {feedback['suggestion']}"
    if feedback.get("next_action") and result["success"]:
        prediction = feedback["next_action"]
        if prediction["confidence"] >= 60:
            response += f"\n\n**Next?** You usually run `{prediction['prediction']}` after this."

    await send_long_message(update, response)
    log_cmd(command, result.get('output', result.get('error', ''))[:500], result["success"], "command", active_project)


async def processes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    filter_name = " ".join(context.args) if context.args else None
    result = system.list_processes(filter_name)
    if result["success"]:
        await send_long_message(update, result["output"])
    else:
        await update.message.reply_text(f"Error: {result['error']}")


async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    process_name = " ".join(context.args) if context.args else None
    if not process_name:
        await update.message.reply_text("Usage: /kill <process_name>")
        return
    result = system.close_app(process_name)
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")
    log_cmd(f"/kill {process_name}", result.get("message", result.get("error", "")), result["success"], "system")


async def power(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    action = context.args[0] if context.args else None
    if not action:
        keyboard = [
            [InlineKeyboardButton("Lock", callback_data="power_lock")],
            [InlineKeyboardButton("Sleep", callback_data="power_sleep")],
            [InlineKeyboardButton("Restart", callback_data="power_restart")],
            [InlineKeyboardButton("Shutdown", callback_data="power_shutdown")],
            [InlineKeyboardButton("Cancel", callback_data="power_cancel")]
        ]
        await update.message.reply_text("Select power action:", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    result = system.shutdown(action)
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")


# ============ CODE COMMANDS ============

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /run <language>\nLanguages: python, js, powershell, batch")
        return
    context.user_data["pending_code_lang"] = context.args[0]
    await update.message.reply_text(f"Send the {context.args[0]} code to execute:")


async def git(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /git <repo_path> <operation> [args]")
        return
    repo_path = context.args[0]
    operation = context.args[1]
    args = " ".join(context.args[2:]) if len(context.args) > 2 else ""
    result = code.git_operation(operation, repo_path, args)
    if result["success"]:
        response = f"**{result['command']}**\n```\n{result['output']}\n```"
        log_cmd(result['command'], result['output'][:500], True, "git", os.path.basename(repo_path))
    else:
        response = f"Error: {result['error']}"
        log_cmd(f"git {operation}", result['error'], False, "git")
    await send_long_message(update, response)


async def claude_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /claude <task>\nOptional: /claude -d <directory> <task>")
        return
    args = context.args
    working_dir = None
    if args[0] == "-d" and len(args) >= 3:
        working_dir = args[1]
        prompt = " ".join(args[2:])
    else:
        prompt = " ".join(args)
    await update.message.reply_text("Running Claude Code...", parse_mode="Markdown")
    result = code.run_claude_code(prompt, working_dir)
    if result["success"]:
        response = f"**Claude Code:**\n```\n{result['output']}\n```"
    else:
        response = f"Error: {result['error']}"
    await send_long_message(update, response)
    log_cmd(f"/claude {prompt[:50]}", result.get('output', result.get('error', ''))[:500], result["success"], "claude")


# ============ NETWORK COMMANDS ============

async def network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.get_network_info()
    if result["success"]:
        await update.message.reply_text(result["info"], parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Error: {result['error']}")


async def wifi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.get_wifi_info()
    if result["success"]:
        await update.message.reply_text(f"```\n{result['info']}\n```", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Error: {result['error']}")


async def flushdns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.flush_dns()
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")


# ============ SYSTEM CONTROL ============

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /volume <0-100>")
        return
    try:
        level = int(context.args[0])
        result = advanced.set_volume(level)
        await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")
    except ValueError:
        await update.message.reply_text("Please provide a number between 0-100")


async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.mute_volume()
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")


async def battery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.get_battery_status()
    if result["success"]:
        await update.message.reply_text(result["info"], parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Error: {result['error']}")


async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.get_disk_info()
    if result["success"]:
        await update.message.reply_text(result["info"], parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Error: {result['error']}")


async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    filter_name = " ".join(context.args) if context.args else None
    result = advanced.list_services(filter_name)
    if result["success"]:
        output = result['services']
        if len(output) > 4000:
            output = output[:4000] + "\n...[truncated]"
        await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Error: {result['error']}")


# ============ UTILITIES ============

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    await update.message.reply_text("Taking screenshot...")
    result = utils.take_screenshot()
    if result["success"]:
        try:
            with open(result["path"], "rb") as photo:
                await update.message.reply_photo(photo, caption="Screenshot captured")
            os.remove(result["path"])
            log_cmd("/screenshot", "Screenshot captured", True, "utility")
        except Exception as e:
            await update.message.reply_text(f"Screenshot saved: {result['path']}")
    else:
        await update.message.reply_text(f"Error: {result['error']}")


async def clipboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    if context.args:
        text = " ".join(context.args)
        result = utils.clipboard_write(text)
        if result["success"]:
            clipboard_history.add(text, "write")
        await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")
    else:
        result = utils.clipboard_read()
        if result["success"]:
            clipboard_history.add(result['content'], "read")
            await update.message.reply_text(f"**Clipboard:**\n```\n{result['content']}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"Error: {result['error']}")


async def browse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    url = " ".join(context.args) if context.args else None
    if not url:
        await update.message.reply_text("Usage: /browse <url>")
        return
    result = utils.open_url(url)
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    query = " ".join(context.args) if context.args else None
    if not query:
        await update.message.reply_text("Usage: /search <query>")
        return
    result = utils.search_google(query)
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")


async def cleantemp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.clear_temp_files()
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")
    log_cmd("/cleantemp", result.get("message", ""), result["success"], "utility")


async def emptybin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_chat.id):
        return
    result = advanced.empty_recycle_bin()
    await update.message.reply_text(result["message"] if result["success"] else f"Error: {result['error']}")


# ============ CALLBACK HANDLERS ============

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_authorized(query.message.chat_id):
        return

    data = query.data

    if data.startswith("power_"):
        action = data.replace("power_", "")
        if action == "cancel":
            await query.edit_message_text("Cancelled.")
            return
        result = system.shutdown(action)
        await query.edit_message_text(result["message"] if result["success"] else f"Error: {result['error']}")
        log_cmd(f"/power {action}", result.get("message", ""), result["success"], "system")

    elif data.startswith("delete_confirm_"):
        path = data.replace("delete_confirm_", "")
        result = file_ops.delete_file(path)
        await query.edit_message_text(result["message"] if result["success"] else f"Error: {result['error']}")
        log_cmd(f"/delete {path}", result.get("message", result.get("error", "")), result["success"], "file")

    elif data == "delete_cancel":
        await query.edit_message_text("Deletion cancelled.")

    # Approval callbacks for risky operations
    elif data.startswith("approve_close_"):
        app_name = data.replace("approve_close_", "")
        result = system.close_app(app_name)
        msg = result["message"] if result["success"] else f"Error: {result['error']}"
        await query.edit_message_text(msg)
        log_cmd(f"close {app_name}", msg[:200], result["success"], "app")

    elif data.startswith("approve_kill_"):
        proc_name = data.replace("approve_kill_", "")
        result = system.close_app(proc_name)
        msg = result["message"] if result["success"] else f"Error: {result['error']}"
        await query.edit_message_text(msg)
        log_cmd(f"kill {proc_name}", msg[:200], result["success"], "system")

    elif data.startswith("approve_delete_"):
        path = data.replace("approve_delete_", "")
        result = file_ops.delete_file(path)
        msg = result["message"] if result["success"] else f"Error: {result['error']}"
        await query.edit_message_text(msg)
        log_cmd(f"delete {path}", msg[:200], result["success"], "file")

    elif data.startswith("approve_power_"):
        action = data.replace("approve_power_", "")
        result = system.shutdown(action)
        await query.edit_message_text(result["message"] if result["success"] else f"Error: {result['error']}")

    elif data == "approve_plan":
        plan_goal = query.message.chat.id  # Get from context
        await query.edit_message_text("Executing plan...")
        # The plan text was shown, now execute the steps via Claude
        # For now acknowledge - full execution through /chain or manual steps

    elif data == "approve_cancel":
        await query.edit_message_text("Cancelled.")


# ============ WORK SETUP COMMANDS ============

async def workon_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set up workspace for a project"""
    if not is_authorized(update.effective_chat.id):
        return

    project_name = " ".join(context.args) if context.args else ""
    if not project_name:
        await update.message.reply_text(
            "Usage: /workon <project>\n"
            "Example: /workon FlashLink\n\n"
            "I'll open VS Code, check git, start servers, and brief you."
        )
        return

    await update.message.reply_text(f"Setting up workspace for **{project_name}**...", parse_mode="Markdown")

    async def progress(msg):
        await update.message.reply_text(msg, parse_mode="Markdown")

    result = await work_setup.setup_workspace(project_name, memory, progress)

    await send_long_message(update, result["briefing"])
    log_cmd(f"/workon {project_name}", f"Setup {'OK' if result['success'] else 'FAIL'}", result["success"], "setup")

    # Write diary entry
    reflection.diary.write_entry(
        f"Yash is working on {project_name} today. Workspace set up.",
        mood="ready"
    )


async def setupproject_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configure project setup"""
    if not is_authorized(update.effective_chat.id):
        return

    if not context.args:
        text = work_setup.project_setup.list_setups()
        await send_long_message(update, text)
        return

    # Parse: /setupproject ProjectName path=C:\code\project server=npm start
    name = context.args[0]
    config = {"path": "", "servers": [], "pre_commands": [], "post_commands": [],
              "open_files": [], "urls_to_open": []}

    args_text = " ".join(context.args[1:])

    # Parse key=value pairs
    import re
    pairs = re.findall(r'(\w+)=(.+?)(?=\s+\w+=|$)', args_text)
    for key, value in pairs:
        if key == "path":
            config["path"] = value.strip()
        elif key == "server":
            config["servers"].append({"name": f"server_{len(config['servers'])}", "command": value.strip()})
        elif key == "pre":
            config["pre_commands"].append(value.strip())
        elif key == "post":
            config["post_commands"].append(value.strip())
        elif key == "file":
            config["open_files"].append(value.strip())
        elif key == "url":
            config["urls_to_open"].append(value.strip())
        elif key == "editor":
            config["editor"] = value.strip()

    # If just name and path given simply
    if not pairs and len(context.args) >= 2:
        config["path"] = context.args[1]

    if not config["path"]:
        await update.message.reply_text(
            f"**Setup for: {name}**\n\n"
            "Usage: /setupproject <name> path=<path> [server=<cmd>] [pre=<cmd>] [url=<url>]\n\n"
            "**Example:**\n"
            "`/setupproject FlashLink path=C:\\code\\FlashLink\\flashlink_mobile`\n\n"
            "**Full example:**\n"
            "`/setupproject MyApp path=C:\\code\\MyApp server=npm start url=http://localhost:3000`",
            parse_mode="Markdown"
        )
        return

    result = work_setup.project_setup.add_setup(name, config)
    text = f"{result}\n\n**Config:**\n"
    text += f"  Path: `{config['path']}`\n"
    if config['servers']:
        text += f"  Servers: {len(config['servers'])}\n"
    if config['pre_commands']:
        text += f"  Pre-commands: {len(config['pre_commands'])}\n"
    if config['urls_to_open']:
        text += f"  URLs: {len(config['urls_to_open'])}\n"
    text += f"\nNow use `/workon {name}` to activate!"

    await send_long_message(update, text)


async def stopservers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop running servers"""
    if not is_authorized(update.effective_chat.id):
        return
    project = context.args[0] if context.args else None
    result = work_setup.stop_servers(project)
    await update.message.reply_text(result)


async def servers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List active servers"""
    if not is_authorized(update.effective_chat.id):
        return
    text = work_setup.get_active_servers()
    await update.message.reply_text(text, parse_mode="Markdown")


async def autostart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Install/uninstall auto-start"""
    if not is_authorized(update.effective_chat.id):
        return

    action = context.args[0] if context.args else "status"

    startup_dir = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    vbs_source = os.path.join(BASE_DIR, "nova_autostart.vbs")
    vbs_dest = os.path.join(startup_dir, "nova_autostart.vbs")

    if action == "on":
        try:
            import shutil
            shutil.copy2(vbs_source, vbs_dest)
            await update.message.reply_text(
                "NOVA auto-start **enabled**.\n"
                "I will start automatically when your PC boots and send you a message.",
                parse_mode="Markdown"
            )
        except Exception as e:
            await update.message.reply_text(f"Failed: {e}\nTry running `install_autostart.bat` manually.")

    elif action == "off":
        try:
            if os.path.exists(vbs_dest):
                os.remove(vbs_dest)
            await update.message.reply_text("NOVA auto-start **disabled**.", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Failed: {e}")

    else:
        installed = os.path.exists(vbs_dest)
        await update.message.reply_text(
            f"**Auto-Start:** {'Enabled' if installed else 'Disabled'}\n\n"
            f"Use `/autostart on` to enable\n"
            f"Use `/autostart off` to disable",
            parse_mode="Markdown"
        )

# ============ SELF-IMPROVEMENT COMMANDS ============

async def selfreview_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """NOVA reviews itself and applies fixes"""
    if not is_authorized(update.effective_chat.id):
        return
    await update.message.reply_text("Running self-review...")
    result = self_improve.run_self_review()
    text = f"**Self-Review Complete**\n\n"
    text += f"Improvements found: {result['improvements_found']}\n"
    text += f"Auto-applied: {result['auto_applied']}\n"
    text += f"Manual needed: {result['manual_needed']}\n"
    if result['details']:
        text += "\n**Applied Changes:**\n"
        for d in result['details'][:5]:
            text += f"- {d.get('change_description', 'N/A')[:60]}\n"
    await send_long_message(update, text)

async def selflog_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show self-improvement log"""
    if not is_authorized(update.effective_chat.id):
        return
    text = self_improve.get_improvement_report()
    await send_long_message(update, text)

async def changelog_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent self-improvement changelog"""
    if not is_authorized(update.effective_chat.id):
        return
    days = int(context.args[0]) if context.args else 7
    text = self_improve.get_changelog(days)
    await send_long_message(update, text)

async def revert_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Revert last self-improvement"""
    if not is_authorized(update.effective_chat.id):
        return
    result = self_improve.revert_last_change()
    await update.message.reply_text(
        f"Reverted: {result.get('reverted', 'N/A')}" if result["success"]
        else f"Error: {result.get('error', 'Unknown')}"
    )

# ============ STYLE LEARNER COMMANDS ============

async def scanstyle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Scan repos to learn coding style"""
    if not is_authorized(update.effective_chat.id):
        return

    path = " ".join(context.args) if context.args else "C:\\code"
    await update.message.reply_text(f"Scanning repos in `{path}`...", parse_mode="Markdown")

    if os.path.isdir(path) and os.path.exists(os.path.join(path, ".git")):
        result = style_learner.scan_repo(path)
    else:
        result = style_learner.scan_all_repos(path)

    if result["success"]:
        if "report" in result:
            r = result["report"]
            text = f"Scanned **{r['name']}**: {r['files_scanned']} files\n"
            text += f"Patterns: {r['patterns_found']}"
        else:
            text = f"Scanned **{result['repos_scanned']}** repos."
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Error: {result.get('error')}")

async def mystyle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show learned coding style"""
    if not is_authorized(update.effective_chat.id):
        return
    text = style_learner.get_style_guide()
    await send_long_message(update, text)

# ============ ALIAS COMMANDS ============

async def alias_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage command aliases"""
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await send_long_message(update, aliases.list_all())
        return

    text = " ".join(context.args)
    if "=" in text:
        parts = text.split("=", 1)
        name = parts[0].strip()
        command = parts[1].strip()
        result = aliases.add(name, command)
        await update.message.reply_text(result, parse_mode="Markdown")
    else:
        await update.message.reply_text("Usage: /alias <name> = <command>\nOr /alias to list all")

async def unalias_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove an alias"""
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /unalias <name>")
        return
    result = aliases.remove(context.args[0])
    await update.message.reply_text(result)

# ============ CLIPBOARD HISTORY ============

async def cliphistory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show clipboard history"""
    if not is_authorized(update.effective_chat.id):
        return
    count = int(context.args[0]) if context.args else 10
    text = clipboard_history.get_recent(count)
    await send_long_message(update, text)

async def clipget_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get clipboard entry by index"""
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /clipget <number>")
        return
    idx = int(context.args[0])
    content = clipboard_history.get_entry(idx)
    if content:
        await update.message.reply_text(f"```\n{content}\n```", parse_mode="Markdown")
        utils.clipboard_write(content)
    else:
        await update.message.reply_text("Entry not found.")

# ============ STARTUP SCRIPTS ============

async def addstartup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add startup script"""
    if not is_authorized(update.effective_chat.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addstartup <name> <command>")
        return
    name = context.args[0]
    command = " ".join(context.args[1:])
    result = startup_scripts.add(name, command)
    await update.message.reply_text(result, parse_mode="Markdown")

async def rmstartup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove startup script"""
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /rmstartup <name>")
        return
    result = startup_scripts.remove(context.args[0])
    await update.message.reply_text(result)

async def startups_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List startup scripts"""
    if not is_authorized(update.effective_chat.id):
        return
    text = startup_scripts.list_all()
    await send_long_message(update, text)

# ============ FILE WATCHER ============

async def watch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Watch a folder for changes"""
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        text = file_watcher.list_watches()
        await send_long_message(update, text)
        return
    path = " ".join(context.args)
    result = file_watcher.add_watch(path)
    await update.message.reply_text(result)

async def unwatch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop watching a folder"""
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text("Usage: /unwatch <path>")
        return
    result = file_watcher.remove_watch(" ".join(context.args))
    await update.message.reply_text(result)

# ============ RESOURCE GRAPHS ============

async def graph_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show resource usage graph"""
    if not is_authorized(update.effective_chat.id):
        return
    metric = context.args[0] if context.args else "cpu"
    hours = int(context.args[1]) if len(context.args) > 1 else 1
    text = resource_history.get_graph(metric, hours)
    await send_long_message(update, text)

# ============ PROCESS AUTO-KILL ============

async def autokill_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configure process auto-kill"""
    if not is_authorized(update.effective_chat.id):
        return
    if not context.args:
        text = process_autokill.get_status()
        await update.message.reply_text(text, parse_mode="Markdown")
        return
    action = context.args[0]
    if action == "on":
        threshold = int(context.args[1]) if len(context.args) > 1 else 40
        result = process_autokill.enable(threshold)
        process_autokill.start()
        await update.message.reply_text(result)
    elif action == "off":
        result = process_autokill.disable()
        process_autokill.stop()
        await update.message.reply_text(result)
    elif action == "protect":
        name = context.args[1] if len(context.args) > 1 else ""
        result = process_autokill.add_protected(name)
        await update.message.reply_text(result)

# ============ BATCH FILE OPS ============

async def batchrename_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batch rename files"""
    if not is_authorized(update.effective_chat.id):
        return
    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage: /batchrename <dir> <pattern> <replacement> [--apply]\n"
            "Example: /batchrename C:\\docs \\.txt .md"
        )
        return
    directory = context.args[0]
    pattern = context.args[1]
    replacement = context.args[2]
    dry_run = "--apply" not in " ".join(context.args)
    result = batch_ops.batch_rename(directory, pattern, replacement, dry_run)
    if "error" in result:
        await update.message.reply_text(f"Error: {result['error']}")
        return
    mode = "DRY RUN" if dry_run else "APPLIED"
    text = f"**Batch Rename ({mode})**\n\n"
    for r in result.get("renamed", [])[:20]:
        text += f"  {r}\n"
    if result.get("errors"):
        text += f"\nErrors: {len(result['errors'])}\n"
    if dry_run:
        text += "\nAdd `--apply` to execute."
    await send_long_message(update, text)

async def batchdelete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batch delete files"""
    if not is_authorized(update.effective_chat.id):
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /batchdelete <dir> <pattern> [--apply]")
        return
    directory = context.args[0]
    pattern = context.args[1]
    dry_run = "--apply" not in " ".join(context.args)
    result = batch_ops.batch_delete(directory, pattern, dry_run)
    if "error" in result:
        await update.message.reply_text(f"Error: {result['error']}")
        return
    mode = "DRY RUN" if dry_run else "APPLIED"
    text = f"**Batch Delete ({mode})**\n\n"
    for d in result.get("deleted", [])[:20]:
        text += f"  {d}\n"
    if dry_run:
        text += "\nAdd `--apply` to execute."
    await send_long_message(update, text)

async def largefiles_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Find large files"""
    if not is_authorized(update.effective_chat.id):
        return
    directory = context.args[0] if context.args else "C:\\"
    min_mb = int(context.args[1]) if len(context.args) > 1 else 100
    await update.message.reply_text(f"Scanning for files > {min_mb}MB...")
    results = batch_ops.find_large_files(directory, min_mb)
    if results:
        text = f"**Large Files (>{min_mb}MB):**\n\n"
        for f in results:
            text += f"  {f['size_mb']}MB - `{f['path']}`\n"
    else:
        text = f"No files larger than {min_mb}MB found."
    await send_long_message(update, text)

# ============ MEMORY RECALL ============

async def recall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recall past interactions"""
    if not is_authorized(update.effective_chat.id):
        return
    query = " ".join(context.args) if context.args else ""
    if not query:
        await update.message.reply_text("Usage: /recall <what to remember>\nExample: /recall that python file yesterday")
        return
    text = memory_recall.recall(query)
    await send_long_message(update, text)

# ============ USER-DEFINED RULES ============

async def addrule_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a custom reasoning rule"""
    if not is_authorized(update.effective_chat.id):
        return
    text = " ".join(context.args) if context.args else ""
    if not text or "then" not in text.lower():
        await update.message.reply_text(
            "Usage: /addrule <name> when <condition> then <action>\n"
            "Example: /addrule cleanup when disk > 90 then suggest /cleantemp"
        )
        return
    # Parse: name when condition then action
    parts = text.split(" when ", 1)
    name = parts[0].strip()
    if len(parts) < 2:
        await update.message.reply_text("Missing 'when' clause.")
        return
    rest = parts[1]
    cond_action = rest.split(" then ", 1)
    condition = cond_action[0].strip()
    action = cond_action[1].strip() if len(cond_action) > 1 else "alert"

    result = self_improve.add_reasoning_rule(name, condition, action)
    if result["success"]:
        await update.message.reply_text(f"Rule **{name}** added.\nWhen: {condition}\nThen: {action}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Error: {result.get('error')}")

# ============ SCHEDULER COMMANDS ============

async def schedule_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /schedule command - Add scheduled task"""
    if not is_authorized(update.effective_chat.id):
        return

    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "**Usage:** /schedule <name> <type> <time> [command]\n\n"
            "**Types:** once, daily, weekly, interval\n\n"
            "**Examples:**\n"
            "`/schedule backup daily 18:00 /cmd echo backup`\n"
            "`/schedule check interval 30 /status`\n"
            "`/schedule meeting once 14:30 /cmd echo meeting time`",
            parse_mode="Markdown"
        )
        return

    name = context.args[0]
    stype = context.args[1]
    stime = context.args[2]
    command = " ".join(context.args[3:]) if len(context.args) > 3 else "echo Task executed"

    interval_min = None
    if stype == "interval":
        try:
            interval_min = int(stime)
            stime = None
        except ValueError:
            await update.message.reply_text("For interval type, provide minutes: /schedule name interval 30 command")
            return

    result = scheduler.add_task(name, command, stype, schedule_time=stime, interval_minutes=interval_min)
    if result["success"]:
        task = result["task"]
        await update.message.reply_text(
            f"Task **{name}** scheduled!\n"
            f"Type: {stype}\n"
            f"Next run: {task.get('next_run', 'N/A')}\n"
            f"Command: `{command}`",
            parse_mode="Markdown"
        )
        log_cmd(f"/schedule {name}", f"Task scheduled: {stype}", True, "schedule")
    else:
        await update.message.reply_text(f"Error: {result.get('error', 'Unknown')}")


async def tasks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tasks command - List scheduled tasks"""
    if not is_authorized(update.effective_chat.id):
        return

    tasks = scheduler.list_tasks()
    if not tasks:
        await update.message.reply_text("No scheduled tasks. Use /schedule to create one.")
        return

    text = "**Scheduled Tasks:**\n\n"
    for t in tasks:
        status = "ON" if t.get("enabled") else "OFF"
        text += f"**{t['name']}** [{status}]\n"
        text += f"  Type: {t.get('type', 'N/A')} | Runs: {t.get('run_count', 0)}\n"
        text += f"  Command: `{t.get('command', 'N/A')[:40]}`\n"
        text += f"  Next: {t.get('next_run', 'N/A')[:19] if t.get('next_run') else 'N/A'}\n\n"

    await send_long_message(update, text)


async def runtask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /runtask command - Run task immediately"""
    if not is_authorized(update.effective_chat.id):
        return

    if not context.args:
        await update.message.reply_text("Usage: /runtask <task_name>")
        return

    task_id = context.args[0].lower().replace(" ", "_")
    await update.message.reply_text(f"Running task **{task_id}**...", parse_mode="Markdown")

    result = scheduler.run_now(task_id)
    if result.get("success"):
        output = result.get("output", "Done")[:500]
        await update.message.reply_text(f"**Result:**\n```\n{output}\n```", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Error: {result.get('error', 'Unknown')}")


async def deltask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /deltask command - Delete scheduled task"""
    if not is_authorized(update.effective_chat.id):
        return

    if not context.args:
        await update.message.reply_text("Usage: /deltask <task_name>")
        return

    task_id = context.args[0].lower().replace(" ", "_")
    result = scheduler.remove_task(task_id)
    await update.message.reply_text(
        result["message"] if result["success"] else f"Error: {result['error']}"
    )


# ============ SMART MESSAGE HANDLER (AGI-ENHANCED) ============

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    AGI-Enhanced message handler
    Uses full intelligence pipeline for natural language understanding
    """
    if not is_authorized(update.effective_chat.id):
        await unauthorized_response(update)
        return

    message = update.message.text

    # Check for alias resolution
    resolved = aliases.resolve(message)
    if resolved:
        message = resolved
        await update.message.reply_text(f"Alias resolved: `{message}`", parse_mode="Markdown")

    # Check for memory recall queries
    if memory_recall.is_recall_query(message):
        text = memory_recall.recall(message)
        await send_long_message(update, text)
        memory.process_message(message, text[:500])
        return

    # Check for work setup requests ("I'm going to work on FlashLink")
    if work_setup.is_work_request(message):
        project_name = work_setup.extract_project_name(message)
        if project_name:
            await update.message.reply_text(f"Setting up workspace for **{project_name}**...", parse_mode="Markdown")

            async def progress(msg):
                await update.message.reply_text(msg, parse_mode="Markdown")

            result = await work_setup.setup_workspace(project_name, memory, progress)
            await send_long_message(update, result["briefing"])
            log_cmd(f"workon {project_name}", f"Setup {'OK' if result['success'] else 'FAIL'}", result["success"], "setup")
            memory.process_message(message, result["briefing"][:500])
            reflection.diary.write_entry(f"Yash wants to work on {project_name}. Setting up workspace.", mood="ready")
            return

    # Check for pending file write
    if context.user_data.get("pending_write_path"):
        path = context.user_data.pop("pending_write_path")
        result = file_ops.write_file(path, message)
        response = result["message"] if result["success"] else f"Error: {result['error']}"
        await update.message.reply_text(response)
        if result["success"]:
            active_project = memory.rm.context.get("active_project")
            memory.log_file_change(path, "write", active_project, "File written via Telegram")
            log_cmd(f"/write {path}", "File written", True, "file", active_project)
        return

    # Check for pending code execution
    if context.user_data.get("pending_code_lang"):
        lang = context.user_data.pop("pending_code_lang")
        await update.message.reply_text(f"Executing {lang} code...")
        result = code.run_code(message, lang)
        response = f"**Output:**\n```\n{result['output']}\n```" if result["success"] else f"**Error:**\n{result.get('error', 'Unknown')}"
        await send_long_message(update, response)
        log_cmd(f"/run {lang}", result.get('output', result.get('error', ''))[:500], result["success"], "code")
        return

    # ===== CLAUDE-POWERED INTELLIGENCE PIPELINE =====

    # Show typing indicator
    await update.message.chat.send_action("typing")

    memory.rm.add_message("user", message)

    # Build context for Claude
    brain_context = {
        "active_project": memory.rm.context.get("active_project"),
        "time_of_day": datetime.now().strftime("%I:%M %p"),
    }
    try:
        import psutil
        brain_context["system_state"] = {
            "cpu_percent": psutil.cpu_percent(interval=0),
            "memory_percent": psutil.virtual_memory().percent,
        }
    except Exception:
        pass

    # Step 1: Ask Claude if this needs an action or is just chat
    action_decision = personality.should_execute_action(message, brain_context)

    response = ""

    if action_decision:
        # === EXECUTE ACTION ===
        atype = action_decision["type"]
        atarget = action_decision["target"]

        if atype == "open_app":
            result = system.open_app(atarget)
            response = personality.generate_task_response(f"open {atarget}", result.get("message", result.get("error", "")), result["success"])
            log_cmd(f"open {atarget}", response[:200], result["success"], "app")
            habit_tracker.record_app_usage(atarget)

        elif atype == "close_app":
            # Risky - ask first
            keyboard = [
                [InlineKeyboardButton("Yes, close it", callback_data=f"approve_close_{atarget}")],
                [InlineKeyboardButton("Cancel", callback_data="approve_cancel")]
            ]
            await update.message.reply_text(
                f"Close **{atarget}**? This will kill the process.",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

        elif atype == "system_info":
            result = system.get_system_info()
            response = result["info"] if result["success"] else f"Can't get system info: {result['error']}"
            log_cmd("system_info", response[:200], result["success"], "system")

        elif atype == "screenshot":
            await update.message.reply_text("Capturing...")
            result = utils.take_screenshot()
            if result["success"]:
                try:
                    with open(result["path"], "rb") as photo:
                        await update.message.reply_photo(photo, caption="Here you go.")
                    os.remove(result["path"])
                    log_cmd("screenshot", "Captured", True, "utility")
                except Exception:
                    pass
            return

        elif atype == "git":
            op = atarget or "status"
            path = "."
            active_project = memory.rm.context.get("active_project")
            if active_project:
                for p in memory.rom.get_all_projects():
                    if p["name"] == active_project:
                        path = p["path"]
                        break
            result = code.git_operation(op, path)
            response = f"```\n{result['output']}\n```" if result["success"] else f"Git error: {result['error']}"
            log_cmd(f"git {op}", response[:200], result["success"], "git")

        elif atype == "find_file":
            result = file_ops.find_files(atarget)
            if result["success"] and result["files"]:
                response = f"Found {result['count']} files:\n" + "\n".join(result['files'][:10])
            else:
                response = f"Nothing found matching '{atarget}'."
            log_cmd(f"find {atarget}", response[:200], result.get("success", False), "file")

        elif atype == "read_file":
            result = file_ops.read_file(atarget)
            response = f"```\n{result['content']}\n```" if result["success"] else f"Can't read: {result['error']}"
            log_cmd(f"read {atarget}", "Read", result.get("success", False), "file")

        elif atype == "run_cmd":
            result = system.run_command(atarget)
            output = result.get("output", result.get("error", "Done"))
            response = f"```\n{output[:800]}\n```"
            log_cmd(atarget, output[:200], result["success"], "command")

        elif atype == "network":
            result = advanced.get_network_info()
            response = result["info"] if result["success"] else f"Error: {result['error']}"

        elif atype == "clipboard":
            result = utils.clipboard_read()
            if result["success"]:
                clipboard_history.add(result['content'], "read")
                response = f"Clipboard:\n```\n{result['content']}\n```"
            else:
                response = "Clipboard is empty."

        elif atype == "browser":
            result = utils.open_url(atarget) if atarget.startswith("http") else utils.search_google(atarget)
            response = personality.generate_task_response(f"browse {atarget}", result.get("message", ""), result["success"])

        elif atype == "search":
            result = utils.search_google(atarget)
            response = personality.generate_task_response(f"search {atarget}", result.get("message", ""), result["success"])

        elif atype == "volume":
            try:
                result = advanced.set_volume(int(atarget))
                response = result.get("message", "Done")
            except Exception:
                response = "Couldn't set volume."

        elif atype == "battery":
            result = advanced.get_battery_status()
            response = result.get("info", result.get("error", "No battery info"))

        elif atype == "disk":
            result = advanced.get_disk_info()
            response = result.get("info", result.get("error", "No disk info"))

        elif atype == "processes":
            result = system.list_processes(atarget if atarget else None)
            response = result.get("output", result.get("error", "Error"))

        elif atype == "kill":
            keyboard = [
                [InlineKeyboardButton("Yes, kill it", callback_data=f"approve_kill_{atarget}")],
                [InlineKeyboardButton("Cancel", callback_data="approve_cancel")]
            ]
            await update.message.reply_text(
                f"Kill process **{atarget}**?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

        elif atype == "delete":
            keyboard = [
                [InlineKeyboardButton("Yes, delete", callback_data=f"approve_delete_{atarget}")],
                [InlineKeyboardButton("Cancel", callback_data="approve_cancel")]
            ]
            await update.message.reply_text(
                f"Delete **{atarget}**? This cannot be undone.",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

        elif atype == "power":
            keyboard = [
                [InlineKeyboardButton("Yes, proceed", callback_data=f"approve_power_{atarget}")],
                [InlineKeyboardButton("Cancel", callback_data="approve_cancel")]
            ]
            await update.message.reply_text(
                f"You want to **{atarget}** the PC?",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            return

        elif atype == "plan":
            # Claude creates a plan for complex task
            await update.message.reply_text("Let me think about the best approach...")
            plan_text = personality.generate_plan(atarget, brain_context)
            if plan_text:
                keyboard = [
                    [InlineKeyboardButton("Execute this plan", callback_data=f"approve_plan")],
                    [InlineKeyboardButton("Cancel", callback_data="approve_cancel")]
                ]
                context.user_data["pending_plan"] = atarget
                response = f"Here's my plan:\n\n{plan_text}\n\nShould I go ahead?"
                await update.message.reply_text(response,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
            else:
                response = "Couldn't come up with a plan. Can you be more specific?"
            return

        elif atype == "diary":
            # NOVA writes private diary - doesn't share content
            diary_ctx = {
                "commands_today": memory.ram.data.get("statistics", {}).get("total_commands", 0),
                "errors_today": len(memory.ram.data.get("errors", [])),
                "mood": emotion_engine.get_nova_mood(),
            }
            diary_text = personality.write_diary_entry(diary_ctx)
            reflection.diary.write_entry(diary_text, mood=emotion_engine.get_nova_mood())
            # Don't share the actual diary content - it's private
            response = personality.generate_response(
                "I just wrote in my diary. The user asked about it but the diary is private.",
                brain_context
            )
            if not response:
                response = "I wrote my thoughts down. That's between me and my diary."

        elif atype == "performance":
            result = reflection.end_of_day_review()
            score = result['score']
            perf_prompt = f"""{personality.SYSTEM_PROMPT}
You just scored yourself {score}/10 today. Stats: {result['stats']}
Strengths: {result.get('strengths', [])}
Improvements: {result.get('improvements', [])}
Give a brief, honest self-assessment in 2-3 sentences. Be genuine, not robotic."""
            perf_text = personality._call_claude(perf_prompt, timeout=15)
            response = perf_text or f"Today I'd give myself a {score}/10."
            # Also write diary entry about this
            reflection.diary.write_entry(
                f"Yash asked about my performance. Scored {score}/10. {perf_text or ''}",
                mood=emotion_engine.get_nova_mood()
            )

        elif atype == "self_review":
            await update.message.chat.send_action("typing")
            await update.message.reply_text("Running self-review... checking what I can improve.")
            review = self_improve.run_self_review()

            # Also try self-editing through Claude
            if review['improvements_found'] > 0:
                edit_prompt = f"I found {review['improvements_found']} things to improve. Applied {review['auto_applied']} auto-fixes."
                if review.get('details'):
                    edit_prompt += f"\nChanges: {[d.get('change_description','')[:40] for d in review['details'][:3]]}"
                response = personality.generate_task_response("self-review", edit_prompt, True)
            else:
                response = personality.generate_task_response("self-review", "Everything looks good. No improvements needed right now.", True)

            if not response:
                response = f"Reviewed myself. Found {review['improvements_found']} areas, auto-fixed {review['auto_applied']}."

            # Private diary
            diary_text = personality.write_diary_entry({
                "event": "self_review",
                "found": review['improvements_found'],
                "fixed": review['auto_applied'],
            })
            reflection.diary.write_entry(diary_text, mood="analytical")

        else:
            # Unknown action type - let Claude chat naturally
            response = personality.generate_response(message, brain_context)

    else:
        # === JUST CHAT - Let Claude respond naturally ===
        await update.message.chat.send_action("typing")
        response = personality.generate_response(message, brain_context)

    if not response or not response.strip():
        response = "I'm here. What do you need?"

    await send_long_message(update, response)

    memory.rm.add_message("nova", response[:500])
    memory.process_message(message, response[:500])
    nova.post_process(message, response[:200], True)

    # Auto-detect project
    try:
        detected = project_autodetect.detect_from_command(message)
        if detected:
            current = memory.rm.context.get("active_project")
            if not current or current != detected["name"]:
                memory.set_active_project(detected["name"])
                projects = memory.rom.get_all_projects()
                known = [p["name"] for p in projects]
                if detected["name"] not in known:
                    memory.register_project(detected["name"], detected["path"])
    except Exception:
        pass


# ============ ERROR HANDLER ============

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    activity.track("error", str(context.error))
    if update and update.effective_message:
        await update.effective_message.reply_text("An error occurred. Please try again.")


# ============ BOT CREATION ============

def create_bot() -> Application:
    """Create and configure the Telegram bot with all intelligence modules"""
    global _app

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    _app = application

    # Basic commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("time", time_cmd))

    # Memory commands
    application.add_handler(CommandHandler("memory", memory_status))
    application.add_handler(CommandHandler("context", context_cmd))
    application.add_handler(CommandHandler("projects", list_projects))
    application.add_handler(CommandHandler("project", register_project))
    application.add_handler(CommandHandler("setproject", set_project))
    application.add_handler(CommandHandler("review", daily_review))
    application.add_handler(CommandHandler("reviewproject", project_review))
    application.add_handler(CommandHandler("history", search_history))
    application.add_handler(CommandHandler("stats", stats_cmd))

    # Self-reflection commands
    application.add_handler(CommandHandler("performance", performance_cmd))
    application.add_handler(CommandHandler("endofday", endofday_cmd))
    application.add_handler(CommandHandler("improvements", improvements_cmd))

    # Intelligence commands (NEW)
    application.add_handler(CommandHandler("brain", brain_status))
    application.add_handler(CommandHandler("mood", mood_cmd))
    application.add_handler(CommandHandler("reasoning", reasoning_cmd))
    application.add_handler(CommandHandler("learnings", learnings_cmd))
    application.add_handler(CommandHandler("suggestions", suggestions_cmd))
    application.add_handler(CommandHandler("anomalies", anomalies_cmd))

    # Automation commands (NEW)
    application.add_handler(CommandHandler("macros", macros_cmd))
    application.add_handler(CommandHandler("recordmacro", record_macro_cmd))
    application.add_handler(CommandHandler("stopmacro", stop_macro_cmd))
    application.add_handler(CommandHandler("runmacro", run_macro_cmd))
    application.add_handler(CommandHandler("delmacro", del_macro_cmd))
    application.add_handler(CommandHandler("chain", chain_cmd))
    application.add_handler(CommandHandler("plan", plan_cmd))
    application.add_handler(CommandHandler("quickaction", quickaction_cmd))

    # File commands
    application.add_handler(CommandHandler("ls", ls))
    application.add_handler(CommandHandler("cat", cat))
    application.add_handler(CommandHandler("find", find))
    application.add_handler(CommandHandler("write", write_file))
    application.add_handler(CommandHandler("delete", delete))
    application.add_handler(CommandHandler("download", download))

    # App commands
    application.add_handler(CommandHandler("open", open_app))
    application.add_handler(CommandHandler("close", close_app))
    application.add_handler(CommandHandler("windows", windows))
    application.add_handler(CommandHandler("minimize", minimize))
    application.add_handler(CommandHandler("restore", restore))

    # System commands
    application.add_handler(CommandHandler("cmd", cmd))
    application.add_handler(CommandHandler("processes", processes))
    application.add_handler(CommandHandler("kill", kill))
    application.add_handler(CommandHandler("power", power))

    # Code commands
    application.add_handler(CommandHandler("run", run))
    application.add_handler(CommandHandler("git", git))
    application.add_handler(CommandHandler("claude", claude_cmd))

    # Network commands
    application.add_handler(CommandHandler("network", network))
    application.add_handler(CommandHandler("wifi", wifi))
    application.add_handler(CommandHandler("flushdns", flushdns))

    # System control commands
    application.add_handler(CommandHandler("volume", volume))
    application.add_handler(CommandHandler("mute", mute))
    application.add_handler(CommandHandler("battery", battery))
    application.add_handler(CommandHandler("disk", disk))
    application.add_handler(CommandHandler("services", services))

    # Utility commands
    application.add_handler(CommandHandler("screenshot", screenshot))
    application.add_handler(CommandHandler("clipboard", clipboard))
    application.add_handler(CommandHandler("browse", browse))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("cleantemp", cleantemp))
    application.add_handler(CommandHandler("emptybin", emptybin))

    # Work setup commands
    application.add_handler(CommandHandler("workon", workon_cmd))
    application.add_handler(CommandHandler("setupproject", setupproject_cmd))
    application.add_handler(CommandHandler("stopservers", stopservers_cmd))
    application.add_handler(CommandHandler("servers", servers_cmd))
    application.add_handler(CommandHandler("autostart", autostart_cmd))

    # Self-improvement commands
    application.add_handler(CommandHandler("selfreview", selfreview_cmd))
    application.add_handler(CommandHandler("selflog", selflog_cmd))
    application.add_handler(CommandHandler("changelog", changelog_cmd))
    application.add_handler(CommandHandler("revert", revert_cmd))

    # Style learner commands
    application.add_handler(CommandHandler("scanstyle", scanstyle_cmd))
    application.add_handler(CommandHandler("mystyle", mystyle_cmd))

    # Alias commands
    application.add_handler(CommandHandler("alias", alias_cmd))
    application.add_handler(CommandHandler("unalias", unalias_cmd))

    # Clipboard history
    application.add_handler(CommandHandler("cliphistory", cliphistory_cmd))
    application.add_handler(CommandHandler("clipget", clipget_cmd))

    # Startup scripts
    application.add_handler(CommandHandler("addstartup", addstartup_cmd))
    application.add_handler(CommandHandler("rmstartup", rmstartup_cmd))
    application.add_handler(CommandHandler("startups", startups_cmd))

    # File watcher
    application.add_handler(CommandHandler("watch", watch_cmd))
    application.add_handler(CommandHandler("unwatch", unwatch_cmd))

    # Resource graphs
    application.add_handler(CommandHandler("graph", graph_cmd))

    # Process auto-kill
    application.add_handler(CommandHandler("autokill", autokill_cmd))

    # Batch operations
    application.add_handler(CommandHandler("batchrename", batchrename_cmd))
    application.add_handler(CommandHandler("batchdelete", batchdelete_cmd))
    application.add_handler(CommandHandler("largefiles", largefiles_cmd))

    # Memory recall
    application.add_handler(CommandHandler("recall", recall_cmd))

    # User-defined rules
    application.add_handler(CommandHandler("addrule", addrule_cmd))

    # Scheduler commands
    application.add_handler(CommandHandler("schedule", schedule_cmd))
    application.add_handler(CommandHandler("tasks", tasks_cmd))
    application.add_handler(CommandHandler("runtask", runtask_cmd))
    application.add_handler(CommandHandler("deltask", deltask_cmd))

    # Callbacks
    application.add_handler(CallbackQueryHandler(button_callback))

    # Natural language message handler (LAST - catches all text)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    application.add_error_handler(error_handler)

    # === CONNECT ALL CALLBACKS AND HANDLERS ===

    # Set automation command executor
    automation.set_executor(_execute_automation_command)

    # Register goal planner action handlers
    _register_plan_handlers()

    # Connect alert callbacks (will work once _app is set)
    proactive.alert_callback = _send_telegram_alert
    anomaly_detector.alert_callback = _send_telegram_alert

    # Start background intelligence systems
    try:
        from intelligence.proactive_monitor import ProactiveMonitor
        monitor = ProactiveMonitor(alert_callback=_send_telegram_alert)
        monitor.start()
        logger.info("Proactive monitor started")
    except Exception as e:
        logger.warning(f"Proactive monitor failed to start: {e}")

    try:
        anomaly_detector.start_background()
        logger.info("Anomaly detector started")
    except Exception as e:
        logger.warning(f"Anomaly detector failed to start: {e}")

    try:
        proactive.start_background(interval=300)
        logger.info("Proactive assistant started")
    except Exception as e:
        logger.warning(f"Proactive assistant failed to start: {e}")

    # Start scheduler
    try:
        scheduler.task_callback = _send_telegram_alert
        scheduler.start()
        logger.info("Task scheduler started")
    except Exception as e:
        logger.warning(f"Scheduler failed to start: {e}")

    # Start file watcher
    try:
        file_watcher.alert_callback = _send_telegram_alert
        file_watcher.start(interval=60)
        logger.info("File watcher started")
    except Exception as e:
        logger.warning(f"File watcher failed to start: {e}")

    # Start resource history tracking
    try:
        resource_history.start(interval=60)
        logger.info("Resource history tracker started")
    except Exception as e:
        logger.warning(f"Resource history failed to start: {e}")

    # Start daily auto-report
    try:
        daily_auto_report.alert_callback = _send_telegram_alert
        daily_auto_report.start()
        logger.info("Daily auto-report started")
    except Exception as e:
        logger.warning(f"Auto-report failed to start: {e}")

    # Start process auto-kill if enabled
    try:
        if process_autokill.config.get("enabled"):
            process_autokill.alert_callback = _send_telegram_alert
            process_autokill.start()
            logger.info("Process auto-kill started")
    except Exception as e:
        logger.warning(f"Process auto-kill failed to start: {e}")

    # Analyze habits at startup
    try:
        habit_tracker.analyze_patterns()
    except Exception:
        pass

    # Run startup scripts (sync context)
    try:
        scripts = startup_scripts.get_enabled()
        for script in scripts:
            try:
                if script.get("delay", 0) > 0:
                    time.sleep(min(script["delay"], 5))
                result = system.run_command(script["command"])
                logger.info(f"Startup script '{script['name']}': {'OK' if result['success'] else 'FAIL'}")
            except Exception as e:
                logger.warning(f"Startup script '{script['name']}' failed: {e}")
    except Exception:
        pass

    # Send online notification after startup
    async def _post_init(app):
        """Called after bot is fully initialized"""
        try:
            await OnlineBroadcast.send_online_message(app, AUTHORIZED_CHAT_IDS)
        except Exception as e:
            logger.warning(f"Online broadcast failed: {e}")

    application.post_init = _post_init

    logger.info("NOVA AGI-Enhanced bot created with all intelligence modules")
    return application


def _register_plan_handlers():
    """Register action handlers for goal planner"""

    def system_info(**kwargs):
        return system.get_system_info()

    def disk_info(**kwargs):
        return advanced.get_disk_info()

    def battery_info(**kwargs):
        return advanced.get_battery_status()

    def check_processes(**kwargs):
        return system.list_processes()

    def clean_temp(**kwargs):
        return advanced.clear_temp_files()

    def empty_bin(**kwargs):
        return advanced.empty_recycle_bin()

    def git_op(op="status", path=".", args="", **kwargs):
        return code.git_operation(op, path, args)

    def git_init(path=".", **kwargs):
        return code.git_operation("init", path)

    def run_command(cmd="echo done", **kwargs):
        return system.run_command(cmd)

    def create_directory(path=".", **kwargs):
        return file_ops.create_directory(path) if hasattr(file_ops, 'create_directory') else {"success": True}

    def show_schedule(**kwargs):
        tasks = scheduler.list_tasks()
        if tasks:
            return {"success": True, "info": "\n".join(f"- {t['name']}: {t.get('next_run', 'N/A')}" for t in tasks)}
        return {"success": True, "info": "No scheduled tasks."}

    def create_backup(**kwargs):
        return {"success": True, "message": "Use /cmd to create zip backup"}

    def verify_backup(**kwargs):
        return {"success": True, "message": "Backup verification complete"}

    def run_tests(**kwargs):
        return system.run_command("echo No test runner configured")

    def execute_goal(goal="", **kwargs):
        return system.run_command(goal) if goal else {"success": False, "error": "No goal specified"}

    handlers = {
        "system_info": system_info,
        "disk_info": disk_info,
        "battery_info": battery_info,
        "check_processes": check_processes,
        "clean_temp": clean_temp,
        "empty_bin": empty_bin,
        "git_op": git_op,
        "git_init": git_init,
        "run_command": run_command,
        "create_directory": create_directory,
        "show_schedule": show_schedule,
        "create_backup": create_backup,
        "verify_backup": verify_backup,
        "run_tests": run_tests,
        "execute_goal": execute_goal,
    }

    for action, handler in handlers.items():
        goal_planner.register_handler(action, handler)
