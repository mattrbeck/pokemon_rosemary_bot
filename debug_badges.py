#!/usr/bin/env python3
"""Debug badge counting to see what's happening."""

import cv2
import numpy as np
from trainer_card_parser import TrainerCardParser


def debug_badges(image_path: str, expected_badges: int):
    """Debug badge counting for a specific image."""
    print(f"\nDebugging badges: {image_path}")
    print(f"Expected: {expected_badges} badges")
    print("="*60)

    parser = TrainerCardParser()
    image = cv2.imread(image_path)

    # Find card region
    card_region = parser.find_trainer_card_region(image)
    if card_region is None:
        card_region = (0, 0, image.shape[1], image.shape[0])

    card_x, card_y, card_w, card_h = card_region
    print(f"Card region: x={card_x}, y={card_y}, w={card_w}, h={card_h}")

    # Check if we need to find actual card
    if card_w > 1000 or card_h > 800:
        print("Card region too large, looking for actual card...")
        card_area = image[card_y:card_y+card_h, card_x:card_x+card_w]
        gray = cv2.cvtColor(card_area, cv2.COLOR_BGR2GRAY)
        _, bright = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            aspect_ratio = w / h if h > 0 else 0
            if 1.2 < aspect_ratio < 3.0 and w > 200:
                card_x, card_y, card_w, card_h = card_x + x, card_y + y, w, h
                print(f"Found actual card: x={card_x}, y={card_y}, w={card_w}, h={card_h}")

    # Get badge region using same logic as main parser
    if card_w <= 250 and card_h <= 170:  # Clean GBA screenshot
        badge_y_start = card_y + 131
        badge_y_end = card_y + 147
        badge_x_start = card_x + 17
        badge_x_end = card_x + 225
    else:  # Larger images
        badge_y_start = card_y + int(card_h * 0.86)
        badge_y_end = card_y + int(card_h * 0.94)
        badge_x_start = card_x + int(card_w * 0.07)
        badge_x_end = card_x + int(card_w * 0.93)

    print(f"Badge region: y={badge_y_start}-{badge_y_end}, x={badge_x_start}-{badge_x_end}")

    badge_region = image[badge_y_start:badge_y_end, badge_x_start:badge_x_end]
    gray_badges = cv2.cvtColor(badge_region, cv2.COLOR_BGR2GRAY)
    hsv_badges = cv2.cvtColor(badge_region, cv2.COLOR_BGR2HSV)

    print(f"Badge region shape: {gray_badges.shape}")

    # Analyze segments
    segment_width = gray_badges.shape[1] // 8
    print(f"Segment width: {segment_width}")

    for i in range(8):
        segment_start = i * segment_width
        segment_end = (i + 1) * segment_width
        gray_segment = gray_badges[:, segment_start:segment_end]
        hsv_segment = hsv_badges[:, segment_start:segment_end]

        if gray_segment.size == 0:
            continue

        # Trim edges like the main algorithm
        if gray_segment.shape[1] > 20:
            trim_width = int(gray_segment.shape[1] * 0.15)
        else:
            trim_width = 1
        if trim_width > 0 and gray_segment.shape[1] > trim_width * 2:
            gray_segment = gray_segment[:, trim_width:-trim_width]
            hsv_segment = hsv_segment[:, trim_width:-trim_width]

        if gray_segment.size == 0:
            continue

        # Calculate metrics
        saturation = hsv_segment[:, :, 1]
        mean_saturation = np.mean(saturation)
        high_sat_pixels = np.sum(saturation > 50)
        high_sat_pct = (high_sat_pixels / saturation.size * 100) if saturation.size > 0 else 0

        std_brightness = np.std(gray_segment)
        min_brightness = np.min(gray_segment)

        # Check using the algorithm's logic
        is_filled = False
        reasons = []

        if mean_saturation > 30 or (high_sat_pixels / saturation.size if saturation.size > 0 else 0) > 0.10:
            is_filled = True
            reasons.append(f"sat")
        if std_brightness > 30:
            is_filled = True
            reasons.append(f"std")
        if min_brightness < 80:
            is_filled = True
            reasons.append(f"min")

        reason = "+".join(reasons) if reasons else "empty"

        print(f"  Badge {i+1}: sat={mean_saturation:.1f}, sat>50={high_sat_pct:.1f}%, "
              f"std={std_brightness:.1f}, min={min_brightness}, filled={is_filled} ({reason})")

    # Get actual count
    badge_count = parser.count_badges(image, card_x, card_y, card_w, card_h)
    print(f"\nDetected: {badge_count} badges (expected: {expected_badges})")


if __name__ == '__main__':
    test_cases = [
        ('/Users/matt/Documents/PokemonRosemary/PokemonRosemary-0.png', 1),
        ('/Users/matt/Downloads/pokemon_rosemary_screen_jaime.png', 1),
        ('/Users/matt/Downloads/pokemon_rosemary_screen_oscar.png', 5),
    ]

    for img_path, expected in test_cases:
        debug_badges(img_path, expected)
