"""
NOVA - Vector Memory System (ChromaDB)
Semantic memory that finds relevant past conversations, facts, and knowledge
by meaning — not just keyword matching.

This gives NOVA true long-term memory:
- "What did Yash say about Flutter last week?" → finds it by meaning
- "Have we discussed this error before?" → finds similar past errors
- Automatically stores every conversation for future retrieval
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "memory", "vector_db")

# Ensure dir exists
os.makedirs(VECTOR_DB_DIR, exist_ok=True)


class VectorMemory:
    """
    Semantic memory powered by ChromaDB.
    Stores conversations, facts, and knowledge as vector embeddings.
    Retrieves by meaning similarity, not keyword matching.
    """

    def __init__(self):
        self.client = None
        self.conversations = None  # Collection for conversation turns
        self.knowledge = None      # Collection for learned facts/knowledge
        self.tasks = None          # Collection for tasks/commands done
        self._initialized = False
        self._init_db()

    def _init_db(self):
        """Initialize ChromaDB with persistent storage"""
        try:
            import chromadb
            from chromadb.config import Settings

            self.client = chromadb.PersistentClient(
                path=VECTOR_DB_DIR,
                settings=Settings(anonymized_telemetry=False)
            )

            # Create collections
            self.conversations = self.client.get_or_create_collection(
                name="conversations",
                metadata={"description": "All conversation turns between NOVA and Yash"}
            )

            self.knowledge = self.client.get_or_create_collection(
                name="knowledge",
                metadata={"description": "Facts, lessons, opinions NOVA has learned"}
            )

            self.tasks = self.client.get_or_create_collection(
                name="tasks",
                metadata={"description": "Tasks and commands NOVA has executed"}
            )

            self._initialized = True
            logger.info(f"Vector memory initialized: {self.conversations.count()} conversations, "
                        f"{self.knowledge.count()} knowledge items, {self.tasks.count()} tasks")

        except ImportError:
            logger.warning("ChromaDB not installed. Run: pip install chromadb")
        except Exception as e:
            logger.error(f"Vector memory init failed: {e}")

    def is_ready(self) -> bool:
        return self._initialized

    # === STORE ===

    def store_conversation(self, role: str, message: str, response: str = "",
                           mood: str = "neutral", topic: str = ""):
        """Store a conversation turn"""
        if not self._initialized:
            return

        try:
            now = datetime.now()
            doc_id = f"conv_{now.strftime('%Y%m%d_%H%M%S')}_{hash(message) % 10000}"

            # Combine message and response for richer embedding
            full_text = f"Yash: {message}"
            if response:
                full_text += f"\nNOVA: {response}"

            self.conversations.add(
                documents=[full_text],
                ids=[doc_id],
                metadatas=[{
                    "role": role,
                    "message": message[:500],
                    "response": response[:500],
                    "mood": mood,
                    "topic": topic,
                    "date": now.strftime("%Y-%m-%d"),
                    "time": now.strftime("%H:%M:%S"),
                    "timestamp": now.isoformat()
                }]
            )
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")

    def store_knowledge(self, content: str, category: str = "general",
                        source: str = "conversation"):
        """Store a piece of knowledge/fact"""
        if not self._initialized:
            return

        try:
            now = datetime.now()
            doc_id = f"know_{now.strftime('%Y%m%d_%H%M%S')}_{hash(content) % 10000}"

            self.knowledge.add(
                documents=[content],
                ids=[doc_id],
                metadatas=[{
                    "category": category,
                    "source": source,
                    "date": now.strftime("%Y-%m-%d"),
                    "timestamp": now.isoformat()
                }]
            )
        except Exception as e:
            logger.error(f"Failed to store knowledge: {e}")

    def store_task(self, task_description: str, result: str, success: bool,
                   category: str = "general"):
        """Store a completed task"""
        if not self._initialized:
            return

        try:
            now = datetime.now()
            doc_id = f"task_{now.strftime('%Y%m%d_%H%M%S')}_{hash(task_description) % 10000}"

            full_text = f"Task: {task_description}\nResult: {result}\nSuccess: {success}"

            self.tasks.add(
                documents=[full_text],
                ids=[doc_id],
                metadatas=[{
                    "task": task_description[:300],
                    "success": str(success),
                    "category": category,
                    "date": now.strftime("%Y-%m-%d"),
                    "timestamp": now.isoformat()
                }]
            )
        except Exception as e:
            logger.error(f"Failed to store task: {e}")

    # === RETRIEVE ===

    def recall_conversations(self, query: str, n_results: int = 5) -> List[Dict]:
        """Find past conversations similar to the query"""
        if not self._initialized:
            return []

        try:
            results = self.conversations.query(
                query_texts=[query],
                n_results=min(n_results, self.conversations.count() or 1)
            )

            if not results or not results["documents"] or not results["documents"][0]:
                return []

            memories = []
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0

                memories.append({
                    "text": doc,
                    "message": meta.get("message", ""),
                    "response": meta.get("response", ""),
                    "date": meta.get("date", ""),
                    "time": meta.get("time", ""),
                    "mood": meta.get("mood", ""),
                    "relevance": round(1 - distance, 3) if distance else 0
                })

            return memories

        except Exception as e:
            logger.error(f"Failed to recall conversations: {e}")
            return []

    def recall_knowledge(self, query: str, n_results: int = 5) -> List[Dict]:
        """Find relevant knowledge by semantic search"""
        if not self._initialized:
            return []

        try:
            results = self.knowledge.query(
                query_texts=[query],
                n_results=min(n_results, self.knowledge.count() or 1)
            )

            if not results or not results["documents"] or not results["documents"][0]:
                return []

            items = []
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0

                items.append({
                    "content": doc,
                    "category": meta.get("category", ""),
                    "source": meta.get("source", ""),
                    "date": meta.get("date", ""),
                    "relevance": round(1 - distance, 3) if distance else 0
                })

            return items

        except Exception as e:
            logger.error(f"Failed to recall knowledge: {e}")
            return []

    def recall_similar_tasks(self, query: str, n_results: int = 3) -> List[Dict]:
        """Find past tasks similar to current request"""
        if not self._initialized:
            return []

        try:
            results = self.tasks.query(
                query_texts=[query],
                n_results=min(n_results, self.tasks.count() or 1)
            )

            if not results or not results["documents"] or not results["documents"][0]:
                return []

            items = []
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                items.append({
                    "text": doc,
                    "task": meta.get("task", ""),
                    "success": meta.get("success", ""),
                    "date": meta.get("date", ""),
                })

            return items

        except Exception as e:
            logger.error(f"Failed to recall tasks: {e}")
            return []

    def get_relevant_context(self, message: str, max_items: int = 5) -> str:
        """
        Get relevant context for a message by searching ALL collections.
        Returns a formatted string ready to inject into the prompt.
        """
        if not self._initialized:
            return ""

        context_parts = []

        # Search past conversations (only include if actually relevant)
        past_convos = self.recall_conversations(message, n_results=3)
        if past_convos:
            relevant = [c for c in past_convos if c.get("relevance", 0) > 0.15]
            if relevant:
                context_parts.append("RELEVANT PAST CONVERSATIONS:")
                for c in relevant[:3]:
                    context_parts.append(f"  [{c['date']}] {c['text'][:200]}")

        # Search knowledge
        knowledge = self.recall_knowledge(message, n_results=3)
        if knowledge:
            relevant = [k for k in knowledge if k.get("relevance", 0) > 0.15]
            if relevant:
                context_parts.append("RELEVANT KNOWLEDGE:")
                for k in relevant[:3]:
                    context_parts.append(f"  [{k['category']}] {k['content'][:200]}")

        # Search similar past tasks
        past_tasks = self.recall_similar_tasks(message, n_results=2)
        if past_tasks:
            context_parts.append("SIMILAR PAST TASKS:")
            for t in past_tasks[:2]:
                context_parts.append(f"  [{t['date']}] {t['task'][:150]} → {t['success']}")

        return "\n".join(context_parts) if context_parts else ""

    # === STATS ===

    def get_stats(self) -> Dict:
        """Get memory statistics"""
        if not self._initialized:
            return {"initialized": False}

        return {
            "initialized": True,
            "conversations": self.conversations.count(),
            "knowledge": self.knowledge.count(),
            "tasks": self.tasks.count(),
            "db_path": VECTOR_DB_DIR
        }

    def get_formatted_stats(self) -> str:
        """Get formatted memory stats for display"""
        stats = self.get_stats()
        if not stats["initialized"]:
            return "Vector memory not initialized."

        return (
            f"**Vector Memory (ChromaDB)**\n\n"
            f"**Conversations stored:** {stats['conversations']}\n"
            f"**Knowledge items:** {stats['knowledge']}\n"
            f"**Tasks logged:** {stats['tasks']}\n"
            f"**DB Path:** `{stats['db_path']}`"
        )
