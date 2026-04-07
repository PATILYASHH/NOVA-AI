"""
NOVA - Power Features
Screen Vision, Web Search, File Content Search, Code Review,
Auto Git Commits, Notes, Clipboard Watcher, App Tracker,
System Dashboard, Study Reminders
"""

import os
import re
import json
import time
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "intelligence", "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ============ SCREEN VISION (OCR) ============

class ScreenVision:
    """Read text from screen using OCR"""

    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def __init__(self):
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = self.TESSERACT_PATH
            self.pytesseract = pytesseract
            self.available = True
        except ImportError:
            self.available = False
            logger.warning("pytesseract not installed")

    def read_screen(self) -> Dict:
        """Take screenshot and read all text from it"""
        if not self.available:
            return {"success": False, "error": "OCR not available"}
        try:
            import pyautogui
            from PIL import Image

            screenshot = pyautogui.screenshot()
            text = self.pytesseract.image_to_string(screenshot)
            text = text.strip()

            return {
                "success": True,
                "text": text[:3000],
                "char_count": len(text),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_area(self, x: int, y: int, width: int, height: int) -> Dict:
        """Read text from a specific screen area"""
        if not self.available:
            return {"success": False, "error": "OCR not available"}
        try:
            import pyautogui
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            text = self.pytesseract.image_to_string(screenshot).strip()
            return {"success": True, "text": text[:2000]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_image(self, image_path: str) -> Dict:
        """Read text from an image file"""
        if not self.available:
            return {"success": False, "error": "OCR not available"}
        try:
            from PIL import Image
            img = Image.open(image_path)
            text = self.pytesseract.image_to_string(img).strip()
            return {"success": True, "text": text[:3000]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def find_on_screen(self, search_text: str) -> Dict:
        """Check if specific text is visible on screen"""
        result = self.read_screen()
        if not result["success"]:
            return result
        found = search_text.lower() in result["text"].lower()
        return {
            "success": True,
            "found": found,
            "search": search_text,
            "context": result["text"][:500] if found else "",
        }


# ============ WEB SEARCH ============

class WebSearch:
    """Search the web and fetch content"""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    def search(self, query: str, num_results: int = 5) -> Dict:
        """Search the web using DuckDuckGo HTML"""
        try:
            import requests
            from bs4 import BeautifulSoup

            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            resp = requests.get(url, headers=self.HEADERS, timeout=10)

            if resp.status_code != 200:
                return {"success": False, "error": f"HTTP {resp.status_code}"}

            soup = BeautifulSoup(resp.text, "html.parser")
            results = []

            for item in soup.select(".result")[:num_results]:
                title_el = item.select_one(".result__title a")
                snippet_el = item.select_one(".result__snippet")

                if title_el:
                    results.append({
                        "title": title_el.get_text(strip=True),
                        "url": title_el.get("href", ""),
                        "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                    })

            return {"success": True, "query": query, "results": results, "count": len(results)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def fetch_page(self, url: str) -> Dict:
        """Fetch and extract text from a webpage"""
        try:
            import requests
            from bs4 import BeautifulSoup

            resp = requests.get(url, headers=self.HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove scripts and styles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            # Clean up
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines)

            return {
                "success": True,
                "url": url,
                "title": soup.title.string if soup.title else "",
                "text": text[:4000],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def quick_answer(self, query: str) -> str:
        """Get a quick answer by searching and summarizing"""
        result = self.search(query, 3)
        if not result["success"] or not result["results"]:
            return f"Couldn't find results for '{query}'."

        text = f"Search: {query}\n\n"
        for i, r in enumerate(result["results"], 1):
            text += f"{i}. {r['title']}\n   {r['snippet']}\n\n"
        return text


# ============ FILE CONTENT SEARCH ============

class FileContentSearch:
    """Search INSIDE files for text/code"""

    SKIP_DIRS = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build"}
    TEXT_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json", ".md",
                 ".txt", ".yaml", ".yml", ".toml", ".bat", ".sh", ".sql", ".dart",
                 ".java", ".cs", ".cpp", ".h", ".go", ".rs", ".xml", ".ini", ".cfg"}

    def search(self, query: str, directory: str = ".", max_results: int = 20,
               file_pattern: str = None) -> Dict:
        """Search for text inside files"""
        results = []
        directory = os.path.expanduser(directory)

        if not os.path.exists(directory):
            return {"success": False, "error": f"Directory not found: {directory}"}

        query_lower = query.lower()

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]

            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in self.TEXT_EXTS:
                    continue
                if file_pattern and not re.search(file_pattern, fname, re.IGNORECASE):
                    continue

                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if query_lower in line.lower():
                                results.append({
                                    "file": fpath,
                                    "line": line_num,
                                    "text": line.strip()[:150],
                                })
                                if len(results) >= max_results:
                                    return {"success": True, "results": results, "count": len(results), "truncated": True}
                except Exception:
                    pass

        return {"success": True, "results": results, "count": len(results), "truncated": False}

    def find_function(self, func_name: str, directory: str = ".") -> Dict:
        """Find function/class definition"""
        patterns = [
            rf"def\s+{re.escape(func_name)}\s*\(",
            rf"class\s+{re.escape(func_name)}\s*[:\(]",
            rf"function\s+{re.escape(func_name)}\s*\(",
            rf"const\s+{re.escape(func_name)}\s*=",
            rf"let\s+{re.escape(func_name)}\s*=",
        ]

        results = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in self.SKIP_DIRS]
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext not in self.TEXT_EXTS:
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            for pattern in patterns:
                                if re.search(pattern, line):
                                    results.append({
                                        "file": fpath,
                                        "line": line_num,
                                        "text": line.strip()[:150],
                                    })
                except Exception:
                    pass
        return {"success": True, "results": results, "count": len(results)}


# ============ CODE REVIEW ============

class CodeReview:
    """Review code changes using Claude brain"""

    def get_git_diff(self, repo_path: str = ".") -> str:
        """Get current git diff"""
        try:
            result = subprocess.run(
                ["git", "diff"], capture_output=True, text=True,
                cwd=repo_path, timeout=10
            )
            diff = result.stdout.strip()
            if not diff:
                result = subprocess.run(
                    ["git", "diff", "--cached"], capture_output=True, text=True,
                    cwd=repo_path, timeout=10
                )
                diff = result.stdout.strip()
            return diff[:3000] if diff else "No changes to review."
        except Exception as e:
            return f"Error: {e}"

    def review(self, repo_path: str = ".", personality=None) -> str:
        """Review code changes using Claude"""
        diff = self.get_git_diff(repo_path)
        if not diff or diff.startswith("No changes") or diff.startswith("Error"):
            return diff

        if personality:
            prompt = (
                f"Review this code diff. Find bugs, issues, improvements. "
                f"Be brief and specific.\n\nDiff:\n{diff[:2000]}"
            )
            review = personality._ask_claude(prompt, timeout=25)
            return review or "Couldn't review right now."

        return f"Changes found:\n```\n{diff[:1000]}\n```"


# ============ AUTO GIT COMMIT ============

class AutoGitCommit:
    """Generate smart commit messages using Claude"""

    def generate_message(self, repo_path: str = ".", personality=None) -> str:
        """Generate commit message from current diff"""
        try:
            diff = subprocess.run(
                ["git", "diff", "--cached", "--stat"], capture_output=True,
                text=True, cwd=repo_path, timeout=10
            ).stdout.strip()

            if not diff:
                diff = subprocess.run(
                    ["git", "diff", "--stat"], capture_output=True,
                    text=True, cwd=repo_path, timeout=10
                ).stdout.strip()

            if not diff:
                return "No changes to commit."

            if personality:
                full_diff = subprocess.run(
                    ["git", "diff"], capture_output=True, text=True,
                    cwd=repo_path, timeout=10
                ).stdout[:1500]

                msg = personality._ask_claude(
                    f"Write a git commit message for these changes. "
                    f"One line, max 72 chars. No quotes.\n\n{full_diff}",
                    timeout=15
                )
                return msg or "Update code"

            return "Update code"
        except Exception as e:
            return f"Error: {e}"

    def auto_commit(self, repo_path: str = ".", message: str = None, personality=None) -> Dict:
        """Stage all, generate message, commit"""
        try:
            subprocess.run(["git", "add", "-A"], cwd=repo_path, capture_output=True, timeout=10)

            if not message:
                message = self.generate_message(repo_path, personality)
                if message in ("No changes to commit.", "") or message.startswith("Error"):
                    return {"success": False, "error": message}

            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True, text=True, cwd=repo_path, timeout=15
            )
            return {
                "success": result.returncode == 0,
                "message": message,
                "output": result.stdout or result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============ NOTES ============

class QuickNotes:
    """Quick notes via Telegram"""

    def __init__(self):
        self.notes_file = os.path.join(DATA_DIR, "notes.json")
        self.notes = self._load()

    def _load(self) -> List:
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save(self):
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, indent=2, default=str)

    def add(self, text: str, tag: str = "general") -> str:
        self.notes.append({
            "text": text,
            "tag": tag,
            "created": datetime.now().isoformat(),
            "done": False,
        })
        self._save()
        return f"Note saved. ({len(self.notes)} total)"

    def list_all(self, tag: str = None) -> str:
        filtered = self.notes if not tag else [n for n in self.notes if n.get("tag") == tag]
        if not filtered:
            return "No notes. Use /note <text> to add one."
        text = "**Notes:**\n\n"
        for i, n in enumerate(filtered, 1):
            done = "x" if n.get("done") else " "
            text += f"[{done}] {i}. {n['text'][:60]}\n"
            text += f"    {n.get('tag', '')} | {n['created'][:10]}\n"
        return text

    def delete(self, index: int) -> str:
        if 1 <= index <= len(self.notes):
            removed = self.notes.pop(index - 1)
            self._save()
            return f"Deleted: {removed['text'][:40]}"
        return "Invalid note number."

    def mark_done(self, index: int) -> str:
        if 1 <= index <= len(self.notes):
            self.notes[index - 1]["done"] = True
            self._save()
            return "Marked as done."
        return "Invalid note number."

    def search(self, query: str) -> str:
        results = [n for n in self.notes if query.lower() in n["text"].lower()]
        if not results:
            return f"No notes matching '{query}'."
        text = f"**Notes matching '{query}':**\n\n"
        for n in results:
            text += f"- {n['text'][:60]} ({n['created'][:10]})\n"
        return text


# ============ APP USAGE TRACKER ============

class AppTracker:
    """Track which apps are running and for how long"""

    def __init__(self):
        self.tracker_file = os.path.join(DATA_DIR, "app_usage.json")
        self.data = self._load()
        self.running = False
        self.thread = None

    def _load(self) -> Dict:
        try:
            if os.path.exists(self.tracker_file):
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"daily": {}, "total": {}}

    def _save(self):
        try:
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception:
            pass

    def snapshot(self):
        """Record current running apps"""
        try:
            import psutil
            today = datetime.now().strftime("%Y-%m-%d")
            if today not in self.data["daily"]:
                self.data["daily"][today] = {}

            daily = self.data["daily"][today]

            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name']
                    if name:
                        daily[name] = daily.get(name, 0) + 1  # Each tick = ~1 min
                        self.data["total"][name] = self.data["total"].get(name, 0) + 1
                except Exception:
                    pass

            self._save()
        except Exception:
            pass

    def start(self, interval: int = 60):
        if self.running:
            return
        self.running = True

        def _loop():
            while self.running:
                self.snapshot()
                time.sleep(interval)

        self.thread = threading.Thread(target=_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def get_report(self, date: str = None) -> str:
        today = date or datetime.now().strftime("%Y-%m-%d")
        daily = self.data.get("daily", {}).get(today, {})
        if not daily:
            return f"No app usage data for {today}."

        # Sort by usage
        sorted_apps = sorted(daily.items(), key=lambda x: x[1], reverse=True)

        text = f"**App Usage - {today}:**\n\n"
        for name, ticks in sorted_apps[:15]:
            mins = ticks  # Each tick ~1 min
            if mins >= 60:
                text += f"  {name}: {mins//60}h {mins%60}m\n"
            else:
                text += f"  {name}: {mins}m\n"
        return text


# ============ SYSTEM DASHBOARD ============

class SystemDashboard:
    """Generate text-based system dashboard"""

    def generate(self) -> str:
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')

            text = "**System Dashboard**\n\n"

            # CPU bar
            cpu_bar = self._bar(cpu)
            text += f"CPU:  {cpu_bar} {cpu}%\n"

            # RAM bar
            ram_bar = self._bar(mem.percent)
            text += f"RAM:  {ram_bar} {mem.percent}% ({mem.used//(1024**3)}/{mem.total//(1024**3)}GB)\n"

            # Disk bar
            disk_bar = self._bar(disk.percent)
            text += f"Disk: {disk_bar} {disk.percent}% ({disk.free//(1024**3)}GB free)\n"

            # Battery
            try:
                bat = psutil.sensors_battery()
                if bat:
                    bat_bar = self._bar(bat.percent)
                    plug = " [Charging]" if bat.power_plugged else ""
                    text += f"Bat:  {bat_bar} {bat.percent}%{plug}\n"
            except Exception:
                pass

            # Top processes
            text += "\n**Top Processes:**\n"
            procs = []
            for p in psutil.process_iter(['name', 'memory_percent', 'cpu_percent']):
                try:
                    procs.append(p.info)
                except Exception:
                    pass

            procs.sort(key=lambda x: x.get('memory_percent', 0) or 0, reverse=True)
            for p in procs[:5]:
                text += f"  {p['name'][:20]:20s} RAM: {p.get('memory_percent', 0):.1f}%\n"

            # Uptime
            boot = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot
            hours = int(uptime.total_seconds() // 3600)
            mins = int((uptime.total_seconds() % 3600) // 60)
            text += f"\nUptime: {hours}h {mins}m"

            return text
        except Exception as e:
            return f"Dashboard error: {e}"

    def _bar(self, percent: float, width: int = 15) -> str:
        filled = int(width * percent / 100)
        return "[" + "#" * filled + "-" * (width - filled) + "]"
