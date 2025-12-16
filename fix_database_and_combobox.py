"""Fix database column and check for other issues"""
import sqlite3

def fix_database():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Check if success_rating column exists
    cursor.execute("PRAGMA table_info(event_analysis)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'success_rating' not in columns:
        print("Adding success_rating column to event_analysis table...")
        cursor.execute('''
            ALTER TABLE event_analysis
            ADD COLUMN success_rating INTEGER
        ''')
        print("SUCCESS: success_rating column added")
    else:
        print("SUCCESS: success_rating column already exists")

    conn.commit()
    conn.close()
    print("\nDatabase fix complete!")

if __name__ == "__main__":
    fix_database()
