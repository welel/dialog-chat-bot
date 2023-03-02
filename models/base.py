from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class BaseOpenAIClient(ABC):
    """Open AI interface that provides requests to OpenAI"""

    @abstractmethod
    def complete(self, prompt: str, stop: str) -> str:
        """Takes prompt and stop words and returns compelation."""
        raise NotImplementedError


class Bot(BaseModel):
    """Bot character that a OpenAI model represents.

    Attrs:
        name: A bot's name.
        role: A context of conversation.
    """

    name: str = Field(..., max_length=50)
    role: str = Field("", max_length=200)


class User(BaseModel):
    """User character."""

    user_id: int
    name: str = Field(..., max_length=50)


class Message(BaseModel):
    message_id: int
    author: User | Bot
    text: str = Field(..., max_length=1995)

    def __len__(self) -> int:
        """Length of a message: text + author name + sequence ' : '."""
        return len(self.author.name) + len(self.text) + 3


class Context(BaseModel):
    """Dialog context of one user and a bot.

    Context keeps the messages history. If length of all messages exceeds
    `max_length` context trims (deletes) oldest messages to keep sum length
    less than `max_length`.

    Attrs:
        context_id: An integer representing the unique ID of the conversation.
        user: A User object representing the user participating
            in the conversation.
        bot: A Bot object representing the bot participating
            in the conversation.
        messages: A list of Message objects representing
            the conversation history.
        max_length: An integer representing the maximum number of characters
            allowed in sum of all messages.
    """

    context_id: int
    user: User
    bot: Bot
    messages: list[Message] = list()
    max_length: int = Field(1900, gt=300, lt=2048)

    def _trim_context(self) -> int:
        """Deletes messages if sum length exedess `max_length`.

        Trims the messages in the context to meet the maximum length specified
        in the context. If the length of the context exceeds the maximum
        length, it removes the oldest messages from the context until it
        meets the length criteria.
        """
        if not self.messages:
            return 0

        length = len(self.bot.role)
        for i, message in enumerate(reversed(self.messages)):
            length += len(message)
            if length > self.max_length:
                wall = len(self.messages) - i
                self.messages = self.messages[wall:]
                return wall
        return 0

    def _next_message_id(self) -> int:
        """Returns the next message ID.

        Returns:
            The next message ID, which is the message ID of the last message in
            the context plus 1, or 0 if the context has no messages yet.
        """
        return (
            0 if len(self.messages) == 0 else self.messages[-1].message_id + 1
        )

    def _trim_message(self, message: Message):
        """Trims long messages to the valid length.

        Takes a Message object as input and returns the modified message
        object with truncated text if the length of the message exceeds
        the `max_length` parameter of the ``Context`` object.

        Args:
            message: A Message object that contains the text message
                to be trimmed.

        Returns:
            The modified Message object.
        """
        if len(message) > self.max_length:
            message.text = message.text[: self.max_length - 250]
        return message

    def add_message(self, author: User | Bot, text: str) -> int:
        """Add a message to the context with the given author and text.

        Args:
            author: The author of the message.
            text: The text of the message.

        Returns:
            The ID of the new message.
        """
        message = Message(
            message_id=self._next_message_id(), author=author, text=text
        )
        message = self._trim_message(message)
        self.messages.append(message)
        self._trim_context()
        return message.message_id

    def _get_prompt(self) -> str:
        """Generates a prompt with using context and history messages.

        Returns the prompt message based on the context history. The prompt
        message is a string that includes the bot's role, dialog history
        (previous messages).

        Returns:
            A string representing the prompt message for the current context.
        """
        prompt_template = "{role}\n\n{dialog}\n{bot_name}: "
        dialog = list(
            map(lambda msg: msg.author.name + ": " + msg.text, self.messages)
        )
        return prompt_template.format(
            role=self.bot.role,
            dialog="\n".join(dialog),
            bot_name=self.bot.name,
        )

    def get_answer(self, openai_client: BaseOpenAIClient) -> Message:
        """Requests OpenAI for an answer and add the answer to the `messages`.

        Generates a message from the OpenAI API in response to the current
        conversation context. The method takes an instance of an
        openai.BaseOpenAIClient subclass as an argument and returns
        a Message object.

        Args:
            openai_client: An instance of an openai.BaseOpenAIClient subclass
                that is used to generate a response to the current conversation
                context.

        Returns:
            A Message object that represents the response generated by
            the OpenAI API.
        """
        prompt = self._get_prompt()
        stop_word = self.user.name + ":"
        answer_text = openai_client.complete(prompt, stop_word)
        self.add_message(self.bot, answer_text)
        return self.messages[-1]


class DialogStorage(ABC):
    """Dialog Storage Interface for storing `Context` objects.

    This is an abstract base class for a Dialog Storage, which defines
    the interface that a concrete Dialog Storage class must implement.
    The Dialog Storage is responsible for storing and retrieving
    conversation contexts.
    """

    @abstractmethod
    def add_context(self, context: Context) -> int:
        """Adds a context to the storage and returns context id."""
        raise NotImplementedError

    @abstractmethod
    def get_context(self, context_id) -> Context:
        """Gets a context from the storage and returns it."""
        raise NotImplementedError


class BaseDialogManager(ABC):
    """Dialog Manager Interface for making requests to OpenAI.

    This is an abstract class that defines the interface for a Dialog Manager
    that interacts with an Open AI chatbot.
    """

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
