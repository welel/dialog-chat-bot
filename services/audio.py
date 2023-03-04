from aiogram import Bot
import os

from aiogram.types import Voice
from pydub import AudioSegment


async def save_voice_as_mp3(bot: Bot, voice: Voice) -> str:
    """Downloads the voice in `ogg`, converts to `mp3` and returns file path."""
    voice_file_info = await bot.get_file(voice.file_id)
    await bot.download_file(
        voice_file_info.file_path,
        f"resources/temp/voice-{voice.file_unique_id}.ogg",
    )
    AudioSegment.from_file(
        f"resources/temp/voice-{voice.file_unique_id}.ogg"
    ).export(
        f"resources/voices/voice-{voice.file_unique_id}.mp3", format="mp3"
    )
    os.remove(f"resources/temp/voice-{voice.file_unique_id}.ogg")
    return f"resources/voices/voice-{voice.file_unique_id}.mp3"
