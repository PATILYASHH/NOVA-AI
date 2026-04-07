"""
NOVA - Conversation Memory Recall
Search past interactions: "remember that file I was working on?"
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MemoryRecall:
    """Search and recall past interactions from memory"""

    RECALL_TRIGGERS = [
        "remember", "recall", "what was", "what did", "last time",
        "yesterday", "earlier", "before", "previous", "that file",
        "that command", "that project", "history of", "when did",
    ]

    def __init__(self, memory_system):
        self.memory = memory_system

    def is_recall_query(self, text: str) -> bool:
        """Check if user is asking about past interactions"""
        text_lower = text.lower()
        return any(trigger in text_lower for trigger in self.RECALL_TRIGGERS)

    def recall(self, query: str) -> str:
        """Search memory and return relevant past interactions"""
        query_lower = query.lower()
        results = []

        # 1. Search command history in ROM
        try:
            search_terms = self._extract_search_terms(query)
            for term in search_terms:
                found = self.memory.rom.search_history(term, 10)
                for r in found:
                    r["_source"] = "command_history"
                    r["_relevance"] = self._relevance_score(query_lower, str(r))
                results.extend(found)
        except Exception as e:
            logger.debug(f"ROM search error: {e}")

        # 2. Search file history
        try:
            if any(w in query_lower for w in ["file", "read", "wrote", "edited", "created", "deleted"]):
                file_results = self._search_file_history(query_lower)
                results.extend(file_results)
        except Exception:
            pass

        # 3. Search project history
        try:
            if any(w in query_lower for w in ["project", "worked", "repo"]):
                project_results = self._search_project_history(query_lower)
                results.extend(project_results)
        except Exception:
            pass

        # 4. Search today's RAM
        try:
            ram_results = self._search_ram(query_lower)
            results.extend(ram_results)
        except Exception:
            pass

        # Deduplicate and sort by relevance
        seen = set()
        unique_results = []
        for r in results:
            key = str(r.get("command", r.get("path", r.get("name", ""))))[:50]
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        unique_results.sort(key=lambda x: x.get("_relevance", 0), reverse=True)

        return self._format_results(query, unique_results[:10])

    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from query"""
        stop_words = {"remember", "recall", "what", "was", "the", "that", "a", "an",
                      "did", "i", "we", "you", "my", "last", "time", "when", "how",
                      "yesterday", "earlier", "before", "previous", "about", "working",
                      "on", "with", "in", "do", "me", "file", "command"}
        words = query.lower().split()
        terms = [w for w in words if w not in stop_words and len(w) > 2]
        return terms if terms else [query.split()[-1]] if query.split() else [""]

    def _relevance_score(self, query: str, text: str) -> float:
        """Calculate relevance score"""
        return SequenceMatcher(None, query, text.lower()[:100]).ratio()

    def _search_file_history(self, query: str) -> List[Dict]:
        """Search file operation history"""
        results = []
        try:
            conn = self.memory.rom._connect()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT file_path, action, project, details, timestamp
                FROM file_history
                ORDER BY timestamp DESC LIMIT 30
            ''')
            rows = cursor.fetchall()
            conn.close()

            for r in rows:
                entry = {"path": r[0], "action": r[1], "project": r[2],
                         "details": r[3], "timestamp": r[4], "_source": "file_history"}
                entry["_relevance"] = self._relevance_score(query, f"{r[0]} {r[1]} {r[3] or ''}")
                if entry["_relevance"] > 0.1:
                    results.append(entry)
        except Exception:
            pass
        return results

    def _search_project_history(self, query: str) -> List[Dict]:
        """Search project change history"""
        results = []
        try:
            projects = self.memory.rom.get_all_projects()
            for p in projects:
                entry = {"name": p["name"], "path": p["path"],
                         "last_accessed": p["last_accessed"], "_source": "project"}
                entry["_relevance"] = self._relevance_score(query, f"{p['name']} {p['path']}")
                results.append(entry)
        except Exception:
            pass
        return results

    def _search_ram(self, query: str) -> List[Dict]:
        """Search today's session memory"""
        results = []
        try:
            recent = self.memory.ram.get_recent_activity(20)
            for r in recent:
                r["_source"] = "today_session"
                r["_relevance"] = self._relevance_score(query, str(r.get("command", "")))
                if r["_relevance"] > 0.1:
                    results.append(r)
        except Exception:
            pass
        return results

    def _format_results(self, query: str, results: List[Dict]) -> str:
        """Format recall results for display"""
        if not results:
            return "I couldn't find anything matching that in my memory."

        text = f"**Memory Recall Results:**\n\n"

        for r in results[:8]:
            source = r.get("_source", "unknown")

            if source == "command_history":
                status = "OK" if r.get("success") else "FAIL"
                text += f"[{status}] `{r.get('command', 'N/A')[:50]}`\n"
                text += f"  When: {r.get('timestamp', 'N/A')[:19]}\n\n"

            elif source == "file_history":
                text += f"File: `{r.get('path', 'N/A')}`\n"
                text += f"  Action: {r.get('action', 'N/A')} | When: {r.get('timestamp', 'N/A')[:19]}\n\n"

            elif source == "project":
                text += f"Project: **{r.get('name', 'N/A')}**\n"
                text += f"  Path: `{r.get('path', 'N/A')}`\n"
                text += f"  Last: {r.get('last_accessed', 'N/A')[:19]}\n\n"

            elif source == "today_session":
                status = "OK" if r.get("success") else "FAIL"
                text += f"Today [{status}]: `{r.get('command', 'N/A')[:50]}`\n\n"

        return text
