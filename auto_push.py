"""
NOVA - Auto Push to GitHub
Runs daily at 5PM to commit and push all changes to NOVA-AI repo.
Called by the scheduler or manually.
"""

import os
import subprocess
import sys
from datetime import datetime

NOVA_DIR = os.path.dirname(os.path.abspath(__file__))


def auto_push():
    """Commit all changes and push to GitHub"""
    os.chdir(NOVA_DIR)
    results = []

    # Check if there are changes
    status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=NOVA_DIR)
    if not status.stdout.strip():
        results.append("No changes to push.")
        return "\n".join(results)

    # Stage all tracked + new code files (not sensitive data)
    subprocess.run(["git", "add", "-A"], capture_output=True, text=True, cwd=NOVA_DIR)
    results.append(f"Staged changes: {len(status.stdout.strip().splitlines())} files")

    # Commit with date
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"NOVA auto-backup {today}"

    commit = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        capture_output=True, text=True, cwd=NOVA_DIR
    )

    if commit.returncode == 0:
        results.append(f"Committed: {commit_msg}")
    else:
        results.append(f"Commit: {commit.stdout or commit.stderr}")
        if "nothing to commit" in (commit.stdout + commit.stderr):
            return "Nothing to commit. All up to date."

    # Push
    push = subprocess.run(
        ["git", "push", "-u", "origin", "master"],
        capture_output=True, text=True, cwd=NOVA_DIR
    )

    if push.returncode == 0:
        results.append("Pushed to GitHub successfully.")
    else:
        # Try main branch
        push2 = subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            capture_output=True, text=True, cwd=NOVA_DIR
        )
        if push2.returncode == 0:
            results.append("Pushed to GitHub successfully.")
        else:
            results.append(f"Push failed: {push.stderr or push2.stderr}")

    return "\n".join(results)


if __name__ == "__main__":
    print(auto_push())
