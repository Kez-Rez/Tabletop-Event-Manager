"""Test PDF generation to see what's happening"""
import sqlite3
from database import Database
from pdf_generator import EventPDFGenerator
import traceback

def test_pdf():
    """Test generating a PDF for the first available event"""
    try:
        # Connect to database
        db = Database('events.db')

        # Get first event
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, event_name FROM events WHERE is_completed = 0 LIMIT 1')
        event = cursor.fetchone()
        conn.close()

        if not event:
            print("No events found in database")
            return

        event_id = event['id']
        event_name = event['event_name']

        print(f"Testing PDF generation for event: {event_name} (ID: {event_id})")
        print("-" * 60)

        # Create PDF generator
        pdf_gen = EventPDFGenerator(db)

        # Try to generate PDF
        print("Generating PDF...")
        output_path = pdf_gen.generate_event_sheet(event_id, "test_event_sheet.pdf")

        print(f"\nPDF generated successfully!")
        print(f"Output path: {output_path}")

        # Check file size
        import os
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"File size: {file_size} bytes")

            if file_size < 100:
                print("WARNING: File is very small - might be empty!")
        else:
            print("ERROR: File was not created!")

    except Exception as e:
        print(f"\nERROR generating PDF:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf()
