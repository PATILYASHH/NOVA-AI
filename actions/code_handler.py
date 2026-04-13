"""
NOVA - Code Handler Module
Handles code execution, editing, Claude Code integration, and Graphify knowledge graphs
"""

import os
import json
import subprocess
import tempfile
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Cache GitHub username (fetched once via gh cli)
_gh_username_cache = None

def _get_gh_username() -> str:
    """Get authenticated GitHub username from gh cli"""
    global _gh_username_cache
    if _gh_username_cache:
        return _gh_username_cache
    try:
        r = subprocess.run(["gh", "api", "user", "--jq", ".login"],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            _gh_username_cache = r.stdout.strip()
            return _gh_username_cache
    except Exception:
        pass
    return "user"


class CodeHandler:
    """Handle code-related operations"""

    INTERPRETERS = {
        "python": "python",
        "py": "python",
        "node": "node",
        "javascript": "node",
        "js": "node",
        "powershell": "powershell -ExecutionPolicy Bypass -File",
        "ps1": "powershell -ExecutionPolicy Bypass -File",
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
    def run_claude_code(prompt: str, working_dir: Optional[str] = None, timeout: int = 300,
                        skip_permissions: bool = True) -> dict:
        """Execute a task using Claude Code CLI via stdin pipe"""
        try:
            cwd = working_dir or os.getcwd()

            cmd = ["claude", "-p"]
            if skip_permissions:
                cmd.append("--dangerously-skip-permissions")

            # Pipe prompt via stdin to avoid shell argument length limits
            result = subprocess.run(
                cmd,
                input=prompt,
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

            subprocess.Popen(f'"{editor}" "{file_path}"', shell=True)
            return {"success": True, "message": f"Opened {file_path} in {editor}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # === GRAPHIFY INTEGRATION ===

    @staticmethod
    def graphify_build(path: str, timeout: int = 300) -> dict:
        """Build a knowledge graph of a codebase using Graphify"""
        try:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                return {"success": False, "error": f"Path not found: {path}"}

            result = subprocess.run(
                ["graphify", path],
                capture_output=True,
                text=True,
                cwd=path,
                timeout=timeout
            )

            output = result.stdout or result.stderr or "Graph build completed"
            graph_out = os.path.join(path, "graphify-out")
            graph_json = os.path.join(graph_out, "graph.json")

            if os.path.exists(graph_json):
                return {
                    "success": True,
                    "output": output[:2000],
                    "graph_path": graph_json,
                    "project_path": path
                }
            else:
                return {
                    "success": result.returncode == 0,
                    "output": output[:2000],
                    "error": "Graph built but graph.json not found" if result.returncode == 0 else output[:500]
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Graph build timed out after {timeout}s"}
        except FileNotFoundError:
            return {"success": False, "error": "Graphify not installed. Run: pip install graphifyy"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def graphify_query(question: str, project_path: str) -> dict:
        """Query a project's knowledge graph and return relevant context"""
        try:
            graph_json = os.path.join(project_path, "graphify-out", "graph.json")
            if not os.path.exists(graph_json):
                return {"success": False, "error": f"No graph found for {project_path}. Run /graphify {project_path} first."}

            with open(graph_json, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)

            # Extract relevant nodes based on question keywords
            question_lower = question.lower()
            keywords = [w for w in question_lower.split() if len(w) > 2]

            relevant_nodes = []
            nodes = graph_data.get("nodes", [])

            for node in nodes:
                node_text = json.dumps(node, default=str).lower()
                score = sum(1 for kw in keywords if kw in node_text)
                if score > 0:
                    relevant_nodes.append((score, node))

            # Sort by relevance and take top results
            relevant_nodes.sort(key=lambda x: x[0], reverse=True)
            top_nodes = [n[1] for n in relevant_nodes[:15]]

            if not top_nodes:
                return {
                    "success": True,
                    "context": "No directly relevant nodes found in the knowledge graph.",
                    "node_count": len(nodes)
                }

            # Format context for Claude
            context_parts = []
            for node in top_nodes:
                name = node.get("name", node.get("id", "unknown"))
                node_type = node.get("type", "unknown")
                desc = node.get("description", node.get("summary", ""))
                file_path = node.get("file", node.get("path", ""))

                entry = f"[{node_type}] {name}"
                if file_path:
                    entry += f" ({file_path})"
                if desc:
                    entry += f": {desc[:200]}"
                context_parts.append(entry)

            context = "\n".join(context_parts)
            return {
                "success": True,
                "context": context,
                "relevant_count": len(top_nodes),
                "total_nodes": len(nodes)
            }
        except json.JSONDecodeError:
            return {"success": False, "error": "graph.json is corrupted"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def graphify_status() -> dict:
        """Check which projects have been indexed with Graphify"""
        indexed = []
        search_paths = [
            "C:\\code",
            os.path.expanduser("~\\projects"),
            os.path.expanduser("~\\code"),
        ]

        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
            try:
                for item in os.listdir(search_path):
                    full_path = os.path.join(search_path, item)
                    graph_out = os.path.join(full_path, "graphify-out", "graph.json")
                    if os.path.exists(graph_out):
                        try:
                            size = os.path.getsize(graph_out)
                            mtime = os.path.getmtime(graph_out)
                            from datetime import datetime
                            indexed.append({
                                "project": item,
                                "path": full_path,
                                "graph_size": f"{size // 1024}KB",
                                "last_updated": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                            })
                        except Exception:
                            pass
            except Exception:
                pass

        return {
            "success": True,
            "indexed_projects": indexed,
            "count": len(indexed)
        }

    # === GITHUB CLI OPERATIONS ===

    @staticmethod
    def github_create_repo(name: str, description: str = "", private: bool = False, path: str = None) -> dict:
        """Create a new GitHub repository and link it to a local folder"""
        try:
            visibility = "--private" if private else "--public"
            cwd = path or os.getcwd()

            if path and os.path.exists(path) and os.path.exists(os.path.join(path, ".git")):
                # Local git repo exists - use --source to create and push
                cmd = ["gh", "repo", "create", name, visibility,
                       "--description", description or f"{name} project",
                       "--source", path, "--push"]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=60)

                if result.returncode != 0:
                    # --source failed, try manual approach: create empty repo then add remote + push
                    cmd2 = ["gh", "repo", "create", name, visibility,
                            "--description", description or f"{name} project"]
                    result2 = subprocess.run(cmd2, capture_output=True, text=True, cwd=cwd, timeout=30)

                    if result2.returncode == 0:
                        # Add remote and push
                        subprocess.run(["git", "remote", "remove", "origin"],
                                       capture_output=True, text=True, cwd=cwd)
                        subprocess.run(["git", "remote", "add", "origin",
                                        f"https://github.com/{_get_gh_username()}/{name}.git"],
                                       capture_output=True, text=True, cwd=cwd)
                        subprocess.run(["git", "branch", "-M", "main"],
                                       capture_output=True, text=True, cwd=cwd)
                        push = subprocess.run(["git", "push", "-u", "origin", "main"],
                                              capture_output=True, text=True, cwd=cwd, timeout=30)
                        result = push if push.returncode == 0 else result2
                    else:
                        result = result2
            else:
                # No local repo - just create empty GitHub repo
                cmd = ["gh", "repo", "create", name, visibility,
                       "--description", description or f"{name} project", "--clone"]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=60)

            output = result.stdout.strip() or result.stderr.strip()
            return {
                "success": result.returncode == 0,
                "output": output,
                "repo_url": f"https://github.com/{_get_gh_username()}/{name}" if result.returncode == 0 else None
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "GitHub operation timed out"}
        except FileNotFoundError:
            return {"success": False, "error": "GitHub CLI (gh) not installed. Install from https://cli.github.com"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def github_create_pr(title: str, body: str = "", base: str = "main", repo_path: str = None) -> dict:
        """Create a pull request"""
        try:
            cmd = ["gh", "pr", "create", "--title", title, "--body", body or "Auto-generated PR by NOVA", "--base", base]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=repo_path or os.getcwd(),
                timeout=30
            )
            output = result.stdout.strip() or result.stderr.strip()
            return {"success": result.returncode == 0, "output": output}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def github_list_repos() -> dict:
        """List user's GitHub repositories"""
        try:
            result = subprocess.run(
                ["gh", "repo", "list", "--limit", "20", "--json", "name,description,url,isPrivate,updatedAt"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                repos = json.loads(result.stdout)
                return {"success": True, "repos": repos, "count": len(repos)}
            return {"success": False, "error": result.stderr.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def github_repo_info(repo_name: str) -> dict:
        """Get info about a specific repo"""
        try:
            result = subprocess.run(
                ["gh", "repo", "view", repo_name, "--json", "name,description,url,defaultBranchRef,stargazerCount,forkCount"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                return {"success": True, "info": json.loads(result.stdout)}
            return {"success": False, "error": result.stderr.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def auto_commit_push(repo_path: str, message: str = None) -> dict:
        """Auto stage all changes, commit with message, and push"""
        try:
            if not os.path.exists(repo_path):
                return {"success": False, "error": f"Path not found: {repo_path}"}

            results = []

            # Stage all changes
            r = subprocess.run(["git", "add", "-A"], capture_output=True, text=True, cwd=repo_path, timeout=15)
            results.append(f"git add: {'OK' if r.returncode == 0 else r.stderr.strip()}")

            # Check if there are changes to commit
            r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=repo_path, timeout=10)
            if not r.stdout.strip():
                return {"success": True, "output": "Nothing to commit, working tree clean", "results": results}

            # Generate commit message if not provided
            if not message:
                message = f"NOVA auto-commit {subprocess.run(['date', '/t'], capture_output=True, text=True, shell=True).stdout.strip()}"

            # Commit
            r = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True, cwd=repo_path, timeout=15)
            results.append(f"git commit: {'OK' if r.returncode == 0 else r.stderr.strip()}")

            if r.returncode != 0:
                return {"success": False, "output": "\n".join(results), "error": r.stderr.strip()}

            # Push
            r = subprocess.run(["git", "push"], capture_output=True, text=True, cwd=repo_path, timeout=30)
            results.append(f"git push: {'OK' if r.returncode == 0 else r.stderr.strip()}")

            # Try push with --set-upstream if regular push fails
            if r.returncode != 0:
                branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=repo_path).stdout.strip()
                r = subprocess.run(["git", "push", "--set-upstream", "origin", branch or "main"],
                                   capture_output=True, text=True, cwd=repo_path, timeout=30)
                results.append(f"git push -u: {'OK' if r.returncode == 0 else r.stderr.strip()}")

            return {
                "success": r.returncode == 0,
                "output": "\n".join(results),
                "results": results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
