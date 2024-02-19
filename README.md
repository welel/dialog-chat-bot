
# OpenAI Telegram Chatbot

This is a Python-based Telegram chatbot that uses the OpenAI API with **gpt-3.5-turbo-\*** models to provide conversational responses to users in a dialog context-aware manner.

You can easily configure the parameters of OpenAI models for the chatbot by using the `models.yml` file. This approach allows for quick adjustments of model settings such as `temperature`, `max_tokens`, `voice` and so on without altering the code. Simply edit the `models.yml` file to change the behavior and response style of your chatbot as needed.

# 🔥 Features

- Provides conversational responses to user input, using OpenAI API.
- Ability to easily configure multiple models and choose between them.
- Supports voice input (processes speech to text using OpenAI Whisper model).
- Supports voice output (processes texts to peech using OpenAI TTS model).
- Can handle multiple conversations with different users simultaneously.

# 🛠️ Requirements

- Python 3.11+
- ffmpeg
- OpenAI account and positive account balance. New users get $5.

# 🏃 Quick Start

1. **Install the Bot**: Choose between a local installation or using Docker. See the Installation section for detailed steps.
2. **Interact with Your Bot**: Once the bot is up and running, open Telegram and start sending messages to your bot's Telegram handle.

# 🏗️ Installation

## Local

- Clone or download the repository.

    ```
    git clone git@github.com:welel/dialog-chat-bot.git
    ```

- Checkout on **gpt-3.5-turbo** branch.

    ```
    git checkout gpt-3.5-turbo
    ```

- [Create virtual environment and activate it](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) and [install dependencies](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#using-requirements-files).

    ```
    python -m venv env
    source env/bin/activate
    pip install --upgrade pip && pip install -r requirements.txt
    ```

- To use voice messages, please install [ffmpeg](https://ffmpeg.org/).

	```
	# on Ubuntu or Debian
	sudo apt update && sudo apt install ffmpeg
	
	# on Arch Linux
	sudo pacman -S ffmpeg
	
	# on MacOS using Homebrew (https://brew.sh/)
	brew install ffmpeg
	
	# on Windows using Chocolatey (https://chocolatey.org/)
	choco install ffmpeg
	
	# on Windows using Scoop (https://scoop.sh/)
	scoop install ffmpeg
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

## Docker

- Install Docker and Docker Compose ([link](https://medium.com/@pavel.loginov.dev/how-to-easily-install-docker-and-compose-on-ubuntu-5423e8a64259) if you don’t know how).

- Copy/rename `.env.dist` to `.env` and fill it with data.

    ```
    cp .env.dist .env
    ```

- Now simply build the image and run it with docker compose:

```
docker compose build
docker compose up -d
```

# 💻 Usage and configuration

To start interact with the bot send any message to the telegram bot.

The chatbot uses configurations specified in the `models.yml` file to tailor its responses. This file allows for detailed customization of the OpenAI model parameters, offering flexibility to adjust the bot's behavior according to different needs or contexts.

### Configuring Models with `models.yml`

The `models.yml` file in the project directory contains configurations for different models or scenarios. Here's how to configure it:

1. **Selecting a Model**: Under the `models` key, you can define multiple configurations. 

    Each configuration can specify a different OpenAI model. For example, the `default` configuration uses `gpt-3.5-turbo` with a `max_tokens` limit of 100. You need to set a model config name in the environment variable `MODEL_CONFIG_NAME` to select the config.
        
2. **Configuring OpenAI chat model (`chat_model` section)**:
    
    - **Model ID**: Choose the appropriate model ID for your use case. Available options include various versions of the `gpt-3.5-turbo` model, each with different capabilities and context window sizes.
    - **Max Tokens**: This required setting controls the output length by limiting the maximum number of tokens the model generates.
    - **Frequency Penalty**: Adjust how new tokens are generated based on their frequency so far. Positive values reduce repetition.
    - **Presence Penalty**: Influence the generation of new tokens based on their presence in the conversation, promoting diversity in topics.
    - **Temperature**: Control the randomness of responses. Lower values result in more predictable text, while higher values increase diversity.
    - **Top P**: An alternative to temperature, focusing the model on the most probable tokens or a broader set, depending on the value.
    - **Stop**: Define specific sequences that signal the model to stop generating further tokens, useful for managing the flow of conversation.

3. **Configuring chatbot behaviour (`chatbot` section)**:

    - **Description**: Set a context or role for the chatbot at the beginning of the conversation, guiding its responses and style.
	- **Length**: The `max_context_len` parameter defines the total number of tokens (user inputs and bot responses) considered in a single conversation window. Adjusting this helps manage the detail of conversational history and can impact computational requirements and billing.

4. **Configuring bot's voice (`voice` section)**:

    - **Model**: Choose between available text-to-speech (TTS) models to define the quality and characteristics of the voice output. Options include tts-1 for standard quality and tts-1-hd for high definition audio. This setting determines the base technology for voice synthesis.
    - **Voice**: Select the specific voice identity to use from the supported options: `alloy`, `echo`, `fable`, `onyx`, `nova`, and `shimmer`. Each voice has a unique tone and style.
    - **Speed**: Adjust the playback speed of the generated audio, with a range from 0.25 (slower) to 4.0 (faster). The default setting is 1, representing normal speed.

# 🙇 Troubleshooting

- **Voice Message Issues**: If the bot fails to process voice messages, ensure ffmpeg is installed on the host machine. Check the bot's logs for any error messages related to voice processing.
- **Access Restrictions**: Users in certain regions, such as Russia, may encounter blocks when trying to access OpenAI services, resulting in the bot returning an HTML error page. To circumvent this, configure a VPN on your hosting machine or consider hosting the bot in a different geographical location where OpenAI services are available.
