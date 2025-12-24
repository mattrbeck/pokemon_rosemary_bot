#!/usr/bin/env python3
"""Pokemon Rosemary Discord Bot - Tracks trainer card progress."""

import discord
from discord import app_commands
from discord.ext import commands
import os
import aiohttp
import tempfile
import asyncio
from multiprocessing import Pool
from typing import Optional, List, Tuple
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
        self.processing_history = False  # Track if we're still processing history

    async def setup_hook(self):
        """Set up the bot before it starts."""
        # Sync slash commands
        await self.tree.sync()
        print("Slash commands synced")

    async def on_ready(self):
        """Called when the bot is ready."""
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        # Process channel history in background (will resume from last processed message)
        # This allows the bot to respond to commands while processing
        if not self.processing_history:
            self.loop.create_task(self.process_channel_history())

    async def process_channel_history(self):
        """Process all historical messages in the configured channel, resuming from last processed."""
        self.processing_history = True
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
            self.processing_history = False
            return

        # Get the last processed message ID to resume from there
        last_processed_id = self.data_store.get_last_processed_message()

        if last_processed_id:
            print(f"Resuming from message ID {last_processed_id}")
            after_snowflake = discord.Object(id=last_processed_id)
        else:
            print("Starting from beginning of channel history")
            after_snowflake = None

        try:
            # Fetch messages after the last processed one, from oldest to newest
            messages = []
            print("Fetching message history...")
            async for message in channel.history(limit=None, after=after_snowflake, oldest_first=True):
                messages.append(message)
                # Yield control to event loop periodically
                if len(messages) % 100 == 0:
                    await asyncio.sleep(0)

            if len(messages) == 0:
                print("No new messages to process")
                self.processing_history = False
                return

            print(f"Found {len(messages)} new messages to process")

            # Collect all images to process
            image_jobs = []  # List of (attachment, author, timestamp, message)
            for message in messages:
                if message.attachments:
                    for attachment in message.attachments:
                        if self._is_image(attachment):
                            image_jobs.append((attachment, message.author, message.created_at, message))

            total_images = len(image_jobs)
            if total_images == 0:
                print("No images to process")
                # Still mark messages as processed
                for message in messages:
                    self.data_store.mark_message_processed(message.id)
                    self.data_store.update_last_processed_message(message.id, message.created_at)
                self.processing_history = False
                return

            print(f"Found {total_images} images to process using process pool")

            # Process images in batches with process pool
            batch_size = 8  # Process 8 images at a time
            processed_count = 0

            # Create process pool with 4 workers
            with Pool(processes=4) as pool:
                for batch_start in range(0, len(image_jobs), batch_size):
                    batch_end = min(batch_start + batch_size, len(image_jobs))
                    batch = image_jobs[batch_start:batch_end]

                    print(f"Processing batch {batch_start // batch_size + 1} ({len(batch)} images)...")

                    # Download all images in this batch (async, in parallel)
                    download_tasks = []
                    for attachment, author, timestamp, message in batch:
                        download_tasks.append(self._download_image(attachment))

                    temp_files = await asyncio.gather(*download_tasks)

                    # Prepare jobs for process pool (only valid downloads)
                    parse_jobs = []
                    job_metadata = []
                    for idx, temp_file in enumerate(temp_files):
                        if temp_file:
                            parse_jobs.append(temp_file)
                            attachment, author, timestamp, message = batch[idx]
                            job_metadata.append((author, timestamp, message, temp_file))

                    if not parse_jobs:
                        continue

                    # Submit all parsing jobs to process pool (runs in parallel)
                    loop = asyncio.get_event_loop()
                    parse_results = await loop.run_in_executor(
                        None,
                        lambda: pool.map(self._safe_parse_trainer_card, parse_jobs)
                    )

                    # Process results and store data
                    for idx, result in enumerate(parse_results):
                        author, timestamp, message, temp_file = job_metadata[idx]

                        try:
                            if result and 'error' not in result:
                                # Success - store the data
                                self.data_store.record_trainer_card(
                                    discord_user_id=str(author.id),
                                    trainer_name=result['name'],
                                    badges=result['badges'],
                                    time=result['time'],
                                    pokedex=result['pokedex'],
                                    message_timestamp=timestamp
                                )
                                processed_count += 1
                                print(f"  [{processed_count}/{total_images}] Parsed card for {author.name}: "
                                      f"{result['name']}, {result['badges']} badges, {result['time']}, "
                                      f"{result['pokedex']} Pokedex")
                            else:
                                # Failed to parse
                                error = result.get('error', 'Unknown error') if result else 'No result'
                                print(f"  Failed to parse card for {author.name}: {error}")
                        finally:
                            # Clean up temp file
                            if temp_file and os.path.exists(temp_file):
                                os.unlink(temp_file)

                    # Yield to event loop between batches
                    await asyncio.sleep(0.1)

            # Mark all messages as processed
            for message in messages:
                self.data_store.mark_message_processed(message.id)
                self.data_store.update_last_processed_message(message.id, message.created_at)

            print(f"Processed {len(messages)} messages with {processed_count}/{total_images} images successfully")
            print("Channel history processing complete")

        except Exception as e:
            print(f"Error processing channel history: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.processing_history = False

    @staticmethod
    def _safe_parse_trainer_card(image_path: str) -> dict:
        """
        Safely parse a trainer card, catching exceptions.
        This is a static method so it can be used with multiprocessing.

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary with parsed data or error
        """
        try:
            return parse_trainer_card(image_path)
        except Exception as e:
            return {'error': str(e)}

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

        # Mark as processed (keep for backwards compatibility)
        self.data_store.mark_message_processed(message.id)

        # Update the last processed message
        self.data_store.update_last_processed_message(message.id, message.created_at)

    def _is_image(self, attachment: discord.Attachment) -> bool:
        """Check if an attachment is an image."""
        if attachment.content_type:
            return attachment.content_type.startswith('image/')
        # Fallback: check file extension
        return attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))

    async def _download_image(self, attachment: discord.Attachment) -> Optional[str]:
        """
        Download an image attachment to a temporary file.

        Args:
            attachment: Discord attachment to download

        Returns:
            Path to temporary file, or None on failure
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status != 200:
                        return None

                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
                        temp_file = f.name
                        f.write(await resp.read())
                    return temp_file
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    async def _process_image(self, attachment: discord.Attachment,
                            author: discord.User,
                            timestamp: datetime,
                            channel: Optional[discord.TextChannel] = None,
                            silent: bool = False) -> bool:
        """
        Download and process an image attachment.

        Args:
            attachment: Discord attachment to process
            author: User who posted the image
            timestamp: When the message was posted
            channel: Channel to send error messages to (if not silent)
            silent: If True, don't send error messages

        Returns:
            True if successfully processed, False otherwise
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
                        return False

                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
                        temp_file = f.name
                        f.write(await resp.read())

            # Parse the trainer card - run in executor to avoid blocking event loop
            try:
                loop = asyncio.get_event_loop()
                # Run the blocking parse_trainer_card in a thread pool
                result = await loop.run_in_executor(None, parse_trainer_card, temp_file)

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
                return True

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
                return False

        except Exception as e:
            if not silent and channel:
                await channel.send(
                    f"{author.mention} I encountered an error processing your image: {e}"
                )
            print(f"Error processing image from {author.name}: {e}")
            return False

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
            message = "I don't have any trainer card data for you yet. Post a screenshot of your trainer card to get started!"
            if bot.processing_history:
                message += "\n\n⚠️ Note: I'm still processing message history, so this data may be incomplete."
            await interaction.response.send_message(message, ephemeral=True)
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

        # Add warning if still processing
        if bot.processing_history:
            embed.set_footer(text="⚠️ Still processing message history - data may be incomplete")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @bot.tree.command(name="rosemary-gym-tracker", description="View all trainers' latest progress")
    async def rosemary_gym_tracker(interaction: discord.Interaction):
        """Show all trainers' latest badge progress."""
        trainers = bot.data_store.get_all_trainers_latest()

        if not trainers:
            message = "No trainer data recorded yet!"
            if bot.processing_history:
                message += "\n\n⚠️ Note: I'm still processing message history, so this data may be incomplete."
            await interaction.response.send_message(message, ephemeral=True)
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

        # Add warning if still processing
        if bot.processing_history:
            embed.set_footer(text="⚠️ Still processing message history - data may be incomplete")

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="rosemary-scores", description="View current score standings")
    async def rosemary_scores(interaction: discord.Interaction):
        """Show current scores (placeholder)."""
        message = "**Rosemary Scores**\n\nTo be implemented."
        if bot.processing_history:
            message += "\n\n⚠️ Note: I'm still processing message history, so data may be incomplete."
        await interaction.response.send_message(message, ephemeral=True)

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
