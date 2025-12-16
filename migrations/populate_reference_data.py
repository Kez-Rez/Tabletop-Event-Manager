"""Populate default reference data for the application"""
import sqlite3

def populate_data():
    """Add default event types, formats, pairing methods, and apps"""
    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()

    # Event Types
    event_types = [
        "Blood Bowl",
        "Board Games",
        "Board Game Tournament",
        "D&D Session",
        "RPG Session",
        "Kill Team",
        "Lorcana",
        "Magic: The Gathering",
        "Riftbound",
        "Warhammer 40k",
        "Age of Sigmar",
        "Pokémon"
    ]

    # Playing Formats
    formats = [
        "Casual",
        "Pauper",
        "Pioneer",
        "Commander",
        "Draft",
        "Sealed",
        "Standard",
        "Story-driven",
        "Competitive"
    ]

    # Pairing Methods
    pairing_methods = [
        "Free Play",
        "Pods",
        "Single Elimination",
        "Swiss"
    ]

    # Pairing Apps
    pairing_apps = [
        "carde.io",
        "Challonge",
        "EventLink with Companion App",
        "Manual",
        "Melee.gg"
    ]

    # Insert event types (skip if already exists)
    for event_type in event_types:
        cursor.execute('SELECT id FROM event_types WHERE name = ?', (event_type,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO event_types (name) VALUES (?)', (event_type,))
            print(f"Added event type: {event_type}")

    # Insert formats
    for format_name in formats:
        cursor.execute('SELECT id FROM playing_formats WHERE name = ?', (format_name,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO playing_formats (name) VALUES (?)', (format_name,))
            print(f"Added format: {format_name}")

    # Insert pairing methods
    for method in pairing_methods:
        cursor.execute('SELECT id FROM pairing_methods WHERE name = ?', (method,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO pairing_methods (name) VALUES (?)', (method,))
            print(f"Added pairing method: {method}")

    # Insert pairing apps
    for app in pairing_apps:
        cursor.execute('SELECT id FROM pairing_apps WHERE name = ?', (app,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO pairing_apps (name) VALUES (?)', (app,))
            print(f"Added pairing app: {app}")

    conn.commit()
    conn.close()

    print("\nDefault reference data populated successfully!")

if __name__ == "__main__":
    populate_data()
