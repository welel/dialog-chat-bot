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
    answer: DialogMessage = dialog_manager.chat(
        message.from_user.id, text=message.text
    )
    await message.reply(text=answer.text)
