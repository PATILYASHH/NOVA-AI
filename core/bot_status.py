"""
NOVA - Bot Status Manager
Updates NOVA's Telegram name and bio based on what it's doing.
Uses Unicode styled text so NOVA and status look different.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class BotStatus:
    """
    Manages NOVA's Telegram display name and short description (bio).
    Uses styled Unicode text to make NOVA name and status visually distinct.
    """

    # NOVA in bold/styled + status in different style
    # Using Unicode small caps / italic style for status
    STATUSES = {
        "online":    {"name": "NOVA",                       "bio": "Online | Ready"},
        "thinking":  {"name": "NOVA | thinking...",         "bio": "Thinking..."},
        "working":   {"name": "NOVA | working...",          "bio": "Working on a task..."},
        "coding":    {"name": "NOVA | coding...",           "bio": "Writing code..."},
        "building":  {"name": "NOVA | building...",         "bio": "Building a project..."},
        "deploying": {"name": "NOVA | deploying...",        "bio": "Deploying..."},
        "pushing":   {"name": "NOVA | pushing...",          "bio": "Pushing to GitHub..."},
        "planning":  {"name": "NOVA | planning...",         "bio": "Making a plan..."},
        "reading":   {"name": "NOVA | reading...",          "bio": "Reading a file..."},
        "searching": {"name": "NOVA | searching...",        "bio": "Searching..."},
        "fixing":    {"name": "NOVA | fixing bugs...",      "bio": "Fixing bugs..."},
        "sleeping":  {"name": "NOVA | zzz",                 "bio": "Idle | Send a message to wake me"},
        "error":     {"name": "NOVA",                       "bio": "Had an error, but I'm here"},
        "busy":      {"name": "NOVA | busy...",             "bio": "Working on something big..."},
    }

    def __init__(self, bot=None):
        self.bot = bot
        self.current_status = "online"
        self._last_name_change = None
        self._name_cooldown = 5  # 5 seconds between name changes (fast resets)
        self._reset_task = None

    def set_bot(self, bot):
        """Set the bot instance (called after bot is created)"""
        self.bot = bot

    async def set_status(self, status: str, custom_bio: str = None, auto_reset: int = 0):
        """
        Update NOVA's status on Telegram.
        """
        if not self.bot:
            return

        if status == self.current_status and not custom_bio:
            return

        config = self.STATUSES.get(status, self.STATUSES["online"])
        self.current_status = status

        # Cancel any pending auto-reset first
        if self._reset_task and not self._reset_task.done():
            self._reset_task.cancel()
            self._reset_task = None

        # Update name (with short cooldown)
        now = datetime.now()
        can_change_name = (
            not self._last_name_change or
            (now - self._last_name_change).total_seconds() >= self._name_cooldown or
            status == "online"  # Always allow reset to online
        )

        if can_change_name:
            try:
                await self.bot.set_my_name(config["name"])
                self._last_name_change = now
            except Exception as e:
                logger.debug(f"Name change failed: {e}")

        # Update bio
        try:
            bio = custom_bio or config["bio"]
            await self.bot.set_my_short_description(bio)
        except Exception as e:
            logger.debug(f"Bio update failed: {e}")

        # Auto-reset to online
        if auto_reset > 0:
            self._reset_task = asyncio.create_task(self._auto_reset(auto_reset))
        elif status != "online" and status not in ("working", "building", "busy"):
            # Auto-reset thinking/planning/reading after 30s
            self._reset_task = asyncio.create_task(self._auto_reset(30))

    async def _auto_reset(self, delay: int):
        """Reset status to online after delay"""
        try:
            await asyncio.sleep(delay)
            await self.set_status("online")
        except asyncio.CancelledError:
            pass

    async def reset(self):
        """Reset to online status immediately"""
        await self.set_status("online")


# Global instance
bot_status = BotStatus()
