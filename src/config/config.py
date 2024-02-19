import os
import logging
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .helpers import get_env_variable


MAX_TELEGRAM_MESSAGE_LEN: int = 4096
logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class TelegramBot:
    token: str
    debug_mode: bool = False


class ModelConfig(BaseModel):
    """Configuration for the GPT model used in chat completions.

    This class specifies the parameters to customize the behavior of the
    GPT model for generating responses in a chat. Utilizes "gpt-3.5-turbo-*"
    for generating chat completions. More about parameters can be found
    in the docs: https://platform.openai.com/docs/api-reference/chat/create

    Attributes:
        model: The GPT model ID to use for chat completions.
        frequency_penalty: Adjusts the likelihood of generating new tokens
            based on their frequency in the text so far.
        presence_penalty: Adjusts the likelihood of generating new tokens
            based on their presence in the text so far.
        max_tokens: Limits the maximum number of tokens in the model's
            response to control the output length.
        temperature: Controls the randomness of the output.
        top_p: Controls output by only considering the top P% probability
            mass of the token distribution.
        stop: A list of strings where the model will stop generating further
            tokens. Useful for ending responses or avoiding certain topics.

    """
    model: Literal[
        "gpt-3.5-turbo-16k-0613",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-1106 ",
    ] = "gpt-3.5-turbo"
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    max_tokens: int = Field(150, gt=0, lt=4095)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    stop: Optional[list[str]] = Field(default=None, max_items=4)


class VoiceConfig(BaseModel):
    """Configuration for the voice synthesis model.

    Specifies the text-to-speech (TTS) model and voice settings for generating
    audio responses.

    Attributes:
        model: The TTS model to use. Choices are "tts-1" and "tts-1-hd".
        voice: The voice ID for the audio generation.
        speed: The speed of the voice playback.
            Range: [0.25, 4.0], where 1.0 is the default speed.
    """
    model: Literal["tts-1", "tts-1-hd"] = "tts-1"
    voice: Literal[
        "alloy", "echo", "fable", "onyx", "nova", "shimmer"
    ] = "alloy"
    speed: float = Field(1.0, ge=0.25, le=4.0)


class ChatbotConfig(BaseModel):
    """Configuration for the chatbot's behavior and context.

    Attributes:
        description: A system-generated message that sets the context
            and behavior of the model at the start of the conversation.
            Defines the role the model should assume, influencing its
            responses. Should be concise, clear, and not exceed 250 characters.
            Example: "You are a helpful assistant."
        max_context_len: Max context window in tokens.

    """
    description: str = Field(
        default="You are a helpful assistant.", max_length=250
    )
    max_context_len: int = Field(3500, gt=0, lt=16385)


class ChatModel(BaseModel):
    """Overall configuration for the chat model.

    Including chat completions, voice synthesis, and chatbot behavior.
    Combines settings for generating text responses, voice output,
    and managing chat context.

    Attributes:
        chat_model: Configuration for the GPT model used in chat completions.
        chatbot: Settings for the chatbot's behavior and context.
        voice: Optional configuration for voice synthesis. If provided,
            enables voice output.

    """

    chat_model: ModelConfig
    chatbot: ChatbotConfig = Field(default_factory=ChatbotConfig)
    voice: Optional[VoiceConfig] = None

    @classmethod
    def load_from_yaml_file(
            cls, file_path: str, model_name: str
    ) -> "ChatModel":
        """Create an chat model instance based on data in the config file.

        Args:
            file_path: YAML file with models configurations.
            model_name: The model name to load.

        Returns:
            Loaded `ChatModel` instance.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"The model configuration file isn't found by {file_path}."
            )
        with open(file_path, "r") as file:
            model_configs = yaml.safe_load(file).get('models', {})
            if not (model_config := model_configs.get(model_name, {})):
                logger.warning(
                    "The model configuration '%s' isn't found. "
                    "Load default model.",
                    model_name,
                )
            return cls(**model_config)

    def get_openai_chat_params(self) -> dict[str, Any]:
        """Returns kwargs params for the OpenAI `completions.create` method."""
        return self.chat_model.model_dump()

    def get_openai_speech_params(self) -> dict[str, str | float]:
        """Returns kwargs params for the OpenAI `speech.create` method."""
        return self.voice.model_dump()

    @property
    def is_voice_mode(self) -> bool:
        return isinstance(self.voice, VoiceConfig)


@dataclass
class Config:
    tg_bot: TelegramBot
    chat_model: ChatModel
    VOICES_DIRECTORY: str
    OPENAI_TOKEN: str


def load_config() -> Config:
    # Parse a `.env` file and load the variables into environment valriables.
    load_dotenv()

    # Common configuration
    BASE_DIR: str = Path(__file__).resolve().parent.parent.parent

    # Telegram bot configuration
    tg_bot: TelegramBot = TelegramBot(
        token=get_env_variable("BOT_TOKEN"),
        debug_mode=get_env_variable("DEBUG") == "1",
    )

    # OpenAI model configuration
    MODEL_CONFIG_PATH = os.path.join(
        BASE_DIR, (get_env_variable("MODEL_CONFIG_PATH"))
    )
    MODEL_CONFIG_NAME = get_env_variable("MODEL_CONFIG_NAME")
    chat_model: ChatModel = ChatModel.load_from_yaml_file(
        MODEL_CONFIG_PATH, MODEL_CONFIG_NAME
    )
    logger.info("The chat model loaded: %s", chat_model)

    VOICES_DIRECTORY: str = os.path.join(BASE_DIR, "temp")
    if not os.path.isdir(VOICES_DIRECTORY):
        os.mkdir(VOICES_DIRECTORY)

    return Config(
        tg_bot=tg_bot,
        chat_model=chat_model,
        VOICES_DIRECTORY=VOICES_DIRECTORY,
        OPENAI_TOKEN=get_env_variable("OPENAI_TOKEN"),
    )
