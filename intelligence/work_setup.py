"""
NOVA - Work Setup System
When user says "I'm going to work on FlashLink", NOVA:
1. Opens VS Code with that project
2. Checks git status
3. Starts any needed servers
4. Gives a project briefing
5. Sets active project context

Also handles:
- Project-specific setup configs (what to open, what to run)
- Server management (start/stop/check)
- Morning briefing when NOVA comes online
"""

import os
import json
import logging
import subprocess
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "intelligence", "data")


class ProjectSetup:
    """Configuration for setting up a project workspace"""

    def __init__(self):
        self.config_file = os.path.join(DATA_DIR, "project_setups.json")
        self.configs = self._load()

    def _load(self) -> Dict:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save(self):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.configs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save project setups: {e}")

    def add_setup(self, project_name: str, config: Dict) -> str:
        """Add or update project setup config"""
        self.configs[project_name.lower()] = {
            "name": project_name,
            "path": config.get("path", ""),
            "editor": config.get("editor", "code"),
            "open_files": config.get("open_files", []),
            "servers": config.get("servers", []),
            "pre_commands": config.get("pre_commands", []),
            "post_commands": config.get("post_commands", []),
            "git_pull": config.get("git_pull", True),
            "check_status": config.get("check_status", True),
            "urls_to_open": config.get("urls_to_open", []),
            "notes": config.get("notes", ""),
            "updated": datetime.now().isoformat(),
        }
        self._save()
        return f"Setup for **{project_name}** configured."

    def get_setup(self, project_name: str) -> Optional[Dict]:
        """Get project setup config"""
        # Try exact match first
        config = self.configs.get(project_name.lower())
        if config:
            return config

        # Try fuzzy match
        for key, conf in self.configs.items():
            if project_name.lower() in key or key in project_name.lower():
                return conf

        return None

    def remove_setup(self, project_name: str) -> str:
        key = project_name.lower()
        if key in self.configs:
            del self.configs[key]
            self._save()
            return f"Setup for '{project_name}' removed."
        return f"No setup found for '{project_name}'."

    def list_setups(self) -> str:
        if not self.configs:
            return "No project setups configured. Use /setupproject to create one."
        text = "**Project Setups:**\n\n"
        for key, config in self.configs.items():
            text += f"**{config['name']}**\n"
            text += f"  Path: `{config.get('path', 'N/A')}`\n"
            text += f"  Servers: {len(config.get('servers', []))}\n"
            text += f"  Pre-commands: {len(config.get('pre_commands', []))}\n\n"
        return text


class WorkSetupEngine:
    """
    Full work setup engine - sets up workspace when user arrives
    """

    # Patterns that indicate user wants to start working
    WORK_TRIGGERS = [
        "work on", "working on", "going to work", "start working",
        "open project", "setup project", "let's work on", "i'll work on",
        "switch to", "continue with", "continue working", "back to",
        "let me work on", "prepare", "set up", "get ready for",
    ]

    def __init__(self):
        self.project_setup = ProjectSetup()
        self.active_servers = {}  # name -> process
        logger.info("Work Setup Engine initialized")

    def is_work_request(self, text: str) -> bool:
        """Check if user is requesting work setup"""
        text_lower = text.lower()
        return any(trigger in text_lower for trigger in self.WORK_TRIGGERS)

    def extract_project_name(self, text: str) -> Optional[str]:
        """Extract project name from work request"""
        text_lower = text.lower()
        for trigger in sorted(self.WORK_TRIGGERS, key=len, reverse=True):
            if trigger in text_lower:
                after = text_lower.split(trigger, 1)[1].strip()
                # Clean up common filler words
                clean_words = []
                skip = {"the", "my", "project", "app", "repo", "code", "on", "a", "an", "for", "to"}
                for word in after.split():
                    cleaned = word.strip(".,!?")
                    if cleaned not in skip or clean_words:
                        # Only skip filler at start, keep everything after first real word
                        if cleaned not in skip:
                            clean_words.append(cleaned)
                        elif clean_words:
                            clean_words.append(cleaned)
                if clean_words:
                    return " ".join(clean_words)
        return None

    async def setup_workspace(self, project_name: str, memory_system=None,
                               progress_callback: Callable = None) -> Dict:
        """
        Full workspace setup for a project
        Returns step-by-step results
        """
        result = {
            "project": project_name,
            "steps": [],
            "success": True,
            "briefing": "",
        }

        # 1. Find project config
        config = self.project_setup.get_setup(project_name)

        # 2. If no config, try to find project path from memory
        project_path = None
        if config:
            project_path = config.get("path")
        elif memory_system:
            projects = memory_system.rom.get_all_projects()
            for p in projects:
                if project_name.lower() in p["name"].lower():
                    project_path = p["path"]
                    break

        # 3. Try to find by scanning C:\code
        if not project_path:
            code_dir = "C:\\code"
            if os.path.exists(code_dir):
                for item in os.listdir(code_dir):
                    if project_name.lower() in item.lower():
                        candidate = os.path.join(code_dir, item)
                        if os.path.isdir(candidate):
                            project_path = candidate
                            break

        if not project_path or not os.path.exists(project_path):
            result["success"] = False
            result["steps"].append({
                "step": "Find project",
                "status": "FAIL",
                "detail": f"Could not find project '{project_name}'. Use /setupproject to configure it."
            })
            return result

        if progress_callback:
            await progress_callback(f"Found project at: `{project_path}`")

        # Step 1: Set active project in memory
        if memory_system:
            memory_system.set_active_project(project_name)
            result["steps"].append({"step": "Set active project", "status": "OK", "detail": project_name})

        # Step 2: Run pre-commands
        if config and config.get("pre_commands"):
            for cmd in config["pre_commands"]:
                if progress_callback:
                    await progress_callback(f"Running: `{cmd}`")
                try:
                    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                          cwd=project_path, timeout=30)
                    result["steps"].append({
                        "step": f"Pre-command: {cmd}",
                        "status": "OK" if proc.returncode == 0 else "WARN",
                        "detail": (proc.stdout or proc.stderr or "Done")[:100]
                    })
                except Exception as e:
                    result["steps"].append({"step": f"Pre-command: {cmd}", "status": "FAIL", "detail": str(e)})

        # Step 3: Git operations
        git_dir = os.path.join(project_path, ".git")
        if os.path.exists(git_dir):
            if progress_callback:
                await progress_callback("Checking git status...")

            # Git status
            try:
                proc = subprocess.run("git status --short", shell=True, capture_output=True,
                                       text=True, cwd=project_path, timeout=15)
                git_status = proc.stdout.strip()
                if git_status:
                    result["steps"].append({
                        "step": "Git status",
                        "status": "INFO",
                        "detail": f"{len(git_status.splitlines())} changed files"
                    })
                else:
                    result["steps"].append({"step": "Git status", "status": "OK", "detail": "Clean"})
            except Exception:
                pass

            # Git pull if configured
            if not config or config.get("git_pull", True):
                try:
                    proc = subprocess.run("git pull --no-rebase", shell=True, capture_output=True,
                                           text=True, cwd=project_path, timeout=30)
                    detail = proc.stdout.strip()[:100] or "Up to date"
                    result["steps"].append({"step": "Git pull", "status": "OK", "detail": detail})
                except Exception as e:
                    result["steps"].append({"step": "Git pull", "status": "WARN", "detail": str(e)[:50]})

            # Current branch
            try:
                proc = subprocess.run("git branch --show-current", shell=True, capture_output=True,
                                       text=True, cwd=project_path, timeout=5)
                branch = proc.stdout.strip()
                if branch:
                    result["steps"].append({"step": "Current branch", "status": "INFO", "detail": branch})
            except Exception:
                pass

            # Recent commits
            try:
                proc = subprocess.run("git log --oneline -3", shell=True, capture_output=True,
                                       text=True, cwd=project_path, timeout=5)
                if proc.stdout.strip():
                    result["steps"].append({
                        "step": "Recent commits",
                        "status": "INFO",
                        "detail": proc.stdout.strip()[:150]
                    })
            except Exception:
                pass

        # Step 4: Open in editor
        editor = config.get("editor", "code") if config else "code"
        if progress_callback:
            await progress_callback(f"Opening {editor}...")
        try:
            subprocess.Popen([editor, project_path], shell=True)
            result["steps"].append({"step": f"Open {editor}", "status": "OK", "detail": project_path})
        except Exception as e:
            result["steps"].append({"step": f"Open {editor}", "status": "FAIL", "detail": str(e)[:50]})

        # Step 5: Open specific files
        if config and config.get("open_files"):
            for fp in config["open_files"]:
                full = os.path.join(project_path, fp) if not os.path.isabs(fp) else fp
                if os.path.exists(full):
                    try:
                        subprocess.Popen([editor, full], shell=True)
                        result["steps"].append({"step": f"Open file: {fp}", "status": "OK"})
                    except Exception:
                        pass

        # Step 6: Start servers
        if config and config.get("servers"):
            for server in config["servers"]:
                server_name = server.get("name", "server")
                server_cmd = server.get("command", "")
                server_cwd = server.get("cwd", project_path)

                if not server_cmd:
                    continue

                if progress_callback:
                    await progress_callback(f"Starting server: {server_name}...")

                try:
                    proc = subprocess.Popen(
                        server_cmd, shell=True, cwd=server_cwd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                    self.active_servers[server_name] = proc
                    # Give it a moment to start
                    await asyncio.sleep(2)
                    if proc.poll() is None:
                        result["steps"].append({
                            "step": f"Server: {server_name}",
                            "status": "OK",
                            "detail": f"PID {proc.pid}"
                        })
                    else:
                        result["steps"].append({
                            "step": f"Server: {server_name}",
                            "status": "FAIL",
                            "detail": "Process exited immediately"
                        })
                except Exception as e:
                    result["steps"].append({
                        "step": f"Server: {server_name}",
                        "status": "FAIL",
                        "detail": str(e)[:50]
                    })

        # Step 7: Open URLs
        if config and config.get("urls_to_open"):
            import webbrowser
            for url in config["urls_to_open"]:
                try:
                    webbrowser.open(url)
                    result["steps"].append({"step": f"Open URL: {url}", "status": "OK"})
                except Exception:
                    pass

        # Step 8: Run post-commands
        if config and config.get("post_commands"):
            for cmd in config["post_commands"]:
                try:
                    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                          cwd=project_path, timeout=30)
                    result["steps"].append({
                        "step": f"Post-command: {cmd}",
                        "status": "OK" if proc.returncode == 0 else "WARN",
                        "detail": (proc.stdout or proc.stderr or "Done")[:100]
                    })
                except Exception:
                    pass

        # Generate briefing
        result["briefing"] = self._generate_briefing(project_name, project_path, result["steps"])

        return result

    def _generate_briefing(self, name: str, path: str, steps: List[Dict]) -> str:
        """Generate a work briefing"""
        briefing = f"**Workspace Ready: {name}**\n\n"

        ok_count = sum(1 for s in steps if s["status"] == "OK")
        fail_count = sum(1 for s in steps if s["status"] == "FAIL")

        briefing += f"Setup: {ok_count} OK"
        if fail_count:
            briefing += f", {fail_count} failed"
        briefing += "\n\n"

        for step in steps:
            icon = {"OK": "+", "FAIL": "X", "WARN": "!", "INFO": "i"}.get(step["status"], " ")
            briefing += f"[{icon}] {step['step']}"
            if step.get("detail"):
                briefing += f"\n    {step['detail']}"
            briefing += "\n"

        briefing += f"\n**Path:** `{path}`\n"
        briefing += f"Ready to work, Yash."
        return briefing

    def stop_servers(self, project_name: str = None) -> str:
        """Stop running servers"""
        stopped = []
        for name, proc in list(self.active_servers.items()):
            if project_name and project_name.lower() not in name.lower():
                continue
            try:
                proc.terminate()
                proc.wait(timeout=5)
                stopped.append(name)
                del self.active_servers[name]
            except Exception:
                try:
                    proc.kill()
                    stopped.append(name)
                    del self.active_servers[name]
                except Exception:
                    pass

        if stopped:
            return f"Stopped servers: {', '.join(stopped)}"
        return "No active servers to stop."

    def get_active_servers(self) -> str:
        """List active servers"""
        if not self.active_servers:
            return "No active servers."
        text = "**Active Servers:**\n"
        for name, proc in self.active_servers.items():
            running = proc.poll() is None
            text += f"  {name}: {'Running' if running else 'Stopped'} (PID: {proc.pid})\n"
        return text


class OnlineBroadcast:
    """Send 'NOVA is online' message when bot starts"""

    @staticmethod
    async def send_online_message(app, chat_ids: list):
        """Send online notification to all authorized users"""
        import psutil
        now = datetime.now()

        hour = now.hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # System info
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            battery_text = ""
            try:
                bat = psutil.sensors_battery()
                if bat:
                    plug = "Plugged in" if bat.power_plugged else "On battery"
                    battery_text = f"\nBattery: {bat.percent}% ({plug})"
            except Exception:
                pass

            system_text = (
                f"CPU: {cpu}% | RAM: {mem.percent}% | "
                f"Disk: {disk.percent}% ({disk.free // (1024**3)}GB free)"
                f"{battery_text}"
            )
        except Exception:
            system_text = "System info unavailable"

        message = (
            f"**{greeting}, Yash.**\n\n"
            f"NOVA is online and ready.\n"
            f"{now.strftime('%A, %B %d, %Y | %I:%M %p')}\n\n"
            f"**System:**\n{system_text}\n\n"
            f"Tell me what you're working on today, or use /help for commands."
        )

        for chat_id in chat_ids:
            try:
                await app.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
                logger.info(f"Online notification sent to {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send online notification: {e}")
