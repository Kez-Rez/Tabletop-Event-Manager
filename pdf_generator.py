"""PDF generator for event sheets"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus.flowables import HRFlowable
from reportlab.graphics.shapes import Drawing, Rect, Line
from datetime import datetime
from typing import Optional
import os


class EventPDFGenerator:
    """Generates printable event day sheets"""

    def __init__(self, db):
        self.db = db
        self.total_pages = 0

    def generate_event_sheet(self, event_id: int, output_path: Optional[str] = None):
        """Generate a PDF event sheet for the given event"""
        # Get event data
        event_data = self._get_event_data(event_id)

        if not event_data:
            raise ValueError(f"Event with ID {event_id} not found")

        # Default output path if not provided
        if not output_path:
            event_name_safe = event_data['event_name'].replace(' ', '_').replace('/', '-')
            event_date = event_data['event_date'].replace('-', '')
            output_path = f"event_sheet_{event_name_safe}_{event_date}.pdf"

        # Store event data for footer
        self.event_data = event_data
        self.event_id_for_story = event_id

        # Build PDF with two-pass approach for correct page numbering
        # First pass: count pages
        doc = self._create_doc_template(output_path)
        story = self._build_event_story(event_id, event_data)
        doc.build(story)
        self.total_pages = doc.page

        # Second pass: build with correct page counts
        doc = self._create_doc_template(output_path)
        story = self._build_event_story(event_id, event_data)
        doc.build(story)

        return output_path

    def _create_doc_template(self, output_path: str):
        """Create a document template with standard settings"""
        doc = BaseDocTemplate(
            output_path,
            pagesize=A4,
            topMargin=15*mm,
            bottomMargin=20*mm,
            leftMargin=15*mm,
            rightMargin=15*mm
        )

        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id='normal'
        )

        template = PageTemplate(id='main', frames=frame, onPage=self._add_footer)
        doc.addPageTemplates([template])

        return doc

    def _build_event_story(self, event_id: int, event_data: dict):
        """Build the story (content) for an event sheet PDF"""
        story = []
        styles = self._get_styles()

        # Title
        story.append(Paragraph(event_data['event_name'], styles['EventTitle']))
        story.append(Spacer(1, 5*mm))

        # Event Date
        try:
            event_date_obj = datetime.strptime(event_data['event_date'], '%Y-%m-%d')
            formatted_date = event_date_obj.strftime('%A, %d %B %Y')
        except:
            formatted_date = event_data['event_date']

        story.append(Paragraph(f"<b>Date:</b> {formatted_date}", styles['Normal']))

        # Time
        if event_data.get('start_time') and event_data.get('end_time'):
            start_time = event_data['start_time'].rsplit(':', 1)[0]  # Remove seconds
            end_time = event_data['end_time'].rsplit(':', 1)[0]
            story.append(Paragraph(f"<b>Time:</b> {start_time} - {end_time}", styles['Normal']))

        story.append(Spacer(1, 3*mm))

        # Event Details Table
        details_data = []

        if event_data.get('event_type_name'):
            details_data.append(['Event Type:', event_data['event_type_name']])

        if event_data.get('format_name'):
            details_data.append(['Playing Format:', event_data['format_name']])

        if event_data.get('pairing_method_name'):
            details_data.append(['Pairing Method:', event_data['pairing_method_name']])

        if event_data.get('pairing_app_name'):
            details_data.append(['Pairing App:', event_data['pairing_app_name']])

        if event_data.get('max_capacity'):
            details_data.append(['Maximum Capacity:', str(event_data['max_capacity']) + ' players'])

        if event_data.get('tickets_available'):
            details_data.append(['Tickets Available:', str(event_data['tickets_available'])])

        if details_data:
            # Wrap values in Paragraphs to enable text wrapping
            wrapped_details = []
            for label, value in details_data:
                wrapped_details.append([
                    Paragraph(f'<b>{label}</b>', styles['Normal']),
                    Paragraph(str(value), styles['Normal'])
                ])

            details_table = Table(wrapped_details, colWidths=[45*mm, 125*mm])
            details_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(details_table)
            story.append(Spacer(1, 5*mm))

        # Description
        if event_data.get('description'):
            story.append(Paragraph('<b>Description:</b>', styles['EventHeading']))
            # Convert line breaks to HTML breaks to preserve formatting
            description_html = event_data['description'].replace('\n', '<br/>')
            story.append(Paragraph(description_html, styles['Normal']))
            story.append(Spacer(1, 5*mm))

        # Ticket Pricing
        ticket_tiers = self._get_ticket_tiers(event_id)
        if ticket_tiers:
            story.append(Paragraph('<b>Ticket Pricing:</b>', styles['EventHeading']))
            pricing_data = [[
                Paragraph('<b>Tier</b>', styles['Normal']),
                Paragraph('<b>Price</b>', styles['Normal']),
                Paragraph('<b>Available</b>', styles['Normal']),
                Paragraph('<b>Attendance</b>', styles['Normal'])
            ]]
            for tier in ticket_tiers:
                pricing_data.append([
                    Paragraph(tier['tier_name'], styles['Normal']),
                    Paragraph(f"${tier['price']:.2f}", styles['Normal']),
                    Paragraph(str(tier['quantity_available']), styles['Normal']),
                    Paragraph('', styles['Normal'])  # Empty for manual fill-in
                ])

            pricing_table = Table(pricing_data, colWidths=[50*mm, 30*mm, 30*mm, 30*mm])
            pricing_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'CENTER'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E6D9F2')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(pricing_table)
            story.append(Spacer(1, 5*mm))

        # Prize Support
        prize_items = self._get_prize_items(event_id)
        if prize_items:
            story.append(Paragraph('<b>Prize Support:</b>', styles['EventHeading']))
            prize_data = [['Description', 'Qty', 'Received']]
            for prize in prize_items:
                qty = str(prize['quantity']) if prize['quantity'] else '-'

                # Create multiple checkboxes based on recipients count
                recipients = prize.get('recipients') or 1
                checkboxes = self._create_checkbox_row(recipients)

                # Use Paragraph for description to enable text wrapping
                desc_para = Paragraph(prize['description'], styles['Normal'])

                prize_data.append([
                    desc_para,
                    qty,
                    checkboxes
                ])

            prize_table = Table(prize_data, colWidths=[95*mm, 20*mm, 40*mm])
            prize_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E6D9F2')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(prize_table)
            story.append(Spacer(1, 5*mm))

        # Event Day Checklist
        checklist_items = self._get_checklist_items(event_id)
        if checklist_items:
            story.append(Paragraph('<b>Event Day Checklist:</b>', styles['EventHeading']))

            # Group by category
            by_category = {}
            for item in checklist_items:
                cat = item.get('category_name')
                # If no category name, default to 'Other'
                if not cat or cat == '':
                    cat = 'Other'
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(item)

            # Display by category (in the order they appear in database)
            # Get list of all categories that actually have items
            all_categories = ['Before the Event', 'During the Event', 'After the Event', 'Other']
            for category in all_categories:
                if category in by_category:
                    story.append(Paragraph(f'<i>{category}:</i>', styles['EventItalic']))
                    checklist_data = []
                    for item in by_category[category]:
                        # Create a checkbox drawing that can be ticked with a pen
                        checkbox = self._create_checkbox(False)
                        # Use Paragraph for description to enable text wrapping
                        desc_para = Paragraph(item['description'], styles['Normal'])
                        checklist_data.append([checkbox, desc_para])

                    checklist_table = Table(checklist_data, colWidths=[8*mm, 162*mm])
                    checklist_table.setStyle(TableStyle([
                        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 2),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ]))
                    story.append(checklist_table)
                    story.append(Spacer(1, 3*mm))

        # Event Notes (only those marked for printout)
        notes = self._get_printable_notes(event_id)
        if notes:
            story.append(Paragraph('<b>Important Notes:</b>', styles['EventHeading']))
            for note in notes:
                story.append(Paragraph(f"• {note['note_text']}", styles['Normal']))
            story.append(Spacer(1, 5*mm))

        # Players/Attendees List
        players = self._get_players(event_id)
        max_capacity = event_data.get('max_capacity') or 0

        # Check if attendees should be included (check include_attendees flag)
        include_attendees = event_data.get('include_attendees', False)

        # If there are players OR a max capacity set AND attendees are flagged for inclusion
        if (players or max_capacity > 0) and include_attendees:
            story.append(Spacer(1, 5*mm))
            story.append(Paragraph('<b>Attendees:</b>', styles['EventHeading']))
            story.append(Spacer(1, 3*mm))

            # Determine number of rows (max capacity or number of players, whichever is greater)
            num_rows = max(max_capacity, len(players)) if max_capacity > 0 else len(players)

            # If we have max_capacity but no players yet, ensure we have at least that many rows
            if num_rows == 0 and max_capacity > 0:
                num_rows = max_capacity

            # Build attendees table
            attendees_data = [[
                Paragraph('<b>Attendee</b>', styles['Normal']),
                Paragraph('<b>Here</b>', styles['Normal']),
                Paragraph('', styles['Normal'])
            ]]  # Header with blank custom column

            for i in range(num_rows):
                if i < len(players):
                    attendee_name = players[i]['player_name']
                else:
                    attendee_name = ''  # Empty row for manual entry

                attendees_data.append([
                    Paragraph(attendee_name, styles['Normal']),
                    Paragraph('', styles['Normal']),
                    Paragraph('', styles['Normal'])
                ])

            attendees_table = Table(attendees_data, colWidths=[80*mm, 20*mm, 70*mm], repeatRows=1)
            attendees_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E6D9F2')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(attendees_table)
            story.append(Spacer(1, 5*mm))

        # Space for handwritten notes
        story.append(Spacer(1, 5*mm))
        story.append(Paragraph('<b>Additional Notes:</b>', styles['EventHeading']))
        story.append(Spacer(1, 3*mm))

        # Create lines for handwritten notes
        for _ in range(5):
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey, spaceBefore=0, spaceAfter=5*mm))

        return story

    def _get_event_data(self, event_id: int):
        """Get event data with joined reference tables"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

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

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def _get_ticket_tiers(self, event_id: int):
        """Get ticket tiers for the event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM ticket_tiers
            WHERE event_id = ?
            ORDER BY price
        ''', (event_id,))

        tiers = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return tiers

    def _get_prize_items(self, event_id: int):
        """Get prize items for the event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM prize_items
            WHERE event_id = ?
            ORDER BY created_at
        ''', (event_id,))

        prizes = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return prizes

    def _get_checklist_items(self, event_id: int):
        """Get checklist items for the event (only those marked for PDF)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT ci.*, cat.name as category_name, cat.sort_order as category_order
            FROM event_checklist_items ci
            LEFT JOIN checklist_categories cat ON ci.category_id = cat.id
            WHERE ci.event_id = ? AND ci.include_in_pdf = 1
            ORDER BY cat.sort_order, ci.sort_order
        ''', (event_id,))

        items = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return items

    def _get_printable_notes(self, event_id: int):
        """Get notes marked for printout"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM event_notes
            WHERE event_id = ? AND include_in_printout = 1
            ORDER BY created_at
        ''', (event_id,))

        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return notes

    def _create_checkbox(self, checked: bool):
        """Create a checkbox drawing with black border and optional checkmark"""
        d = Drawing(10, 10)
        # Draw black border box
        d.add(Rect(1, 1, 8, 8, strokeColor=colors.black, strokeWidth=1, fillColor=None))
        # Add checkmark if checked
        if checked:
            d.add(Line(2, 5, 4, 3, strokeColor=colors.black, strokeWidth=1.5))
            d.add(Line(4, 3, 8, 8, strokeColor=colors.black, strokeWidth=1.5))
        return d

    def _create_checkbox_row(self, count: int):
        """Create a row of checkboxes for prize distribution tracking"""
        if count <= 0:
            count = 1

        # For small counts (1-6), show all checkboxes in a row
        if count <= 6:
            width = count * 12  # 10 for box + 2 for spacing
            d = Drawing(width, 10)
            for i in range(count):
                x_offset = i * 12
                d.add(Rect(x_offset + 1, 1, 8, 8, strokeColor=colors.black, strokeWidth=1, fillColor=None))
            return d

        # For larger counts, show grid layout with checkboxes
        # Calculate rows needed (max 6 per row)
        boxes_per_row = 6
        rows_needed = (count + boxes_per_row - 1) // boxes_per_row  # Ceiling division

        width = boxes_per_row * 12
        height = rows_needed * 12

        d = Drawing(width, height)

        for i in range(count):
            row = i // boxes_per_row
            col = i % boxes_per_row
            x_offset = col * 12
            y_offset = height - (row * 12) - 10  # Flip Y coordinate

            d.add(Rect(x_offset + 1, y_offset + 1, 8, 8, strokeColor=colors.black, strokeWidth=1, fillColor=None))

        return d

    def _get_styles(self):
        """Get custom paragraph styles"""
        styles = getSampleStyleSheet()

        # Custom title style
        styles.add(ParagraphStyle(
            name='EventTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#8B5FBF'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Custom heading style
        styles.add(ParagraphStyle(
            name='EventHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#4A2D5E'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))

        # Italic style
        styles.add(ParagraphStyle(
            name='EventItalic',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Oblique',
            spaceAfter=3
        ))

        return styles

    def _get_players(self, event_id: int):
        """Get players for the event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM event_players
            WHERE event_id = ?
            ORDER BY sort_order, player_name
        ''', (event_id,))

        players = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return players

    def _add_footer(self, canvas, doc):
        """Add footer to each page"""
        canvas.saveState()

        # Get page dimensions
        page_width = A4[0]
        footer_y = 10*mm

        # Left - Event name (truncate if too long)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(15*mm, footer_y, self.event_data['event_name'][:50])

        # Middle - Date in shortform
        try:
            event_date_obj = datetime.strptime(self.event_data['event_date'], '%Y-%m-%d')
            short_date = event_date_obj.strftime('%d/%m/%Y')
        except:
            short_date = self.event_data['event_date']

        canvas.drawCentredString(page_width / 2, footer_y, short_date)

        # Right - Page number with total pages
        if self.total_pages > 0:
            page_num_text = f"Page {canvas._pageNumber} of {self.total_pages}"
        else:
            page_num_text = f"Page {canvas._pageNumber}"
        canvas.drawRightString(page_width - 15*mm, footer_y, page_num_text)

        canvas.restoreState()

    def _add_simple_footer(self, canvas, doc):
        """Add simple footer to each page for multi-event list"""
        canvas.saveState()

        # Get page dimensions
        page_width = A4[0]
        footer_y = 10*mm

        # Left - Document title
        canvas.setFont('Helvetica', 8)
        canvas.drawString(15*mm, footer_y, "Upcoming Events")

        # Middle - Generation date
        today = datetime.now().strftime('%d/%m/%Y')
        canvas.drawCentredString(page_width / 2, footer_y, f"Generated: {today}")

        # Right - Page number with total pages
        if self.total_pages > 0:
            page_num_text = f"Page {canvas._pageNumber} of {self.total_pages}"
        else:
            page_num_text = f"Page {canvas._pageNumber}"
        canvas.drawRightString(page_width - 15*mm, footer_y, page_num_text)

        canvas.restoreState()

    def generate_upcoming_events_list(self, output_path: Optional[str] = None):
        """Generate a PDF list of all upcoming events ordered by date"""
        # Get all upcoming events (not completed)
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                e.*,
                et.name as event_type_name,
                pf.name as format_name,
                pm.name as pairing_method_name
            FROM events e
            LEFT JOIN event_types et ON e.event_type_id = et.id
            LEFT JOIN playing_formats pf ON e.playing_format_id = pf.id
            LEFT JOIN pairing_methods pm ON e.pairing_method_id = pm.id
            WHERE e.is_completed = 0 AND e.is_deleted = 0
            ORDER BY e.event_date ASC
        ''')

        events = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not events:
            raise ValueError("No upcoming events found")

        # Default output path if not provided
        if not output_path:
            today = datetime.now().strftime('%Y%m%d')
            output_path = f"upcoming_events_{today}.pdf"

        # Create PDF with custom page template for footer
        doc = BaseDocTemplate(
            output_path,
            pagesize=A4,
            topMargin=15*mm,
            bottomMargin=20*mm,
            leftMargin=15*mm,
            rightMargin=15*mm
        )

        # Create frame for main content
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id='normal'
        )

        # Create page template with footer
        template = PageTemplate(id='main', frames=frame, onPage=self._add_simple_footer)
        doc.addPageTemplates([template])

        # Build content
        story = []
        styles = self._get_styles()

        # Title
        story.append(Paragraph("Upcoming Events", styles['EventTitle']))
        story.append(Spacer(1, 3*mm))

        # Generation info
        gen_date = datetime.now().strftime('%A, %d %B %Y at %I:%M %p')
        story.append(Paragraph(f"<i>Generated: {gen_date}</i>", styles['EventItalic']))
        story.append(Paragraph(f"<i>Total Events: {len(events)}</i>", styles['EventItalic']))
        story.append(Spacer(1, 8*mm))

        # Display each event
        for i, event in enumerate(events):
            # Event card/section
            # Event name as heading
            story.append(Paragraph(event['event_name'], styles['EventHeading']))
            story.append(Spacer(1, 2*mm))

            # Format date nicely
            try:
                event_date = datetime.strptime(event['event_date'], '%Y-%m-%d')
                formatted_date = event_date.strftime('%A, %d %B %Y')
            except:
                formatted_date = event['event_date']

            # Event details
            details_data = [['Date:', formatted_date]]

            # Time
            if event.get('start_time') and event.get('end_time'):
                start_time = event['start_time'].rsplit(':', 1)[0]
                end_time = event['end_time'].rsplit(':', 1)[0]
                details_data.append(['Time:', f"{start_time} - {end_time}"])

            if event.get('event_type_name'):
                details_data.append(['Event Type:', event['event_type_name']])

            if event.get('format_name'):
                details_data.append(['Playing Format:', event['format_name']])

            if event.get('pairing_method_name'):
                details_data.append(['Pairing Method:', event['pairing_method_name']])

            if event.get('tables_booked'):
                details_data.append(['Tables Booked:', str(event['tables_booked'])])

            if event.get('max_capacity'):
                details_data.append(['Maximum Capacity:', f"{event['max_capacity']} players"])

            # Wrap details in Paragraphs to enable text wrapping
            wrapped_details = []
            for label, value in details_data:
                wrapped_details.append([
                    Paragraph(f'<b>{label}</b>', styles['Normal']),
                    Paragraph(str(value), styles['Normal'])
                ])

            # Create details table
            details_table = Table(wrapped_details, colWidths=[40*mm, 130*mm])
            details_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(details_table)
            story.append(Spacer(1, 3*mm))

            # Status badges
            status_items = []
            if event.get('is_organised'):
                status_items.append('Organised')
            if event.get('tickets_live'):
                status_items.append('Tickets Live')
            if event.get('is_advertised'):
                status_items.append('Advertised')

            if status_items:
                status_text = ' • '.join(status_items)
                story.append(Paragraph(f"<b>Status:</b> {status_text}", styles['Normal']))
                story.append(Spacer(1, 3*mm))

            # Description
            if event.get('description'):
                # Convert line breaks to HTML breaks to preserve formatting
                description_html = event['description'].replace('\n', '<br/>')
                story.append(Paragraph(f"<b>Description:</b> {description_html}", styles['Normal']))
                story.append(Spacer(1, 3*mm))

            # Add separator line between events (except after last event)
            if i < len(events) - 1:
                story.append(Spacer(1, 3*mm))
                story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E6D9F2'),
                                       spaceBefore=0, spaceAfter=5*mm))
                story.append(Spacer(1, 3*mm))

        # Build PDF with two-pass approach for correct page numbering
        # First pass: count pages
        doc.build(story)
        self.total_pages = doc.page

        # Rebuild the document and story for second pass
        doc = BaseDocTemplate(
            output_path,
            pagesize=A4,
            topMargin=15*mm,
            bottomMargin=20*mm,
            leftMargin=15*mm,
            rightMargin=15*mm
        )
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id='normal'
        )
        template = PageTemplate(id='main', frames=frame, onPage=self._add_simple_footer)
        doc.addPageTemplates([template])

        # Rebuild story (we need to recreate it as the first build consumed it)
        story = []
        styles = self._get_styles()

        # Title
        story.append(Paragraph("Upcoming Events", styles['EventTitle']))
        story.append(Spacer(1, 3*mm))

        # Generation info
        gen_date = datetime.now().strftime('%A, %d %B %Y at %I:%M %p')
        story.append(Paragraph(f"<i>Generated: {gen_date}</i>", styles['EventItalic']))
        story.append(Paragraph(f"<i>Total Events: {len(events)}</i>", styles['EventItalic']))
        story.append(Spacer(1, 8*mm))

        # Display each event (rebuild the same content)
        for i, event in enumerate(events):
            story.append(Paragraph(event['event_name'], styles['EventHeading']))
            story.append(Spacer(1, 2*mm))

            try:
                event_date = datetime.strptime(event['event_date'], '%Y-%m-%d')
                formatted_date = event_date.strftime('%A, %d %B %Y')
            except:
                formatted_date = event['event_date']

            details_data = [['Date:', formatted_date]]

            if event.get('start_time') and event.get('end_time'):
                start_time = event['start_time'].rsplit(':', 1)[0]
                end_time = event['end_time'].rsplit(':', 1)[0]
                details_data.append(['Time:', f"{start_time} - {end_time}"])

            if event.get('event_type_name'):
                details_data.append(['Event Type:', event['event_type_name']])

            if event.get('format_name'):
                details_data.append(['Playing Format:', event['format_name']])

            if event.get('pairing_method_name'):
                details_data.append(['Pairing Method:', event['pairing_method_name']])

            if event.get('tables_booked'):
                details_data.append(['Tables Booked:', str(event['tables_booked'])])

            if event.get('max_capacity'):
                details_data.append(['Maximum Capacity:', f"{event['max_capacity']} players"])

            # Wrap details in Paragraphs to enable text wrapping
            wrapped_details = []
            for label, value in details_data:
                wrapped_details.append([
                    Paragraph(f'<b>{label}</b>', styles['Normal']),
                    Paragraph(str(value), styles['Normal'])
                ])

            details_table = Table(wrapped_details, colWidths=[40*mm, 130*mm])
            details_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(details_table)
            story.append(Spacer(1, 3*mm))

            status_items = []
            if event.get('is_organised'):
                status_items.append('Organised')
            if event.get('tickets_live'):
                status_items.append('Tickets Live')
            if event.get('is_advertised'):
                status_items.append('Advertised')

            if status_items:
                status_text = ' • '.join(status_items)
                story.append(Paragraph(f"<b>Status:</b> {status_text}", styles['Normal']))
                story.append(Spacer(1, 3*mm))

            if event.get('description'):
                description_html = event['description'].replace('\n', '<br/>')
                story.append(Paragraph(f"<b>Description:</b> {description_html}", styles['Normal']))
                story.append(Spacer(1, 3*mm))

            if i < len(events) - 1:
                story.append(Spacer(1, 3*mm))
                story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E6D9F2'),
                                       spaceBefore=0, spaceAfter=5*mm))
                story.append(Spacer(1, 3*mm))

        # Second pass build
        doc.build(story)

        return output_path
