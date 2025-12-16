"""Table Booking Management View"""
import customtkinter as ctk
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import calendar


class TableBookingView(ctk.CTkFrame):
    """View for managing table bookings and capacity"""

    def __init__(self, parent, database, navigation_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = database
        self.navigation_manager = navigation_manager
        self.selected_date = datetime.now().date()
        self.current_week_start = self._get_week_start(self.selected_date)

        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Title and settings bar
        self.create_header(main_container)

        # Week navigation and overview
        self.create_week_navigation(main_container)
        self.week_overview_frame = ctk.CTkFrame(main_container, fg_color="white", corner_radius=10)
        self.week_overview_frame.pack(fill="x", pady=(10, 20))

        # Daily detail view
        self.daily_view_frame = ctk.CTkScrollableFrame(main_container, fg_color="white", corner_radius=10)
        self.daily_view_frame.pack(fill="both", expand=True)

        # Load initial data
        self.refresh_view()

    def create_header(self, parent):
        """Create header with title and settings"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Table Booking Manager",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(side="left")

        # Settings button
        settings_btn = ctk.CTkButton(
            header_frame,
            text="⚙ Settings",
            command=self.open_settings_dialog,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=120,
            height=35
        )
        settings_btn.pack(side="right", padx=(10, 0))

        # Export button
        export_btn = ctk.CTkButton(
            header_frame,
            text="📄 Export Day",
            command=self.export_day_schedule,
            fg_color="#D4A5D4",
            hover_color="#C494C4",
            text_color="#4A2D5E",
            width=140,
            height=35
        )
        export_btn.pack(side="right")

        # Current capacity display
        total_tables = int(self.db.get_setting('total_tables_available') or 10)
        capacity_label = ctk.CTkLabel(
            header_frame,
            text=f"Total Tables: {total_tables}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        )
        capacity_label.pack(side="right", padx=(0, 20))

    def create_week_navigation(self, parent):
        """Create week navigation controls"""
        nav_frame = ctk.CTkFrame(parent, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(0, 10))

        # Previous week button
        prev_btn = ctk.CTkButton(
            nav_frame,
            text="← Previous Week",
            command=self.previous_week,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=140
        )
        prev_btn.pack(side="left")

        # Current week display
        week_end = self.current_week_start + timedelta(days=6)
        self.week_label = ctk.CTkLabel(
            nav_frame,
            text=f"Week of {self.current_week_start.strftime('%d %b %Y')} - {week_end.strftime('%d %b %Y')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        )
        self.week_label.pack(side="left", expand=True)

        # Today button
        today_btn = ctk.CTkButton(
            nav_frame,
            text="Today",
            command=self.go_to_today,
            fg_color="#D4A5D4",
            hover_color="#C494C4",
            text_color="#4A2D5E",
            width=100
        )
        today_btn.pack(side="left", padx=(0, 10))

        # Next week button
        next_btn = ctk.CTkButton(
            nav_frame,
            text="Next Week →",
            command=self.next_week,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=140
        )
        next_btn.pack(side="left")

    def _get_week_start(self, date: datetime.date) -> datetime.date:
        """Get the Monday of the week containing the given date"""
        return date - timedelta(days=date.weekday())

    def previous_week(self):
        """Navigate to previous week"""
        self.current_week_start -= timedelta(days=7)
        self.refresh_view()

    def next_week(self):
        """Navigate to next week"""
        self.current_week_start += timedelta(days=7)
        self.refresh_view()

    def go_to_today(self):
        """Navigate to current week and select today"""
        self.selected_date = datetime.now().date()
        self.current_week_start = self._get_week_start(self.selected_date)
        self.refresh_view()

    def refresh_view(self):
        """Refresh all data displays"""
        # Update week label
        week_end = self.current_week_start + timedelta(days=6)
        self.week_label.configure(
            text=f"Week of {self.current_week_start.strftime('%d %b %Y')} - {week_end.strftime('%d %b %Y')}"
        )

        # Refresh week overview
        self.refresh_week_overview()

        # Refresh daily view
        self.refresh_daily_view()

    def refresh_week_overview(self):
        """Refresh the weekly overview grid"""
        # Clear existing widgets
        for widget in self.week_overview_frame.winfo_children():
            widget.destroy()

        # Get total tables available
        total_tables = int(self.db.get_setting('total_tables_available') or 10)

        # Create day cards for the week
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for i, day_name in enumerate(days):
            current_date = self.current_week_start + timedelta(days=i)

            # Check for capacity override
            override_capacity = self._get_capacity_override(current_date)
            day_capacity = override_capacity if override_capacity else total_tables

            # Get events for this day
            events = self._get_events_for_date(current_date)

            # Calculate table usage
            scheduled_tables = sum(e['tables_booked'] or 0 for e in events if e['start_time'])
            unscheduled_tables = sum(e['tables_booked'] or 0 for e in events if not e['start_time'])

            # Determine color based on usage
            utilization = (scheduled_tables / day_capacity * 100) if day_capacity > 0 else 0
            if utilization < 70:
                color = "#C8E6C9"  # Green
            elif utilization < 90:
                color = "#FFF9C4"  # Yellow
            elif utilization <= 100:
                color = "#FFCCBC"  # Orange
            else:
                color = "#FFCDD2"  # Red (overbooked)

            # Create day card
            day_card = ctk.CTkFrame(self.week_overview_frame, fg_color=color, corner_radius=8)
            day_card.grid(row=0, column=i, padx=5, pady=10, sticky="nsew")
            self.week_overview_frame.grid_columnconfigure(i, weight=1, uniform="day")

            # Day name and date
            is_today = current_date == datetime.now().date()
            day_text = f"{day_name}\n{current_date.strftime('%d %b')}"
            if is_today:
                day_text += "\n(Today)"

            day_label = ctk.CTkLabel(
                day_card,
                text=day_text,
                font=ctk.CTkFont(size=12, weight="bold" if is_today else "normal"),
                text_color="#4A2D5E"
            )
            day_label.pack(pady=(10, 5))

            # Table usage
            usage_text = f"{scheduled_tables}/{day_capacity} tables"
            usage_label = ctk.CTkLabel(
                day_card,
                text=usage_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#4A2D5E"
            )
            usage_label.pack(pady=5)

            # Event count
            event_count_text = f"{len(events)} event{'s' if len(events) != 1 else ''}"
            event_count_label = ctk.CTkLabel(
                day_card,
                text=event_count_text,
                font=ctk.CTkFont(size=11),
                text_color="#666666"
            )
            event_count_label.pack(pady=5)

            # Unscheduled warning
            if unscheduled_tables > 0:
                warning_label = ctk.CTkLabel(
                    day_card,
                    text=f"⚠ {unscheduled_tables} tables\nunscheduled",
                    font=ctk.CTkFont(size=10),
                    text_color="#D32F2F"
                )
                warning_label.pack(pady=(0, 5))

            # Click to view day
            day_card.bind("<Button-1>", lambda e, d=current_date: self.select_date(d))
            for child in day_card.winfo_children():
                child.bind("<Button-1>", lambda e, d=current_date: self.select_date(d))

    def select_date(self, date: datetime.date):
        """Select a specific date for detailed view"""
        self.selected_date = date
        self.refresh_daily_view()

    def refresh_daily_view(self):
        """Refresh the daily detail view"""
        # Clear existing widgets
        for widget in self.daily_view_frame.winfo_children():
            widget.destroy()

        # Header with selected date and add booking button
        header_frame = ctk.CTkFrame(self.daily_view_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 20), padx=10)

        date_header = ctk.CTkLabel(
            header_frame,
            text=f"Details for {self.selected_date.strftime('%A, %d %B %Y')}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        )
        date_header.pack(side="left")

        # Add booking button
        add_booking_btn = ctk.CTkButton(
            header_frame,
            text="+ Add Booking",
            command=lambda: self.open_booking_dialog(),
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=120,
            height=30
        )
        add_booking_btn.pack(side="right")

        # Operating hours display
        hours_info = self._get_operating_hours_for_date(self.selected_date)
        hours_frame = ctk.CTkFrame(self.daily_view_frame, fg_color="#E8F5E9" if hours_info['is_open'] else "#FFEBEE", corner_radius=8)
        hours_frame.pack(fill="x", padx=10, pady=(0, 10))

        hours_content_frame = ctk.CTkFrame(hours_frame, fg_color="transparent")
        hours_content_frame.pack(fill="x", padx=15, pady=10)

        if hours_info['is_open']:
            open_time = hours_info['open_time'].rsplit(':', 1)[0] if hours_info['open_time'] else 'N/A'
            close_time = hours_info['close_time'].rsplit(':', 1)[0] if hours_info['close_time'] else 'N/A'
            hours_text = f"🕒 Operating Hours: {open_time} - {close_time}"
        else:
            hours_text = "🚫 Closed"

        if hours_info.get('is_special_date') and hours_info.get('reason'):
            hours_text += f" ({hours_info['reason']})"

        hours_label = ctk.CTkLabel(
            hours_content_frame,
            text=hours_text,
            font=ctk.CTkFont(size=13, weight="bold" if hours_info.get('is_special_date') else "normal"),
            text_color="#2E7D32" if hours_info['is_open'] else "#C62828"
        )
        hours_label.pack(side="left")

        # Edit hours button
        edit_hours_btn = ctk.CTkButton(
            hours_content_frame,
            text="Edit Hours",
            command=self.edit_date_hours,
            fg_color="#8B5FBF",
            hover_color="#7A4FAF",
            text_color="white",
            width=100,
            height=28
        )
        edit_hours_btn.pack(side="right")

        # Get events and standalone bookings for selected date
        events = self._get_events_for_date(self.selected_date)
        standalone_bookings = self._get_standalone_bookings_for_date(self.selected_date)

        # Get capacity for this day
        total_tables = int(self.db.get_setting('total_tables_available') or 10)
        override_capacity = self._get_capacity_override(self.selected_date)
        day_capacity = override_capacity if override_capacity else total_tables

        # Separate scheduled and unscheduled items (both events and bookings)
        scheduled_items = []
        unscheduled_items = []

        # Add events with type marker
        for event in events:
            item = dict(event)
            item['_type'] = 'event'
            if event['start_time']:
                scheduled_items.append(item)
            else:
                unscheduled_items.append(item)

        # Add standalone bookings with type marker
        for booking in standalone_bookings:
            item = dict(booking)
            item['_type'] = 'booking'
            if booking['start_time']:
                scheduled_items.append(item)
            else:
                unscheduled_items.append(item)

        # Sort scheduled items by time
        scheduled_items.sort(key=lambda x: x['start_time'])

        # Calculate usage
        scheduled_tables = sum(item['tables_booked'] or 0 for item in scheduled_items)
        unscheduled_tables = sum(item['tables_booked'] or 0 for item in unscheduled_items)

        # Summary card
        summary_frame = ctk.CTkFrame(self.daily_view_frame, fg_color="#F3E5F5", corner_radius=8)
        summary_frame.pack(fill="x", padx=10, pady=(0, 20))

        summary_text = f"📊 {scheduled_tables}/{day_capacity} tables scheduled"
        if unscheduled_tables > 0:
            summary_text += f" | ⚠ {unscheduled_tables} tables unscheduled"

        summary_label = ctk.CTkLabel(
            summary_frame,
            text=summary_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        )
        summary_label.pack(pady=15, padx=20)

        # Unscheduled items section (if any)
        if unscheduled_items:
            unscheduled_header = ctk.CTkLabel(
                self.daily_view_frame,
                text="⚠ Unscheduled Items (No Time Set)",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#D32F2F"
            )
            unscheduled_header.pack(pady=(0, 10), padx=10, anchor="w")

            for item in unscheduled_items:
                if item['_type'] == 'event':
                    self._create_event_card(item, is_unscheduled=True, has_conflict=False)
                else:  # booking
                    self._create_booking_card(item, is_unscheduled=True)

            # Separator
            separator = ctk.CTkFrame(self.daily_view_frame, height=2, fg_color="#E6D9F2")
            separator.pack(fill="x", padx=10, pady=20)

        # Scheduled items section (events and bookings together)
        if scheduled_items:
            scheduled_header = ctk.CTkLabel(
                self.daily_view_frame,
                text="📅 Scheduled Items",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#8B5FBF"
            )
            scheduled_header.pack(pady=(0, 10), padx=10, anchor="w")

            # Check for conflicts (only for events, as they have IDs that matter)
            scheduled_events_only = [item for item in scheduled_items if item['_type'] == 'event']
            conflicts = self._detect_time_conflicts(scheduled_events_only)

            # Show conflict warning if any
            if conflicts:
                conflict_warning = ctk.CTkLabel(
                    self.daily_view_frame,
                    text=f"⚠ WARNING: {len(conflicts)} event(s) have overlapping times!",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#D32F2F"
                )
                conflict_warning.pack(pady=(0, 10), padx=10, anchor="w")

            # Display all items in chronological order
            for item in scheduled_items:
                if item['_type'] == 'event':
                    has_conflict = item['id'] in conflicts
                    self._create_event_card(item, is_unscheduled=False, has_conflict=has_conflict)
                else:  # booking
                    self._create_booking_card(item, is_unscheduled=False)

        # Empty message if nothing at all
        if not scheduled_items and not unscheduled_items:
            empty_label = ctk.CTkLabel(
                self.daily_view_frame,
                text="No events or bookings scheduled for this day",
                font=ctk.CTkFont(size=14),
                text_color="#999999"
            )
            empty_label.pack(pady=40)

    def _create_event_card(self, event: dict, is_unscheduled: bool, has_conflict: bool = False):
        """Create an event card in the daily view"""
        tables_booked = event.get('tables_booked') or 0

        # Determine card color based on status
        if is_unscheduled or has_conflict or tables_booked == 0:
            card_color = "#FFEBEE"  # Red for unscheduled, conflicts, or no tables booked
        else:
            card_color = "#E8F5E9"  # Green for normal scheduled events

        event_card = ctk.CTkFrame(self.daily_view_frame, fg_color=card_color, corner_radius=8)
        event_card.pack(fill="x", padx=10, pady=5)

        # Main content frame
        content_frame = ctk.CTkFrame(event_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=12)

        # Left side: Event info
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)

        # Event name
        name_label = ctk.CTkLabel(
            left_frame,
            text=event['event_name'],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        )
        name_label.pack(anchor="w")

        # Time
        if event['start_time'] and event['end_time']:
            start_time = event['start_time'].rsplit(':', 1)[0]  # Remove seconds
            end_time = event['end_time'].rsplit(':', 1)[0]
            time_text = f"🕐 {start_time} - {end_time}"
        else:
            time_text = "🕐 No time set"

        time_label = ctk.CTkLabel(
            left_frame,
            text=time_text,
            font=ctk.CTkFont(size=13),
            text_color="#666666",
            anchor="w"
        )
        time_label.pack(anchor="w", pady=(2, 0))

        # Event type
        if event.get('event_type_name'):
            type_label = ctk.CTkLabel(
                left_frame,
                text=f"📌 {event['event_type_name']}",
                font=ctk.CTkFont(size=12),
                text_color="#666666",
                anchor="w"
            )
            type_label.pack(anchor="w", pady=(2, 0))

        # Conflict warning
        if has_conflict:
            conflict_label = ctk.CTkLabel(
                left_frame,
                text="⚠ TIME CONFLICT",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#D32F2F",
                anchor="w"
            )
            conflict_label.pack(anchor="w", pady=(4, 0))

        # No tables warning
        if not is_unscheduled and tables_booked == 0:
            no_tables_label = ctk.CTkLabel(
                left_frame,
                text="⚠ NO TABLES BOOKED",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#D32F2F",
                anchor="w"
            )
            no_tables_label.pack(anchor="w", pady=(4, 0))

        # Right side: Table count
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.pack(side="right")

        tables_booked = event['tables_booked'] or 0
        tables_label = ctk.CTkLabel(
            right_frame,
            text=f"{tables_booked}\ntables",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4A2D5E"
        )
        tables_label.pack()

        # View event button
        view_btn = ctk.CTkButton(
            right_frame,
            text="View Event",
            command=lambda: self.view_event_details(event['id']),
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=100,
            height=30
        )
        view_btn.pack(pady=(5, 0))

    def _get_events_for_date(self, date: datetime.date) -> List[dict]:
        """Get all events for a specific date"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                e.*,
                et.name as event_type_name
            FROM events e
            LEFT JOIN event_types et ON e.event_type_id = et.id
            WHERE e.event_date = ? AND e.is_cancelled = 0 AND e.is_deleted = 0
            ORDER BY e.start_time
        ''', (date.strftime('%Y-%m-%d'),))

        events = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return events

    def _get_standalone_bookings_for_date(self, date: datetime.date) -> List[dict]:
        """Get all standalone bookings for a specific date"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT *
            FROM standalone_bookings
            WHERE booking_date = ? AND is_deleted = 0
            ORDER BY start_time
        ''', (date.strftime('%Y-%m-%d'),))

        bookings = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return bookings

    def _delete_standalone_booking(self, booking_id: int):
        """Soft delete a standalone booking"""
        from tkinter import messagebox
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this booking?"):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE standalone_bookings SET is_deleted = 1 WHERE id = ?', (booking_id,))
            conn.commit()
            conn.close()
            self.refresh_view()

    def _detect_time_conflicts(self, events: List[dict]) -> set:
        """Detect events that have overlapping times and return their IDs"""
        conflicts = set()

        for i, event1 in enumerate(events):
            if not event1['start_time'] or not event1['end_time']:
                continue

            for event2 in events[i+1:]:
                if not event2['start_time'] or not event2['end_time']:
                    continue

                # Check if times overlap
                start1 = event1['start_time']
                end1 = event1['end_time']
                start2 = event2['start_time']
                end2 = event2['end_time']

                # Events overlap if: start1 < end2 AND start2 < end1
                if start1 < end2 and start2 < end1:
                    conflicts.add(event1['id'])
                    conflicts.add(event2['id'])

        return conflicts

    def _get_capacity_override(self, date: datetime.date) -> Optional[int]:
        """Get capacity override for a specific date, if any"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT total_tables FROM daily_capacity_overrides
            WHERE override_date = ?
        ''', (date.strftime('%Y-%m-%d'),))

        result = cursor.fetchone()
        conn.close()

        return result['total_tables'] if result else None

    def _get_operating_hours_for_date(self, date: datetime.date) -> dict:
        """Get operating hours for a specific date, checking date-specific overrides first"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # First check for date-specific hours
        cursor.execute('''
            SELECT is_open, open_time, close_time, reason
            FROM date_specific_hours
            WHERE specific_date = ?
        ''', (date.strftime('%Y-%m-%d'),))

        date_specific = cursor.fetchone()

        if date_specific:
            # Use date-specific hours
            conn.close()
            return {
                'is_open': bool(date_specific['is_open']),
                'open_time': date_specific['open_time'],
                'close_time': date_specific['close_time'],
                'reason': date_specific.get('reason'),
                'is_special_date': True
            }

        # Fall back to day-of-week hours
        day_of_week = date.weekday()  # 0 = Monday, 6 = Sunday
        cursor.execute('''
            SELECT is_open, open_time, close_time
            FROM operating_hours
            WHERE day_of_week = ?
        ''', (day_of_week,))

        regular_hours = cursor.fetchone()
        conn.close()

        if regular_hours:
            return {
                'is_open': bool(regular_hours['is_open']),
                'open_time': regular_hours['open_time'],
                'close_time': regular_hours['close_time'],
                'reason': None,
                'is_special_date': False
            }

        # Default if no hours configured
        return {
            'is_open': True,
            'open_time': '10:00:00',
            'close_time': '22:00:00',
            'reason': None,
            'is_special_date': False
        }

    def view_event_details(self, event_id: int):
        """Open event details window"""
        from views.events_view import EventEditDialog
        dialog = EventEditDialog(self, self.db, event_id)
        dialog.wait_window()
        self.refresh_view()

    def _create_booking_card(self, booking: dict, is_unscheduled: bool):
        """Create a standalone booking card in the daily view"""
        tables_booked = booking.get('tables_booked') or 0

        # Determine card color based on status
        if is_unscheduled:
            card_color = "#FFEBEE"  # Red for unscheduled
        else:
            card_color = "#E3F2FD"  # Light blue for bookings

        booking_card = ctk.CTkFrame(self.daily_view_frame, fg_color=card_color, corner_radius=8)
        booking_card.pack(fill="x", padx=10, pady=5)

        # Main content frame
        content_frame = ctk.CTkFrame(booking_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=12)

        # Left side: Booking info
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)

        # Booking name
        name_label = ctk.CTkLabel(
            left_frame,
            text=booking['booking_name'],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        )
        name_label.pack(anchor="w")

        # Time
        if booking['start_time'] and booking['end_time']:
            start_time = booking['start_time'].rsplit(':', 1)[0]  # Remove seconds
            end_time = booking['end_time'].rsplit(':', 1)[0]
            time_text = f"🕐 {start_time} - {end_time}"
        else:
            time_text = "🕐 No time set"

        time_label = ctk.CTkLabel(
            left_frame,
            text=time_text,
            font=ctk.CTkFont(size=13),
            text_color="#666666",
            anchor="w"
        )
        time_label.pack(anchor="w", pady=(2, 0))

        # Description
        if booking.get('booking_description'):
            desc_label = ctk.CTkLabel(
                left_frame,
                text=f"📝 {booking['booking_description']}",
                font=ctk.CTkFont(size=12),
                text_color="#666666",
                anchor="w",
                wraplength=400
            )
            desc_label.pack(anchor="w", pady=(2, 0))

        # Notes
        if booking.get('notes'):
            notes_label = ctk.CTkLabel(
                left_frame,
                text=f"💬 {booking['notes']}",
                font=ctk.CTkFont(size=11),
                text_color="#888888",
                anchor="w",
                wraplength=400
            )
            notes_label.pack(anchor="w", pady=(2, 0))

        # Right side: Table count and actions
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.pack(side="right")

        tables_label = ctk.CTkLabel(
            right_frame,
            text=f"{tables_booked}\ntables",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4A2D5E"
        )
        tables_label.pack()

        # Button frame for edit and delete
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.pack(pady=(5, 0))

        # Edit button
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="Edit",
            command=lambda: self.open_booking_dialog(booking),
            fg_color="#5A7FA3",
            hover_color="#4A6F93",
            text_color="white",
            width=70,
            height=28
        )
        edit_btn.pack(side="left", padx=2)

        # Delete button
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=lambda: self._delete_standalone_booking(booking['id']),
            fg_color="#D32F2F",
            hover_color="#C12F2F",
            text_color="white",
            width=70,
            height=28
        )
        delete_btn.pack(side="left", padx=2)

    def open_booking_dialog(self, booking: dict = None):
        """Open dialog to add or edit a standalone booking"""
        dialog = StandaloneBookingDialog(self, self.db, self.selected_date, booking)
        dialog.wait_window()
        self.refresh_view()

    def edit_date_hours(self):
        """Open dialog to edit operating hours for the selected date"""
        dialog = SpecialDateDialog(self, self.db, self.selected_date)
        dialog.wait_window()
        # Schedule refresh on next event loop to ensure dialog is fully destroyed
        # and database changes are committed
        self.after(10, self.refresh_view)

    def open_settings_dialog(self):
        """Open settings dialog for table capacity configuration"""
        dialog = TableSettingsDialog(self, self.db)
        dialog.wait_window()
        self.refresh_view()

    def export_day_schedule(self):
        """Export daily schedule to PDF"""
        from tkinter import messagebox, filedialog
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        try:
            # Get events and bookings for selected date
            events = self._get_events_for_date(self.selected_date)
            standalone_bookings = self._get_standalone_bookings_for_date(self.selected_date)

            if not events and not standalone_bookings:
                messagebox.showinfo("Export", f"No events or bookings scheduled for {self.selected_date.strftime('%d %B %Y')}")
                return

            # Ask for save location
            date_str = self.selected_date.strftime('%Y%m%d')
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"table_schedule_{date_str}.pdf"
            )

            if not filename:
                return

            # Create PDF
            doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm)
            story = []
            styles = getSampleStyleSheet()

            # Title style
            title_style = ParagraphStyle(
                name='CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#8B5FBF'),
                spaceAfter=12,
                alignment=TA_CENTER
            )

            # Title
            title_text = f"Table Schedule - {self.selected_date.strftime('%A, %d %B %Y')}"
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 10*mm))

            # Get capacity
            total_tables = int(self.db.get_setting('total_tables_available') or 10)
            override_capacity = self._get_capacity_override(self.selected_date)
            day_capacity = override_capacity if override_capacity else total_tables

            # Combine events and bookings
            scheduled_items = []
            unscheduled_items = []

            for event in events:
                item = dict(event)
                item['_type'] = 'event'
                if event['start_time']:
                    scheduled_items.append(item)
                else:
                    unscheduled_items.append(item)

            for booking in standalone_bookings:
                item = dict(booking)
                item['_type'] = 'booking'
                if booking['start_time']:
                    scheduled_items.append(item)
                else:
                    unscheduled_items.append(item)

            # Sort by time
            scheduled_items.sort(key=lambda x: x['start_time'])

            # Calculate summary
            scheduled_tables = sum(item['tables_booked'] or 0 for item in scheduled_items)
            total_items = len(events) + len(standalone_bookings)

            summary_text = f"<b>Total Tables Available:</b> {day_capacity} | <b>Tables Booked:</b> {scheduled_tables} | <b>Total Items:</b> {total_items}"
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 10*mm))

            # Unscheduled items
            if unscheduled_items:
                story.append(Paragraph("<b>Unscheduled Items (No Time Set)</b>", styles['Heading2']))
                story.append(Spacer(1, 5*mm))

                unscheduled_data = [['Name', 'Type', 'Tables']]
                for item in unscheduled_items:
                    if item['_type'] == 'event':
                        name = item['event_name']
                        type_text = item.get('event_type_name') or 'Event'
                    else:  # booking
                        name = item['booking_name']
                        type_text = 'Booking'

                    unscheduled_data.append([
                        Paragraph(name, styles['Normal']),
                        Paragraph(type_text, styles['Normal']),
                        str(item['tables_booked'] or 0)
                    ])

                unscheduled_table = Table(unscheduled_data, colWidths=[80*mm, 60*mm, 30*mm])
                unscheduled_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFCDD2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4A2D5E')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFEBEE')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(unscheduled_table)
                story.append(Spacer(1, 10*mm))

            # Scheduled items
            if scheduled_items:
                story.append(Paragraph("<b>Scheduled Items</b>", styles['Heading2']))
                story.append(Spacer(1, 5*mm))

                # Detect conflicts (only for events)
                scheduled_events_only = [item for item in scheduled_items if item['_type'] == 'event']
                conflicts = self._detect_time_conflicts(scheduled_events_only)

                scheduled_data = [['Time', 'Name', 'Type', 'Tables']]
                for item in scheduled_items:
                    start_time = item['start_time'].rsplit(':', 1)[0] if item['start_time'] else 'N/A'
                    end_time = item['end_time'].rsplit(':', 1)[0] if item['end_time'] else 'N/A'
                    time_str = f"{start_time} - {end_time}"

                    if item['_type'] == 'event':
                        name = item['event_name']
                        type_text = item.get('event_type_name') or 'Event'
                    else:  # booking
                        name = item['booking_name']
                        type_text = 'Booking'

                    scheduled_data.append([
                        time_str,
                        Paragraph(name, styles['Normal']),
                        Paragraph(type_text, styles['Normal']),
                        str(item['tables_booked'] or 0)
                    ])

                scheduled_table = Table(scheduled_data, colWidths=[35*mm, 70*mm, 45*mm, 20*mm])

                # Base style with white background for data rows
                table_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C8E6C9')),  # Header green
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4A2D5E')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # White for data rows
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]

                # Color conflict rows in red (only for events)
                for idx, item in enumerate(scheduled_items):
                    if item['_type'] == 'event' and item['id'] in conflicts:
                        row_num = idx + 1  # +1 because row 0 is header
                        table_style.append(('BACKGROUND', (0, row_num), (-1, row_num), colors.HexColor('#FFEBEE')))

                scheduled_table.setStyle(TableStyle(table_style))
                story.append(scheduled_table)

            # Build PDF
            doc.build(story)
            messagebox.showinfo("Export Complete", f"Schedule exported to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export schedule: {str(e)}")


class TableSettingsDialog(ctk.CTkToplevel):
    """Dialog for configuring table booking settings"""

    def __init__(self, parent, database):
        super().__init__(parent)
        self.db = database

        self.title("Table Booking Settings")
        self.geometry("600x700")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Main frame with scrolling
        main_frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="Table Booking Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(pady=(0, 20))

        # Total tables
        tables_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        tables_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            tables_frame,
            text="Total Tables Available:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        current_tables = self.db.get_setting('total_tables_available') or '10'
        self.tables_entry = ctk.CTkEntry(
            tables_frame,
            width=100,
            font=ctk.CTkFont(size=14)
        )
        self.tables_entry.insert(0, current_tables)
        self.tables_entry.pack(anchor="w", padx=15, pady=(0, 15))

        # Setup padding
        setup_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        setup_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            setup_frame,
            text="Default Setup Time (minutes):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        current_setup = self.db.get_setting('default_setup_padding_minutes') or '30'
        self.setup_entry = ctk.CTkEntry(
            setup_frame,
            width=100,
            font=ctk.CTkFont(size=14)
        )
        self.setup_entry.insert(0, current_setup)
        self.setup_entry.pack(anchor="w", padx=15, pady=(0, 15))

        # Breakdown padding
        breakdown_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        breakdown_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            breakdown_frame,
            text="Default Breakdown Time (minutes):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        current_breakdown = self.db.get_setting('default_breakdown_padding_minutes') or '15'
        self.breakdown_entry = ctk.CTkEntry(
            breakdown_frame,
            width=100,
            font=ctk.CTkFont(size=14)
        )
        self.breakdown_entry.insert(0, current_breakdown)
        self.breakdown_entry.pack(anchor="w", padx=15, pady=(0, 15))

        # Operating Hours Section
        hours_section = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        hours_section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            hours_section,
            text="Standard Operating Hours:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Get operating hours from database
        operating_hours = self._get_operating_hours()

        # Days of the week
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for day_num, day_name in enumerate(day_names):
            day_data = operating_hours.get(day_num, {'is_open': 1, 'open_time': '10:00:00', 'close_time': '22:00:00'})

            day_frame = ctk.CTkFrame(hours_section, fg_color="#F5F5F5", corner_radius=5)
            day_frame.pack(fill="x", padx=15, pady=5)

            # Day name
            day_label = ctk.CTkLabel(
                day_frame,
                text=day_name,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#4A2D5E",
                width=100,
                anchor="w"
            )
            day_label.pack(side="left", padx=10, pady=8)

            # Hours display
            if day_data['is_open']:
                open_time = day_data['open_time'].rsplit(':', 1)[0] if day_data['open_time'] else '10:00'
                close_time = day_data['close_time'].rsplit(':', 1)[0] if day_data['close_time'] else '22:00'
                hours_text = f"{open_time} - {close_time}"
            else:
                hours_text = "Closed"

            hours_label = ctk.CTkLabel(
                day_frame,
                text=hours_text,
                font=ctk.CTkFont(size=12),
                text_color="#666666",
                width=120,
                anchor="w"
            )
            hours_label.pack(side="left", padx=5)

            # Edit button
            edit_btn = ctk.CTkButton(
                day_frame,
                text="Edit",
                command=lambda d=day_num, n=day_name: self.edit_day_hours(d, n),
                fg_color="#8B5FBF",
                hover_color="#7A4FAF",
                text_color="white",
                width=60,
                height=28
            )
            edit_btn.pack(side="right", padx=10)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(20, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            command=self.save_settings,
            fg_color="#8B5FBF",
            hover_color="#7A4FAF",
            text_color="white",
            width=150,
            height=35
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#999999",
            hover_color="#888888",
            text_color="white",
            width=150,
            height=35
        )
        cancel_btn.pack(side="left", padx=5)

    def save_settings(self):
        """Save settings to database"""
        try:
            # Validate inputs
            total_tables = int(self.tables_entry.get())
            setup_padding = int(self.setup_entry.get())
            breakdown_padding = int(self.breakdown_entry.get())

            if total_tables < 1:
                raise ValueError("Total tables must be at least 1")
            if setup_padding < 0:
                raise ValueError("Setup padding cannot be negative")
            if breakdown_padding < 0:
                raise ValueError("Breakdown padding cannot be negative")

            # Save to database
            self.db.update_setting('total_tables_available', str(total_tables))
            self.db.update_setting('default_setup_padding_minutes', str(setup_padding))
            self.db.update_setting('default_breakdown_padding_minutes', str(breakdown_padding))

            self.destroy()

        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Invalid Input", str(e), parent=self)

    def _get_operating_hours(self):
        """Get operating hours from database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM operating_hours ORDER BY day_of_week')
        rows = cursor.fetchall()
        conn.close()

        # Convert to dict keyed by day_of_week
        hours_dict = {}
        for row in rows:
            hours_dict[row['day_of_week']] = dict(row)

        return hours_dict

    def edit_day_hours(self, day_num: int, day_name: str):
        """Open dialog to edit hours for a specific day"""
        dialog = DayHoursDialog(self, self.db, day_num, day_name)
        dialog.wait_window()
        # Note: Hours will be visible on next open of settings dialog


class StandaloneBookingDialog(ctk.CTkToplevel):
    """Dialog for adding/editing standalone table bookings"""

    def __init__(self, parent, database, selected_date, booking: dict = None):
        super().__init__(parent)
        self.db = database
        self.selected_date = selected_date
        self.booking = booking  # None for new booking, dict for editing

        # Configure window
        if booking:
            self.title("Edit Booking")
        else:
            self.title("Add New Booking")
        self.geometry("550x600")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Main frame
        main_frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="Booking Details" if booking else "New Booking",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#5A7FA3"
        )
        title.pack(pady=(0, 20))

        # Booking name
        name_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        name_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            name_frame,
            text="Booking Name: *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.name_entry = ctk.CTkEntry(
            name_frame,
            font=ctk.CTkFont(size=14),
            placeholder_text="Enter booking name"
        )
        self.name_entry.pack(fill="x", padx=15, pady=(0, 15))
        if booking:
            self.name_entry.insert(0, booking['booking_name'])

        # Description
        desc_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        desc_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            desc_frame,
            text="Description:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.desc_entry = ctk.CTkEntry(
            desc_frame,
            font=ctk.CTkFont(size=14),
            placeholder_text="Brief description"
        )
        self.desc_entry.pack(fill="x", padx=15, pady=(0, 15))
        if booking and booking.get('booking_description'):
            self.desc_entry.insert(0, booking['booking_description'])

        # Date
        date_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        date_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            date_frame,
            text="Date: *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        date_str = booking['booking_date'] if booking else selected_date.strftime('%Y-%m-%d')
        self.date_entry = ctk.CTkEntry(
            date_frame,
            font=ctk.CTkFont(size=14),
            placeholder_text="YYYY-MM-DD"
        )
        self.date_entry.insert(0, date_str)
        self.date_entry.pack(fill="x", padx=15, pady=(0, 15))

        # Times
        time_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        time_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            time_frame,
            text="Times (leave empty for no specific time):",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        times_inner = ctk.CTkFrame(time_frame, fg_color="transparent")
        times_inner.pack(fill="x", padx=15, pady=(0, 15))

        # Start time
        ctk.CTkLabel(
            times_inner,
            text="Start:",
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        ).pack(side="left", padx=(0, 5))

        self.start_time_entry = ctk.CTkEntry(
            times_inner,
            font=ctk.CTkFont(size=14),
            placeholder_text="HH:MM",
            width=100
        )
        self.start_time_entry.pack(side="left", padx=5)
        if booking and booking.get('start_time'):
            self.start_time_entry.insert(0, booking['start_time'].rsplit(':', 1)[0])

        # End time
        ctk.CTkLabel(
            times_inner,
            text="End:",
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        ).pack(side="left", padx=(20, 5))

        self.end_time_entry = ctk.CTkEntry(
            times_inner,
            font=ctk.CTkFont(size=14),
            placeholder_text="HH:MM",
            width=100
        )
        self.end_time_entry.pack(side="left", padx=5)
        if booking and booking.get('end_time'):
            self.end_time_entry.insert(0, booking['end_time'].rsplit(':', 1)[0])

        # Tables booked
        tables_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        tables_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            tables_frame,
            text="Number of Tables: *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.tables_entry = ctk.CTkEntry(
            tables_frame,
            font=ctk.CTkFont(size=14),
            placeholder_text="1",
            width=100
        )
        self.tables_entry.pack(anchor="w", padx=15, pady=(0, 15))
        if booking:
            self.tables_entry.insert(0, str(booking['tables_booked']))
        else:
            self.tables_entry.insert(0, "1")

        # Notes
        notes_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        notes_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            notes_frame,
            text="Notes:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.notes_textbox = ctk.CTkTextbox(
            notes_frame,
            font=ctk.CTkFont(size=12),
            height=80
        )
        self.notes_textbox.pack(fill="x", padx=15, pady=(0, 15))
        if booking and booking.get('notes'):
            self.notes_textbox.insert("1.0", booking['notes'])

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(20, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Booking",
            command=self.save_booking,
            fg_color="#5A7FA3",
            hover_color="#4A6F93",
            text_color="white",
            width=150,
            height=35
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#999999",
            hover_color="#888888",
            text_color="white",
            width=150,
            height=35
        )
        cancel_btn.pack(side="left", padx=5)

    def save_booking(self):
        """Save the booking to database"""
        from tkinter import messagebox

        try:
            # Validate required fields
            booking_name = self.name_entry.get().strip()
            if not booking_name:
                raise ValueError("Booking name is required")

            booking_date = self.date_entry.get().strip()
            if not booking_date:
                raise ValueError("Date is required")

            # Validate date format
            try:
                datetime.strptime(booking_date, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")

            # Validate tables
            try:
                tables_booked = int(self.tables_entry.get().strip())
                if tables_booked < 1:
                    raise ValueError("Number of tables must be at least 1")
            except ValueError:
                raise ValueError("Number of tables must be a valid number")

            # Get optional fields
            booking_description = self.desc_entry.get().strip() or None
            start_time = self.start_time_entry.get().strip() or None
            end_time = self.end_time_entry.get().strip() or None
            notes = self.notes_textbox.get("1.0", "end-1c").strip() or None

            # Validate times if provided
            if start_time:
                try:
                    datetime.strptime(start_time, '%H:%M')
                    start_time = start_time + ":00"  # Add seconds
                except ValueError:
                    raise ValueError("Start time must be in HH:MM format")

            if end_time:
                try:
                    datetime.strptime(end_time, '%H:%M')
                    end_time = end_time + ":00"  # Add seconds
                except ValueError:
                    raise ValueError("End time must be in HH:MM format")

            # Ensure both times are provided or neither
            if (start_time and not end_time) or (end_time and not start_time):
                raise ValueError("Both start and end times must be provided, or leave both empty")

            # Save to database
            conn = self.db.get_connection()
            cursor = conn.cursor()

            if self.booking:
                # Update existing booking
                cursor.execute('''
                    UPDATE standalone_bookings
                    SET booking_name = ?,
                        booking_description = ?,
                        booking_date = ?,
                        start_time = ?,
                        end_time = ?,
                        tables_booked = ?,
                        notes = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (booking_name, booking_description, booking_date, start_time, end_time,
                      tables_booked, notes, self.booking['id']))
            else:
                # Insert new booking
                cursor.execute('''
                    INSERT INTO standalone_bookings
                    (booking_name, booking_description, booking_date, start_time, end_time,
                     tables_booked, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (booking_name, booking_description, booking_date, start_time, end_time,
                      tables_booked, notes))

            conn.commit()
            conn.close()

            self.destroy()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save booking: {str(e)}", parent=self)


class DayHoursDialog(ctk.CTkToplevel):
    """Dialog for editing operating hours for a specific day"""

    def __init__(self, parent, database, day_num: int, day_name: str):
        super().__init__(parent)
        self.db = database
        self.day_num = day_num
        self.day_name = day_name

        self.title(f"Edit Hours - {day_name}")
        self.geometry("450x400")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Get current hours
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM operating_hours WHERE day_of_week = ?', (day_num,))
        self.current_hours = cursor.fetchone()
        conn.close()

        if not self.current_hours:
            # Create default if not exists
            self.current_hours = {
                'is_open': 1,
                'open_time': '10:00:00',
                'close_time': '22:00:00'
            }

        # Main frame with scrolling
        main_frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text=f"{day_name} Hours",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(pady=(0, 20))

        # Open/Closed toggle
        self.is_open_var = ctk.IntVar(value=self.current_hours['is_open'])

        toggle_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        toggle_frame.pack(fill="x", pady=(0, 15))

        self.open_checkbox = ctk.CTkCheckBox(
            toggle_frame,
            text="Store is open on this day",
            variable=self.is_open_var,
            command=self.toggle_open_closed,
            font=ctk.CTkFont(size=14),
            text_color="#4A2D5E"
        )
        self.open_checkbox.pack(padx=15, pady=15)

        # Hours frame
        self.hours_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        self.hours_frame.pack(fill="x", pady=(0, 15))

        # Open time
        ctk.CTkLabel(
            self.hours_frame,
            text="Opening Time:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.open_time_entry = ctk.CTkEntry(
            self.hours_frame,
            font=ctk.CTkFont(size=14),
            placeholder_text="HH:MM",
            width=100
        )
        open_time = self.current_hours['open_time'].rsplit(':', 1)[0] if self.current_hours['open_time'] else '10:00'
        self.open_time_entry.insert(0, open_time)
        self.open_time_entry.pack(anchor="w", padx=15, pady=(0, 10))

        # Close time
        ctk.CTkLabel(
            self.hours_frame,
            text="Closing Time:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(5, 5))

        self.close_time_entry = ctk.CTkEntry(
            self.hours_frame,
            font=ctk.CTkFont(size=14),
            placeholder_text="HH:MM",
            width=100
        )
        close_time = self.current_hours['close_time'].rsplit(':', 1)[0] if self.current_hours['close_time'] else '22:00'
        self.close_time_entry.insert(0, close_time)
        self.close_time_entry.pack(anchor="w", padx=15, pady=(0, 15))

        # Update state based on is_open
        self.toggle_open_closed()

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(10, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_hours,
            fg_color="#8B5FBF",
            hover_color="#7A4FAF",
            text_color="white",
            width=120,
            height=35
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#999999",
            hover_color="#888888",
            text_color="white",
            width=120,
            height=35
        )
        cancel_btn.pack(side="left", padx=5)

    def toggle_open_closed(self):
        """Enable/disable time entries based on open status"""
        if self.is_open_var.get():
            self.open_time_entry.configure(state="normal")
            self.close_time_entry.configure(state="normal")
        else:
            self.open_time_entry.configure(state="disabled")
            self.close_time_entry.configure(state="disabled")

    def save_hours(self):
        """Save the hours to database"""
        from tkinter import messagebox

        try:
            is_open = self.is_open_var.get()
            open_time = None
            close_time = None

            if is_open:
                # Validate times
                open_time_str = self.open_time_entry.get().strip()
                close_time_str = self.close_time_entry.get().strip()

                if not open_time_str or not close_time_str:
                    raise ValueError("Both opening and closing times are required")

                try:
                    datetime.strptime(open_time_str, '%H:%M')
                    open_time = open_time_str + ":00"
                except ValueError:
                    raise ValueError("Opening time must be in HH:MM format")

                try:
                    datetime.strptime(close_time_str, '%H:%M')
                    close_time = close_time_str + ":00"
                except ValueError:
                    raise ValueError("Closing time must be in HH:MM format")

            # Save to database
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Check if record exists
            cursor.execute('SELECT id FROM operating_hours WHERE day_of_week = ?', (self.day_num,))
            exists = cursor.fetchone()

            if exists:
                # Update
                cursor.execute('''
                    UPDATE operating_hours
                    SET is_open = ?,
                        open_time = ?,
                        close_time = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE day_of_week = ?
                ''', (is_open, open_time, close_time, self.day_num))
            else:
                # Insert
                cursor.execute('''
                    INSERT INTO operating_hours
                    (day_of_week, is_open, open_time, close_time)
                    VALUES (?, ?, ?, ?)
                ''', (self.day_num, is_open, open_time, close_time))

            conn.commit()
            conn.close()

            self.destroy()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save hours: {str(e)}", parent=self)


class SpecialDateDialog(ctk.CTkToplevel):
    """Dialog for editing operating hours for a specific date"""

    def __init__(self, parent, database, date_param=None):
        super().__init__(parent)
        self.db = database

        # date_param can be either a date object or a dict with date_data
        # If it's a date object, we'll load any existing special date data for it
        if isinstance(date_param, datetime.date):
            self.selected_date = date_param
            self.date_data = self._get_existing_special_date(date_param)
        elif isinstance(date_param, dict):
            # Legacy support for dict format
            self.date_data = date_param
            self.selected_date = datetime.strptime(date_param['specific_date'], '%Y-%m-%d').date()
        else:
            # No date provided
            self.selected_date = None
            self.date_data = None

        self.title(f"Edit Hours - {self.selected_date.strftime('%A, %d %B %Y')}" if self.selected_date else "Add Special Date")
        self.geometry("500x550")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Get default hours for this date (day of week)
        if self.selected_date:
            self.default_hours = self._get_default_hours_for_date(self.selected_date)
        else:
            self.default_hours = None

        # Main frame with scrolling
        main_frame = ctk.CTkScrollableFrame(self, fg_color="#F5F0F6")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="Operating Hours for This Date",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(pady=(0, 10))

        # Show if using default or custom hours
        if self.selected_date:
            day_name = self.selected_date.strftime('%A')
            if self.date_data:
                status_text = f"Custom hours set for {self.selected_date.strftime('%d %B %Y')}"
                status_color = "#8B5FBF"
            else:
                status_text = f"Using default {day_name} hours"
                status_color = "#666666"

            status_label = ctk.CTkLabel(
                main_frame,
                text=status_text,
                font=ctk.CTkFont(size=12, style="italic"),
                text_color=status_color
            )
            status_label.pack(pady=(0, 20))

        # Date display (non-editable when selected_date is provided)
        date_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        date_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            date_frame,
            text="Date:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.date_entry = ctk.CTkEntry(
            date_frame,
            font=ctk.CTkFont(size=14),
            placeholder_text="YYYY-MM-DD"
        )
        if self.selected_date:
            self.date_entry.insert(0, self.selected_date.strftime('%Y-%m-%d'))
            self.date_entry.configure(state="disabled")  # Can't change date when editing
        elif self.date_data:
            self.date_entry.insert(0, self.date_data['specific_date'])
            self.date_entry.configure(state="disabled")
        self.date_entry.pack(anchor="w", padx=15, pady=(0, 15), fill="x")

        # Reason entry
        reason_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        reason_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            reason_frame,
            text="Reason/Description:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.reason_entry = ctk.CTkEntry(
            reason_frame,
            font=ctk.CTkFont(size=14),
            placeholder_text="e.g., Christmas, New Year's Day"
        )
        if self.date_data and self.date_data.get('reason'):
            self.reason_entry.insert(0, self.date_data['reason'])
        self.reason_entry.pack(anchor="w", padx=15, pady=(0, 15), fill="x")

        # Open/Closed toggle
        # Use date_data if exists, otherwise use default_hours, otherwise default to open
        if self.date_data:
            is_open_value = self.date_data['is_open']
        elif self.default_hours:
            is_open_value = self.default_hours['is_open']
        else:
            is_open_value = 1

        self.is_open_var = ctk.IntVar(value=is_open_value)

        toggle_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        toggle_frame.pack(fill="x", pady=(0, 15))

        self.open_checkbox = ctk.CTkCheckBox(
            toggle_frame,
            text="Store is open on this date",
            variable=self.is_open_var,
            command=self.toggle_open_closed,
            font=ctk.CTkFont(size=14),
            text_color="#4A2D5E"
        )
        self.open_checkbox.pack(padx=15, pady=15)

        # Hours frame
        self.hours_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=8)
        self.hours_frame.pack(fill="x", pady=(0, 15))

        # Open time
        ctk.CTkLabel(
            self.hours_frame,
            text="Opening Time:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.open_time_entry = ctk.CTkEntry(
            self.hours_frame,
            font=ctk.CTkFont(size=14),
            placeholder_text="HH:MM",
            width=100
        )
        # Use date_data if exists, otherwise use default_hours, otherwise default to 10:00
        if self.date_data and self.date_data.get('open_time'):
            open_time = self.date_data['open_time'].rsplit(':', 1)[0]
        elif self.default_hours and self.default_hours.get('open_time'):
            open_time = self.default_hours['open_time'].rsplit(':', 1)[0]
        else:
            open_time = '10:00'
        self.open_time_entry.insert(0, open_time)
        self.open_time_entry.pack(anchor="w", padx=15, pady=(0, 10))

        # Close time
        ctk.CTkLabel(
            self.hours_frame,
            text="Closing Time:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", padx=15, pady=(5, 5))

        self.close_time_entry = ctk.CTkEntry(
            self.hours_frame,
            font=ctk.CTkFont(size=14),
            placeholder_text="HH:MM",
            width=100
        )
        # Use date_data if exists, otherwise use default_hours, otherwise default to 22:00
        if self.date_data and self.date_data.get('close_time'):
            close_time = self.date_data['close_time'].rsplit(':', 1)[0]
        elif self.default_hours and self.default_hours.get('close_time'):
            close_time = self.default_hours['close_time'].rsplit(':', 1)[0]
        else:
            close_time = '22:00'
        self.close_time_entry.insert(0, close_time)
        self.close_time_entry.pack(anchor="w", padx=15, pady=(0, 15))

        # Update state based on is_open
        self.toggle_open_closed()

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=(10, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Custom Hours",
            command=self.save_special_date,
            fg_color="#8B5FBF",
            hover_color="#7A4FAF",
            text_color="white",
            width=150,
            height=35
        )
        save_btn.pack(side="left", padx=5)

        # Only show "Revert to Default" if there's custom hours set
        if self.date_data:
            revert_btn = ctk.CTkButton(
                button_frame,
                text="Revert to Default",
                command=self.revert_to_default,
                fg_color="#FF9800",
                hover_color="#F57C00",
                text_color="white",
                width=150,
                height=35
            )
            revert_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#999999",
            hover_color="#888888",
            text_color="white",
            width=120,
            height=35
        )
        cancel_btn.pack(side="left", padx=5)

    def toggle_open_closed(self):
        """Enable/disable time entries based on open status"""
        if self.is_open_var.get():
            self.open_time_entry.configure(state="normal")
            self.close_time_entry.configure(state="normal")
        else:
            self.open_time_entry.configure(state="disabled")
            self.close_time_entry.configure(state="disabled")

    def _get_existing_special_date(self, date: datetime.date) -> dict:
        """Get existing special date hours from database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM date_specific_hours
            WHERE specific_date = ?
        ''', (date.strftime('%Y-%m-%d'),))

        result = cursor.fetchone()
        conn.close()

        return dict(result) if result else None

    def _get_default_hours_for_date(self, date: datetime.date) -> dict:
        """Get default day-of-week hours for a date"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        day_of_week = date.weekday()  # 0 = Monday, 6 = Sunday
        cursor.execute('''
            SELECT is_open, open_time, close_time
            FROM operating_hours
            WHERE day_of_week = ?
        ''', (day_of_week,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return dict(result)
        else:
            # Default fallback
            return {
                'is_open': 1,
                'open_time': '10:00:00',
                'close_time': '22:00:00'
            }

    def revert_to_default(self):
        """Delete custom hours and revert to default day-of-week hours"""
        from tkinter import messagebox

        result = messagebox.askyesno(
            "Revert to Default",
            "This will remove the custom hours for this date and use the default hours.\n\nAre you sure?",
            parent=self
        )

        if result:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM date_specific_hours WHERE id = ?', (self.date_data['id'],))
            conn.commit()
            conn.close()
            self.destroy()

    def save_special_date(self):
        """Save the special date to database"""
        from tkinter import messagebox

        try:
            # Get date
            if self.selected_date:
                specific_date = self.selected_date.strftime('%Y-%m-%d')
            elif self.date_data:
                specific_date = self.date_data['specific_date']
            else:
                specific_date = self.date_entry.get().strip()
                if not specific_date:
                    raise ValueError("Date is required")

                # Validate date format
                try:
                    datetime.strptime(specific_date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError("Date must be in YYYY-MM-DD format")

            # Get reason
            reason = self.reason_entry.get().strip() or None

            # Get open/close status and times
            is_open = self.is_open_var.get()
            open_time = None
            close_time = None

            if is_open:
                # Validate times
                open_time_str = self.open_time_entry.get().strip()
                close_time_str = self.close_time_entry.get().strip()

                if not open_time_str or not close_time_str:
                    raise ValueError("Both opening and closing times are required")

                try:
                    datetime.strptime(open_time_str, '%H:%M')
                    open_time = open_time_str + ":00"
                except ValueError:
                    raise ValueError("Opening time must be in HH:MM format")

                try:
                    datetime.strptime(close_time_str, '%H:%M')
                    close_time = close_time_str + ":00"
                except ValueError:
                    raise ValueError("Closing time must be in HH:MM format")

            # Save to database
            conn = self.db.get_connection()
            cursor = conn.cursor()

            if self.date_data:
                # Update existing
                cursor.execute('''
                    UPDATE date_specific_hours
                    SET is_open = ?,
                        open_time = ?,
                        close_time = ?,
                        reason = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (is_open, open_time, close_time, reason, self.date_data['id']))
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO date_specific_hours
                    (specific_date, is_open, open_time, close_time, reason)
                    VALUES (?, ?, ?, ?, ?)
                ''', (specific_date, is_open, open_time, close_time, reason))

            conn.commit()
            conn.close()

            self.destroy()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save special date: {str(e)}", parent=self)
