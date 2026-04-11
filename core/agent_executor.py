"""
NOVA - Autonomous Agent Executor
Chains Claude Code + Git + GitHub CLI to execute complex multi-step tasks.
Handles: project creation, full coding, testing, GitHub push, PR creation.
"""

import os
import re
import json
import asyncio
import logging
import subprocess
from datetime import datetime
from typing import Dict, Optional, Callable, List
from collections import deque

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AgentStep:
    """A single step in an autonomous execution plan"""

    def __init__(self, name: str, description: str, action: str, params: dict = None):
        self.name = name
        self.description = description
        self.action = action
        self.params = params or {}
        self.status = "pending"  # pending, running, completed, failed, skipped
        self.result = None
        self.error = None

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "action": self.action,
            "status": self.status,
            "result": str(self.result)[:300] if self.result else None,
            "error": self.error
        }


class AgentExecutor:
    """
    Autonomous agent that can execute multi-step tasks:
    - Create full projects from a description
    - Write code using Claude Code
    - Create GitHub repos
    - Commit and push code
    - Create PRs
    - Run tests
    - Chain any combination of the above
    """

    def __init__(self):
        from actions.code_handler import CodeHandler
        from actions.file_ops import FileOperations as FileOps
        from actions.system_control import SystemControl

        self.code = CodeHandler
        self.file_ops = FileOps
        self.system = SystemControl
        self.current_plan = []
        self.is_running = False
        self._task_queue = deque()
        self._active_tasks = {}

    async def build_project(self, description: str, progress_cb: Callable = None) -> dict:
        """
        Full autonomous project creation:
        1. Parse project requirements from description
        2. Create project directory
        3. Use Claude Code to generate the entire project
        4. Initialize git
        5. Create GitHub repo
        6. Commit and push
        7. Return results

        Args:
            description: Natural language project description
            progress_cb: Async callback for progress updates
        """
        self.is_running = True
        results = {"steps": [], "success": False}

        try:
            # Step 1: Parse project info from description
            await self._notify(progress_cb, "Analyzing project requirements...")
            project_info = self._parse_project_info(description)
            project_name = project_info["name"]
            project_path = project_info["path"]
            results["project_name"] = project_name
            results["project_path"] = project_path

            # Step 2: Create project directory
            await self._notify(progress_cb, f"Creating project directory: `{project_path}`")
            if not os.path.exists(project_path):
                os.makedirs(project_path, exist_ok=True)
            results["steps"].append({"step": "create_directory", "status": "done"})

            # Step 3: Use Claude Code to generate the project
            await self._notify(progress_cb, "Writing code with Claude Code... (this may take a few minutes)")

            claude_prompt = self._build_claude_prompt(description, project_info)
            claude_result = self.code.run_claude_code(claude_prompt, working_dir=project_path, timeout=600)

            results["steps"].append({
                "step": "claude_code",
                "status": "done" if claude_result["success"] else "failed",
                "output": claude_result.get("output", claude_result.get("error", ""))[:1000]
            })

            if not claude_result["success"]:
                results["error"] = f"Claude Code failed: {claude_result.get('error', 'Unknown error')}"
                await self._notify(progress_cb, f"Claude Code encountered an issue: {claude_result.get('error', '')[:200]}")
                # Continue anyway - partial code may still be useful

            # Step 4: Initialize git
            await self._notify(progress_cb, "Initializing git repository...")
            git_init = self._run_cmd("git init", cwd=project_path)
            results["steps"].append({"step": "git_init", "status": "done" if git_init["success"] else "failed"})

            # Create .gitignore if not exists
            gitignore_path = os.path.join(project_path, ".gitignore")
            if not os.path.exists(gitignore_path):
                self._create_gitignore(project_path, project_info.get("language", ""))

            # Step 5: Stage and commit
            await self._notify(progress_cb, "Committing code...")
            self._run_cmd("git add -A", cwd=project_path)
            commit_msg = f"Initial commit: {project_name} - {description[:100]}"
            commit_result = self._run_cmd(f'git commit -m "{commit_msg}"', cwd=project_path)
            results["steps"].append({"step": "git_commit", "status": "done" if commit_result["success"] else "failed"})

            # Step 6: Create GitHub repo
            await self._notify(progress_cb, f"Creating GitHub repository: **{project_name}**...")
            gh_result = self.code.github_create_repo(
                name=project_name,
                description=description[:200],
                private=project_info.get("private", False),
                path=project_path
            )
            results["steps"].append({
                "step": "github_create",
                "status": "done" if gh_result["success"] else "failed",
                "output": gh_result.get("output", gh_result.get("error", ""))[:500]
            })

            if gh_result["success"]:
                results["repo_url"] = gh_result.get("repo_url", f"https://github.com/{self._get_gh_user()}/{project_name}")
                await self._notify(progress_cb, f"Repo created: {results['repo_url']}")
            else:
                # Repo might already exist, try to add remote and push
                await self._notify(progress_cb, "Repo creation failed, trying to push to existing repo...")
                self._run_cmd(f"git remote add origin https://github.com/{self._get_gh_user()}/{project_name}.git", cwd=project_path)
                push_result = self._run_cmd("git push -u origin main", cwd=project_path)
                if not push_result["success"]:
                    # Try master branch
                    self._run_cmd("git branch -M main", cwd=project_path)
                    push_result = self._run_cmd("git push -u origin main", cwd=project_path)
                results["steps"].append({"step": "manual_push", "status": "done" if push_result["success"] else "failed"})

            # Step 7: List created files
            try:
                files = []
                for root, dirs, filenames in os.walk(project_path):
                    # Skip hidden dirs and node_modules
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules' and d != '__pycache__']
                    for f in filenames:
                        rel = os.path.relpath(os.path.join(root, f), project_path)
                        files.append(rel)
                results["files_created"] = files[:50]  # Limit to 50 files
                results["file_count"] = len(files)
            except Exception:
                pass

            results["success"] = True
            await self._notify(progress_cb, "Project build complete!")

        except Exception as e:
            results["error"] = str(e)
            results["success"] = False
            await self._notify(progress_cb, f"Error: {str(e)[:200]}")
            logger.error(f"Agent executor error: {e}", exc_info=True)
        finally:
            self.is_running = False

        return results

    async def auto_push(self, repo_path: str, message: str = None, progress_cb: Callable = None) -> dict:
        """Auto stage, commit, and push all changes"""
        try:
            await self._notify(progress_cb, "Checking for changes...")

            # Check status
            status = self._run_cmd("git status --porcelain", cwd=repo_path)
            if not status.get("output", "").strip():
                return {"success": True, "output": "Nothing to commit, working tree clean."}

            changes = status["output"].strip().split("\n")
            await self._notify(progress_cb, f"Found {len(changes)} changed files. Committing...")

            # Generate smart commit message if not provided
            if not message:
                diff_result = self._run_cmd("git diff --stat", cwd=repo_path)
                message = self._generate_commit_message(diff_result.get("output", ""), changes)

            # Stage, commit, push
            result = self.code.auto_commit_push(repo_path, message)

            if result["success"]:
                await self._notify(progress_cb, f"Pushed successfully!\nCommit: {message}")
            else:
                await self._notify(progress_cb, f"Push failed: {result.get('error', result.get('output', ''))}")

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_repo(self, name: str, description: str = "", path: str = None,
                          private: bool = False, progress_cb: Callable = None) -> dict:
        """Create a new GitHub repo and optionally link to local directory"""
        try:
            await self._notify(progress_cb, f"Creating GitHub repo: **{name}**...")

            # If path exists and has git, use --source
            if path and os.path.exists(path):
                # Init git if needed
                if not os.path.exists(os.path.join(path, ".git")):
                    self._run_cmd("git init", cwd=path)
                    self._run_cmd("git add -A", cwd=path)
                    self._run_cmd(f'git commit -m "Initial commit"', cwd=path)

            result = self.code.github_create_repo(name, description, private, path)

            if result["success"]:
                await self._notify(progress_cb, f"Repo created: {result.get('repo_url', '')}")
            else:
                await self._notify(progress_cb, f"Failed: {result.get('error', result.get('output', ''))}")

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_task(self, task_description: str, working_dir: str = None, progress_cb: Callable = None) -> dict:
        """
        Execute any arbitrary task autonomously using Claude Code.
        This is the general-purpose 'do anything' method.
        """
        try:
            cwd = working_dir or os.getcwd()
            await self._notify(progress_cb, f"Working on: {task_description[:100]}...")

            # Run Claude Code with the task
            result = self.code.run_claude_code(task_description, working_dir=cwd, timeout=600)

            if result["success"]:
                await self._notify(progress_cb, "Task completed!")
            else:
                await self._notify(progress_cb, f"Task had issues: {result.get('error', '')[:200]}")

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === INTERNAL HELPERS ===

    def _parse_project_info(self, description: str) -> dict:
        """Extract project name, language, type from description"""
        desc_lower = description.lower()

        # Try to extract a project name
        name = None
        # Check for quoted names
        quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', description)
        if quoted:
            name = quoted[0][0] or quoted[0][1]

        # Check for "called X" or "named X" patterns
        if not name:
            match = re.search(r'(?:called|named|name(?:d)?)\s+(\S+)', desc_lower)
            if match:
                name = match.group(1).strip('.,!?')

        # Generate from description
        if not name:
            words = [w for w in desc_lower.split() if w not in
                     ("create", "build", "make", "a", "an", "the", "new", "project", "app",
                      "for", "with", "and", "that", "which", "using", "in")]
            name = "-".join(words[:3]) if words else "nova-project"

        # Clean name
        name = re.sub(r'[^a-zA-Z0-9_-]', '-', name).strip('-')
        if not name:
            name = f"project-{datetime.now().strftime('%Y%m%d-%H%M')}"

        # Detect language
        language = "python"  # default
        lang_map = {
            "flutter": "dart", "dart": "dart",
            "react": "javascript", "next": "javascript", "node": "javascript", "express": "javascript",
            "javascript": "javascript", "js": "javascript", "typescript": "typescript", "ts": "typescript",
            "python": "python", "django": "python", "flask": "python", "fastapi": "python",
            "rust": "rust", "go": "go", "golang": "go",
            "java": "java", "spring": "java", "kotlin": "kotlin",
            "c#": "csharp", "csharp": "csharp", ".net": "csharp",
        }
        for keyword, lang in lang_map.items():
            if keyword in desc_lower:
                language = lang
                break

        # Detect project type
        project_type = "general"
        type_map = {
            "api": "api", "rest": "api", "backend": "api",
            "web": "web", "website": "web", "frontend": "web",
            "app": "app", "mobile": "app", "android": "app", "ios": "app",
            "cli": "cli", "tool": "cli", "script": "script",
            "bot": "bot", "telegram": "bot", "discord": "bot",
            "game": "game", "library": "library", "package": "library",
        }
        for keyword, ptype in type_map.items():
            if keyword in desc_lower:
                project_type = ptype
                break

        # Detect if private
        private = "private" in desc_lower

        project_path = os.path.join("C:\\code", name)

        return {
            "name": name,
            "path": project_path,
            "language": language,
            "type": project_type,
            "private": private,
            "description": description
        }

    def _build_claude_prompt(self, description: str, project_info: dict) -> str:
        """Build a specific, actionable prompt for Claude Code to generate the project"""
        return f"""You are in an empty project directory. Create a COMPLETE, WORKING project.

PROJECT DESCRIPTION: {description}
LANGUAGE: {project_info['language']}
TYPE: {project_info['type']}

DO THIS NOW:
1. Create ALL source code files with COMPLETE working code (not stubs, not placeholders, not TODOs)
2. Create a README.md with project description and how to run it
3. Create any config files needed (package.json, requirements.txt, pubspec.yaml, etc.)
4. Create a .gitignore file

RULES:
- Every file must have COMPLETE, RUNNABLE code
- Do NOT write placeholder comments like "// TODO" or "// implement this"
- Do NOT skip any function body - write the full implementation
- Include ALL imports and dependencies
- The project must work immediately after creation
- If it has a UI, make it look clean and modern
- Write at least 3-5 source files for any non-trivial project

START CREATING FILES NOW. Use the Write tool to create each file."""

    def _create_gitignore(self, project_path: str, language: str):
        """Create a .gitignore file based on language"""
        ignores = {
            "python": "*.pyc\n__pycache__/\n*.pyo\nvenv/\n.env\n*.egg-info/\ndist/\nbuild/\n.pytest_cache/\n",
            "javascript": "node_modules/\n.env\ndist/\nbuild/\n.DS_Store\n*.log\ncoverage/\n",
            "typescript": "node_modules/\n.env\ndist/\nbuild/\n.DS_Store\n*.log\ncoverage/\n",
            "dart": ".dart_tool/\n.packages\nbuild/\n.flutter-plugins\n.flutter-plugins-dependencies\n*.iml\n",
            "rust": "target/\nCargo.lock\n",
            "go": "bin/\n*.exe\n*.test\n",
            "java": "*.class\ntarget/\n.gradle/\nbuild/\n",
            "csharp": "bin/\nobj/\n*.user\n.vs/\n",
        }
        content = ignores.get(language, "") + "\n# Common\n.env\n.DS_Store\n*.log\n.idea/\n.vscode/\n"

        try:
            with open(os.path.join(project_path, ".gitignore"), "w") as f:
                f.write(content)
        except Exception:
            pass

    def _generate_commit_message(self, diff_stat: str, changes: list) -> str:
        """Generate a simple commit message from changes"""
        if not changes:
            return "NOVA auto-commit"

        added = sum(1 for c in changes if c.startswith("A") or c.startswith("?"))
        modified = sum(1 for c in changes if c.startswith("M"))
        deleted = sum(1 for c in changes if c.startswith("D"))

        parts = []
        if added:
            parts.append(f"add {added} files")
        if modified:
            parts.append(f"update {modified} files")
        if deleted:
            parts.append(f"remove {deleted} files")

        return f"NOVA: {', '.join(parts)}" if parts else f"NOVA auto-commit {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    def _get_gh_user(self) -> str:
        """Get GitHub username"""
        try:
            r = self._run_cmd("gh api user --jq .login")
            if r["success"] and r["output"].strip():
                return r["output"].strip()
        except Exception:
            pass
        return "user"

    def _run_cmd(self, command: str, cwd: str = None) -> dict:
        """Run a shell command"""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                cwd=cwd or os.getcwd(), timeout=60
            )
            return {
                "success": result.returncode == 0,
                "output": (result.stdout or result.stderr or "").strip()
            }
        except Exception as e:
            return {"success": False, "output": "", "error": str(e)}

    async def _notify(self, callback: Callable, message: str):
        """Send progress notification"""
        if callback:
            try:
                await callback(message)
            except Exception:
                pass
        logger.info(f"Agent: {message}")

    # === BACKGROUND TASK QUEUE ===

    def queue_task(self, task_name: str, coro_func, *args, **kwargs):
        """Queue a task for background execution"""
        self._task_queue.append({
            "name": task_name,
            "func": coro_func,
            "args": args,
            "kwargs": kwargs,
            "status": "queued",
            "queued_at": datetime.now().isoformat()
        })

    async def run_background_task(self, task_name: str, coro, alert_cb: Callable = None):
        """Run a task in the background without blocking"""
        self._active_tasks[task_name] = {"status": "running", "started": datetime.now().isoformat()}

        try:
            result = await coro
            self._active_tasks[task_name]["status"] = "completed"
            self._active_tasks[task_name]["result"] = str(result)[:500]

            if alert_cb:
                success = result.get("success", False) if isinstance(result, dict) else bool(result)
                status = "completed" if success else "failed"
                await self._notify(alert_cb, f"Background task **{task_name}** {status}.")

            return result
        except Exception as e:
            self._active_tasks[task_name]["status"] = "failed"
            self._active_tasks[task_name]["error"] = str(e)
            if alert_cb:
                await self._notify(alert_cb, f"Background task **{task_name}** failed: {str(e)[:200]}")
            return {"success": False, "error": str(e)}

    def get_active_tasks(self) -> dict:
        """Get status of all active/recent tasks"""
        return {
            "running": self.is_running,
            "queue_size": len(self._task_queue),
            "active_tasks": self._active_tasks
        }
