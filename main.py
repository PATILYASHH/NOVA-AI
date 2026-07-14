"""
NOVA - Main Entry Point (AGI-Enhanced)
Professional AI Office Assistant for Remote PC Control
With Intelligence Modules: NLP, Reasoning, Context, Emotion, Learning

Created for Yash
"""

import os
import sys
import logging
from datetime import datetime

# Fix encoding for background/silent mode
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TELEGRAM_BOT_TOKEN, AUTHORIZED_CHAT_IDS, NOVA_PERSONALITY, LOGS_DIR

# Setup logging
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "nova.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print NOVA startup banner"""
    banner = """
    +-----------------------------------------------------------+
    |                                                           |
    |     N   N  OOO  V   V  AAA                                |
    |     NN  N O   O V   V A   A                               |
    |     N N N O   O V   V AAAAA                               |
    |     N  NN O   O  V V  A   A                               |
    |     N   N  OOO    V   A   A                               |
    |                                                           |
    |        AGI-Enhanced AI Office Assistant                    |
    |        Remote PC Control via Telegram                     |
    |                                                           |
    +-----------------------------------------------------------+
    """
    print(banner)


def print_modules():
    """Print intelligence module status"""
    modules = """
    Intelligence Modules:
    +----------------------------------------+
    |  [+] NLP Engine         - Online       |
    |  [+] Reasoning Engine   - Online       |
    |  [+] Context Engine     - Online       |
    |  [+] Emotion Engine     - Online       |
    |  [+] Learning Loop      - Online       |
    |  [+] Goal Planner       - Online       |
    |  [+] Habit Tracker      - Online       |
    |  [+] Proactive Monitor  - Online       |
    |  [+] Anomaly Detector   - Online       |
    |  [+] Smart Automation   - Online       |
    |  [+] Self-Reflection    - Online       |
    |  [+] Self-Improvement   - Online       |
    |  [+] Style Learner      - Online       |
    |  [+] Work Setup         - Online       |
    |  [+] 3-Tier Memory      - Online       |
    +----------------------------------------+
    """
    print(modules)


# Single-instance guard. Bind a localhost port for the process lifetime.
# If it's already taken, another NOVA is polling this bot token - two pollers
# cause Telegram 409 conflicts and both instances thrash. The socket is
# released automatically by the OS when this process dies (no stale lock).
_instance_lock_socket = None
_INSTANCE_LOCK_PORT = 47921


def acquire_single_instance_lock() -> bool:
    """Return True if we got the lock, False if NOVA is already running."""
    global _instance_lock_socket
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        s.bind(("127.0.0.1", _INSTANCE_LOCK_PORT))
        s.listen(1)
        _instance_lock_socket = s  # keep alive for the process lifetime
        return True
    except OSError:
        s.close()
        return False


def check_config():
    """Verify configuration is valid"""
    errors = []

    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is not set in .env file")

    if not AUTHORIZED_CHAT_IDS:
        logger.warning("AUTHORIZED_CHAT_IDS is empty - bot will accept commands from anyone!")

    return errors


def ensure_directories():
    """Ensure all required directories exist"""
    base = os.path.dirname(os.path.abspath(__file__))
    dirs = [
        os.path.join(base, "memory", "RM"),
        os.path.join(base, "memory", "RAM"),
        os.path.join(base, "memory", "ROM"),
        os.path.join(base, "projects"),
        os.path.join(base, "self", "diary"),
        os.path.join(base, "self", "performance"),
        os.path.join(base, "logs", "daily"),
        os.path.join(base, "logs", "commands"),
        os.path.join(base, "intelligence", "data"),
        os.path.join(base, "schedules"),
        os.path.join(base, "backups"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def main():
    """Main entry point"""
    print_banner()
    print(f"Starting NOVA at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Owner: {NOVA_PERSONALITY['owner']}")
    print("-" * 60)

    # Refuse to start a second instance (would 409-conflict on the bot token).
    # Exit code 3 signals the watchdog to stop (not restart-loop).
    if not acquire_single_instance_lock():
        print("\nNOVA is already running (another instance holds the lock).")
        print("Refusing to start a second poller - it would conflict on Telegram.")
        logger.warning("Startup aborted: another NOVA instance is already running")
        sys.exit(3)

    # Check configuration
    errors = check_config()
    if errors:
        print("\nConfiguration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease configure your .env file and try again.")
        print("Copy .env.example to .env and fill in your values.")
        sys.exit(1)

    # Ensure directories
    ensure_directories()

    print(f"\nAuthorized Chat IDs: {AUTHORIZED_CHAT_IDS}")

    # Print intelligence modules
    print_modules()

    print("NOVA is starting up...")
    print("Press Ctrl+C to stop.\n")

    try:
        from telegram_bot import create_bot
        bot = create_bot()

        logger.info("NOVA AGI-Enhanced is now online and listening")
        print("NOVA is online! Send a message to your Telegram bot.")
        print("Intelligence modules active. Natural language enabled.\n")

        bot.run_polling()

    except KeyboardInterrupt:
        print("\n\nNOVA shutting down...")
        logger.info("NOVA shutdown by user")
    except Exception as e:
        logger.error(f"Error starting NOVA: {e}")
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
