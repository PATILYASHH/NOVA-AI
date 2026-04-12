"""
NOVA Watchdog - Keeps NOVA always running.
Restarts NOVA if it crashes. Run this instead of main.py for always-on mode.
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs", "watchdog.log")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - WATCHDOG - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger()


def run_nova():
    """Run NOVA and return when it exits"""
    log.info("Starting NOVA...")
    try:
        process = subprocess.run(
            [sys.executable, "main.py"],
            cwd=BASE_DIR
        )
        return process.returncode
    except KeyboardInterrupt:
        log.info("NOVA stopped by user (Ctrl+C)")
        return -1
    except Exception as e:
        log.error(f"NOVA crashed: {e}")
        return 1


def main():
    log.info("=" * 40)
    log.info("NOVA Watchdog started - always-on mode")
    log.info("=" * 40)

    restart_count = 0
    max_rapid_restarts = 5
    rapid_restart_window = 60  # seconds
    restart_times = []

    while True:
        start_time = time.time()
        exit_code = run_nova()

        if exit_code == -1:
            # User manually stopped
            log.info("NOVA stopped manually. Watchdog exiting.")
            break

        elapsed = time.time() - start_time
        restart_count += 1
        now = time.time()
        restart_times.append(now)

        # Check for rapid restart loop (crash loop protection)
        recent_restarts = [t for t in restart_times if now - t < rapid_restart_window]
        if len(recent_restarts) >= max_rapid_restarts:
            log.error(f"NOVA crashed {max_rapid_restarts} times in {rapid_restart_window}s. Waiting 5 minutes before retry.")
            time.sleep(300)
            restart_times.clear()
            continue

        log.warning(f"NOVA exited (code: {exit_code}) after {elapsed:.0f}s. Restart #{restart_count}")

        # Wait a bit before restarting
        wait = min(10, restart_count * 2)
        log.info(f"Restarting in {wait}s...")
        time.sleep(wait)


if __name__ == "__main__":
    main()
