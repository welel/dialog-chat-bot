import random as rand

import openai

from config import load_config


openai.api_key = load_config().openai.token

MESSAGES = {
    "nobother": [
        "Сегодня я не в настроении болтать. Пожалуйста, не раздражайте меня!",
        "Сегодня я не хочу ничего рассказывать. Не трогайте меня!",
        "Сегодня я ничему не рад. Никого не слушаю!",
        "Скорость, скорость - это моя философия! Никому ничему!",
        "Я - занят своими думами! Нельзя, чтобы кто-нибудь мешал мне!",
        "Я - свободный! Когда не хочу отвечать - не отвечаю!",
    ],
    "noinput": [
        "Ты должен что-то сказать, иначе мы не сможем продолжить разговор.",
        "Ты должен что-то ввести, иначе разговор не случится.",
        "Ты должен что-то сказать, иначе разговору нельзя будет уделить внимания.",
        "Ты должен что-то сказать, чтобы развивался разговор.",
        "Ты должен хоть что-нибудь сказать.",
    ],
}


def get_message(messages_key: str) -> str:
    """Returns a random message from the `MESSAGES` dictionary.

    Args:
        messages_key: The key of the MESSAGES dictionary (gets a messages list).

    Returns:
        str: A random message from the MESSAGES dictionary corresponding to
             the given key.

    Raises:
        KeyError: If the given key is not present in the MESSAGES dictionary.
    """
    msg_index = rand.randint(0, len(MESSAGES[messages_key]) - 1)
    return MESSAGES[messages_key][msg_index]


def complete(
    prompt: str,
    stop: str,
) -> str:
    if not prompt:
        return get_message("noinput")

    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=2048,
            top_p=0.8,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=stop,
        )
    except Exception as error:
        print(error)
        return get_message("nobother")
    return response["choices"][0]["text"].strip()
