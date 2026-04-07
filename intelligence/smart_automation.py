"""
NOVA - Smart Automation
Command chaining, macros, workflow automation,
and intelligent task sequencing
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Macro:
    """A recorded macro - sequence of commands"""

    def __init__(self, name: str, description: str = "", steps: List[Dict] = None):
        self.name = name
        self.description = description
        self.steps = steps or []
        self.created_at = datetime.now().isoformat()
        self.run_count = 0
        self.last_run = None

    def add_step(self, command: str, params: Dict = None, delay: float = 0):
        """Add a step to the macro"""
        self.steps.append({
            "command": command,
            "params": params or {},
            "delay": delay,
            "order": len(self.steps)
        })

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "created_at": self.created_at,
            "run_count": self.run_count,
            "last_run": self.last_run,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Macro':
        macro = cls(data["name"], data.get("description", ""))
        macro.steps = data.get("steps", [])
        macro.created_at = data.get("created_at", datetime.now().isoformat())
        macro.run_count = data.get("run_count", 0)
        macro.last_run = data.get("last_run")
        return macro


class CommandChain:
    """Chain multiple commands with conditions"""

    def __init__(self, name: str = ""):
        self.name = name
        self.commands = []
        self.results = []
        self.status = "pending"

    def add(self, command: str, params: Dict = None,
            on_success: str = None, on_failure: str = None,
            condition: str = None):
        """Add command to chain"""
        self.commands.append({
            "command": command,
            "params": params or {},
            "on_success": on_success,
            "on_failure": on_failure,
            "condition": condition,
            "status": "pending"
        })

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "commands": self.commands,
            "results": self.results,
            "status": self.status,
        }


class SmartAutomation:
    """
    NOVA's automation engine
    - Create and run macros
    - Chain commands with conditions
    - Smart workflows with error handling
    - Batch operations
    """

    def __init__(self):
        self.macros: Dict[str, Macro] = {}
        self.active_chains: List[CommandChain] = []
        self.command_executor = None  # Set by telegram_bot
        self.recording = False
        self.recording_macro = None
        self._load_macros()
        logger.info("Smart Automation initialized")

    def _macros_file(self):
        return os.path.join(BASE_DIR, "intelligence", "data", "macros.json")

    def _load_macros(self):
        """Load saved macros"""
        try:
            path = self._macros_file()
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, macro_data in data.items():
                        self.macros[name] = Macro.from_dict(macro_data)
        except Exception as e:
            logger.error(f"Failed to load macros: {e}")

    def _save_macros(self):
        """Save macros"""
        try:
            os.makedirs(os.path.dirname(self._macros_file()), exist_ok=True)
            with open(self._macros_file(), 'w', encoding='utf-8') as f:
                json.dump({name: macro.to_dict() for name, macro in self.macros.items()},
                          f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save macros: {e}")

    def set_executor(self, executor: Callable):
        """Set the command executor function"""
        self.command_executor = executor

    # ============ MACRO OPERATIONS ============

    def create_macro(self, name: str, description: str = "",
                     steps: List[Dict] = None) -> Macro:
        """Create a new macro"""
        macro = Macro(name, description, steps)
        self.macros[name] = macro
        self._save_macros()
        return macro

    def start_recording(self, name: str, description: str = ""):
        """Start recording a macro"""
        self.recording = True
        self.recording_macro = Macro(name, description)
        return f"Recording macro '{name}'. Use /stopmacro to stop."

    def record_command(self, command: str, params: Dict = None):
        """Record a command during macro recording"""
        if self.recording and self.recording_macro:
            self.recording_macro.add_step(command, params)
            return True
        return False

    def stop_recording(self) -> Optional[Macro]:
        """Stop recording and save macro"""
        if self.recording and self.recording_macro:
            self.recording = False
            macro = self.recording_macro
            self.macros[macro.name] = macro
            self._save_macros()
            self.recording_macro = None
            return macro
        return None

    def delete_macro(self, name: str) -> bool:
        """Delete a macro"""
        if name in self.macros:
            del self.macros[name]
            self._save_macros()
            return True
        return False

    def list_macros(self) -> str:
        """List all macros"""
        if not self.macros:
            return "No macros saved. Use /recordmacro <name> to create one."

        text = "**Saved Macros:**\n\n"
        for name, macro in self.macros.items():
            text += f"**{name}** - {macro.description or 'No description'}\n"
            text += f"  Steps: {len(macro.steps)} | Runs: {macro.run_count}\n"
            for i, step in enumerate(macro.steps[:5]):
                text += f"  {i+1}. `{step['command']}`\n"
            if len(macro.steps) > 5:
                text += f"  ... and {len(macro.steps) - 5} more steps\n"
            text += "\n"
        return text

    async def run_macro(self, name: str, progress_callback: Callable = None) -> Dict:
        """Execute a macro"""
        if name not in self.macros:
            return {"success": False, "error": f"Macro '{name}' not found"}

        macro = self.macros[name]
        results = []
        all_success = True

        for i, step in enumerate(macro.steps):
            if progress_callback:
                await progress_callback(f"Step {i+1}/{len(macro.steps)}: {step['command']}")

            # Execute step
            if self.command_executor:
                try:
                    result = await self.command_executor(step["command"], step.get("params", {}))
                    results.append({"step": i, "command": step["command"],
                                    "result": str(result)[:200], "success": True})
                except Exception as e:
                    results.append({"step": i, "command": step["command"],
                                    "error": str(e), "success": False})
                    all_success = False
            else:
                results.append({"step": i, "command": step["command"],
                                "error": "No executor configured", "success": False})
                all_success = False

            # Delay between steps if specified
            if step.get("delay", 0) > 0:
                await asyncio.sleep(step["delay"])

        # Update macro stats
        macro.run_count += 1
        macro.last_run = datetime.now().isoformat()
        self._save_macros()

        return {
            "success": all_success,
            "macro": name,
            "steps_total": len(macro.steps),
            "steps_success": sum(1 for r in results if r["success"]),
            "results": results
        }

    # ============ COMMAND CHAINING ============

    def create_chain(self, commands: List[str], name: str = "") -> CommandChain:
        """Create a command chain from a list of commands"""
        chain = CommandChain(name or f"chain_{datetime.now().strftime('%H%M%S')}")
        for cmd in commands:
            chain.add(cmd)
        self.active_chains.append(chain)
        return chain

    async def execute_chain(self, chain: CommandChain,
                            progress_callback: Callable = None) -> Dict:
        """Execute a command chain"""
        chain.status = "running"
        results = []

        for i, cmd_data in enumerate(chain.commands):
            cmd = cmd_data["command"]

            if progress_callback:
                await progress_callback(f"Chain step {i+1}/{len(chain.commands)}: {cmd}")

            if self.command_executor:
                try:
                    result = await self.command_executor(cmd, cmd_data.get("params", {}))
                    cmd_data["status"] = "completed"
                    results.append({"command": cmd, "result": str(result)[:200], "success": True})

                    # Handle on_success redirect
                    if cmd_data.get("on_success"):
                        results.append({"command": cmd_data["on_success"],
                                        "note": "Triggered by on_success"})

                except Exception as e:
                    cmd_data["status"] = "failed"
                    results.append({"command": cmd, "error": str(e), "success": False})

                    # Handle on_failure redirect
                    if cmd_data.get("on_failure"):
                        results.append({"command": cmd_data["on_failure"],
                                        "note": "Triggered by on_failure"})
                    else:
                        break  # Stop chain on failure if no handler

        chain.results = results
        chain.status = "completed" if all(r.get("success", False) for r in results) else "failed"

        return chain.to_dict()

    # ============ QUICK CHAINS ============

    def parse_chain_from_text(self, text: str) -> Optional[List[str]]:
        """Parse a chain of commands from natural language"""
        # Detect chaining patterns
        separators = [" then ", " and then ", " && ", " after that ", " next "]

        for sep in separators:
            if sep in text.lower():
                parts = text.lower().split(sep)
                return [p.strip() for p in parts if p.strip()]

        # Check for numbered steps
        import re
        numbered = re.findall(r'(?:\d+[.)]\s*)(.+?)(?=\d+[.)]|$)', text)
        if len(numbered) > 1:
            return [s.strip() for s in numbered if s.strip()]

        return None

    # ============ PREDEFINED QUICK ACTIONS ============

    def get_quick_actions(self) -> Dict[str, List[str]]:
        """Get predefined quick action chains"""
        return {
            "morning": [
                "/status",
                "/disk",
                "/battery",
            ],
            "git_save": [
                "/git . status",
                "/git . add .",
                "/git . commit -m 'Quick save'",
            ],
            "cleanup": [
                "/cleantemp",
                "/emptybin",
                "/disk",
            ],
            "dev_start": [
                "/status",
                "/open vscode",
            ],
        }

    def get_summary(self) -> str:
        """Get automation summary"""
        text = "**Smart Automation Status**\n\n"
        text += f"**Macros:** {len(self.macros)} saved\n"
        text += f"**Active Chains:** {len(self.active_chains)}\n"
        text += f"**Recording:** {'Yes' if self.recording else 'No'}\n"

        if self.macros:
            text += "\n**Top Macros:**\n"
            sorted_macros = sorted(self.macros.values(),
                                    key=lambda m: m.run_count, reverse=True)
            for macro in sorted_macros[:5]:
                text += f"- {macro.name}: {macro.run_count} runs, {len(macro.steps)} steps\n"

        return text
