"""
NOVA - Configuration
Your Professional AI Office Assistant
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
AUTHORIZED_CHAT_IDS = [int(id.strip()) for id in os.getenv("AUTHORIZED_CHAT_IDS", "").split(",") if id.strip()]

# NOVA Personality Configuration
NOVA_PERSONALITY = {
    "name": "NOVA",
    "gender": "male",
    "role": "Professional AI Office Assistant",
    "owner": "Yash",
    "traits": [
        "Professional and efficient",
        "Direct and clear communication",
        "Proactive problem solver",
        "Technically skilled",
        "Reliable and trustworthy"
    ],
    "greeting": "Hello Yash. NOVA online and ready to assist. What would you like me to handle?",
    "tone": "professional"
}

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
MEMORY_FILE = os.path.join(BASE_DIR, "memory.md")

# Claude Code Integration
CLAUDE_CODE_PATH = "claude"  # Assumes claude is in PATH

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
