"""
NOVA - Goal Planner
Autonomous task decomposition, multi-step execution,
planning and re-planning capabilities
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class Task:
    """A single task in a plan"""

    def __init__(self, task_id: int, description: str, action: str,
                 params: Dict = None, depends_on: List[int] = None):
        self.id = task_id
        self.description = description
        self.action = action
        self.params = params or {}
        self.depends_on = depends_on or []
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.retries = 0
        self.max_retries = 2

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "action": self.action,
            "params": self.params,
            "status": self.status.value,
            "result": str(self.result)[:200] if self.result else None,
            "error": self.error,
        }


class Plan:
    """A multi-step execution plan"""

    def __init__(self, goal: str, plan_id: str = None):
        self.id = plan_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.goal = goal
        self.tasks: List[Task] = []
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        self.current_task_index = 0

    def add_task(self, description: str, action: str, params: Dict = None,
                 depends_on: List[int] = None) -> Task:
        """Add a task to the plan"""
        task = Task(
            task_id=len(self.tasks),
            description=description,
            action=action,
            params=params,
            depends_on=depends_on
        )
        self.tasks.append(task)
        return task

    def get_next_task(self) -> Optional[Task]:
        """Get next executable task"""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                # Check dependencies
                deps_met = all(
                    self.tasks[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.depends_on
                    if dep_id < len(self.tasks)
                )
                if deps_met:
                    return task
        return None

    def get_progress(self) -> Dict:
        """Get plan progress"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        running = sum(1 for t in self.tasks if t.status == TaskStatus.RUNNING)

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": total - completed - failed - running,
            "progress_percent": int((completed / total) * 100) if total > 0 else 0,
            "status": self.status.value,
        }

    def is_complete(self) -> bool:
        """Check if plan is fully executed"""
        return all(t.status in (TaskStatus.COMPLETED, TaskStatus.SKIPPED, TaskStatus.FAILED)
                   for t in self.tasks)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "goal": self.goal,
            "status": self.status.value,
            "tasks": [t.to_dict() for t in self.tasks],
            "progress": self.get_progress(),
            "created_at": self.created_at,
        }

    def format_status(self) -> str:
        """Format plan status for display"""
        progress = self.get_progress()
        status_icons = {
            TaskStatus.PENDING: "[ ]",
            TaskStatus.RUNNING: "[>]",
            TaskStatus.COMPLETED: "[+]",
            TaskStatus.FAILED: "[X]",
            TaskStatus.SKIPPED: "[-]",
            TaskStatus.BLOCKED: "[!]",
        }

        text = f"**Plan: {self.goal}**\n"
        text += f"Progress: {progress['progress_percent']}% ({progress['completed']}/{progress['total']})\n\n"

        for task in self.tasks:
            icon = status_icons.get(task.status, "[ ]")
            text += f"{icon} {task.description}"
            if task.error:
                text += f" (Error: {task.error[:50]})"
            text += "\n"

        return text


class GoalPlanner:
    """
    NOVA's autonomous goal planner
    Breaks down goals into executable steps
    """

    # Templates for common goal patterns
    GOAL_TEMPLATES = {
        "project_setup": {
            "patterns": ["setup project", "create project", "init project", "new project",
                         "initialize", "scaffold"],
            "tasks": [
                ("Create project directory", "create_directory", {}),
                ("Initialize git repository", "git_init", {}),
                ("Create basic file structure", "create_files", {}),
                ("Install dependencies", "run_command", {"cmd": "npm install"}),
            ]
        },
        "git_workflow": {
            "patterns": ["commit and push", "save changes", "push to git",
                         "update repo", "deploy changes"],
            "tasks": [
                ("Check git status", "git_op", {"op": "status"}),
                ("Stage all changes", "git_op", {"op": "add", "args": "."}),
                ("Create commit", "git_op", {"op": "commit"}),
                ("Push to remote", "git_op", {"op": "push"}),
            ]
        },
        "system_cleanup": {
            "patterns": ["clean system", "free space", "cleanup", "clear cache",
                         "free up disk", "system maintenance"],
            "tasks": [
                ("Clear temporary files", "clean_temp", {}),
                ("Empty recycle bin", "empty_bin", {}),
                ("Check disk usage", "disk_info", {}),
                ("List large processes", "check_processes", {}),
            ]
        },
        "code_review": {
            "patterns": ["review code", "check code", "code quality",
                         "analyze code", "inspect project"],
            "tasks": [
                ("Check git status", "git_op", {"op": "status"}),
                ("Show recent changes", "git_op", {"op": "diff"}),
                ("List modified files", "git_op", {"op": "log"}),
                ("Run tests if available", "run_tests", {}),
            ]
        },
        "backup_project": {
            "patterns": ["backup", "save backup", "archive project", "backup project"],
            "tasks": [
                ("Check project status", "git_op", {"op": "status"}),
                ("Commit any uncommitted changes", "git_op", {"op": "commit"}),
                ("Create backup archive", "create_backup", {}),
                ("Verify backup", "verify_backup", {}),
            ]
        },
        "morning_routine": {
            "patterns": ["morning routine", "start of day", "daily check", "morning check"],
            "tasks": [
                ("Check system status", "system_info", {}),
                ("Check disk space", "disk_info", {}),
                ("List running processes", "check_processes", {}),
                ("Check battery status", "battery_info", {}),
                ("Show today's schedule", "show_schedule", {}),
            ]
        },
    }

    def __init__(self):
        self.active_plans: Dict[str, Plan] = {}
        self.completed_plans: List[Dict] = []
        self.action_handlers: Dict[str, Callable] = {}
        self._load_history()
        logger.info("Goal Planner initialized")

    def _history_file(self):
        return os.path.join(BASE_DIR, "intelligence", "data", "plan_history.json")

    def _load_history(self):
        """Load plan history"""
        try:
            path = self._history_file()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.completed_plans = json.load(f)
        except Exception:
            pass

    def _save_history(self):
        """Save plan history"""
        try:
            os.makedirs(os.path.dirname(self._history_file()), exist_ok=True)
            with open(self._history_file(), 'w', encoding='utf-8') as f:
                json.dump(self.completed_plans[-50:], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save plan history: {e}")

    def register_handler(self, action: str, handler: Callable):
        """Register an action handler"""
        self.action_handlers[action] = handler

    def create_plan(self, goal: str, custom_tasks: List[Dict] = None) -> Plan:
        """
        Create an execution plan for a goal
        Either from templates or custom tasks
        """
        plan = Plan(goal)

        if custom_tasks:
            for task_data in custom_tasks:
                plan.add_task(
                    description=task_data["description"],
                    action=task_data["action"],
                    params=task_data.get("params", {}),
                    depends_on=task_data.get("depends_on", [])
                )
        else:
            # Try to match a template
            template = self._match_template(goal)
            if template:
                for desc, action, params in template["tasks"]:
                    plan.add_task(desc, action, params)
            else:
                # Create a single-step plan
                plan.add_task(
                    description=goal,
                    action="execute_goal",
                    params={"goal": goal}
                )

        self.active_plans[plan.id] = plan
        return plan

    def _match_template(self, goal: str) -> Optional[Dict]:
        """Match a goal to a template"""
        goal_lower = goal.lower()
        best_match = None
        best_score = 0

        for name, template in self.GOAL_TEMPLATES.items():
            for pattern in template["patterns"]:
                if pattern in goal_lower:
                    score = len(pattern)
                    if score > best_score:
                        best_score = score
                        best_match = template

        return best_match

    async def execute_plan(self, plan: Plan, progress_callback: Callable = None) -> Dict:
        """
        Execute a plan step by step
        Calls progress_callback after each step with status update
        """
        plan.status = TaskStatus.RUNNING

        while not plan.is_complete():
            task = plan.get_next_task()
            if not task:
                # Check for blocked tasks
                blocked = [t for t in plan.tasks if t.status == TaskStatus.PENDING]
                for t in blocked:
                    t.status = TaskStatus.BLOCKED
                    t.error = "Dependencies not met"
                break

            # Execute task
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now().isoformat()

            if progress_callback:
                await progress_callback(plan, task, "started")

            try:
                result = await self._execute_task(task)
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now().isoformat()

                if progress_callback:
                    await progress_callback(plan, task, "completed")

            except Exception as e:
                task.error = str(e)
                task.retries += 1

                if task.retries <= task.max_retries:
                    task.status = TaskStatus.PENDING  # Retry
                    logger.warning(f"Task '{task.description}' failed, retrying ({task.retries}/{task.max_retries})")
                else:
                    task.status = TaskStatus.FAILED
                    if progress_callback:
                        await progress_callback(plan, task, "failed")

        # Finalize plan
        progress = plan.get_progress()
        if progress["failed"] == 0:
            plan.status = TaskStatus.COMPLETED
        else:
            plan.status = TaskStatus.FAILED

        plan.completed_at = datetime.now().isoformat()

        # Archive
        self.completed_plans.append(plan.to_dict())
        if plan.id in self.active_plans:
            del self.active_plans[plan.id]
        self._save_history()

        return plan.to_dict()

    async def _execute_task(self, task: Task) -> Any:
        """Execute a single task"""
        handler = self.action_handlers.get(task.action)
        if handler:
            if asyncio.iscoroutinefunction(handler):
                return await handler(**task.params)
            else:
                return handler(**task.params)
        else:
            raise ValueError(f"No handler registered for action: {task.action}")

    def get_active_plans(self) -> List[Dict]:
        """Get all active plans"""
        return [plan.to_dict() for plan in self.active_plans.values()]

    def get_plan_status(self, plan_id: str) -> Optional[str]:
        """Get formatted status of a plan"""
        plan = self.active_plans.get(plan_id)
        if plan:
            return plan.format_status()
        return None

    def cancel_plan(self, plan_id: str) -> bool:
        """Cancel an active plan"""
        if plan_id in self.active_plans:
            plan = self.active_plans[plan_id]
            for task in plan.tasks:
                if task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                    task.status = TaskStatus.SKIPPED
            plan.status = TaskStatus.FAILED
            del self.active_plans[plan_id]
            return True
        return False

    def decompose_goal(self, goal: str, entities: Dict = None) -> List[Dict]:
        """
        Intelligently decompose a complex goal into steps
        Returns list of task descriptions
        """
        goal_lower = goal.lower()
        steps = []

        # Pattern-based decomposition
        # "X and then Y" or "X, then Y"
        if " then " in goal_lower or " and then " in goal_lower:
            parts = goal_lower.replace(" and then ", " then ").split(" then ")
            for i, part in enumerate(parts):
                steps.append({
                    "description": part.strip().capitalize(),
                    "action": "execute_goal",
                    "params": {"goal": part.strip()},
                    "depends_on": [i - 1] if i > 0 else []
                })
            return steps

        # "First X, then Y, finally Z"
        sequential_markers = ["first", "then", "next", "after that", "finally", "lastly"]
        for marker in sequential_markers:
            if marker in goal_lower:
                # Simple split won't work well, use template matching instead
                break

        # Try template matching
        template = self._match_template(goal)
        if template:
            for i, (desc, action, params) in enumerate(template["tasks"]):
                steps.append({
                    "description": desc,
                    "action": action,
                    "params": params,
                    "depends_on": [i - 1] if i > 0 else []
                })
            return steps

        # Single step fallback
        steps.append({
            "description": goal,
            "action": "execute_goal",
            "params": {"goal": goal}
        })
        return steps

    def suggest_plan(self, intent: str, entities: Dict) -> Optional[List[str]]:
        """Suggest a plan based on intent and entities"""
        suggestions = {
            "git_operation": [
                "I can help with a full git workflow:",
                "1. Check current status",
                "2. Stage changes",
                "3. Commit with a message",
                "4. Push to remote",
                "Would you like me to execute this plan?"
            ],
            "file_operation": [
                "For file operations, I can:",
                "1. Search for the file",
                "2. Show its contents",
                "3. Make modifications",
                "4. Verify changes",
            ],
            "system_cleanup": [
                "System cleanup plan:",
                "1. Clear temp files",
                "2. Empty recycle bin",
                "3. Check disk space",
                "4. Review large files",
            ],
        }
        return suggestions.get(intent)
