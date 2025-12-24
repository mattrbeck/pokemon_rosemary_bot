#!/usr/bin/env python3
"""Test the pattern matching."""

import re

text = "oPOkeDE* 3b"

patterns = [
    r'[oO]?POK[EéÉe](?:DEX|NEX|eDE|keDE)[\*:\s]+3\s*[6Gb]',
    r'[oO]?POK[EéÉe](?:DEX|NEX|DE|eDE|keDE)[\*:\s]+3\s*[6Gb]',  # Added just "DE"
]

for i, pattern in enumerate(patterns):
    match = re.search(pattern, text, re.IGNORECASE)
    print(f"Pattern {i+1}: {pattern}")
    print(f"  Match: {match.group(0) if match else 'NO MATCH'}")
    print()
