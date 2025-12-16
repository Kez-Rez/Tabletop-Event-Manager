"""Fix include_attendees for existing events"""
import sqlite3

def fix_data():
    """Update any NULL include_attendees values to 0"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # First check if column exists
    cursor.execute("PRAGMA table_info(events)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'include_attendees' not in columns:
        print("ERROR: include_attendees column does not exist!")
        print("Please run: python add_include_attendees.py first")
        conn.close()
        return

    # Update any NULL values to 0
    cursor.execute('''
        UPDATE events
        SET include_attendees = 0
        WHERE include_attendees IS NULL
    ''')

    rows_updated = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_updated > 0:
        print(f"SUCCESS: Updated {rows_updated} event(s) to have include_attendees = 0")
    else:
        print("INFO: No events needed updating - all have include_attendees values set")

if __name__ == "__main__":
    fix_data()
