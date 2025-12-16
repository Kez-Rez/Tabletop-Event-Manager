"""Templates view UI"""
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
from template_manager import TemplateManager
from event_manager import EventManager
from typing import Optional
from datetime import datetime

class TemplatesView(ctk.CTkFrame):
    """Templates list and management view"""

    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.template_manager = TemplateManager(db)
        self.event_manager = EventManager(db)

        self.configure(fg_color="#F5F0F6")

        # Create header
        self.create_header()

        # Create templates list
        self.create_templates_list()

        # Load templates
        self.load_templates()

    def create_header(self):
        """Create the header with title and buttons"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Event Templates",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(side="left")

        # New template button
        btn_new = ctk.CTkButton(
            header_frame,
            text="+ New Template",
            command=self.show_new_template_dialog,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=140,
            height=40
        )
        btn_new.pack(side="right")

    def create_templates_list(self):
        """Create the scrollable templates list"""
        # Container frame with border
        list_container = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        list_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Scrollable frame
        self.templates_scroll = ctk.CTkScrollableFrame(
            list_container,
            fg_color="white",
            corner_radius=10
        )
        self.templates_scroll.pack(fill="both", expand=True, padx=2, pady=2)

    def load_templates(self):
        """Load and display templates"""
        # Clear existing widgets
        for widget in self.templates_scroll.winfo_children():
            widget.destroy()

        # Get templates
        templates = self.template_manager.get_all_templates()

        if not templates:
            # No templates message
            no_templates = ctk.CTkLabel(
                self.templates_scroll,
                text="No templates yet. Create your first template!",
                font=ctk.CTkFont(size=16),
                text_color="#999999"
            )
            no_templates.pack(pady=40)
            return

        # Display templates
        for template in templates:
            self.create_template_card(template)

    def create_template_card(self, template: dict):
        """Create a card for a template"""
        # Card frame
        card = ctk.CTkFrame(
            self.templates_scroll,
            fg_color="#F9F5FA",
            corner_radius=8,
            border_width=1,
            border_color="#E6D9F2"
        )
        card.pack(fill="x", padx=10, pady=5)

        # Main content frame
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        # Left side - Template info
        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)

        # Template name
        name_label = ctk.CTkLabel(
            left_frame,
            text=template['name'],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        )
        name_label.pack(anchor="w")

        # Template details
        details_text = []
        if template.get('event_type_name'):
            details_text.append(template['event_type_name'])
        if template.get('format_name'):
            details_text.append(template['format_name'])
        if template.get('pairing_method_name'):
            details_text.append(template['pairing_method_name'])
        if template.get('max_capacity'):
            details_text.append(f"Max: {template['max_capacity']} players")

        if details_text:
            details_label = ctk.CTkLabel(
                left_frame,
                text=" • ".join(details_text),
                font=ctk.CTkFont(size=15),
                text_color="#666666",
                anchor="w"
            )
            details_label.pack(anchor="w", pady=(5, 0))

        # Events count
        event_count = self.template_manager.count_events_using_template(template['id'])
        count_label = ctk.CTkLabel(
            left_frame,
            text=f"{event_count} event{'s' if event_count != 1 else ''} created from this template",
            font=ctk.CTkFont(size=15),
            text_color="#999999",
            anchor="w"
        )
        count_label.pack(anchor="w", pady=(5, 0))

        # Right side - Actions
        right_frame = ctk.CTkFrame(content, fg_color="transparent")
        right_frame.pack(side="right")

        # Create event from template button
        btn_create = ctk.CTkButton(
            right_frame,
            text="Create Event",
            command=lambda t=template: self.create_event_from_template(t['id'], t['name']),
            fg_color="#4CAF50",
            hover_color="#45a049",
            text_color="white",
            width=120
        )
        btn_create.pack(pady=2)

        # Edit button
        btn_edit = ctk.CTkButton(
            right_frame,
            text="Edit",
            command=lambda t=template: self.show_template_details(t['id']),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=120
        )
        btn_edit.pack(pady=2)

        # Delete button
        btn_delete = ctk.CTkButton(
            right_frame,
            text="Delete",
            command=lambda t=template: self.delete_template(t['id'], t['name']),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=120
        )
        btn_delete.pack(pady=2)

    def show_new_template_dialog(self):
        """Show dialog to create a new template"""
        dialog = TemplateEditDialog(self, self.db, None)
        self.wait_window(dialog)
        self.load_templates()

    def show_template_details(self, template_id: int):
        """Show template details/edit dialog"""
        dialog = TemplateEditDialog(self, self.db, template_id)
        self.wait_window(dialog)
        self.load_templates()

    def delete_template(self, template_id: int, template_name: str):
        """Delete a template after confirmation"""
        event_count = self.template_manager.count_events_using_template(template_id)

        if event_count > 0:
            message = f"'{template_name}' has been used to create {event_count} event(s).\n\nDeleting this template will not delete those events, but they will no longer be linked to this template.\n\nAre you sure?"
        else:
            message = f"Are you sure you want to delete '{template_name}'?\n\nThis cannot be undone."

        result = messagebox.askyesno("Confirm Delete", message)
        if result:
            self.template_manager.delete_template(template_id)
            self.load_templates()
            messagebox.showinfo("Deleted", f"'{template_name}' has been deleted.")

    def create_event_from_template(self, template_id: int, template_name: str):
        """Show dialog to create an event from this template"""
        dialog = CreateFromTemplateDialog(self, self.db, template_id, template_name)
        self.wait_window(dialog)


class TemplateEditDialog(ctk.CTkToplevel):
    """Dialog for creating/editing templates"""

    def __init__(self, parent, db, template_id: Optional[int] = None):
        super().__init__(parent)

        self.db = db
        self.template_manager = TemplateManager(db)
        self.template_id = template_id
        self.template_data = None

        # Configure window
        if template_id:
            self.title("Edit Template")
            self.template_data = self.template_manager.get_template_by_id(template_id)
        else:
            self.title("New Template")

        self.geometry("900x700")
        self.configure(fg_color="#F5F0F6")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Create notebook for tabs
        self.create_tabs()

        # Load reference data
        self.ref_data = self.template_manager.get_reference_data()
        self.populate_dropdowns()

        # If editing, populate fields
        if self.template_data:
            self.populate_fields()
            self.load_checklist_items()

    def create_tabs(self):
        """Create tabbed interface"""
        # Tab view
        self.tabview = ctk.CTkTabview(self, fg_color="#F5F0F6")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Create tabs
        self.tabview.add("Template Details")

        # Only show additional tabs for existing templates
        if self.template_id:
            self.tabview.add("Ticket Tiers")
            self.tabview.add("Prize Support")
            self.tabview.add("Checklist Items")
            self.tabview.add("Notes")
            self.tabview.add("Pre-Event Analysis")

        # Populate tabs
        self.create_details_tab()

        if self.template_id:
            self.create_tickets_tab()
            self.create_prizes_tab()
            self.create_checklist_tab()
            self.create_notes_tab()
            self.create_pre_event_tab()

    def create_details_tab(self):
        """Create the template details tab"""
        tab = self.tabview.tab("Template Details")

        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(tab, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True)

        # Template Name
        ctk.CTkLabel(scroll, text="Template Name *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_name = ctk.CTkEntry(scroll, placeholder_text="e.g., Weekly Commander Night")
        self.entry_name.pack(fill="x", pady=(0, 15))

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

        # Max Capacity
        ctk.CTkLabel(scroll, text="Maximum Capacity", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_capacity = ctk.CTkEntry(scroll, placeholder_text="e.g., 24")
        self.entry_capacity.pack(fill="x", pady=(0, 15))

        # Description
        ctk.CTkLabel(scroll, text="Description", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.text_description = ctk.CTkTextbox(scroll, height=100)
        self.text_description.pack(fill="x", pady=(0, 15))

        # Save button
        btn_save = ctk.CTkButton(
            scroll,
            text="Save Template",
            command=self.save_template,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(fill="x", pady=(20, 0))

    def create_checklist_tab(self):
        """Create the checklist items tab"""
        tab = self.tabview.tab("Checklist Items")

        # Header with add button
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header,
            text="Checklist Items",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4A2D5E"
        ).pack(side="left")

        btn_add = ctk.CTkButton(
            header,
            text="+ Add Item",
            command=self.add_checklist_item,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            width=100
        )
        btn_add.pack(side="right")

        # Scrollable checklist
        self.checklist_scroll = ctk.CTkScrollableFrame(tab, fg_color="white")
        self.checklist_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Save button at bottom
        btn_frame = ctk.CTkFrame(tab, fg_color="#F5F0F6")
        btn_frame.pack(fill="x", padx=10, pady=10)

        btn_save_template = ctk.CTkButton(
            btn_frame,
            text="Save Template",
            command=self.save_template,
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            height=40
        )
        btn_save_template.pack(fill="x")

    def create_tickets_tab(self):
        """Create the ticket tiers management tab"""
        tab = self.tabview.tab("Ticket Tiers")

        # Scrollable content area
        scroll = ctk.CTkScrollableFrame(tab, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Header with title
        header_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text="Ticket Tiers",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

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

        # Save button at bottom (outside scrollable frame)
        btn_frame = ctk.CTkFrame(tab, fg_color="#F5F0F6")
        btn_frame.pack(fill="x", padx=10, pady=10)

        btn_save_template = ctk.CTkButton(
            btn_frame,
            text="Save Template",
            command=self.save_template,
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            height=40
        )
        btn_save_template.pack(fill="x")

    def refresh_tickets_list(self):
        """Refresh the ticket tiers list"""
        # Clear existing widgets
        for widget in self.tickets_list_frame.winfo_children():
            widget.destroy()

        # Get tickets
        tickets = self.template_manager.get_template_ticket_tiers(self.template_id)

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

        info_text = f"Price: ${ticket['price']:.2f}"
        if ticket['quantity_available']:
            info_text += f" | Available: {ticket['quantity_available']}"
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
        dialog = TemplateTicketTierDialog(self, self.db, self.template_id)
        self.wait_window(dialog)
        self.refresh_tickets_list()

    def edit_ticket_tier(self, ticket):
        """Show dialog to edit a ticket tier"""
        dialog = TemplateTicketTierDialog(self, self.db, self.template_id, ticket)
        self.wait_window(dialog)
        self.refresh_tickets_list()

    def delete_ticket_tier(self, ticket):
        """Delete a ticket tier"""
        if messagebox.askyesno("Confirm Delete", f"Delete ticket tier '{ticket['tier_name']}'?"):
            self.template_manager.delete_template_ticket_tier(ticket['id'])
            self.refresh_tickets_list()

    def create_prizes_tab(self):
        """Create the prize support management tab"""
        tab = self.tabview.tab("Prize Support")

        # Scrollable content area
        scroll = ctk.CTkScrollableFrame(tab, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Header with title
        header_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text="Prize Support",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

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

        # Save button at bottom (outside scrollable frame)
        btn_frame = ctk.CTkFrame(tab, fg_color="#F5F0F6")
        btn_frame.pack(fill="x", padx=10, pady=10)

        btn_save_template = ctk.CTkButton(
            btn_frame,
            text="Save Template",
            command=self.save_template,
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            height=40
        )
        btn_save_template.pack(fill="x")

    def refresh_prizes_list(self):
        """Refresh the prizes list"""
        # Clear existing widgets
        for widget in self.prizes_list_frame.winfo_children():
            widget.destroy()

        # Get prizes
        prizes = self.template_manager.get_template_prize_items(self.template_id)

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
        if prize['supplier']:
            info_parts.append(f"Supplier: {prize['supplier']}")

        if info_parts:
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
        dialog = TemplatePrizeDialog(self, self.db, self.template_id)
        self.wait_window(dialog)
        self.refresh_prizes_list()

    def edit_prize(self, prize):
        """Show dialog to edit a prize"""
        dialog = TemplatePrizeDialog(self, self.db, self.template_id, prize)
        self.wait_window(dialog)
        self.refresh_prizes_list()

    def delete_prize(self, prize):
        """Delete a prize"""
        if messagebox.askyesno("Confirm Delete", f"Delete prize '{prize['description']}'?"):
            self.template_manager.delete_template_prize_item(prize['id'])
            self.refresh_prizes_list()

    def create_notes_tab(self):
        """Create the notes management tab"""
        tab = self.tabview.tab("Notes")

        # Scrollable content area
        scroll = ctk.CTkScrollableFrame(tab, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Header with title
        header_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header_frame,
            text="Template Notes",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

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

        # Save button at bottom (outside scrollable frame)
        btn_frame = ctk.CTkFrame(tab, fg_color="#F5F0F6")
        btn_frame.pack(fill="x", padx=10, pady=10)

        btn_save_template = ctk.CTkButton(
            btn_frame,
            text="Save Template",
            command=self.save_template,
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            height=40
        )
        btn_save_template.pack(fill="x")

    def refresh_notes_list(self):
        """Refresh the notes list"""
        # Clear existing widgets
        for widget in self.notes_list_frame.winfo_children():
            widget.destroy()

        # Get notes
        notes = self.template_manager.get_template_notes(self.template_id)

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

        # Bottom row - checkbox and buttons
        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.pack(fill="x")

        # Include in printout indicator
        if note['include_in_printout']:
            ctk.CTkLabel(
                bottom,
                text="✓ Included in printout",
                text_color="#4CAF50",
                font=ctk.CTkFont(size=15)
            ).pack(side="left")
        else:
            ctk.CTkLabel(
                bottom,
                text="Not included in printout",
                text_color="#999999",
                font=ctk.CTkFont(size=15)
            ).pack(side="left")

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
        dialog = TemplateNoteDialog(self, self.db, self.template_id)
        self.wait_window(dialog)
        self.refresh_notes_list()

    def edit_note(self, note):
        """Show dialog to edit a note"""
        dialog = TemplateNoteDialog(self, self.db, self.template_id, note)
        self.wait_window(dialog)
        self.refresh_notes_list()

    def delete_note(self, note):
        """Delete a note"""
        if messagebox.askyesno("Confirm Delete", "Delete this note?"):
            self.template_manager.delete_template_note(note['id'])
            self.refresh_notes_list()

    def create_pre_event_tab(self):
        """Create pre-event analysis tab"""
        tab = self.tabview.tab("Pre-Event Analysis")

        # Scrollable content area
        scroll = ctk.CTkScrollableFrame(tab, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        # Header with title
        header_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text="Pre-Event Analysis",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

        # Info message
        ctk.CTkLabel(
            scroll,
            text="Pre-event analysis helps you plan your event's financial projections.\n\nWhen you create an event from this template, the projected labor costs and revenue will be calculated based on the ticket tiers and prize support you've defined.",
            text_color="#666666",
            font=ctk.CTkFont(size=15),
            wraplength=650,
            justify="left"
        ).pack(anchor="w", pady=(0, 20))

        # Show summary of template data that affects projections
        ctk.CTkLabel(
            scroll,
            text="Template Configuration Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(10, 10))

        # Summary frame
        summary_frame = ctk.CTkFrame(scroll, fg_color="white", corner_radius=10)
        summary_frame.pack(fill="x", pady=(0, 20))

        summary_content = ctk.CTkFrame(summary_frame, fg_color="transparent")
        summary_content.pack(fill="x", padx=20, pady=15)

        # Ticket tiers summary
        tickets = self.template_manager.get_template_ticket_tiers(self.template_id)
        if tickets:
            ctk.CTkLabel(
                summary_content,
                text=f"Ticket Tiers: {len(tickets)} tier(s) defined",
                text_color="#4A2D5E",
                font=ctk.CTkFont(size=15)
            ).pack(anchor="w", pady=2)
            for ticket in tickets:
                ctk.CTkLabel(
                    summary_content,
                    text=f"  • {ticket['tier_name']}: ${ticket['price']:.2f}" +
                         (f" ({ticket['quantity_available']} available)" if ticket['quantity_available'] else ""),
                    text_color="#666666",
                    font=ctk.CTkFont(size=15)
                ).pack(anchor="w", padx=(20, 0))
        else:
            ctk.CTkLabel(
                summary_content,
                text="No ticket tiers defined yet",
                text_color="#999999",
                font=ctk.CTkFont(size=15)
            ).pack(anchor="w", pady=2)

        # Prize support summary
        prizes = self.template_manager.get_template_prize_items(self.template_id)
        if prizes:
            total_cost = sum(p.get('total_cost', 0) or 0 for p in prizes)
            ctk.CTkLabel(
                summary_content,
                text=f"Prize Support: {len(prizes)} prize(s) defined, Total Cost: ${total_cost:.2f}",
                text_color="#4A2D5E",
                font=ctk.CTkFont(size=15)
            ).pack(anchor="w", pady=(10, 2))
        else:
            ctk.CTkLabel(
                summary_content,
                text="No prize support defined yet",
                text_color="#999999",
                font=ctk.CTkFont(size=15)
            ).pack(anchor="w", pady=(10, 2))

        # Save button at bottom (outside scrollable frame)
        btn_frame = ctk.CTkFrame(tab, fg_color="#F5F0F6")
        btn_frame.pack(fill="x", padx=10, pady=10)

        btn_save_template = ctk.CTkButton(
            btn_frame,
            text="Save Template",
            command=self.save_template,
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            height=40
        )
        btn_save_template.pack(fill="x")

    def load_checklist_items(self):
        """Load and display checklist items"""
        if not self.template_id:
            return

        # Clear existing
        for widget in self.checklist_scroll.winfo_children():
            widget.destroy()

        # Get items
        items = self.template_manager.get_template_checklist_items(self.template_id)

        if not items:
            msg = ctk.CTkLabel(
                self.checklist_scroll,
                text="No checklist items yet. Add your first item!",
                text_color="#999999"
            )
            msg.pack(pady=20)
            return

        # Group by category
        categories = {}
        for item in items:
            cat_name = item.get('category_name') or 'Uncategorised'
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(item)

        # Display by category
        for cat_name, cat_items in categories.items():
            # Category header
            cat_label = ctk.CTkLabel(
                self.checklist_scroll,
                text=cat_name,
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#8B5FBF",
                anchor="w"
            )
            cat_label.pack(fill="x", padx=10, pady=(10, 5))

            # Items
            for item in cat_items:
                self.create_checklist_item_card(item)

    def create_checklist_item_card(self, item: dict):
        """Create a card for a checklist item"""
        card = ctk.CTkFrame(self.checklist_scroll, fg_color="#F9F5FA")
        card.pack(fill="x", padx=10, pady=2)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)

        # Description
        desc = ctk.CTkLabel(
            content,
            text=item['description'],
            text_color="#4A2D5E",
            anchor="w"
        )
        desc.pack(side="left", fill="x", expand=True)

        # Flags container
        flags_frame = ctk.CTkFrame(content, fg_color="transparent")
        flags_frame.pack(side="right", padx=5)

        # Show flag indicators
        if item.get('show_on_dashboard'):
            dash_label = ctk.CTkLabel(
                flags_frame,
                text="[Dashboard]",
                text_color="#8B5FBF",
                font=ctk.CTkFont(size=15)
            )
            dash_label.pack(side="left", padx=2)

        if item.get('include_in_pdf'):
            pdf_label = ctk.CTkLabel(
                flags_frame,
                text="[PDF]",
                text_color="#8B5FBF",
                font=ctk.CTkFont(size=15)
            )
            pdf_label.pack(side="left", padx=2)

        # Delete button
        btn_delete = ctk.CTkButton(
            content,
            text="✕",
            command=lambda i=item: self.delete_checklist_item(i['id']),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=30,
            height=25
        )
        btn_delete.pack(side="right")

    def add_checklist_item(self):
        """Show dialog to add a checklist item"""
        dialog = ChecklistItemDialog(self, self.db, self.template_id)
        self.wait_window(dialog)
        self.load_checklist_items()

    def delete_checklist_item(self, item_id: int):
        """Delete a checklist item"""
        self.template_manager.delete_checklist_item(item_id)
        self.load_checklist_items()

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
        """Populate form fields with template data"""
        if not self.template_data:
            return

        self.entry_name.insert(0, self.template_data['name'])

        if self.template_data.get('event_type_name'):
            self.combo_event_type.set(self.template_data['event_type_name'])

        if self.template_data.get('format_name'):
            self.combo_format.set(self.template_data['format_name'])

        if self.template_data.get('pairing_method_name'):
            self.combo_pairing_method.set(self.template_data['pairing_method_name'])

        if self.template_data.get('pairing_app_name'):
            self.combo_pairing_app.set(self.template_data['pairing_app_name'])

        if self.template_data.get('max_capacity'):
            self.entry_capacity.insert(0, str(self.template_data['max_capacity']))

        if self.template_data.get('description'):
            self.text_description.insert("1.0", self.template_data['description'])

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
        self.ref_data = self.template_manager.get_reference_data()

        return new_id

    def save_template(self):
        """Save the template"""
        # Validate
        if not self.entry_name.get():
            messagebox.showerror("Validation Error", "Template name is required")
            return

        # Build template data
        template_data = {
            'name': self.entry_name.get(),
            'event_type_id': self.get_id_from_name(self.ref_data['event_types'], self.combo_event_type.get()),
            'playing_format_id': self.get_id_from_name(self.ref_data['playing_formats'], self.combo_format.get()),
            'pairing_method_id': self.get_id_from_name(self.ref_data['pairing_methods'], self.combo_pairing_method.get()),
            'pairing_app_id': self.get_id_from_name(self.ref_data['pairing_apps'], self.combo_pairing_app.get()),
            'max_capacity': int(self.entry_capacity.get()) if self.entry_capacity.get() else None,
            'description': self.text_description.get("1.0", "end-1c")
        }

        # Save to database
        try:
            if self.template_id:
                self.template_manager.update_template(self.template_id, template_data)
                messagebox.showinfo("Success", "Template updated successfully!")
            else:
                new_id = self.template_manager.create_template(template_data)
                self.template_id = new_id
                self.template_data = self.template_manager.get_template_by_id(new_id)
                messagebox.showinfo("Success", "Template created successfully!\n\nYou can now add checklist items.")

                # Recreate tabs to enable checklist tab
                self.tabview.destroy()
                self.create_tabs()
                self.populate_dropdowns()
                self.populate_fields()
                self.load_checklist_items()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {str(e)}")


class ChecklistItemDialog(ctk.CTkToplevel):
    """Dialog for adding a checklist item"""

    def __init__(self, parent, db, template_id: int):
        super().__init__(parent)

        self.db = db
        self.template_manager = TemplateManager(db)
        self.template_id = template_id

        self.title("Add Checklist Item")
        self.geometry("500x400")
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

    def create_form(self):
        """Create the form"""
        frame = ctk.CTkFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Category
        ctk.CTkLabel(frame, text="Category", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))

        categories = self.template_manager.get_checklist_categories()
        category_names = [c['name'] for c in categories]

        self.combo_category = ctk.CTkComboBox(frame, values=category_names, state="readonly")
        self.combo_category.pack(fill="x", pady=(0, 15))
        if category_names:
            self.combo_category.set(category_names[0])

        # Description
        ctk.CTkLabel(frame, text="Description *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_description = ctk.CTkTextbox(frame, height=100)
        self.entry_description.pack(fill="x", pady=(0, 15))

        # Include in PDF checkbox
        self.checkbox_include_pdf = ctk.CTkCheckBox(
            frame,
            text="Include in PDF Printout",
            text_color="#4A2D5E",
            fg_color="#8B5FBF",
            hover_color="#7A4FB0"
        )
        self.checkbox_include_pdf.pack(anchor="w", pady=(0, 10))
        self.checkbox_include_pdf.select()  # Default to checked

        # Show on Dashboard checkbox
        self.checkbox_show_dashboard = ctk.CTkCheckBox(
            frame,
            text="Show on Dashboard (when event is created from template)",
            text_color="#4A2D5E",
            fg_color="#8B5FBF",
            hover_color="#7A4FB0"
        )
        self.checkbox_show_dashboard.pack(anchor="w", pady=(0, 15))
        # Default to unchecked

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Add Item",
            command=self.save_item,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def save_item(self):
        """Save the checklist item"""
        description = self.entry_description.get("1.0", "end-1c").strip()

        if not description:
            messagebox.showerror("Validation Error", "Description is required")
            return

        # Get category ID
        categories = self.template_manager.get_checklist_categories()
        category_id = None
        for cat in categories:
            if cat['name'] == self.combo_category.get():
                category_id = cat['id']
                break

        # Get checkbox values
        include_in_pdf = self.checkbox_include_pdf.get() == 1
        show_on_dashboard = self.checkbox_show_dashboard.get() == 1

        try:
            self.template_manager.add_checklist_item(
                self.template_id,
                category_id,
                description,
                sort_order=0,
                include_in_pdf=include_in_pdf,
                show_on_dashboard=show_on_dashboard
            )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")


class CreateFromTemplateDialog(ctk.CTkToplevel):
    """Dialog for creating an event from a template"""

    def __init__(self, parent, db, template_id: int, template_name: str):
        super().__init__(parent)

        self.db = db
        self.event_manager = EventManager(db)
        self.template_id = template_id
        self.template_name = template_name

        self.title(f"Create Event from Template: {template_name}")
        self.geometry("500x250")
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

    def create_form(self):
        """Create the form"""
        frame = ctk.CTkFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Event Name
        ctk.CTkLabel(frame, text="Event Name", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_name = ctk.CTkEntry(frame, placeholder_text=f"Leave blank to use '{self.template_name}'")
        self.entry_name.pack(fill="x", pady=(0, 15))

        # Event Date
        ctk.CTkLabel(frame, text="Event Date *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_date = DateEntry(frame, selectmode='day', date_pattern='yyyy-mm-dd',
                                    background='#8B5FBF', foreground='white', borderwidth=2)
        self.entry_date.pack(fill="x", pady=(0, 15))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_create = ctk.CTkButton(
            button_frame,
            text="Create Event",
            command=self.create_event,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_create.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def create_event(self):
        """Create the event from template"""
        # Validate date
        if not self.entry_date.get():
            messagebox.showerror("Validation Error", "Event date is required")
            return

        try:
            datetime.strptime(self.entry_date.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Validation Error", "Date must be in YYYY-MM-DD format")
            return

        # Create event
        try:
            event_name = self.entry_name.get().strip() or None
            event_id = self.event_manager.create_event_from_template(
                self.template_id,
                self.entry_date.get(),
                event_name
            )

            messagebox.showinfo("Success", "Event created successfully from template!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create event: {str(e)}")


class TemplateTicketTierDialog(ctk.CTkToplevel):
    """Dialog for adding/editing template ticket tiers"""

    def __init__(self, parent, db, template_id: int, ticket: Optional[dict] = None):
        super().__init__(parent)

        self.db = db
        self.template_manager = TemplateManager(db)
        self.template_id = template_id
        self.ticket = ticket

        self.title("Edit Ticket Tier" if ticket else "Add Ticket Tier")
        self.geometry("500x350")
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

    def create_form(self):
        """Create the form"""
        frame = ctk.CTkFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tier Name
        ctk.CTkLabel(frame, text="Tier Name *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_tier_name = ctk.CTkEntry(frame, placeholder_text="e.g., Early Bird, Regular")
        self.entry_tier_name.pack(fill="x", pady=(0, 15))

        # Price
        ctk.CTkLabel(frame, text="Price *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_price = ctk.CTkEntry(frame, placeholder_text="e.g., 10.00")
        self.entry_price.pack(fill="x", pady=(0, 15))

        # Quantity Available
        ctk.CTkLabel(frame, text="Quantity Available", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_quantity = ctk.CTkEntry(frame, placeholder_text="e.g., 20 (optional)")
        self.entry_quantity.pack(fill="x", pady=(0, 15))

        # Populate if editing
        if self.ticket:
            self.entry_tier_name.insert(0, self.ticket['tier_name'])
            self.entry_price.insert(0, str(self.ticket['price']))
            if self.ticket.get('quantity_available'):
                self.entry_quantity.insert(0, str(self.ticket['quantity_available']))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_ticket,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def save_ticket(self):
        """Save the ticket tier"""
        # Validate
        if not self.entry_tier_name.get():
            messagebox.showerror("Validation Error", "Tier name is required")
            return
        if not self.entry_price.get():
            messagebox.showerror("Validation Error", "Price is required")
            return

        try:
            price = float(self.entry_price.get())
        except ValueError:
            messagebox.showerror("Validation Error", "Price must be a valid number")
            return

        quantity = None
        if self.entry_quantity.get():
            try:
                quantity = int(self.entry_quantity.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Quantity must be a valid integer")
                return

        try:
            if self.ticket:
                self.template_manager.update_template_ticket_tier(
                    self.ticket['id'],
                    self.entry_tier_name.get(),
                    price,
                    quantity
                )
            else:
                self.template_manager.add_template_ticket_tier(
                    self.template_id,
                    self.entry_tier_name.get(),
                    price,
                    quantity
                )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save ticket tier: {str(e)}")


class TemplatePrizeDialog(ctk.CTkToplevel):
    """Dialog for adding/editing template prize items"""

    def __init__(self, parent, db, template_id: int, prize: Optional[dict] = None):
        super().__init__(parent)

        self.db = db
        self.template_manager = TemplateManager(db)
        self.template_id = template_id
        self.prize = prize

        self.title("Edit Prize" if prize else "Add Prize")
        self.geometry("450x600")
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

    def create_form(self):
        """Create the form"""
        # Use scrollable frame
        frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Description
        ctk.CTkLabel(frame, text="Prize Description *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_description = ctk.CTkEntry(frame, placeholder_text="e.g., 1st Place - Booster Box")
        self.entry_description.pack(fill="x", pady=(0, 15))

        # Quantity
        ctk.CTkLabel(frame, text="Quantity", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_quantity = ctk.CTkEntry(frame, placeholder_text="e.g., 1")
        self.entry_quantity.pack(fill="x", pady=(0, 15))

        # Cost per item
        ctk.CTkLabel(frame, text="Cost Per Item (AUD)", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_cost_per_item = ctk.CTkEntry(frame, placeholder_text="e.g., 150.00")
        self.entry_cost_per_item.pack(fill="x", pady=(0, 15))

        # Total cost (calculated automatically)
        ctk.CTkLabel(frame, text="Total Cost (AUD)", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_total_cost = ctk.CTkEntry(frame, placeholder_text="Auto-calculated")
        self.entry_total_cost.pack(fill="x", pady=(0, 15))

        # Auto-calculate total on quantity/cost changes
        self.entry_quantity.bind('<KeyRelease>', self.calculate_total)
        self.entry_cost_per_item.bind('<KeyRelease>', self.calculate_total)

        # Supplier
        ctk.CTkLabel(frame, text="Supplier", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_supplier = ctk.CTkEntry(frame, placeholder_text="e.g., WOTC")
        self.entry_supplier.pack(fill="x", pady=(0, 15))

        # Populate if editing
        if self.prize:
            self.entry_description.insert(0, self.prize['description'])
            if self.prize.get('quantity'):
                self.entry_quantity.insert(0, str(self.prize['quantity']))
            if self.prize.get('cost_per_item'):
                self.entry_cost_per_item.insert(0, str(self.prize['cost_per_item']))
            if self.prize.get('total_cost'):
                self.entry_total_cost.insert(0, str(self.prize['total_cost']))
            if self.prize.get('supplier'):
                self.entry_supplier.insert(0, self.prize['supplier'])

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_prize,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def calculate_total(self, event=None):
        """Calculate total cost"""
        try:
            qty = int(self.entry_quantity.get() or 0)
            cost_per = float(self.entry_cost_per_item.get() or 0)
            total = qty * cost_per
            self.entry_total_cost.delete(0, 'end')
            self.entry_total_cost.insert(0, f"{total:.2f}")
        except:
            pass

    def save_prize(self):
        """Save the prize"""
        # Validate
        description = self.entry_description.get().strip()
        if not description:
            messagebox.showerror("Validation Error", "Description is required")
            return

        quantity = None
        if self.entry_quantity.get():
            try:
                quantity = int(self.entry_quantity.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Quantity must be a valid integer")
                return

        cost_per_item = None
        if self.entry_cost_per_item.get():
            try:
                cost_per_item = float(self.entry_cost_per_item.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Cost per item must be a valid number")
                return

        total_cost = None
        if self.entry_total_cost.get():
            try:
                total_cost = float(self.entry_total_cost.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Total cost must be a valid number")
                return

        supplier = self.entry_supplier.get().strip() or None

        try:
            if self.prize:
                self.template_manager.update_template_prize_item(
                    self.prize['id'],
                    description,
                    quantity,
                    cost_per_item,
                    total_cost,
                    supplier
                )
            else:
                self.template_manager.add_template_prize_item(
                    self.template_id,
                    description,
                    quantity,
                    cost_per_item,
                    total_cost,
                    supplier
                )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save prize: {str(e)}")


class TemplateNoteDialog(ctk.CTkToplevel):
    """Dialog for adding/editing template notes"""

    def __init__(self, parent, db, template_id: int, note: Optional[dict] = None):
        super().__init__(parent)

        self.db = db
        self.template_manager = TemplateManager(db)
        self.template_id = template_id
        self.note = note

        self.title("Edit Note" if note else "Add Note")
        self.geometry("500x400")
        self.configure(fg_color="#F5F0F6")

        self.transient(parent)
        self.grab_set()

        self.create_form()

    def create_form(self):
        """Create the form"""
        frame = ctk.CTkFrame(self, fg_color="#F5F0F6")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Note text
        ctk.CTkLabel(frame, text="Note *", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        self.entry_note = ctk.CTkTextbox(frame, height=200)
        self.entry_note.pack(fill="x", pady=(0, 15))

        # Include in printout checkbox
        self.var_include = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            frame,
            text="Include in printout",
            variable=self.var_include,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            checkmark_color="white"
        ).pack(anchor="w", pady=(0, 15))

        # Populate if editing
        if self.note:
            self.entry_note.insert("1.0", self.note['note_text'])
            self.var_include.set(bool(self.note['include_in_printout']))

        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        btn_save = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_note,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            text_color="white",
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def save_note(self):
        """Save the note"""
        # Validate
        note_text = self.entry_note.get("1.0", "end-1c").strip()
        if not note_text:
            messagebox.showerror("Validation Error", "Note text is required")
            return

        try:
            if self.note:
                self.template_manager.update_template_note(
                    self.note['id'],
                    note_text,
                    self.var_include.get()
                )
            else:
                self.template_manager.add_template_note(
                    self.template_id,
                    note_text,
                    self.var_include.get()
                )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save note: {str(e)}")
