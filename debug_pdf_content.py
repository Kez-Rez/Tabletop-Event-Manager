"""Debug what content is being added to the PDF"""
import sqlite3
from database import Database

def debug_event_content(event_id):
    """Check what content would be added to PDF for this event"""
    db = Database('events.db')
    conn = db.get_connection()
    cursor = conn.cursor()

    print(f"Checking content for event ID {event_id}")
    print("=" * 60)

    # Event data
    cursor.execute('''
        SELECT
            e.*,
            et.name as event_type_name,
            pf.name as format_name,
            pm.name as pairing_method_name,
            pa.name as pairing_app_name
        FROM events e
        LEFT JOIN event_types et ON e.event_type_id = et.id
        LEFT JOIN playing_formats pf ON e.playing_format_id = pf.id
        LEFT JOIN pairing_methods pm ON e.pairing_method_id = pm.id
        LEFT JOIN pairing_apps pa ON e.pairing_app_id = pa.id
        WHERE e.id = ?
    ''', (event_id,))
    event = dict(cursor.fetchone())

    print(f"\nEvent Name: {event['event_name']}")
    print(f"Event Date: {event['event_date']}")
    print(f"Start Time: {event.get('start_time')}")
    print(f"End Time: {event.get('end_time')}")
    print(f"Description: {event.get('description')}")
    print(f"Event Type: {event.get('event_type_name')}")
    print(f"Format: {event.get('format_name')}")
    print(f"Max Capacity: {event.get('max_capacity')}")

    # Ticket tiers
    cursor.execute('SELECT * FROM ticket_tiers WHERE event_id = ?', (event_id,))
    tickets = cursor.fetchall()
    print(f"\nTicket Tiers: {len(tickets)}")
    for ticket in tickets:
        print(f"  - {ticket['tier_name']}: ${ticket['price']}")

    # Prize items
    cursor.execute('SELECT * FROM prize_items WHERE event_id = ?', (event_id,))
    prizes = cursor.fetchall()
    print(f"\nPrize Items: {len(prizes)}")
    for prize in prizes:
        print(f"  - {prize['description']}")

    # Checklist items (for PDF)
    cursor.execute('''
        SELECT ci.*, cat.name as category_name
        FROM event_checklist_items ci
        LEFT JOIN checklist_categories cat ON ci.category_id = cat.id
        WHERE ci.event_id = ? AND ci.include_in_pdf = 1
    ''', (event_id,))
    checklist = cursor.fetchall()
    print(f"\nChecklist Items (include_in_pdf=1): {len(checklist)}")
    for item in checklist:
        cat = item['category_name'] or 'Other'
        print(f"  - [{cat}] {item['description']}")

    # Notes (for printout)
    cursor.execute('''
        SELECT * FROM event_notes
        WHERE event_id = ? AND include_in_printout = 1
    ''', (event_id,))
    notes = cursor.fetchall()
    print(f"\nNotes (include_in_printout=1): {len(notes)}")
    for note in notes:
        print(f"  - {note['note_text'][:50]}...")

    # Attendees
    cursor.execute('SELECT * FROM event_players WHERE event_id = ?', (event_id,))
    players = cursor.fetchall()
    print(f"\nPlayers/Attendees: {len(players)}")

    print(f"\nInclude Attendees in PDF: {event.get('include_attendees', False)}")

    conn.close()

if __name__ == "__main__":
    # Get first event
    db = Database('events.db')
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM events WHERE is_completed = 0 LIMIT 1')
    event = cursor.fetchone()
    conn.close()

    if event:
        debug_event_content(event['id'])
