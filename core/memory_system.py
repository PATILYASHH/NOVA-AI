"""
NOVA - 3-Tier Memory System

Memory Architecture:
1. RM (Register Memory) - Current context, low storage, fast access
   - Stores current conversation context
   - Cleared on session end
   - Quick retrieval for immediate responses

2. RAM (Random Access Memory) - Session memory, bigger context
   - Stores conversation history, learned patterns
   - Persists across conversations within a day
   - JSON files for flexibility

3. ROM (Read Only Memory) - Permanent storage
   - SQLite database for permanent records
   - Never deleted, always available
   - Historical data, project info, commands log
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
RM_DIR = os.path.join(MEMORY_DIR, "RM")
RAM_DIR = os.path.join(MEMORY_DIR, "RAM")
ROM_DIR = os.path.join(MEMORY_DIR, "ROM")
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DAILY_LOGS_DIR = os.path.join(LOGS_DIR, "daily")
COMMANDS_LOGS_DIR = os.path.join(LOGS_DIR, "commands")

# Ensure directories exist
for dir_path in [RM_DIR, RAM_DIR, ROM_DIR, PROJECTS_DIR, DAILY_LOGS_DIR, COMMANDS_LOGS_DIR]:
    os.makedirs(dir_path, exist_ok=True)


class RegisterMemory:
    """
    RM - Register Memory
    Current context storage, fast access, cleared on restart
    """

    def __init__(self):
        self.context_file = os.path.join(RM_DIR, "current_context.json")
        self.context = self._load()

    def _load(self) -> Dict:
        """Load current context"""
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {
            "session_start": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "conversation": [],
            "current_task": None,
            "active_project": None,
            "recent_commands": [],
            "temp_data": {}
        }

    def _save(self):
        """Save context to file"""
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.context, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"RM save error: {e}")

    def add_message(self, role: str, content: str):
        """Add message to conversation context"""
        self.context["conversation"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 20 messages for quick context
        self.context["conversation"] = self.context["conversation"][-20:]
        self.context["last_activity"] = datetime.now().isoformat()
        self._save()

    def add_command(self, command: str, result: str):
        """Track recent command"""
        self.context["recent_commands"].append({
            "command": command,
            "result": result[:500],  # Truncate result
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 10 commands
        self.context["recent_commands"] = self.context["recent_commands"][-10:]
        self._save()

    def set_active_project(self, project: str):
        """Set currently active project"""
        self.context["active_project"] = project
        self._save()

    def set_current_task(self, task: str):
        """Set current task being worked on"""
        self.context["current_task"] = task
        self._save()

    def get_context_summary(self) -> str:
        """Get summary of current context for NOVA"""
        conv_count = len(self.context["conversation"])
        recent_cmds = len(self.context["recent_commands"])
        project = self.context.get("active_project", "None")
        task = self.context.get("current_task", "None")

        return f"Session: {conv_count} messages, {recent_cmds} commands | Project: {project} | Task: {task}"

    def clear(self):
        """Clear register memory (new session)"""
        self.context = {
            "session_start": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "conversation": [],
            "current_task": None,
            "active_project": None,
            "recent_commands": [],
            "temp_data": {}
        }
        self._save()

    def store_temp(self, key: str, value: Any):
        """Store temporary data"""
        self.context["temp_data"][key] = value
        self._save()

    def get_temp(self, key: str) -> Any:
        """Get temporary data"""
        return self.context["temp_data"].get(key)


class RandomAccessMemory:
    """
    RAM - Random Access Memory
    Session-persistent memory, bigger context, day-wise storage
    """

    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.session_file = os.path.join(RAM_DIR, f"session_{self.today}.json")
        self.data = self._load()

    def _load(self) -> Dict:
        """Load today's session data"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {
            "date": self.today,
            "conversations": [],
            "commands_executed": [],
            "files_modified": [],
            "projects_worked": [],
            "insights": [],
            "errors": [],
            "statistics": {
                "total_commands": 0,
                "total_messages": 0,
                "session_count": 0
            }
        }

    def _save(self):
        """Save session data"""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"RAM save error: {e}")

    def log_conversation(self, user_msg: str, nova_response: str):
        """Log a conversation exchange"""
        self.data["conversations"].append({
            "user": user_msg,
            "nova": nova_response,
            "timestamp": datetime.now().isoformat()
        })
        self.data["statistics"]["total_messages"] += 1
        self._save()

    def log_command(self, command: str, result: str, success: bool, category: str = "general"):
        """Log command execution with details"""
        self.data["commands_executed"].append({
            "command": command,
            "result": result[:1000],
            "success": success,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        self.data["statistics"]["total_commands"] += 1
        self._save()

    def log_file_change(self, file_path: str, action: str, project: str = None):
        """Log file modification"""
        self.data["files_modified"].append({
            "path": file_path,
            "action": action,
            "project": project,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def log_project_work(self, project: str, action: str, details: str = ""):
        """Log project activity"""
        # Check if project already logged today
        if project not in self.data["projects_worked"]:
            self.data["projects_worked"].append(project)

        # This will also be logged to project-specific tracking
        self._save()

    def add_insight(self, insight: str, category: str = "general"):
        """Add learned insight or pattern"""
        self.data["insights"].append({
            "insight": insight,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def log_error(self, error: str, context: str = ""):
        """Log error for review"""
        self.data["errors"].append({
            "error": error,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def increment_session(self):
        """Mark new session start"""
        self.data["statistics"]["session_count"] += 1
        self._save()

    def get_daily_summary(self) -> Dict:
        """Get summary of today's activity"""
        return {
            "date": self.today,
            "total_commands": self.data["statistics"]["total_commands"],
            "total_messages": self.data["statistics"]["total_messages"],
            "sessions": self.data["statistics"]["session_count"],
            "projects_worked": self.data["projects_worked"],
            "files_modified": len(self.data["files_modified"]),
            "errors": len(self.data["errors"])
        }

    def get_recent_activity(self, count: int = 10) -> List[Dict]:
        """Get recent commands and activities"""
        return self.data["commands_executed"][-count:]


class ReadOnlyMemory:
    """
    ROM - Read Only Memory (Permanent Storage)
    SQLite database for permanent records
    """

    def __init__(self):
        self.db_path = os.path.join(ROM_DIR, "nova_memory.db")
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Commands history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                result TEXT,
                success INTEGER,
                category TEXT,
                project TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                path TEXT,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_accessed DATETIME
            )
        ''')

        # Project changes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                change_type TEXT,
                file_path TEXT,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Daily summaries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                total_commands INTEGER,
                total_messages INTEGER,
                projects_worked TEXT,
                summary TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Conversations archive
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                nova_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insights and learnings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insight TEXT NOT NULL,
                category TEXT,
                source TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # File tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                action TEXT,
                project TEXT,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def _connect(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def store_command(self, command: str, result: str, success: bool, category: str = "general", project: str = None):
        """Permanently store command"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO commands (command, result, success, category, project)
            VALUES (?, ?, ?, ?, ?)
        ''', (command, result[:2000], 1 if success else 0, category, project))
        conn.commit()
        conn.close()

    def store_conversation(self, user_msg: str, nova_response: str):
        """Archive conversation"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (user_message, nova_response)
            VALUES (?, ?)
        ''', (user_msg, nova_response[:2000]))
        conn.commit()
        conn.close()

    def register_project(self, name: str, path: str, description: str = ""):
        """Register a project"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO projects (name, path, description, last_accessed)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (name, path, description))
        conn.commit()
        conn.close()

    def log_project_change(self, project_name: str, change_type: str, file_path: str = None, description: str = ""):
        """Log change to a project"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO project_changes (project_name, change_type, file_path, description)
            VALUES (?, ?, ?, ?)
        ''', (project_name, change_type, file_path, description))
        # Update project last accessed
        cursor.execute('''
            UPDATE projects SET last_accessed = CURRENT_TIMESTAMP WHERE name = ?
        ''', (project_name,))
        conn.commit()
        conn.close()

    def store_daily_summary(self, date: str, total_commands: int, total_messages: int, projects: List[str], summary: str):
        """Store daily summary"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO daily_summaries (date, total_commands, total_messages, projects_worked, summary)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, total_commands, total_messages, json.dumps(projects), summary))
        conn.commit()
        conn.close()

    def store_file_action(self, file_path: str, action: str, project: str = None, details: str = ""):
        """Track file action"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO file_history (file_path, action, project, details)
            VALUES (?, ?, ?, ?)
        ''', (file_path, action, project, details))
        conn.commit()
        conn.close()

    def add_insight(self, insight: str, category: str = "general", source: str = ""):
        """Store permanent insight"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO insights (insight, category, source)
            VALUES (?, ?, ?)
        ''', (insight, category, source))
        conn.commit()
        conn.close()

    def get_project_history(self, project_name: str, limit: int = 50) -> List[Dict]:
        """Get project change history"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT change_type, file_path, description, timestamp
            FROM project_changes
            WHERE project_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (project_name, limit))
        rows = cursor.fetchall()
        conn.close()

        return [{"type": r[0], "file": r[1], "description": r[2], "timestamp": r[3]} for r in rows]

    def get_all_projects(self) -> List[Dict]:
        """Get all registered projects"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT name, path, description, last_accessed FROM projects ORDER BY last_accessed DESC')
        rows = cursor.fetchall()
        conn.close()

        return [{"name": r[0], "path": r[1], "description": r[2], "last_accessed": r[3]} for r in rows]

    def get_command_stats(self, days: int = 7) -> Dict:
        """Get command statistics"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*), SUM(success), category
            FROM commands
            WHERE timestamp >= datetime('now', ?)
            GROUP BY category
        ''', (f'-{days} days',))
        rows = cursor.fetchall()
        conn.close()

        stats = {}
        for row in rows:
            stats[row[2] or "general"] = {"total": row[0], "success": row[1]}
        return stats

    def search_history(self, query: str, limit: int = 20) -> List[Dict]:
        """Search command history"""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT command, result, success, timestamp
            FROM commands
            WHERE command LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', limit))
        rows = cursor.fetchall()
        conn.close()

        return [{"command": r[0], "result": r[1], "success": r[2], "timestamp": r[3]} for r in rows]


class ProjectTracker:
    """
    Project-specific tracking and logging
    Creates md/json files per project
    """

    def __init__(self):
        self.projects_dir = PROJECTS_DIR

    def _get_project_dir(self, project_name: str) -> str:
        """Get or create project tracking directory"""
        # Sanitize project name for directory
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in project_name)
        project_dir = os.path.join(self.projects_dir, safe_name)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(os.path.join(project_dir, "logs"), exist_ok=True)
        return project_dir

    def init_project(self, project_name: str, project_path: str, description: str = ""):
        """Initialize project tracking"""
        project_dir = self._get_project_dir(project_name)

        # Create project info file
        info_file = os.path.join(project_dir, "project_info.json")
        info = {
            "name": project_name,
            "path": project_path,
            "description": description,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2)

        # Create initial changelog
        changelog = os.path.join(project_dir, "CHANGELOG.md")
        if not os.path.exists(changelog):
            with open(changelog, 'w', encoding='utf-8') as f:
                f.write(f"# {project_name} - NOVA Changelog\n\n")
                f.write(f"Project tracking started: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                f.write("---\n\n")

    def log_change(self, project_name: str, change_type: str, description: str, files: List[str] = None):
        """Log a change to the project"""
        project_dir = self._get_project_dir(project_name)
        today = datetime.now().strftime("%Y-%m-%d")

        # Update changes.json
        changes_file = os.path.join(project_dir, "changes.json")
        changes = []
        if os.path.exists(changes_file):
            try:
                with open(changes_file, 'r', encoding='utf-8') as f:
                    changes = json.load(f)
            except:
                changes = []

        changes.append({
            "type": change_type,
            "description": description,
            "files": files or [],
            "timestamp": datetime.now().isoformat()
        })

        with open(changes_file, 'w', encoding='utf-8') as f:
            json.dump(changes, f, indent=2)

        # Update daily log
        daily_log = os.path.join(project_dir, "logs", f"{today}.md")
        with open(daily_log, 'a', encoding='utf-8') as f:
            time_str = datetime.now().strftime("%H:%M:%S")
            f.write(f"\n## {time_str} - {change_type}\n")
            f.write(f"{description}\n")
            if files:
                f.write("Files: " + ", ".join(files) + "\n")

        # Update changelog
        changelog = os.path.join(project_dir, "CHANGELOG.md")
        with open(changelog, 'a', encoding='utf-8') as f:
            f.write(f"\n### {datetime.now().strftime('%Y-%m-%d %H:%M')} - {change_type}\n")
            f.write(f"{description}\n")
            if files:
                for file in files:
                    f.write(f"- `{file}`\n")

    def get_project_summary(self, project_name: str) -> Dict:
        """Get project summary"""
        project_dir = self._get_project_dir(project_name)

        # Load project info
        info_file = os.path.join(project_dir, "project_info.json")
        info = {}
        if os.path.exists(info_file):
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)

        # Count changes
        changes_file = os.path.join(project_dir, "changes.json")
        change_count = 0
        if os.path.exists(changes_file):
            with open(changes_file, 'r', encoding='utf-8') as f:
                changes = json.load(f)
                change_count = len(changes)

        return {
            "name": project_name,
            "info": info,
            "total_changes": change_count,
            "tracking_dir": project_dir
        }

    def list_tracked_projects(self) -> List[str]:
        """List all tracked projects"""
        try:
            return [d for d in os.listdir(self.projects_dir)
                    if os.path.isdir(os.path.join(self.projects_dir, d))]
        except:
            return []


class DailyReviewer:
    """
    End of day review system
    Reviews all projects and creates daily summary
    """

    def __init__(self, rm: RegisterMemory, ram: RandomAccessMemory, rom: ReadOnlyMemory, tracker: ProjectTracker):
        self.rm = rm
        self.ram = ram
        self.rom = rom
        self.tracker = tracker

    def generate_daily_review(self) -> str:
        """Generate end of day review"""
        today = datetime.now().strftime("%Y-%m-%d")

        # Get RAM summary
        daily_stats = self.ram.get_daily_summary()

        # Get projects worked
        projects = daily_stats.get("projects_worked", [])

        # Build review
        review = f"""# NOVA Daily Review - {today}

## Summary
- **Total Commands:** {daily_stats['total_commands']}
- **Total Messages:** {daily_stats['total_messages']}
- **Sessions:** {daily_stats['sessions']}
- **Files Modified:** {daily_stats['files_modified']}
- **Errors:** {daily_stats['errors']}

## Projects Worked On
"""

        for project in projects:
            summary = self.tracker.get_project_summary(project)
            review += f"\n### {project}\n"
            review += f"- Changes today: {summary.get('total_changes', 0)}\n"

        if not projects:
            review += "\nNo projects worked on today.\n"

        # Recent commands summary
        review += "\n## Recent Activity\n"
        recent = self.ram.get_recent_activity(10)
        for cmd in recent:
            status = "OK" if cmd.get("success") else "FAIL"
            review += f"- [{status}] {cmd.get('command', 'N/A')[:50]}\n"

        # Store review
        review_file = os.path.join(DAILY_LOGS_DIR, f"{today}_review.md")
        with open(review_file, 'w', encoding='utf-8') as f:
            f.write(review)

        # Store summary in ROM
        self.rom.store_daily_summary(
            today,
            daily_stats['total_commands'],
            daily_stats['total_messages'],
            projects,
            review
        )

        return review

    def review_project(self, project_name: str) -> str:
        """Review specific project (read-only)"""
        summary = self.tracker.get_project_summary(project_name)
        history = self.rom.get_project_history(project_name, 20)

        review = f"""# Project Review: {project_name}

## Info
- Path: {summary['info'].get('path', 'N/A')}
- Created: {summary['info'].get('created', 'N/A')}
- Total Changes Tracked: {summary['total_changes']}

## Recent Changes
"""

        for change in history[:10]:
            review += f"\n### {change['timestamp']}\n"
            review += f"- Type: {change['type']}\n"
            review += f"- Description: {change['description']}\n"
            if change['file']:
                review += f"- File: {change['file']}\n"

        return review


class NovaMemorySystem:
    """
    Main memory system interface
    Integrates all 3 tiers
    """

    def __init__(self):
        self.rm = RegisterMemory()
        self.ram = RandomAccessMemory()
        self.rom = ReadOnlyMemory()
        self.tracker = ProjectTracker()
        self.reviewer = DailyReviewer(self.rm, self.ram, self.rom, self.tracker)

        # Increment session count
        self.ram.increment_session()
        logger.info("NOVA Memory System initialized")

    def process_message(self, user_msg: str, nova_response: str):
        """Process a conversation exchange"""
        # RM - current context
        self.rm.add_message("user", user_msg)
        self.rm.add_message("nova", nova_response)

        # RAM - session memory
        self.ram.log_conversation(user_msg, nova_response)

        # ROM - permanent archive (every 5th message to save space)
        if self.ram.data["statistics"]["total_messages"] % 5 == 0:
            self.rom.store_conversation(user_msg, nova_response)

    def log_command(self, command: str, result: str, success: bool, category: str = "general", project: str = None):
        """Log command across all memory tiers"""
        # RM
        self.rm.add_command(command, result)

        # RAM
        self.ram.log_command(command, result, success, category)

        # ROM
        self.rom.store_command(command, result, success, category, project)

        # Project tracking
        if project:
            self.tracker.log_change(project, "command", f"Executed: {command}", [])
            self.rom.log_project_change(project, "command", None, command)

    def log_file_change(self, file_path: str, action: str, project: str = None, details: str = ""):
        """Log file modification"""
        # RAM
        self.ram.log_file_change(file_path, action, project)

        # ROM
        self.rom.store_file_action(file_path, action, project, details)

        # Project tracking
        if project:
            self.tracker.log_change(project, f"file_{action}", details or f"{action}: {file_path}", [file_path])
            self.rom.log_project_change(project, f"file_{action}", file_path, details)

    def register_project(self, name: str, path: str, description: str = ""):
        """Register and track a project"""
        self.tracker.init_project(name, path, description)
        self.rom.register_project(name, path, description)
        self.ram.log_project_work(name, "registered", description)

    def set_active_project(self, project: str):
        """Set currently active project"""
        self.rm.set_active_project(project)
        self.ram.log_project_work(project, "activated")

    def get_context(self) -> Dict:
        """Get full context from all tiers"""
        return {
            "rm": {
                "summary": self.rm.get_context_summary(),
                "recent_commands": self.rm.context.get("recent_commands", []),
                "active_project": self.rm.context.get("active_project"),
                "current_task": self.rm.context.get("current_task")
            },
            "ram": self.ram.get_daily_summary(),
            "projects": self.tracker.list_tracked_projects()
        }

    def daily_review(self) -> str:
        """Generate daily review"""
        return self.reviewer.generate_daily_review()

    def project_review(self, project_name: str) -> str:
        """Review specific project"""
        return self.reviewer.review_project(project_name)

    def search(self, query: str) -> List[Dict]:
        """Search memory"""
        return self.rom.search_history(query)

    def get_stats(self, days: int = 7) -> Dict:
        """Get overall statistics"""
        return self.rom.get_command_stats(days)
