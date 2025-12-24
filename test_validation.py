#!/usr/bin/env python3
"""Test that validation properly rejects non-trainer-card images."""

from trainer_card_parser import parse_trainer_card
import cv2
import numpy as np


def test_invalid_image():
    """Test that parser rejects an image without a trainer card."""
    # Create a simple test image that's not a trainer card
    # Just a solid color image
    test_image_path = '/tmp/test_not_trainer_card.png'

    # Create a 300x200 blue image
    image = np.zeros((200, 300, 3), dtype=np.uint8)
    image[:, :] = (255, 0, 0)  # Blue in BGR
    cv2.imwrite(test_image_path, image)

    print("Testing with a non-trainer-card image...")
    print("="*60)

    try:
        result = parse_trainer_card(test_image_path)
        print(f"✗ FAIL: Parser should have rejected this image!")
        print(f"  Got result: {result}")
        return False
    except ValueError as e:
        print(f"✓ PASS: Parser correctly rejected the image")
        print(f"  Error message: {e}")
        return True


def test_valid_images():
    """Test that parser accepts all valid trainer card images."""
    valid_images = [
        '/Users/matt/Documents/PokemonRosemary/PokemonRosemary-0.png',
        '/Users/matt/Documents/PokemonRosemary/PokemonRosemary-2.png',
        '/Users/matt/Documents/PokemonRosemary/PokemonRosemary-4.png',
        '/Users/matt/Downloads/pokemon_rosemary_screen_jaime.png',
        '/Users/matt/Downloads/pokemon_rosemary_screen_nik.png',
        '/Users/matt/Downloads/pokemon_rosemary_screen_haley.png',
        '/Users/matt/Downloads/pokemon_rosemary_screen_zac.png',
        '/Users/matt/Downloads/pokemon_rosemary_screen_oscar.png',
    ]

    print("\nTesting that valid trainer cards are accepted...")
    print("="*60)

    all_passed = True
    for image_path in valid_images:
        try:
            result = parse_trainer_card(image_path)
            print(f"✓ {image_path.split('/')[-1]}: Accepted")
        except ValueError as e:
            print(f"✗ {image_path.split('/')[-1]}: Rejected (should have been accepted)")
            print(f"  Error: {e}")
            all_passed = False

    return all_passed


if __name__ == '__main__':
    print("Validation Test Suite")
    print("="*60)

    # Test invalid image
    invalid_passed = test_invalid_image()

    # Test valid images
    valid_passed = test_valid_images()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if invalid_passed and valid_passed:
        print("✓ All validation tests passed!")
        print("  - Invalid images are correctly rejected")
        print("  - Valid trainer cards are correctly accepted")
    else:
        print("✗ Some validation tests failed")
        if not invalid_passed:
            print("  - Failed to reject invalid image")
        if not valid_passed:
            print("  - Failed to accept some valid trainer cards")
