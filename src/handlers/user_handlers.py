from aiogram import Bot, F, Router
from aiogram.types import Message

from src.errors.errors import EmptyTrancriptionResult
from src.handlers.helpers import debug_handler_reply
from src.models import TelegramDialogManager, DictDialogStorage
from src.services.messages import SystemMessage, get_message


router = Router()
dialog_manager = TelegramDialogManager(DictDialogStorage())


@router.message(F.content_type == "text")
@debug_handler_reply
async def process_text_message(message: Message):
    """Gets text update and sends answer of an Open AI chatbot model."""
    if not message.text:
        answer = get_message(SystemMessage.NO_INPUT)
        await message.reply(text=answer)
    else:
        await dialog_manager.reply_on_text(message)


@router.message(F.content_type == "voice")
@debug_handler_reply
async def process_voice_message(message: Message, bot: Bot):
    """Gets audio update and sends answer of an Open AI chatbot model."""
    try:
        await dialog_manager.reply_on_voice(message, bot)

    except EmptyTrancriptionResult:
        answer = get_message(SystemMessage.UNINTELLIGIBLE_VOICE_INPUT)
        await message.reply(text=answer)
