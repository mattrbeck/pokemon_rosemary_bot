#!/usr/bin/env python3
"""Example usage of the TrainerDataStore."""

from trainer_data_store import TrainerDataStore
from datetime import datetime, timedelta


def main():
    """Demonstrate the data store functionality."""
    print("Pokemon Rosemary - Data Store Example")
    print("=" * 60)

    # Create a data store (uses 'trainer_data.json' by default)
    store = TrainerDataStore('example_data.json')

    # Example: Recording trainer cards
    print("\n1. Recording trainer card data...")

    # User 1 posts their first badge
    store.record_trainer_card(
        discord_user_id='123456789',
        trainer_name='ASH',
        badges=1,
        time='2:15',
        pokedex=15,
        message_timestamp=datetime.now() - timedelta(days=5)
    )
    print("  ✓ Recorded: ASH - 1 badge")

    # User 1 posts their third badge
    store.record_trainer_card(
        discord_user_id='123456789',
        trainer_name='ASH',
        badges=3,
        time='5:30',
        pokedex=25,
        message_timestamp=datetime.now() - timedelta(days=3)
    )
    print("  ✓ Recorded: ASH - 3 badges")

    # User 2 posts their second badge
    store.record_trainer_card(
        discord_user_id='987654321',
        trainer_name='MISTY',
        badges=2,
        time='3:45',
        pokedex=18,
        message_timestamp=datetime.now() - timedelta(days=2)
    )
    print("  ✓ Recorded: MISTY - 2 badges")

    # Example: New badge level (even if older timestamp, it's a new record)
    print("\n2. Recording badge 2 (chronologically between badges 1 and 3)...")
    result = store.record_trainer_card(
        discord_user_id='123456789',
        trainer_name='ASH',
        badges=2,
        time='4:00',
        pokedex=20,
        message_timestamp=datetime.now() - timedelta(days=4)  # Between 1 and 3
    )
    if result:
        print("  ✓ Recorded: ASH - 2 badges (new badge level)")

    # Example: Trying to override with older data (should be rejected)
    print("\n3. Testing conflict resolution - older data for existing badge...")
    result = store.record_trainer_card(
        discord_user_id='123456789',
        trainer_name='ASH',
        badges=3,
        time='6:00',  # Different time
        pokedex=30,
        message_timestamp=datetime.now() - timedelta(days=4)  # Older than existing badge 3
    )
    if not result:
        print("  ✓ Correctly rejected older data (existing badge 3 unchanged)")

    # Example: Newer data (should override)
    print("\n4. Testing conflict resolution - newer data should override...")
    result = store.record_trainer_card(
        discord_user_id='123456789',
        trainer_name='ASH',
        badges=1,
        time='2:10',  # Better time
        pokedex=16,
        message_timestamp=datetime.now()  # Newer timestamp
    )
    if result:
        print("  ✓ Successfully updated badge 1 with newer data")

    # Example: Viewing user progress
    print("\n5. Viewing user progress...")
    progress = store.get_user_progress('123456789')
    if progress:
        print(f"\n  Trainer: {progress['trainer_name']}")
        for badge, data in sorted(progress['badge_records'].items()):
            print(f"    Badge {badge}: Time {data['time']}, Pokédex {data['pokedex']}")

    # Example: Getting latest badge
    print("\n6. Getting latest badge for each user...")
    for user_id in ['123456789', '987654321']:
        latest = store.get_latest_badge_for_user(user_id)
        if latest:
            badges, time, pokedex = latest
            trainer_name = store.get_trainer_name(user_id)
            print(f"  {trainer_name}: {badges} badges, {time}, {pokedex} Pokédex")

    # Example: Viewing all trainers
    print("\n7. Viewing gym tracker (all trainers)...")
    all_trainers = store.get_all_trainers_latest()
    for trainer in all_trainers:
        print(f"  {trainer['trainer_name']}: "
              f"{trainer['badges']} badges, "
              f"{trainer['time']}, "
              f"{trainer['pokedex']} Pokédex")

    print("\n" + "=" * 60)
    print("Data has been saved to example_data.json")
    print("You can inspect this file to see the JSON structure.")


if __name__ == '__main__':
    main()
