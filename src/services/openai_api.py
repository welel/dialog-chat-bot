"""A module provides a function to complete a prompt with OpenAI's model."""
import os
import logging
from typing import Iterable

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.config import ChatModel, configs


client = AsyncOpenAI(api_key=configs.OPENAI_TOKEN)
logger: logging.Logger = logging.getLogger(__name__)


async def complete(
    messages: Iterable[ChatCompletionMessageParam], chat_model: ChatModel
) -> str:
    """Completes the given prompt using OpenAI's language model.

    Args:
        messages: A list of messages comprising the conversation so far.
        chat_model: Chat model to use for the completion.

    Returns:
        str: The completed text generated by the model.
    """
    try:
        completion = await client.chat.completions.create(
            messages=messages, **chat_model.get_openai_params()
        )
    except Exception as e:
        logger.exception(
            "Error while completion: %s. Messages: %s", e, messages
        )
        raise
    message = completion.choices[0].message.content or ""
    return message.strip()


async def audio_to_text(file_path: str, delete_file: bool = True) -> str:
    """Gets audio file path and returns transcribed text.

    Args:
        file_path: The audio file path to transcribe, in one of these formats:
            flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.
        delete_file: Delete audio file after transcribition. Default: True.

    Returns:
        The transcription text of the audio file.
    """
    with open(file_path, "rb") as audio_file:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )

    if delete_file:
        os.remove(file_path)

    logger.debug("Transcribed text: %s", transcript.text)
    return transcript.text