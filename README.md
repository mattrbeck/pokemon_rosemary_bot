# Pokemon Rosemary Bot

A Python tool to parse Pokemon Emerald trainer cards from screenshots and extract key information.

## Features

- Extracts trainer name, badges, playtime, and Pokedex count
- Works with clean screenshots, mobile emulator overlays, and photos of screens
- 100% local processing (no remote API calls)
- Ready for Discord bot integration

## Installation

1. Install Tesseract OCR:
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```python
from trainer_card_parser import parse_trainer_card

result = parse_trainer_card("path/to/screenshot.png")
print(f"Name: {result['name']}")
print(f"Badges: {result['badges']}")
print(f"Time: {result['time']}")
print(f"Pokedex: {result['pokedex']}")
```

## Running Tests

```bash
python test_parser.py
```
