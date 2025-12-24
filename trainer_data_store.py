#!/usr/bin/env python3
"""Data storage for Pokemon Rosemary bot trainer tracking."""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class TrainerDataStore:
    """Manages storage and retrieval of trainer card data."""

    def __init__(self, data_file: str = 'trainer_data.json'):
        """Initialize the data store."""
        self.data_file = data_file
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """Load data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load {self.data_file}: {e}")
                return {'users': {}, 'processed_messages': []}
        return {'users': {}, 'processed_messages': []}

    def _save_data(self):
        """Save data to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving data to {self.data_file}: {e}")

    def record_trainer_card(self, discord_user_id: str, trainer_name: str,
                           badges: int, time: str, pokedex: int,
                           message_timestamp: Optional[datetime] = None) -> bool:
        """
        Record a trainer card entry.

        Args:
            discord_user_id: Discord user ID (as string)
            trainer_name: Trainer name from the card
            badges: Number of badges (0-8)
            time: Playtime string (H:MM format)
            pokedex: Number of Pokemon caught
            message_timestamp: When the message was posted (for ordering)

        Returns:
            True if this is new/updated data, False if duplicate
        """
        user_id = str(discord_user_id)

        # Initialize user data if not exists
        if user_id not in self.data['users']:
            self.data['users'][user_id] = {
                'trainer_name': trainer_name,
                'badge_records': {},
                'last_updated': None
            }

        user_data = self.data['users'][user_id]

        # Update trainer name if provided
        if trainer_name:
            user_data['trainer_name'] = trainer_name

        # Record badge data
        badge_key = str(badges)
        timestamp_str = message_timestamp.isoformat() if message_timestamp else datetime.now().isoformat()

        # Check if this is new data or should override
        if badge_key in user_data['badge_records']:
            existing_timestamp = user_data['badge_records'][badge_key].get('timestamp', '')
            # Latest data wins - only update if this is newer or no timestamp exists
            if not existing_timestamp or timestamp_str > existing_timestamp:
                user_data['badge_records'][badge_key] = {
                    'time': time,
                    'pokedex': pokedex,
                    'timestamp': timestamp_str
                }
                user_data['last_updated'] = timestamp_str
                self._save_data()
                return True
            return False  # Older data, don't override
        else:
            # New badge record
            user_data['badge_records'][badge_key] = {
                'time': time,
                'pokedex': pokedex,
                'timestamp': timestamp_str
            }
            user_data['last_updated'] = timestamp_str
            self._save_data()
            return True

    def get_user_progress(self, discord_user_id: str) -> Optional[Dict]:
        """
        Get all badge records for a user.

        Returns:
            Dict with 'trainer_name' and 'badge_records' (badge -> {time, pokedex})
            or None if user not found
        """
        user_id = str(discord_user_id)
        if user_id not in self.data['users']:
            return None

        user_data = self.data['users'][user_id]
        return {
            'trainer_name': user_data.get('trainer_name', 'Unknown'),
            'badge_records': {
                int(badge): {
                    'time': data['time'],
                    'pokedex': data['pokedex']
                }
                for badge, data in user_data.get('badge_records', {}).items()
            }
        }

    def get_latest_badge_for_user(self, discord_user_id: str) -> Optional[Tuple[int, str, int]]:
        """
        Get the latest (highest) badge number for a user with associated data.

        Returns:
            Tuple of (badge_number, time, pokedex) or None if no data
        """
        user_id = str(discord_user_id)
        if user_id not in self.data['users']:
            return None

        badge_records = self.data['users'][user_id].get('badge_records', {})
        if not badge_records:
            return None

        # Find the highest badge number
        latest_badge = max(int(badge) for badge in badge_records.keys())
        latest_data = badge_records[str(latest_badge)]

        return (latest_badge, latest_data['time'], latest_data['pokedex'])

    def get_all_trainers_latest(self) -> List[Dict]:
        """
        Get latest badge info for all tracked trainers.

        Returns:
            List of dicts with: discord_user_id, trainer_name, badges, time, pokedex
        """
        result = []

        for user_id, user_data in self.data['users'].items():
            latest = self.get_latest_badge_for_user(user_id)
            if latest:
                badges, time, pokedex = latest
                result.append({
                    'discord_user_id': user_id,
                    'trainer_name': user_data.get('trainer_name', 'Unknown'),
                    'badges': badges,
                    'time': time,
                    'pokedex': pokedex
                })

        return result

    def get_trainer_name(self, discord_user_id: str) -> Optional[str]:
        """Get the trainer name for a Discord user."""
        user_id = str(discord_user_id)
        if user_id in self.data['users']:
            return self.data['users'][user_id].get('trainer_name')
        return None

    def mark_message_processed(self, message_id: str):
        """Mark a message as processed to avoid duplicate processing."""
        msg_id = str(message_id)
        if msg_id not in self.data.get('processed_messages', []):
            if 'processed_messages' not in self.data:
                self.data['processed_messages'] = []
            self.data['processed_messages'].append(msg_id)
            self._save_data()

    def is_message_processed(self, message_id: str) -> bool:
        """Check if a message has already been processed."""
        return str(message_id) in self.data.get('processed_messages', [])
