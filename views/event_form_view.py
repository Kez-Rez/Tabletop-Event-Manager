"""Event creation/editing form as an in-window view"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from utils.navigation import NavigableView
from event_manager import EventManager


class EventFormView(NavigableView):
    """Form view for creating or editing events"""

    def __init__(self, parent, navigation_manager, context=None):
        super().__init__(parent, navigation_manager, context)

        self.db = context.get('db')
        self.event_manager = EventManager(self.db)
        self.event_id = context.get('event_id')  # None for new event
        self.template_id = context.get('template_id')  # Optional template to use
        self.event_data = None

        # Load event data if editing
        if self.event_id:
            self.event_data = self.event_manager.get_event_by_id(self.event_id)

        self.create_ui()

    def create_ui(self):
        """Create the form UI"""
        # Header with back button
        title = "Edit Event" if self.event_id else "New Event"
        if self.template_id and not self.event_id:
            title += " from Template"

        header = self.create_header_with_back(title)

        # Scrollable content area
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="white",
            corner_radius=10
        )
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Form content
        form_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Event Name
        ctk.CTkLabel(
            form_container,
            text="Event Name *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.name_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Enter event name",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.name_entry.pack(fill="x", pady=(0, 20))

        # Event Date
        ctk.CTkLabel(
            form_container,
            text="Event Date *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.date_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="YYYY-MM-DD",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.date_entry.pack(fill="x", pady=(0, 20))

        # Time Row
        time_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        time_frame.pack(fill="x", pady=(0, 20))

        # Start Time
        left_col = ctk.CTkFrame(time_frame, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            left_col,
            text="Start Time",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.start_time_entry = ctk.CTkEntry(
            left_col,
            placeholder_text="HH:MM",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.start_time_entry.pack(fill="x")

        # End Time
        right_col = ctk.CTkFrame(time_frame, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(
            right_col,
            text="End Time",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.end_time_entry = ctk.CTkEntry(
            right_col,
            placeholder_text="HH:MM",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.end_time_entry.pack(fill="x")

        # Description
        ctk.CTkLabel(
            form_container,
            text="Description",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.description_text = ctk.CTkTextbox(
            form_container,
            height=120,
            font=ctk.CTkFont(size=14)
        )
        self.description_text.pack(fill="x", pady=(0, 20))

        # Load reference data for dropdowns
        self.load_reference_data()

        # Event Type
        ctk.CTkLabel(
            form_container,
            text="Event Type",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.event_type_var = ctk.StringVar(value="Select event type")
        self.event_type_menu = ctk.CTkOptionMenu(
            form_container,
            variable=self.event_type_var,
            values=self.event_type_names,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.event_type_menu.pack(fill="x", pady=(0, 20))

        # Max Capacity
        ctk.CTkLabel(
            form_container,
            text="Maximum Capacity",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.capacity_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Enter maximum capacity",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.capacity_entry.pack(fill="x", pady=(0, 20))

        # Number of Rounds
        ctk.CTkLabel(
            form_container,
            text="Number of Rounds",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.rounds_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Enter number of rounds",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.rounds_entry.pack(fill="x", pady=(0, 20))

        # Action Buttons
        button_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        # Save Button
        btn_save = ctk.CTkButton(
            button_frame,
            text="Save Event",
            command=self.save_event,
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        btn_save.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Cancel Button
        btn_cancel = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.navigation_manager.go_back,
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        btn_cancel.pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Populate form if editing or using template
        if self.event_data:
            self.populate_form()

    def load_reference_data(self):
        """Load dropdown options from database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Event types
        cursor.execute('SELECT id, name FROM event_types ORDER BY name')
        self.event_types = {row['name']: row['id'] for row in cursor.fetchall()}
        self.event_type_names = list(self.event_types.keys())

        conn.close()

    def populate_form(self):
        """Populate form with existing event data"""
        if not self.event_data:
            return

        self.name_entry.insert(0, self.event_data.get('event_name', ''))
        self.date_entry.insert(0, self.event_data.get('event_date', ''))

        if self.event_data.get('start_time'):
            self.start_time_entry.insert(0, self.event_data['start_time'])
        if self.event_data.get('end_time'):
            self.end_time_entry.insert(0, self.event_data['end_time'])

        if self.event_data.get('description'):
            self.description_text.insert("1.0", self.event_data['description'])

        if self.event_data.get('event_type_name'):
            self.event_type_var.set(self.event_data['event_type_name'])

        if self.event_data.get('max_capacity'):
            self.capacity_entry.insert(0, str(self.event_data['max_capacity']))

        if self.event_data.get('number_of_rounds'):
            self.rounds_entry.insert(0, str(self.event_data['number_of_rounds']))

    def check_time_conflicts(self, event_date, start_time, end_time):
        """Check for time conflicts with existing events on the same date"""
        if not start_time or not end_time:
            return []

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Query all events on the same date (excluding current event if editing)
        if self.event_id:
            cursor.execute('''
                SELECT id, event_name, start_time, end_time
                FROM events
                WHERE event_date = ? AND id != ? AND is_deleted = 0
                AND start_time IS NOT NULL AND end_time IS NOT NULL
            ''', (event_date, self.event_id))
        else:
            cursor.execute('''
                SELECT id, event_name, start_time, end_time
                FROM events
                WHERE event_date = ? AND is_deleted = 0
                AND start_time IS NOT NULL AND end_time IS NOT NULL
            ''', (event_date,))

        existing_events = cursor.fetchall()
        conn.close()

        # Check for time overlaps
        conflicts = []
        for event in existing_events:
            # Two events conflict if: start1 < end2 AND start2 < end1
            if start_time < event['end_time'] and event['start_time'] < end_time:
                conflicts.append(event)

        return conflicts

    def save_event(self):
        """Validate and save the event"""
        # Get form data
        event_name = self.name_entry.get().strip()
        event_date = self.date_entry.get().strip()
        start_time = self.start_time_entry.get().strip() or None
        end_time = self.end_time_entry.get().strip() or None
        description = self.description_text.get("1.0", "end-1c").strip() or None
        max_capacity = self.capacity_entry.get().strip()
        number_of_rounds = self.rounds_entry.get().strip()

        # Validation
        if not event_name:
            messagebox.showerror("Validation Error", "Event name is required", parent=self)
            return

        if not event_date:
            messagebox.showerror("Validation Error", "Event date is required", parent=self)
            return

        # Validate date format
        try:
            datetime.strptime(event_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid date format. Use YYYY-MM-DD", parent=self)
            return

        # Get event type ID
        event_type_name = self.event_type_var.get()
        event_type_id = self.event_types.get(event_type_name) if event_type_name != "Select event type" else None

        # Build event data
        event_data = {
            'event_name': event_name,
            'event_date': event_date,
            'start_time': start_time,
            'end_time': end_time,
            'description': description,
            'event_type_id': event_type_id,
            'max_capacity': int(max_capacity) if max_capacity else None,
            'number_of_rounds': int(number_of_rounds) if number_of_rounds else None
        }

        # Add template_id if creating from template
        if self.template_id:
            event_data['template_id'] = self.template_id

        # Check for time conflicts
        if start_time and end_time:
            conflicts = self.check_time_conflicts(event_date, start_time, end_time)
            if conflicts:
                conflict_names = '\n'.join([f"- {event['event_name']} ({event['start_time']} - {event['end_time']})"
                                           for event in conflicts])
                message = f"Time conflict detected!\n\nThe following events overlap with your selected time:\n\n{conflict_names}\n\nDo you want to save anyway?"

                result = messagebox.askyesno("Time Conflict Warning", message, parent=self, icon='warning')
                if not result:
                    return  # User chose not to proceed

        try:
            if self.event_id:
                # Update existing event
                self.event_manager.update_event(self.event_id, event_data)
            else:
                # Create new event
                new_id = self.event_manager.create_event(event_data)

            # Go back to events list (user will see the saved event there)
            self.navigation_manager.go_back()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save event: {str(e)}", parent=self)
