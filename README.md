# Context Aware Telegram Chatbot

This is a Python-based chatbot that uses the OpenAI API with the **text-davinci-003** model to provide conversational responses to users in a dialog context-aware manner. This chatbot allows you to set a character for both the bot and the user, as well as a prehistory for their conversation, creating a more engaging and personalized chat experience.

It is designed to work with the Telegram messaging platform and uses the **aiogram 3** library for Telegram integration. Users can interact with the bot in a natural conversational style.


# Features

- Provides conversational responses to user input, using OpenAI API.
- Ability to set a character for both the bot and the user.
- Supports customization of bot name and conversation context.
- Can handle multiple conversations with different users simultaneously.
- Saves conversation histories to a storage for future reference.

# Installation

- Clone or donwload the repository.

    ```
    git clone git@github.com:welel/dialog-chat-bot.git
    ```

- Checkout on **text-davinci-003** branch.

    ```
    git checkout text-davinci-003
    ```

- [Create virtual environment and activate it](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) and [install dependencies](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#using-requirements-files).

    ```
    python -m venv env
    source env/bin/activate
    ```

    ```
    pip install -r requirements/local.txt
    ```

- Copy/rename `.env.dist` to `.env` and fill it with data.

    ```
    cp .env.dist .env
    ```

    - Set up a Telegram bot and obtain a bot token (see https://medium.com/geekculture/generate-telegram-token-for-bot-api-d26faf9bf064 for instructions).

    - Set up an OpenAI account and obtain an [API key](https://platform.openai.com/account/api-keys) (see https://beta.openai.com/docs/quickstart for instructions).

- Run the bot.

    ```
    python bot.py
    ```

# Usage and configuration

- To start interact with the bot send any message to the telegram bot.

- To set a character and role for the bot and user user `.env` file.

    ```js
    # Chatbot
        # Max length = 50
    BOT_CHARACTER=Ilon Mask
        # Max length = 50
    USER_CHARACTER=Person
        # Max length = 200
    ROLE=Ilon Mask is having conversation with a Person.
    ```

    Set character name (role) for bot in a variable `BOT_CHARACTER` (for example: `Ilon Musk`, `Jonh Snow`, `King`, `Cat`...). Set character name for user the same way. And you can set a context for the conversation in a variable `ROLE` for exapmle: `Elon Musk passionately argues that there is life on Mars.`.

