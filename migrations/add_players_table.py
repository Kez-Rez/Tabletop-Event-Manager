"""Add players table to database"""
import sqlite3

def add_players_table():
    """Add players table for tracking attendees"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                player_name TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        print("SUCCESS: Created 'event_players' table!")
    except sqlite3.Error as e:
        print(f"ERROR: {e}")

    conn.close()

if __name__ == "__main__":
    add_players_table()
