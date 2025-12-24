#!/usr/bin/env python3
"""Check if the bot is properly configured before running."""

import os
import sys


def check_tesseract():
    """Check if Tesseract is installed."""
    try:
        import pytesseract
        import subprocess
        result = subprocess.run(['tesseract', '--version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ Tesseract OCR: {version}")
            return True
        else:
            print("✗ Tesseract OCR: Not found or not working")
            return False
    except Exception as e:
        print(f"✗ Tesseract OCR: {e}")
        return False


def check_dependencies():
    """Check if required Python packages are installed."""
    required = ['discord', 'cv2', 'PIL', 'numpy', 'aiohttp']
    all_ok = True

    for package in required:
        try:
            if package == 'cv2':
                import cv2
                print(f"✓ OpenCV: {cv2.__version__}")
            elif package == 'discord':
                import discord
                print(f"✓ discord.py: {discord.__version__}")
            elif package == 'PIL':
                import PIL
                print(f"✓ Pillow: {PIL.__version__}")
            elif package == 'numpy':
                import numpy
                print(f"✓ NumPy: {numpy.__version__}")
            elif package == 'aiohttp':
                import aiohttp
                print(f"✓ aiohttp: {aiohttp.__version__}")
            else:
                __import__(package)
                print(f"✓ {package}: installed")
        except ImportError:
            print(f"✗ {package}: Not installed")
            all_ok = False

    return all_ok


def check_environment():
    """Check if environment variables are set."""
    token = os.getenv('DISCORD_BOT_TOKEN')
    channel_id = os.getenv('DISCORD_CHANNEL_ID')

    all_ok = True

    if token:
        print(f"✓ DISCORD_BOT_TOKEN: Set ({len(token)} characters)")
    else:
        print("✗ DISCORD_BOT_TOKEN: Not set")
        print("  Set it with: export DISCORD_BOT_TOKEN='your_token_here'")
        all_ok = False

    if channel_id:
        try:
            int(channel_id)
            print(f"✓ DISCORD_CHANNEL_ID: Set ({channel_id})")
        except ValueError:
            print(f"✗ DISCORD_CHANNEL_ID: Invalid (must be numeric, got '{channel_id}')")
            all_ok = False
    else:
        print("✗ DISCORD_CHANNEL_ID: Not set")
        print("  Set it with: export DISCORD_CHANNEL_ID='your_channel_id'")
        all_ok = False

    return all_ok


def main():
    """Run all checks."""
    print("Pokemon Rosemary Bot - Setup Check")
    print("=" * 60)

    print("\n1. Checking Tesseract OCR...")
    tesseract_ok = check_tesseract()

    print("\n2. Checking Python dependencies...")
    deps_ok = check_dependencies()

    print("\n3. Checking environment variables...")
    env_ok = check_environment()

    print("\n" + "=" * 60)

    if tesseract_ok and deps_ok and env_ok:
        print("✓ All checks passed! You're ready to run the bot.")
        print("\nRun the bot with:")
        print("  python rosemary_bot.py")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")

        if not tesseract_ok:
            print("\nTo install Tesseract:")
            print("  macOS: brew install tesseract")
            print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
            print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")

        if not deps_ok:
            print("\nTo install Python dependencies:")
            print("  pip install -r requirements.txt")

        return 1


if __name__ == '__main__':
    sys.exit(main())
