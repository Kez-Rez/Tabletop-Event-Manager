import sqlite3

# Add quantity_handed_out column to prize_items table
conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Check if column already exists
cursor.execute("PRAGMA table_info(prize_items)")
columns = [column[1] for column in cursor.fetchall()]

if 'quantity_handed_out' not in columns:
    print("Adding quantity_handed_out column to prize_items table...")
    cursor.execute('''
        ALTER TABLE prize_items
        ADD COLUMN quantity_handed_out INTEGER DEFAULT 0
    ''')
    conn.commit()
    print("Column added successfully!")
else:
    print("Column quantity_handed_out already exists.")

conn.close()
