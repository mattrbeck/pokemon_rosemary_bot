#!/usr/bin/env python3
"""Debug haley.png Pokedex extraction."""

from trainer_card_parser import TrainerCardParser
import cv2
import re


def debug_haley():
    """Debug haley.png specifically."""
    print("Debugging haley.png Pokedex extraction")
    print("="*60)

    parser = TrainerCardParser()
    image = cv2.imread('/Users/matt/Downloads/pokemon_rosemary_screen_haley.png')

    # Find card region
    card_region = parser.find_trainer_card_region(image)
    if card_region is None:
        card_region = (0, 0, image.shape[1], image.shape[0])

    card_x, card_y, card_w, card_h = card_region
    card_image = image[card_y:card_y+card_h, card_x:card_x+card_w]

    # Get OCR text
    text = parser.extract_text_multimethod(card_image)

    print(f"\nFull OCR text:")
    print("-"*60)
    print(text)
    print("-"*60)

    # Test the pattern
    three_six_pattern = r'POK[EéÉe](?:DEX|NEX)[\*:\s]+3[6Gb]'
    match = re.search(three_six_pattern, text, re.IGNORECASE)
    if match:
        print(f"\nPattern matched: {match.group(0)}")
    else:
        print(f"\nPattern did NOT match")

    # Look for variations
    print("\nLooking for variations:")
    if '3b' in text:
        print("  Found '3b' in text")
        idx = text.find('3b')
        print(f"  Context: ...{text[max(0, idx-20):idx+20]}...")

    if '36' in text:
        print("  Found '36' in text")
        idx = text.find('36')
        print(f"  Context: ...{text[max(0, idx-20):idx+20]}...")

    # Try to find any POKEDEX-like keyword followed by anything
    poke_pattern = r'[oO]?POK[EéÉe](?:DEX|NEX|eDE)[\*:\s]+(\S+)'
    matches = re.findall(poke_pattern, text, re.IGNORECASE)
    if matches:
        print(f"\n  Found POKEDEX-like patterns followed by: {matches}")

    # Run the actual extraction
    result = parser.extract_pokedex(text)
    print(f"\nExtraction result: {result}")


if __name__ == '__main__':
    debug_haley()
