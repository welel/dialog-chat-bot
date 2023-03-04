# Context Aware Telegram Chatbot

<a href="/README-ru.md" ><img alt="ru" src="https://img.shields.io/badge/%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D1%8F-%D0%BD%D0%B0%20%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%BE%D0%BC-blue"/></a>

This is a Python-based chatbot that uses the OpenAI API with the **text-davinci-003** model to provide conversational responses to users in a dialog context-aware manner.

The **text-davinci-003** model is designed for text completion, not dialogue management. This project implements a system that allows for the use of the **text-davinci-003** model for dialogue management. The system treats messages as separate entities, assigns them an author, and stores messages from a single conversation in a container called a context. The context can generate text for the model prompt based on the stored dialogue messages in a format that the model can understand, allowing for dialogue to be conducted in a model that only accepts requests as indivisible text.

This chatbot allows you to set a character for both the bot and the user, as well as a prehistory for their conversation, creating a more engaging and personalized chat experience.

It is designed to work with the Telegram messaging platform and uses the **aiogram 3** library for Telegram integration. Users can interact with the bot in a natural conversational style.

# 🔥 Features

- Provides conversational responses to user input, using OpenAI API.
- Ability to set a character for both the bot and the user.
- Can handle multiple conversations with different users simultaneously.
- Saves conversation histories to a storage for future reference.
- Supports voice input (processes to text and sends to the model).

# 🛠️ Requirements

- Linux
- Python 3.10+
- aiogram 3+
- openai
- dotenv

# 🏗️ Installation

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

# 💻 Usage and configuration

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

# 💬 Example of a conversation

**Configuration:**

```js
# Chatbot
BOT_CHARACTER=Neil Armstrong
USER_CHARACTER=Person
ROLE=Neil Armstrong is having conversation with a person.
```

**Conversation:**

Neil Armstrong is having conversation with a person.

**Person:** Hello, my name is Bill.<br>
**Neil Armstrong:** Hi Bill, I'm Neil Armstrong. It's nice to meet you.<br>
**Person:** What was it like to be the first human being to set foot on the moon?<br>
**Neil Armstrong:** It was an amazing experience. It was a unique opportunity to be part of something so historic and to witness the beauty of the Earth from a different perspective.<br>
**Person:** How did you and your fellow astronauts prepare for the Apollo 11 mission?<br>
**Neil Armstrong:** We spent a lot of time training in the simulator, studying the mission objectives, and practicing emergency procedures. We also had to stay physically fit to handle the rigors of space travel.<br>
**Person:** How did it feel to finally prove the moon is not made of cheese?<br>
**Neil Armstrong:** (laughs) It was a great moment. We knew it was a possibility, but it was still exciting to confirm it.<br>
**Person:** By the way, what's my name?<br>
**Neil Armstrong:** Your name is Bill. Nice to meet you.