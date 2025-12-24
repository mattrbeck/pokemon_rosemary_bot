#!/usr/bin/env python3
"""Pokemon Rosemary Discord Bot - Tracks trainer card progress."""

import discord
from discord import app_commands
from discord.ext import commands
import os
import aiohttp
import tempfile
from typing import Optional, List
from datetime import datetime

from trainer_card_parser import parse_trainer_card
from trainer_data_store import TrainerDataStore


class RosemaryBot(commands.Bot):
    """Pokemon Rosemary trainer card tracking bot."""

    def __init__(self, channel_id: int):
        """Initialize the bot."""
        intents = discord.Intents.default()
        intents.message_content = True  # Required to read message content
        intents.messages = True          # Required to receive message events
        intents.guilds = True            # Required to see servers and channels

        super().__init__(command_prefix='!', intents=intents)

        self.channel_id = channel_id
        self.data_store = TrainerDataStore()
        self.startup_complete = False

    async def setup_hook(self):
        """Set up the bot before it starts."""
        # Sync slash commands
        await self.tree.sync()
        print("Slash commands synced")

    async def on_ready(self):
        """Called when the bot is ready."""
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        # Process historical messages on first startup
        if not self.startup_complete:
            await self.process_channel_history()
            self.startup_complete = True

    async def process_channel_history(self):
        """Process all historical messages in the configured channel."""
        print("Processing channel history...")

        channel = self.get_channel(self.channel_id)
        if not channel:
            print(f"ERROR: Could not find channel {self.channel_id}")
            print(f"\nBot is currently in {len(self.guilds)} server(s):")
            for guild in self.guilds:
                print(f"  - {guild.name} (ID: {guild.id})")
            print("\nPossible issues:")
            print("  1. The bot hasn't been invited to the server with this channel")
            print("  2. The channel ID is incorrect")
            print("  3. The bot lacks permissions to view the channel")
            print(f"\nRun 'python diagnose_bot.py' for detailed diagnostics")
            return

        message_count = 0
        image_count = 0

        try:
            # Fetch messages from oldest to newest
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                messages.append(message)

            print(f"Found {len(messages)} historical messages to process")

            for message in messages:
                # Skip if already processed
                if self.data_store.is_message_processed(message.id):
                    continue

                message_count += 1

                # Process attachments
                if message.attachments:
                    for attachment in message.attachments:
                        if self._is_image(attachment):
                            image_count += 1
                            await self._process_image(
                                attachment,
                                message.author,
                                message.created_at,
                                silent=True  # Don't send error messages for historical data
                            )

                # Mark as processed
                self.data_store.mark_message_processed(message.id)

            print(f"Processed {message_count} messages with {image_count} images from history")

        except Exception as e:
            print(f"Error processing channel history: {e}")

    async def on_message(self, message: discord.Message):
        """Handle new messages."""
        # Ignore our own messages
        if message.author == self.user:
            return

        # Only process messages from the configured channel
        if message.channel.id != self.channel_id:
            return

        # Skip if already processed
        if self.data_store.is_message_processed(message.id):
            return

        # Check for image attachments
        if message.attachments:
            for attachment in message.attachments:
                if self._is_image(attachment):
                    await self._process_image(
                        attachment,
                        message.author,
                        message.created_at,
                        message.channel,
                        silent=False  # Send error messages for new images
                    )

        # Mark as processed
        self.data_store.mark_message_processed(message.id)

    def _is_image(self, attachment: discord.Attachment) -> bool:
        """Check if an attachment is an image."""
        if attachment.content_type:
            return attachment.content_type.startswith('image/')
        # Fallback: check file extension
        return attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))

    async def _process_image(self, attachment: discord.Attachment,
                            author: discord.User,
                            timestamp: datetime,
                            channel: Optional[discord.TextChannel] = None,
                            silent: bool = False):
        """
        Download and process an image attachment.

        Args:
            attachment: Discord attachment to process
            author: User who posted the image
            timestamp: When the message was posted
            channel: Channel to send error messages to (if not silent)
            silent: If True, don't send error messages
        """
        temp_file = None

        try:
            # Download image to temporary file
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status != 200:
                        if not silent and channel:
                            await channel.send(
                                f"{author.mention} I couldn't download your image. Please try again."
                            )
                        return

                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
                        temp_file = f.name
                        f.write(await resp.read())

            # Parse the trainer card
            try:
                result = parse_trainer_card(temp_file)

                # Store the data
                self.data_store.record_trainer_card(
                    discord_user_id=str(author.id),
                    trainer_name=result['name'],
                    badges=result['badges'],
                    time=result['time'],
                    pokedex=result['pokedex'],
                    message_timestamp=timestamp
                )

                # Success - silent unless debugging
                print(f"Parsed card for {author.name}: {result['name']}, "
                      f"{result['badges']} badges, {result['time']}, {result['pokedex']} Pokedex")

            except ValueError as e:
                # Failed to parse trainer card
                if not silent and channel:
                    error_msg = str(e)
                    if "No valid trainer card found" in error_msg:
                        await channel.send(
                            f"{author.mention} I couldn't find a trainer card in your image. "
                            f"Please make sure you're posting a Pokemon Emerald trainer card screenshot."
                        )
                    elif "Could not extract critical fields" in error_msg:
                        await channel.send(
                            f"{author.mention} I found a trainer card but couldn't read some important fields. "
                            f"Could you post a clearer screenshot?"
                        )
                    else:
                        await channel.send(
                            f"{author.mention} I had trouble reading your trainer card. "
                            f"Please try posting a clearer screenshot."
                        )
                print(f"Failed to parse card for {author.name}: {e}")

        except Exception as e:
            if not silent and channel:
                await channel.send(
                    f"{author.mention} I encountered an error processing your image: {e}"
                )
            print(f"Error processing image from {author.name}: {e}")

        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)


# Initialize bot instance
bot = None


def create_bot(channel_id: int) -> RosemaryBot:
    """Create and configure the bot instance."""
    global bot
    bot = RosemaryBot(channel_id=channel_id)

    @bot.tree.command(name="rosemary-trainer", description="View your trainer card progress")
    async def rosemary_trainer(interaction: discord.Interaction):
        """Show the user's own trainer card progress."""
        user_id = str(interaction.user.id)
        progress = bot.data_store.get_user_progress(user_id)

        if not progress or not progress['badge_records']:
            await interaction.response.send_message(
                "I don't have any trainer card data for you yet. "
                "Post a screenshot of your trainer card to get started!",
                ephemeral=True
            )
            return

        # Build the response
        trainer_name = progress['trainer_name']
        badge_records = progress['badge_records']

        embed = discord.Embed(
            title=f"Trainer Progress: {trainer_name}",
            color=discord.Color.green()
        )

        # Sort by badge number
        for badge_num in sorted(badge_records.keys()):
            record = badge_records[badge_num]
            badge_label = f"{'Badge' if badge_num == 1 else 'Badges'}"
            embed.add_field(
                name=f"{badge_num} {badge_label}",
                value=f"⏱️ Time: {record['time']}\n📖 Pokédex: {record['pokedex']}",
                inline=True
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="rosemary-gym-tracker", description="View all trainers' latest progress")
    async def rosemary_gym_tracker(interaction: discord.Interaction):
        """Show all trainers' latest badge progress."""
        trainers = bot.data_store.get_all_trainers_latest()

        if not trainers:
            await interaction.response.send_message(
                "No trainer data recorded yet!",
                ephemeral=True
            )
            return

        # Sort by badge count (descending), then by time (ascending)
        trainers.sort(key=lambda x: (-x['badges'], x['time']))

        embed = discord.Embed(
            title="Pokemon Rosemary - Gym Tracker",
            description="Latest progress for all trainers",
            color=discord.Color.blue()
        )

        for trainer in trainers:
            badge_emoji = "🏅" * trainer['badges']
            if not badge_emoji:
                badge_emoji = "Starting journey..."

            embed.add_field(
                name=f"{trainer['trainer_name']}",
                value=f"{badge_emoji}\n"
                      f"**Badges:** {trainer['badges']}\n"
                      f"**Time:** {trainer['time']}\n"
                      f"**Pokédex:** {trainer['pokedex']}",
                inline=True
            )

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="rosemary-scores", description="View current score standings")
    async def rosemary_scores(interaction: discord.Interaction):
        """Show current scores (placeholder)."""
        await interaction.response.send_message(
            "**Rosemary Scores**\n\nTo be implemented.",
            ephemeral=True
        )

    return bot


def main():
    """Main entry point for the bot."""
    # Get configuration from environment variables
    token = os.getenv('DISCORD_BOT_TOKEN')
    channel_id = os.getenv('DISCORD_CHANNEL_ID')

    if not token:
        print("Error: DISCORD_BOT_TOKEN environment variable not set")
        print("Set it with: export DISCORD_BOT_TOKEN='your_token_here'")
        return

    if not channel_id:
        print("Error: DISCORD_CHANNEL_ID environment variable not set")
        print("Set it with: export DISCORD_CHANNEL_ID='channel_id_here'")
        return

    try:
        channel_id = int(channel_id)
    except ValueError:
        print(f"Error: DISCORD_CHANNEL_ID must be a numeric ID, got: {channel_id}")
        return

    # Create and run the bot
    bot_instance = create_bot(channel_id)
    bot_instance.run(token)


if __name__ == '__main__':
    main()
