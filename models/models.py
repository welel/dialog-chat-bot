from config import ChatBot, load_config, OpenAI
from services.chatbot import complete as complete_text

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

    def complete(self, prompt: str, stop: str):
        print(prompt)
        return complete_text(
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

    def add_context(self, context: Context) -> int:
        """Adds a context to the storage and returns context id."""
        self.contexts[context.context_id] = context
        return context.context_id

    def get_context(self, context_id) -> Context:
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

    def chat(self, context_id: int, text: str) -> Message:
        if self.dialog_storage.is_context(context_id):
            return super().chat(context_id, text)
        else:
            user = User(user_id=context_id, name=self.config.user_character)
            bot = Bot(
                name=self.config.bot_character,
                role=self.config.role,
            )
            context = Context(context_id=context_id, user=user, bot=bot)
            self.add_context(context)
            return super().chat(context_id, text)
