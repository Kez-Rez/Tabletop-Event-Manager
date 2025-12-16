"""Add include_attendees column to events table"""
import sqlite3

def update_database():
    """Add include_attendees column"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    try:
        cursor.execute('ALTER TABLE events ADD COLUMN include_attendees INTEGER DEFAULT 0')
        conn.commit()
        print("SUCCESS: Added 'include_attendees' column to events table!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("INFO: Column 'include_attendees' already exists - no update needed!")
        else:
            print(f"ERROR: {e}")

    conn.close()

if __name__ == "__main__":
    update_database()
