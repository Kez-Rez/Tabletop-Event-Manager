"""Check pairing apps table"""
import sqlite3

conn = sqlite3.connect('events.db')
cursor = conn.cursor()

# Check pairing_apps table
cursor.execute("SELECT * FROM pairing_apps ORDER BY name")
apps = cursor.fetchall()

print("Pairing Apps:")
for app in apps:
    print(f"  ID: {app[0]}, Name: {app[1]}")

# Check if any events are using cardle.io
cursor.execute("SELECT COUNT(*) FROM events WHERE pairing_app_id IN (SELECT id FROM pairing_apps WHERE LOWER(name) LIKE '%cardle%')")
count = cursor.fetchone()[0]
print(f"\nEvents using cardle.io: {count}")

# Check if any templates are using cardle.io
cursor.execute("SELECT COUNT(*) FROM event_templates WHERE pairing_app_id IN (SELECT id FROM pairing_apps WHERE LOWER(name) LIKE '%cardle%')")
template_count = cursor.fetchone()[0]
print(f"Templates using cardle.io: {template_count}")

# Get the schema for pairing_apps table
cursor.execute("PRAGMA table_info(pairing_apps)")
columns = cursor.fetchall()
print("\nPairing Apps table schema:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
