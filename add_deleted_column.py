"""Migration script to add is_deleted column to events table"""
import sqlite3
from pathlib import Path

def migrate():
    """Add is_deleted column to events table"""
    db_path = Path("events.db")

    if not db_path.exists():
        print("Database not found. Please run the application first.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(events)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'is_deleted' in columns:
            print("Column 'is_deleted' already exists. Migration skipped.")
            return

        # Add is_deleted column
        cursor.execute('''
            ALTER TABLE events
            ADD COLUMN is_deleted BOOLEAN DEFAULT 0
        ''')

        # Add deleted_at column for tracking when item was deleted
        cursor.execute('''
            ALTER TABLE events
            ADD COLUMN deleted_at TIMESTAMP
        ''')

        conn.commit()
        print("Successfully added is_deleted and deleted_at columns to events table!")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
