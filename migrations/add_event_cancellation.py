"""Add event cancellation tracking fields"""
import sqlite3

def add_cancellation_fields():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute('PRAGMA table_info(events)')
    columns = [column[1] for column in cursor.fetchall()]

    # Add is_cancelled column if it doesn't exist
    if 'is_cancelled' not in columns:
        cursor.execute('''
            ALTER TABLE events ADD COLUMN is_cancelled BOOLEAN DEFAULT 0
        ''')
        print("[OK] Added is_cancelled column to events table")
    else:
        print("- is_cancelled column already exists")

    # Add cancelled_date column if it doesn't exist
    if 'cancelled_date' not in columns:
        cursor.execute('''
            ALTER TABLE events ADD COLUMN cancelled_date TIMESTAMP
        ''')
        print("[OK] Added cancelled_date column to events table")
    else:
        print("- cancelled_date column already exists")

    # Add cancellation_reason column if it doesn't exist
    if 'cancellation_reason' not in columns:
        cursor.execute('''
            ALTER TABLE events ADD COLUMN cancellation_reason TEXT
        ''')
        print("[OK] Added cancellation_reason column to events table")
    else:
        print("- cancellation_reason column already exists")

    conn.commit()
    conn.close()
    print("\nEvent cancellation tracking setup complete!")

if __name__ == '__main__':
    add_cancellation_fields()
