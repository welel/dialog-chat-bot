from config import ChatBot, load_config
from config.config import MAX_TELEGRAM_MESSAGE_LEN

from .base import DialogStorage, DialogManager, Chat


class ChatDoesNotExist(Exception):
    """Raises when a chat is missing in a storage."""

    pass


class DictDialogStorage(DialogStorage):
    """Dialog Storage that stores context in Python dict."""

    chats: dict[int, Chat] = dict()

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

    def is_chat(self, user_id: int, chat_id: int) -> bool:
        return (user_id, chat_id) in self.chats


class TelegramDialogManager(DialogManager):
    config: ChatBot = load_config().chatbot
    dialog_storage: DictDialogStorage

    async def chat(self, user_id: int, chat_id: int, text: str) -> str:
        """Gets answer from Open AI chatbot on `text` prompt.

        Uses the telegram user_id, chat_id as a chat identifier.
        """
        if self.dialog_storage.is_chat(user_id, chat_id):
            answer = await super().chat(user_id, chat_id, text)
        else:
            chat = Chat(user_id=user_id, chat_id=chat_id)
            await self.add_chat(chat)
            answer = await super().chat(user_id, chat_id, text)
        return answer[:MAX_TELEGRAM_MESSAGE_LEN - 1]
