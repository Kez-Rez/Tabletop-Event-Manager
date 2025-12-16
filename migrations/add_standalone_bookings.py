"""Add standalone table bookings"""
import sqlite3
from datetime import datetime

def migrate(db_path: str = "events.db"):
    """Create table for standalone bookings (not tied to events)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create standalone bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS standalone_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_name TEXT NOT NULL,
            booking_description TEXT,
            booking_date DATE NOT NULL,
            start_time TIME,
            end_time TIME,
            tables_booked INTEGER NOT NULL DEFAULT 1,
            notes TEXT,
            is_deleted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create index for faster date lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_standalone_bookings_date
        ON standalone_bookings(booking_date)
        WHERE is_deleted = 0
    ''')

    conn.commit()
    conn.close()
    print("Standalone bookings migration completed successfully")

if __name__ == '__main__':
    migrate()
