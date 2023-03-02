from aiogram import Router
from aiogram.types import Message

from models import (
    Message as DialogMessage,
    TelegramDialogManager,
    DictDialogStorage,
    OpenAIClient,
)


router: Router = Router()
dialog_manager = TelegramDialogManager(OpenAIClient(), DictDialogStorage())


@router.message()
async def process_chat(message: Message):
    """Gets any update and sends answer of an Open AI chatbot model."""
    answer: DialogMessage = await dialog_manager.chat(
        message.from_user.id, text=message.text
    )
    await message.reply(text=answer.text)
