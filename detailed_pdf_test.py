"""Detailed PDF generation test with debugging"""
from database import Database
from pdf_generator import EventPDFGenerator
from reportlab.platypus import Paragraph, Table, Spacer
import traceback

# Monkey-patch the generate_event_sheet to add debugging
original_generate = EventPDFGenerator.generate_event_sheet

def debug_generate(self, event_id, output_path=None):
    """Generate PDF with debugging"""
    print(f"Starting PDF generation for event ID: {event_id}")

    # Get event data
    event_data = self._get_event_data(event_id)
    if not event_data:
        print(f"ERROR: Event {event_id} not found!")
        return None

    print(f"Event found: {event_data['event_name']}")

    # Check what content is available
    print("\n--- Checking content ---")

    ticket_tiers = self._get_ticket_tiers(event_id)
    print(f"Ticket tiers: {len(ticket_tiers)}")

    prize_items = self._get_prize_items(event_id)
    print(f"Prize items: {len(prize_items)}")

    checklist_items = self._get_checklist_items(event_id)
    print(f"Checklist items (for PDF): {len(checklist_items)}")
    for item in checklist_items:
        print(f"  - {item.get('category_name', 'None')}: {item['description']}")

    notes = self._get_printable_notes(event_id)
    print(f"Printable notes: {len(notes)}")

    players = self._get_players(event_id)
    print(f"Players: {len(players)}")

    include_attendees = event_data.get('include_attendees', False)
    print(f"Include attendees: {include_attendees}")

    print("\n--- Calling original generate function ---")
    try:
        result = original_generate(self, event_id, output_path)
        print(f"\nGeneration completed successfully!")
        return result
    except Exception as e:
        print(f"\nERROR during generation:")
        print(f"{type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise

# Apply monkey patch
EventPDFGenerator.generate_event_sheet = debug_generate

if __name__ == "__main__":
    db = Database('events.db')

    # Get first event
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM events WHERE is_completed = 0 LIMIT 1')
    event = cursor.fetchone()
    conn.close()

    if event:
        event_id = event['id']
        pdf_gen = EventPDFGenerator(db)
        output = pdf_gen.generate_event_sheet(event_id, "detailed_test.pdf")

        # Check file size
        import os
        if os.path.exists(output):
            size = os.path.getsize(output)
            print(f"\nFinal PDF size: {size} bytes")
    else:
        print("No events found!")
