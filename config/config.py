from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

from errors.errors import ImproperlyConfigured, NoSuchResource


def get_env_variable(var_name: str, cast_to=str) -> str:
    """Get an environment variable or raise an exception.

    Args:
        var_name: a name of a environment variable.

    Returns:
        A value of the environment variable.

    Raises:
        ImproperlyConfigured: if the environment variable is not set.
    """
    try:
        return cast_to(os.environ[var_name])
    except KeyError:
        raise ImproperlyConfigured(var_name)
    except ValueError:
        raise ValueError("Bad environment variable casting.")


@dataclass
class Redis:
    location: str
    db_num: int


@dataclass
class ResourceManager:
    RESOURCES_PATH: str
    resources: dict[str, str]

    def get_path(self, resource_name: str) -> str:
        try:
            return os.path.join(
                self.RESOURCES_PATH, self.resources[resource_name]
            )
        except KeyError:
            raise NoSuchResource(resource_name)


@dataclass
class TelegramBot:
    token: str


@dataclass
class Config:
    tg_bot: TelegramBot
    resource_manager: ResourceManager
    redis: Redis


def load_config() -> Config:
    # Parse a `.env` file and load the variables into environment valriables
    load_dotenv()

    # Common configuration
    BASE_DIR: str = Path(__file__).resolve().parent.parent

    # Telegram bot configuration
    tg_bot: TelegramBot = TelegramBot(token=get_env_variable("BOT_TOKEN"))

    # Redis configuration
    redis: Redis = Redis(
        location=get_env_variable("REDIS_LOCATION"),
        db_num=get_env_variable("REDIS_DB_NUM", int),
    )

    # Resource manager configuration
    RESOURCES_PATH: str = os.path.join(BASE_DIR, "resources/")
    resources: dict[str, str] = ...
    resources_manager: ResourceManager = ResourceManager(
        RESOURCES_PATH=RESOURCES_PATH, resources=resources
    )

    return Config(
        tg_bot=tg_bot,
        redis=redis,
        resource_manager=resources_manager,
    )
