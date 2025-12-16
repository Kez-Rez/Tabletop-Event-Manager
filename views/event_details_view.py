"""Detailed event view with all functionality"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from event_manager import EventManager
from datetime import datetime
from typing import Optional
import os
import shutil

class EventDetailsView(ctk.CTkToplevel):
    """Comprehensive event details window"""

    def __init__(self, parent, db, event_id: int):
        super().__init__(parent)

        self.db = db
        self.event_manager = EventManager(db)
        self.event_id = event_id
        self.event_data = self.event_manager.get_event_by_id(event_id)

        if not self.event_data:
            messagebox.showerror("Error", "Event not found")
            self.destroy()
            return

        # Configure window
        self.title(f"Event Details: {self.event_data['event_name']}")
        self.geometry("1100x750")
        self.configure(fg_color="#F5F0F6")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Create tabbed interface
        self.create_tabs()

    def create_tabs(self):
        """Create tabbed interface"""
        # Tab view
        self.tabview = ctk.CTkTabview(self, fg_color="#F5F0F6")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        # Create tabs
        self.tabview.add("Overview")
        self.tabview.add("Checklist")
        self.tabview.add("Financial")
        self.tabview.add("Tickets")
        self.tabview.add("Materials & Prize Support")
        self.tabview.add("Notes")
        self.tabview.add("Pre-Event")
        self.tabview.add("Post-Event")

        # Populate tabs
        self.create_overview_tab()
        self.create_checklist_tab()
        self.create_financial_tab()
        self.create_tickets_tab()
        self.create_materials_prizes_tab()
        self.create_notes_tab()
        self.create_pre_event_tab()
        self.create_post_event_tab()

    def create_overview_tab(self):
        """Create overview tab"""
        tab = self.tabview.tab("Overview")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Header with event name and edit button
        header_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        # Event name
        ctk.CTkLabel(
            header_frame,
            text=self.event_data['event_name'],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

        # Edit button
        btn_edit = ctk.CTkButton(
            header_frame,
            text="Edit Event Details",
            command=self.edit_event_details,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=150,
            height=35
        )
        btn_edit.pack(side="right")

        # Event details
        details = [
            ("Date", self.format_date(self.event_data['event_date'])),
            ("Start Time", self.format_time(self.event_data.get('start_time'))),
            ("End Time", self.format_time(self.event_data.get('end_time'))),
            ("Event Type", self.event_data.get('event_type_name')),
            ("Playing Format", self.event_data.get('format_name')),
            ("Pairing Method", self.event_data.get('pairing_method_name')),
            ("Pairing App", self.event_data.get('pairing_app_name')),
            ("Number of Rounds", str(self.event_data.get('number_of_rounds')) if self.event_data.get('number_of_rounds') else "Not set"),
            ("Max Capacity", str(self.event_data.get('max_capacity')) if self.event_data.get('max_capacity') else "Not set"),
        ]

        for label, value in details:
            if value:
                self.create_detail_row(scroll, label, value)

        # Description
        if self.event_data.get('description'):
            ctk.CTkLabel(
                scroll,
                text="Description",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#4A2D5E"
            ).pack(anchor="w", pady=(20, 5))

            desc_box = ctk.CTkTextbox(scroll, height=100, fg_color="white")
            desc_box.insert("1.0", self.event_data['description'])
            desc_box.configure(state="disabled")
            desc_box.pack(fill="x", pady=(0, 20))

        # Status section
        ctk.CTkLabel(
            scroll,
            text="Status",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", pady=(20, 10))

        status_frame = ctk.CTkFrame(scroll, fg_color="white")
        status_frame.pack(fill="x", pady=(0, 20))

        # Status toggles
        self.var_organised = ctk.BooleanVar(value=bool(self.event_data.get('is_organised')))
        self.var_tickets_live = ctk.BooleanVar(value=bool(self.event_data.get('tickets_live')))
        self.var_advertised = ctk.BooleanVar(value=bool(self.event_data.get('is_advertised')))

        ctk.CTkCheckBox(
            status_frame,
            text="Fully Organised",
            variable=self.var_organised,
            command=self.save_status,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        ).pack(anchor="w", padx=15, pady=5)

        ctk.CTkCheckBox(
            status_frame,
            text="Tickets Live",
            variable=self.var_tickets_live,
            command=self.save_status,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        ).pack(anchor="w", padx=15, pady=5)

        ctk.CTkCheckBox(
            status_frame,
            text="Advertised",
            variable=self.var_advertised,
            command=self.save_status,
            text_color="#4A2D5E",
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        ).pack(anchor="w", padx=15, pady=5)

        # Event completion section (separated for visibility)
        ctk.CTkLabel(status_frame, text="", height=1).pack()  # Spacer

        completion_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        completion_frame.pack(fill="x", padx=15, pady=10)

        # Show appropriate button based on completion status
        if self.event_data.get('is_completed'):
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
                text="Undo",
                command=self.mark_event_incomplete,
                fg_color="#E57373",
                hover_color="#D32F2F",
                text_color="white",
                width=80,
                height=32
            ).pack(side="left")
        else:
            # Show mark as complete button
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

    def create_checklist_tab(self):
        """Create checklist tab"""
        tab = self.tabview.tab("Checklist")

        # Header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header,
            text="Event Checklist",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

        btn_add = ctk.CTkButton(
            header,
            text="+ Add Item",
            command=self.add_checklist_item,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=100
        )
        btn_add.pack(side="right")

        # Scrollable checklist
        self.checklist_scroll = ctk.CTkScrollableFrame(tab, fg_color="white")
        self.checklist_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_checklist_items()

    def create_financial_tab(self):
        """Create financial tracking tab"""
        tab = self.tabview.tab("Financial")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Labour cost section
        ctk.CTkLabel(
            scroll,
            text="Labour Cost",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 10))

        labour_frame = ctk.CTkFrame(scroll, fg_color="white")
        labour_frame.pack(fill="x", pady=(0, 20))

        labour_content = ctk.CTkFrame(labour_frame, fg_color="transparent")
        labour_content.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(labour_content, text="Number of Staff:", text_color="#4A2D5E").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_staff_count = ctk.CTkEntry(labour_content, width=100, placeholder_text="1")
        self.entry_staff_count.grid(row=0, column=1, padx=10, pady=5)

        btn_calc_labour = ctk.CTkButton(
            labour_content,
            text="Calculate Labour Cost",
            command=self.calculate_labour,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=150
        )
        btn_calc_labour.grid(row=0, column=2, padx=10, pady=5)

        self.label_labour_cost = ctk.CTkLabel(
            labour_content,
            text="Cost: Not calculated",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold")
        )
        self.label_labour_cost.grid(row=0, column=3, padx=10, pady=5)

        # Load labour cost if exists
        self.load_labour_cost()

        # Other costs section
        ctk.CTkLabel(
            scroll,
            text="Other Costs",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(20, 10))

        costs_header = ctk.CTkFrame(scroll, fg_color="transparent")
        costs_header.pack(fill="x", pady=(0, 10))

        btn_add_cost = ctk.CTkButton(
            costs_header,
            text="+ Add Cost",
            command=self.add_cost,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=100
        )
        btn_add_cost.pack(side="right")

        self.costs_scroll = ctk.CTkScrollableFrame(scroll, fg_color="white", height=200)
        self.costs_scroll.pack(fill="both", expand=True)

        self.load_costs()

        # Total costs summary
        self.label_total_costs = ctk.CTkLabel(
            scroll,
            text="Total Costs: $0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        )
        self.label_total_costs.pack(anchor="e", pady=(10, 0))

    def create_tickets_tab(self):
        """Create tickets tab"""
        tab = self.tabview.tab("Tickets")

        # Header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header,
            text="Ticket Tiers",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

        btn_add = ctk.CTkButton(
            header,
            text="+ Add Tier",
            command=self.add_ticket_tier,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=100
        )
        btn_add.pack(side="right")

        # Scrollable tickets list
        self.tickets_scroll = ctk.CTkScrollableFrame(tab, fg_color="white")
        self.tickets_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_ticket_tiers()

    def create_materials_prizes_tab(self):
        """Create materials and prizes tab"""
        tab = self.tabview.tab("Materials & Prize Support")

        # Header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header,
            text="Materials & Prize Support",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

        btn_add = ctk.CTkButton(
            header,
            text="+ Add Item",
            command=self.add_prize,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=100
        )
        btn_add.pack(side="right")

        # Scrollable prizes list
        self.prizes_scroll = ctk.CTkScrollableFrame(tab, fg_color="white")
        self.prizes_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_prizes()

    def create_notes_tab(self):
        """Create notes tab"""
        tab = self.tabview.tab("Notes")

        # Header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header,
            text="Event Notes",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

        btn_add = ctk.CTkButton(
            header,
            text="+ Add Note",
            command=self.add_note,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=100
        )
        btn_add.pack(side="right")

        # Scrollable notes list
        self.notes_scroll = ctk.CTkScrollableFrame(tab, fg_color="white")
        self.notes_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_notes()

    def create_pre_event_tab(self):
        """Create pre-event cost projection tab"""
        tab = self.tabview.tab("Pre-Event")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll,
            text="Pre-Event Analysis",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 20))

        self.load_pre_event_analysis(scroll)

    def create_post_event_tab(self):
        """Create post-event analysis tab"""
        tab = self.tabview.tab("Post-Event")

        scroll = ctk.CTkScrollableFrame(tab, fg_color="#F5F0F6")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll,
            text="Post-Event Analysis",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(0, 20))

        # Load or create analysis form (always show, not just when completed)
        self.load_post_event_analysis(scroll)

    # Helper methods
    def format_date(self, date_str: Optional[str]) -> str:
        """Format date for display"""
        if not date_str:
            return "Not set"
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%A, %d %B %Y')
        except:
            return date_str

    def format_time(self, time_str: Optional[str]) -> str:
        """Format time for display"""
        if not time_str:
            return "Not set"
        try:
            # Remove seconds if present
            return time_str.rsplit(':', 1)[0]
        except:
            return time_str

    def create_detail_row(self, parent, label: str, value: str):
        """Create a detail row"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=2)

        ctk.CTkLabel(
            frame,
            text=f"{label}:",
            font=ctk.CTkFont(weight="bold"),
            text_color="#4A2D5E",
            width=150,
            anchor="w"
        ).pack(side="left")

        ctk.CTkLabel(
            frame,
            text=value,
            text_color="#666666",
            anchor="w"
        ).pack(side="left")

    def save_status(self):
        """Save status changes (for checkboxes only)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE events
            SET is_organised = ?, tickets_live = ?, is_advertised = ?
            WHERE id = ?
        ''', (
            self.var_organised.get(),
            self.var_tickets_live.get(),
            self.var_advertised.get(),
            self.event_id
        ))

        conn.commit()
        conn.close()

        # Reload event data
        self.event_data = self.event_manager.get_event_by_id(self.event_id)

    def mark_event_complete(self):
        """Mark event as completed and navigate to post-event analysis"""
        # Confirm action
        if not messagebox.askyesno("Mark as Completed",
            "Mark this event as completed?\n\nThis will take you to the Post-Event Analysis tab where you can enter event results."):
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE events
            SET is_completed = 1
            WHERE id = ?
        ''', (self.event_id,))

        conn.commit()
        conn.close()

        # Reload event data
        self.event_data = self.event_manager.get_event_by_id(self.event_id)

        # Recreate the overview tab to show the new status
        self.tabview.delete("Overview")
        self.tabview.add("Overview")
        self.create_overview_tab()

        # Reload and switch to post-event tab
        self.tabview.delete("Post-Event")
        self.tabview.add("Post-Event")
        self.create_post_event_tab()
        self.tabview.set("Post-Event")

        messagebox.showinfo("Event Completed", "Event marked as completed. You can now enter post-event analysis data.")

    def mark_event_incomplete(self):
        """Undo event completion status"""
        # Confirm action
        if not messagebox.askyesno("Undo Completion",
            "Mark this event as not completed?\n\nThis will revert the completion status."):
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE events
            SET is_completed = 0
            WHERE id = ?
        ''', (self.event_id,))

        conn.commit()
        conn.close()

        # Reload event data
        self.event_data = self.event_manager.get_event_by_id(self.event_id)

        # Recreate the overview tab to show the new status
        self.tabview.delete("Overview")
        self.tabview.add("Overview")
        self.create_overview_tab()

        # Switch back to overview tab
        self.tabview.set("Overview")

        messagebox.showinfo("Status Updated", "Event marked as not completed.")

    def load_checklist_items(self):
        """Load checklist items"""
        for widget in self.checklist_scroll.winfo_children():
            widget.destroy()

        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT ci.*, cat.name as category_name
            FROM event_checklist_items ci
            LEFT JOIN checklist_categories cat ON ci.category_id = cat.id
            WHERE ci.event_id = ?
            ORDER BY cat.sort_order, ci.sort_order
        ''', (self.event_id,))

        items = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not items:
            ctk.CTkLabel(
                self.checklist_scroll,
                text="No checklist items yet. Add your first item!",
                text_color="#999999"
            ).pack(pady=20)
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
            ctk.CTkLabel(
                self.checklist_scroll,
                text=cat_name,
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#8B5FBF",
                anchor="w"
            ).pack(fill="x", padx=10, pady=(10, 5))

            for item in cat_items:
                self.create_checklist_item_card(item)

    def create_checklist_item_card(self, item: dict):
        """Create checklist item card"""
        card = ctk.CTkFrame(self.checklist_scroll, fg_color="#F9F5FA")
        card.pack(fill="x", padx=10, pady=2)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)

        # Checkbox
        var = ctk.BooleanVar(value=bool(item['is_completed']))
        chk = ctk.CTkCheckBox(
            content,
            text=item['description'],
            variable=var,
            command=lambda i=item, v=var: self.toggle_checklist_item(i['id'], v.get()),
            text_color="#4A2D5E",
            border_color="black",
            fg_color="white",
            hover_color="#E6D9F2",
            checkmark_color="black"
        )
        chk.pack(side="left", fill="x", expand=True)

        # Reorder buttons
        btn_up = ctk.CTkButton(
            content,
            text="▲",
            command=lambda i=item: self.move_checklist_item_up(i['id'], i['category_id']),
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=30,
            height=25
        )
        btn_up.pack(side="right", padx=2)

        btn_down = ctk.CTkButton(
            content,
            text="▼",
            command=lambda i=item: self.move_checklist_item_down(i['id'], i['category_id']),
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=30,
            height=25
        )
        btn_down.pack(side="right", padx=2)

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
        btn_delete.pack(side="right", padx=2)

    def add_checklist_item(self):
        """Add checklist item"""
        from views.event_dialogs import ChecklistItemDialog
        dialog = ChecklistItemDialog(self, self.db, self.event_id)
        self.wait_window(dialog)
        self.load_checklist_items()

    def toggle_checklist_item(self, item_id: int, completed: bool):
        """Toggle checklist item completion"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE event_checklist_items SET is_completed = ? WHERE id = ?', (completed, item_id))
        conn.commit()
        conn.close()

    def delete_checklist_item(self, item_id: int):
        """Delete checklist item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM event_checklist_items WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        self.load_checklist_items()

    def move_checklist_item_up(self, item_id: int, category_id: int):
        """Move checklist item up in the order"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get current item's sort_order
        cursor.execute('''
            SELECT sort_order FROM event_checklist_items
            WHERE id = ? AND event_id = ?
        ''', (item_id, self.event_id))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return

        current_order = result['sort_order']

        # Find the item immediately before this one in the same category
        cursor.execute('''
            SELECT id, sort_order FROM event_checklist_items
            WHERE event_id = ? AND category_id IS ? AND sort_order < ?
            ORDER BY sort_order DESC
            LIMIT 1
        ''', (self.event_id, category_id, current_order))
        prev_item = cursor.fetchone()

        if prev_item:
            # Swap sort_order values
            cursor.execute('''
                UPDATE event_checklist_items
                SET sort_order = ?
                WHERE id = ?
            ''', (prev_item['sort_order'], item_id))

            cursor.execute('''
                UPDATE event_checklist_items
                SET sort_order = ?
                WHERE id = ?
            ''', (current_order, prev_item['id']))

            conn.commit()

        conn.close()
        self.load_checklist_items()

    def move_checklist_item_down(self, item_id: int, category_id: int):
        """Move checklist item down in the order"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get current item's sort_order
        cursor.execute('''
            SELECT sort_order FROM event_checklist_items
            WHERE id = ? AND event_id = ?
        ''', (item_id, self.event_id))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return

        current_order = result['sort_order']

        # Find the item immediately after this one in the same category
        cursor.execute('''
            SELECT id, sort_order FROM event_checklist_items
            WHERE event_id = ? AND category_id IS ? AND sort_order > ?
            ORDER BY sort_order ASC
            LIMIT 1
        ''', (self.event_id, category_id, current_order))
        next_item = cursor.fetchone()

        if next_item:
            # Swap sort_order values
            cursor.execute('''
                UPDATE event_checklist_items
                SET sort_order = ?
                WHERE id = ?
            ''', (next_item['sort_order'], item_id))

            cursor.execute('''
                UPDATE event_checklist_items
                SET sort_order = ?
                WHERE id = ?
            ''', (current_order, next_item['id']))

            conn.commit()

        conn.close()
        self.load_checklist_items()

    def calculate_labour(self):
        """Calculate labour cost"""
        try:
            staff_count = int(self.entry_staff_count.get() or 1)
            cost = self.event_manager.calculate_labour_cost(self.event_id, staff_count)
            self.label_labour_cost.configure(text=f"Cost: ${cost:.2f}")
            self.load_costs()  # Reload costs to update total
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate labour cost: {str(e)}")

    def load_labour_cost(self):
        """Load existing labour cost"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM labour_costs WHERE event_id = ?', (self.event_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            self.entry_staff_count.insert(0, str(result['staff_count']))
            self.label_labour_cost.configure(text=f"Cost: ${result['total_cost']:.2f}")

    def load_costs(self):
        """Load other costs"""
        for widget in self.costs_scroll.winfo_children():
            widget.destroy()

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get labour cost
        cursor.execute('SELECT total_cost FROM labour_costs WHERE event_id = ?', (self.event_id,))
        labour = cursor.fetchone()
        labour_cost = float(labour['total_cost']) if labour else 0.0

        # Get other costs
        cursor.execute('SELECT * FROM event_costs WHERE event_id = ? ORDER BY created_at', (self.event_id,))
        costs = [dict(row) for row in cursor.fetchall()]
        conn.close()

        total = labour_cost
        for cost in costs:
            total += float(cost['amount'])
            # Create cost card (simplified)

        self.label_total_costs.configure(text=f"Total Costs: ${total:.2f}")

    def add_cost(self):
        """Add cost - placeholder"""
        messagebox.showinfo("Add Cost", "Add cost functionality - TODO")

    def load_ticket_tiers(self):
        """Load ticket tiers - placeholder"""
        for widget in self.tickets_scroll.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.tickets_scroll,
            text="Ticket management coming soon...",
            text_color="#999999"
        ).pack(pady=20)

    def add_ticket_tier(self):
        """Add ticket tier - placeholder"""
        messagebox.showinfo("Add Tier", "Ticket tier functionality - TODO")

    def load_prizes(self):
        """Load all prizes for this event"""
        for widget in self.prizes_scroll.winfo_children():
            widget.destroy()

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM prize_items
            WHERE event_id = ?
            ORDER BY created_at DESC
        ''', (self.event_id,))
        prizes = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not prizes:
            ctk.CTkLabel(
                self.prizes_scroll,
                text="No prizes yet. Add your first prize!",
                text_color="#999999"
            ).pack(pady=20)
            return

        for prize in prizes:
            self.create_prize_card(prize)

    def create_prize_card(self, prize: dict):
        """Create visual card for a prize or material"""
        card = ctk.CTkFrame(self.prizes_scroll, fg_color="#F9F5FA")
        card.pack(fill="x", padx=10, pady=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)

        # Left side - prize details
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        # Description with item type
        desc_frame = ctk.CTkFrame(left, fg_color="transparent")
        desc_frame.pack(anchor="w")

        ctk.CTkLabel(
            desc_frame,
            text=prize['description'],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(side="left")

        # Item type badge
        item_type = prize.get('item_type', 'prize')
        type_color = "#9C27B0" if item_type == "material" else "#8B5FBF"
        type_text = "Material" if item_type == "material" else "Prize"

        ctk.CTkLabel(
            desc_frame,
            text=type_text,
            fg_color=type_color,
            text_color="white",
            corner_radius=8,
            padx=6,
            pady=2,
            font=ctk.CTkFont(size=15)
        ).pack(side="left", padx=(8, 0))

        # Details row
        details_frame = ctk.CTkFrame(left, fg_color="transparent")
        details_frame.pack(anchor="w", pady=(5, 0))

        quantity = prize.get('quantity') or 0
        cost_per = prize.get('cost_per_item') or 0
        total_cost = prize.get('total_cost') or 0
        handed_out = prize.get('quantity_handed_out') or 0

        ctk.CTkLabel(
            details_frame,
            text=f"Quantity: {quantity} | Cost per item: ${cost_per:.2f} | Total: ${total_cost:.2f}",
            text_color="#666666",
            font=ctk.CTkFont(size=15)
        ).pack(side="left")

        # Badges row
        badges_frame = ctk.CTkFrame(left, fg_color="transparent")
        badges_frame.pack(anchor="w", pady=(5, 0))

        # Received badge
        if prize.get('is_received'):
            received_badge = ctk.CTkLabel(
                badges_frame,
                text="Received",
                fg_color="#81C784",
                text_color="white",
                corner_radius=10,
                padx=8,
                pady=2
            )
            received_badge.pack(side="left", padx=(0, 5))

        # Handed out display
        handed_label = ctk.CTkLabel(
            badges_frame,
            text=f"Handed out: {handed_out}/{quantity}",
            fg_color="#8B5FBF",
            text_color="white",
            corner_radius=10,
            padx=8,
            pady=2
        )
        handed_label.pack(side="left", padx=(0, 5))

        # Show remaining if applicable
        if quantity > 0:
            remaining = quantity - handed_out
            if remaining > 0:
                remaining_badge = ctk.CTkLabel(
                    badges_frame,
                    text=f"{remaining} remaining",
                    fg_color="#FFB74D",
                    text_color="white",
                    corner_radius=10,
                    padx=8,
                    pady=2
                )
                remaining_badge.pack(side="left")
            elif remaining < 0:
                extras_badge = ctk.CTkLabel(
                    badges_frame,
                    text=f"{abs(remaining)} extras given",
                    fg_color="#E57373",
                    text_color="white",
                    corner_radius=10,
                    padx=8,
                    pady=2
                )
                extras_badge.pack(side="left")

        # Right side - action buttons
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")

        btn_edit = ctk.CTkButton(
            right,
            text="Edit",
            command=lambda p=prize: self.edit_prize(p),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=70,
            height=30
        )
        btn_edit.pack(side="left", padx=2)

        btn_delete = ctk.CTkButton(
            right,
            text="Delete",
            command=lambda p=prize: self.delete_prize(p),
            fg_color="#E57373",
            hover_color="#D32F2F",
            width=70,
            height=30
        )
        btn_delete.pack(side="left", padx=2)

    def add_prize(self):
        """Open PrizeDialog to add new prize"""
        from views.event_dialogs import PrizeDialog
        dialog = PrizeDialog(self, self.db, self.event_id)
        self.wait_window(dialog)
        self.load_prizes()

    def edit_prize(self, prize_data: dict):
        """Edit an existing prize"""
        from views.event_dialogs import PrizeDialog
        dialog = PrizeDialog(self, self.db, self.event_id, prize_data)
        self.wait_window(dialog)
        self.load_prizes()

    def delete_prize(self, prize_data: dict):
        """Delete a prize"""
        if messagebox.askyesno("Confirm Delete", f"Delete prize '{prize_data['description']}'?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM prize_items WHERE id = ?', (prize_data['id'],))
            conn.commit()
            conn.close()
            self.load_prizes()
            messagebox.showinfo("Success", "Prize deleted")

    def load_notes(self):
        """Load all notes for this event"""
        for widget in self.notes_scroll.winfo_children():
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
                self.notes_scroll,
                text="No notes yet. Add your first note!",
                text_color="#999999"
            ).pack(pady=20)
            return

        for note in notes:
            self.create_note_card(note)

    def create_note_card(self, note: dict):
        """Create visual card for a note"""
        card = ctk.CTkFrame(self.notes_scroll, fg_color="#F9F5FA")
        card.pack(fill="x", padx=10, pady=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)

        # Left side - note content
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        # Note text
        note_text = note.get('note_text', '')
        # Truncate if too long
        display_text = note_text if len(note_text) <= 200 else note_text[:200] + "..."

        ctk.CTkLabel(
            left,
            text=display_text,
            text_color="#4A2D5E",
            anchor="w",
            wraplength=600,
            justify="left"
        ).pack(anchor="w")

        # Badges row
        badges_frame = ctk.CTkFrame(left, fg_color="transparent")
        badges_frame.pack(anchor="w", pady=(8, 0))

        # Include in printout badge
        if note.get('include_in_printout'):
            print_badge = ctk.CTkLabel(
                badges_frame,
                text="Include in printout",
                fg_color="#64B5F6",
                text_color="white",
                corner_radius=10,
                padx=8,
                pady=2
            )
            print_badge.pack(side="left", padx=(0, 5))

        # Send to template badge
        if note.get('send_to_template'):
            template_badge = ctk.CTkLabel(
                badges_frame,
                text="Sent to template",
                fg_color="#9C27B0",
                text_color="white",
                corner_radius=10,
                padx=8,
                pady=2
            )
            template_badge.pack(side="left", padx=(0, 5))

        # Timestamp
        if note.get('created_at'):
            timestamp = ctk.CTkLabel(
                badges_frame,
                text=note['created_at'][:10],  # Just the date part
                text_color="#999999",
                font=ctk.CTkFont(size=15)
            )
            timestamp.pack(side="left", padx=(5, 0))

        # Right side - action buttons
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")

        btn_edit = ctk.CTkButton(
            right,
            text="Edit",
            command=lambda n=note: self.edit_note(n),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=70,
            height=30
        )
        btn_edit.pack(side="left", padx=2)

        btn_delete = ctk.CTkButton(
            right,
            text="Delete",
            command=lambda n=note: self.delete_note(n),
            fg_color="#E57373",
            hover_color="#D32F2F",
            width=70,
            height=30
        )
        btn_delete.pack(side="left", padx=2)

    def add_note(self):
        """Open NoteDialog to add new note"""
        from views.event_dialogs import NoteDialog
        template_id = self.event_data.get('template_id')
        dialog = NoteDialog(self, self.db, self.event_id, template_id)
        self.wait_window(dialog)
        self.load_notes()

    def edit_note(self, note_data: dict):
        """Edit an existing note"""
        from views.event_dialogs import NoteDialog
        template_id = self.event_data.get('template_id')
        dialog = NoteDialog(self, self.db, self.event_id, template_id, note_data)
        self.wait_window(dialog)
        self.load_notes()

    def delete_note(self, note_data: dict):
        """Delete a note"""
        if messagebox.askyesno("Confirm Delete", "Delete this note?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM event_notes WHERE id = ?', (note_data['id'],))
            conn.commit()
            conn.close()
            self.load_notes()
            messagebox.showinfo("Success", "Note deleted")

    def load_pre_event_analysis(self, parent):
        """Load pre-event cost projection and break-even analysis"""
        # Coming soon message
        ctk.CTkLabel(
            parent,
            text="Coming soon...",
            font=ctk.CTkFont(size=15),
            text_color="#999999"
        ).pack(expand=True)

    def load_post_event_analysis(self, parent):
        """Load post-event analysis form"""
        # Labour Costs Section
        labour_header = ctk.CTkFrame(parent, fg_color="transparent")
        labour_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            labour_header,
            text="Labour Costs",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

        btn_add_labour = ctk.CTkButton(
            labour_header,
            text="+ Add Labour Entry",
            command=self.add_labour_cost,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=140
        )
        btn_add_labour.pack(side="right")

        # Labour costs list
        self.labour_scroll = ctk.CTkScrollableFrame(parent, fg_color="white", height=200)
        self.labour_scroll.pack(fill="x", padx=10, pady=(0, 20))

        self.load_labour_costs()

        # Total Labour Cost Display
        total_labour = self.event_manager.get_total_labour_cost(self.event_id)
        ctk.CTkLabel(
            parent,
            text=f"Total Labour Cost: ${total_labour:.2f}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="e", padx=10, pady=(0, 20))

        # Ticket Sales Section
        ctk.CTkLabel(
            parent,
            text="Ticket Sales",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(10, 10))

        # Get ticket tiers
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM ticket_tiers
            WHERE event_id = ?
            ORDER BY price DESC
        ''', (self.event_id,))
        ticket_tiers = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if ticket_tiers:
            ticket_frame = ctk.CTkFrame(parent, fg_color="white")
            ticket_frame.pack(fill="x", pady=(0, 10))

            # Header row
            header = ctk.CTkFrame(ticket_frame, fg_color="#E6D9F2")
            header.pack(fill="x", padx=5, pady=(5, 2))

            ctk.CTkLabel(header, text="Tier Name", width=150, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Price", width=80, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Available", width=80, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Sold", width=80, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Revenue", width=100, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

            # Data rows
            self.ticket_sold_entries = {}
            self.ticket_revenue_labels = {}
            self.ticket_prices = {}
            total_revenue = 0
            for tier in ticket_tiers:
                row = ctk.CTkFrame(ticket_frame, fg_color="#F9F5FA")
                row.pack(fill="x", padx=5, pady=1)

                ctk.CTkLabel(row, text=tier['tier_name'], width=150, anchor="w", text_color="#4A2D5E").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=f"${tier['price']:.2f}", width=80, anchor="w", text_color="#666666").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=str(tier['quantity_available']), width=80, anchor="w", text_color="#666666").pack(side="left", padx=5)

                # Editable quantity sold
                entry_sold = ctk.CTkEntry(row, width=80, placeholder_text="0")
                if tier.get('quantity_sold'):
                    entry_sold.insert(0, str(tier['quantity_sold']))
                entry_sold.pack(side="left", padx=5)
                self.ticket_sold_entries[tier['id']] = entry_sold
                self.ticket_prices[tier['id']] = tier['price']

                # Bind key release to update revenue in real-time
                entry_sold.bind('<KeyRelease>', lambda e: self.update_ticket_revenues())

                # Calculate revenue
                sold = tier.get('quantity_sold') or 0
                revenue = tier['price'] * sold
                total_revenue += revenue

                # Store revenue label for updates
                revenue_label = ctk.CTkLabel(row, text=f"${revenue:.2f}", width=100, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold"))
                revenue_label.pack(side="left", padx=5)
                self.ticket_revenue_labels[tier['id']] = revenue_label

            # Total revenue label (stored for updates)
            self.total_ticket_revenue_label = ctk.CTkLabel(
                parent,
                text=f"Total Ticket Revenue: ${total_revenue:.2f}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#4A2D5E"
            )
            self.total_ticket_revenue_label.pack(anchor="e", padx=10, pady=(5, 20))
        else:
            ctk.CTkLabel(
                parent,
                text="No ticket tiers configured",
                text_color="#999999"
            ).pack(pady=(0, 20))

        # Prize Distribution Section
        ctk.CTkLabel(
            parent,
            text="Prize Distribution",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(10, 10))

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

        if prizes:
            prize_frame = ctk.CTkFrame(parent, fg_color="white")
            prize_frame.pack(fill="x", pady=(0, 10))

            # Header row
            header = ctk.CTkFrame(prize_frame, fg_color="#E6D9F2")
            header.pack(fill="x", padx=5, pady=(5, 2))

            ctk.CTkLabel(header, text="Prize", width=200, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Quantity", width=80, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Handed Out", width=100, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Remaining", width=100, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

            # Data rows - with editable handed out field
            self.prize_handed_out_entries = {}
            self.prize_remaining_labels = {}
            self.prize_quantities = {}
            for prize in prizes:
                row = ctk.CTkFrame(prize_frame, fg_color="#F9F5FA")
                row.pack(fill="x", padx=5, pady=1)

                quantity = prize.get('quantity') or 0
                handed_out = prize.get('quantity_handed_out') or 0

                ctk.CTkLabel(row, text=prize['description'], width=200, anchor="w", text_color="#4A2D5E").pack(side="left", padx=5)
                ctk.CTkLabel(row, text=str(quantity), width=80, anchor="w", text_color="#666666").pack(side="left", padx=5)

                # Editable handed out field
                entry_handed_out = ctk.CTkEntry(row, width=100, placeholder_text="0")
                if handed_out > 0:
                    entry_handed_out.insert(0, str(handed_out))
                entry_handed_out.pack(side="left", padx=5)
                self.prize_handed_out_entries[prize['id']] = entry_handed_out
                self.prize_quantities[prize['id']] = quantity

                # Bind key release to update remaining in real-time
                entry_handed_out.bind('<KeyRelease>', lambda e: self.update_prize_remaining())

                # Remaining (calculated display)
                remaining = quantity - handed_out
                remaining_color = "#4A2D5E"
                if remaining > 0:
                    remaining_color = "#FF9800"  # Orange for extras remaining
                elif remaining < 0:
                    remaining_color = "#E57373"  # Red for over-distributed

                remaining_label = ctk.CTkLabel(
                    row,
                    text=str(remaining),
                    width=100,
                    anchor="w",
                    text_color=remaining_color,
                    font=ctk.CTkFont(weight="bold")
                )
                remaining_label.pack(side="left", padx=5)
                self.prize_remaining_labels[prize['id']] = remaining_label
        else:
            ctk.CTkLabel(
                parent,
                text="No prizes configured",
                text_color="#999999"
            ).pack(pady=(0, 20))

        # Event Notes Section
        notes_header = ctk.CTkFrame(parent, fg_color="transparent")
        notes_header.pack(fill="x", pady=(20, 10))

        ctk.CTkLabel(
            notes_header,
            text="Event Notes",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(side="left")

        btn_add_note = ctk.CTkButton(
            notes_header,
            text="+ Add Note",
            command=self.add_post_event_note,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=100
        )
        btn_add_note.pack(side="right")

        # Notes list
        self.post_event_notes_scroll = ctk.CTkScrollableFrame(parent, fg_color="white", height=150)
        self.post_event_notes_scroll.pack(fill="x", padx=10, pady=(0, 20))

        self.load_post_event_notes()

        # Other Post-Event Analysis Fields
        ctk.CTkLabel(
            parent,
            text="Event Analysis",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(anchor="w", pady=(10, 10))

        # Get existing analysis data
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM event_analysis WHERE event_id = ?', (self.event_id,))
        analysis = cursor.fetchone()
        conn.close()

        # Actual Attendance
        ctk.CTkLabel(parent, text="Actual Attendance", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(5, 2))
        self.entry_attendance = ctk.CTkEntry(parent, placeholder_text="Number of attendees", font=ctk.CTkFont(size=15))
        self.entry_attendance.pack(fill="x", pady=(0, 10))

        # Attendee Enjoyment Rating
        enjoyment_frame = ctk.CTkFrame(parent, fg_color="#F9F5FA", corner_radius=8)
        enjoyment_frame.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(
            enjoyment_frame,
            text="Attendee Enjoyment Rating",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold", size=15)
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Info label
        ctk.CTkLabel(
            enjoyment_frame,
            text="How much did the majority of attendees enjoy the event?",
            text_color="#666666",
            font=ctk.CTkFont(size=15)
        ).pack(anchor="w", padx=15, pady=(0, 5))

        # Scale explanation
        enjoyment_scale_text = """Rating Scale:

10: Everyone absolutely loved it - overwhelmingly positive feedback
9: Nearly everyone had a great time - very positive experience
8: Most attendees thoroughly enjoyed it - positive overall
7: Majority enjoyed it - generally well-received
6: More people liked it than didn't - acceptable
5: Mixed reactions - neutral feedback
4: More negative than positive - needs improvement
3: Most didn't enjoy it - significant issues
2: Very poor reception - major problems
1: Almost nobody enjoyed it - serious failures
0: Complete disaster - total event failure"""

        ctk.CTkLabel(
            enjoyment_frame,
            text=enjoyment_scale_text,
            text_color="#666666",
            font=ctk.CTkFont(size=15),
            justify="left",
            wraplength=800
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Enjoyment rating entry
        enjoyment_row = ctk.CTkFrame(enjoyment_frame, fg_color="transparent")
        enjoyment_row.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            enjoyment_row,
            text="Enjoyment Rating (0-10):",
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15),
            width=220,
            anchor="w"
        ).pack(side="left")

        self.entry_enjoyment = ctk.CTkEntry(enjoyment_row, placeholder_text="0-10", width=100, font=ctk.CTkFont(size=15))
        self.entry_enjoyment.pack(side="left", padx=5)
        self.entry_enjoyment.bind('<KeyRelease>', lambda e: self.update_overall_success_score())

        # Event Smoothness Rating
        smoothness_frame = ctk.CTkFrame(parent, fg_color="#F9F5FA", corner_radius=8)
        smoothness_frame.pack(fill="x", pady=(15, 10))

        ctk.CTkLabel(
            smoothness_frame,
            text="Event Smoothness Rating",
            text_color="#4A2D5E",
            font=ctk.CTkFont(weight="bold", size=15)
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
            font=ctk.CTkFont(size=15),
            width=220,
            anchor="w"
        ).pack(side="left")

        self.entry_smoothness = ctk.CTkEntry(smoothness_row, placeholder_text="0-10", width=100, font=ctk.CTkFont(size=15))
        self.entry_smoothness.pack(side="left", padx=5)
        self.entry_smoothness.bind('<KeyRelease>', lambda e: self.update_overall_success_score())

        # Overall Success Score Display
        self.overall_success_label = ctk.CTkLabel(
            parent,
            text="Overall Event Success Score: --/20",
            text_color="#8B5FBF",
            font=ctk.CTkFont(weight="bold", size=15)
        )
        self.overall_success_label.pack(anchor="w", pady=(10, 5))

        ctk.CTkLabel(
            parent,
            text="Calculated as: Enjoyment Rating + Smoothness Rating (max 20)",
            text_color="#666666",
            font=ctk.CTkFont(size=15)
        ).pack(anchor="w", pady=(0, 15))

        # Notes
        ctk.CTkLabel(parent, text="Notes/Feedback", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold", size=15)).pack(anchor="w", pady=(5, 2))
        self.text_analysis_notes = ctk.CTkTextbox(parent, height=100, font=ctk.CTkFont(size=15))
        self.text_analysis_notes.pack(fill="x", pady=(0, 15))

        # Populate if analysis exists
        if analysis:
            if analysis['actual_attendance']:
                self.entry_attendance.insert(0, str(analysis['actual_attendance']))
            # Load enjoyment rating (attendee_satisfaction field)
            if analysis.get('attendee_satisfaction') is not None:
                self.entry_enjoyment.insert(0, str(analysis['attendee_satisfaction']))
            if analysis.get('event_smoothness') is not None:
                self.entry_smoothness.insert(0, str(analysis['event_smoothness']))
            if analysis['notes']:
                self.text_analysis_notes.insert("1.0", analysis['notes'])
            # Update the calculated score display
            self.update_overall_success_score()

        # Warning if there are unsaved ticket sales
        self.unsaved_warning_frame = ctk.CTkFrame(parent, fg_color="#FFE4B5", corner_radius=8)
        warning_content = ctk.CTkFrame(self.unsaved_warning_frame, fg_color="transparent")
        warning_content.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            warning_content,
            text="⚠️ Warning: Unsaved Ticket Data",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#CC6600"
        ).pack(anchor="w")

        ctk.CTkLabel(
            warning_content,
            text="You have ticket sales data that hasn't been saved to the analysis.\nClick 'Save Post-Event Analysis' below to calculate revenue.",
            font=ctk.CTkFont(size=13),
            text_color="#8B4513",
            justify="left"
        ).pack(anchor="w", pady=(5, 0))

        # Check if warning should be shown
        self.check_and_update_unsaved_warning()

        # Separator before save button
        separator = ctk.CTkFrame(parent, height=2, fg_color="#C5A8D9")
        separator.pack(fill="x", pady=(20, 20))

        # Bottom frame for save button and last saved timestamp
        bottom_frame = ctk.CTkFrame(parent, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(0, 20))

        # Save button - prominent and clear
        btn_save = ctk.CTkButton(
            bottom_frame,
            text="Save Post-Event Analysis",
            command=self.save_post_event_analysis,
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            height=50,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        btn_save.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Last saved timestamp
        self.last_saved_label = ctk.CTkLabel(
            bottom_frame,
            text="Not saved yet",
            text_color="#666666",
            font=ctk.CTkFont(size=13),
            anchor="e"
        )
        self.last_saved_label.pack(side="right", padx=(10, 0))

        # Update last saved label if event has been updated
        if self.event_data.get('updated_at'):
            try:
                updated_time = datetime.strptime(self.event_data['updated_at'], '%Y-%m-%d %H:%M:%S')
                self.last_saved_label.configure(text=f"Last saved: {updated_time.strftime('%d/%m/%Y %H:%M')}")
            except:
                pass

    def load_labour_costs(self):
        """Load labour cost entries"""
        for widget in self.labour_scroll.winfo_children():
            widget.destroy()

        labour_costs = self.event_manager.get_labour_costs(self.event_id)

        if not labour_costs:
            ctk.CTkLabel(
                self.labour_scroll,
                text="No labour cost entries yet. Add your first entry!",
                text_color="#999999"
            ).pack(pady=20)
            return

        # Header row
        header = ctk.CTkFrame(self.labour_scroll, fg_color="#E6D9F2")
        header.pack(fill="x", padx=5, pady=(5, 2))

        ctk.CTkLabel(header, text="Staff", width=120, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Hours", width=60, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Rate Type", width=100, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Rate", width=70, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Status", width=70, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Total", width=80, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        # Data rows
        for labour in labour_costs:
            self.create_labour_cost_row(labour)

    def create_labour_cost_row(self, labour: dict):
        """Create a labour cost row"""
        row = ctk.CTkFrame(self.labour_scroll, fg_color="#F9F5FA")
        row.pack(fill="x", padx=5, pady=1)

        # Staff name
        staff_name = labour.get('staff_name') or 'Unnamed'
        ctk.CTkLabel(row, text=staff_name, width=120, anchor="w", text_color="#4A2D5E").pack(side="left", padx=5)

        # Hours
        hours = f"{labour['hours_worked']:.1f}" if labour.get('hours_worked') else "0"
        ctk.CTkLabel(row, text=hours, width=60, anchor="w", text_color="#666666").pack(side="left", padx=5)

        # Rate type
        rate_type = labour.get('rate_type', 'weekday').replace('_', ' ').title()
        ctk.CTkLabel(row, text=rate_type, width=100, anchor="w", text_color="#666666").pack(side="left", padx=5)

        # Hourly rate
        rate = f"${labour['hourly_rate']:.2f}" if labour.get('hourly_rate') else "$0.00"
        ctk.CTkLabel(row, text=rate, width=70, anchor="w", text_color="#666666").pack(side="left", padx=5)

        # Work status
        status = labour.get('work_status', 'full').capitalize()
        ctk.CTkLabel(row, text=status, width=70, anchor="w", text_color="#666666").pack(side="left", padx=5)

        # Total cost
        total = f"${labour['total_cost']:.2f}" if labour.get('total_cost') else "$0.00"
        ctk.CTkLabel(row, text=total, width=80, anchor="w", text_color="#4A2D5E", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        # Action buttons
        btn_edit = ctk.CTkButton(
            row,
            text="Edit",
            command=lambda l=labour: self.edit_labour_cost(l),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=50,
            height=25
        )
        btn_edit.pack(side="left", padx=2)

        btn_delete = ctk.CTkButton(
            row,
            text="Delete",
            command=lambda l=labour: self.delete_labour_cost(l),
            fg_color="#E57373",
            hover_color="#D32F2F",
            width=50,
            height=25
        )
        btn_delete.pack(side="left", padx=2)

    def add_labour_cost(self):
        """Add a new labour cost entry"""
        from views.event_dialogs import LabourCostDialog
        dialog = LabourCostDialog(self, self.db, self.event_id)
        self.wait_window(dialog)
        self.load_labour_costs()
        self.refresh_labour_total()

    def edit_labour_cost(self, labour_data: dict):
        """Edit an existing labour cost entry"""
        from views.event_dialogs import LabourCostDialog
        dialog = LabourCostDialog(self, self.db, self.event_id, labour_data)
        self.wait_window(dialog)
        self.load_labour_costs()
        self.refresh_labour_total()

    def delete_labour_cost(self, labour_data: dict):
        """Delete a labour cost entry"""
        if messagebox.askyesno("Confirm Delete", f"Delete labour cost entry for {labour_data.get('staff_name') or 'Unnamed'}?"):
            self.event_manager.delete_labour_cost_entry(labour_data['id'])
            self.load_labour_costs()
            self.refresh_labour_total()
            messagebox.showinfo("Success", "Labour cost entry deleted")

    def refresh_labour_total(self):
        """Refresh the total labour cost display"""
        # Find and update the total label
        # This is a simple approach - in production you might want a more elegant solution
        self.tabview.delete("Post-Event")
        self.tabview.add("Post-Event")
        self.create_post_event_tab()

    def update_satisfaction_score(self):
        """Calculate and display satisfaction score in real-time"""
        try:
            loved = int(self.entry_loved_pct.get() or 0)
            liked = int(self.entry_liked_pct.get() or 0)
            disliked = int(self.entry_disliked_pct.get() or 0)

            # Validate percentages
            total = loved + liked + disliked
            if total > 100:
                self.calculated_score_label.configure(
                    text="Total exceeds 100%!",
                    text_color="#E57373"
                )
                return

            # Calculate weighted score: (loved% × 10 + liked% × 6 + disliked% × 2.5) ÷ 100
            score = (loved * 10 + liked * 6 + disliked * 2.5) / 100

            # Update label
            if total == 0:
                self.calculated_score_label.configure(
                    text="Calculated Satisfaction Score: --/10",
                    text_color="#8B5FBF"
                )
            elif total != 100:
                self.calculated_score_label.configure(
                    text=f"Calculated Score: {score:.1f}/10 (Total: {total}% - should be 100%)",
                    text_color="#FFB74D"
                )
            else:
                self.calculated_score_label.configure(
                    text=f"Calculated Satisfaction Score: {score:.1f}/10",
                    text_color="#8B5FBF"
                )

            # Update overall success score when satisfaction changes
            self.update_overall_success_score()
        except ValueError:
            self.calculated_score_label.configure(
                text="Calculated Satisfaction Score: --/10",
                text_color="#8B5FBF"
            )

    def update_overall_success_score(self):
        """Calculate and display overall success score in real-time"""
        try:
            # Get enjoyment rating
            enjoyment_text = self.entry_enjoyment.get()
            if not enjoyment_text:
                self.overall_success_label.configure(
                    text="Overall Event Success Score: --/20 (Enter enjoyment rating)",
                    text_color="#FFB74D"
                )
                return

            enjoyment = float(enjoyment_text)
            if enjoyment < 0 or enjoyment > 10:
                self.overall_success_label.configure(
                    text="Enjoyment rating must be between 0-10",
                    text_color="#E57373"
                )
                return

            # Get smoothness rating
            smoothness_text = self.entry_smoothness.get()
            if not smoothness_text:
                self.overall_success_label.configure(
                    text="Overall Event Success Score: --/20 (Enter smoothness rating)",
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

            # Calculate overall success score: enjoyment + smoothness
            overall_score = enjoyment + smoothness

            # Update label with color coding
            if overall_score >= 16:
                color = "#4CAF50"  # Green for excellent (16-20)
            elif overall_score >= 12:
                color = "#8B5FBF"  # Purple for good (12-15)
            elif overall_score >= 8:
                color = "#FFB74D"  # Orange for okay (8-11)
            else:
                color = "#E57373"  # Red for poor (0-7)

            self.overall_success_label.configure(
                text=f"Overall Event Success Score: {overall_score:.1f}/20",
                text_color=color
            )
        except ValueError:
            self.overall_success_label.configure(
                text="Overall Event Success Score: --/20",
                text_color="#8B5FBF"
            )

    def update_ticket_revenues(self):
        """Update ticket revenue displays in real-time"""
        if not hasattr(self, 'ticket_sold_entries'):
            return

        total_revenue = 0
        for tier_id, entry in self.ticket_sold_entries.items():
            try:
                quantity_sold = int(entry.get() or 0)
                price = self.ticket_prices[tier_id]
                revenue = quantity_sold * price
                total_revenue += revenue

                # Update individual revenue label
                if tier_id in self.ticket_revenue_labels:
                    self.ticket_revenue_labels[tier_id].configure(text=f"${revenue:.2f}")
            except ValueError:
                # If invalid input, show 0
                if tier_id in self.ticket_revenue_labels:
                    self.ticket_revenue_labels[tier_id].configure(text="$0.00")

        # Update total revenue label
        if hasattr(self, 'total_ticket_revenue_label'):
            self.total_ticket_revenue_label.configure(text=f"Total Ticket Revenue: ${total_revenue:.2f}")

        # Check if warning should be shown
        self.check_and_update_unsaved_warning()

    def check_and_update_unsaved_warning(self):
        """Check if there's unsaved ticket data and show/hide warning"""
        if not hasattr(self, 'unsaved_warning_frame'):
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Calculate current ticket revenue from UI
        current_revenue = 0
        if hasattr(self, 'ticket_sold_entries'):
            for tier_id, entry in self.ticket_sold_entries.items():
                try:
                    quantity_sold = int(entry.get() or 0)
                    price = self.ticket_prices.get(tier_id, 0)
                    current_revenue += quantity_sold * price
                except ValueError:
                    pass

        # Get saved revenue from database
        cursor.execute('''
            SELECT revenue_total
            FROM event_analysis
            WHERE event_id = ?
        ''', (self.event_id,))
        result = cursor.fetchone()
        saved_revenue = float(result['revenue_total']) if result and result['revenue_total'] else 0.0

        conn.close()

        # Show warning if there's unsaved data (revenue doesn't match or there's revenue but no saved data)
        has_unsaved_changes = (current_revenue > 0 and current_revenue != saved_revenue)

        if has_unsaved_changes:
            # Show the warning if not already packed
            if not self.unsaved_warning_frame.winfo_ismapped():
                self.unsaved_warning_frame.pack(fill="x", pady=(10, 10))
        else:
            # Hide the warning
            self.unsaved_warning_frame.pack_forget()

    def update_prize_remaining(self):
        """Update prize remaining displays in real-time"""
        if not hasattr(self, 'prize_handed_out_entries'):
            return

        for prize_id, entry in self.prize_handed_out_entries.items():
            try:
                handed_out = int(entry.get() or 0)
                quantity = self.prize_quantities[prize_id]
                remaining = quantity - handed_out

                # Determine color based on remaining
                if remaining > 0:
                    color = "#FF9800"  # Orange for extras remaining
                elif remaining < 0:
                    color = "#E57373"  # Red for over-distributed
                else:
                    color = "#4A2D5E"  # Normal color for exactly right

                # Update remaining label
                if prize_id in self.prize_remaining_labels:
                    self.prize_remaining_labels[prize_id].configure(
                        text=str(remaining),
                        text_color=color
                    )
            except ValueError:
                # If invalid input, calculate with 0
                quantity = self.prize_quantities[prize_id]
                if prize_id in self.prize_remaining_labels:
                    self.prize_remaining_labels[prize_id].configure(
                        text=str(quantity),
                        text_color="#4A2D5E"
                    )

    def save_post_event_analysis(self):
        """Save post-event analysis data"""
        # Save ticket sales quantities first
        conn = self.db.get_connection()
        cursor = conn.cursor()

        if hasattr(self, 'ticket_sold_entries'):
            for tier_id, entry in self.ticket_sold_entries.items():
                try:
                    quantity_sold = int(entry.get() or 0)
                    cursor.execute('''
                        UPDATE ticket_tiers
                        SET quantity_sold = ?
                        WHERE id = ?
                    ''', (quantity_sold, tier_id))
                except ValueError:
                    messagebox.showerror("Validation Error", f"Invalid ticket quantity for tier ID {tier_id}")
                    conn.close()
                    return

        # Save prize handed out quantities
        if hasattr(self, 'prize_handed_out_entries'):
            for prize_id, entry in self.prize_handed_out_entries.items():
                try:
                    quantity_handed_out = int(entry.get() or 0)
                    cursor.execute('''
                        UPDATE prize_items
                        SET quantity_handed_out = ?
                        WHERE id = ?
                    ''', (quantity_handed_out, prize_id))
                except ValueError:
                    messagebox.showerror("Validation Error", f"Invalid prize quantity for prize ID {prize_id}")
                    conn.close()
                    return

        conn.commit()

        # Validate attendance
        attendance = None
        if self.entry_attendance.get():
            try:
                attendance = int(self.entry_attendance.get())
            except ValueError:
                messagebox.showerror("Validation Error", "Attendance must be a whole number")
                conn.close()
                return

        # Validate enjoyment rating
        enjoyment_score = None
        if self.entry_enjoyment.get():
            try:
                enjoyment_score = float(self.entry_enjoyment.get())
                if enjoyment_score < 0 or enjoyment_score > 10:
                    messagebox.showerror("Validation Error", "Enjoyment rating must be between 0 and 10")
                    conn.close()
                    return
                enjoyment_score = round(enjoyment_score, 1)
            except ValueError:
                messagebox.showerror("Validation Error", "Enjoyment rating must be a number")
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
        if enjoyment_score is not None and event_smoothness is not None:
            # Formula: enjoyment + smoothness
            overall_success_score = enjoyment_score + event_smoothness
            overall_success_score = round(overall_success_score, 1)

        # Get notes
        notes = self.text_analysis_notes.get("1.0", "end-1c").strip()

        # Calculate totals
        total_labour = self.event_manager.get_total_labour_cost(self.event_id)

        # Get revenue from ticket sales
        cursor.execute('''
            SELECT SUM(price * quantity_sold) as revenue
            FROM ticket_tiers
            WHERE event_id = ?
        ''', (self.event_id,))
        result = cursor.fetchone()
        revenue = result['revenue'] if result and result['revenue'] else 0.0

        # Get other costs
        cursor.execute('''
            SELECT SUM(amount) as costs
            FROM event_costs
            WHERE event_id = ?
        ''', (self.event_id,))
        result = cursor.fetchone()
        other_costs = result['costs'] if result and result['costs'] else 0.0

        # Calculate totals
        total_cost = total_labour + other_costs
        profit_margin = revenue - total_cost

        # Save or update analysis
        cursor.execute('SELECT id FROM event_analysis WHERE event_id = ?', (self.event_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute('''
                UPDATE event_analysis
                SET actual_attendance = ?,
                    attendee_satisfaction = ?,
                    event_smoothness = ?,
                    overall_success_score = ?,
                    profit_margin = ?,
                    revenue_total = ?,
                    cost_total = ?,
                    notes = ?
                WHERE event_id = ?
            ''', (attendance, enjoyment_score,
                  event_smoothness, overall_success_score,
                  profit_margin, revenue, total_cost, notes, self.event_id))
        else:
            cursor.execute('''
                INSERT INTO event_analysis
                (event_id, actual_attendance, attendee_satisfaction,
                 event_smoothness, overall_success_score,
                 profit_margin, revenue_total, cost_total, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.event_id, attendance, enjoyment_score,
                  event_smoothness, overall_success_score,
                  profit_margin, revenue, total_cost, notes))

        conn.commit()
        conn.close()

        # Update the warning indicator (should hide it now)
        self.check_and_update_unsaved_warning()

        # Update the last saved timestamp
        current_time = datetime.now()
        if hasattr(self, 'last_saved_label'):
            self.last_saved_label.configure(text=f"Last saved: {current_time.strftime('%d/%m/%Y %H:%M')}")

    def load_post_event_notes(self):
        """Load event notes for post-event analysis"""
        for widget in self.post_event_notes_scroll.winfo_children():
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
                self.post_event_notes_scroll,
                text="No notes yet. Add your first note!",
                text_color="#999999"
            ).pack(pady=20)
            return

        for note in notes:
            self.create_post_event_note_card(note)

    def create_post_event_note_card(self, note: dict):
        """Create visual card for a post-event note"""
        card = ctk.CTkFrame(self.post_event_notes_scroll, fg_color="#F9F5FA")
        card.pack(fill="x", padx=10, pady=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)

        # Left side - note content
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        # Note text
        note_text = note.get('note_text', '')
        # Truncate if too long
        display_text = note_text if len(note_text) <= 150 else note_text[:150] + "..."

        ctk.CTkLabel(
            left,
            text=display_text,
            text_color="#4A2D5E",
            anchor="w",
            wraplength=500,
            justify="left"
        ).pack(anchor="w")

        # Badges row
        badges_frame = ctk.CTkFrame(left, fg_color="transparent")
        badges_frame.pack(anchor="w", pady=(8, 0))

        # Send to template badge
        if note.get('send_to_template'):
            template_badge = ctk.CTkLabel(
                badges_frame,
                text="Sent to template",
                fg_color="#9C27B0",
                text_color="white",
                corner_radius=10,
                padx=8,
                pady=2
            )
            template_badge.pack(side="left", padx=(0, 5))

        # Right side - action buttons
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right")

        btn_template = ctk.CTkButton(
            right,
            text="Save to Template",
            command=lambda n=note: self.save_note_to_template(n),
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            width=120,
            height=30
        )
        btn_template.pack(side="left", padx=2)

        btn_edit = ctk.CTkButton(
            right,
            text="Edit",
            command=lambda n=note: self.edit_post_event_note(n),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            width=70,
            height=30
        )
        btn_edit.pack(side="left", padx=2)

        btn_delete = ctk.CTkButton(
            right,
            text="Delete",
            command=lambda n=note: self.delete_post_event_note(n),
            fg_color="#E57373",
            hover_color="#D32F2F",
            width=70,
            height=30
        )
        btn_delete.pack(side="left", padx=2)

    def add_post_event_note(self):
        """Open dialog to add new post-event note"""
        from views.event_dialogs import PostEventFeedbackDialog
        template_id = self.event_data.get('template_id')
        dialog = PostEventFeedbackDialog(self, self.db, self.event_id, template_id)
        self.wait_window(dialog)
        self.load_post_event_notes()

    def edit_post_event_note(self, note_data: dict):
        """Edit an existing post-event note"""
        from views.event_dialogs import NoteDialog
        template_id = self.event_data.get('template_id')
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
        """Save a note to the event's template"""
        template_id = self.event_data.get('template_id')

        if not template_id:
            messagebox.showwarning("No Template", "This event is not based on a template. Cannot save note to template.")
            return

        # Get list of templates to choose from
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM event_templates ORDER BY name')
        templates = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not templates:
            messagebox.showwarning("No Templates", "No templates available. Create a template first.")
            return

        # Create a simple dialog to select template(s)
        from views.event_dialogs import TemplateSelectionDialog
        dialog = TemplateSelectionDialog(self, self.db, templates, note_data, self.event_id)
        self.wait_window(dialog)
        self.load_post_event_notes()

    def edit_event_details(self):
        """Open dialog to edit basic event details"""
        from views.event_dialogs import EventDetailsEditDialog
        dialog = EventDetailsEditDialog(self, self.db, self.event_id)
        self.wait_window(dialog)
        # Reload event data and refresh the overview tab
        self.event_data = self.event_manager.get_event_by_id(self.event_id)
        self.tabview.delete("Overview")
        self.tabview.add("Overview")
        self.create_overview_tab()
        self.tabview.set("Overview")
