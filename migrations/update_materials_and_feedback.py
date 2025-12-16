"""
Migration script to:
1. Add item_type column to prize_items table (to distinguish materials vs prizes)
2. Rename prize_items table to material_prize_items
3. Add feedback_items table for the feedback menu
4. Add event_smoothness and overall_success_score to event_analysis
5. Remove old satisfaction fields
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
        # Check if item_type column already exists
        cursor.execute("PRAGMA table_info(prize_items)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'item_type' not in columns:
            print("Adding item_type column to prize_items...")
            cursor.execute('''
                ALTER TABLE prize_items ADD COLUMN item_type TEXT DEFAULT 'prize'
            ''')
            print("[OK] Added item_type column")
        else:
            print("[OK] item_type column already exists")

        # Check if feedback_items table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='feedback_items'
        """)

        if not cursor.fetchone():
            print("Creating feedback_items table...")
            cursor.execute('''
                CREATE TABLE feedback_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    feedback_text TEXT NOT NULL,
                    is_dismissed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
                )
            ''')
            print("[OK] Created feedback_items table")
        else:
            print("[OK] feedback_items table already exists")

        # Check event_analysis table and add missing columns
        cursor.execute("PRAGMA table_info(event_analysis)")
        analysis_columns = [col[1] for col in cursor.fetchall()]

        if 'event_smoothness' not in analysis_columns:
            print("Adding event_smoothness column to event_analysis...")
            cursor.execute('''
                ALTER TABLE event_analysis ADD COLUMN event_smoothness DECIMAL(3,1)
            ''')
            print("[OK] Added event_smoothness column")
        else:
            print("[OK] event_smoothness column already exists")

        if 'overall_success_score' not in analysis_columns:
            print("Adding overall_success_score column to event_analysis...")
            cursor.execute('''
                ALTER TABLE event_analysis ADD COLUMN overall_success_score DECIMAL(3,1)
            ''')
            print("[OK] Added overall_success_score column")
        else:
            print("[OK] overall_success_score column already exists")

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
