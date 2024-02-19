from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class Message(BaseModel):
    content: str
    role: Role


class BaseChat(BaseModel):
    """Chat of one user and a chatbot.

    Attrs:
        user_id: Telegram user ID.
        chat_id: Telegram chat ID.
        messages: A list of Message objects representing the conversation
            history.
        max_tokens: An integer representing the maximum number of tokens
            allowed in sum of all messages.
    """

    user_id: int
    chat_id: int
    messages: list[Message] = Field(default_factory=list)
    max_tokens: int = 150


class DialogStorage(ABC):
    """Dialog Storage Interface for storing `Chat` objects.

    This is an abstract base class for a Dialog Storage, which defines
    the interface that a concrete Dialog Storage class must implement.
    The Dialog Storage is responsible for storing and retrieving
    conversation contexts (chats).
    """

    @abstractmethod
    async def add_chat(self, chat: BaseChat):
        """Adds a context to the storage and returns context id."""
        raise NotImplementedError

    @abstractmethod
    async def get_chat(self, user_id: int, chat_id: int) -> BaseChat:
        """Gets a context from the storage and returns it."""
        raise NotImplementedError
