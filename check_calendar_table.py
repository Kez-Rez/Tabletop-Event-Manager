"""Check calendar_entries table"""
import sqlite3

conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Check if calendar_entries table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calendar_entries'")
result = cursor.fetchone()

if result:
    print("calendar_entries table exists!")
    cursor.execute("PRAGMA table_info(calendar_entries)")
    columns = cursor.fetchall()
    print("\nColumns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
else:
    print("calendar_entries table does NOT exist! Creating it...")
    cursor.execute('''
        CREATE TABLE calendar_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date DATE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            entry_type TEXT NOT NULL,
            color TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print("Table created successfully!")

conn.close()
