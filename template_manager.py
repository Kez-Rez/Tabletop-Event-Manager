"""Template management functionality"""
from database import Database
from typing import Optional, List, Dict, Any

class TemplateManager:
    """Manages event template CRUD operations"""

    def __init__(self, db: Database):
        self.db = db

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Get all templates with related information"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                t.*,
                et.name as event_type_name,
                pf.name as format_name,
                pm.name as pairing_method_name,
                pa.name as pairing_app_name
            FROM event_templates t
            LEFT JOIN event_types et ON t.event_type_id = et.id
            LEFT JOIN playing_formats pf ON t.playing_format_id = pf.id
            LEFT JOIN pairing_methods pm ON t.pairing_method_id = pm.id
            LEFT JOIN pairing_apps pa ON t.pairing_app_id = pa.id
            ORDER BY t.name
        ''')

        templates = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return templates

    def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get a single template by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                t.*,
                et.name as event_type_name,
                pf.name as format_name,
                pm.name as pairing_method_name,
                pa.name as pairing_app_name
            FROM event_templates t
            LEFT JOIN event_types et ON t.event_type_id = et.id
            LEFT JOIN playing_formats pf ON t.playing_format_id = pf.id
            LEFT JOIN pairing_methods pm ON t.pairing_method_id = pm.id
            LEFT JOIN pairing_apps pa ON t.pairing_app_id = pa.id
            WHERE t.id = ?
        ''', (template_id,))

        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def create_template(self, template_data: Dict[str, Any]) -> int:
        """Create a new template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO event_templates (
                name, event_type_id, playing_format_id, pairing_method_id,
                pairing_app_id, max_capacity, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            template_data['name'],
            template_data.get('event_type_id'),
            template_data.get('playing_format_id'),
            template_data.get('pairing_method_id'),
            template_data.get('pairing_app_id'),
            template_data.get('max_capacity'),
            template_data.get('description')
        ))

        template_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return template_id

    def update_template(self, template_id: int, template_data: Dict[str, Any]):
        """Update an existing template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE event_templates SET
                name = ?,
                event_type_id = ?,
                playing_format_id = ?,
                pairing_method_id = ?,
                pairing_app_id = ?,
                max_capacity = ?,
                description = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            template_data['name'],
            template_data.get('event_type_id'),
            template_data.get('playing_format_id'),
            template_data.get('pairing_method_id'),
            template_data.get('pairing_app_id'),
            template_data.get('max_capacity'),
            template_data.get('description'),
            template_id
        ))

        conn.commit()
        conn.close()

    def delete_template(self, template_id: int):
        """Delete a template (cascades to checklist items)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM event_templates WHERE id = ?', (template_id,))
        conn.commit()
        conn.close()

    def get_template_checklist_items(self, template_id: int) -> List[Dict[str, Any]]:
        """Get checklist items for a template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                ci.*,
                cat.name as category_name
            FROM template_checklist_items ci
            LEFT JOIN checklist_categories cat ON ci.category_id = cat.id
            WHERE ci.template_id = ?
            ORDER BY cat.sort_order, ci.sort_order
        ''', (template_id,))

        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    def add_checklist_item(self, template_id: int, category_id: Optional[int], description: str, sort_order: int = 0, include_in_pdf: bool = True, show_on_dashboard: bool = False):
        """Add a checklist item to a template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO template_checklist_items (template_id, category_id, description, sort_order, include_in_pdf, show_on_dashboard)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (template_id, category_id, description, sort_order, 1 if include_in_pdf else 0, 1 if show_on_dashboard else 0))

        conn.commit()
        conn.close()

    def update_checklist_item(self, item_id: int, description: str, category_id: Optional[int] = None, include_in_pdf: bool = True, show_on_dashboard: bool = False):
        """Update a checklist item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE template_checklist_items
            SET description = ?, category_id = ?, include_in_pdf = ?, show_on_dashboard = ?
            WHERE id = ?
        ''', (description, category_id, 1 if include_in_pdf else 0, 1 if show_on_dashboard else 0, item_id))

        conn.commit()
        conn.close()

    def delete_checklist_item(self, item_id: int):
        """Delete a checklist item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM template_checklist_items WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()

    def get_checklist_categories(self) -> List[Dict[str, Any]]:
        """Get all checklist categories"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM checklist_categories ORDER BY sort_order')
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return categories

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

        # Checklist categories
        cursor.execute('SELECT * FROM checklist_categories ORDER BY sort_order')
        data['checklist_categories'] = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return data

    def count_events_using_template(self, template_id: int) -> int:
        """Count how many events use this template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM events WHERE template_id = ?', (template_id,))
        result = cursor.fetchone()
        conn.close()
        return result['count'] if result else 0

    # Template Ticket Tiers Management
    def get_template_ticket_tiers(self, template_id: int) -> List[Dict[str, Any]]:
        """Get all ticket tiers for a template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM template_ticket_tiers
            WHERE template_id = ?
            ORDER BY price
        ''', (template_id,))
        tickets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tickets

    def add_template_ticket_tier(self, template_id: int, tier_name: str, price: float, quantity_available: Optional[int] = None):
        """Add a ticket tier to a template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO template_ticket_tiers (template_id, tier_name, price, quantity_available)
            VALUES (?, ?, ?, ?)
        ''', (template_id, tier_name, price, quantity_available))
        conn.commit()
        conn.close()

    def update_template_ticket_tier(self, tier_id: int, tier_name: str, price: float, quantity_available: Optional[int] = None):
        """Update a template ticket tier"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE template_ticket_tiers
            SET tier_name = ?, price = ?, quantity_available = ?
            WHERE id = ?
        ''', (tier_name, price, quantity_available, tier_id))
        conn.commit()
        conn.close()

    def delete_template_ticket_tier(self, tier_id: int):
        """Delete a template ticket tier"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM template_ticket_tiers WHERE id = ?', (tier_id,))
        conn.commit()
        conn.close()

    # Template Prize Items Management
    def get_template_prize_items(self, template_id: int) -> List[Dict[str, Any]]:
        """Get all prize items for a template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM template_prize_items
            WHERE template_id = ?
            ORDER BY created_at
        ''', (template_id,))
        prizes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return prizes

    def add_template_prize_item(self, template_id: int, description: str, quantity: Optional[int] = None,
                                cost_per_item: Optional[float] = None, total_cost: Optional[float] = None,
                                supplier: Optional[str] = None):
        """Add a prize item to a template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO template_prize_items (template_id, description, quantity, cost_per_item, total_cost, supplier)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (template_id, description, quantity, cost_per_item, total_cost, supplier))
        conn.commit()
        conn.close()

    def update_template_prize_item(self, prize_id: int, description: str, quantity: Optional[int] = None,
                                   cost_per_item: Optional[float] = None, total_cost: Optional[float] = None,
                                   supplier: Optional[str] = None):
        """Update a template prize item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE template_prize_items
            SET description = ?, quantity = ?, cost_per_item = ?, total_cost = ?, supplier = ?
            WHERE id = ?
        ''', (description, quantity, cost_per_item, total_cost, supplier, prize_id))
        conn.commit()
        conn.close()

    def delete_template_prize_item(self, prize_id: int):
        """Delete a template prize item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM template_prize_items WHERE id = ?', (prize_id,))
        conn.commit()
        conn.close()

    # Template Notes Management
    def get_template_notes(self, template_id: int) -> List[Dict[str, Any]]:
        """Get all notes for a template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM template_notes
            WHERE template_id = ?
            ORDER BY created_at DESC
        ''', (template_id,))
        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return notes

    def add_template_note(self, template_id: int, note_text: str, include_in_printout: bool = False):
        """Add a note to a template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO template_notes (template_id, note_text, include_in_printout)
            VALUES (?, ?, ?)
        ''', (template_id, note_text, 1 if include_in_printout else 0))
        conn.commit()
        conn.close()

    def update_template_note(self, note_id: int, note_text: str, include_in_printout: bool = False):
        """Update a template note"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE template_notes
            SET note_text = ?, include_in_printout = ?
            WHERE id = ?
        ''', (note_text, 1 if include_in_printout else 0, note_id))
        conn.commit()
        conn.close()

    def delete_template_note(self, note_id: int):
        """Delete a template note"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM template_notes WHERE id = ?', (note_id,))
        conn.commit()
        conn.close()
