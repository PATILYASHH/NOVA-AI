"""
NOVA - Configuration
Your Professional AI Office Assistant
"""

import os
import shutil
from dotenv import load_dotenv

# Use the Windows certificate store for TLS. Office networks with SSL
# inspection break certifi's bundle (CERTIFICATE_VERIFY_FAILED on Telegram).
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
AUTHORIZED_CHAT_IDS = [int(id.strip()) for id in os.getenv("AUTHORIZED_CHAT_IDS", "").split(",") if id.strip()]

# NOVA Personality Configuration
OWNER_NAME = os.getenv("OWNER_NAME", "User")
NOVA_PERSONALITY = {
    "name": "NOVA",
    "gender": "male",
    "role": "Professional AI Office Assistant",
    "owner": OWNER_NAME,
    "traits": [
        "Professional and efficient",
        "Direct and clear communication",
        "Proactive problem solver",
        "Technically skilled",
        "Reliable and trustworthy"
    ],
    "greeting": f"Hello {OWNER_NAME}. NOVA online and ready to assist. What would you like me to handle?",
    "tone": "professional"
}

# WhatsApp sharing ("share <file> to me").
# Values live in .env only - this file is pushed to a public repo.
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "")      # intl format, no '+'
WHATSAPP_USERNAME = os.getenv("WHATSAPP_USERNAME", "")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
MEMORY_FILE = os.path.join(BASE_DIR, "memory.md")

# Claude Code Integration
# On Windows, npm exposes claude only as .cmd/.ps1 shims which
# subprocess.run(["claude", ...]) cannot launch (FileNotFoundError).
# Resolve the native exe behind the shim; fall back to cmd /c.
def _resolve_claude_cmd():
    found = shutil.which("claude.exe") or shutil.which("claude")
    if not found:
        return ["claude"]
    if found.lower().endswith(".exe"):
        return [found]
    native = os.path.join(os.path.dirname(found), "node_modules",
                          "@anthropic-ai", "claude-code", "bin", "claude.exe")
    if os.path.exists(native):
        return [native]
    if found.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", found]
    return [found]

CLAUDE_CMD = _resolve_claude_cmd()  # argv prefix for subprocess calls
CLAUDE_CODE_PATH = CLAUDE_CMD[-1]

# Allowed Operations
ALLOWED_OPERATIONS = [
    "file_read",
    "file_write",
    "file_delete",
    "run_command",
    "open_app",
    "close_app",
    "clipboard_read",
    "clipboard_write",
    "screenshot",
    "code_execute",
    "git_operations",
    "browser_open",
    "system_info"
]
