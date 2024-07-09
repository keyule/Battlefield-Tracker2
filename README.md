# Battlefield Monitoring Tool Lousy Version

This Python script is designed to monitor and report on battlefield conditions and mob spawns in a specific online game. It connects to the game's API to fetch real-time data about active battlefields, including their ID, region, level and time. The script tracks changes over time and alerts users when new mobs appear.

## Features

- **Real-time updates:** Automatically fetches and updates battlefield information every 10 minutes.
- **Alert system:** Notifies users of new mob spawns that meet specific time and reward criteria.
- **Data presentation:** Displays battlefield information in a clear and structured table format.

## Requirements

- Python 3.8 or newer
- Requests
- PyTZ
- Python-dotenv
- PrettyTable
- python-telegram-bot

## Installation

1. Clone this repository or download the script to your local machine.
2. Install the required Python packages:

```bash
pip install requests pytz python-dotenv prettytable python-telegram-bot
```
3. Ensure that you have the necessary environment variables set. You can do this by creating a .env file in the same directory as the script with the following contents:
```plaintext
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_ALERTS_ENABLED=False
```

## Usage
To run the script, simply execute it from the command line:
```bash
python battlefield.py -token YOUR_BEARER_TOKEN_HERE
```

For detailed instructions on how to obtain the BEARER_TOKEN, refer to our [Guide on Obtaining the Bearer Token](https://github.com/keyule/Battlefield-Tracker/tree/main/Guide). This guide provides step-by-step instructions to capture the necessary token through network interception using tools like BlueStacks and HTTP Toolkit.

> Note: The Bearer Token will expire and is needed to be changed daily, so you will have to do all those steps everyday. When you get an error and the thing stops running, means its time to change your token. 
