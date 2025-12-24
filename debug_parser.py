#!/usr/bin/env python3
"""Debug script to visualize what the parser is detecting."""

import cv2
import numpy as np
import pytesseract
from trainer_card_parser import TrainerCardParser
import sys


def debug_image(image_path: str):
    """Debug a single image to see what's being detected."""
    print(f"\nDebugging: {image_path}")
    print("="*60)

    parser = TrainerCardParser()

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not load image: {image_path}")
        return

    # Find trainer card region
    card_region = parser.find_trainer_card_region(image)
    if card_region is None:
        print("Could not detect trainer card region, using whole image")
        card_region = (0, 0, image.shape[1], image.shape[0])
    else:
        print(f"Detected card region: {card_region}")

    card_x, card_y, card_w, card_h = card_region
    card_image = image[card_y:card_y+card_h, card_x:card_x+card_w]

    # Get preprocessed image
    processed = parser.preprocess_image(card_image)

    # Get all OCR text
    text = pytesseract.image_to_string(processed, config=parser.tesseract_config_multiline)
    print(f"\nFull OCR text:\n{'-'*40}")
    print(text)
    print('-'*40)

    # Show badge region
    badge_y_start = card_y + int(card_h * 0.75)
    badge_y_end = card_y + card_h
    badge_x_start = card_x + int(card_w * 0.05)
    badge_x_end = card_x + int(card_w * 0.65)

    print(f"\nBadge region: y={badge_y_start}-{badge_y_end}, x={badge_x_start}-{badge_x_end}")

    # Count badges with more details
    badge_count = parser.count_badges(image, card_x, card_y, card_w, card_h)
    print(f"Detected badge count: {badge_count}")

    # Parse and show results
    result = parser.parse_trainer_card(image_path)
    print(f"\nFinal parsed result:")
    print(f"  Name: {result['name']}")
    print(f"  Badges: {result['badges']}")
    print(f"  Time: {result['time']}")
    print(f"  Pokedex: {result['pokedex']}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        debug_image(sys.argv[1])
    else:
        # Debug all test images
        test_images = [
            '/Users/matt/Documents/PokemonRosemary/PokemonRosemary-0.png',
            '/Users/matt/Downloads/pokemon_rosemary_screen_jaime.png',
            '/Users/matt/Downloads/pokemon_rosemary_screen_oscar.png',
        ]
        for img_path in test_images:
            debug_image(img_path)
