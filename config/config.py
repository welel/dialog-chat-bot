from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .helpers import get_env_variable


MAX_TELEGRAM_MESSAGE_LEN: int = 4096


@dataclass
class TelegramBot:
    token: str
    debug_mode: bool = False


class OpenAI(BaseModel):
    """OpenAI client configuration.

    Uses the model - "gpt-3.5-turbo". More about parameters in docs.
    Docs: https://platform.openai.com/docs/api-reference/chat/create

    Attrs:
        token: The OpenAI API key to use for authentication.
        model: The GPT model to use. Defaults to "gpt-3.5-turbo".
        max_tokens: The maximum number of tokens to generate in the completion.
        temperature: A value controlling the randomness of the generated text.
        stop: If provided, the model will stop generating text when any of
            the strings in the list are encountered in the completion.
        presence_penalty: A value controlling how much the model favors
            words that were present in the input text.
        frequency_penalty: A value controlling how much the model favors
            rare words.

    """

    token: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = Field(lt=4048)
    temperature: float = Field(ge=0.0, le=2.0)
    stop: list[str] | str | None = Field(None, max_items=4)
    presence_penalty: float = Field(ge=-2.0, le=2.0)
    frequency_penalty: float = Field(ge=-2.0, le=2.0)


@dataclass
class ChatBot:
    """Chatbot configuration.

    Attrs:
        description: The chatbot description.
    """

    description: str = Field(max_length=250)


@dataclass
class Config:
    tg_bot: TelegramBot
    openai: OpenAI
    chatbot: ChatBot
    VOICES_DIRECTORY: str


def load_config() -> Config:
    # Parse a `.env` file and load the variables into environment valriables
    load_dotenv()

    # Common configuration
    BASE_DIR: str = Path(__file__).resolve().parent.parent

    # Telegram bot configuration
    tg_bot: TelegramBot = TelegramBot(
        token=get_env_variable("BOT_TOKEN"),
        debug_mode=get_env_variable("DEBUG") == "1",
    )

    # OpenAI configuration
    openai: OpenAI = OpenAI(
        token=get_env_variable("OPENAI_TOKEN"),
        temperature=get_env_variable("CHAT_TEMPERATURE", float),
        max_tokens=get_env_variable("CHAT_MAX_TOKENS", int),
        frequency_penalty=get_env_variable("CHAT_FREQUENCY_PENALTY", float),
        presence_penalty=get_env_variable("CHAT_PRESENCE_PENALTY", float),
    )

    chatbot: ChatBot = ChatBot(
        description=get_env_variable("CHATBOT_DESCRIPTION"),
    )

    VOICES_DIRECTORY: str = os.path.join(BASE_DIR, "voice_files")
    if not os.path.isdir(VOICES_DIRECTORY):
        os.mkdir(VOICES_DIRECTORY)

    return Config(
        tg_bot=tg_bot,
        openai=openai,
        chatbot=chatbot,
        VOICES_DIRECTORY=VOICES_DIRECTORY,
    )
