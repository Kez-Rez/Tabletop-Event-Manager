"""Delete carde.io from pairing apps"""
import sqlite3

conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Delete carde.io (case insensitive)
cursor.execute("DELETE FROM pairing_apps WHERE LOWER(name) LIKE '%carde%' OR LOWER(name) LIKE '%cardle%'")
deleted = cursor.rowcount

conn.commit()
conn.close()

print(f"Deleted {deleted} entries containing 'carde' or 'cardle'")
