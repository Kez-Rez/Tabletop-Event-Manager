"""Add operating hours for table booking"""
import sqlite3

def migrate(db_path: str = "events.db"):
    """Create table for standard operating hours by day of week"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create operating hours table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operating_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week INTEGER NOT NULL UNIQUE,
            is_open INTEGER DEFAULT 1,
            open_time TIME,
            close_time TIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK (day_of_week >= 0 AND day_of_week <= 6)
        )
    ''')

    # Insert default hours (Monday=0 to Sunday=6)
    default_hours = [
        (0, 1, '10:00:00', '22:00:00'),  # Monday
        (1, 1, '10:00:00', '22:00:00'),  # Tuesday
        (2, 1, '10:00:00', '22:00:00'),  # Wednesday
        (3, 1, '10:00:00', '22:00:00'),  # Thursday
        (4, 1, '10:00:00', '22:00:00'),  # Friday
        (5, 1, '10:00:00', '22:00:00'),  # Saturday
        (6, 1, '10:00:00', '22:00:00'),  # Sunday
    ]

    for day, is_open, open_time, close_time in default_hours:
        cursor.execute('''
            INSERT OR IGNORE INTO operating_hours
            (day_of_week, is_open, open_time, close_time)
            VALUES (?, ?, ?, ?)
        ''', (day, is_open, open_time, close_time))

    conn.commit()
    conn.close()
    print("Operating hours migration completed successfully")

if __name__ == '__main__':
    migrate()
