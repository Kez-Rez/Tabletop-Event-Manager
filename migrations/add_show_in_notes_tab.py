"""
Migration script to add show_in_notes_tab column to event_notes table
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
        # Check if show_in_notes_tab column already exists
        cursor.execute("PRAGMA table_info(event_notes)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'show_in_notes_tab' not in columns:
            print("Adding show_in_notes_tab column to event_notes...")
            cursor.execute('''
                ALTER TABLE event_notes ADD COLUMN show_in_notes_tab BOOLEAN DEFAULT 0
            ''')

            # Migrate existing data: if include_in_printout is 1, set show_in_notes_tab to 1
            print("Migrating existing data...")
            cursor.execute('''
                UPDATE event_notes
                SET show_in_notes_tab = include_in_printout
            ''')

            print("[OK] Added show_in_notes_tab column and migrated data")
        else:
            print("[OK] show_in_notes_tab column already exists")

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
