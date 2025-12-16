"""One-time script to add columns to existing database"""
import sqlite3

def update_database():
    """Add new columns to tables"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Add tickets_available column to events table
    try:
        cursor.execute('ALTER TABLE events ADD COLUMN tickets_available INTEGER')
        conn.commit()
        print("SUCCESS: Added 'tickets_available' column to events table!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("INFO: Column 'tickets_available' already exists - no update needed!")
        else:
            print(f"ERROR: {e}")

    # Add recipients column to prize_items table
    try:
        cursor.execute('ALTER TABLE prize_items ADD COLUMN recipients INTEGER DEFAULT 1')
        conn.commit()
        print("SUCCESS: Added 'recipients' column to prize_items table!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("INFO: Column 'recipients' already exists - no update needed!")
        else:
            print(f"ERROR: {e}")

    conn.close()

if __name__ == "__main__":
    update_database()
