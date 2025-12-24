#!/usr/bin/env python3
"""Debug badge scoring."""

import cv2
import numpy as np
import sys


def debug_scores(image_path: str, expected_badges: int):
    """Debug badge scoring for a specific image."""
    print(f"\nDebugging: {image_path}")
    print(f"Expected: {expected_badges} badges")
    print("="*60)

    image = cv2.imread(image_path)
    card_x, card_y, card_w, card_h = 0, 0, image.shape[1], image.shape[0]

    # Find actual card region for large images
    if card_w > 500 or card_h > 400:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, bright = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            aspect_ratio = w / h if h > 0 else 0
            if 1.2 < aspect_ratio < 3.0 and w > 100:
                card_x, card_y, card_w, card_h = x, y, w, h
                print(f"Found card region: x={card_x}, y={card_y}, w={card_w}, h={card_h}")

    # Badge region coordinates
    if card_w <= 250 and card_h <= 170:
        badge_y_start = card_y + 131
        badge_y_end = card_y + 147
        badge_x_start = card_x + 17
        badge_x_end = card_x + 225
    else:
        badge_y_start = card_y + int(card_h * 0.86)
        badge_y_end = card_y + int(card_h * 0.94)
        badge_x_start = card_x + int(card_w * 0.07)
        badge_x_end = card_x + int(card_w * 0.93)

    badge_region = image[badge_y_start:badge_y_end, badge_x_start:badge_x_end]
    gray_badges = cv2.cvtColor(badge_region, cv2.COLOR_BGR2GRAY)
    hsv_badges = cv2.cvtColor(badge_region, cv2.COLOR_BGR2HSV)

    segment_width = gray_badges.shape[1] // 8

    for i in range(8):
        segment_start = i * segment_width
        segment_end = (i + 1) * segment_width
        gray_segment = gray_badges[:, segment_start:segment_end]
        hsv_segment = hsv_badges[:, segment_start:segment_end]

        if gray_segment.shape[1] > 20:
            trim_width = int(gray_segment.shape[1] * 0.15)
        else:
            trim_width = 1
        if trim_width > 0 and gray_segment.shape[1] > trim_width * 2:
            gray_segment = gray_segment[:, trim_width:-trim_width]
            hsv_segment = hsv_segment[:, trim_width:-trim_width]

        saturation = hsv_segment[:, :, 1]
        mean_saturation = np.mean(saturation)
        std_brightness = np.std(gray_segment)
        min_brightness = np.min(gray_segment)
        mean_brightness = np.mean(gray_segment)

        # Calculate score using new logic
        score = 0
        details = []

        # Saturation
        if mean_saturation < 40:
            score += 4
            details.append("sat<40:+4")
        elif mean_saturation < 70:
            score += 2
            details.append("sat<70:+2")
        elif mean_saturation > 100:
            score -= 4
            details.append("sat>100:-4")

        # Variance
        if std_brightness > 50:
            score += 3
            details.append("std>50:+3")
        elif std_brightness > 35:
            score += 2
            details.append("std>35:+2")
        elif std_brightness < 20:
            score -= 2
            details.append("std<20:-2")

        # Dark pixels
        if min_brightness < 30:
            score += 3
            details.append("min<30:+3")
        elif min_brightness < 70:
            score += 2
            details.append("min<70:+2")
        elif min_brightness < 100:
            score += 1
            details.append("min<100:+1")

        # Mean brightness
        if mean_brightness < 150:
            score += 2
            details.append("mean<150:+2")
        elif mean_brightness < 180:
            score += 1
            details.append("mean<180:+1")
        elif mean_brightness > 200:
            score -= 1
            details.append("mean>200:-1")

        print(f"  Badge {i+1}: score={score:2d}  sat={mean_saturation:5.1f}  std={std_brightness:4.1f}  "
              f"min={min_brightness:3d}  mean={mean_brightness:5.1f}")
        print(f"           {', '.join(details)}")

    print()


if __name__ == '__main__':
    test_cases = [
        ('/Users/matt/Documents/PokemonRosemary/PokemonRosemary-0.png', 1),
        ('/Users/matt/Downloads/pokemon_rosemary_screen_jaime.png', 1),
        ('/Users/matt/Downloads/pokemon_rosemary_screen_oscar.png', 5),
    ]

    for img_path, expected in test_cases:
        debug_scores(img_path, expected)
