from aiogram import Bot, F, Router
from aiogram.types import Message

from config import configs
from models import TelegramDialogManager, DictDialogStorage
from services.audio import save_voice_as_mp3
from services.openai_api import audio_to_text
from services.messages import SystemMessage, get_message


router = Router()
dialog_manager = TelegramDialogManager(DictDialogStorage())


@router.message(F.content_type == "text")
async def process_text_message(message: Message):
    """Gets text update and sends answer of an Open AI chatbot model."""
    try:
        if not message.text:
            answer = get_message(SystemMessage.NO_INPUT)
        else:
            answer = await dialog_manager.chat(
                message.from_user.id, message.chat.id, message.text
            )
        await message.reply(text=answer)
    except Exception as e:
        if configs.tg_bot.debug_mode:
            await message.reply(text=f"Error: {e}")
        raise


@router.message(F.content_type == "voice")
async def process_voice_message(message: Message, bot: Bot):
    """Gets audio update and sends answer of an Open AI chatbot model."""
    try:
        voice_path = await save_voice_as_mp3(bot, message.voice)
        transcripted_voice_text = await audio_to_text(voice_path)

        if transcripted_voice_text:
            answer = await dialog_manager.chat(
                message.from_user.id, message.chat.id, transcripted_voice_text
            )
        else:
            answer = get_message(SystemMessage.UNINTELLIGIBLE_VOICE_INPUT)
        await message.reply(text=answer)
    except Exception as e:
        if configs.tg_bot.debug_mode:
            await message.reply(text=f"Error: {e}")
        raise
