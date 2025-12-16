"""
Migration script to add supplier column to prize_items table
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
        # Check if supplier column already exists
        cursor.execute("PRAGMA table_info(prize_items)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'supplier' not in columns:
            print("Adding supplier column to prize_items...")
            cursor.execute('''
                ALTER TABLE prize_items ADD COLUMN supplier TEXT
            ''')
            print("[OK] Added supplier column")
        else:
            print("[OK] supplier column already exists")

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
