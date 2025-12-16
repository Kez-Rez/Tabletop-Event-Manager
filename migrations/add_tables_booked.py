"""Add tables_booked column to events table"""
import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

def migrate():
    """Add tables_booked column to events table"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    # Check if column already exists
    cursor.execute("PRAGMA table_info(events)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'tables_booked' not in columns:
        print("Adding tables_booked column to events table...")
        cursor.execute('''
            ALTER TABLE events
            ADD COLUMN tables_booked INTEGER DEFAULT 0
        ''')
        conn.commit()
        print("[OK] Added tables_booked column")
    else:
        print("[OK] tables_booked column already exists")

    conn.close()
    print("\nMigration completed successfully!")

if __name__ == "__main__":
    migrate()
