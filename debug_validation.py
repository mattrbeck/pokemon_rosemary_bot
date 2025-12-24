#!/usr/bin/env python3
"""Debug validation for images that are failing."""

from trainer_card_parser import TrainerCardParser
import cv2


def debug_validation(image_path: str):
    """Debug validation for a specific image."""
    print(f"\nDebugging: {image_path}")
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

    # Check for TRAINER CARD
    if 'TRAINER' in text:
        print("\n'TRAINER' found in text")
        idx = text.find('TRAINER')
        print(f"Context: ...{text[max(0, idx-20):idx+60]}...")
    else:
        print("\n'TRAINER' NOT found in text")

    if 'CARD' in text:
        print("'CARD' found in text")
        idx = text.find('CARD')
        print(f"Context: ...{text[max(0, idx-20):idx+20]}...")
    else:
        print("'CARD' NOT found in text")

    # Run validation
    is_valid = parser.validate_trainer_card(text)
    print(f"\nValidation result: {is_valid}")


if __name__ == '__main__':
    debug_validation('/Users/matt/Documents/PokemonRosemary/PokemonRosemary-4.png')
    debug_validation('/Users/matt/Downloads/pokemon_rosemary_screen_oscar.png')
