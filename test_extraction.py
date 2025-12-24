#!/usr/bin/env python3
"""Test extraction functions directly."""

from trainer_card_parser import TrainerCardParser
import cv2


def test_extraction(image_path: str, expected_time: str, expected_pokedex: int):
    """Test extraction for a specific image."""
    print(f"\nTesting: {image_path}")
    print("="*60)

    parser = TrainerCardParser()
    image = cv2.imread(image_path)

    # Find card region
    card_region = parser.find_trainer_card_region(image)
    if card_region is None:
        card_region = (0, 0, image.shape[1], image.shape[0])

    card_x, card_y, card_w, card_h = card_region
    card_image = image[card_y:card_y+card_h, card_x:card_x+card_w]

    # Get OCR text
    text = parser.extract_text_multimethod(card_image)

    # Test time extraction
    time_result = parser.extract_time(text)
    print(f"Time: extracted='{time_result}', expected='{expected_time}'")
    if time_result != expected_time:
        print(f"  Looking for TIME in text...")
        if 'TIME' in text:
            idx = text.find('TIME')
            print(f"  Context: ...{text[idx:idx+50]}...")

    # Test Pokedex extraction
    pokedex_result = parser.extract_pokedex(text)
    print(f"Pokedex: extracted={pokedex_result}, expected={expected_pokedex}")
    if pokedex_result != expected_pokedex:
        print(f"  Looking for POKEDEX in text...")
        for variant in ['POKEDEX', 'POKEDEX', 'PoKenex']:
            if variant in text:
                idx = text.find(variant)
                print(f"  Found '{variant}' at {idx}")
                print(f"  Context: ...{text[idx:idx+30]}...")
                break


if __name__ == '__main__':
    test_extraction('/Users/matt/Downloads/pokemon_rosemary_screen_jaime.png', '2:17', 11)
    test_extraction('/Users/matt/Downloads/pokemon_rosemary_screen_oscar.png', '10:46', 49)
