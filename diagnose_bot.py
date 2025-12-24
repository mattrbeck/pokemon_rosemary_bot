#!/usr/bin/env python3
"""Diagnose Discord bot connection and permissions issues."""

import discord
import os
import sys


async def diagnose():
    """Check bot connection and channel access."""
    token = os.getenv('DISCORD_BOT_TOKEN')
    channel_id = os.getenv('DISCORD_CHANNEL_ID')

    if not token or not channel_id:
        print("Error: Missing environment variables")
        return

    try:
        channel_id = int(channel_id)
    except ValueError:
        print(f"Error: Invalid channel ID: {channel_id}")
        return

    # Create a minimal bot with all necessary intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True
    intents.guilds = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"\n✓ Bot connected as: {client.user} (ID: {client.user.id})")
        print("=" * 60)

        # List all guilds (servers) the bot is in
        print(f"\nBot is in {len(client.guilds)} server(s):")
        for guild in client.guilds:
            print(f"  - {guild.name} (ID: {guild.id})")

        # Try to find the channel
        print(f"\nLooking for channel ID: {channel_id}")
        channel = client.get_channel(channel_id)

        if channel:
            print(f"✓ Found channel: #{channel.name}")
            print(f"  Server: {channel.guild.name}")
            print(f"  Type: {channel.type}")

            # Check permissions
            permissions = channel.permissions_for(channel.guild.me)
            print(f"\nBot permissions in this channel:")
            print(f"  Read Messages: {permissions.read_messages}")
            print(f"  Send Messages: {permissions.send_messages}")
            print(f"  Read Message History: {permissions.read_message_history}")
            print(f"  Attach Files: {permissions.attach_files}")

            if permissions.read_messages and permissions.read_message_history:
                print("\n✓ Bot has necessary permissions!")
            else:
                print("\n✗ Bot is missing necessary permissions!")
                print("  Required: Read Messages, Read Message History")
        else:
            print("✗ Channel not found!")
            print("\nPossible reasons:")
            print("  1. The bot is not in the server where this channel exists")
            print("  2. The channel ID is incorrect")
            print("  3. The channel was deleted")
            print("\nTo verify the channel ID:")
            print("  1. In Discord, enable Developer Mode (Settings > Advanced)")
            print("  2. Right-click the channel and select 'Copy ID'")
            print("\nAvailable channels in servers:")

            for guild in client.guilds:
                print(f"\n  {guild.name}:")
                text_channels = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
                for ch in text_channels[:10]:  # Show first 10 channels
                    print(f"    #{ch.name} (ID: {ch.id})")
                if len(text_channels) > 10:
                    print(f"    ... and {len(text_channels) - 10} more channels")

        print("\n" + "=" * 60)
        print("Diagnosis complete. Shutting down...")
        await client.close()

    try:
        await client.start(token)
    except discord.LoginFailure:
        print("✗ Login failed! Check your DISCORD_BOT_TOKEN")
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run the diagnostic."""
    print("Pokemon Rosemary Bot - Diagnostic Tool")
    print("=" * 60)

    token = os.getenv('DISCORD_BOT_TOKEN')
    channel_id = os.getenv('DISCORD_CHANNEL_ID')

    if not token:
        print("✗ DISCORD_BOT_TOKEN not set")
        print("  Set it with: export DISCORD_BOT_TOKEN='your_token'")
        return 1

    if not channel_id:
        print("✗ DISCORD_CHANNEL_ID not set")
        print("  Set it with: export DISCORD_CHANNEL_ID='channel_id'")
        return 1

    import asyncio
    asyncio.run(diagnose())
    return 0


if __name__ == '__main__':
    sys.exit(main())
