"""
NOVA - Auto Backup System
Automatically backup important files and projects
"""

import os
import json
import shutil
import zipfile
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
BACKUP_CONFIG = os.path.join(BASE_DIR, "intelligence", "data", "backup_config.json")


class AutoBackup:
    """
    Automatic backup system for files and projects
    """

    def __init__(self):
        self.config = self._load_config()
        os.makedirs(BACKUP_DIR, exist_ok=True)

    def _load_config(self) -> Dict:
        """Load backup configuration"""
        try:
            if os.path.exists(BACKUP_CONFIG):
                with open(BACKUP_CONFIG, 'r') as f:
                    return json.load(f)
        except:
            pass

        return {
            "backup_targets": [],
            "max_backups": 5,
            "exclude_patterns": [
                "node_modules",
                "__pycache__",
                ".git",
                "*.pyc",
                "*.log",
                "venv",
                ".env"
            ],
            "last_backup": None
        }

    def _save_config(self):
        """Save backup configuration"""
        try:
            os.makedirs(os.path.dirname(BACKUP_CONFIG), exist_ok=True)
            with open(BACKUP_CONFIG, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save backup config: {e}")

    def add_backup_target(self, path: str, name: str = None) -> Dict:
        """Add a path to backup targets"""
        if not os.path.exists(path):
            return {"success": False, "error": f"Path not found: {path}"}

        target = {
            "path": path,
            "name": name or os.path.basename(path),
            "added": datetime.now().isoformat(),
            "last_backup": None
        }

        # Check if already exists
        for t in self.config["backup_targets"]:
            if t["path"] == path:
                return {"success": False, "error": "Path already in backup targets"}

        self.config["backup_targets"].append(target)
        self._save_config()

        return {"success": True, "message": f"Added {path} to backup targets"}

    def remove_backup_target(self, path: str) -> Dict:
        """Remove a path from backup targets"""
        self.config["backup_targets"] = [
            t for t in self.config["backup_targets"]
            if t["path"] != path
        ]
        self._save_config()
        return {"success": True, "message": f"Removed {path} from backup targets"}

    def list_targets(self) -> List[Dict]:
        """List all backup targets"""
        return self.config["backup_targets"]

    def _should_exclude(self, path: str) -> bool:
        """Check if path should be excluded from backup"""
        path_lower = path.lower()
        for pattern in self.config["exclude_patterns"]:
            if pattern.startswith("*"):
                if path_lower.endswith(pattern[1:]):
                    return True
            elif pattern in path_lower:
                return True
        return False

    def backup_path(self, path: str, name: str = None) -> Dict:
        """Backup a specific path"""
        if not os.path.exists(path):
            return {"success": False, "error": f"Path not found: {path}"}

        try:
            name = name or os.path.basename(path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{name}_{timestamp}.zip"
            backup_path = os.path.join(BACKUP_DIR, backup_name)

            # Create zip
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isfile(path):
                    zipf.write(path, os.path.basename(path))
                else:
                    for root, dirs, files in os.walk(path):
                        # Filter excluded directories
                        dirs[:] = [d for d in dirs if not self._should_exclude(d)]

                        for file in files:
                            file_path = os.path.join(root, file)
                            if not self._should_exclude(file_path):
                                arcname = os.path.relpath(file_path, path)
                                zipf.write(file_path, arcname)

            # Get backup size
            size = os.path.getsize(backup_path)
            size_mb = size / (1024 * 1024)

            # Update config
            for target in self.config["backup_targets"]:
                if target["path"] == path:
                    target["last_backup"] = datetime.now().isoformat()

            self.config["last_backup"] = datetime.now().isoformat()
            self._save_config()

            # Cleanup old backups
            self._cleanup_old_backups(name)

            return {
                "success": True,
                "backup_path": backup_path,
                "size_mb": round(size_mb, 2),
                "message": f"Backup created: {backup_name} ({size_mb:.2f} MB)"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def backup_all(self) -> Dict:
        """Backup all configured targets"""
        results = []
        for target in self.config["backup_targets"]:
            result = self.backup_path(target["path"], target["name"])
            results.append({
                "name": target["name"],
                "path": target["path"],
                "result": result
            })

        success_count = sum(1 for r in results if r["result"]["success"])

        return {
            "success": True,
            "total": len(results),
            "successful": success_count,
            "results": results
        }

    def _cleanup_old_backups(self, name: str):
        """Keep only the last N backups for a name"""
        max_backups = self.config.get("max_backups", 5)

        # Find all backups for this name
        backups = []
        for f in os.listdir(BACKUP_DIR):
            if f.startswith(f"{name}_") and f.endswith(".zip"):
                full_path = os.path.join(BACKUP_DIR, f)
                backups.append({
                    "path": full_path,
                    "time": os.path.getmtime(full_path)
                })

        # Sort by time (newest first)
        backups.sort(key=lambda x: x["time"], reverse=True)

        # Delete old backups
        for backup in backups[max_backups:]:
            try:
                os.remove(backup["path"])
                logger.info(f"Deleted old backup: {backup['path']}")
            except Exception as e:
                logger.error(f"Failed to delete old backup: {e}")

    def list_backups(self, name: str = None) -> List[Dict]:
        """List all backups"""
        backups = []
        for f in os.listdir(BACKUP_DIR):
            if f.endswith(".zip"):
                if name and not f.startswith(f"{name}_"):
                    continue

                full_path = os.path.join(BACKUP_DIR, f)
                size = os.path.getsize(full_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(full_path))

                backups.append({
                    "name": f,
                    "path": full_path,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "created": mtime.isoformat()
                })

        backups.sort(key=lambda x: x["created"], reverse=True)
        return backups

    def restore_backup(self, backup_name: str, restore_path: str) -> Dict:
        """Restore a backup"""
        backup_path = os.path.join(BACKUP_DIR, backup_name)

        if not os.path.exists(backup_path):
            return {"success": False, "error": f"Backup not found: {backup_name}"}

        try:
            os.makedirs(restore_path, exist_ok=True)

            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_path)

            return {
                "success": True,
                "message": f"Restored to {restore_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_backup(self, backup_name: str) -> Dict:
        """Delete a backup"""
        backup_path = os.path.join(BACKUP_DIR, backup_name)

        if not os.path.exists(backup_path):
            return {"success": False, "error": f"Backup not found: {backup_name}"}

        try:
            os.remove(backup_path)
            return {"success": True, "message": f"Deleted {backup_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_backup_status(self) -> Dict:
        """Get backup system status"""
        total_size = 0
        backup_count = 0

        for f in os.listdir(BACKUP_DIR):
            if f.endswith(".zip"):
                backup_count += 1
                total_size += os.path.getsize(os.path.join(BACKUP_DIR, f))

        return {
            "backup_dir": BACKUP_DIR,
            "targets_count": len(self.config["backup_targets"]),
            "backup_count": backup_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "last_backup": self.config.get("last_backup"),
            "max_backups_per_target": self.config.get("max_backups", 5)
        }
