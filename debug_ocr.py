#!/usr/bin/env python3
"""Debug OCR output for specific images."""

from trainer_card_parser import TrainerCardParser
import cv2


def debug_ocr(image_path: str, field: str):
    """Debug OCR for a specific image and field."""
    print(f"\nDebugging: {image_path}")
    print(f"Field: {field}")
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

    print(f"\nFull OCR text:")
    print("-"*60)
    print(text)
    print("-"*60)

    # Search for relevant keywords
    if field == "time":
        print("\nSearching for TIME keyword:")
        if 'TIME' in text:
            idx = text.find('TIME')
            print(f"  Found at position {idx}")
            print(f"  Context: ...{text[max(0, idx-10):idx+50]}...")
        else:
            print("  'TIME' not found in text")

    elif field == "pokedex":
        print("\nSearching for POKEDEX keyword:")
        for variant in ['POKEDEX', 'POKEDEV', 'POKéDEX', 'POKéeDE', 'PoKenex']:
            if variant in text:
                idx = text.find(variant)
                print(f"  Found '{variant}' at position {idx}")
                print(f"  Context: ...{text[max(0, idx-10):idx+50]}...")
                break
        else:
            print("  No POKEDEX variant found")


if __name__ == '__main__':
    debug_ocr('/Users/matt/Downloads/pokemon_rosemary_screen_nik.png', 'time')
    debug_ocr('/Users/matt/Downloads/pokemon_rosemary_screen_haley.png', 'pokedex')
