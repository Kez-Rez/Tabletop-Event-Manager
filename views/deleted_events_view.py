"""Deleted Events view UI"""
import customtkinter as ctk
from tkinter import messagebox
from event_manager import EventManager
from datetime import datetime


class DeletedEventsView(ctk.CTkFrame):
    """View for managing deleted events (trash bin)"""

    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = db
        self.event_manager = EventManager(db)
        self.selected_events = set()  # Track selected event IDs

        self.configure(fg_color="#F5F0F6")

        # Create header
        self.create_header()

        # Create deleted events list
        self.create_deleted_events_list()

        # Load deleted events
        self.load_deleted_events()

    def create_header(self):
        """Create the header with title and buttons"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 20))

        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Deleted Events",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(side="left")

        # Buttons frame
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.pack(side="right")

        # Restore selected button
        btn_restore = ctk.CTkButton(
            buttons_frame,
            text="Restore Selected",
            command=self.restore_selected,
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            width=160,
            height=40
        )
        btn_restore.pack(side="left", padx=5)

        # Permanently delete selected button
        btn_permanent_delete = ctk.CTkButton(
            buttons_frame,
            text="Permanently Delete",
            command=self.permanently_delete_selected,
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=160,
            height=40
        )
        btn_permanent_delete.pack(side="left", padx=5)

        # Empty trash button
        btn_empty_trash = ctk.CTkButton(
            buttons_frame,
            text="Empty Trash",
            command=self.empty_trash,
            fg_color="#9E9E9E",
            hover_color="#757575",
            text_color="white",
            width=140,
            height=40
        )
        btn_empty_trash.pack(side="left", padx=5)

    def create_deleted_events_list(self):
        """Create the scrollable deleted events list"""
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

    def load_deleted_events(self):
        """Load and display deleted events"""
        # Clear existing widgets
        for widget in self.events_scroll.winfo_children():
            widget.destroy()

        # Clear selection
        self.selected_events.clear()

        # Get deleted events
        events = self.event_manager.get_deleted_events()

        if not events:
            # No deleted events message
            no_events = ctk.CTkLabel(
                self.events_scroll,
                text="No deleted events.\nDeleted events will appear here and can be restored or permanently deleted.",
                font=ctk.CTkFont(size=16),
                text_color="#999999"
            )
            no_events.pack(pady=40)
            return

        # Display events
        for event in events:
            self.create_deleted_event_card(event)

    def create_deleted_event_card(self, event: dict):
        """Create a card for a deleted event"""
        # Card frame
        card = ctk.CTkFrame(
            self.events_scroll,
            fg_color="#FFE6E6",  # Light red background for deleted items
            corner_radius=8,
            border_width=1,
            border_color="#FFCCCC"
        )
        card.pack(fill="x", padx=10, pady=5)

        # Main content frame
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        # Left side - Checkbox and Event info
        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)

        # Checkbox for selection
        checkbox_var = ctk.BooleanVar(value=False)
        checkbox = ctk.CTkCheckBox(
            left_frame,
            text="",
            variable=checkbox_var,
            command=lambda e_id=event['id'], var=checkbox_var: self.toggle_selection(e_id, var),
            fg_color="#8B5FBF",
            hover_color="#7A4FB0",
            border_color="#8B5FBF",
            checkmark_color="white",
            width=20
        )
        checkbox.pack(side="left", padx=(0, 15))

        # Event details frame
        details_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        details_frame.pack(side="left", fill="both", expand=True)

        # Event name
        name_label = ctk.CTkLabel(
            details_frame,
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

        details_label = ctk.CTkLabel(
            details_frame,
            text=" • ".join(details_text),
            font=ctk.CTkFont(size=15),
            text_color="#666666",
            anchor="w"
        )
        details_label.pack(anchor="w", pady=(5, 0))

        # Deleted date
        if event.get('deleted_at'):
            try:
                deleted_dt = datetime.strptime(event['deleted_at'], '%Y-%m-%d %H:%M:%S')
                deleted_text = f"Deleted: {deleted_dt.strftime('%d %B %Y at %I:%M %p')}"
            except:
                deleted_text = f"Deleted: {event['deleted_at']}"

            deleted_label = ctk.CTkLabel(
                details_frame,
                text=deleted_text,
                font=ctk.CTkFont(size=13, slant="italic"),
                text_color="#999999",
                anchor="w"
            )
            deleted_label.pack(anchor="w", pady=(5, 0))

        # Right side - Quick Actions
        right_frame = ctk.CTkFrame(content, fg_color="transparent")
        right_frame.pack(side="right")

        # Restore button
        btn_restore = ctk.CTkButton(
            right_frame,
            text="Restore",
            command=lambda e=event: self.restore_event(e['id'], e['event_name']),
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            width=100
        )
        btn_restore.pack(pady=2)

        # Permanent delete button
        btn_delete = ctk.CTkButton(
            right_frame,
            text="Delete Forever",
            command=lambda e=event: self.permanently_delete_event(e['id'], e['event_name']),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=100
        )
        btn_delete.pack(pady=2)

    def toggle_selection(self, event_id: int, checkbox_var):
        """Toggle selection of an event"""
        if checkbox_var.get():
            self.selected_events.add(event_id)
        else:
            self.selected_events.discard(event_id)

    def restore_event(self, event_id: int, event_name: str):
        """Restore a single event"""
        result = messagebox.askyesno(
            "Restore Event",
            f"Restore '{event_name}'?"
        )
        if result:
            self.event_manager.restore_event(event_id)
            self.load_deleted_events()
            messagebox.showinfo("Restored", f"'{event_name}' has been restored.")

    def restore_selected(self):
        """Restore all selected events"""
        if not self.selected_events:
            messagebox.showwarning("No Selection", "Please select events to restore.")
            return

        result = messagebox.askyesno(
            "Restore Events",
            f"Restore {len(self.selected_events)} selected event(s)?"
        )
        if result:
            for event_id in self.selected_events:
                self.event_manager.restore_event(event_id)

            count = len(self.selected_events)
            self.load_deleted_events()
            messagebox.showinfo("Restored", f"{count} event(s) have been restored.")

    def permanently_delete_event(self, event_id: int, event_name: str):
        """Permanently delete a single event"""
        result = messagebox.askyesno(
            "Permanent Delete",
            f"PERMANENTLY delete '{event_name}'?\n\nThis action cannot be undone!",
            icon="warning"
        )
        if result:
            self.event_manager.permanently_delete_event(event_id)
            self.load_deleted_events()
            messagebox.showinfo("Deleted", f"'{event_name}' has been permanently deleted.")

    def permanently_delete_selected(self):
        """Permanently delete all selected events"""
        if not self.selected_events:
            messagebox.showwarning("No Selection", "Please select events to permanently delete.")
            return

        result = messagebox.askyesno(
            "Permanent Delete",
            f"PERMANENTLY delete {len(self.selected_events)} selected event(s)?\n\nThis action cannot be undone!",
            icon="warning"
        )
        if result:
            for event_id in self.selected_events:
                self.event_manager.permanently_delete_event(event_id)

            count = len(self.selected_events)
            self.load_deleted_events()
            messagebox.showinfo("Deleted", f"{count} event(s) have been permanently deleted.")

    def empty_trash(self):
        """Permanently delete all deleted events"""
        # Get all deleted events
        deleted_events = self.event_manager.get_deleted_events()

        if not deleted_events:
            messagebox.showinfo("Empty Trash", "Trash is already empty.")
            return

        result = messagebox.askyesno(
            "Empty Trash",
            f"PERMANENTLY delete ALL {len(deleted_events)} event(s) in trash?\n\nThis action cannot be undone!",
            icon="warning"
        )
        if result:
            for event in deleted_events:
                self.event_manager.permanently_delete_event(event['id'])

            self.load_deleted_events()
            messagebox.showinfo("Trash Emptied", f"{len(deleted_events)} event(s) have been permanently deleted.")
