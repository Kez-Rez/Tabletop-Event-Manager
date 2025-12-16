"""Test PDF generation with multiple pages to verify page numbering"""
from database import Database
from pdf_generator import EventPDFGenerator

db = Database('events.db')

# Find an event or create test data that will span multiple pages
conn = db.get_connection()
cursor = conn.cursor()

# Get an event with some content
cursor.execute('''
    SELECT e.id, e.event_name,
           COUNT(DISTINCT ci.id) as checklist_count,
           COUNT(DISTINCT pi.id) as prize_count
    FROM events e
    LEFT JOIN event_checklist_items ci ON e.id = ci.event_id AND ci.include_in_pdf = 1
    LEFT JOIN prize_items pi ON e.id = pi.event_id
    WHERE e.is_completed = 0
    GROUP BY e.id
    ORDER BY checklist_count DESC, prize_count DESC
    LIMIT 1
''')

event = cursor.fetchone()
conn.close()

if event:
    event_id = event['id']
    event_name = event['event_name']
    checklist_count = event['checklist_count']
    prize_count = event['prize_count']

    print(f"Testing with event: {event_name}")
    print(f"  - Checklist items: {checklist_count}")
    print(f"  - Prize items: {prize_count}")
    print()

    pdf_gen = EventPDFGenerator(db)
    output = pdf_gen.generate_event_sheet(event_id, "multipage_test.pdf")

    print(f"PDF generated: {output}")
    print(f"Total pages: {pdf_gen.total_pages}")

    import os
    if os.path.exists(output):
        size = os.path.getsize(output)
        print(f"File size: {size} bytes")

        # Open the PDF for inspection
        print(f"\nOpening PDF for manual verification...")
        os.startfile(output)
else:
    print("No events found!")
