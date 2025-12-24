# Pokemon Rosemary Bot

A Discord bot that tracks Pokemon Emerald trainer card progress by automatically parsing screenshots.

## Features

- **Automatic Trainer Card Parsing**: Monitors a Discord channel for trainer card screenshots
- **Silent Success**: Only posts messages when parsing fails
- **Progress Tracking**: Stores badge progress, playtime, and Pokedex count for each badge level
- **Historical Processing**: On startup, processes all historical images in the channel
- **Smart Conflict Resolution**: Latest data always overrides older data
- **100% Local Processing**: All image parsing happens locally using Tesseract OCR

## Commands

### `/rosemary-trainer`
View your own trainer card progress. Shows your time and Pokedex count for each badge level you've posted.

### `/rosemary-gym-tracker`
View all trainers' latest progress. Shows each trainer's most recent badge count, time, and Pokedex entries.

### `/rosemary-scores`
_(To be implemented)_ Will show current score standings.

## Setup

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR installed on your system
  - macOS: `brew install tesseract`
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Installation

1. Clone or download this repository

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a Discord bot:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to the "Bot" section and click "Add Bot"
   - Under "Privileged Gateway Intents", enable:
     - Message Content Intent
   - Copy the bot token

4. Get your channel ID:
   - In Discord, enable Developer Mode (User Settings > Advanced > Developer Mode)
   - Right-click on the channel you want to monitor and select "Copy ID"

5. Set environment variables:
   ```bash
   export DISCORD_BOT_TOKEN='your_bot_token_here'
   export DISCORD_CHANNEL_ID='your_channel_id_here'
   ```

6. Invite the bot to your server:
   - In the Developer Portal, go to OAuth2 > URL Generator
   - Select scopes: `bot` and `applications.commands`
   - Select bot permissions: `Read Messages/View Channels`, `Send Messages`, `Read Message History`
   - Copy the generated URL and open it in your browser to invite the bot

### Running the Bot

```bash
source .venv/bin/activate  # If not already activated
python rosemary_bot.py
```

On first startup, the bot will process all historical messages in the configured channel.

## Data Storage

Trainer data is stored in `trainer_data.json` in the bot's directory. This file contains:
- Mapping of Discord user IDs to trainer names
- Badge progress records (badge number → time, Pokedex count)
- Processed message IDs (to avoid duplicate processing)

## How It Works

1. **Image Detection**: The bot monitors the configured channel for messages with image attachments

2. **Trainer Card Parsing**: Each image is downloaded and processed using OCR to extract:
   - Trainer name
   - Number of badges (0-8)
   - Playtime (H:MM format)
   - Pokedex count

3. **Data Storage**: Successfully parsed data is stored with timestamps. If a user posts conflicting data (e.g., later posting a card with fewer badges), the latest data always wins based on message timestamp.

4. **Error Handling**: If parsing fails, the bot notifies the user in the channel and requests a clearer screenshot.

## Supported Image Types

The parser handles three types of screenshots:
- Pure GBA screenshots (240x160 pixels)
- Screenshots with emulator overlays (mobile controls, etc.)
- Photos of physical screens

## Development

### Running Tests

Test the trainer card parser:
```bash
python test_parser.py
```

Test validation:
```bash
python test_validation.py
```

### Parser Usage (Standalone)

```python
from trainer_card_parser import parse_trainer_card

result = parse_trainer_card("path/to/screenshot.png")
print(f"Name: {result['name']}")
print(f"Badges: {result['badges']}")
print(f"Time: {result['time']}")
print(f"Pokedex: {result['pokedex']}")
```

### Debug Tools

- `debug_badges.py`: Debug badge counting
- `debug_scores.py`: Debug badge scoring algorithm
- `debug_ocr.py`: Debug OCR text extraction
- `debug_validation.py`: Debug trainer card validation

## Troubleshooting

### "Could not find channel" Error

If you see this error when the bot starts:
```
Warning: Could not find channel 1234567890
```

**Run the diagnostic tool:**
```bash
python diagnose_bot.py
```

This will help identify the issue. Common causes:

1. **Bot not invited to the server**
   - Go to the Discord Developer Portal
   - Navigate to OAuth2 > URL Generator
   - Select scopes: `bot` and `applications.commands`
   - Select permissions: `Read Messages/View Channels`, `Send Messages`, `Read Message History`
   - Copy the generated URL and open it to invite the bot to your server

2. **Wrong channel ID**
   - In Discord, enable Developer Mode (Settings > Advanced > Developer Mode)
   - Right-click on the channel and select "Copy ID"
   - Update your environment variable: `export DISCORD_CHANNEL_ID='correct_id_here'`

3. **Missing intents in Developer Portal**
   - Go to Discord Developer Portal > Your Application > Bot
   - Under "Privileged Gateway Intents", enable:
     - **Message Content Intent** (required)
   - Save changes and restart the bot

4. **Bot lacks channel permissions**
   - In Discord, check the channel permissions
   - Ensure the bot role has:
     - View Channel
     - Read Message History
     - Send Messages

### Bot doesn't respond to commands

- Make sure slash commands are synced (happens automatically on startup)
- Wait a few minutes after inviting the bot (commands can take time to register)
- Try kicking and re-inviting the bot if commands don't appear
