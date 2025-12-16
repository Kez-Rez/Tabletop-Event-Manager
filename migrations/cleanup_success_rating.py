"""Clean up: Remove old success_rating column, keep only attendee_satisfaction"""
import sqlite3
import shutil
from datetime import datetime

def cleanup_success_rating():
    # Create a backup first
    backup_name = f"events_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2('events.db', backup_name)
    print(f"[BACKUP] Created backup: {backup_name}")

    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    print("\nCleaning up database schema...")

    # Step 1: Create new event_analysis table without success_rating
    print("[1/4] Creating new table structure...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_analysis_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL UNIQUE,
            actual_attendance INTEGER,
            attendee_satisfaction INTEGER CHECK(attendee_satisfaction >= 1 AND attendee_satisfaction <= 10),
            profit_margin DECIMAL(10,2),
            revenue_total DECIMAL(10,2),
            cost_total DECIMAL(10,2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
        )
    ''')

    # Step 2: Copy data, using attendee_satisfaction if available, otherwise success_rating
    print("[2/4] Migrating data (using attendee_satisfaction, falling back to success_rating)...")
    cursor.execute('''
        INSERT INTO event_analysis_new
            (id, event_id, actual_attendance, attendee_satisfaction, profit_margin,
             revenue_total, cost_total, notes, created_at)
        SELECT
            id,
            event_id,
            actual_attendance,
            COALESCE(attendee_satisfaction, success_rating) as attendee_satisfaction,
            profit_margin,
            revenue_total,
            cost_total,
            notes,
            created_at
        FROM event_analysis
    ''')

    # Step 3: Drop old table and rename new one
    print("[3/4] Replacing old table with new structure...")
    cursor.execute('DROP TABLE event_analysis')
    cursor.execute('ALTER TABLE event_analysis_new RENAME TO event_analysis')

    # Step 4: Verify
    cursor.execute('PRAGMA table_info(event_analysis)')
    columns = [column[1] for column in cursor.fetchall()]

    print("[4/4] Verifying cleanup...")
    if 'success_rating' in columns:
        print("[ERROR] success_rating column still exists!")
        conn.rollback()
        return False
    elif 'attendee_satisfaction' in columns:
        print("[OK] Cleanup successful! Only attendee_satisfaction column exists.")

        # Show the data to confirm
        cursor.execute('SELECT COUNT(*) as count FROM event_analysis WHERE attendee_satisfaction IS NOT NULL')
        count = cursor.fetchone()[0]
        print(f"[INFO] {count} event(s) have attendee_satisfaction data")
    else:
        print("[ERROR] Neither column exists - something went wrong!")
        conn.rollback()
        return False

    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print("SUCCESS! Database cleaned up.")
    print("- Removed: success_rating column")
    print("- Kept: attendee_satisfaction column")
    print("- All data preserved")
    print(f"- Backup saved as: {backup_name}")
    print("="*60)

    return True

if __name__ == '__main__':
    cleanup_success_rating()
