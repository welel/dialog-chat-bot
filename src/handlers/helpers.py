import functools

from aiogram.types import Message

from src.config import configs
from src.config.config import MAX_TELEGRAM_MESSAGE_LEN


def process_error(error_message: str) -> str:
    """Translates the message to human and adds Markdown style."""

    # Handle OpenAI location restriction.
    if "unable_to_access" in error_message:
        error_message = (
            "Most likely your requests for OpenAI are blocked due to your "
            "region. Try using a VPN or deploying the bot on a server in a "
            "different region."
        )

    error_message = error_message[:MAX_TELEGRAM_MESSAGE_LEN - 13]
    return f"```Error: {error_message}```"


def debug_handler_reply(handler):
    """Replies on message with raised error message."""

    @functools.wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if not isinstance(message, Message):
            return await handler(message, *args, **kwargs)

        try:
            return await handler(message, *args, **kwargs)
        except Exception as e:
            if configs.tg_bot.debug_mode:
                error_message = process_error(str(e))
                await message.reply(text=error_message, parse_mode="Markdown")
            raise
    return wrapper
