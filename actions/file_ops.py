"""
NOVA - File Operations Module
Handles all file and directory operations
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class FileOperations:
    """Handle file system operations"""

    @staticmethod
    def read_file(path: str, lines: Optional[int] = None) -> dict:
        """Read contents of a file"""
        try:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                return {"success": False, "error": f"File not found: {path}"}

            with open(path, "r", encoding="utf-8") as f:
                if lines:
                    content = "".join(f.readlines()[:lines])
                else:
                    content = f.read()

            # Truncate if too long for Telegram
            if len(content) > 4000:
                content = content[:4000] + "\n\n... [truncated]"

            return {"success": True, "content": content, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def write_file(path: str, content: str, append: bool = False) -> dict:
        """Write content to a file"""
        try:
            path = os.path.expanduser(path)
            mode = "a" if append else "w"

            # Create directory if needed
            dir_path = os.path.dirname(path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            with open(path, mode, encoding="utf-8") as f:
                f.write(content)

            return {"success": True, "message": f"File {'appended' if append else 'written'}: {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def delete_file(path: str) -> dict:
        """Delete a file or directory"""
        try:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                return {"success": False, "error": f"Path not found: {path}"}

            if os.path.isdir(path):
                shutil.rmtree(path)
                return {"success": True, "message": f"Directory deleted: {path}"}
            else:
                os.remove(path)
                return {"success": True, "message": f"File deleted: {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def list_directory(path: str = ".", detailed: bool = False) -> dict:
        """List contents of a directory"""
        try:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                return {"success": False, "error": f"Directory not found: {path}"}

            items = os.listdir(path)

            if detailed:
                detailed_items = []
                for item in items:
                    item_path = os.path.join(path, item)
                    is_dir = os.path.isdir(item_path)
                    size = os.path.getsize(item_path) if not is_dir else 0
                    detailed_items.append({
                        "name": item,
                        "type": "dir" if is_dir else "file",
                        "size": size
                    })
                return {"success": True, "items": detailed_items, "path": path}
            else:
                dirs = [f"[DIR] {i}" for i in items if os.path.isdir(os.path.join(path, i))]
                files = [f"      {i}" for i in items if not os.path.isdir(os.path.join(path, i))]
                listing = "\n".join(sorted(dirs) + sorted(files))
                return {"success": True, "listing": listing, "path": path, "count": len(items)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_files(pattern: str, path: str = ".", max_results: int = 20) -> dict:
        """Find files matching a pattern"""
        try:
            path = os.path.expanduser(path)
            matches = list(Path(path).rglob(pattern))[:max_results]
            files = [str(m) for m in matches]
            return {
                "success": True,
                "files": files,
                "count": len(files),
                "pattern": pattern
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def copy_file(source: str, destination: str) -> dict:
        """Copy file or directory"""
        try:
            source = os.path.expanduser(source)
            destination = os.path.expanduser(destination)

            if os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)

            return {"success": True, "message": f"Copied {source} to {destination}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def move_file(source: str, destination: str) -> dict:
        """Move file or directory"""
        try:
            source = os.path.expanduser(source)
            destination = os.path.expanduser(destination)
            shutil.move(source, destination)
            return {"success": True, "message": f"Moved {source} to {destination}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
