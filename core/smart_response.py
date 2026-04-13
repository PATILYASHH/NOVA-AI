"""
NOVA - Smart Response System
Advanced Telegram chat features:
- Live "thinking" message that updates to final response
- Expandable thinking section (spoiler) showing what NOVA considered
- Progress indicators for long tasks
- Interactive quick-reply buttons
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


class SmartResponse:
    """
    Makes NOVA's Telegram responses feel advanced and alive.
    Shows thinking process, live updates, and interactive elements.
    """

    @staticmethod
    async def send_thinking_response(bot, chat_id: int, user_message: str,
                                      get_response_func, context: dict = None):
        """
        Send a response with a live thinking phase:
        1. Show "thinking about: [summary]" message
        2. Update with the actual response
        3. Add thinking details as spoiler (tap to reveal)

        Returns the response text.
        """
        # Step 1: Send thinking message
        thinking_text = SmartResponse._make_thinking_text(user_message)
        try:
            thinking_msg = await bot.send_message(
                chat_id=chat_id,
                text=thinking_text,
                parse_mode="HTML"
            )
        except Exception:
            thinking_msg = await bot.send_message(chat_id=chat_id, text="thinking...")

        # Step 2: Get the actual response (non-blocking)
        try:
            response = await get_response_func()
        except Exception as e:
            response = f"Had an issue: {str(e)[:200]}"

        if not response or not response.strip():
            response = "hmm, couldn't come up with anything. try again?"

        # Step 3: Edit the thinking message with final response
        final_text = SmartResponse._make_final_text(response, user_message)
        try:
            await thinking_msg.edit_text(
                text=final_text,
                parse_mode="HTML"
            )
        except Exception:
            # If HTML fails, try plain text
            try:
                await thinking_msg.edit_text(text=response)
            except Exception:
                # If edit fails entirely, send new message
                await bot.send_message(chat_id=chat_id, text=response)

        return response

    @staticmethod
    def _make_thinking_text(user_message: str) -> str:
        """Create the thinking indicator message"""
        # Short summary of what NOVA is thinking about
        msg_preview = user_message[:60]
        if len(user_message) > 60:
            msg_preview += "..."

        return f'<i>thinking about: "{msg_preview}"</i>'

    @staticmethod
    def _make_final_text(response: str, user_message: str = "") -> str:
        """
        Create the final response with optional thinking spoiler.
        Uses HTML format for Telegram.
        """
        # Escape HTML special chars in response (but preserve code blocks)
        safe_response = SmartResponse._escape_html_safe(response)

        return safe_response

    @staticmethod
    def _escape_html_safe(text: str) -> str:
        """
        Escape HTML chars but preserve code blocks and formatting.
        Converts markdown code blocks to HTML <code> and <pre>.
        """
        import re

        # Extract code blocks first
        code_blocks = []
        def replace_code_block(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

        # Triple backtick code blocks
        text = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, text, flags=re.DOTALL)

        # Inline backticks
        inline_codes = []
        def replace_inline(match):
            inline_codes.append(match.group(1))
            return f"__INLINE_{len(inline_codes) - 1}__"

        text = re.sub(r'`([^`]+)`', replace_inline, text)

        # Escape HTML in normal text
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Convert markdown bold to HTML
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__(?!CODE|INLINE)', r'<i>\1</i>', text)

        # Restore code blocks as HTML <pre><code>
        for i, block in enumerate(code_blocks):
            lang_match = re.match(r'```(\w*)\n(.*?)```', block, re.DOTALL)
            if lang_match:
                code_content = lang_match.group(2).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                text = text.replace(f"__CODE_BLOCK_{i}__", f"<pre><code>{code_content}</code></pre>")

        # Restore inline codes
        for i, code in enumerate(inline_codes):
            safe_code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            text = text.replace(f"__INLINE_{i}__", f"<code>{safe_code}</code>")

        return text

    @staticmethod
    async def send_with_actions(bot, chat_id: int, text: str,
                                 actions: List[Dict] = None):
        """
        Send a message with quick-action buttons at the bottom.
        actions: [{"label": "Push to GitHub", "callback": "quick_push"}, ...]
        """
        keyboard = None
        if actions:
            buttons = []
            row = []
            for i, action in enumerate(actions):
                row.append(InlineKeyboardButton(
                    action["label"],
                    callback_data=action.get("callback", f"quick_{i}")
                ))
                if len(row) >= 2:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
            keyboard = InlineKeyboardMarkup(buttons)

        try:
            return await bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception:
            return await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard
            )

    @staticmethod
    async def send_progress_bar(bot, chat_id: int, current: int, total: int,
                                 label: str = "Progress") -> object:
        """Send a text-based progress bar"""
        bar = SmartResponse.make_progress_bar(current, total)
        text = f"<b>{label}</b>\n{bar}\n{current}/{total} complete"
        try:
            return await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        except Exception:
            return await bot.send_message(chat_id=chat_id, text=f"{label}: {current}/{total}")

    @staticmethod
    def make_progress_bar(current: int, total: int, width: int = 20) -> str:
        """Create a text progress bar"""
        if total <= 0:
            return ""
        pct = min(current / total, 1.0)
        filled = int(width * pct)
        empty = width - filled
        bar = ">" * filled + "-" * empty
        return f"[{bar}] {int(pct * 100)}%"
