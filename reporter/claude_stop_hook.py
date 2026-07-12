"""
NOVA Claude Reporter - Stop Hook
Registered as a global Claude Code Stop hook. Fires every time a Claude
session (VS Code extension, terminal, anywhere) finishes a turn.

What it does:
  1. Reads hook input JSON from stdin (session_id, transcript_path, cwd)
  2. Extracts the last user prompt + last assistant reply from the transcript
  3. Appends a report entry to global.md
  4. Sends the report to Telegram via the reporter bot
  5. Records message_id -> session mapping so replies in Telegram can
     resume the exact session (handled by reporter_bot.py)

Dependency-free: stdlib only, so it runs with any system Python.
Exits 0 always - a reporting failure must never block Claude.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime

REPORTER_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(REPORTER_DIR)
ENV_FILE = os.path.join(BASE_DIR, ".env")
GLOBAL_MD = os.path.join(BASE_DIR, "global.md")
SESSIONS_FILE = os.path.join(REPORTER_DIR, "sessions.json")
MUTE_FLAG = os.path.join(REPORTER_DIR, "muted")

MAX_TG_LEN = 3800  # Telegram hard limit is 4096; leave headroom for header


def load_env():
    env = {}
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip()
    except OSError:
        pass
    return env


def extract_last_messages(transcript_path):
    """Return (last_user_text, last_assistant_text) from a session transcript."""
    last_user = ""
    last_assistant = ""
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = entry.get("message") or {}
                content = msg.get("content")
                if entry.get("type") == "user":
                    # user content can be a plain string or content blocks;
                    # skip tool_result-only entries
                    if isinstance(content, str) and content.strip():
                        last_user = content.strip()
                    elif isinstance(content, list):
                        texts = [b.get("text", "") for b in content
                                 if isinstance(b, dict) and b.get("type") == "text"]
                        joined = "\n".join(t for t in texts if t).strip()
                        if joined:
                            last_user = joined
                elif entry.get("type") == "assistant" and isinstance(content, list):
                    texts = [b.get("text", "") for b in content
                             if isinstance(b, dict) and b.get("type") == "text"]
                    joined = "\n".join(t for t in texts if t).strip()
                    if joined:
                        last_assistant = joined
    except OSError:
        pass
    return last_user, last_assistant


def send_telegram(token, chat_id, text):
    """Send a message, return message_id or None."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    try:
        with urllib.request.urlopen(url, data=data, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            if result.get("ok"):
                return result["result"]["message_id"]
    except Exception:
        pass
    return None


def record_session(message_id, session_id, cwd):
    sessions = {"latest": None, "by_message": {}}
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            sessions = json.load(f)
    except (OSError, json.JSONDecodeError):
        pass
    entry = {"session_id": session_id, "cwd": cwd,
             "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    sessions["latest"] = entry
    if message_id is not None:
        sessions.setdefault("by_message", {})[str(message_id)] = entry
        # keep only the 50 most recent mappings
        keys = sorted(sessions["by_message"], key=int)
        for k in keys[:-50]:
            del sessions["by_message"][k]
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)


def append_global_md(project, session_id, task, reply):
    header_needed = not os.path.exists(GLOBAL_MD)
    with open(GLOBAL_MD, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("# Claude Global Report Log\n\n"
                    "All Claude Code sessions report here on every finished turn.\n\n")
        f.write(f"## [{datetime.now().strftime('%Y-%m-%d %H:%M')}] "
                f"{project} - session {session_id[:8]}\n\n")
        if task:
            f.write(f"**Task:** {task[:300]}\n\n")
        f.write(f"{reply}\n\n---\n\n")


def main():
    # NOVA's internal claude -p calls (and reporter bot resumes) set this
    # so they don't spam reports
    if os.environ.get("NOVA_REPORT_SUPPRESS") == "1":
        return
    if os.path.exists(MUTE_FLAG):
        return

    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    if hook_input.get("stop_hook_active"):
        return

    session_id = hook_input.get("session_id", "unknown")
    transcript_path = hook_input.get("transcript_path", "")
    cwd = hook_input.get("cwd", "")

    task, reply = extract_last_messages(transcript_path)
    if not reply:
        return

    project = os.path.basename(cwd.rstrip("\\/")) or cwd or "unknown"
    append_global_md(project, session_id, task, reply)

    env = load_env()
    token = env.get("REPORTER_BOT_TOKEN", "")
    chat_id = env.get("REPORTER_CHAT_ID", "") or (
        env.get("AUTHORIZED_CHAT_IDS", "").split(",")[0].strip())
    if not token or not chat_id:
        return

    header = f"[{project}] session {session_id[:8]}\n"
    if task:
        header += f"Task: {task[:200]}\n"
    header += "-" * 30 + "\n"
    body = reply if len(reply) <= MAX_TG_LEN else reply[:MAX_TG_LEN] + "\n[...truncated, full text in global.md]"

    message_id = send_telegram(token, chat_id, header + body)
    record_session(message_id, session_id, cwd)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never block Claude on reporter failure
    sys.exit(0)
