"""Check ticket_tiers table schema"""
import sqlite3

conn = sqlite3.connect('events.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(ticket_tiers)")
columns = cursor.fetchall()

print("ticket_tiers table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
