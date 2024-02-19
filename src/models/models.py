import logging
import uuid

from aiogram import Bot
from aiogram.types import BufferedInputFile, Message as TgMessage
import tiktoken

from src.config import configs
from src.config.config import MAX_TELEGRAM_MESSAGE_LEN
from src.errors.errors import ChatDoesNotExist, EmptyTrancriptionResult
from src.services.audio import save_voice_as_mp3
from src.services.openai_api import complete, text_to_speech, speech_to_text

from .base import BaseChat, DialogStorage, Role, Message


chat_model = configs.chat_model
encoder = tiktoken.encoding_for_model(chat_model.chat_model.model)
logger = logging.getLogger(__name__)


class Chat(BaseChat):
    """Chat of one user and a chatbot.

    Chat manages the messages history and makes request to OpenAI.

    """

    max_context_window: int = chat_model.chatbot.max_context_len
    """Maxinum context window in tokens.

    Old messages that exceed this windows will be removed.
    """

    def add_message(self, text: str, role: Role = Role.USER):
        """Add a message to the chat.

        Args:
            text: The text of the message.
            role: OpenAI chat role.
        """
        self.messages.append(Message(content=text, role=role))
        self._trim_context()

    def model_post_init(self, __context) -> None:
        """Initializes the context with the chatbot description."""
        self.add_message(chat_model.chatbot.description, Role.SYSTEM)

    @classmethod
    def _get_message_tokens_num(cls, message: Message) -> int:
        """Returns the number of tokens in a message."""
        message_as_str = f"{message.content}{message.role}"
        # Every reply is primed with <|start|>role<|message|>, so add 3 tokens.
        return len(encoder.encode(message_as_str)) + 3

    def _trim_context(self):
        """Deletes messages if tokens sum exedess `max_context_window`.

        Trims the messages in the context to meet the maximum length specified
        in the context. If the length of the context exceeds the maximum
        length, it removes the oldest messages from the context until it
        meets the length criteria. If last messages if above of the window
        then trim these messages.
        """
        if not self.messages:
            return

        system_message = self.messages.pop(0)
        tokens = self._get_message_tokens_num(system_message)

        for i, message in enumerate(reversed(self.messages)):
            tokens += self._get_message_tokens_num(message)
            if tokens >= self.max_context_window:
                wall = len(self.messages) - i
                self.messages = self.messages[wall:]

        self.messages.insert(0, system_message)

    async def _generate_bot_answer(self) -> str:
        """Generates a prompt with using context and history messages.

        Gets bot answer, adds to the `messages`.

        Returns:
            A string response from the model.
        """
        answer = await complete(self.messages, chat_model)
        self.add_message(answer, Role.ASSISTANT)
        return answer

    async def get_answer(self, text: str) -> str:
        """Requests OpenAI for an answer and returns it.

        Generates a message from the OpenAI API in response to the current
        conversation context.

        Args:
            text: User message text to answer.

        Returns:
            OpenAI chat model answer.
        """
        self.add_message(text, Role.USER)
        answer = await self._generate_bot_answer()
        logger.debug("Chat state: %s", self)
        return answer

    async def get_audio_answer(self, text: str) -> bytes:
        """Requests OpenAI for an answer and returns it as audio bytes."""
        answer = await self.get_answer(text)
        return await text_to_speech(answer, chat_model)

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
        """Checks wheather the chat exists in the storage."""
        return (user_id, chat_id) in self.chats


class DialogManager:
    """Manages `Chat` and `DialogStorage` together."""

    def __init__(self, dialog_storage: DialogStorage):
        self.dialog_storage: DialogStorage = dialog_storage

    async def add_chat(self, chat: Chat):
        """Adds a chat to the manager's storage."""
        await self.dialog_storage.add_chat(chat)

    async def get_chat(self, user_id: int, chat_id: int) -> Chat:
        """Gets a chat from the manager's storage and returns it."""
        return await self.dialog_storage.get_chat(user_id, chat_id)


class TelegramDialogManager(DialogManager):
    """Manages `Chat` and `DialogStorage` together for telegram replies."""

    dialog_storage: DictDialogStorage

    async def get_or_create_chat(self, user_id: int, chat_id: int) -> Chat:
        """Gets a chat from the manager's storage (creates if don't exists)."""
        if self.dialog_storage.is_chat_exists(user_id, chat_id):
            chat = await super().get_chat(user_id, chat_id)
        else:
            chat = Chat(user_id=user_id, chat_id=chat_id)
            await self.add_chat(chat)
        return chat

    async def reply_on_text(
            self, message: TgMessage, text: str | None = None
    ) -> None:
        """"Sends chat model's answer by given telegram message.

        Args:
            message: A telegram message.
            text: Prompt text to use. If None use text from the given message.
        """
        message_text = text or message.text
        chat = await self.get_or_create_chat(
            message.from_user.id, message.chat.id
        )

        if chat_model.is_voice_mode:
            response = await chat.get_audio_answer(message_text)
            voice_file = BufferedInputFile(
                response, filename=f"{uuid.uuid4}.mp3"
            )
            await message.answer_voice(voice_file)
        else:
            answer = await chat.get_answer(message_text)
            answer = answer[:MAX_TELEGRAM_MESSAGE_LEN]
            await message.reply(text=answer)

    async def reply_on_voice(self, message: TgMessage, bot: Bot) -> None:
        """"Sends chat model's answer by given telegram voice message.

        Args:
            message: A telegram message.
            bot: Current telegram bot.

        Raises:
            EmptyTrancriptionResult: OpenAI transciption got empty result.
        """
        voice_path = await save_voice_as_mp3(bot, message.voice)
        if transcripted_voice_text := await speech_to_text(voice_path):
            await self.reply_on_text(message, text=transcripted_voice_text)
        else:
            raise EmptyTrancriptionResult
