"""
Migration script to update checklist categories
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def migrate():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    print("Starting migration...")

    try:
        # Update existing categories to new names
        category_mapping = {
            'Before Event': 'Before the Event',
            'Day Of': 'During the Event',
            'After Event': 'After the Event'
        }

        for old_name, new_name in category_mapping.items():
            cursor.execute('''
                UPDATE checklist_categories
                SET name = ?
                WHERE name = ?
            ''', (new_name, old_name))
            print(f"[OK] Updated '{old_name}' to '{new_name}'")

        # Add 'Other' category if it doesn't exist
        cursor.execute('''
            INSERT OR IGNORE INTO checklist_categories (name, sort_order)
            VALUES ('Other', 4)
        ''')
        print("[OK] Added 'Other' category")

        conn.commit()
        print("\n[SUCCESS] Migration completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
