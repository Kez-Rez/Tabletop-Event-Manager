"""Check event tables schema"""
import sqlite3

conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%ticket%' OR name LIKE '%prize%' OR name LIKE '%note%')")
tables = cursor.fetchall()

print("Relevant tables:")
for table in tables:
    print(f"  {table[0]}")
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"    {col[1]} ({col[2]})")
    print()

conn.close()
