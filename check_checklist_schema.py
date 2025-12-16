"""Check template checklist items schema"""
import sqlite3

conn = sqlite3.connect('events.db')
cursor = conn.cursor()

print("Template Checklist Items Schema:")
cursor.execute("PRAGMA table_info(template_checklist_items)")
for row in cursor.fetchall():
    print(f"  {row}")

print("\nEvent Checklist Items Schema:")
cursor.execute("PRAGMA table_info(event_checklist_items)")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
