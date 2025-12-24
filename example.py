#!/usr/bin/env python3
"""Example usage of the Pokemon Emerald trainer card parser."""

from trainer_card_parser import parse_trainer_card


def main():
    # Parse a trainer card screenshot
    image_path = "/Users/matt/Documents/PokemonRosemary/PokemonRosemary-0.png"

    print(f"Parsing trainer card: {image_path}\n")

    result = parse_trainer_card(image_path)

    print("Results:")
    print(f"  Trainer Name: {result['name']}")
    print(f"  Badges:       {result['badges']}")
    print(f"  Playtime:     {result['time']}")
    print(f"  Pokedex:      {result['pokedex']}")


if __name__ == '__main__':
    main()
