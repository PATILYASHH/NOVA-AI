"""
NOVA - Code Handler Module
Handles code execution, editing, and Claude Code integration
"""

import os
import subprocess
import tempfile
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CodeHandler:
    """Handle code-related operations"""

    INTERPRETERS = {
        "python": "python",
        "py": "python",
        "node": "node",
        "javascript": "node",
        "js": "node",
        "powershell": "powershell -Command",
        "ps1": "powershell -File",
        "batch": "cmd /c",
        "bat": "cmd /c",
    }

    @classmethod
    def run_code(cls, code: str, language: str = "python", timeout: int = 30) -> dict:
        """Execute code in the specified language"""
        try:
            lang = language.lower()
            if lang not in cls.INTERPRETERS:
                return {"success": False, "error": f"Unsupported language: {language}. Supported: {list(cls.INTERPRETERS.keys())}"}

            # Create temp file with appropriate extension
            extensions = {"python": ".py", "py": ".py", "node": ".js", "javascript": ".js", "js": ".js",
                          "powershell": ".ps1", "ps1": ".ps1", "batch": ".bat", "bat": ".bat"}

            ext = extensions.get(lang, ".txt")
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name

            try:
                interpreter = cls.INTERPRETERS[lang]
                if lang in ["powershell", "ps1"]:
                    command = f'{interpreter} "{temp_path}"'
                else:
                    command = f'{interpreter} "{temp_path}"'

                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                output = result.stdout or result.stderr or "Code executed successfully (no output)"

                if len(output) > 4000:
                    output = output[:4000] + "\n\n... [truncated]"

                return {
                    "success": result.returncode == 0,
                    "output": output,
                    "return_code": result.returncode
                }
            finally:
                os.unlink(temp_path)

        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Code execution timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def run_claude_code(prompt: str, working_dir: Optional[str] = None, timeout: int = 300) -> dict:
        """Execute a task using Claude Code CLI"""
        try:
            cwd = working_dir or os.getcwd()

            # Run claude with the prompt (use list form to avoid injection)
            result = subprocess.run(
                ["claude", "-p", prompt],
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout
            )

            output = result.stdout or result.stderr or "Claude Code task completed"

            if len(output) > 4000:
                output = output[:4000] + "\n\n... [truncated]"

            return {
                "success": result.returncode == 0,
                "output": output,
                "working_dir": cwd
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Claude Code task timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def git_operation(operation: str, repo_path: str, args: str = "") -> dict:
        """Execute git operations"""
        try:
            if not os.path.exists(repo_path):
                return {"success": False, "error": f"Repository path not found: {repo_path}"}

            valid_operations = ["status", "pull", "push", "commit", "add", "branch", "checkout", "log", "diff", "fetch", "stash"]

            if operation not in valid_operations:
                return {"success": False, "error": f"Invalid git operation. Use: {valid_operations}"}

            command = f"git {operation} {args}".strip()

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=repo_path,
                timeout=60
            )

            output = result.stdout or result.stderr or f"git {operation} completed"

            if len(output) > 4000:
                output = output[:4000] + "\n\n... [truncated]"

            return {
                "success": result.returncode == 0,
                "output": output,
                "command": command
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def open_in_editor(file_path: str, editor: str = "code") -> dict:
        """Open a file in code editor"""
        try:
            file_path = os.path.expanduser(file_path)

            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}"}

            subprocess.Popen([editor, file_path], shell=True)
            return {"success": True, "message": f"Opened {file_path} in {editor}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
