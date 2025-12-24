# Discord Bot Setup Guide - Step by Step

## Part 1: Create the Bot in Discord Developer Portal

### Step 1: Create an Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** (top right)
3. Give it a name (e.g., "Pokemon Rosemary Bot")
4. Click **"Create"**

### Step 2: Create a Bot User
1. In the left sidebar, click **"Bot"**
2. Click **"Add Bot"** button
3. Click **"Yes, do it!"** to confirm
4. You should now see a bot user with a token

### Step 3: Enable Privileged Intents
Still on the Bot page:
1. Scroll down to **"Privileged Gateway Intents"**
2. Toggle ON: **"MESSAGE CONTENT INTENT"** ✓
3. Click **"Save Changes"** at the bottom

### Step 4: Copy Your Bot Token
1. Still on the Bot page, find the **"Token"** section
2. Click **"Reset Token"** (if you haven't copied it yet)
3. Click **"Copy"** to copy your bot token
4. **IMPORTANT**: Save this somewhere safe - you'll need it later
5. Never share this token publicly!

## Part 2: Invite the Bot to Your Server

### Step 5: Generate an Invite URL
1. In the left sidebar, click **"OAuth2"**
2. Click **"URL Generator"** (sub-menu under OAuth2)

3. Under **"Scopes"**, select:
   - ✓ `bot`
   - ✓ `applications.commands`

4. Under **"Bot Permissions"** (appears after selecting bot scope), select:
   - ✓ `View Channels`
   - ✓ `Send Messages`
   - ✓ `Read Message History`

5. At the bottom, you'll see a **"Generated URL"**
6. Click **"Copy"** to copy this URL

### Step 6: Invite the Bot
1. Paste the copied URL into your browser
2. Select the server you want to add the bot to
3. Click **"Continue"**
4. Review the permissions and click **"Authorize"**
5. Complete the CAPTCHA if prompted

### Step 7: Verify the Bot is in Your Server
1. Go to Discord
2. Open your server
3. Check the member list (right sidebar)
4. You should see your bot listed with a "BOT" tag
5. The bot will appear offline (gray) until you run it

## Part 3: Configure and Run the Bot

### Step 8: Get Your Channel ID
1. In Discord, go to **Settings > Advanced**
2. Enable **"Developer Mode"** ✓
3. Go to the channel where you want the bot to monitor images
4. Right-click on the channel name
5. Click **"Copy ID"**
6. Save this ID - you'll need it next

### Step 9: Set Environment Variables
In your terminal, run:

```bash
# Set the bot token (paste the token you copied in Step 4)
export DISCORD_BOT_TOKEN='paste_your_token_here'

# Set the channel ID (paste the ID you copied in Step 8)
export DISCORD_CHANNEL_ID='paste_channel_id_here'
```

**For permanent setup**, add these to your shell profile:
```bash
# Add to ~/.zshrc (macOS) or ~/.bashrc (Linux)
echo 'export DISCORD_BOT_TOKEN="your_token_here"' >> ~/.zshrc
echo 'export DISCORD_CHANNEL_ID="your_channel_id_here"' >> ~/.zshrc
source ~/.zshrc
```

### Step 10: Run the Diagnostic
Before running the bot, verify everything is set up correctly:

```bash
# Activate your virtual environment
source .venv/bin/activate

# Run the diagnostic tool
python diagnose_bot.py
```

You should see:
- ✓ Bot connected
- ✓ Bot is in your server
- ✓ Channel found
- ✓ Bot has necessary permissions

### Step 11: Run the Bot
If the diagnostic passes:

```bash
python rosemary_bot.py
```

You should see:
```
Logged in as YourBotName (ID: ...)
Processing channel history...
Found X historical messages to process
Processed X messages with Y images from history
```

The bot is now running! It will:
- Monitor the configured channel for new images
- Automatically parse trainer cards
- Respond to slash commands

## Part 4: Using the Bot

### Test with a Slash Command
In Discord, in any channel where the bot has access, type:
```
/rosemary-
```

You should see the three commands appear:
- `/rosemary-trainer` - View your progress
- `/rosemary-gym-tracker` - View all trainers
- `/rosemary-scores` - (Not yet implemented)

### Post a Trainer Card
1. Post a Pokemon Emerald trainer card screenshot in the configured channel
2. The bot will silently parse it (no message if successful)
3. Use `/rosemary-trainer` to see your recorded progress

## Troubleshooting

### "Could not find channel"
- Make sure you invited the bot to the correct server
- Verify the channel ID is correct (copy it again)
- Check that the bot can see the channel (not a private channel it's excluded from)

### Bot appears offline
- This is normal until you run the Python script
- Once you run `python rosemary_bot.py`, the bot should show as online (green)

### Slash commands don't appear
- Wait 5-10 minutes after first inviting the bot
- Make sure you selected `applications.commands` scope when inviting
- Try kicking the bot and re-inviting with the correct scopes

### "Message Content Intent" error
- Go back to Developer Portal > Bot
- Enable "MESSAGE CONTENT INTENT"
- Save changes
- Restart the bot

### Token invalid
- Make sure you copied the entire token
- Check for extra spaces
- Generate a new token if needed (Developer Portal > Bot > Reset Token)

## Quick Reference

**Check if everything is configured:**
```bash
python setup_check.py
```

**Diagnose connection issues:**
```bash
python diagnose_bot.py
```

**Run the bot:**
```bash
python rosemary_bot.py
```

**Test the parser manually:**
```bash
python test_parser.py
```
