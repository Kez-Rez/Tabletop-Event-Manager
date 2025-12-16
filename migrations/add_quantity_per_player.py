"""
Migration script to add quantity_per_player column to prize_items table
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
        # Check if quantity_per_player column already exists
        cursor.execute("PRAGMA table_info(prize_items)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'quantity_per_player' not in columns:
            print("Adding quantity_per_player column to prize_items...")
            cursor.execute('''
                ALTER TABLE prize_items ADD COLUMN quantity_per_player INTEGER
            ''')
            print("[OK] Added quantity_per_player column")
        else:
            print("[OK] quantity_per_player column already exists")

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
