# Too Good To Go Telegram Bot

This repository contains a Python-based Telegram bot that interacts with the Too Good To Go (TGTG) service to notify users about available food items from their favorite stores. The bot uses the `tgtg` library to communicate with the TGTG API and the `python-telegram-bot` library to interact with Telegram.

## Features

- **User Authentication**: Only authorized users can interact with the bot.
- **Favorite Items Monitoring**: The bot checks for updates on favorite items and notifies users when items are available.
- **Commands**:
  - `/start`: Start receiving notifications.
  - `/stop`: Stop receiving notifications.
  - `/init <email>`: Initialize the bot with your TGTG account.
  - `/info`: Get user information.

## Setup

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/tgtg_telegram_bot.git
    cd tgtg_telegram_bot
    ```

2. **Install dependencies**:
    ```sh
    pip install python-telegram-bot tgtg
    ```

3. **Run the bot**:
    ```sh
    python main.py
    ```

## Configuration

When you run the bot for the first time, you will be prompted to enter your Telegram bot token and the user IDs of authorized users. This information will be saved in `allowed_users.pkl` and `tgtg_users.pkl` files.

## Code Overview

- **Imports**: The necessary libraries are imported, including `tgtg` for TGTG API interaction and `python-telegram-bot` for Telegram bot functionality.
- **Global Variables**: Variables like `tgtg_users`, `active_users`, `allowed_users`, `cache`, and `telegram_token` are defined to manage user data and bot state.
- **Functions**:
  - `save_tgtg_users()`, `load_tgtg_users()`: Save and load TGTG user data.
  - `save_config()`, `load_config()`: Save and load bot configuration.
  - `check_auth(user_id)`: Check if a user is authorized.
  - `get_favs()`, `get_updates()`: Fetch favorite items and updates from TGTG.
  - `check_updates_per_user(userid)`: Check updates for a specific user.
- **Async Functions**:
  - `start()`, `stop()`, `init()`, `info()`: Handle Telegram commands.
  - `main(tg_bot)`: Main loop to check for updates and send notifications.
- **Main Execution**:
  - Load user data and configuration.
  - Start the bot and run the main loop in a separate thread.
  - Add command handlers and run the bot until interrupted.

## Contributing

Feel free to submit issues or pull requests if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License.
