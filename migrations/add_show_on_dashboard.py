"""Add show_on_dashboard column to event_checklist_items table"""
import sqlite3

def add_column():
    """Add show_on_dashboard column"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            ALTER TABLE event_checklist_items
            ADD COLUMN show_on_dashboard INTEGER DEFAULT 0
        ''')
        print("Added show_on_dashboard column to event_checklist_items table")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print("show_on_dashboard column already exists")
        else:
            raise

    conn.commit()
    conn.close()

    print("\nDashboard enhancement added successfully!")

if __name__ == "__main__":
    add_column()
