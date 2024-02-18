import enum
import random


class SystemMessage(str, enum.Enum):
    NO_BOTHER = "no_bother"
    NO_INPUT = "no_input"
    UNINTELLIGIBLE_VOICE_INPUT = "unintelligible_voice_input"


MESSAGES: dict[SystemMessage, list[str]] = {
    SystemMessage.NO_BOTHER: [
        "Today, I'm not in the mood for chatting. Please, don't bother me!",
        "Today, I don't feel like sharing anything. Leave me be!",
        "Today, nothing pleases me. I'm not listening to anyone!",
        "Speed, speed - that's my philosophy! No lessons, no listening!",
        "I'm occupied with my thoughts! Nobody should disturb me!",
        "I am free! When I don't want to respond, I won't!",
    ],
    SystemMessage.NO_INPUT: [
        "You need to say something, or we can't continue our conversation.",
        "You need to input something, otherwise, there can be no dialogue.",
        "You need to say something, or the chat can't be given attention.",
        "You need to say something to keep the conversation going.",
        "You have to say at least something.",
    ],
    SystemMessage.UNINTELLIGIBLE_VOICE_INPUT: [
        "I couldn't understand what was said. "
        "Could you please repeat that and speak a bit more clearly?",
        "It seems like your message didn't come through clearly. "
        "Please try again and speak clearly.",
        "I'm having trouble understanding your voice message. "
        "Could you repeat it more clearly, please?",
        "Your message was not clear to me. Please say it again, "
        "speaking clearly.",
        "Sorry, I couldn't catch that. Could you speak more clearly "
        "and try sending your message again?",
    ],
}


def get_message(message_type: SystemMessage) -> str:
    """Returns a random message from the `MESSAGES` dictionary.

    Args:
        message_type: The key of the `MESSAGES` dictionary (gets a messages
            list).

    Returns:
        str: A random message from the `MESSAGES` dictionary corresponding to
             the given key. If a key or messages don't exists, returns "".
    """
    messages = MESSAGES.get(message_type, [""])
    message_index = random.randint(0, len(messages) - 1)
    return messages[message_index]
