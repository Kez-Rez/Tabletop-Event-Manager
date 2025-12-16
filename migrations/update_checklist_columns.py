"""Add columns to event_checklist_items table"""
import sqlite3

def update_checklist_table():
    """Add due_date and include_in_pdf columns"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Add due_date column
    try:
        cursor.execute('ALTER TABLE event_checklist_items ADD COLUMN due_date DATE')
        conn.commit()
        print("SUCCESS: Added 'due_date' column to event_checklist_items table!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("INFO: Column 'due_date' already exists - no update needed!")
        else:
            print(f"ERROR: {e}")

    # Add include_in_pdf column
    try:
        cursor.execute('ALTER TABLE event_checklist_items ADD COLUMN include_in_pdf INTEGER DEFAULT 1')
        conn.commit()
        print("SUCCESS: Added 'include_in_pdf' column to event_checklist_items table!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("INFO: Column 'include_in_pdf' already exists - no update needed!")
        else:
            print(f"ERROR: {e}")

    conn.close()

if __name__ == "__main__":
    update_checklist_table()
