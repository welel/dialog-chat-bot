import io
import os

from aiogram import Bot
from aiogram.types import Voice
from pydub import AudioSegment

from config import configs


async def save_voice_as_mp3(bot: Bot, voice: Voice) -> str:
    """Downloads the voice in ogg, converts to mp3 and returns file path."""
    voice_file_info = await bot.get_file(voice.file_id)
    voice_ogg = io.BytesIO()
    await bot.download_file(voice_file_info.file_path, voice_ogg)
    voice_mp3_path = os.path.join(
        configs.VOICES_DIRECTORY, f"voice-{voice.file_unique_id}.mp3"
    )
    AudioSegment.from_file(voice_ogg, format="ogg").export(
        voice_mp3_path, format="mp3"
    )
    return voice_mp3_path
