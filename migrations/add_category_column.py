"""Add category column to event_checklist_items table"""
import sqlite3

def update_database():
    """Add category column"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    try:
        cursor.execute('ALTER TABLE event_checklist_items ADD COLUMN category TEXT DEFAULT "Other"')
        conn.commit()
        print("SUCCESS: Added 'category' column to event_checklist_items table!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("INFO: Column 'category' already exists - no update needed!")
        else:
            print(f"ERROR: {e}")

    conn.close()

if __name__ == "__main__":
    update_database()
