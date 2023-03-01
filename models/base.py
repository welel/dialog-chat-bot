from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseOpenAIClient(ABC):
    @abstractmethod
    def complete(self, prompt: str, stop: str) -> str:
        raise NotImplementedError


class Bot(BaseModel):
    name: str
    role: str = ""


class User(BaseModel):
    user_id: int
    name: str


class Message(BaseModel):
    message_id: int
    author: User | Bot
    text: str

    def __len__(self) -> int:
        return len(self.author.name) + len(self.text) + 3


class Context(BaseModel):
    context_id: int
    user: User
    bot: Bot
    messages: list[Message] = list()
    max_length: int = 1900

    def _trim_messages(self) -> int:
        if not self.messages:
            return 0

        if len(self.messages[-1]) + len(self.bot.role) > self.max_length:
            trimed_num = len(self.messages) - 1
            self.messages = self.messages[-1:]
            wall = self.max_length + len(self.bot.role)
            self.messages[1].text = self.messages[1].text[:wall]
            return trimed_num

        length = len(self.bot.role)
        for i, message in enumerate(reversed(self.messages)):
            length += len(message)
            if length > self.max_length:
                wall = len(self.messages) - i
                self.messages = self.messages[wall:]
                return wall
        return 0

    def add_message(self, author: User | Bot, text: str) -> int:
        next_id = (
            0 if len(self.messages) == 0 else self.messages[-1].message_id + 1
        )
        self.messages.append(
            Message(message_id=next_id, author=author, text=text)
        )
        self._trim_messages()
        return next_id

    def _get_prompt(self) -> str:
        return (
            self.bot.role
            + "\n\n"
            + "\n".join(
                list(
                    map(
                        lambda msg: msg.author.name + ": " + msg.text,
                        self.messages,
                    )
                )
            )
            + "\n"
            + self.bot.name
            + ":"
        )

    def get_answer(self, openai_client: BaseOpenAIClient) -> Message:
        prompt = self._get_prompt()
        stop_word = self.user.name + ":"
        answer_text = openai_client.complete(prompt, stop_word)
        self.add_message(self.bot, answer_text)
        return self.messages[-1]


class DialogStorage(ABC):
    @abstractmethod
    def add_context(self, context: Context) -> int:
        """Adds a context to the storage and returns context id."""
        raise NotImplementedError

    @abstractmethod
    def get_context(self, context_id) -> Context:
        """Gets a context from the storage and returns it."""
        raise NotImplementedError


class BaseDialogManager(ABC):
    @abstractmethod
    def add_context(self, context: Context) -> int:
        """Adds new context to the manager, returns context id."""
        raise NotImplementedError

    @abstractmethod
    def chat(self, context_id: int, text: str) -> Message:
        """Gets answer from Open AI chatbot on `text` prompt."""
        raise NotImplementedError


class DialogManager(BaseDialogManager):
    def __init__(
        self, openai_client: BaseOpenAIClient, dialog_storage: DialogStorage
    ):
        self.openai_client = openai_client
        self.dialog_storage = dialog_storage

    def add_context(self, context: Context) -> int:
        self.dialog_storage.add_context(context)

    def chat(self, context_id: int, text: str) -> Message:
        """Gets answer from Open AI chatbot on `text` prompt."""
        context = self.dialog_storage.get_context(context_id)
        context.add_message(author=context.user, text=text)
        return context.get_answer(self.openai_client)
