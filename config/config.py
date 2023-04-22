from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .helpers import get_env_variable


@dataclass
class TelegramBot:
    token: str


class OpenAI(BaseModel):
    """OpenAI client configuration.

    Uses the model - "text-davinci-003". More about parameters in docs.
    Docs: https://platform.openai.com/docs/api-reference/completions/create

    Attrs:
        token: The OpenAI API key to use for authentication.
        model: The GPT model to use. Defaults to "text-davinci-003".
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
    model: str = "text-davinci-003"
    max_tokens: int = Field(lt=4048)
    temperature: float = Field(ge=0.0, le=2.0)
    stop: list[str] | str | None = Field(None, max_items=4)
    presence_penalty: float = Field(ge=-2.0, le=2.0)
    frequency_penalty: float = Field(ge=-2.0, le=2.0)


@dataclass
class ChatBot:
    """Chatbot configuration.

    Attrs:
        bot_character: The character being played by the AI.
        user_character: The user name or character.
        role: the context of the conversation.
    """

    bot_character: str
    user_character: str
    role: str


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
    tg_bot: TelegramBot = TelegramBot(token=get_env_variable("BOT_TOKEN"))

    # OpenAI configuration
    openai: OpenAI = OpenAI(
        token=get_env_variable("OPENAI_TOKEN"),
        temperature=get_env_variable("TEMPERATURE", float),
        max_tokens=get_env_variable("MAX_TOKENS", int),
        frequency_penalty=get_env_variable("FREQUENCY_PENALTY", float),
        presence_penalty=get_env_variable("PRESENCE_PENALTY", float),
    )

    chatbot: ChatBot = ChatBot(
        bot_character=get_env_variable("BOT_CHARACTER"),
        user_character=get_env_variable("USER_CHARACTER"),
        role=get_env_variable("ROLE"),
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
