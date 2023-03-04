from aiogram import Bot, F, Router
from aiogram.types import Message

from models import (
    Message as DialogMessage,
    TelegramDialogManager,
    DictDialogStorage,
    OpenAIClient,
)
from services.openai_api import audio_to_text
from services.audio import save_voice_as_mp3


router = Router()
dialog_manager = TelegramDialogManager(OpenAIClient(), DictDialogStorage())


@router.message(F.content_type == "text")
async def process_text_message(message: Message):
    """Gets text update and sends answer of an Open AI chatbot model."""
    answer: DialogMessage = await dialog_manager.chat(
        message.from_user.id, text=message.text
    )
    await message.reply(text=answer.text)


@router.message(F.content_type == "voice")
async def process_voice_message(message: Message, bot: Bot):
    """Gets audio update and sends answer of an Open AI chatbot model."""
    voice_path = await save_voice_as_mp3(bot, message.voice)
    transcripted_voice_text = await audio_to_text(voice_path)

    if transcripted_voice_text:
        answer: DialogMessage = await dialog_manager.chat(
            message.from_user.id, text=transcripted_voice_text
        )
        await message.reply(text=answer.text)
