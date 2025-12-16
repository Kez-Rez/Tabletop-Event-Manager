"""Add satisfaction breakdown fields (loved%, liked%, disliked%)"""
import sqlite3
import shutil
from datetime import datetime

def add_satisfaction_breakdown():
    # Create backup
    backup_name = f"events_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2('events.db', backup_name)
    print(f"[BACKUP] Created backup: {backup_name}")

    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Check current schema
    cursor.execute('PRAGMA table_info(event_analysis)')
    columns = [column[1] for column in cursor.fetchall()]

    # Add new columns if they don't exist
    new_columns = [
        ('satisfaction_loved_pct', 'INTEGER CHECK(satisfaction_loved_pct >= 0 AND satisfaction_loved_pct <= 100)'),
        ('satisfaction_liked_pct', 'INTEGER CHECK(satisfaction_liked_pct >= 0 AND satisfaction_liked_pct <= 100)'),
        ('satisfaction_disliked_pct', 'INTEGER CHECK(satisfaction_disliked_pct >= 0 AND satisfaction_disliked_pct <= 100)')
    ]

    for col_name, col_type in new_columns:
        if col_name not in columns:
            cursor.execute(f'''
                ALTER TABLE event_analysis
                ADD COLUMN {col_name} {col_type}
            ''')
            print(f"[OK] Added {col_name} column")
        else:
            print(f"- {col_name} column already exists")

    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print("SUCCESS! Satisfaction breakdown fields added.")
    print("New fields:")
    print("- satisfaction_loved_pct (8-10/10 rating)")
    print("- satisfaction_liked_pct (5-7/10 rating)")
    print("- satisfaction_disliked_pct (1-4/10 rating)")
    print("")
    print("Formula: (loved% × 9 + liked% × 6 + disliked% × 2.5) ÷ 100")
    print(f"Backup saved as: {backup_name}")
    print("="*60)

if __name__ == '__main__':
    add_satisfaction_breakdown()
