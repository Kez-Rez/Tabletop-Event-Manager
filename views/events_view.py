"""Events view UI"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
from event_manager import EventManager
from pdf_generator import EventPDFGenerator
from views.event_dialogs import TicketTierDialog, PrizeDialog, NoteDialog, ChecklistItemDialog
from datetime import datetime
from typing import Optional
import os

class EventsView(ctk.CTkFrame):
    """Events list and management view"""

    def __init__(self, parent, db, navigation_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.event_manager = EventManager(db)
        self.navigation_manager = navigation_manager

        self.configure(fg_color="#F5F0F6")

        # Create header
        self.create_header()

        # Create events list
        self.create_events_list()

        # Load events
        self.load_events()

    def create_header(self):
        """Create the header with title and buttons"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Events",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(side="left")

        # Buttons frame
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.pack(side="right")

        # New event button
        btn_new = ctk.CTkButton(
            buttons_frame,
            text="+ New Event",
            command=self.show_new_event_dialog,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=140,
            height=40
        )
        btn_new.pack(side="left", padx=5)

        # From template button
        btn_template = ctk.CTkButton(
            buttons_frame,
            text="From Template",
            command=self.show_template_selection_dialog,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=140,
            height=40
        )
        btn_template.pack(side="left", padx=5)

        # Export All Events PDF button
        btn_export_pdf = ctk.CTkButton(
            buttons_frame,
            text="Export All Events PDF",
            command=self.export_all_events_pdf,
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            text_color="white",
            width=160,
            height=40
        )
        btn_export_pdf.pack(side="left", padx=5)

        # Filter frame
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(0, 20))

        # Show completed checkbox - default unchecked, state persists during session
        self.show_completed_var = ctk.BooleanVar(value=False)
        chk_completed = ctk.CTkCheckBox(
            filter_frame,
            text="Show Completed Events",
            variable=self.show_completed_var,
            command=self.load_events,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            checkmark_color="white"
        )
        chk_completed.pack(side="left")

    def create_events_list(self):
        """Create the scrollable events list"""
        # Container frame with border
        list_container = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        list_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Scrollable frame
        self.events_scroll = ctk.CTkScrollableFrame(
            list_container,
            fg_color="white",
            corner_radius=10
        )
        self.events_scroll.pack(fill="both", expand=True, padx=2, pady=2)

    def refresh(self):
        """Refresh the view (called when navigating back)"""
        self.load_events()

    def load_events(self):
        """Load and display events"""
        # Clear existing widgets
        for widget in self.events_scroll.winfo_children():
            widget.destroy()

        # Get events
        events = self.event_manager.get_all_events(
            include_completed=self.show_completed_var.get()
        )

        if not events:
            # No events message
            no_events = ctk.CTkLabel(
                self.events_scroll,
                text="No events yet. Create your first event!",
                font=ctk.CTkFont(size=16),
                text_color="#999999"
            )
            no_events.pack(pady=40)
            return

        # Display events
        for event in events:
            self.create_event_card(event)

    def create_event_card(self, event: dict):
        """Create a card for an event"""
        # Card frame
        card = ctk.CTkFrame(
            self.events_scroll,
            fg_color="#F9F5FA",
            corner_radius=8,
            border_width=1,
            border_color="#E6D9F2"
        )
        card.pack(fill="x", padx=10, pady=5)

        # Main content frame
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        # Left side - Event info
        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)

        # Event name
        name_label = ctk.CTkLabel(
            left_frame,
            text=event['event_name'],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        )
        name_label.pack(anchor="w")

        # Event details
        details_text = []

        # Format date nicely
        try:
            event_date = datetime.strptime(event['event_date'], '%Y-%m-%d')
            formatted_date = event_date.strftime('%A, %d %B %Y')
            details_text.append(formatted_date)
        except:
            details_text.append(event['event_date'])

        if event.get('event_type_name'):
            details_text.append(event['event_type_name'])
        if event.get('format_name'):
            details_text.append(event['format_name'])
        if event.get('pairing_method_name'):
            details_text.append(event['pairing_method_name'])

        details_label = ctk.CTkLabel(
            left_frame,
            text=" • ".join(details_text),
            font=ctk.CTkFont(size=15),
            text_color="#666666",
            anchor="w"
        )
        details_label.pack(anchor="w", pady=(5, 0))

        # Tables booked
        if event.get('tables_booked'):
            tables_label = ctk.CTkLabel(
                left_frame,
                text=f"Tables Booked: {event['tables_booked']}",
                font=ctk.CTkFont(size=15),
                text_color="#8B5FBF",
                anchor="w"
            )
            tables_label.pack(anchor="w", pady=(5, 0))

        # Status badges frame
        badges_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        badges_frame.pack(anchor="w", pady=(10, 0))

        # Status badges
        if event.get('is_organised'):
            self.create_badge(badges_frame, "Organised", "#4CAF50")
        if event.get('tickets_live'):
            self.create_badge(badges_frame, "Tickets Live", "#2196F3")
        if event.get('is_advertised'):
            self.create_badge(badges_frame, "Advertised", "#FF9800")
        if event.get('is_completed'):
            self.create_badge(badges_frame, "Completed", "#9C27B0")

        # Incomplete checklist items
        incomplete_items = self.get_incomplete_checklist_items(event['id'])
        if incomplete_items:
            checklist_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
            checklist_frame.pack(anchor="w", pady=(10, 0))

            ctk.CTkLabel(
                checklist_frame,
                text="To Do:",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#999999",
                anchor="w"
            ).pack(anchor="w")

            for item in incomplete_items[:3]:  # Show max 3 items
                item_label = ctk.CTkLabel(
                    checklist_frame,
                    text=f"☐ {item['description']}",
                    font=ctk.CTkFont(size=15),
                    text_color="#AAAAAA",
                    anchor="w"
                )
                item_label.pack(anchor="w", padx=(10, 0))

            if len(incomplete_items) > 3:
                more_label = ctk.CTkLabel(
                    checklist_frame,
                    text=f"   +{len(incomplete_items) - 3} more...",
                    font=ctk.CTkFont(size=15),
                    text_color="#CCCCCC",
                    anchor="w"
                )
                more_label.pack(anchor="w", padx=(10, 0))

        # Right side - Actions
        right_frame = ctk.CTkFrame(content, fg_color="transparent")
        right_frame.pack(side="right")

        # View/Edit button
        btn_edit = ctk.CTkButton(
            right_frame,
            text="View/Edit",
            command=lambda e=event: self.show_event_details(e['id']),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=100
        )
        btn_edit.pack(pady=2)

        # Delete button
        btn_delete = ctk.CTkButton(
            right_frame,
            text="Delete",
            command=lambda e=event: self.delete_event(e['id'], e['event_name']),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=100
        )
        btn_delete.pack(pady=2)

        # Make into Template button
        btn_template = ctk.CTkButton(
            right_frame,
            text="Make Template",
            command=lambda e=event: self.make_into_template(e['id']),
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            text_color="white",
            width=100
        )
        btn_template.pack(pady=2)

    def create_badge(self, parent, text: str, color: str):
        """Create a status badge"""
        badge = ctk.CTkLabel(
            parent,
            text=text,
            fg_color=color,
            text_color="white",
            corner_radius=4,
            font=ctk.CTkFont(size=15),
            padx=8,
            pady=2
        )
        badge.pack(side="left", padx=(0, 5))

    def get_incomplete_checklist_items(self, event_id: int):
        """Get incomplete checklist items for an event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM event_checklist_items
            WHERE event_id = ? AND is_completed = 0
            ORDER BY sort_order
        ''', (event_id,))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    def show_new_event_dialog(self):
        """Show dialog to create a new event"""
        dialog = EventEditDialog(self, self.db, None)
        self.wait_window(dialog)
        self.load_events()

    def show_template_selection_dialog(self):
        """Show dialog to select a template and create event"""
        dialog = TemplateSelectionDialog(self, self.db, self.event_manager)
        self.wait_window(dialog)
        if dialog.created_event_id:
            self.load_events()
            messagebox.showinfo("Event Created", f"Event '{dialog.created_event_name}' has been created from template!")

    def show_event_details(self, event_id: int):
        """Show event details/edit dialog"""
        dialog = EventEditDialog(self, self.db, event_id)
        self.wait_window(dialog)
        self.load_events()

    def delete_event(self, event_id: int, event_name: str):
        """Delete an event after confirmation"""
        result = messagebox.askyesno(
            "Move to Trash",
            f"Move '{event_name}' to Deleted Events?\n\nYou can restore it later from the Deleted Events page."
        )
        if result:
            self.event_manager.delete_event(event_id)
            self.load_events()
            messagebox.showinfo("Moved to Trash", f"'{event_name}' has been moved to Deleted Events.\n\nYou can restore it from the Deleted Events page.")

    def make_into_template(self, event_id: int):
        """Convert an event into a template"""
        from template_manager import TemplateManager

        # Get event data
        event = self.event_manager.get_event_by_id(event_id)
        if not event:
            messagebox.showerror("Error", "Event not found")
            return

        # Ask for template name
        dialog = ctk.CTkInputDialog(
            text=f"Create template from '{event['event_name']}'?\n\nEnter template name:",
            title="Create Template"
        )
        template_name = dialog.get_input()

        if not template_name:
            return  # User cancelled

        try:
            # Create template
            template_manager = TemplateManager(self.db)

            template_data = {
                'name': template_name,
                'event_type_id': event.get('event_type_id'),
                'playing_format_id': event.get('playing_format_id'),
                'pairing_method_id': event.get('pairing_method_id'),
                'pairing_app_id': event.get('pairing_app_id'),
                'max_capacity': event.get('max_capacity'),
                'description': event.get('description')
            }

            template_id = template_manager.create_template(template_data)

            # Copy event data to template
            self.copy_event_to_template(event_id, template_id)

            messagebox.showinfo(
                "Success",
                f"Template '{template_name}' created successfully!\n\nAll event details, checklists, tickets, prizes, and notes have been copied."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create template: {str(e)}")

    def copy_event_to_template(self, event_id: int, template_id: int):
        """Copy event checklist, tickets, prizes, and notes to template"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Copy checklist items
        cursor.execute('''
            SELECT category_id, description, sort_order, include_in_pdf, show_on_dashboard
            FROM event_checklist_items
            WHERE event_id = ?
            ORDER BY sort_order
        ''', (event_id,))
        checklist_items = [dict(row) for row in cursor.fetchall()]

        for item in checklist_items:
            cursor.execute('''
                INSERT INTO template_checklist_items (template_id, category_id, description, sort_order, include_in_pdf, show_on_dashboard)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (template_id, item['category_id'], item['description'], item['sort_order'],
                  item.get('include_in_pdf', 1), item.get('show_on_dashboard', 0)))

        # Copy ticket tiers
        cursor.execute('''
            SELECT tier_name, price, quantity_available
            FROM ticket_tiers
            WHERE event_id = ?
            ORDER BY price
        ''', (event_id,))
        tickets = [dict(row) for row in cursor.fetchall()]

        for ticket in tickets:
            cursor.execute('''
                INSERT INTO template_ticket_tiers (template_id, tier_name, price, quantity_available)
                VALUES (?, ?, ?, ?)
            ''', (template_id, ticket['tier_name'], ticket['price'], ticket.get('quantity_available')))

        # Copy prize items (both prizes and materials)
        cursor.execute('''
            SELECT description, quantity, cost_per_item, total_cost
            FROM prize_items
            WHERE event_id = ?
            ORDER BY created_at
        ''', (event_id,))
        prizes = [dict(row) for row in cursor.fetchall()]

        for prize in prizes:
            cursor.execute('''
                INSERT INTO template_prize_items (template_id, description, quantity, cost_per_item, total_cost, supplier)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (template_id, prize['description'], prize.get('quantity'), prize.get('cost_per_item'),
                  prize.get('total_cost'), None))

        # Copy notes (only those marked for templates or general notes)
        cursor.execute('''
            SELECT note_text, show_in_notes_tab, include_in_printout
            FROM event_notes
            WHERE event_id = ?
            ORDER BY created_at DESC
        ''', (event_id,))
        notes = [dict(row) for row in cursor.fetchall()]

        for note in notes:
            cursor.execute('''
                INSERT INTO template_notes (template_id, note_text, include_in_printout)
                VALUES (?, ?, ?)
            ''', (template_id, note['note_text'], note.get('include_in_printout', 0)))

        conn.commit()
        conn.close()

    def export_all_events_pdf(self):
        """Export all upcoming events to a printable PDF"""
        try:
            # Create PDF generator
            pdf_gen = EventPDFGenerator(self.db)

            # Ask user where to save the PDF
            output_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"upcoming_events_{datetime.now().strftime('%Y%m%d')}.pdf"
            )

            if not output_path:
                return  # User cancelled

            # Generate the PDF
            result_path = pdf_gen.generate_upcoming_events_list(output_path)

            # Show success message
            messagebox.showinfo(
                "PDF Generated",
                f"Upcoming events PDF has been generated successfully!\n\nSaved to:\n{result_path}"
            )

            # Ask if user wants to open the file
            if messagebox.askyesno("Open PDF", "Would you like to open the PDF now?"):
                os.startfile(result_path)

        except ValueError as e:
            # No upcoming events
            messagebox.showwarning("No Events", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF:\n{str(e)}")


class TemplateSelectionDialog(ctk.CTkToplevel):
    """Dialog for selecting a template and creating an event"""

    def __init__(self, parent, db, event_manager):
        super().__init__(parent)

        self.db = db
        self.event_manager = event_manager
        self.created_event_id = None
        self.created_event_name = None
        self.selected_template = None

        # Configure window
        self.title("Create Event from Template")
        self.geometry("600x500")
        self.minsize(500, 400)  # Set minimum size for resizing
        self.configure(fg_color="#F5F0F6")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Load templates
        self.templates = self.load_templates()

        if not self.templates:
            messagebox.showwarning("No Templates", "No templates available. Please create a template first.")
            self.destroy()
            return

        self.create_ui()

    def load_templates(self):
        """Load all available templates"""
        ref_data = self.event_manager.get_reference_data()
        return ref_data.get('templates', [])

    def create_ui(self):
        """Create the user interface"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Select a Template",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(pady=(20, 10))

        # Instructions
        instructions = ctk.CTkLabel(
            self,
            text="Choose a template to create a new event with its settings and checklist",
            font=ctk.CTkFont(size=15),
            text_color="#666666",
            wraplength=500
        )
        instructions.pack(pady=(0, 20))

        # Templates list
        list_frame = ctk.CTkFrame(self, fg_color="white")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Scrollable frame for templates
        scroll = ctk.CTkScrollableFrame(list_frame, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Create a button for each template
        for template in self.templates:
            template_card = ctk.CTkFrame(
                scroll,
                fg_color="#F5F0F6",
                border_width=2,
                border_color="#C5A8D9"
            )
            template_card.pack(fill="x", padx=5, pady=5)

            # Template name
            name_label = ctk.CTkLabel(
                template_card,
                text=template['name'],
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#4A2D5E",
                anchor="w"
            )
            name_label.pack(anchor="w", padx=15, pady=(10, 5))

            # Template description (if available)
            if template.get('description'):
                desc_label = ctk.CTkLabel(
                    template_card,
                    text=template['description'],
                    font=ctk.CTkFont(size=15),
                    text_color="#666666",
                    anchor="w",
                    wraplength=500
                )
                desc_label.pack(anchor="w", padx=15, pady=(0, 5))

            # Select button
            select_btn = ctk.CTkButton(
                template_card,
                text="Use This Template",
                command=lambda t=template: self.select_template(t),
                fg_color="#8B5FBF",
                hover_color="#7A4FB0",
                text_color="white",
                width=150
            )
            select_btn.pack(anchor="e", padx=15, pady=(0, 10))

        # Cancel button
        cancel_btn = ctk.CTkButton(
            self,
            text="Cancel",
            command=self.destroy,
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=120
        )
        cancel_btn.pack(pady=(0, 20))

    def select_template(self, template):
        """Handle template selection"""
        self.selected_template = template

        # Create a dialog to get event date and name
        date_dialog = EventFromTemplateDialog(self, template)
        self.wait_window(date_dialog)

        if date_dialog.event_date:
            try:
                # Create event from template
                self.created_event_id = self.event_manager.create_event_from_template(
                    template['id'],
                    date_dialog.event_date,
                    date_dialog.event_name
                )
                self.created_event_name = date_dialog.event_name or template['name']
                self.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create event from template:\n{str(e)}")


class EventFromTemplateDialog(ctk.CTkToplevel):
    """Dialog to get event date and optional custom name"""

    def __init__(self, parent, template):
        super().__init__(parent)

        self.template = template
        self.event_date = None
        self.event_name = None

        # Configure window
        self.title("Event Details")
        self.geometry("500x350")
        self.configure(fg_color="#F5F0F6")

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.create_ui()

    def create_ui(self):
        """Create the user interface"""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text=f"Creating Event from:\n{self.template['name']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(pady=(0, 20))

        # Event date
        date_label = ctk.CTkLabel(
            main_frame,
            text="Event Date *",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        )
        date_label.pack(anchor="w", pady=(10, 5))

        self.date_entry = DateEntry(
            main_frame,
            background='#C5A8D9',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.date_entry.pack(fill="x", pady=(0, 15))

        # Event name (optional)
        name_label = ctk.CTkLabel(
            main_frame,
            text="Event Name (leave blank to use template name)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        )
        name_label.pack(anchor="w", pady=(10, 5))

        self.name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text=self.template['name'],
            height=35
        )
        self.name_entry.pack(fill="x", pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(20, 0))

        create_btn = ctk.CTkButton(
            button_frame,
            text="Create Event",
            command=self.create_event,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=140
        )
        create_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=140
        )
        cancel_btn.pack(side="left", padx=5)

    def create_event(self):
        """Validate and create event"""
        # Get date
        date_str = self.date_entry.get_date().strftime('%Y-%m-%d')
        self.event_date = date_str

        # Get custom name if provided
        custom_name = self.name_entry.get().strip()
        if custom_name:
            self.event_name = custom_name
        else:
            self.event_name = self.template['name']

        self.destroy()


class EventEditDialog(ctk.CTkToplevel):
    """Dialog for creating/editing events"""

    def __init__(self, parent, db, event_id: Optional[int] = None):
        super().__init__(parent)

        self.db = db
        self.event_manager = EventManager(db)
        self.event_id = event_id
        self.event_data = None
        self.analysis_data = None

        # Configure window
        if event_id:
            self.title("Edit Event")
            self.event_data = self.event_manager.get_event_by_id(event_id)
            # Load analysis data if event is completed
            if self.event_data and self.event_data.get('is_completed'):
                self.analysis_data = self.load_analysis_data()
        else:
            self.title("New Event")

        self.geometry("800x900")
        self.minsize(600, 600)  # Set minimum size for resizing
        self.configure(fg_color="#F5F0F6")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Create tabbed interface
        self.create_tabs()

        # Load reference data
        self.ref_data = self.event_manager.get_reference_data()
        self.populate_dropdowns()

        # If editing, populate fields
        if self.event_data:
            self.populate_fields()

    def load_analysis_data(self):
        """Load post-event analysis data if it exists"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM event_analysis WHERE event_id = ?', (self.event_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def create_tabs(self):
        """Create tabbed interface"""
        # Create tab view
        self.tabview = ctk.CTkTabview(self, fg_color="#F5F0F6")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        # Add tabs
        self.tab_details = self.tabview.add("Event Details")

        # Only show additional tabs for existing events
        if self.event_id:
            self.tab_tickets = self.tabview.add("Ticket Tiers")
            self.tab_prizes = self.tabview.add("Prize Support and Materials")
            self.tab_players = self.tabview.add("Players")
            self.tab_checklist = self.tabview.add("Checklist")
            self.tab_notes = self.tabview.add("Notes")
            self.tab_pre_event = self.tabview.add("Pre-Event Analysis")
            self.tab_post_event = self.tabview.add("Post-Event Analysis")

        # Create content for each tab
        self.create_details_tab()

        if self.event_id:
            self.create_tickets_tab()
            self.create_prizes_tab()
            self.create_players_tab()
            self.create_checklist_tab()
            self.create_notes_tab()
            self.create_pre_event_tab()
            self.create_post_event_tab()

        # Save/Cancel buttons at bottom (outside tabs)
        self.create_buttons()

    def create_buttons(self):
        """Create save/cancel buttons"""
        # Destroy existing button frame if it exists to prevent duplicates
        if hasattr(self, 'button_frame') and self.button_frame.winfo_exists():
            self.button_frame.destroy()

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Print PDF button (only for existing events)
        if self.event_id:
            btn_print = ctk.CTkButton(
                self.button_frame,
                text="Print Event Sheet",
                command=self.print_event_sheet,
                fg_color="#C5A8D9",
                hover_color="#B491CC",
                text_color="#4A2D5E",
                height=40
            )
            btn_print.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_cancel = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            self.button_frame,
            text="Save Event",
            command=self.save_event,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def create_details_tab(self):
        """Create the event details tab"""
        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(self.tab_details, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Completion status section (if event is completed)
        if self.event_data and self.event_data.get('is_completed'):
            completion_banner = ctk.CTkFrame(scroll, fg_color="#E8F5E9", corner_radius=8, border_width=2, border_color="#81C784")
            completion_banner.pack(fill="x", pady=(0, 20))

            content = ctk.CTkFrame(completion_banner, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=15)

            # Left side - completion badge
            left_side = ctk.CTkFrame(content, fg_color="transparent")
            left_side.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                left_side,
                text="✓ This event is marked as completed",
                text_color="#2E7D32",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
                left_side,
                text="To edit event details, reopen the event first",
                text_color="#558B2F",
                font=ctk.CTkFont(size=13)
            ).pack(anchor="w", pady=(5, 0))

            # Right side - reopen button
            ctk.CTkButton(
                content,
                text="Reopen Event",
                command=self.mark_event_incomplete,
                fg_color="#8B5FBF",
                hover_color="#7A4FB0",
                text_color="white",
                width=140,
                height=36,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="right")

        # Event Name
        ctk.CTkLabel(scroll, text="Event Name *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_name = ctk.CTkEntry(scroll, placeholder_text="e.g., MTG Commander Night")
        self.entry_name.pack(fill="x", pady=(0, 15))

        # Event Date
        ctk.CTkLabel(scroll, text="Event Date *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_date = DateEntry(scroll, selectmode='day', date_pattern='yyyy-mm-dd',
                                    background='#8B5FBF', foreground='white', borderwidth=2)
        self.entry_date.pack(fill="x", pady=(0, 15))

        # Time frame
        time_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        time_frame.pack(fill="x", pady=(0, 15))

        # Start time
        left_time = ctk.CTkFrame(time_frame, fg_color="transparent")
        left_time.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(left_time, text="Start Time", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_start_time = ctk.CTkEntry(left_time, placeholder_text="HH:MM (e.g., 18:00)")
        self.entry_start_time.pack(fill="x")

        # End time
        right_time = ctk.CTkFrame(time_frame, fg_color="transparent")
        right_time.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(right_time, text="End Time", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_end_time = ctk.CTkEntry(right_time, placeholder_text="HH:MM (e.g., 22:00)")
        self.entry_end_time.pack(fill="x")

        # Event Type
        ctk.CTkLabel(scroll, text="Event Type", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.combo_event_type = ctk.CTkComboBox(scroll, values=[""], state="normal")
        self.combo_event_type.set("")
        self.combo_event_type.pack(fill="x", pady=(0, 15))

        # Playing Format
        ctk.CTkLabel(scroll, text="Playing Format", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.combo_format = ctk.CTkComboBox(scroll, values=[""], state="normal")
        self.combo_format.set("")
        self.combo_format.pack(fill="x", pady=(0, 15))

        # Pairing Method
        ctk.CTkLabel(scroll, text="Pairing Method", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.combo_pairing_method = ctk.CTkComboBox(scroll, values=[""], state="normal")
        self.combo_pairing_method.set("")
        self.combo_pairing_method.pack(fill="x", pady=(0, 15))

        # Pairing App
        ctk.CTkLabel(scroll, text="Pairing App", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.combo_pairing_app = ctk.CTkComboBox(scroll, values=[""], state="normal")
        self.combo_pairing_app.set("")
        self.combo_pairing_app.pack(fill="x", pady=(0, 15))

        # Capacity frame
        capacity_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        capacity_frame.pack(fill="x", pady=(0, 15))

        # Tickets Available (now on left)
        left_capacity = ctk.CTkFrame(capacity_frame, fg_color="transparent")
        left_capacity.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(left_capacity, text="Tickets Available", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_tickets_available = ctk.CTkEntry(left_capacity, placeholder_text="e.g., 24")
        self.entry_tickets_available.pack(fill="x")

        # Max Capacity (now on right)
        right_capacity = ctk.CTkFrame(capacity_frame, fg_color="transparent")
        right_capacity.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(right_capacity, text="Maximum Capacity", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_capacity = ctk.CTkEntry(right_capacity, placeholder_text="e.g., 24")
        self.entry_capacity.pack(fill="x")

        # Tables Booked
        ctk.CTkLabel(scroll, text="Tables Booked", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_tables_booked = ctk.CTkEntry(scroll, placeholder_text="e.g., 5")
        self.entry_tables_booked.pack(fill="x", pady=(0, 15))

        # Description
        ctk.CTkLabel(scroll, text="Description", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.text_description = ctk.CTkTextbox(scroll, height=100)
        self.text_description.pack(fill="x", pady=(0, 15))

        # Status checkboxes
        ctk.CTkLabel(scroll, text="Status", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))

        self.var_organised = ctk.BooleanVar()
        ctk.CTkCheckBox(
            scroll,
            text="Fully Organised",
            variable=self.var_organised,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        ).pack(anchor="w", pady=2)

        self.var_tickets_live = ctk.BooleanVar()
        ctk.CTkCheckBox(
            scroll,
            text="Tickets Live",
            variable=self.var_tickets_live,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        ).pack(anchor="w", pady=2)

        self.var_advertised = ctk.BooleanVar()
        ctk.CTkCheckBox(
            scroll,
            text="Advertised",
            variable=self.var_advertised,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        ).pack(anchor="w", pady=2)

    def create_tickets_tab(self):
        """Create the ticket tiers management tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_tickets, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            scroll,
            text="Ticket Tiers",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 10))

        # Add button
        btn_add = ctk.CTkButton(
            scroll,
            text="+ Add Ticket Tier",
            command=self.add_ticket_tier,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=150
        )
        btn_add.pack(anchor="w", pady=(0, 15))

        # Tickets list frame
        self.tickets_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.tickets_list_frame.pack(fill="both", expand=True)

        # Load existing tickets
        self.refresh_tickets_list()

    def refresh_tickets_list(self):
        """Refresh the ticket tiers list"""
        # Clear existing widgets
        for widget in self.tickets_list_frame.winfo_children():
            widget.destroy()

        # Get tickets
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM ticket_tiers
            WHERE event_id = ?
            ORDER BY price
        ''', (self.event_id,))
        tickets = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not tickets:
            ctk.CTkLabel(
                self.tickets_list_frame,
                text="No ticket tiers yet. Click 'Add Ticket Tier' to create one.",
                text_color="#999999",
                font=ctk.CTkFont()
            ).pack(pady=20)
            return

        # Display tickets
        for ticket in tickets:
            self.create_ticket_card(ticket)

    def create_ticket_card(self, ticket):
        """Create a card for a ticket tier"""
        card = ctk.CTkFrame(
            self.tickets_list_frame,
            fg_color="#F9F5FA",
            corner_radius=8,
            border_width=1,
            border_color="#E6D9F2"
        )
        card.pack(fill="x", pady=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)

        # Left side - info
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            left,
            text=ticket['tier_name'],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w")

        info_text = f"Price: ${ticket['price']:.2f} | Available: {ticket['quantity_available']} | Sold: {ticket['quantity_sold']}"
        ctk.CTkLabel(
            left,
            text=info_text,
            text_color="#666666"
        ).pack(anchor="w")

        # Right side - buttons
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")

        btn_edit = ctk.CTkButton(
            right,
            text="Edit",
            command=lambda t=ticket: self.edit_ticket_tier(t),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=80
        )
        btn_edit.pack(side="left", padx=2)

        btn_delete = ctk.CTkButton(
            right,
            text="Delete",
            command=lambda t=ticket: self.delete_ticket_tier(t),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=80
        )
        btn_delete.pack(side="left", padx=2)

    def add_ticket_tier(self):
        """Show dialog to add a new ticket tier"""
        dialog = TicketTierDialog(self, self.db, self.event_id)
        self.wait_window(dialog)
        self.refresh_tickets_list()

    def edit_ticket_tier(self, ticket):
        """Show dialog to edit a ticket tier"""
        dialog = TicketTierDialog(self, self.db, self.event_id, ticket)
        self.wait_window(dialog)
        self.refresh_tickets_list()

    def delete_ticket_tier(self, ticket):
        """Delete a ticket tier"""
        if messagebox.askyesno("Confirm Delete", f"Delete ticket tier '{ticket['tier_name']}'?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM ticket_tiers WHERE id = ?', (ticket['id'],))
            conn.commit()
            conn.close()
            self.refresh_tickets_list()

    def create_prizes_tab(self):
        """Create the prize support management tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_prizes, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            scroll,
            text="Prize Support and Materials",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 10))

        # Add button
        btn_add = ctk.CTkButton(
            scroll,
            text="+ Add Prize",
            command=self.add_prize,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=150
        )
        btn_add.pack(anchor="w", pady=(0, 15))

        # Prizes list frame
        self.prizes_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.prizes_list_frame.pack(fill="both", expand=True)

        # Load existing prizes
        self.refresh_prizes_list()

    def refresh_prizes_list(self):
        """Refresh the prizes list"""
        # Clear existing widgets
        for widget in self.prizes_list_frame.winfo_children():
            widget.destroy()

        # Get prizes
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM prize_items
            WHERE event_id = ?
            ORDER BY created_at
        ''', (self.event_id,))
        prizes = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not prizes:
            ctk.CTkLabel(
                self.prizes_list_frame,
                text="No prizes yet. Click 'Add Prize' to add one.",
                text_color="#999999",
                font=ctk.CTkFont()
            ).pack(pady=20)
            return

        # Display prizes
        for prize in prizes:
            self.create_prize_card(prize)

    def create_prize_card(self, prize):
        """Create a card for a prize"""
        card = ctk.CTkFrame(
            self.prizes_list_frame,
            fg_color="#F9F5FA",
            corner_radius=8,
            border_width=1,
            border_color="#E6D9F2"
        )
        card.pack(fill="x", pady=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)

        # Left side - info
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            left,
            text=prize['description'],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E",
            wraplength=450,
            justify="left"
        ).pack(anchor="w")

        info_parts = []
        if prize['quantity']:
            info_parts.append(f"Qty: {prize['quantity']}")
        if prize['cost_per_item']:
            info_parts.append(f"Cost each: ${prize['cost_per_item']:.2f}")
        if prize['total_cost']:
            info_parts.append(f"Total: ${prize['total_cost']:.2f}")
        if prize['is_received']:
            info_parts.append("✓ Received")
        else:
            info_parts.append("⏳ Not received")

        ctk.CTkLabel(
            left,
            text=" | ".join(info_parts),
            text_color="#666666"
        ).pack(anchor="w")

        # Right side - buttons
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")

        btn_edit = ctk.CTkButton(
            right,
            text="Edit",
            command=lambda p=prize: self.edit_prize(p),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=80
        )
        btn_edit.pack(side="left", padx=2)

        btn_delete = ctk.CTkButton(
            right,
            text="Delete",
            command=lambda p=prize: self.delete_prize(p),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=80
        )
        btn_delete.pack(side="left", padx=2)

    def add_prize(self):
        """Show dialog to add a new prize"""
        dialog = PrizeDialog(self, self.db, self.event_id)
        self.wait_window(dialog)
        self.refresh_prizes_list()

    def edit_prize(self, prize):
        """Show dialog to edit a prize"""
        dialog = PrizeDialog(self, self.db, self.event_id, prize)
        self.wait_window(dialog)
        self.refresh_prizes_list()

    def delete_prize(self, prize):
        """Delete a prize"""
        if messagebox.askyesno("Confirm Delete", f"Delete prize '{prize['description']}'?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM prize_items WHERE id = ?', (prize['id'],))
            conn.commit()
            conn.close()
            self.refresh_prizes_list()

    def create_players_tab(self):
        """Create the players management tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_players, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            scroll,
            text="Attendees",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 10))

        # Instructions
        ctk.CTkLabel(
            scroll,
            text="Enter player names separated by commas, tabs, or new lines. Or enter one at a time.",
            text_color="#666666",
            font=ctk.CTkFont(size=15)
        ).pack(anchor="w", pady=(0, 10))

        # Include attendees in PDF checkbox
        self.var_include_attendees = ctk.BooleanVar(value=self.event_data.get('include_attendees', False) if self.event_data else False)
        ctk.CTkCheckBox(
            scroll,
            text="Include attendees checklist in PDF printout",
            variable=self.var_include_attendees,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            checkmark_color="white"
        ).pack(anchor="w", pady=(0, 15))

        # Add player section (textbox for bulk import)
        add_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        add_frame.pack(fill="x", pady=(0, 15))

        self.text_player_names = ctk.CTkTextbox(
            add_frame,
            height=80
        )
        self.text_player_names.pack(side="left", fill="both", expand=True, padx=(0, 10))

        btn_add = ctk.CTkButton(
            add_frame,
            text="+ Add Players",
            command=self.add_players,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=120
        )
        btn_add.pack(side="left")

        # Players list frame
        self.players_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.players_list_frame.pack(fill="both", expand=True)

        # Load existing players
        self.refresh_players_list()

    def refresh_players_list(self):
        """Refresh the players list"""
        # Clear existing widgets
        for widget in self.players_list_frame.winfo_children():
            widget.destroy()

        # Get players
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM event_players
            WHERE event_id = ?
            ORDER BY sort_order, player_name
        ''', (self.event_id,))
        players = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not players:
            ctk.CTkLabel(
                self.players_list_frame,
                text="No players added yet. Enter a name above and click 'Add Player'.",
                text_color="#999999",
                font=ctk.CTkFont()
            ).pack(pady=20)
            return

        # Display players
        for player in players:
            self.create_player_card(player)

    def create_player_card(self, player):
        """Create a card for a player"""
        card = ctk.CTkFrame(
            self.players_list_frame,
            fg_color="#F9F5FA",
            corner_radius=8,
            border_width=1,
            border_color="#E6D9F2"
        )
        card.pack(fill="x", pady=2)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=8)

        # Player name
        ctk.CTkLabel(
            content,
            text=player['player_name'],
            font=ctk.CTkFont(size=15),
            text_color="#4A2D5E"
        ).pack(side="left", fill="x", expand=True)

        # Delete button
        btn_delete = ctk.CTkButton(
            content,
            text="✕",
            command=lambda p=player: self.delete_player(p),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=30,
            height=24
        )
        btn_delete.pack(side="right")

    def add_players(self):
        """Add one or more players (supports bulk import)"""
        import re

        # Get text from textbox
        text = self.text_player_names.get("1.0", "end-1c").strip()

        if not text:
            return

        # Split by newlines, commas, or tabs
        # Replace tabs and commas with newlines, then split
        text = text.replace('\t', '\n').replace(',', '\n')

        # Split by newlines and clean up
        player_names = []
        for line in text.split('\n'):
            name = line.strip()
            if name:  # Only add non-empty names
                player_names.append(name)

        if not player_names:
            return

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        for player_name in player_names:
            cursor.execute('''
                INSERT INTO event_players (event_id, player_name)
                VALUES (?, ?)
            ''', (self.event_id, player_name))

        conn.commit()
        conn.close()

        # Clear textbox and refresh
        self.text_player_names.delete("1.0", "end")
        self.refresh_players_list()

        # Show confirmation
        if len(player_names) == 1:
            messagebox.showinfo("Success", "1 player added!")
        else:
            messagebox.showinfo("Success", f"{len(player_names)} players added!")

    def delete_player(self, player):
        """Delete a player"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM event_players WHERE id = ?', (player['id'],))
        conn.commit()
        conn.close()
        self.refresh_players_list()

    def create_checklist_tab(self):
        """Create the checklist management tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_checklist, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            scroll,
            text="Event Checklist",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 10))

        # Instructions
        ctk.CTkLabel(
            scroll,
            text="Manage tasks for this event. Items can be included in the PDF printout and/or shown on the dashboard.",
            text_color="#666666",
            font=ctk.CTkFont(size=15)
        ).pack(anchor="w", pady=(0, 10))

        # Add button
        btn_add = ctk.CTkButton(
            scroll,
            text="+ Add Checklist Item",
            command=self.add_checklist_item,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=150
        )
        btn_add.pack(anchor="w", pady=(0, 15))

        # Checklist items list frame
        self.checklist_items_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.checklist_items_frame.pack(fill="both", expand=True)

        # Load existing items
        self.refresh_checklist_items()

    def refresh_checklist_items(self):
        """Refresh the checklist items list"""
        # Clear existing widgets
        for widget in self.checklist_items_frame.winfo_children():
            widget.destroy()

        # Get checklist items grouped by category
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ci.*, cc.name as category_name
            FROM event_checklist_items ci
            LEFT JOIN checklist_categories cc ON ci.category_id = cc.id
            WHERE ci.event_id = ?
            ORDER BY cc.sort_order, ci.sort_order, ci.description
        ''', (self.event_id,))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not items:
            ctk.CTkLabel(
                self.checklist_items_frame,
                text="No checklist items yet. Click 'Add Checklist Item' to create one.",
                text_color="#999999",
                font=ctk.CTkFont()
            ).pack(pady=20)
            return

        # Group items by category
        categories = {}
        for item in items:
            category = item.get('category_name') or 'Other'
            if category not in categories:
                categories[category] = []
            categories[category].append(item)

        # Display by category
        category_order = ["Before the Event", "During the Event", "After the Event", "Other"]
        for category in category_order:
            if category in categories:
                # Category header
                category_frame = ctk.CTkFrame(self.checklist_items_frame, fg_color="transparent")
                category_frame.pack(fill="x", pady=(10, 5))

                ctk.CTkLabel(
                    category_frame,
                    text=category,
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="#8B5FBF"
                ).pack(anchor="w")

                # Items in this category
                for item in categories[category]:
                    self.create_checklist_item_card(item)

    def create_checklist_item_card(self, item):
        """Create a card for a checklist item"""
        card = ctk.CTkFrame(
            self.checklist_items_frame,
            fg_color="#F9F5FA",
            corner_radius=8,
            border_width=1,
            border_color="#E6D9F2"
        )
        card.pack(fill="x", pady=2)

        # Store item data for drag-and-drop
        card.item_data = item

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)

        # Reorder buttons (up/down arrows)
        reorder_frame = ctk.CTkFrame(content, fg_color="transparent")
        reorder_frame.pack(side="left", padx=(0, 10))

        btn_up = ctk.CTkButton(
            reorder_frame,
            text="▲",
            command=lambda i=item: self.move_checklist_item_up(i),
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=25,
            height=20,
            font=ctk.CTkFont(size=10)
        )
        btn_up.pack(pady=(0, 2))

        btn_down = ctk.CTkButton(
            reorder_frame,
            text="▼",
            command=lambda i=item: self.move_checklist_item_down(i),
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=25,
            height=20,
            font=ctk.CTkFont(size=10)
        )
        btn_down.pack()

        # Left side - info
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        # Description with completion checkbox
        desc_frame = ctk.CTkFrame(left, fg_color="transparent")
        desc_frame.pack(anchor="w", fill="x")

        # Completion checkbox
        var_completed = ctk.BooleanVar(value=bool(item.get('is_completed', 0)))
        chk = ctk.CTkCheckBox(
            desc_frame,
            text="",
            variable=var_completed,
            command=lambda i=item, v=var_completed: self.toggle_checklist_completion(i, v),
            text_color="#4A2D5E",
            border_color="black",
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            checkmark_color="white",
            width=20
        )
        chk.pack(side="left", padx=(0, 10))

        # Description text
        desc_label = ctk.CTkLabel(
            desc_frame,
            text=item['description'],
            font=ctk.CTkFont(size=15),
            text_color="#4A2D5E" if not item.get('is_completed') else "#999999"
        )
        desc_label.pack(side="left")

        # Additional info
        info_parts = []
        if item.get('due_date'):
            info_parts.append(f"Due: {item['due_date']}")
        if item.get('include_in_pdf'):
            info_parts.append("📄 PDF")

        if info_parts:
            ctk.CTkLabel(
                left,
                text=" | ".join(info_parts),
                text_color="#666666",
                font=ctk.CTkFont(size=15)
            ).pack(anchor="w", padx=(30, 0))

        # Right side - buttons
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")

        btn_edit = ctk.CTkButton(
            right,
            text="Edit",
            command=lambda i=item: self.edit_checklist_item(i),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=80
        )
        btn_edit.pack(side="left", padx=2)

        btn_delete = ctk.CTkButton(
            right,
            text="Delete",
            command=lambda i=item: self.delete_checklist_item(i),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=80
        )
        btn_delete.pack(side="left", padx=2)

    def move_checklist_item_up(self, item):
        """Move a checklist item up in the order within its category"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get current sort_order and category
        current_order = item['sort_order']
        category_id = item.get('category_id')

        # Find the item immediately above this one in the same category
        cursor.execute('''
            SELECT id, sort_order
            FROM event_checklist_items
            WHERE event_id = ?
              AND category_id IS ?
              AND sort_order < ?
            ORDER BY sort_order DESC
            LIMIT 1
        ''', (self.event_id, category_id, current_order))

        prev_item = cursor.fetchone()

        if prev_item:
            # Swap sort_order values
            prev_id, prev_order = prev_item

            cursor.execute('''
                UPDATE event_checklist_items
                SET sort_order = ?
                WHERE id = ?
            ''', (prev_order, item['id']))

            cursor.execute('''
                UPDATE event_checklist_items
                SET sort_order = ?
                WHERE id = ?
            ''', (current_order, prev_id))

            conn.commit()

            # Refresh the checklist display
            self.refresh_checklist_items()

        conn.close()

    def move_checklist_item_down(self, item):
        """Move a checklist item down in the order within its category"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get current sort_order and category
        current_order = item['sort_order']
        category_id = item.get('category_id')

        # Find the item immediately below this one in the same category
        cursor.execute('''
            SELECT id, sort_order
            FROM event_checklist_items
            WHERE event_id = ?
              AND category_id IS ?
              AND sort_order > ?
            ORDER BY sort_order ASC
            LIMIT 1
        ''', (self.event_id, category_id, current_order))

        next_item = cursor.fetchone()

        if next_item:
            # Swap sort_order values
            next_id, next_order = next_item

            cursor.execute('''
                UPDATE event_checklist_items
                SET sort_order = ?
                WHERE id = ?
            ''', (next_order, item['id']))

            cursor.execute('''
                UPDATE event_checklist_items
                SET sort_order = ?
                WHERE id = ?
            ''', (current_order, next_id))

            conn.commit()

            # Refresh the checklist display
            self.refresh_checklist_items()

        conn.close()

    def toggle_checklist_completion(self, item, var):
        """Toggle completion status of a checklist item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE event_checklist_items
            SET is_completed = ?
            WHERE id = ?
        ''', (1 if var.get() else 0, item['id']))
        conn.commit()
        conn.close()
        self.refresh_checklist_items()

    def add_checklist_item(self):
        """Show dialog to add a new checklist item"""
        dialog = ChecklistItemDialog(self, self.db, self.event_id)
        self.wait_window(dialog)
        self.refresh_checklist_items()

    def edit_checklist_item(self, item):
        """Show dialog to edit a checklist item"""
        dialog = ChecklistItemDialog(self, self.db, self.event_id, item)
        self.wait_window(dialog)
        self.refresh_checklist_items()

    def delete_checklist_item(self, item):
        """Delete a checklist item"""
        if messagebox.askyesno("Confirm Delete", f"Delete checklist item '{item['description']}'?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM event_checklist_items WHERE id = ?', (item['id'],))
            conn.commit()
            conn.close()
            self.refresh_checklist_items()

    def create_notes_tab(self):
        """Create the notes management tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_notes, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            scroll,
            text="Event Notes",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 10))

        # Add button
        btn_add = ctk.CTkButton(
            scroll,
            text="+ Add Note",
            command=self.add_note,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=150
        )
        btn_add.pack(anchor="w", pady=(0, 15))

        # Notes list frame
        self.notes_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.notes_list_frame.pack(fill="both", expand=True)

        # Load existing notes
        self.refresh_notes_list()

    def refresh_notes_list(self):
        """Refresh the notes list"""
        # Clear existing widgets
        for widget in self.notes_list_frame.winfo_children():
            widget.destroy()

        # Get notes (only those marked to show in Notes tab)
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM event_notes
            WHERE event_id = ? AND show_in_notes_tab = 1
            ORDER BY created_at DESC
        ''', (self.event_id,))
        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not notes:
            ctk.CTkLabel(
                self.notes_list_frame,
                text="No notes yet. Click 'Add Note' to create one.",
                text_color="#999999",
                font=ctk.CTkFont()
            ).pack(pady=20)
            return

        # Display notes
        for note in notes:
            self.create_note_card(note)

    def create_note_card(self, note):
        """Create a card for a note"""
        card = ctk.CTkFrame(
            self.notes_list_frame,
            fg_color="#F9F5FA",
            corner_radius=8,
            border_width=1,
            border_color="#E6D9F2"
        )
        card.pack(fill="x", pady=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=10)

        # Note text
        ctk.CTkLabel(
            content,
            text=note['note_text'],
            text_color="#4A2D5E",
            wraplength=600,
            justify="left"
        ).pack(anchor="w", pady=(0, 5))

        # Bottom row - buttons
        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.pack(fill="x")

        # Buttons
        btn_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        btn_frame.pack(side="right")

        btn_edit = ctk.CTkButton(
            btn_frame,
            text="Edit",
            command=lambda n=note: self.edit_note(n),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=80
        )
        btn_edit.pack(side="left", padx=2)

        btn_delete = ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=lambda n=note: self.delete_note(n),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=80
        )
        btn_delete.pack(side="left", padx=2)

    def add_note(self):
        """Show dialog to add a new note"""
        template_id = self.event_data.get('template_id') if hasattr(self, 'event_data') else None
        dialog = NoteDialog(self, self.db, self.event_id, template_id, note_data=None, from_notes_tab=True)
        self.wait_window(dialog)
        self.refresh_notes_list()

    def edit_note(self, note):
        """Show dialog to edit a note"""
        template_id = self.event_data.get('template_id') if hasattr(self, 'event_data') else None
        dialog = NoteDialog(self, self.db, self.event_id, template_id, note_data=note, from_notes_tab=True)
        self.wait_window(dialog)
        self.refresh_notes_list()

    def delete_note(self, note):
        """Delete a note"""
        if messagebox.askyesno("Confirm Delete", "Delete this note?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM event_notes WHERE id = ?', (note['id'],))
            conn.commit()
            conn.close()
            self.refresh_notes_list()

    def create_pre_event_tab(self):
        """Create pre-event analysis tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_pre_event, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll,
            text="Pre-Event Analysis",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 20))

        # Labor Projection Section
        ctk.CTkLabel(
            scroll,
            text="Labor Cost Projection",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(10, 10))

        self.load_labor_projection(scroll)

        # Revenue Projection Section
        ctk.CTkLabel(
            scroll,
            text="Revenue Projection",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(20, 10))

        self.load_revenue_projection(scroll)

        # Cost Summary and Break-Even Analysis
        self.breakeven_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.breakeven_frame.pack(fill="x", pady=(20, 10))

        self.calculate_breakeven()

    def load_labor_projection(self, parent):
        """Load labor cost projection inputs"""
        labor_frame = ctk.CTkFrame(parent, fg_color="white")
        labor_frame.pack(fill="x", pady=(0, 10))

        header = ctk.CTkFrame(labor_frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="Add workers at different rate types",
            text_color="#666666",
            font=ctk.CTkFont(size=15)
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="+ Add Worker Group",
            command=self.add_labor_entry,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=150,
            height=32
        ).pack(side="right")

        # Container for labor entries
        self.labor_entries_frame = ctk.CTkScrollableFrame(labor_frame, fg_color="white", height=150)
        self.labor_entries_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.load_labor_entries()

    def load_labor_entries(self):
        """Load and display labor entries"""
        for widget in self.labor_entries_frame.winfo_children():
            widget.destroy()

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Check if we have labor projections stored for this event
        cursor.execute('''
            SELECT * FROM labour_costs
            WHERE event_id = ?
            ORDER BY id
        ''', (self.event_id,))

        labor_entries = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not labor_entries:
            ctk.CTkLabel(
                self.labor_entries_frame,
                text="No labor entries yet. Click '+ Add Worker Group' to add workers.",
                text_color="#999999",
                font=ctk.CTkFont(size=15)
            ).pack(pady=20)
            return

        total_cost = 0
        for entry in labor_entries:
            entry_frame = ctk.CTkFrame(self.labor_entries_frame, fg_color="#F9F5FA")
            entry_frame.pack(fill="x", pady=5)

            content = ctk.CTkFrame(entry_frame, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=10)

            # Left side - entry details
            left = ctk.CTkFrame(content, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True)

            # Display worker info
            workers = entry.get('staff_count', 1)
            hours = entry.get('hours_worked', 0)
            rate = entry.get('hourly_rate', 0)
            cost = entry.get('total_cost', 0)
            rate_type = entry.get('rate_type', 'Unknown')

            info_text = f"{workers} worker(s) × {hours} hours @ ${rate:.2f}/hr ({rate_type})"
            ctk.CTkLabel(
                left,
                text=info_text,
                text_color="#4A2D5E",
                font=ctk.CTkFont(size=15)
            ).pack(anchor="w")

            ctk.CTkLabel(
                left,
                text=f"Cost: ${cost:.2f}",
                text_color="#8B5FBF",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", pady=(3, 0))

            # Right side - action buttons
            right = ctk.CTkFrame(content, fg_color="transparent")
            right.pack(side="right")

            ctk.CTkButton(
                right,
                text="Edit",
                command=lambda e=entry: self.edit_labor_entry(e),
                fg_color="#8B5FBF",
                hover_color="#7A4FB0",
                width=60,
                height=28
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                right,
                text="Delete",
                command=lambda e=entry: self.delete_labor_entry(e),
                fg_color="#E57373",
                hover_color="#D32F2F",
                width=60,
                height=28
            ).pack(side="left", padx=2)

            total_cost += cost

        # Show total
        if labor_entries:
            total_frame = ctk.CTkFrame(self.labor_entries_frame, fg_color="transparent")
            total_frame.pack(fill="x", pady=(10, 5))

            ctk.CTkLabel(
                total_frame,
                text=f"Total Labor Cost: ${total_cost:.2f}",
                text_color="#8B5FBF",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w")

    def add_labor_entry(self):
        """Open dialog to add labor entry"""
        from views.event_dialogs import LaborProjectionDialog
        dialog = LaborProjectionDialog(self, self.db, self.event_id)
        self.wait_window(dialog)
        self.load_labor_entries()
        self.calculate_breakeven()

    def edit_labor_entry(self, entry_data: dict):
        """Edit an existing labor entry"""
        from views.event_dialogs import LaborProjectionDialog
        dialog = LaborProjectionDialog(self, self.db, self.event_id, entry_data)
        self.wait_window(dialog)
        self.load_labor_entries()
        self.calculate_breakeven()

    def delete_labor_entry(self, entry_data: dict):
        """Delete a labor entry"""
        if messagebox.askyesno("Confirm Delete", "Delete this labor entry?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM labour_costs WHERE id = ?', (entry_data['id'],))
            conn.commit()
            conn.close()
            self.load_labor_entries()
            self.calculate_breakeven()
            messagebox.showinfo("Success", "Labor entry deleted")

    def load_revenue_projection(self, parent):
        """Load revenue projection from ticket tiers"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM ticket_tiers
            WHERE event_id = ?
            ORDER BY price DESC
        ''', (self.event_id,))
        ticket_tiers = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not ticket_tiers:
            ctk.CTkLabel(
                parent,
                text="No ticket tiers configured. Add ticket tiers to see revenue projection.",
                text_color="#999999"
            ).pack(anchor="w", pady=(0, 20))
            return

        revenue_frame = ctk.CTkFrame(parent, fg_color="white")
        revenue_frame.pack(fill="x", pady=(0, 10))

        content = ctk.CTkFrame(revenue_frame, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=15)

        for tier in ticket_tiers:
            tier_frame = ctk.CTkFrame(content, fg_color="transparent")
            tier_frame.pack(fill="x", pady=5)

            tier_revenue = tier['price'] * tier['quantity_available']
            label_text = f"{tier['tier_name']}: ${tier['price']:.2f} × {tier['quantity_available']} = ${tier_revenue:.2f}"

            ctk.CTkLabel(
                tier_frame,
                text=label_text,
                text_color="#4A2D5E",
                font=ctk.CTkFont(size=15)
            ).pack(side="left")

        # Total potential revenue
        total_revenue = sum(tier['price'] * tier['quantity_available'] for tier in ticket_tiers)
        ctk.CTkLabel(
            content,
            text=f"Maximum Potential Revenue: ${total_revenue:.2f}",
            text_color="#8B5FBF",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", pady=(10, 0))

    def calculate_breakeven(self):
        """Calculate break-even analysis"""
        # Clear existing breakeven display
        for widget in self.breakeven_frame.winfo_children():
            widget.destroy()

        # Get costs from database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get labor costs from labour_costs table
        cursor.execute('SELECT SUM(total_cost) as labor_total FROM labour_costs WHERE event_id = ?', (self.event_id,))
        result = cursor.fetchone()
        labor_cost = result['labor_total'] if result and result['labor_total'] else 0.0

        cursor.execute('SELECT SUM(total_cost) as prize_total FROM prize_items WHERE event_id = ?', (self.event_id,))
        result = cursor.fetchone()
        prize_cost = result['prize_total'] if result and result['prize_total'] else 0.0

        cursor.execute('SELECT SUM(amount) as other_total FROM event_costs WHERE event_id = ?', (self.event_id,))
        result = cursor.fetchone()
        other_cost = result['other_total'] if result and result['other_total'] else 0.0

        total_costs = labor_cost + prize_cost + other_cost

        # Get ticket tiers
        cursor.execute('SELECT * FROM ticket_tiers WHERE event_id = ? ORDER BY price DESC', (self.event_id,))
        ticket_tiers = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Display cost summary
        ctk.CTkLabel(
            self.breakeven_frame,
            text="Cost Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 10))

        costs_frame = ctk.CTkFrame(self.breakeven_frame, fg_color="white")
        costs_frame.pack(fill="x", pady=(0, 20))

        costs_content = ctk.CTkFrame(costs_frame, fg_color="transparent")
        costs_content.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(costs_content, text=f"Labor: ${labor_cost:.2f}", text_color="#4A2D5E", font=ctk.CTkFont(size=15)).pack(anchor="w", pady=3)
        ctk.CTkLabel(costs_content, text=f"Prize Support: ${prize_cost:.2f}", text_color="#4A2D5E", font=ctk.CTkFont(size=15)).pack(anchor="w", pady=3)
        ctk.CTkLabel(costs_content, text=f"Other Costs: ${other_cost:.2f}", text_color="#4A2D5E", font=ctk.CTkFont(size=15)).pack(anchor="w", pady=3)
        ctk.CTkLabel(costs_content, text=f"Total Costs: ${total_costs:.2f}", text_color="#8B5FBF", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(8, 0))

        # Break-even analysis
        if not ticket_tiers or total_costs == 0:
            ctk.CTkLabel(
                self.breakeven_frame,
                text="Add ticket tiers and costs to see break-even analysis",
                text_color="#999999"
            ).pack(pady=20)
            return

        ctk.CTkLabel(
            self.breakeven_frame,
            text="Break-Even Analysis",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(10, 10))

        be_frame = ctk.CTkFrame(self.breakeven_frame, fg_color="white")
        be_frame.pack(fill="x", pady=(0, 10))

        be_content = ctk.CTkFrame(be_frame, fg_color="transparent")
        be_content.pack(fill="x", padx=15, pady=15)

        # Calculate per-tier break-even
        total_capacity = sum(tier['quantity_available'] for tier in ticket_tiers)
        max_revenue = sum(tier['price'] * tier['quantity_available'] for tier in ticket_tiers)

        if total_capacity > 0:
            # Calculate how many tickets at average price
            avg_price = max_revenue / total_capacity
            tickets_needed = total_costs / avg_price if avg_price > 0 else 0
            breakeven_percentage = (tickets_needed / total_capacity) * 100

            # Determine status color
            if breakeven_percentage < 60:
                status_color = "#81C784"  # Green - very achievable
                status_text = "Very Achievable"
            elif breakeven_percentage < 80:
                status_color = "#FFB74D"  # Orange - achievable
                status_text = "Achievable"
            else:
                status_color = "#E57373"  # Red - challenging
                status_text = "Challenging"

            ctk.CTkLabel(
                be_content,
                text=f"Need to sell {int(tickets_needed)} of {total_capacity} tickets ({breakeven_percentage:.1f}%)",
                text_color=status_color,
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w", pady=5)

            ctk.CTkLabel(
                be_content,
                text=f"Status: {status_text}",
                text_color=status_color,
                font=ctk.CTkFont(size=15)
            ).pack(anchor="w", pady=3)

            ctk.CTkLabel(
                be_content,
                text=f"Maximum Potential Revenue: ${max_revenue:.2f}",
                text_color="#4A2D5E",
                font=ctk.CTkFont(size=15)
            ).pack(anchor="w", pady=3)

            profit_at_capacity = max_revenue - total_costs
            ctk.CTkLabel(
                be_content,
                text=f"Profit at Full Capacity: ${profit_at_capacity:.2f}",
                text_color="#81C784" if profit_at_capacity > 0 else "#E57373",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w", pady=(8, 3))

            # Per-tier break-even analysis
            ctk.CTkLabel(
                be_content,
                text="\nPer-Tier Break-Even:",
                text_color="#4A2D5E",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w", pady=(10, 5))

            remaining_costs = total_costs
            for tier in ticket_tiers:
                if tier['price'] > 0:
                    # How many of this tier alone would break even
                    tier_breakeven = min(remaining_costs / tier['price'], tier['quantity_available'])
                    tier_percentage = (tier_breakeven / tier['quantity_available']) * 100 if tier['quantity_available'] > 0 else 0

                    tier_text = f"  • {tier['tier_name']}: {int(tier_breakeven)} of {tier['quantity_available']} ({tier_percentage:.1f}%)"

                    ctk.CTkLabel(
                        be_content,
                        text=tier_text,
                        text_color="#666666",
                        font=ctk.CTkFont(size=15)
                    ).pack(anchor="w", pady=2)

                    # Update remaining costs
                    tier_revenue = tier['price'] * tier_breakeven
                    remaining_costs = max(0, remaining_costs - tier_revenue)

    def create_post_event_tab(self):
        """Create post-event analysis tab"""
        scroll = ctk.CTkScrollableFrame(self.tab_post_event, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll,
            text="Post-Event Analysis",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 20))

        # Ticket Sales Tracking Section
        ctk.CTkLabel(
            scroll,
            text="Ticket Sales (Actual)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(10, 10))

        self.load_ticket_sales_tracking(scroll)

        # Prize Handout Tracking Section
        ctk.CTkLabel(
            scroll,
            text="Prize Handouts",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(20, 10))

        ctk.CTkLabel(
            scroll,
            text="Track how many prizes were actually handed out (can be more than originally planned)",
            text_color="#666666",
            font=ctk.CTkFont(size=15)
        ).pack(anchor="w", pady=(0, 10))

        self.load_prize_handout_tracking(scroll)

        # Event Analysis Section
        ctk.CTkLabel(
            scroll,
            text="Event Analysis",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(20, 10))

        self.load_event_analysis(scroll)

        # Event Notes Section
        ctk.CTkLabel(
            scroll,
            text="Event Notes",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(20, 10))

        btn_add_note = ctk.CTkButton(
            scroll,
            text="+ Add Note",
            command=self.add_post_event_note,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=120
        )
        btn_add_note.pack(anchor="w", pady=(0, 10))

        # Notes list container
        self.post_event_notes_frame = ctk.CTkScrollableFrame(scroll, fg_color="white", height=200)
        self.post_event_notes_frame.pack(fill="x", pady=(0, 20))

        self.load_post_event_notes()

        # Event completion section at the bottom
        ctk.CTkLabel(scroll, text="", height=20).pack()  # Spacer

        completion_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        completion_frame.pack(fill="x", padx=0, pady=(10, 20))

        # Show appropriate button based on completion status
        if self.event_data and self.event_data.get('is_completed'):
            # Show completed badge and undo button
            badge_frame = ctk.CTkFrame(completion_frame, fg_color="transparent")
            badge_frame.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                badge_frame,
                text="✓ Event Completed",
                fg_color="#81C784",
                text_color="white",
                corner_radius=8,
                padx=15,
                pady=8,
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(side="left", padx=(0, 10))

            ctk.CTkButton(
                badge_frame,
                text="Undo Completion",
                command=self.mark_event_incomplete,
                fg_color="#E57373",
                hover_color="#D32F2F",
                text_color="white",
                width=140,
                height=32
            ).pack(side="left")
        else:
            # Show mark as complete button (only for existing events)
            if self.event_data:
                ctk.CTkButton(
                    completion_frame,
                    text="Mark Event as Completed",
                    command=self.mark_event_complete,
                    fg_color="#81C784",
                    hover_color="#66BB6A",
                    text_color="white",
                    height=40,
                    font=ctk.CTkFont(size=15, weight="bold")
                ).pack(fill="x", pady=5)

    def mark_event_complete(self):
        """Mark event as completed"""
        # Confirm action
        if not messagebox.askyesno("Mark as Completed",
            "Mark this event as completed?"):
            return

        # Save event completion status
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE events
            SET is_completed = 1
            WHERE id = ?
        ''', (self.event_id,))

        conn.commit()
        conn.close()

        # Reload event data from database to ensure it's a fresh dict
        self.event_data = self.event_manager.get_event_by_id(self.event_id)

        # Refresh the details tab to show completion banner
        if hasattr(self, 'tab_details'):
            for widget in self.tab_details.winfo_children():
                widget.destroy()
            self.create_details_tab()
            self.populate_fields()

        # Refresh the post-event analysis tab to show updated completion status
        if hasattr(self, 'tab_post_event'):
            # Clear the tab and recreate it
            for widget in self.tab_post_event.winfo_children():
                widget.destroy()
            self.create_post_event_tab()

        messagebox.showinfo("Event Completed", "Event marked as completed!")

    def mark_event_incomplete(self):
        """Undo event completion status"""
        # Confirm action
        if not messagebox.askyesno("Reopen Event",
            "Reopen this event for editing?\n\nThis will mark it as not completed."):
            return

        # Save event status
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE events
            SET is_completed = 0
            WHERE id = ?
        ''', (self.event_id,))

        conn.commit()
        conn.close()

        # Reload event data from database to ensure it's a fresh dict
        self.event_data = self.event_manager.get_event_by_id(self.event_id)

        # Refresh the details tab to remove completion banner
        if hasattr(self, 'tab_details'):
            for widget in self.tab_details.winfo_children():
                widget.destroy()
            self.create_details_tab()
            self.populate_fields()

        # Refresh the post-event analysis tab to show updated completion status
        if hasattr(self, 'tab_post_event'):
            # Clear the tab and recreate it
            for widget in self.tab_post_event.winfo_children():
                widget.destroy()
            self.create_post_event_tab()

        messagebox.showinfo("Event Reopened", "Event has been reopened and can now be edited.")

    def load_ticket_sales_tracking(self, parent):
        """Load ticket sales tracking for post-event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM ticket_tiers
            WHERE event_id = ?
            ORDER BY tier_name
        ''', (self.event_id,))
        ticket_tiers = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not ticket_tiers:
            ctk.CTkLabel(
                parent,
                text="No ticket tiers configured",
                text_color="#999999"
            ).pack(anchor="w", pady=(0, 20))
            return

        # Create a frame for all ticket inputs
        tickets_frame = ctk.CTkFrame(parent, fg_color="white")
        tickets_frame.pack(fill="x", pady=(0, 10))

        # Store entry widgets with their tier IDs
        self.ticket_entries = {}

        for tier in ticket_tiers:
            tier_frame = ctk.CTkFrame(tickets_frame, fg_color="transparent")
            tier_frame.pack(fill="x", padx=15, pady=8)

            # Tier name and quantity
            label_text = f"{tier['tier_name']} (${tier['price']:.2f}) - Available: {tier['quantity_available']}"
            ctk.CTkLabel(
                tier_frame,
                text=label_text,
                text_color="#4A2D5E",
                font=ctk.CTkFont(weight="bold")
            ).pack(side="left", padx=(0, 10))

            # Input for actual sold
            ctk.CTkLabel(
                tier_frame,
                text="Sold:",
                text_color="#666666"
            ).pack(side="left", padx=(10, 5))

            entry = ctk.CTkEntry(tier_frame, width=80)
            entry.insert(0, str(tier.get('quantity_sold', 0)))
            entry.pack(side="left", padx=(0, 10))

            # Store entry with tier ID
            self.ticket_entries[tier['id']] = entry

        # Single save button for all ticket sales
        ctk.CTkButton(
            parent,
            text="Save All Ticket Sales",
            command=self.save_all_ticket_sales,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            height=35
        ).pack(anchor="w", pady=(0, 20))

    def save_all_ticket_sales(self):
        """Save all ticket sales at once"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            for tier_id, entry_widget in self.ticket_entries.items():
                try:
                    quantity_sold = int(entry_widget.get())
                    if quantity_sold < 0:
                        messagebox.showerror("Invalid Input", "Quantity sold cannot be negative")
                        return
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter valid numbers for all ticket tiers")
                    return

                cursor.execute('''
                    UPDATE ticket_tiers
                    SET quantity_sold = ?
                    WHERE id = ?
                ''', (quantity_sold, tier_id))

            conn.commit()
            messagebox.showinfo("Success", "All ticket sales updated!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to save ticket sales: {str(e)}")
        finally:
            conn.close()

    def load_prize_handout_tracking(self, parent):
        """Load prize handout tracking for post-event"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM prize_items
            WHERE event_id = ?
            ORDER BY description
        ''', (self.event_id,))
        prizes = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not prizes:
            ctk.CTkLabel(
                parent,
                text="No prizes configured",
                text_color="#999999"
            ).pack(anchor="w", pady=(0, 20))
            return

        # Create a frame for all prize inputs
        prizes_frame = ctk.CTkFrame(parent, fg_color="white")
        prizes_frame.pack(fill="x", pady=(0, 10))

        # Store entry widgets with their prize IDs
        self.prize_entries = {}

        for prize in prizes:
            prize_frame = ctk.CTkFrame(prizes_frame, fg_color="transparent")
            prize_frame.pack(fill="x", padx=15, pady=8)

            # Prize description
            desc_text = f"{prize['description']} (Planned: {prize['quantity']})"
            ctk.CTkLabel(
                prize_frame,
                text=desc_text,
                text_color="#4A2D5E",
                font=ctk.CTkFont(weight="bold"),
                wraplength=300,
                anchor="w"
            ).pack(side="left", padx=(0, 10), fill="x", expand=True)

            # Input for actual handed out
            ctk.CTkLabel(
                prize_frame,
                text="Handed Out:",
                text_color="#666666"
            ).pack(side="left", padx=(10, 5))

            entry = ctk.CTkEntry(prize_frame, width=80)
            entry.insert(0, str(prize.get('quantity_handed_out', 0)))
            entry.pack(side="left", padx=(0, 10))

            # Store entry with prize ID
            self.prize_entries[prize['id']] = entry

        # Single save button for all prize handouts
        ctk.CTkButton(
            parent,
            text="Save All Prize Handouts",
            command=self.save_all_prize_handouts,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            height=35
        ).pack(anchor="w", pady=(0, 20))

    def save_all_prize_handouts(self):
        """Save all prize handouts at once"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            for prize_id, entry_widget in self.prize_entries.items():
                try:
                    quantity_handed_out = int(entry_widget.get())
                    if quantity_handed_out < 0:
                        messagebox.showerror("Invalid Input", "Quantity cannot be negative")
                        return
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter valid numbers for all prizes")
                    return

                cursor.execute('''
                    UPDATE prize_items
                    SET quantity_handed_out = ?
                    WHERE id = ?
                ''', (quantity_handed_out, prize_id))

            conn.commit()
            messagebox.showinfo("Success", "All prize handouts updated!")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to save prize handouts: {str(e)}")
        finally:
            conn.close()

    def load_event_analysis(self, parent):
        """Load comprehensive event analysis form"""
        # Get existing analysis data
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM event_analysis WHERE event_id = ?', (self.event_id,))
        row = cursor.fetchone()
        analysis = dict(row) if row else None
        conn.close()

        # Actual Attendance
        ctk.CTkLabel(parent, text="Actual Attendance", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 2))
        self.entry_attendance = ctk.CTkEntry(parent, placeholder_text="Number of attendees")
        self.entry_attendance.pack(fill="x", pady=(0, 10))

        # Attendee Satisfaction Rating
        satisfaction_frame = ctk.CTkFrame(parent, fg_color="#F9F5FA", corner_radius=8)
        satisfaction_frame.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(
            satisfaction_frame,
            text="Attendee Satisfaction Rating",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold", size=13)
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Scale explanation
        satisfaction_scale_text = """Rate how much the majority of attendees enjoyed the evening (0-10):

10: Exceptional - Everyone had an amazing time
8-9: Excellent - Vast majority loved it, highly recommended
6-7: Good - Most attendees enjoyed it and would return
4-5: Fair - Mixed reactions, some enjoyed it while others didn't
2-3: Poor - Most attendees didn't enjoy the event
0-1: Very Poor - Almost no one enjoyed it"""

        ctk.CTkLabel(
            satisfaction_frame,
            text=satisfaction_scale_text,
            text_color="#666666",
            font=ctk.CTkFont(size=15),
            justify="left",
            wraplength=800
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Satisfaction rating entry
        satisfaction_row = ctk.CTkFrame(satisfaction_frame, fg_color="transparent")
        satisfaction_row.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            satisfaction_row,
            text="Satisfaction Rating (0-10):",
            text_color="#4A2D5E",
            width=180,
            anchor="w"
        ).pack(side="left")

        self.entry_satisfaction = ctk.CTkEntry(satisfaction_row, placeholder_text="0-10", width=100)
        self.entry_satisfaction.pack(side="left", padx=5)
        self.entry_satisfaction.bind('<KeyRelease>', lambda e: self.update_overall_success_score())

        # Event Smoothness Rating
        smoothness_frame = ctk.CTkFrame(parent, fg_color="#F9F5FA", corner_radius=8)
        smoothness_frame.pack(fill="x", pady=(15, 10))

        ctk.CTkLabel(
            smoothness_frame,
            text="Event Smoothness Rating",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold", size=13)
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Scale explanation
        scale_text = """How well did the event run operationally?

9-10: Flawless execution, no issues
      Examples: Perfect timing, no delays, all tech worked, smooth check-in

7-8: Ran smoothly with only minor hiccups
     Examples: Slight registration delay, minor app glitch (quickly fixed)

5-6: Some noticeable issues but manageable
     Examples: 15+ min delays, some prize confusion, app issues requiring workarounds

3-4: Multiple problems that affected the experience
     Examples: Significant delays, frequent app crashes, prize mix-ups, seating chaos

1-2: Significant operational failures
     Examples: Major technical failures, event had to pause, severe prize/pairing issues

0: Event was chaotic/had to be stopped
   Examples: Complete app failure, event cancelled mid-way, major safety issues"""

        ctk.CTkLabel(
            smoothness_frame,
            text=scale_text,
            text_color="#666666",
            font=ctk.CTkFont(size=15),
            justify="left",
            wraplength=800
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Smoothness rating entry
        smoothness_row = ctk.CTkFrame(smoothness_frame, fg_color="transparent")
        smoothness_row.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            smoothness_row,
            text="Smoothness Rating (0-10):",
            text_color="#4A2D5E",
            width=180,
            anchor="w"
        ).pack(side="left")

        self.entry_smoothness = ctk.CTkEntry(smoothness_row, placeholder_text="0-10", width=100)
        self.entry_smoothness.pack(side="left", padx=5)
        self.entry_smoothness.bind('<KeyRelease>', lambda e: self.update_overall_success_score())

        # Overall Success Score Display
        self.overall_success_label = ctk.CTkLabel(
            parent,
            text="Overall Event Success Score: --/10",
            text_color="#8B5FBF",
            font=ctk.CTkFont(weight="bold", size=16)
        )
        self.overall_success_label.pack(anchor="w", pady=(10, 5))

        ctk.CTkLabel(
            parent,
            text="Calculated as: (Attendee Satisfaction × 60%) + (Event Smoothness × 40%)",
            text_color="#666666",
            font=ctk.CTkFont(size=15)
        ).pack(anchor="w", pady=(0, 15))


        # Populate if analysis exists
        if analysis:
            if analysis['actual_attendance']:
                self.entry_attendance.insert(0, str(analysis['actual_attendance']))
            if analysis.get('attendee_satisfaction') is not None:
                self.entry_satisfaction.insert(0, str(analysis['attendee_satisfaction']))
            if analysis.get('event_smoothness') is not None:
                self.entry_smoothness.insert(0, str(analysis['event_smoothness']))
            # Update the overall success score display
            self.update_overall_success_score()

    def update_overall_success_score(self):
        """Calculate and display overall success score in real-time"""
        try:
            # Get satisfaction score
            satisfaction_text = self.entry_satisfaction.get()
            if not satisfaction_text:
                self.overall_success_label.configure(
                    text="Overall Event Success Score: --/10 (Enter satisfaction rating)",
                    text_color="#FFB74D"
                )
                return

            satisfaction_score = float(satisfaction_text)
            if satisfaction_score < 0 or satisfaction_score > 10:
                self.overall_success_label.configure(
                    text="Satisfaction rating must be between 0-10",
                    text_color="#E57373"
                )
                return

            # Get smoothness rating
            smoothness_text = self.entry_smoothness.get()
            if not smoothness_text:
                self.overall_success_label.configure(
                    text="Overall Event Success Score: --/10 (Enter smoothness rating)",
                    text_color="#FFB74D"
                )
                return

            smoothness = float(smoothness_text)
            if smoothness < 0 or smoothness > 10:
                self.overall_success_label.configure(
                    text="Smoothness rating must be between 0-10",
                    text_color="#E57373"
                )
                return

            # Calculate overall success score
            overall_score = (satisfaction_score * 0.6) + (smoothness * 0.4)

            # Update label with color coding
            if overall_score >= 8:
                color = "#4CAF50"  # Green for excellent
            elif overall_score >= 6:
                color = "#8B5FBF"  # Purple for good
            elif overall_score >= 4:
                color = "#FFB74D"  # Orange for okay
            else:
                color = "#E57373"  # Red for poor

            self.overall_success_label.configure(
                text=f"Overall Event Success Score: {overall_score:.1f}/10",
                text_color=color
            )
        except ValueError:
            self.overall_success_label.configure(
                text="Overall Event Success Score: --/10",
                text_color="#8B5FBF"
            )

    def save_event_analysis(self, show_success_message=True):
        """Save comprehensive event analysis data"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Validate attendance
        attendance = None
        if self.entry_attendance.get():
            try:
                attendance = int(self.entry_attendance.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Attendance must be a whole number")
                conn.close()
                return

        # Validate satisfaction rating
        satisfaction_score = None
        if self.entry_satisfaction.get():
            try:
                satisfaction_score = float(self.entry_satisfaction.get())
                if satisfaction_score < 0 or satisfaction_score > 10:
                    messagebox.showerror("Validation Error", "Satisfaction rating must be between 0 and 10")
                    conn.close()
                    return
                satisfaction_score = round(satisfaction_score, 1)
            except ValueError:
                messagebox.showerror("Validation Error", "Satisfaction rating must be a number")
                conn.close()
                return

        # Validate event smoothness
        event_smoothness = None
        if self.entry_smoothness.get():
            try:
                event_smoothness = float(self.entry_smoothness.get())
                if event_smoothness < 0 or event_smoothness > 10:
                    messagebox.showerror("Validation Error", "Event smoothness must be between 0 and 10")
                    conn.close()
                    return
                event_smoothness = round(event_smoothness, 1)
            except ValueError:
                messagebox.showerror("Validation Error", "Event smoothness must be a number")
                conn.close()
                return

        # Calculate overall success score if both components are available
        overall_success_score = None
        if satisfaction_score is not None and event_smoothness is not None:
            overall_success_score = (satisfaction_score * 0.6) + (event_smoothness * 0.4)
            overall_success_score = round(overall_success_score, 1)

        # Save or update analysis
        cursor.execute('SELECT id FROM event_analysis WHERE event_id = ?', (self.event_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute('''
                UPDATE event_analysis
                SET actual_attendance = ?,
                    attendee_satisfaction = ?,
                    event_smoothness = ?,
                    overall_success_score = ?
                WHERE event_id = ?
            ''', (attendance, satisfaction_score, event_smoothness, overall_success_score, self.event_id))
        else:
            cursor.execute('''
                INSERT INTO event_analysis
                (event_id, actual_attendance, attendee_satisfaction, event_smoothness, overall_success_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.event_id, attendance, satisfaction_score, event_smoothness, overall_success_score))

        conn.commit()
        conn.close()

        # Show comprehensive summary if requested
        if show_success_message:
            summary_parts = []
            summary_parts.append("=== EVENT ANALYSIS SAVED ===")

            if attendance is not None:
                summary_parts.append(f"\nAttendance: {attendance}")
            if satisfaction_score is not None:
                summary_parts.append(f"Attendee Satisfaction: {satisfaction_score:.1f}/10")
            if event_smoothness is not None:
                summary_parts.append(f"Event Smoothness: {event_smoothness:.1f}/10")
            if overall_success_score is not None:
                summary_parts.append(f"\nOVERALL SUCCESS SCORE: {overall_success_score:.1f}/10")
                # Add rating interpretation
                if overall_success_score >= 8:
                    summary_parts.append("(Excellent Event!)")
                elif overall_success_score >= 6:
                    summary_parts.append("(Good Event)")
                elif overall_success_score >= 4:
                    summary_parts.append("(Needs Improvement)")
                else:
                    summary_parts.append("(Poor Performance)")

            summary = "\n".join(summary_parts)
            messagebox.showinfo("Analysis Saved", summary)

    def load_post_event_notes(self):
        """Load event notes for post-event analysis"""
        for widget in self.post_event_notes_frame.winfo_children():
            widget.destroy()

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM event_notes
            WHERE event_id = ?
            ORDER BY created_at DESC
        ''', (self.event_id,))
        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not notes:
            ctk.CTkLabel(
                self.post_event_notes_frame,
                text="No notes yet. Add your first note!",
                text_color="#999999"
            ).pack(pady=20)
            return

        for note in notes:
            self.create_post_event_note_card(note)

    def create_post_event_note_card(self, note: dict):
        """Create visual card for a post-event note"""
        card = ctk.CTkFrame(self.post_event_notes_frame, fg_color="#F9F5FA")
        card.pack(fill="x", padx=10, pady=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)

        # Left side - note content
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        # Note text
        note_text = note.get('note_text', '')
        display_text = note_text if len(note_text) <= 150 else note_text[:150] + "..."

        ctk.CTkLabel(
            left,
            text=display_text,
            text_color="#4A2D5E",
            anchor="w",
            wraplength=400,
            justify="left"
        ).pack(anchor="w")

        # Badge if sent to template
        if note.get('send_to_template'):
            badge = ctk.CTkLabel(
                left,
                text="Saved to template",
                fg_color="#9C27B0",
                text_color="white",
                corner_radius=10,
                padx=8,
                pady=2
            )
            badge.pack(anchor="w", pady=(5, 0))

        # Right side - action buttons
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")

        ctk.CTkButton(
            right,
            text="Save to Template",
            command=lambda n=note: self.save_note_to_template(n),
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            width=120,
            height=28
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            right,
            text="Save to Feedback",
            command=lambda n=note: self.save_note_to_feedback(n),
            fg_color="#4CAF50",
            hover_color="#45a049",
            width=120,
            height=28
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            right,
            text="Edit",
            command=lambda n=note: self.edit_post_event_note(n),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=60,
            height=28
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            right,
            text="Delete",
            command=lambda n=note: self.delete_post_event_note(n),
            fg_color="#E57373",
            hover_color="#D32F2F",
            width=60,
            height=28
        ).pack(side="left", padx=2)

    def add_post_event_note(self):
        """Open dialog to add new post-event note"""
        from views.event_dialogs import NoteDialog
        template_id = self.event_data.get('template_id') if self.event_data else None
        dialog = NoteDialog(self, self.db, self.event_id, template_id)
        self.wait_window(dialog)
        self.load_post_event_notes()

    def edit_post_event_note(self, note_data: dict):
        """Edit an existing post-event note"""
        from views.event_dialogs import NoteDialog
        template_id = self.event_data.get('template_id') if self.event_data else None
        dialog = NoteDialog(self, self.db, self.event_id, template_id, note_data)
        self.wait_window(dialog)
        self.load_post_event_notes()

    def delete_post_event_note(self, note_data: dict):
        """Delete a post-event note"""
        if messagebox.askyesno("Confirm Delete", "Delete this note?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM event_notes WHERE id = ?', (note_data['id'],))
            conn.commit()
            conn.close()
            self.load_post_event_notes()
            messagebox.showinfo("Success", "Note deleted")

    def save_note_to_template(self, note_data: dict):
        """Save a note to template(s)"""
        # Get list of templates to choose from
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM event_templates ORDER BY name')
        templates = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not templates:
            messagebox.showwarning("No Templates", "No templates available. Create a template first.")
            return

        # Create a dialog to select template(s)
        from views.event_dialogs import TemplateSelectionDialog
        dialog = TemplateSelectionDialog(self, self.db, templates, note_data, self.event_id)
        self.wait_window(dialog)
        self.load_post_event_notes()

    def save_note_to_feedback(self, note_data: dict):
        """Save a single note as a feedback card"""
        # Format the note with timestamp
        from datetime import datetime
        note_date = datetime.strptime(note_data['created_at'], '%Y-%m-%d %H:%M:%S')
        date_str = note_date.strftime('%d %b %Y at %H:%M')
        feedback_text = f"[{date_str}] {note_data['note_text']}"

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Insert new feedback item
        cursor.execute('''
            INSERT INTO feedback_items (event_id, feedback_text)
            VALUES (?, ?)
        ''', (self.event_id, feedback_text))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Note saved to Feedback menu successfully!")

    def create_analysis_tab(self):
        """Create the post-event analysis tab"""
        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(self.tab_analysis, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        ctk.CTkLabel(
            scroll,
            text="Post-Event Analysis",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 20))

        # Actual Attendance
        ctk.CTkLabel(
            scroll,
            text="Actual Attendance",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        attendance_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        attendance_frame.pack(fill="x", pady=(0, 15))

        self.entry_actual_attendance = ctk.CTkEntry(
            attendance_frame,
            placeholder_text="How many people attended?"
        )
        self.entry_actual_attendance.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Show capacity comparison
        if self.event_data and self.event_data.get('max_capacity'):
            capacity_label = ctk.CTkLabel(
                attendance_frame,
                text=f"Capacity: {self.event_data['max_capacity']}",
                text_color="#666666"
            )
            capacity_label.pack(side="left")

        # Success Rating
        ctk.CTkLabel(
            scroll,
            text="Success Rating (1-10)",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        rating_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        rating_frame.pack(fill="x", pady=(0, 5))

        self.rating_slider = ctk.CTkSlider(
            rating_frame,
            from_=1,
            to=10,
            number_of_steps=9,
            fg_color="#C5A8D9",
            progress_color="#8B5FBF",
            button_color="#8B5FBF",
            button_hover_color="#7A4FB0"
        )
        self.rating_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.rating_slider.set(5)  # Default to middle

        self.rating_label = ctk.CTkLabel(
            rating_frame,
            text="5",
            text_color="#8B5FBF",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=30
        )
        self.rating_label.pack(side="left")

        # Update label when slider moves
        self.rating_slider.configure(command=lambda value: self.rating_label.configure(text=str(int(value))))

        # Financial Summary Section
        ctk.CTkLabel(
            scroll,
            text="Financial Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(20, 10))

        # Calculate financial data
        financial_data = self.calculate_financial_summary()

        # Revenue
        revenue_frame = ctk.CTkFrame(scroll, fg_color="#E8F5E9", corner_radius=8)
        revenue_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(
            revenue_frame,
            text="Total Revenue:",
            text_color="#2E7D32",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(
            revenue_frame,
            text=f"${financial_data['revenue']:.2f}",
            text_color="#2E7D32",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="right", padx=15, pady=10)

        # Costs
        costs_frame = ctk.CTkFrame(scroll, fg_color="#FFEBEE", corner_radius=8)
        costs_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(
            costs_frame,
            text="Total Costs:",
            text_color="#C62828",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(
            costs_frame,
            text=f"${financial_data['costs']:.2f}",
            text_color="#C62828",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="right", padx=15, pady=10)

        # Profit/Loss
        profit = financial_data['revenue'] - financial_data['costs']
        profit_color = "#2E7D32" if profit >= 0 else "#C62828"
        profit_bg = "#E8F5E9" if profit >= 0 else "#FFEBEE"

        profit_frame = ctk.CTkFrame(scroll, fg_color=profit_bg, corner_radius=8, border_width=2, border_color=profit_color)
        profit_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(
            profit_frame,
            text="Profit/Loss:",
            text_color=profit_color,
            font=ctk.CTkFont(weight="bold", size=14)
        ).pack(side="left", padx=15, pady=12)
        ctk.CTkLabel(
            profit_frame,
            text=f"${profit:.2f}",
            text_color=profit_color,
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="right", padx=15, pady=12)


        # Notes
        ctk.CTkLabel(
            scroll,
            text="Notes / Feedback",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(20, 5))

        self.text_analysis_notes = ctk.CTkTextbox(scroll, height=100)
        self.text_analysis_notes.pack(fill="x", pady=(0, 15))

        # Template Feedback (if event was created from template)
        if self.event_data and self.event_data.get('template_id'):
            ctk.CTkLabel(
                scroll,
                text="Template Feedback",
                text_color="#4A2D5E",
                font=ctk.CTkFont(weight="bold")
            ).pack(anchor="w", pady=(20, 5))

            ctk.CTkLabel(
                scroll,
                text="This feedback will appear when creating future events from this template",
                text_color="#666666",
                font=ctk.CTkFont(size=15)
            ).pack(anchor="w", pady=(0, 5))

            self.text_template_feedback = ctk.CTkTextbox(scroll, height=80)
            self.text_template_feedback.pack(fill="x", pady=(0, 15))

        # Populate fields if analysis data exists
        if self.analysis_data:
            self.populate_analysis_fields()

    def calculate_financial_summary(self):
        """Calculate total revenue, costs, and profit"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get ticket revenue
        cursor.execute('''
            SELECT SUM(price * quantity_sold) as revenue
            FROM ticket_tiers
            WHERE event_id = ?
        ''', (self.event_id,))
        revenue_row = cursor.fetchone()
        revenue = float(revenue_row['revenue']) if revenue_row and revenue_row['revenue'] else 0.0

        # Get costs (event_costs + labour_costs)
        cursor.execute('''
            SELECT SUM(amount) as total_costs
            FROM event_costs
            WHERE event_id = ?
        ''', (self.event_id,))
        event_costs_row = cursor.fetchone()
        event_costs = float(event_costs_row['total_costs']) if event_costs_row and event_costs_row['total_costs'] else 0.0

        cursor.execute('''
            SELECT SUM(total_cost) as labour_total
            FROM labour_costs
            WHERE event_id = ?
        ''', (self.event_id,))
        labour_row = cursor.fetchone()
        labour_costs = float(labour_row['labour_total']) if labour_row and labour_row['labour_total'] else 0.0

        total_costs = event_costs + labour_costs

        conn.close()

        return {
            'revenue': revenue,
            'costs': total_costs
        }

    def populate_analysis_fields(self):
        """Populate analysis fields with existing data"""
        if not self.analysis_data:
            return

        if self.analysis_data.get('actual_attendance'):
            self.entry_actual_attendance.insert(0, str(self.analysis_data['actual_attendance']))

        if self.analysis_data.get('success_rating'):
            self.rating_slider.set(self.analysis_data['success_rating'])
            self.rating_label.configure(text=str(self.analysis_data['success_rating']))

        if self.analysis_data.get('notes'):
            self.text_analysis_notes.insert("1.0", self.analysis_data['notes'])

        # Load template feedback if exists
        if self.event_data and self.event_data.get('template_id') and hasattr(self, 'text_template_feedback'):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT feedback_text FROM template_feedback
                WHERE event_id = ?
            ''', (self.event_id,))
            feedback_row = cursor.fetchone()
            conn.close()

            if feedback_row:
                self.text_template_feedback.insert("1.0", feedback_row['feedback_text'])

    def save_analysis_data(self):
        """Save post-event analysis data"""
        # Validate attendance
        actual_attendance = None
        if self.entry_actual_attendance.get().strip():
            try:
                actual_attendance = int(self.entry_actual_attendance.get().strip())
                if actual_attendance < 0:
                    messagebox.showerror("Validation Error", "Actual attendance must be a positive number")
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Actual attendance must be a whole number")
                return

        # Get success rating
        success_rating = int(self.rating_slider.get())

        # Calculate financial summary
        financial_data = self.calculate_financial_summary()
        profit_margin = financial_data['revenue'] - financial_data['costs']

        # Get notes
        notes = self.text_analysis_notes.get("1.0", "end-1c")

        # Save to database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Check if analysis record exists
        cursor.execute('SELECT id FROM event_analysis WHERE event_id = ?', (self.event_id,))
        existing = cursor.fetchone()

        if existing:
            # Update existing
            cursor.execute('''
                UPDATE event_analysis
                SET actual_attendance = ?,
                    success_rating = ?,
                    profit_margin = ?,
                    revenue_total = ?,
                    cost_total = ?,
                    notes = ?
                WHERE event_id = ?
            ''', (actual_attendance, success_rating, profit_margin,
                  financial_data['revenue'], financial_data['costs'], notes, self.event_id))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO event_analysis
                (event_id, actual_attendance, success_rating, profit_margin, revenue_total, cost_total, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.event_id, actual_attendance, success_rating, profit_margin,
                  financial_data['revenue'], financial_data['costs'], notes))

        # Save template feedback if applicable
        if self.event_data and self.event_data.get('template_id') and hasattr(self, 'text_template_feedback'):
            feedback_text = self.text_template_feedback.get("1.0", "end-1c")
            if feedback_text.strip():
                # Delete existing feedback
                cursor.execute('DELETE FROM template_feedback WHERE event_id = ?', (self.event_id,))
                # Insert new feedback
                cursor.execute('''
                    INSERT INTO template_feedback (template_id, event_id, feedback_text)
                    VALUES (?, ?, ?)
                ''', (self.event_data['template_id'], self.event_id, feedback_text))

        conn.commit()
        conn.close()

    def print_event_sheet(self):
        """Generate and save PDF event sheet"""
        try:
            # Default filename
            event_name_safe = self.event_data['event_name'].replace(' ', '_').replace('/', '-')
            event_date = self.event_data['event_date'].replace('-', '')
            default_filename = f"event_sheet_{event_name_safe}_{event_date}.pdf"

            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=default_filename,
                title="Save Event Sheet PDF"
            )

            if not file_path:
                return  # User cancelled

            # Generate PDF
            pdf_generator = EventPDFGenerator(self.db)
            output_path = pdf_generator.generate_event_sheet(self.event_id, file_path)

            messagebox.showinfo(
                "Success",
                f"Event sheet saved successfully!\n\nLocation: {output_path}"
            )

            # Ask if user wants to open the PDF
            if messagebox.askyesno("Open PDF?", "Would you like to open the PDF now?"):
                os.startfile(output_path)  # Windows-specific

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")

    def populate_dropdowns(self):
        """Populate dropdown values from reference data"""
        # Event types
        event_type_names = [et['name'] for et in self.ref_data['event_types']]
        self.combo_event_type.configure(values=event_type_names)
        self.combo_event_type.set("")  # Empty by default

        # Formats
        format_names = [f['name'] for f in self.ref_data['playing_formats']]
        self.combo_format.configure(values=format_names)
        self.combo_format.set("")  # Empty by default

        # Pairing methods
        method_names = [m['name'] for m in self.ref_data['pairing_methods']]
        self.combo_pairing_method.configure(values=method_names)
        self.combo_pairing_method.set("")  # Empty by default

        # Pairing apps
        app_names = [a['name'] for a in self.ref_data['pairing_apps']]
        self.combo_pairing_app.configure(values=app_names)
        self.combo_pairing_app.set("")  # Empty by default

    def populate_fields(self):
        """Populate form fields with event data"""
        if not self.event_data:
            return

        self.entry_name.insert(0, self.event_data['event_name'])
        # Set date for DateEntry widget
        try:
            event_date = datetime.strptime(self.event_data['event_date'], '%Y-%m-%d')
            self.entry_date.set_date(event_date)
        except:
            pass  # If date parsing fails, leave it at today

        if self.event_data.get('start_time'):
            # Remove seconds from time display
            start_time = self.event_data['start_time'].rsplit(':', 1)[0]
            self.entry_start_time.insert(0, start_time)

        if self.event_data.get('end_time'):
            end_time = self.event_data['end_time'].rsplit(':', 1)[0]
            self.entry_end_time.insert(0, end_time)

        if self.event_data.get('event_type_name'):
            self.combo_event_type.set(self.event_data['event_type_name'])

        if self.event_data.get('format_name'):
            self.combo_format.set(self.event_data['format_name'])

        if self.event_data.get('pairing_method_name'):
            self.combo_pairing_method.set(self.event_data['pairing_method_name'])

        if self.event_data.get('pairing_app_name'):
            self.combo_pairing_app.set(self.event_data['pairing_app_name'])

        if self.event_data.get('max_capacity'):
            self.entry_capacity.insert(0, str(self.event_data['max_capacity']))

        if self.event_data.get('tickets_available'):
            self.entry_tickets_available.insert(0, str(self.event_data['tickets_available']))

        if self.event_data.get('tables_booked'):
            self.entry_tables_booked.insert(0, str(self.event_data['tables_booked']))

        if self.event_data.get('description'):
            self.text_description.insert("1.0", self.event_data['description'])

        self.var_organised.set(bool(self.event_data.get('is_organised')))
        self.var_tickets_live.set(bool(self.event_data.get('tickets_live')))
        self.var_advertised.set(bool(self.event_data.get('is_advertised')))

    def get_id_from_name(self, items: list, name: str) -> Optional[int]:
        """Get ID from a name in reference data - creates new item if doesn't exist"""
        if not name:
            return None

        # Check if exists
        for item in items:
            if item['name'] == name:
                return item['id']

        # Doesn't exist - create it
        # Determine table name from items structure
        if items and items == self.ref_data.get('event_types'):
            table = 'event_types'
        elif items and items == self.ref_data.get('playing_formats'):
            table = 'playing_formats'
        elif items and items == self.ref_data.get('pairing_methods'):
            table = 'pairing_methods'
        elif items and items == self.ref_data.get('pairing_apps'):
            table = 'pairing_apps'
        else:
            return None

        # Add new item to database
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO {table} (name) VALUES (?)', (name,))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Refresh reference data
        self.ref_data = self.event_manager.get_reference_data()

        return new_id

    def save_event(self):
        """Save the event"""
        # Validate required fields
        if not self.entry_name.get():
            messagebox.showerror("Validation Error", "Event name is required")
            return

        if not self.entry_date.get():
            messagebox.showerror("Validation Error", "Event date is required")
            return

        # Validate date format
        try:
            datetime.strptime(self.entry_date.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format")
            return

        # Validate time format if provided
        start_time = None
        end_time = None

        if self.entry_start_time.get():
            try:
                # Add seconds if not provided
                time_str = self.entry_start_time.get()
                if len(time_str.split(':')) == 2:
                    time_str += ':00'
                datetime.strptime(time_str, '%H:%M:%S')
                start_time = time_str
            except ValueError:
                messagebox.showerror("Validation Error", "Start time must be in HH:MM format")
                return

        if self.entry_end_time.get():
            try:
                time_str = self.entry_end_time.get()
                if len(time_str.split(':')) == 2:
                    time_str += ':00'
                datetime.strptime(time_str, '%H:%M:%S')
                end_time = time_str
            except ValueError:
                messagebox.showerror("Validation Error", "End time must be in HH:MM format")
                return

        # Validate and convert capacity
        max_capacity = None
        if self.entry_capacity.get().strip():
            try:
                max_capacity = int(self.entry_capacity.get().strip())
                if max_capacity < 0:
                    messagebox.showerror("Validation Error", "Maximum capacity must be a positive number")
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Maximum capacity must be a whole number")
                return

        # Validate and convert tickets available
        tickets_available = None
        if self.entry_tickets_available.get().strip():
            try:
                tickets_available = int(self.entry_tickets_available.get().strip())
                if tickets_available < 0:
                    messagebox.showerror("Validation Error", "Tickets available must be a positive number")
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Tickets available must be a whole number")
                return

        # Validate and convert tables booked
        tables_booked = None
        if self.entry_tables_booked.get().strip():
            try:
                tables_booked = int(self.entry_tables_booked.get().strip())
                if tables_booked < 0:
                    messagebox.showerror("Validation Error", "Tables booked must be a positive number")
                    return
            except ValueError:
                messagebox.showerror("Validation Error", "Tables booked must be a whole number")
                return

        # Build event data
        event_data = {
            'event_name': self.entry_name.get(),
            'event_date': self.entry_date.get(),
            'start_time': start_time,
            'end_time': end_time,
            'event_type_id': self.get_id_from_name(self.ref_data['event_types'], self.combo_event_type.get()),
            'playing_format_id': self.get_id_from_name(self.ref_data['playing_formats'], self.combo_format.get()),
            'pairing_method_id': self.get_id_from_name(self.ref_data['pairing_methods'], self.combo_pairing_method.get()),
            'pairing_app_id': self.get_id_from_name(self.ref_data['pairing_apps'], self.combo_pairing_app.get()),
            'max_capacity': max_capacity,
            'tickets_available': tickets_available,
            'tables_booked': tables_booked,
            'description': self.text_description.get("1.0", "end-1c"),
            'is_organised': self.var_organised.get(),
            'tickets_live': self.var_tickets_live.get(),
            'is_advertised': self.var_advertised.get(),
            'is_completed': self.event_data.get('is_completed') if self.event_data else False,
            'include_attendees': self.var_include_attendees.get() if hasattr(self, 'var_include_attendees') else False
        }

        # Save to database
        try:
            if self.event_id:
                self.event_manager.update_event(self.event_id, event_data)
                # If post-event analysis tab exists, save analysis data
                if hasattr(self, 'tab_post_event'):
                    self.save_event_analysis(show_success_message=False)
                messagebox.showinfo("Success", "Event updated successfully!")
            else:
                new_event_id = self.event_manager.create_event(event_data)
                messagebox.showinfo("Success", "Event created successfully!")
                # Update dialog to edit mode for the newly created event
                self.event_id = new_event_id
                self.event_data = self.event_manager.get_event_by_id(new_event_id)
                # Recreate tabs to show all tabs now that event exists
                self.tabview.destroy()
                for widget in self.winfo_children():
                    if widget != self.tabview and not isinstance(widget, type(self.tabview)):
                        widget.destroy()
                self.create_tabs()
                self.ref_data = self.event_manager.get_reference_data()
                self.populate_dropdowns()
                self.populate_fields()
                self.create_buttons()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save event: {str(e)}")
