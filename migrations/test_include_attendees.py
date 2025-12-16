"""Test script to check include_attendees values"""
import sqlite3

def test_values():
    """Check include_attendees values for all events"""
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT id, event_name, include_attendees FROM events')
    events = [dict(row) for row in cursor.fetchall()]

    if not events:
        print("No events found in database")
    else:
        print(f"Found {len(events)} event(s):\n")
        for event in events:
            attendees_value = event.get('include_attendees')
            print(f"Event ID: {event['id']}")
            print(f"Name: {event['event_name']}")
            print(f"include_attendees: {attendees_value} (type: {type(attendees_value).__name__})")
            print(f"Boolean value: {bool(attendees_value)}")
            print("-" * 50)

    conn.close()

if __name__ == "__main__":
    test_values()
