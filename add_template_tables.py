"""Add template-specific tables for tickets, prizes, and notes"""
import sqlite3

def add_template_tables():
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Create template_ticket_tiers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS template_ticket_tiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER NOT NULL,
            tier_name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity_available INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES event_templates(id) ON DELETE CASCADE
        )
    ''')

    # Create template_prize_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS template_prize_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            quantity INTEGER,
            cost_per_item REAL,
            total_cost REAL,
            supplier TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES event_templates(id) ON DELETE CASCADE
        )
    ''')

    # Create template_notes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS template_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER NOT NULL,
            note_text TEXT NOT NULL,
            include_in_printout INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES event_templates(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("Template tables created successfully!")

if __name__ == "__main__":
    add_template_tables()
