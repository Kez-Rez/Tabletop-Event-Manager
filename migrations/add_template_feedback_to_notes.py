"""Add template_id column to event_notes for template feedback"""
import sqlite3

def add_column():
    """Add template_id column to event_notes"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            ALTER TABLE event_notes
            ADD COLUMN send_to_template INTEGER DEFAULT 0
        ''')
        print("Added send_to_template column to event_notes table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("send_to_template column already exists")
        else:
            raise

    conn.commit()
    conn.close()

    print("\nTemplate feedback enhancement added successfully!")

if __name__ == "__main__":
    add_column()
