#!/usr/bin/env python3
"""Test the trainer card parser on example images."""

from trainer_card_parser import parse_trainer_card


def test_image(image_path: str, expected_name: str, expected_badges: int,
               expected_time: str, expected_pokedex: int):
    """Test parsing a single image and compare with expected values."""
    print(f"\n{'='*60}")
    print(f"Testing: {image_path}")
    print(f"{'='*60}")

    try:
        result = parse_trainer_card(image_path)

        print(f"\nExtracted values:")
        print(f"  Name:    {result['name']}")
        print(f"  Badges:  {result['badges']}")
        print(f"  Time:    {result['time']}")
        print(f"  Pokedex: {result['pokedex']}")

        print(f"\nExpected values:")
        print(f"  Name:    {expected_name}")
        print(f"  Badges:  {expected_badges}")
        print(f"  Time:    {expected_time}")
        print(f"  Pokedex: {expected_pokedex}")

        # Check accuracy
        checks = {
            'Name': result['name'] == expected_name,
            'Badges': result['badges'] == expected_badges,
            'Time': result['time'] == expected_time,
            'Pokedex': result['pokedex'] == expected_pokedex
        }

        print(f"\nAccuracy:")
        all_correct = True
        for field, is_correct in checks.items():
            status = "✓" if is_correct else "✗"
            print(f"  {status} {field}")
            if not is_correct:
                all_correct = False

        if all_correct:
            print("\n✓ ALL CHECKS PASSED!")
        else:
            print("\n✗ Some checks failed")

        return all_correct

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Pokemon Emerald Trainer Card Parser - Test Suite")
    print("="*60)

    test_cases = [
        {
            'path': '/Users/matt/Documents/PokemonRosemary/PokemonRosemary-0.png',
            'name': 'MATT',
            'badges': 1,
            'time': '1:33',
            'pokedex': 12
        },
        {
            'path': '/Users/matt/Documents/PokemonRosemary/PokemonRosemary-2.png',
            'name': 'MATT',
            'badges': 2,
            'time': '2:40',
            'pokedex': 16
        },
        {
            'path': '/Users/matt/Documents/PokemonRosemary/PokemonRosemary-4.png',
            'name': 'MATT',
            'badges': 3,
            'time': '4:30',
            'pokedex': 21
        },
        {
            'path': '/Users/matt/Downloads/pokemon_rosemary_screen_jaime.png',
            'name': 'ZAC 2.0',
            'badges': 1,
            'time': '2:17',
            'pokedex': 11
        },
        {
            'path': '/Users/matt/Downloads/pokemon_rosemary_screen_nik.png',
            'name': 'KERMIT',
            'badges': 3,
            'time': '5:49',
            'pokedex': 25
        },
        {
            'path': '/Users/matt/Downloads/pokemon_rosemary_screen_haley.png',
            'name': 'HALEY',
            'badges': 5,
            'time': '14:13',
            'pokedex': 36
        },
        {
            'path': '/Users/matt/Downloads/pokemon_rosemary_screen_zac.png',
            'name': 'Zac',
            'badges': 6,
            'time': '14:11',
            'pokedex': 55
        },
        {
            'path': '/Users/matt/Downloads/pokemon_rosemary_screen_oscar.png',
            'name': 'OG',
            'badges': 5,
            'time': '10:46',
            'pokedex': 49
        }
    ]

    results = []
    for test_case in test_cases:
        passed = test_image(
            test_case['path'],
            test_case['name'],
            test_case['badges'],
            test_case['time'],
            test_case['pokedex']
        )
        results.append(passed)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    passed_count = sum(results)
    total_count = len(results)
    print(f"\nTests passed: {passed_count}/{total_count}")

    if passed_count == total_count:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")


if __name__ == '__main__':
    main()
