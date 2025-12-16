"""Calendar View - Monthly calendar with events and manual entries"""
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta
import calendar as cal

class CalendarView(ctk.CTkFrame):
    """View for calendar with events and manual entries"""

    def __init__(self, parent, database, navigation_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = database
        self.navigation_manager = navigation_manager
        self.configure(fg_color="#F5F0F6")

        # Create header
        self.create_header()

        # Create calendar content
        self.create_calendar_content()

    def create_header(self):
        """Create the header section"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text="Event Calendar",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(side="left")

    def create_calendar_content(self):
        """Create main calendar content"""
        # Main container
        container = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Left side - Calendar
        left_frame = ctk.CTkFrame(container, fg_color="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # Calendar widget
        self.calendar = Calendar(
            left_frame,
            selectmode='day',
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day,
            background='white',
            foreground='black',
            normalbackground='white',
            normalforeground='black',
            headersbackground='#8B5FBF',
            headersforeground='white',
            selectbackground='#4A2D5E',
            selectforeground='white',
            weekendbackground='white',
            weekendforeground='black',
            othermonthbackground='#F3E5F5',
            othermonthforeground='#9E9E9E',
            othermonthwebackground='#F3E5F5',
            othermonthweforeground='#9E9E9E',
            font=('Segoe UI', 14),
            borderwidth=2,
            bordercolor='#8B5FBF'
        )
        self.calendar.pack(fill="both", expand=True, pady=10, padx=10)

        # Bind calendar selection and month changes
        self.calendar.bind("<<CalendarSelected>>", self.on_date_selected)
        self.calendar.bind("<<CalendarMonthChanged>>", self.on_month_changed)

        # Right side - Selected date info and controls
        right_frame = ctk.CTkFrame(container, fg_color="#F5F0F6", corner_radius=8, width=350)
        right_frame.pack(side="right", fill="both", padx=(0, 20), pady=20)
        right_frame.pack_propagate(False)

        # Selected date label
        self.date_label = ctk.CTkLabel(
            right_frame,
            text=f"Selected: {datetime.now().strftime('%d %B %Y')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        )
        self.date_label.pack(pady=(20, 10), padx=20)

        # Events for selected date
        self.events_frame = ctk.CTkScrollableFrame(
            right_frame,
            fg_color="white",
            corner_radius=8,
            height=300
        )
        self.events_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Add entry button
        add_btn = ctk.CTkButton(
            right_frame,
            text="+ Add Calendar Entry",
            command=self.add_calendar_entry,
            fg_color="#8B5FBF",
            hover_color="#7A4FAF"
        )
        add_btn.pack(pady=(10, 20), padx=20)

        # Legend
        legend_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        legend_frame.pack(pady=(0, 20), padx=20)

        ctk.CTkLabel(
            legend_frame,
            text="Legend:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w")

        self.create_legend_item(legend_frame, "Events (from system)", "#BA68C8")
        self.create_legend_item(legend_frame, "Public Holidays", "#E0E0E0")
        self.create_legend_item(legend_frame, "Miscellaneous", "#FFF59D")
        self.create_legend_item(legend_frame, "Multiple Events", "#C8E6C9")

        # Load initial data
        self.load_calendar_markers()
        self.on_date_selected()

    def create_legend_item(self, parent, text, color):
        """Create a legend item"""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(anchor="w", pady=2)

        color_box = ctk.CTkFrame(item_frame, fg_color=color, width=15, height=15, corner_radius=3)
        color_box.pack(side="left", padx=(0, 5))

        label = ctk.CTkLabel(
            item_frame,
            text=text,
            font=ctk.CTkFont(size=15),
            text_color="#4A2D5E"
        )
        label.pack(side="left")

    def load_calendar_markers(self):
        """Load and mark dates that have events or entries"""
        # Clear existing marks
        self.calendar.calevent_remove('all')

        # Get current month/year from calendar
        year = self.calendar.get_displayed_month()[1]
        month = self.calendar.get_displayed_month()[0]

        # Get first and last day of displayed month
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, cal.monthrange(year, month)[1])

        # Load events from database
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Track event types and titles per date
        date_events = {}  # date_str: {'types': set(), 'titles': list()}

        # Get system events (exclude deleted)
        cursor.execute('''
            SELECT event_date, event_name
            FROM events
            WHERE event_date >= ? AND event_date <= ?
            AND is_cancelled = 0
            AND is_deleted = 0
            ORDER BY event_date
        ''', (first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))

        events = cursor.fetchall()
        for event in events:
            date_str = event['event_date']
            if date_str not in date_events:
                date_events[date_str] = {'types': set(), 'titles': []}
            date_events[date_str]['types'].add('event')
            date_events[date_str]['titles'].append(event['event_name'])

        # Get calendar entries
        cursor.execute('''
            SELECT entry_date, title, entry_type, color
            FROM calendar_entries
            WHERE entry_date >= ? AND entry_date <= ?
            ORDER BY entry_date
        ''', (first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))

        entries = cursor.fetchall()
        for entry in entries:
            date_str = entry['entry_date']
            if date_str not in date_events:
                date_events[date_str] = {'types': set(), 'titles': []}
            date_events[date_str]['types'].add(f"entry_{entry['entry_type']}")
            date_events[date_str]['titles'].append(entry['title'])

        conn.close()

        # Configure tag colors
        self.calendar.tag_config('event', background='#BA68C8', foreground='white')  # Purple
        self.calendar.tag_config('entry_public_holiday', background='#E0E0E0', foreground='black')  # Grey
        self.calendar.tag_config('entry_misc', background='#FFF59D', foreground='black')  # Yellow
        self.calendar.tag_config('multi', background='#C8E6C9', foreground='black')  # Pale green for multiple events

        # Create ONE calendar marker per date - use special 'multi' tag for dates with multiple events
        for date_str, data in date_events.items():
            event_date = datetime.strptime(date_str, '%Y-%m-%d')
            event_types = data['types']

            if len(event_types) > 1:
                # Multiple event types on this date - use special multi-type color
                title = f"{len(data['titles'])} events"
                self.calendar.calevent_create(event_date, title, 'multi')
            else:
                # Single event type - use its specific color
                single_type = list(event_types)[0]
                title = data['titles'][0] if len(data['titles']) == 1 else f"{len(data['titles'])} events"
                self.calendar.calevent_create(event_date, title, single_type)

    def on_month_changed(self, event=None):
        """Handle month/year change - reload calendar markers"""
        self.load_calendar_markers()

    def on_date_selected(self, event=None):
        """Handle date selection"""
        selected_date = self.calendar.get_date()
        date_obj = datetime.strptime(selected_date, '%m/%d/%y')

        # Update date label
        self.date_label.configure(text=f"Selected: {date_obj.strftime('%d %B %Y')}")

        # Clear events frame
        for widget in self.events_frame.winfo_children():
            widget.destroy()

        # Load events and entries for this date
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get system events (exclude deleted)
        cursor.execute('''
            SELECT id, event_name, start_time, event_type_id, is_cancelled
            FROM events
            WHERE event_date = ?
            AND is_deleted = 0
            ORDER BY start_time
        ''', (date_obj.strftime('%Y-%m-%d'),))

        events = cursor.fetchall()

        # Get event type names
        event_types = {}
        cursor.execute('SELECT id, name FROM event_types')
        for row in cursor.fetchall():
            event_types[row['id']] = row['name']

        # Display events
        if events:
            for event in events:
                self.create_event_card(
                    event['id'],
                    event['event_name'],
                    event['start_time'] or '',
                    event_types.get(event['event_type_id'], 'Unknown'),
                    '#BA68C8',  # Purple for system events
                    is_cancelled=event['is_cancelled']
                )

        # Get calendar entries
        cursor.execute('''
            SELECT id, title, description, entry_type, color
            FROM calendar_entries
            WHERE entry_date = ?
            ORDER BY created_at
        ''', (date_obj.strftime('%Y-%m-%d'),))

        entries = cursor.fetchall()

        # Display calendar entries
        if entries:
            for entry in entries:
                color = entry['color'] if entry['color'] else '#FFF59D'  # Default to yellow
                self.create_calendar_entry_card(
                    entry['id'],
                    entry['title'],
                    entry['description'] or '',
                    entry['entry_type'],
                    color
                )

        conn.close()

        # Show message if nothing on this date
        if not events and not entries:
            ctk.CTkLabel(
                self.events_frame,
                text="No events or entries for this date",
                font=ctk.CTkFont(size=15),
                text_color="#999999"
            ).pack(pady=20)

    def create_event_card(self, event_id, name, time, event_type, color, is_cancelled=False):
        """Create a card for a system event"""
        card = ctk.CTkFrame(self.events_frame, fg_color=color, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)

        # Make card clickable
        card.bind("<Button-1>", lambda e: self.open_event_details(event_id))
        card.configure(cursor="hand2")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)

        # Make content frame also clickable
        content.bind("<Button-1>", lambda e: self.open_event_details(event_id))
        content.configure(cursor="hand2")

        # Event name
        name_text = f"{name} (CANCELLED)" if is_cancelled else name
        name_label = ctk.CTkLabel(
            content,
            text=name_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        )
        name_label.pack(anchor="w")
        name_label.bind("<Button-1>", lambda e: self.open_event_details(event_id))
        name_label.configure(cursor="hand2")

        # Time and type
        info = f"{time} - {event_type}" if time else event_type
        info_label = ctk.CTkLabel(
            content,
            text=info,
            font=ctk.CTkFont(size=15),
            text_color="#666666",
            anchor="w"
        )
        info_label.pack(anchor="w")
        info_label.bind("<Button-1>", lambda e: self.open_event_details(event_id))
        info_label.configure(cursor="hand2")

    def create_calendar_entry_card(self, entry_id, title, description, entry_type, color):
        """Create a card for a calendar entry"""
        card = ctk.CTkFrame(self.events_frame, fg_color=color, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)

        # Title
        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        )
        title_label.pack(anchor="w")

        # Description
        if description:
            ctk.CTkLabel(
                content,
                text=description,
                font=ctk.CTkFont(size=15),
                text_color="#666666",
                anchor="w",
                wraplength=280
            ).pack(anchor="w")

        # Type badge
        type_text = "Public Holiday" if entry_type == "public_holiday" else "Misc Entry"
        ctk.CTkLabel(
            content,
            text=type_text,
            font=ctk.CTkFont(size=15),
            text_color="#8B5FBF",
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))

        # Buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=(5, 0))

        ctk.CTkButton(
            btn_frame,
            text="Edit",
            width=60,
            height=25,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            command=lambda: self.edit_calendar_entry(entry_id)
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Delete",
            width=60,
            height=25,
            fg_color="#FFCCCC",
            hover_color="#FFAAAA",
            text_color="#CC0000",
            command=lambda: self.delete_calendar_entry(entry_id)
        ).pack(side="left")

    def refresh(self):
        """Refresh the view (called when navigating back)"""
        self.load_calendar_markers()
        self.on_date_selected()

    def add_calendar_entry(self):
        """Show form to add a new calendar entry"""
        selected_date = self.calendar.get_date()
        date_obj = datetime.strptime(selected_date, '%m/%d/%y')

        # Use navigation if available, otherwise use dialog
        if self.navigation_manager:
            from views.calendar_entry_form_view import CalendarEntryFormView
            self.navigation_manager.navigate_to(
                CalendarEntryFormView,
                "New Calendar Entry",
                context={'db': self.db, 'date': date_obj}
            )
        else:
            dialog = CalendarEntryDialog(self, date_obj, self.db)
            self.wait_window(dialog)
            self.load_calendar_markers()
            self.on_date_selected()

    def edit_calendar_entry(self, entry_id):
        """Edit an existing calendar entry"""
        # Get entry data
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM calendar_entries WHERE id = ?', (entry_id,))
        entry = cursor.fetchone()
        conn.close()

        if entry:
            date_obj = datetime.strptime(entry['entry_date'], '%Y-%m-%d')

            # Use navigation if available, otherwise use dialog
            if self.navigation_manager:
                from views.calendar_entry_form_view import CalendarEntryFormView
                self.navigation_manager.navigate_to(
                    CalendarEntryFormView,
                    "Edit Calendar Entry",
                    context={'db': self.db, 'date': date_obj, 'entry_data': dict(entry)}
                )
            else:
                dialog = CalendarEntryDialog(self, date_obj, self.db, dict(entry))
                self.wait_window(dialog)
                self.load_calendar_markers()
                self.on_date_selected()

    def open_event_details(self, event_id):
        """Open event details dialog"""
        from views.events_view import EventEditDialog
        dialog = EventEditDialog(self, self.db, event_id)
        dialog.wait_window()
        # Refresh calendar to show any updates
        self.load_calendar_markers()
        self.on_date_selected()

    def delete_calendar_entry(self, entry_id):
        """Delete a calendar entry"""
        if messagebox.askyesno("Confirm Delete", "Delete this calendar entry?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM calendar_entries WHERE id = ?', (entry_id,))
            conn.commit()
            conn.close()

            # Refresh calendar
            self.load_calendar_markers()
            self.on_date_selected()


class CalendarEntryDialog(ctk.CTkToplevel):
    """Dialog for adding/editing calendar entries"""

    def __init__(self, parent, date, db, entry_data=None):
        super().__init__(parent)

        self.date = date
        self.db = db
        self.entry_data = entry_data

        self.title("Calendar Entry" if not entry_data else "Edit Calendar Entry")
        self.geometry("500x500")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 450) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 400) // 2
        self.geometry(f"+{x}+{y}")

        self.create_ui()

    def create_ui(self):
        """Create dialog UI"""
        main = ctk.CTkFrame(self, fg_color="white")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Date display
        ctk.CTkLabel(
            main,
            text=f"Date: {self.date.strftime('%d %B %Y')}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#8B5FBF"
        ).pack(pady=(0, 15))

        # Title
        ctk.CTkLabel(
            main,
            text="Title:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", pady=(0, 5))

        self.title_entry = ctk.CTkEntry(main, width=410, placeholder_text="e.g., Australia Day")
        self.title_entry.pack(pady=(0, 15))

        # Description
        ctk.CTkLabel(
            main,
            text="Description (optional):",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", pady=(0, 5))

        self.desc_entry = ctk.CTkTextbox(main, width=410, height=80)
        self.desc_entry.pack(pady=(0, 15))

        # Type
        ctk.CTkLabel(
            main,
            text="Type:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", pady=(0, 5))

        self.type_var = ctk.StringVar(value="misc")
        type_frame = ctk.CTkFrame(main, fg_color="transparent")
        type_frame.pack(anchor="w", pady=(0, 15))

        ctk.CTkRadioButton(
            type_frame,
            text="Public Holiday (Grey)",
            variable=self.type_var,
            value="public_holiday",
            command=self.update_color_preview
        ).pack(side="left", padx=(0, 20))

        ctk.CTkRadioButton(
            type_frame,
            text="Miscellaneous (Yellow)",
            variable=self.type_var,
            value="misc",
            command=self.update_color_preview
        ).pack(side="left")

        # Color preview
        self.color_preview = ctk.CTkFrame(main, width=410, height=30, corner_radius=5)
        self.color_preview.pack(pady=(0, 15))

        # Populate if editing
        if self.entry_data:
            self.title_entry.insert(0, self.entry_data['title'])
            if self.entry_data['description']:
                self.desc_entry.insert("1.0", self.entry_data['description'])
            self.type_var.set(self.entry_data['entry_type'])

        self.update_color_preview()

        # Buttons - make them prominent at the bottom
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))

        btn_save = ctk.CTkButton(
            btn_frame,
            text="Save",
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            height=40,
            command=self.save_entry
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(0, 5))

        btn_cancel = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="#CCCCCC",
            hover_color="#BBBBBB",
            text_color="#4A2D5E",
            height=40,
            command=self.destroy
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def update_color_preview(self):
        """Update color preview based on type"""
        color_map = {
            'public_holiday': '#E0E0E0',  # Grey
            'misc': '#FFF59D'  # Yellow
        }
        color = color_map.get(self.type_var.get(), '#FFF59D')
        self.color_preview.configure(fg_color=color)

    def save_entry(self):
        """Save the calendar entry"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Required", "Please enter a title", parent=self)
            return

        description = self.desc_entry.get("1.0", "end-1c").strip()
        entry_type = self.type_var.get()
        color_map = {
            'public_holiday': '#E0E0E0',  # Grey
            'misc': '#FFF59D'  # Yellow
        }
        color = color_map.get(entry_type, '#FFF59D')

        conn = self.db.get_connection()
        cursor = conn.cursor()

        if self.entry_data:
            # Update existing
            cursor.execute('''
                UPDATE calendar_entries
                SET title = ?, description = ?, entry_type = ?, color = ?
                WHERE id = ?
            ''', (title, description, entry_type, color, self.entry_data['id']))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO calendar_entries (entry_date, title, description, entry_type, color)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.date.strftime('%Y-%m-%d'), title, description, entry_type, color))

        conn.commit()
        conn.close()

        self.destroy()
