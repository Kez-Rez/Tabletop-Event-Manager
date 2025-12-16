import customtkinter as ctk
from database import Database
from views.events_view import EventsView
from views.templates_view import TemplatesView
from views.settings_view import SettingsView
from views.help_view import HelpView
from views.analysis_view import AnalysisView
from views.feature_requests_view import FeatureRequestsView
from views.deleted_events_view import DeletedEventsView
from views.table_booking_view import TableBookingView
from utils.text_selection import setup_global_text_selection
from utils.navigation import NavigationManager
import sys
import os
import shutil
from datetime import datetime
from pathlib import Path

class BGEventsApp(ctk.CTk):
    """Main application window for TT Events Manager"""

    def __init__(self):
        super().__init__()

        # Initialize database
        self.db = Database()

        # Perform automatic daily backup
        self.perform_automatic_backup()

        # Configure window
        self.title("TT Events Manager")
        self.geometry("1200x800")

        # Set minimum window size to prevent it from becoming too small
        self.minsize(800, 600)

        # Initialize zoom/scaling
        self.current_scale = 1.0
        ctk.set_widget_scaling(self.current_scale)
        ctk.set_window_scaling(self.current_scale)

        # Store reference globally so dialogs can access it
        BGEventsApp._instance = self

        # Set colour scheme - pale blues, pinks, and purples
        ctk.set_appearance_mode("light")

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create sidebar
        self.create_sidebar()

        # Create main content area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#F5F0F6")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Initialize navigation manager
        self.navigation_manager = NavigationManager(self.main_frame)

        # Set up keyboard shortcuts
        self.setup_keyboard_shortcuts()

        # Enable text selection and copying throughout the app
        setup_global_text_selection(self)

        # Show dashboard by default
        self.show_dashboard()

    def create_sidebar(self):
        """Create the navigation sidebar"""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#E6D9F2")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Logo/Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="TT Events\nManager",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#8B5FBF"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 40))

        # Navigation buttons
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            command=self.show_dashboard,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E"
        )
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_events = ctk.CTkButton(
            self.sidebar,
            text="Events",
            command=self.show_events,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E"
        )
        self.btn_events.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_templates = ctk.CTkButton(
            self.sidebar,
            text="Templates",
            command=self.show_templates,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E"
        )
        self.btn_templates.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_analysis = ctk.CTkButton(
            self.sidebar,
            text="Analysis",
            command=self.show_analysis,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E"
        )
        self.btn_analysis.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_table_booking = ctk.CTkButton(
            self.sidebar,
            text="Table Booking",
            command=self.show_table_booking,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E"
        )
        self.btn_table_booking.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.btn_calendar = ctk.CTkButton(
            self.sidebar,
            text="Calendar",
            command=self.show_calendar,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E"
        )
        self.btn_calendar.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.btn_settings = ctk.CTkButton(
            self.sidebar,
            text="Settings",
            command=self.show_settings,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E"
        )
        self.btn_settings.grid(row=7, column=0, padx=20, pady=10, sticky="ew")

        self.btn_help = ctk.CTkButton(
            self.sidebar,
            text="Help",
            command=self.show_help,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E"
        )
        self.btn_help.grid(row=8, column=0, padx=20, pady=10, sticky="ew")

        self.btn_feature_requests = ctk.CTkButton(
            self.sidebar,
            text="Feature Requests",
            command=self.show_feature_requests,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E"
        )
        self.btn_feature_requests.grid(row=9, column=0, padx=20, pady=10, sticky="ew")

        self.btn_feedback = ctk.CTkButton(
            self.sidebar,
            text="Feedback",
            command=self.show_feedback,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E"
        )
        self.btn_feedback.grid(row=10, column=0, padx=20, pady=10, sticky="ew")

        self.btn_deleted_events = ctk.CTkButton(
            self.sidebar,
            text="Deleted Events",
            command=self.show_deleted_events,
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white"
        )
        self.btn_deleted_events.grid(row=11, column=0, padx=20, pady=10, sticky="ew")

        # Last backup info at bottom
        self.backup_info_label = ctk.CTkLabel(
            self.sidebar,
            text=self.get_last_backup_text(),
            font=ctk.CTkFont(size=10),
            text_color="#8B5FBF",
            wraplength=180
        )
        self.backup_info_label.grid(row=12, column=0, padx=20, pady=(20, 5))

        # Designer credit
        self.credit_label = ctk.CTkLabel(
            self.sidebar,
            text="designed by Kerry Restante",
            font=ctk.CTkFont(size=10),
            text_color="#8B5FBF"
        )
        self.credit_label.grid(row=13, column=0, padx=20, pady=(5, 20))

    def clear_main_frame(self):
        """Clear all widgets from main frame"""
        # Clear navigation stack when switching main views
        if hasattr(self, 'navigation_manager'):
            self.navigation_manager.view_stack.clear()
            self.navigation_manager.current_view = None

        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Display the dashboard view"""
        self.clear_main_frame()

        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(pady=30, padx=30, anchor="w")

        # Get checklist items marked as show_on_dashboard
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                ci.id,
                ci.description,
                ci.due_date,
                ci.is_completed,
                e.event_name,
                e.id as event_id
            FROM event_checklist_items ci
            JOIN events e ON ci.event_id = e.id
            WHERE ci.show_on_dashboard = 1
            AND e.is_deleted = 0
            AND e.is_completed = 0
            ORDER BY
                ci.is_completed ASC,
                CASE
                    WHEN ci.due_date < date('now') THEN 0
                    WHEN ci.due_date = date('now') THEN 1
                    WHEN ci.due_date <= date('now', '+7 days') THEN 2
                    ELSE 3
                END,
                ci.due_date ASC
        ''')

        dashboard_items = [dict(row) for row in cursor.fetchall()]

        # Get events with unreceived materials/prize support (exclude deleted)
        cursor.execute('''
            SELECT DISTINCT
                e.id,
                e.event_name,
                e.event_date,
                COUNT(p.id) as unreceived_count
            FROM events e
            JOIN prize_items p ON e.id = p.event_id
            WHERE p.is_received = 0
            AND e.is_completed = 0
            AND e.is_deleted = 0
            AND e.event_date >= date('now')
            GROUP BY e.id, e.event_name, e.event_date
            ORDER BY e.event_date ASC
        ''')

        unreceived_prizes = [dict(row) for row in cursor.fetchall()]
        conn.close()

        # Check if we have anything to display
        has_content = bool(dashboard_items or unreceived_prizes)

        if has_content:
            # Scrollable frame for all dashboard items
            scroll = ctk.CTkScrollableFrame(self.main_frame, fg_color="white")
            scroll.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Display unreceived items section first (higher priority)
        if unreceived_prizes:
            # Section header
            ctk.CTkLabel(
                scroll,
                text="Materials & Prizes Not Received",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#E57373"
            ).pack(pady=(10, 15), padx=10, anchor="w")

            from datetime import datetime, date

            for prize_item in unreceived_prizes:
                # Determine urgency based on event date
                event_date = datetime.strptime(prize_item['event_date'], '%Y-%m-%d').date()
                today = date.today()
                days_until = (event_date - today).days

                if days_until < 0:
                    bg_color = "#FFEBEE"  # Light red for past events
                    border_color = "#E57373"
                    urgency_text = f"EVENT PASSED {abs(days_until)} day(s) ago"
                elif days_until == 0:
                    bg_color = "#FFEBEE"  # Light red for today
                    border_color = "#E57373"
                    urgency_text = "EVENT IS TODAY"
                elif days_until <= 7:
                    bg_color = "#FFF3E0"  # Light orange for soon
                    border_color = "#FFB74D"
                    urgency_text = f"Event in {days_until} day(s)"
                else:
                    bg_color = "#FFF9C4"  # Light yellow for future
                    border_color = "#FFD54F"
                    urgency_text = f"Event in {days_until} days"

                # Create card
                card = ctk.CTkFrame(scroll, fg_color=bg_color, border_width=2, border_color=border_color)
                card.pack(fill="x", padx=10, pady=5)

                # Make card clickable
                event_id = prize_item['id']
                card.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                card.configure(cursor="hand2")

                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="x", padx=15, pady=12)

                # Make content frame also clickable
                content.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                content.configure(cursor="hand2")

                # Left side - info
                left_content = ctk.CTkFrame(content, fg_color="transparent")
                left_content.pack(side="left", fill="both", expand=True)
                left_content.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                left_content.configure(cursor="hand2")

                # Event name
                event_label = ctk.CTkLabel(
                    left_content,
                    text=prize_item['event_name'],
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="#8B5FBF",
                    anchor="w"
                )
                event_label.pack(anchor="w")
                event_label.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                event_label.configure(cursor="hand2")

                # Materials/Prize support message
                msg_label = ctk.CTkLabel(
                    left_content,
                    text=f"{prize_item['unreceived_count']} item(s) not yet received from supplier",
                    font=ctk.CTkFont(size=15),
                    text_color="#4A2D5E",
                    anchor="w"
                )
                msg_label.pack(anchor="w", pady=(3, 0))
                msg_label.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                msg_label.configure(cursor="hand2")

                # Urgency and event date
                formatted_date = event_date.strftime('%A, %d %B %Y')
                info_text = f"{urgency_text} - {formatted_date}"

                info_label = ctk.CTkLabel(
                    left_content,
                    text=info_text,
                    font=ctk.CTkFont(size=15),
                    text_color="#666666",
                    anchor="w"
                )
                info_label.pack(anchor="w", pady=(3, 0))
                info_label.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                info_label.configure(cursor="hand2")

                # Right side - button
                right_content = ctk.CTkFrame(content, fg_color="transparent")
                right_content.pack(side="right", padx=(10, 0))

                ctk.CTkButton(
                    right_content,
                    text="View/Edit Event",
                    command=lambda eid=event_id: self.open_event_from_dashboard(eid),
                    fg_color="#8B5FBF",
                    hover_color="#7A4FB0",
                    text_color="white",
                    width=120,
                    height=32
                ).pack()

        if dashboard_items:
            # Section header
            ctk.CTkLabel(
                scroll,
                text="Important Checklist Items",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#4A2D5E"
            ).pack(pady=(20, 15), padx=10, anchor="w")

            from datetime import datetime, date

            for item in dashboard_items:
                # Determine urgency and color
                if item['is_completed']:
                    bg_color = "#E8F5E9"  # Light green for completed
                    border_color = "#81C784"
                    urgency_text = "Completed"
                elif item['due_date']:
                    due_date = datetime.strptime(item['due_date'], '%Y-%m-%d').date()
                    today = date.today()
                    days_until = (due_date - today).days

                    if days_until < 0:
                        bg_color = "#FFEBEE"  # Light red for overdue
                        border_color = "#E57373"
                        urgency_text = f"OVERDUE by {abs(days_until)} day(s)"
                    elif days_until == 0:
                        bg_color = "#FFF3E0"  # Light orange for today
                        border_color = "#FFB74D"
                        urgency_text = "DUE TODAY"
                    elif days_until <= 7:
                        bg_color = "#FFF9C4"  # Light yellow for soon
                        border_color = "#FFD54F"
                        urgency_text = f"Due in {days_until} day(s)"
                    else:
                        bg_color = "#F5F5F5"  # Light gray for future
                        border_color = "#BDBDBD"
                        urgency_text = f"Due in {days_until} days"
                else:
                    bg_color = "#F5F5F5"
                    border_color = "#BDBDBD"
                    urgency_text = "No due date"

                # Create card for each item (clickable)
                card = ctk.CTkFrame(scroll, fg_color=bg_color, border_width=2, border_color=border_color)
                card.pack(fill="x", padx=10, pady=5)

                # Make card clickable
                event_id = item['event_id']
                card.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                card.configure(cursor="hand2")

                content = ctk.CTkFrame(card, fg_color="transparent")
                content.pack(fill="x", padx=15, pady=12)

                # Make content frame also clickable
                content.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                content.configure(cursor="hand2")

                # Left side - info
                left_content = ctk.CTkFrame(content, fg_color="transparent")
                left_content.pack(side="left", fill="both", expand=True)
                left_content.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                left_content.configure(cursor="hand2")

                # Event name
                event_label = ctk.CTkLabel(
                    left_content,
                    text=item['event_name'],
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color="#8B5FBF",
                    anchor="w"
                )
                event_label.pack(anchor="w")
                event_label.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                event_label.configure(cursor="hand2")

                # Checklist item description
                desc_label = ctk.CTkLabel(
                    left_content,
                    text=item['description'],
                    font=ctk.CTkFont(size=15),
                    text_color="#4A2D5E",
                    anchor="w"
                )
                desc_label.pack(anchor="w", pady=(3, 0))
                desc_label.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                desc_label.configure(cursor="hand2")

                # Urgency and due date
                info_text = f"{urgency_text}"
                if item['due_date']:
                    formatted_date = datetime.strptime(item['due_date'], '%Y-%m-%d').strftime('%A, %d %B %Y')
                    info_text += f" - {formatted_date}"

                info_label = ctk.CTkLabel(
                    left_content,
                    text=info_text,
                    font=ctk.CTkFont(size=15),
                    text_color="#666666",
                    anchor="w"
                )
                info_label.pack(anchor="w", pady=(3, 0))
                info_label.bind("<Button-1>", lambda e, eid=event_id: self.open_event_from_dashboard(eid))
                info_label.configure(cursor="hand2")

                # Right side - button
                right_content = ctk.CTkFrame(content, fg_color="transparent")
                right_content.pack(side="right", padx=(10, 0))

                ctk.CTkButton(
                    right_content,
                    text="View/Edit Event",
                    command=lambda eid=event_id: self.open_event_from_dashboard(eid),
                    fg_color="#8B5FBF",
                    hover_color="#7A4FB0",
                    text_color="white",
                    width=120,
                    height=32
                ).pack()

        # Show message if nothing to display
        if not has_content:
            ctk.CTkLabel(
                self.main_frame,
                text="No important items to display.\n\nMark checklist items as 'Show on Dashboard' to see them here.\nPrizes not yet received from suppliers will also appear here.",
                font=ctk.CTkFont(size=15),
                text_color="#999999"
            ).pack(pady=40, padx=30)

    def open_event_from_dashboard(self, event_id):
        """Open event details dialog from dashboard"""
        from views.events_view import EventEditDialog
        dialog = EventEditDialog(self, self.db, event_id)
        dialog.wait_window()
        # Refresh dashboard to show any updates
        self.show_dashboard()

    def show_events(self):
        """Display the events view"""
        self.clear_main_frame()

        # Create and display events view
        events_view = EventsView(self.main_frame, self.db, fg_color="#F5F0F6")
        events_view.pack(fill="both", expand=True)

    def show_templates(self):
        """Display the templates view"""
        self.clear_main_frame()

        # Create and display templates view
        templates_view = TemplatesView(self.main_frame, self.db, fg_color="#F5F0F6")
        templates_view.pack(fill="both", expand=True)

    def show_analysis(self):
        """Display the analysis view"""
        self.clear_main_frame()

        # Create and display analysis view
        analysis_view = AnalysisView(self.main_frame, self.db, fg_color="#F5F0F6")
        analysis_view.pack(fill="both", expand=True)

    def show_table_booking(self):
        """Display the table booking view"""
        self.clear_main_frame()

        # Create and display table booking view
        table_booking_view = TableBookingView(self.main_frame, self.db, navigation_manager=self.navigation_manager, fg_color="#F5F0F6")
        table_booking_view.pack(fill="both", expand=True)

    def show_settings(self):
        """Display the settings view"""
        self.clear_main_frame()

        # Create and display settings view
        settings_view = SettingsView(self.main_frame, self.db, fg_color="#F5F0F6")
        settings_view.pack(fill="both", expand=True)

    def show_help(self):
        """Display the help view"""
        self.clear_main_frame()

        # Create and display help view
        help_view = HelpView(self.main_frame, self.db, fg_color="#F5F0F6")
        help_view.pack(fill="both", expand=True)

    def show_feature_requests(self):
        """Display the feature requests view"""
        self.clear_main_frame()

        # Create and display feature requests view
        feature_requests_view = FeatureRequestsView(self.main_frame, self.db, fg_color="#F5F0F6")
        feature_requests_view.pack(fill="both", expand=True)

    def show_feedback(self):
        """Display the feedback view"""
        self.clear_main_frame()

        # Import here to avoid circular imports
        from views.feedback_view import FeedbackView
        feedback_view = FeedbackView(self.main_frame, self.db, fg_color="#F5F0F6")
        feedback_view.pack(fill="both", expand=True)

    def show_deleted_events(self):
        """Display the deleted events view"""
        self.clear_main_frame()

        # Create and display deleted events view
        deleted_events_view = DeletedEventsView(self.main_frame, self.db, fg_color="#F5F0F6")
        deleted_events_view.pack(fill="both", expand=True)

    def show_calendar(self):
        """Display the calendar view"""
        self.clear_main_frame()

        # Import here to avoid circular imports
        from views.calendar_view import CalendarView
        calendar_view = CalendarView(self.main_frame, self.db, navigation_manager=self.navigation_manager, fg_color="#F5F0F6")
        calendar_view.pack(fill="both", expand=True)

        # Set as root view in navigation stack
        self.navigation_manager.view_stack.append((calendar_view, "Calendar", {}))
        self.navigation_manager.current_view = calendar_view

    def setup_keyboard_shortcuts(self):
        """Set up global keyboard shortcuts"""
        # Ctrl+N - Quick create new event
        self.bind('<Control-n>', lambda e: self.quick_new_event())

        # Ctrl+S - Save current form (delegates to current view if it has save method)
        self.bind('<Control-s>', lambda e: self.save_current_view())

        # Ctrl+P - Print current view (delegates to current view if it has print method)
        self.bind('<Control-p>', lambda e: self.print_current_view())

        # Ctrl+B - Manual backup
        self.bind('<Control-b>', lambda e: self.manual_backup())

        # Ctrl++ or Ctrl+= - Zoom in
        self.bind('<Control-plus>', lambda e: self.zoom_in())
        self.bind('<Control-equal>', lambda e: self.zoom_in())  # For keyboards without numpad

        # Ctrl+- - Zoom out
        self.bind('<Control-minus>', lambda e: self.zoom_out())

        # Ctrl+0 - Reset zoom
        self.bind('<Control-Key-0>', lambda e: self.zoom_reset())

        # Ctrl+MouseWheel - Zoom in/out
        self.bind('<Control-MouseWheel>', self._on_ctrl_mousewheel)

        # F1 - Open help
        self.bind('<F1>', lambda e: self.show_help())

    def quick_new_event(self):
        """Quick create new event shortcut"""
        self.show_events()
        # Give the events view time to load, then trigger new event dialog
        self.after(100, self._trigger_new_event)

    def _trigger_new_event(self):
        """Trigger new event dialog in events view"""
        # Find the EventsView widget and call its method
        for widget in self.main_frame.winfo_children():
            if hasattr(widget, 'show_new_event_dialog'):
                widget.show_new_event_dialog()
                break

    def save_current_view(self):
        """Save current view if it has a save method"""
        for widget in self.main_frame.winfo_children():
            if hasattr(widget, 'save'):
                widget.save()
                return
        # If no save method found, show message
        from tkinter import messagebox
        messagebox.showinfo("Save", "No active form to save")

    def print_current_view(self):
        """Print current view if it has a print method"""
        for widget in self.main_frame.winfo_children():
            if hasattr(widget, 'print_view'):
                widget.print_view()
                return
        # If no print method found, show message
        from tkinter import messagebox
        messagebox.showinfo("Print", "Current view does not support printing")

    def manual_backup(self):
        """Create a manual backup"""
        from tkinter import messagebox, filedialog

        if not os.path.exists("events.db"):
            messagebox.showerror("Error", "No database file found")
            return

        # Ask user where to save backup
        filename = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            initialfile=f"events_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )

        if filename:
            try:
                shutil.copy2("events.db", filename)
                messagebox.showinfo("Backup Complete", f"Database backed up to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Backup Failed", f"Failed to create backup:\n{str(e)}")

    def perform_automatic_backup(self):
        """Perform automatic daily backup if needed"""
        try:
            # Create backups directory if it doesn't exist
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            # Check if backup was done today
            today = datetime.now().strftime('%Y%m%d')
            today_backup = backup_dir / f"events_backup_{today}.db"

            if not today_backup.exists() and os.path.exists("events.db"):
                # Create backup
                shutil.copy2("events.db", today_backup)
                print(f"[AUTO-BACKUP] Created: {today_backup}")

                # Clean up old backups (keep only last 7)
                self.cleanup_old_backups(backup_dir)

                # Update the backup label
                if hasattr(self, 'backup_info_label'):
                    self.backup_info_label.configure(text=self.get_last_backup_text())

        except Exception as e:
            print(f"[AUTO-BACKUP] Error: {e}")

    def cleanup_old_backups(self, backup_dir):
        """Keep only the last 7 backups"""
        try:
            # Get all backup files
            backups = sorted(backup_dir.glob("events_backup_*.db"), reverse=True)

            # Delete backups beyond the 7 most recent
            for old_backup in backups[7:]:
                old_backup.unlink()
                print(f"[AUTO-BACKUP] Deleted old backup: {old_backup.name}")

        except Exception as e:
            print(f"[AUTO-BACKUP] Error cleaning old backups: {e}")

    def zoom_in(self):
        """Increase the UI scale"""
        self.current_scale = min(2.0, self.current_scale + 0.1)
        ctk.set_widget_scaling(self.current_scale)
        ctk.set_window_scaling(self.current_scale)
        self.update_title_with_zoom()

    def zoom_out(self):
        """Decrease the UI scale"""
        self.current_scale = max(0.5, self.current_scale - 0.1)
        ctk.set_widget_scaling(self.current_scale)
        ctk.set_window_scaling(self.current_scale)
        self.update_title_with_zoom()

    def zoom_reset(self):
        """Reset the UI scale to 100%"""
        self.current_scale = 1.0
        ctk.set_widget_scaling(self.current_scale)
        ctk.set_window_scaling(self.current_scale)
        self.update_title_with_zoom()

    @classmethod
    def get_current_scale(cls):
        """Get the current zoom scale for use by dialogs"""
        if hasattr(cls, '_instance'):
            return cls._instance.current_scale
        return 1.0

    def update_title_with_zoom(self):
        """Update window title to show current zoom level"""
        zoom_percent = int(self.current_scale * 100)
        self.title(f"TT Events Manager ({zoom_percent}%)")

    def _on_ctrl_mousewheel(self, event):
        """Handle Ctrl+MouseWheel for zooming"""
        if event.delta > 0:
            # Scroll up = zoom in
            self.zoom_in()
        else:
            # Scroll down = zoom out
            self.zoom_out()

    def get_last_backup_text(self):
        """Get text showing last backup time"""
        try:
            backup_dir = Path("backups")
            if not backup_dir.exists():
                return "No backups yet"

            # Get most recent backup
            backups = sorted(backup_dir.glob("events_backup_*.db"), reverse=True)
            if not backups:
                return "No backups yet"

            # Get the date from filename
            latest = backups[0]
            date_str = latest.stem.replace("events_backup_", "")
            backup_date = datetime.strptime(date_str, '%Y%m%d')

            # Check if it's today
            today = datetime.now().date()
            if backup_date.date() == today:
                return "Last backup: Today"
            else:
                days_ago = (today - backup_date.date()).days
                if days_ago == 1:
                    return "Last backup: Yesterday"
                else:
                    return f"Last backup:\n{days_ago} days ago"

        except Exception as e:
            return "Backup status unknown"


def main():
    """Main entry point"""
    app = BGEventsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
