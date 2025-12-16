"""Add include_in_pdf and show_on_dashboard columns to template_checklist_items"""
import sqlite3

def add_checklist_flags():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Check current schema
    cursor.execute("PRAGMA table_info(template_checklist_items)")
    columns = [row[1] for row in cursor.fetchall()]

    # Add include_in_pdf if it doesn't exist
    if 'include_in_pdf' not in columns:
        print("Adding include_in_pdf column to template_checklist_items...")
        cursor.execute('''
            ALTER TABLE template_checklist_items
            ADD COLUMN include_in_pdf INTEGER DEFAULT 1
        ''')
        print("SUCCESS: include_in_pdf column added")
    else:
        print("SUCCESS: include_in_pdf column already exists")

    # Add show_on_dashboard if it doesn't exist
    if 'show_on_dashboard' not in columns:
        print("Adding show_on_dashboard column to template_checklist_items...")
        cursor.execute('''
            ALTER TABLE template_checklist_items
            ADD COLUMN show_on_dashboard INTEGER DEFAULT 0
        ''')
        print("SUCCESS: show_on_dashboard column added")
    else:
        print("SUCCESS: show_on_dashboard column already exists")

    conn.commit()
    conn.close()
    print("\nDatabase migration complete!")

if __name__ == "__main__":
    add_checklist_flags()
