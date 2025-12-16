import sqlite3

# Add send_to_template column to event_notes table
conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Check if column already exists
cursor.execute("PRAGMA table_info(event_notes)")
columns = [column[1] for column in cursor.fetchall()]

if 'send_to_template' not in columns:
    print("Adding send_to_template column to event_notes table...")
    cursor.execute('''
        ALTER TABLE event_notes
        ADD COLUMN send_to_template BOOLEAN DEFAULT 0
    ''')
    conn.commit()
    print("Column added successfully!")
else:
    print("Column send_to_template already exists.")

conn.close()
