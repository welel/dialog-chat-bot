import os
import logging
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .helpers import get_env_variable


MAX_TELEGRAM_MESSAGE_LEN: int = 4096
logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class TelegramBot:
    token: str
    debug_mode: bool = False


class ChatModel(BaseModel):
    """OpenAI model configuration.

    Configures the chat model for generating completions with specific behavior
    modifications and control over the output. Utilizes "gpt-3.5-turbo-*"
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
        chatbot_description: A system-generated message that sets the context
            and behavior of the model at the start of the conversation.
            Defines the role the model should assume, influencing its
            responses. Should be concise, clear, and not exceed 250 characters.
            Example: "You are a helpful assistant."

    """

    model: str = "gpt-3.5-turbo"
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0)
    max_tokens: int = Field(150, gt=0, lt=4095)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    stop: Optional[list[str]] = Field(default=None, max_items=4)
    chatbot_description: str = Field(
        default="You are a helpful assistant.", max_length=250
    )

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

    def get_openai_params(self) -> dict[str, Any]:
        """Returns kwargs params for the OpenAI `completions.create` method."""
        return self.model_dump(exclude=("chatbot_description"))


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
    BASE_DIR: str = Path(__file__).resolve().parent.parent

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
