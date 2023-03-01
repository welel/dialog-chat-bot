from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from errors import errors


router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    ...
