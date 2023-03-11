from config import ChatBot, load_config, OpenAI
from services.openai_api import complete as complete_text

from .base import (
    BaseOpenAIClient,
    Bot,
    Context,
    DialogStorage,
    DialogManager,
    Message,
    User,
)


class ContextDoesNotExist(Exception):
    """Raises when a context is missing in a storage."""

    pass


class OpenAIClient(BaseOpenAIClient):
    config: OpenAI = load_config().openai

    async def complete(self, prompt: str, stop: str):
        print(prompt)
        return await complete_text(
            prompt,
            stop,
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            frequency_penalty=self.config.frequency_penalty,
            presence_penalty=self.config.presence_penalty,
        )


class DictDialogStorage(DialogStorage):
    """Dialog Storage that stores context in Python dict."""

    contexts: dict[int, Context] = dict()

    async def add_context(self, context: Context) -> int:
        """Adds a context to the storage and returns context id."""
        self.contexts[context.context_id] = context
        return context.context_id

    async def get_context(self, context_id) -> Context:
        """Gets a context from the storage and returns it."""
        try:
            return self.contexts[context_id]
        except KeyError:
            raise ContextDoesNotExist(
                f"Context with id {context_id} doesn't exist."
            )

    def is_context(self, context_id: int) -> bool:
        return context_id in self.contexts


class TelegramDialogManager(DialogManager):
    config: ChatBot = load_config().chatbot

    async def chat(self, user_id: int, text: str) -> Message:
        """Gets answer from Open AI chatbot on `text` prompt.

        Uses the telegram user id as a context identifier.
        """
        if self.dialog_storage.is_context(user_id):
            return await super().chat(user_id, text)
        else:
            user = User(user_id=user_id, name=self.config.user_character)
            bot = Bot(name=self.config.bot_character, role=self.config.role)
            context = Context(context_id=user_id, user=user, bot=bot)
            await self.add_context(context)
            return await super().chat(user_id, text)
