"""Migration to add number_of_rounds column to events table"""
import sqlite3
from datetime import datetime
import shutil

# Create backup
backup_name = f"events_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
print(f"Creating backup: {backup_name}")
shutil.copy2('events.db', backup_name)

# Connect and migrate
print("Connecting to database...")
conn = sqlite3.connect('events.db')
cursor = conn.cursor()

try:
    # Add number_of_rounds column
    print("Adding number_of_rounds column to events table...")
    cursor.execute('''
        ALTER TABLE events
        ADD COLUMN number_of_rounds INTEGER
    ''')

    conn.commit()
    print("Migration complete!")
    print(f"Backup saved as: {backup_name}")

except sqlite3.Error as e:
    print(f"Error during migration: {e}")
    conn.rollback()

finally:
    conn.close()
