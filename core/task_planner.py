"""
NOVA - Smart Task Planner
Breaks big tasks into steps, shows live-updating progress on Telegram,
gets user approval before starting, and executes steps one by one.

Features:
- Asks Claude to break task into small steps
- Shows plan on Telegram with Accept/Reject/Changes buttons
- Live-updates a single message with checkmarks as steps complete
- No auto-timeout - user controls via /killtask
"""

import os
import json
import asyncio
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TaskPlan:
    """A plan with steps that can be tracked"""

    def __init__(self, task_id: str, description: str, steps: List[Dict]):
        self.task_id = task_id
        self.description = description
        self.steps = steps  # [{"name": "...", "command": "...", "status": "pending"}]
        self.status = "pending"  # pending, approved, running, completed, failed, rejected
        self.created_at = datetime.now().isoformat()
        self.message_id = None  # Telegram message ID for live updates
        self.chat_id = None

    def get_progress_text(self) -> str:
        """Format the plan as a live-updating progress message"""
        text = f"*Task:* {self.description[:100]}\n\n"

        for i, step in enumerate(self.steps, 1):
            status = step.get("status", "pending")
            if status == "completed":
                icon = "[ done ]"
            elif status == "running":
                icon = "[ ... ]"
            elif status == "failed":
                icon = "[ FAIL ]"
            elif status == "skipped":
                icon = "[ skip ]"
            else:
                icon = "[      ]"

            name = step.get("name", f"Step {i}")
            text += f"{icon}  {name}\n"

        # Add summary
        completed = sum(1 for s in self.steps if s["status"] == "completed")
        total = len(self.steps)

        if self.status == "running":
            text += f"\n_Progress: {completed}/{total} steps_"
        elif self.status == "completed":
            text += f"\n*All {total} steps completed!*"
        elif self.status == "failed":
            failed_step = next((s for s in self.steps if s["status"] == "failed"), None)
            if failed_step:
                text += f"\n_Failed at: {failed_step['name']}_"

        return text

    def mark_step(self, index: int, status: str, result: str = ""):
        """Mark a step's status"""
        if 0 <= index < len(self.steps):
            self.steps[index]["status"] = status
            if result:
                self.steps[index]["result"] = result[:500]


class TaskPlanner:
    """
    Plans and executes big tasks with live Telegram updates.
    """

    def __init__(self):
        self.active_plans = {}  # task_id -> TaskPlan
        self.pending_approval = {}  # task_id -> TaskPlan (waiting for user)

    def generate_plan(self, description: str) -> Optional[TaskPlan]:
        """Use Claude to break a task into steps"""
        prompt = f"""Break this task into small, concrete steps that can be executed one by one.

TASK: {description}

Reply in this EXACT JSON format (no other text):
{{
  "steps": [
    {{"name": "Step description (short)", "command": "what to do (detailed)"}},
    {{"name": "Step 2", "command": "what to do"}},
    ...
  ]
}}

Rules:
- Each step should be ONE clear action
- 3-8 steps total (not more)
- Steps should be in order of execution
- Each step's "command" should be specific enough for Claude Code to execute
- Include setup, implementation, testing, and deployment steps as needed
- Be practical, not vague"""

        try:
            result = subprocess.run(
                ["claude", "-p", "--system-prompt",
                 "You are a task planner. Break tasks into concrete executable steps. Reply ONLY with valid JSON."],
                input=prompt,
                capture_output=True, text=True,
                cwd=BASE_DIR, timeout=30,
                encoding="utf-8", errors="replace"
            )

            if result.returncode == 0 and result.stdout.strip():
                response = result.stdout.strip()
                # Extract JSON from response
                json_str = self._extract_json(response)
                if json_str:
                    data = json.loads(json_str)
                    steps = data.get("steps", [])
                    if steps:
                        # Add status to each step
                        for step in steps:
                            step["status"] = "pending"
                            step["result"] = ""

                        task_id = f"plan_{datetime.now().strftime('%H%M%S')}"
                        plan = TaskPlan(task_id, description, steps)
                        return plan
        except Exception as e:
            logger.error(f"Plan generation failed: {e}")

        return None

    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from Claude's response"""
        # Try direct parse first
        text = text.strip()
        if text.startswith("{"):
            return text

        # Look for JSON block
        import re
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return match.group(0)

        return None

    async def execute_plan(self, plan: TaskPlan, bot, chat_id: int,
                           working_dir: str = None) -> Dict:
        """Execute a plan step by step with live Telegram updates"""
        plan.status = "running"
        plan.chat_id = chat_id
        self.active_plans[plan.task_id] = plan
        cwd = working_dir or os.getcwd()

        # Send initial progress message
        progress_text = plan.get_progress_text()
        try:
            msg = await bot.send_message(
                chat_id=chat_id,
                text=progress_text,
                parse_mode="Markdown"
            )
            plan.message_id = msg.message_id
        except Exception:
            try:
                msg = await bot.send_message(chat_id=chat_id, text=progress_text)
                plan.message_id = msg.message_id
            except Exception as e:
                logger.error(f"Failed to send progress message: {e}")

        results = []

        for i, step in enumerate(plan.steps):
            # Check if plan was cancelled
            if plan.status == "rejected":
                for j in range(i, len(plan.steps)):
                    plan.mark_step(j, "skipped")
                await self._update_progress(plan, bot)
                break

            # Mark step as running
            plan.mark_step(i, "running")
            await self._update_progress(plan, bot)

            # Execute step using Claude Code
            try:
                step_prompt = f"""Execute this step for the task "{plan.description}":

Step {i+1}: {step['name']}
Details: {step['command']}

Working directory: {cwd}
Previous steps completed: {[s['name'] for s in plan.steps[:i] if s['status'] == 'completed']}

Execute this step now. Be specific and thorough."""

                step_result = subprocess.run(
                    ["claude", "-p", "--dangerously-skip-permissions", step_prompt],
                    input=step_prompt,
                    capture_output=True, text=True,
                    cwd=cwd, timeout=300,
                    encoding="utf-8", errors="replace"
                )

                if step_result.returncode == 0:
                    plan.mark_step(i, "completed", step_result.stdout[:500])
                    results.append({"step": step["name"], "success": True})
                else:
                    error = step_result.stderr[:300] or "Step failed"
                    plan.mark_step(i, "failed", error)
                    results.append({"step": step["name"], "success": False, "error": error})
                    # Don't stop on failure - mark remaining as skipped and break
                    for j in range(i + 1, len(plan.steps)):
                        plan.mark_step(j, "skipped")
                    plan.status = "failed"
                    await self._update_progress(plan, bot)
                    break

            except subprocess.TimeoutExpired:
                plan.mark_step(i, "failed", "Step timed out (5 min)")
                results.append({"step": step["name"], "success": False, "error": "Timeout"})
                for j in range(i + 1, len(plan.steps)):
                    plan.mark_step(j, "skipped")
                plan.status = "failed"
                await self._update_progress(plan, bot)
                break
            except Exception as e:
                plan.mark_step(i, "failed", str(e)[:300])
                results.append({"step": step["name"], "success": False, "error": str(e)})

            # Update progress after each step
            await self._update_progress(plan, bot)

            # Small delay between steps
            await asyncio.sleep(1)

        # Final status
        if plan.status != "failed" and plan.status != "rejected":
            plan.status = "completed"
            await self._update_progress(plan, bot)

        # Cleanup
        if plan.task_id in self.active_plans:
            del self.active_plans[plan.task_id]

        return {
            "success": plan.status == "completed",
            "steps_completed": sum(1 for s in plan.steps if s["status"] == "completed"),
            "total_steps": len(plan.steps),
            "results": results
        }

    async def _update_progress(self, plan: TaskPlan, bot):
        """Update the live progress message on Telegram"""
        if not plan.message_id or not plan.chat_id:
            return

        try:
            text = plan.get_progress_text()
            await bot.edit_message_text(
                chat_id=plan.chat_id,
                message_id=plan.message_id,
                text=text,
                parse_mode="Markdown"
            )
        except Exception:
            # Markdown might fail, try without
            try:
                text = plan.get_progress_text()
                await bot.edit_message_text(
                    chat_id=plan.chat_id,
                    message_id=plan.message_id,
                    text=text
                )
            except Exception:
                pass

    def cancel_plan(self, task_id: str) -> bool:
        """Cancel a running plan"""
        if task_id in self.active_plans:
            self.active_plans[task_id].status = "rejected"
            return True
        if task_id in self.pending_approval:
            del self.pending_approval[task_id]
            return True
        return False

    def get_plan_message_with_buttons(self, plan: TaskPlan) -> Dict:
        """Format a plan message with Accept/Reject/Changes buttons"""
        text = f"*Task Plan*\n\n"
        text += f"*Goal:* {plan.description}\n\n"
        text += f"*Steps ({len(plan.steps)}):*\n"

        for i, step in enumerate(plan.steps, 1):
            text += f"\n{i}. *{step['name']}*\n"
            text += f"   _{step['command'][:100]}_\n"

        text += f"\n---\nApprove this plan to start execution."

        buttons = [
            [{"text": "Accept Plan", "callback_data": f"plan_accept_{plan.task_id}"}],
            [{"text": "Reject Plan", "callback_data": f"plan_reject_{plan.task_id}"}],
            [{"text": "Need Changes", "callback_data": f"plan_changes_{plan.task_id}"}]
        ]

        return {"text": text, "buttons": buttons}
