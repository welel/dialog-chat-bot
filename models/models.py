import logging

import tiktoken

from config import configs
from config.config import MAX_TELEGRAM_MESSAGE_LEN
from errors.errors import ChatDoesNotExist
from services.openai_api import complete

from .base import BaseChat, BaseDialogManager, DialogStorage, Role, Message


chat_model = configs.chat_model
encoder = tiktoken.encoding_for_model(chat_model.model)
logger = logging.getLogger(__name__)


class Chat(BaseChat):
    """Chat of one user and a chatbot.

    Chat manages the messages history and makes request to OpenAI.

    """
    max_tokens: int = chat_model.max_tokens

    def add_message(self, text: str, role: Role = Role.USER):
        """Add a message to the chat.

        Args:
            text: The text of the message.
            role: OpenAI chat role.
        """
        message = Message(content=text, role=role)
        self.messages.append(message)
        self._trim_context()

    def model_post_init(self, __context) -> None:
        """Initializes the context with the chatbot description."""
        self.add_message(chat_model.chatbot_description, Role.SYSTEM)

    @classmethod
    def _get_message_tokens_num(cls, message: Message) -> int:
        """Returns the number of tokens in a message."""
        message_as_str = f"{message.content}{message.role}"
        tokens = len(encoder.encode(message_as_str))
        tokens += 3  # Every reply is primed with <|start|>role<|message|>
        return tokens

    def _trim_context(self):
        """Deletes messages if tokens sum exedess `max_tokens`.

        Trims the messages in the context to meet the maximum length specified
        in the context. If the length of the context exceeds the maximum
        length, it removes the oldest messages from the context until it
        meets the length criteria. If last message if above of `max_tokens`
        then trim this message.
        """
        if not self.messages:
            return

        system_message = self.messages.pop(0)
        tokens = self._get_message_tokens_num(system_message)

        for i, message in enumerate(reversed(self.messages)):
            tokens += self._get_message_tokens_num(message)
            if tokens >= self.max_tokens:
                wall = len(self.messages) - i
                self.messages = self.messages[wall:]

        self.messages.insert(0, system_message)

    async def _get_prompt(self):
        """Generates a prompt with using context and history messages.

        Gets bot answer, adds to the `messages`.

        Returns:
            A string representing the prompt message for the current context.
        """
        answer = await complete(self.messages, chat_model)
        self.add_message(answer, Role.ASSISTANT)

    async def get_answer(self, text: str) -> str:
        """Requests OpenAI for an answer and add the answer to the `text`.

        Generates a message from the OpenAI API in response to the current
        conversation context.

        Args:
            text: User message text to answer.

        Returns:
            OpenAI chat answer.
        """
        self.add_message(text, Role.USER)
        await self._get_prompt()
        logger.debug("Chat state: %s", self)
        return self.messages[-1].content

    def __len__(self) -> int:
        """Chat length in tokens."""
        if not self.messages:
            return 0

        tokens = 0
        for message in self.messages:
            tokens += self._get_message_tokens_num(message)
        return tokens


class DictDialogStorage(DialogStorage):
    """Dialog Storage that stores context in Python dict."""

    chats: dict[tuple[int, int], Chat] = dict()

    async def add_chat(self, chat: Chat):
        """Adds a chat to the storage."""
        self.chats[(chat.user_id, chat.chat_id)] = chat

    async def get_chat(self, user_id: int, chat_id: int) -> Chat:
        """Gets a chat from the storage and returns it."""
        try:
            return self.chats[(user_id, chat_id)]
        except KeyError:
            raise ChatDoesNotExist(
                f"Chat for {(user_id, chat_id)} doesn't exist.",
            )

    def is_chat_exists(self, user_id: int, chat_id: int) -> bool:
        return (user_id, chat_id) in self.chats


class DialogManager(BaseDialogManager):

    def __init__(self, dialog_storage: DialogStorage):
        self.dialog_storage: DialogStorage = dialog_storage

    async def add_chat(self, chat: Chat):
        await self.dialog_storage.add_chat(chat)

    async def chat(self, user_id: int, chat_id: int, text: str) -> str:
        """Gets answer from Open AI chatbot on `text` prompt."""
        chat = await self.dialog_storage.get_chat(user_id, chat_id)
        return await chat.get_answer(text)


class TelegramDialogManager(DialogManager):
    dialog_storage: DictDialogStorage

    async def chat(self, user_id: int, chat_id: int, text: str) -> str:
        """Gets answer from Open AI chatbot on `text` prompt.

        Uses the telegram user_id, chat_id as a chat identifier.
        """
        if self.dialog_storage.is_chat_exists(user_id, chat_id):
            answer = await super().chat(user_id, chat_id, text)
        else:
            chat = Chat(user_id=user_id, chat_id=chat_id)
            await self.add_chat(chat)
            answer = await super().chat(user_id, chat_id, text)
        return answer[:MAX_TELEGRAM_MESSAGE_LEN - 1]
