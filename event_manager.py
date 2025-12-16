"""Event management functionality"""
from database import Database
from datetime import datetime, time
from typing import Optional, List, Dict, Any

class EventManager:
    """Manages event CRUD operations"""

    def __init__(self, db: Database):
        self.db = db

    def get_all_events(self, include_completed: bool = True) -> List[Dict[str, Any]]:
        """Get all events with related information"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT
                e.*,
                et.name as event_type_name,
                pf.name as format_name,
                pm.name as pairing_method_name,
                pa.name as pairing_app_name,
                temp.name as template_name
            FROM events e
            LEFT JOIN event_types et ON e.event_type_id = et.id
            LEFT JOIN playing_formats pf ON e.playing_format_id = pf.id
            LEFT JOIN pairing_methods pm ON e.pairing_method_id = pm.id
            LEFT JOIN pairing_apps pa ON e.pairing_app_id = pa.id
            LEFT JOIN event_templates temp ON e.template_id = temp.id
        '''

        # Build WHERE clause
        where_conditions = ['e.is_deleted = 0']  # Always exclude deleted events
        if not include_completed:
            where_conditions.append('e.is_completed = 0')

        if where_conditions:
            query += ' WHERE ' + ' AND '.join(where_conditions)

        query += ' ORDER BY e.event_date ASC'

        cursor.execute(query)
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return events

    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get a single event by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                e.*,
                et.name as event_type_name,
                pf.name as format_name,
                pm.name as pairing_method_name,
                pa.name as pairing_app_name,
                temp.name as template_name
            FROM events e
            LEFT JOIN event_types et ON e.event_type_id = et.id
            LEFT JOIN playing_formats pf ON e.playing_format_id = pf.id
            LEFT JOIN pairing_methods pm ON e.pairing_method_id = pm.id
            LEFT JOIN pairing_apps pa ON e.pairing_app_id = pa.id
            LEFT JOIN event_templates temp ON e.template_id = temp.id
            WHERE e.id = ?
        ''', (event_id,))

        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def create_event(self, event_data: Dict[str, Any]) -> int:
        """Create a new event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO events (
                template_id, event_name, event_date, start_time, end_time,
                event_type_id, playing_format_id, pairing_method_id, pairing_app_id,
                max_capacity, tickets_available, description, tables_booked, is_organised, tickets_live, is_advertised,
                is_completed, include_attendees, number_of_rounds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data.get('template_id'),
            event_data['event_name'],
            event_data['event_date'],
            event_data.get('start_time'),
            event_data.get('end_time'),
            event_data.get('event_type_id'),
            event_data.get('playing_format_id'),
            event_data.get('pairing_method_id'),
            event_data.get('pairing_app_id'),
            event_data.get('max_capacity'),
            event_data.get('tickets_available'),
            event_data.get('description'),
            event_data.get('tables_booked', 0),
            event_data.get('is_organised', 0),
            event_data.get('tickets_live', 0),
            event_data.get('is_advertised', 0),
            event_data.get('is_completed', 0),
            event_data.get('include_attendees', 0),
            event_data.get('number_of_rounds')
        ))

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return event_id

    def update_event(self, event_id: int, event_data: Dict[str, Any]):
        """Update an existing event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE events SET
                event_name = ?,
                event_date = ?,
                start_time = ?,
                end_time = ?,
                event_type_id = ?,
                playing_format_id = ?,
                pairing_method_id = ?,
                pairing_app_id = ?,
                max_capacity = ?,
                tickets_available = ?,
                description = ?,
                tables_booked = ?,
                is_organised = ?,
                tickets_live = ?,
                is_advertised = ?,
                is_completed = ?,
                include_attendees = ?,
                number_of_rounds = ?,
                updated_at = ?
            WHERE id = ?
        ''', (
            event_data['event_name'],
            event_data['event_date'],
            event_data.get('start_time'),
            event_data.get('end_time'),
            event_data.get('event_type_id'),
            event_data.get('playing_format_id'),
            event_data.get('pairing_method_id'),
            event_data.get('pairing_app_id'),
            event_data.get('max_capacity'),
            event_data.get('tickets_available'),
            event_data.get('description'),
            event_data.get('tables_booked', 0),
            event_data.get('is_organised', 0),
            event_data.get('tickets_live', 0),
            event_data.get('is_advertised', 0),
            event_data.get('is_completed', 0),
            event_data.get('include_attendees', 0),
            event_data.get('number_of_rounds'),
            datetime.now(),
            event_id
        ))

        conn.commit()
        conn.close()

    def delete_event(self, event_id: int):
        """Soft delete an event (marks as deleted instead of removing)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE events
            SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (event_id,))
        conn.commit()
        conn.close()

    def get_deleted_events(self) -> List[Dict[str, Any]]:
        """Get all deleted events"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                e.*,
                et.name as event_type_name,
                pf.name as format_name,
                pm.name as pairing_method_name,
                pa.name as pairing_app_name,
                temp.name as template_name
            FROM events e
            LEFT JOIN event_types et ON e.event_type_id = et.id
            LEFT JOIN playing_formats pf ON e.playing_format_id = pf.id
            LEFT JOIN pairing_methods pm ON e.pairing_method_id = pm.id
            LEFT JOIN pairing_apps pa ON e.pairing_app_id = pa.id
            LEFT JOIN event_templates temp ON e.template_id = temp.id
            WHERE e.is_deleted = 1
            ORDER BY e.deleted_at DESC
        ''')
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return events

    def restore_event(self, event_id: int):
        """Restore a deleted event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE events
            SET is_deleted = 0, deleted_at = NULL
            WHERE id = ?
        ''', (event_id,))
        conn.commit()
        conn.close()

    def permanently_delete_event(self, event_id: int):
        """Permanently delete an event and all related data"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
        conn.close()

    def create_event_from_template(self, template_id: int, event_date: str, event_name: str = None) -> int:
        """Create a new event from a template"""
        template = self.get_template_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Get template feedback notes to add to new event
        feedback_notes = self.get_template_feedback(template_id)

        event_data = {
            'template_id': template_id,
            'event_name': event_name or template['name'],
            'event_date': event_date,
            'event_type_id': template['event_type_id'],
            'playing_format_id': template['playing_format_id'],
            'pairing_method_id': template['pairing_method_id'],
            'pairing_app_id': template['pairing_app_id'],
            'max_capacity': template['max_capacity'],
            'description': template['description']
        }

        event_id = self.create_event(event_data)

        # Copy template data to event
        self.copy_template_checklist(template_id, event_id)
        self.copy_template_ticket_tiers(template_id, event_id)
        self.copy_template_prize_items(template_id, event_id)
        self.copy_template_notes(template_id, event_id)

        # Add feedback notes from previous events
        for feedback in feedback_notes:
            self.add_event_note(event_id, f"Previous feedback: {feedback['feedback_text']}", include_in_printout=True)

        return event_id

    def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get a template by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM event_templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def copy_template_checklist(self, template_id: int, event_id: int):
        """Copy checklist items from template to event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM template_checklist_items
            WHERE template_id = ?
            ORDER BY sort_order
        ''', (template_id,))

        template_items = [dict(row) for row in cursor.fetchall()]

        for item in template_items:
            cursor.execute('''
                INSERT INTO event_checklist_items (
                    event_id, category_id, description, sort_order, include_in_pdf, show_on_dashboard
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (event_id, item['category_id'], item['description'], item['sort_order'],
                  item.get('include_in_pdf', 1), item.get('show_on_dashboard', 0)))

        conn.commit()
        conn.close()

    def copy_template_ticket_tiers(self, template_id: int, event_id: int):
        """Copy ticket tiers from template to event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM template_ticket_tiers
            WHERE template_id = ?
            ORDER BY price
        ''', (template_id,))

        template_tickets = [dict(row) for row in cursor.fetchall()]

        for ticket in template_tickets:
            cursor.execute('''
                INSERT INTO ticket_tiers (
                    event_id, tier_name, price, quantity_available, quantity_sold
                ) VALUES (?, ?, ?, ?, 0)
            ''', (event_id, ticket['tier_name'], ticket['price'], ticket.get('quantity_available')))

        conn.commit()
        conn.close()

    def copy_template_prize_items(self, template_id: int, event_id: int):
        """Copy prize items from template to event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM template_prize_items
            WHERE template_id = ?
            ORDER BY created_at
        ''', (template_id,))

        template_prizes = [dict(row) for row in cursor.fetchall()]

        for prize in template_prizes:
            cursor.execute('''
                INSERT INTO prize_items (
                    event_id, description, quantity, cost_per_item, total_cost, supplier, is_received, recipients, quantity_handed_out
                ) VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0)
            ''', (event_id, prize['description'], prize.get('quantity'), prize.get('cost_per_item'), prize.get('total_cost'), prize.get('supplier')))

        conn.commit()
        conn.close()

    def copy_template_notes(self, template_id: int, event_id: int):
        """Copy notes from template to event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM template_notes
            WHERE template_id = ?
            ORDER BY created_at DESC
        ''', (template_id,))

        template_notes = [dict(row) for row in cursor.fetchall()]

        for note in template_notes:
            cursor.execute('''
                INSERT INTO event_notes (
                    event_id, note_text, include_in_printout, send_to_template
                ) VALUES (?, ?, ?, 0)
            ''', (event_id, note['note_text'], note.get('include_in_printout', 0)))

        conn.commit()
        conn.close()

    def get_template_feedback(self, template_id: int) -> List[Dict[str, Any]]:
        """Get feedback notes from previous events using this template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM template_feedback
            WHERE template_id = ?
            ORDER BY created_at DESC
        ''', (template_id,))
        feedback = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return feedback

    def add_event_note(self, event_id: int, note_text: str, include_in_printout: bool = False):
        """Add a note to an event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO event_notes (event_id, note_text, include_in_printout)
            VALUES (?, ?, ?)
        ''', (event_id, note_text, include_in_printout))
        conn.commit()
        conn.close()

    def get_reference_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all reference data for dropdowns"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        data = {}

        # Event types
        cursor.execute('SELECT * FROM event_types ORDER BY name')
        data['event_types'] = [dict(row) for row in cursor.fetchall()]

        # Playing formats
        cursor.execute('SELECT * FROM playing_formats ORDER BY name')
        data['playing_formats'] = [dict(row) for row in cursor.fetchall()]

        # Pairing methods
        cursor.execute('SELECT * FROM pairing_methods ORDER BY name')
        data['pairing_methods'] = [dict(row) for row in cursor.fetchall()]

        # Pairing apps
        cursor.execute('SELECT * FROM pairing_apps ORDER BY name')
        data['pairing_apps'] = [dict(row) for row in cursor.fetchall()]

        # Templates
        cursor.execute('SELECT * FROM event_templates ORDER BY name')
        data['templates'] = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return data

    def calculate_labour_cost(self, event_id: int, staff_count: int = 1) -> float:
        """Calculate labour cost based on event timing and award rates"""
        event = self.get_event_by_id(event_id)
        if not event or not event['start_time'] or not event['end_time']:
            return 0.0

        # Parse times
        start = datetime.strptime(event['start_time'], '%H:%M:%S').time()
        end = datetime.strptime(event['end_time'], '%H:%M:%S').time()

        # Calculate hours
        start_dt = datetime.combine(datetime.today(), start)
        end_dt = datetime.combine(datetime.today(), end)
        if end_dt < start_dt:  # Event goes past midnight
            end_dt = datetime.combine(datetime.today().replace(day=datetime.today().day + 1), end)

        hours_worked = (end_dt - start_dt).total_seconds() / 3600

        # Determine day of week
        event_date = datetime.strptime(event['event_date'], '%Y-%m-%d')
        day_of_week = event_date.weekday()  # 0 = Monday, 5 = Saturday, 6 = Sunday

        # Get appropriate rate
        if day_of_week == 6:  # Sunday
            rate = float(self.db.get_setting('sunday_rate') or 35.0)
        elif day_of_week == 5:  # Saturday
            rate = float(self.db.get_setting('saturday_rate') or 30.0)
        else:  # Weekday - check if after 6pm
            if start.hour >= 18:
                rate = float(self.db.get_setting('weekday_after_6pm_rate') or 25.5)
            else:
                rate = float(self.db.get_setting('weekday_after_6pm_rate') or 25.5)  # Default to same rate

        total_cost = hours_worked * rate * staff_count

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Check if labour cost already exists
        cursor.execute('SELECT id FROM labour_costs WHERE event_id = ?', (event_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute('''
                UPDATE labour_costs
                SET staff_count = ?, hours_worked = ?, hourly_rate = ?, total_cost = ?
                WHERE event_id = ?
            ''', (staff_count, hours_worked, rate, total_cost, event_id))
        else:
            cursor.execute('''
                INSERT INTO labour_costs (event_id, staff_count, hours_worked, hourly_rate, total_cost)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_id, staff_count, hours_worked, rate, total_cost))

        conn.commit()
        conn.close()

        return total_cost

    def get_labour_costs(self, event_id: int) -> List[Dict[str, Any]]:
        """Get all labour cost entries for an event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM labour_costs
            WHERE event_id = ?
            ORDER BY created_at
        ''', (event_id,))

        labour_costs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return labour_costs

    def add_labour_cost_entry(self, event_id: int, staff_name: str = None,
                             hours_worked: float = 0, rate_type: str = 'weekday',
                             hourly_rate: float = 0, work_status: str = 'full') -> int:
        """Add a new labour cost entry for an event"""
        total_cost = hours_worked * hourly_rate

        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO labour_costs
            (event_id, staff_name, hours_worked, rate_type, hourly_rate, work_status, total_cost, staff_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (event_id, staff_name, hours_worked, rate_type, hourly_rate, work_status, total_cost))

        labour_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return labour_id

    def update_labour_cost_entry(self, labour_id: int, staff_name: str = None,
                                 hours_worked: float = 0, rate_type: str = 'weekday',
                                 hourly_rate: float = 0, work_status: str = 'full'):
        """Update an existing labour cost entry"""
        total_cost = hours_worked * hourly_rate

        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE labour_costs
            SET staff_name = ?, hours_worked = ?, rate_type = ?, hourly_rate = ?,
                work_status = ?, total_cost = ?
            WHERE id = ?
        ''', (staff_name, hours_worked, rate_type, hourly_rate, work_status, total_cost, labour_id))

        conn.commit()
        conn.close()

    def delete_labour_cost_entry(self, labour_id: int):
        """Delete a labour cost entry"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM labour_costs WHERE id = ?', (labour_id,))
        conn.commit()
        conn.close()

    def get_total_labour_cost(self, event_id: int) -> float:
        """Calculate total labour cost for an event from all entries"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT SUM(total_cost) as total FROM labour_costs
            WHERE event_id = ?
        ''', (event_id,))

        result = cursor.fetchone()
        conn.close()

        return result['total'] if result and result['total'] else 0.0
