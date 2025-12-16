"""Analysis View - Post-event analysis and insights"""
import customtkinter as ctk
from datetime import datetime, timedelta
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

class AnalysisView(ctk.CTkFrame):
    """View for post-event analysis and metrics"""

    def __init__(self, parent, database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = database

        # Title
        title = ctk.CTkLabel(
            self,
            text="Post-Event Analysis",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(pady=30, padx=30, anchor="w")

        # Period selector frame
        period_frame = ctk.CTkFrame(self, fg_color="transparent")
        period_frame.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkLabel(
            period_frame,
            text="Analysis Period:",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E"
        ).pack(side="left", padx=(0, 10))

        self.period_var = ctk.StringVar(value="Last 30 Days")
        periods = ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "All Time"]

        self.period_menu = ctk.CTkOptionMenu(
            period_frame,
            variable=self.period_var,
            values=periods,
            command=lambda _: self.refresh_analysis(),
            fg_color="#C5A8D9",
            button_color="#B491CC",
            button_hover_color="#A380BB",
            text_color="#4A2D5E",
            width=150
        )
        self.period_menu.pack(side="left")

        # Refresh button
        ctk.CTkButton(
            period_frame,
            text="Refresh",
            command=self.refresh_analysis,
            fg_color="#D4A5D4",
            hover_color="#C494C4",
            text_color="#4A2D5E",
            width=100
        ).pack(side="left", padx=(20, 0))

        # Scrollable content frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="white")
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Load analysis
        self.refresh_analysis()

    def get_date_range(self) -> Optional[str]:
        """Get SQL date filter based on selected period"""
        period = self.period_var.get()

        if period == "All Time":
            return None

        days_map = {
            "Last 7 Days": 7,
            "Last 30 Days": 30,
            "Last 90 Days": 90,
            "Last 6 Months": 180,
            "Last Year": 365
        }

        days = days_map.get(period, 30)
        date_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return f"event_date >= '{date_threshold}'"

    def refresh_analysis(self):
        """Refresh all analysis data"""
        # Clear existing widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        date_filter = self.get_date_range()
        where_clause = f"WHERE {date_filter}" if date_filter else ""
        where_completed = f"WHERE is_completed = 1 AND {date_filter}" if date_filter else "WHERE is_completed = 1"

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Check if we have any completed events
        cursor.execute(f"SELECT COUNT(*) as count FROM events {where_completed}")
        completed_count = cursor.fetchone()['count']

        if completed_count == 0:
            ctk.CTkLabel(
                self.scroll_frame,
                text=f"No completed events found for {self.period_var.get()}.\n\nMark events as completed to see analysis here.",
                font=ctk.CTkFont(size=15),
                text_color="#999999"
            ).pack(pady=40)
            conn.close()
            return

        # === TREND GRAPHS ===
        self.create_section_header("Trends Over Time")
        self.create_trend_graphs(cursor, where_completed)

        # === KEY PERFORMANCE INDICATORS ===
        self.create_section_header("Key Performance Indicators")

        # Get KPI data
        cursor.execute(f'''
            SELECT
                COUNT(*) as total_events,
                SUM(CASE WHEN is_cancelled = 1 THEN 1 ELSE 0 END) as cancelled_events
            FROM events
            {where_clause}
        ''')
        event_stats = dict(cursor.fetchone())

        cursor.execute(f'''
            SELECT
                COALESCE(SUM(actual_attendance), 0) as total_attendance,
                COALESCE(AVG(actual_attendance), 0) as avg_attendance,
                COALESCE(SUM(revenue_total), 0) as total_revenue,
                COALESCE(AVG(revenue_total), 0) as avg_revenue,
                COALESCE(SUM(cost_total), 0) as total_costs,
                COALESCE(SUM(profit_margin), 0) as total_profit,
                COALESCE(AVG(attendee_satisfaction), 0) as avg_satisfaction,
                COALESCE(AVG(event_smoothness), 0) as avg_smoothness,
                COALESCE(AVG(overall_success_score), 0) as avg_overall_success
            FROM event_analysis ea
            JOIN events e ON ea.event_id = e.id
            {where_completed}
        ''')
        kpi_data = dict(cursor.fetchone())

        # Calculate averages
        avg_revenue_per_attendee = 0
        if kpi_data['total_attendance'] > 0:
            avg_revenue_per_attendee = kpi_data['total_revenue'] / kpi_data['total_attendance']

        # Display KPIs in grid
        kpi_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=10, pady=(0, 20))

        kpis = [
            ("Total Events", f"{event_stats['total_events']}", "#E3F2FD"),
            ("Completed Events", f"{completed_count}", "#E8F5E9"),
            ("Cancelled Events", f"{event_stats['cancelled_events']}", "#FFEBEE"),
            ("Total Attendees", f"{int(kpi_data['total_attendance'])}", "#F3E5F5"),
            ("Avg Attendees/Event", f"{kpi_data['avg_attendance']:.1f}", "#FFF9C4"),
            ("Total Revenue", f"${kpi_data['total_revenue']:.2f}", "#E8F5E9"),
            ("Total Costs", f"${kpi_data['total_costs']:.2f}", "#FFEBEE"),
            ("Total Profit", f"${kpi_data['total_profit']:.2f}", "#E3F2FD"),
            ("Avg Revenue/Event", f"${kpi_data['avg_revenue']:.2f}", "#F3E5F5"),
            ("Avg Revenue/Attendee", f"${avg_revenue_per_attendee:.2f}", "#FFF9C4"),
            ("Avg Attendee Satisfaction", f"{kpi_data['avg_satisfaction']:.1f}/10", "#E1F5FE"),
            ("Avg Event Smoothness", f"{kpi_data['avg_smoothness']:.1f}/10", "#F3E5F5"),
            ("Avg Overall Success Score", f"{kpi_data['avg_overall_success']:.1f}/10", "#C8E6C9"),
            ("Cancellation Rate", f"{(event_stats['cancelled_events']/max(event_stats['total_events'], 1)*100):.1f}%", "#FFEBEE")
        ]

        for i, (label, value, color) in enumerate(kpis):
            col = i % 3
            row = i // 3

            kpi_card = ctk.CTkFrame(kpi_frame, fg_color=color, corner_radius=8)
            kpi_card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            ctk.CTkLabel(
                kpi_card,
                text=value,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#4A2D5E"
            ).pack(pady=(15, 5))

            ctk.CTkLabel(
                kpi_card,
                text=label,
                font=ctk.CTkFont(size=15),
                text_color="#666666"
            ).pack(pady=(0, 15))

        # Configure grid columns to be equal width
        for col in range(3):
            kpi_frame.grid_columnconfigure(col, weight=1, uniform="kpi")

        # === EVENT TYPE PERFORMANCE ===
        self.create_section_header("Performance by Event Type")

        cursor.execute(f'''
            SELECT
                et.name as event_type,
                COUNT(DISTINCT e.id) as event_count,
                COALESCE(SUM(ea.actual_attendance), 0) as total_attendance,
                COALESCE(AVG(ea.actual_attendance), 0) as avg_attendance,
                COALESCE(SUM(ea.revenue_total), 0) as total_revenue,
                COALESCE(AVG(ea.revenue_total), 0) as avg_revenue,
                COALESCE(AVG(ea.attendee_satisfaction), 0) as avg_rating
            FROM events e
            LEFT JOIN event_types et ON e.event_type_id = et.id
            LEFT JOIN event_analysis ea ON e.id = ea.event_id
            {where_completed}
            GROUP BY et.name
            ORDER BY total_revenue DESC
        ''')
        type_performance = cursor.fetchall()

        if type_performance:
            self.create_data_table(
                ["Event Type", "Events", "Total Attendees", "Avg Attendees", "Total Revenue", "Avg Revenue", "Avg Satisfaction"],
                [
                    [
                        row['event_type'] or 'Unknown',
                        str(row['event_count']),
                        str(int(row['total_attendance'])),
                        f"{row['avg_attendance']:.1f}",
                        f"${row['total_revenue']:.2f}",
                        f"${row['avg_revenue']:.2f}",
                        f"{row['avg_rating']:.1f}/10"
                    ]
                    for row in type_performance
                ]
            )
        else:
            self.create_empty_message("No event type data available")

        # === CAPACITY UTILIZATION ===
        self.create_section_header("Capacity Utilization")

        cursor.execute(f'''
            SELECT
                e.event_name,
                e.event_date,
                COALESCE(SUM(tt.quantity_available), 0) as tickets_available,
                ea.actual_attendance,
                CASE
                    WHEN COALESCE(SUM(tt.quantity_available), 0) > 0
                    THEN (ea.actual_attendance * 100.0 / SUM(tt.quantity_available))
                    ELSE 0
                END as utilization_percent
            FROM events e
            JOIN event_analysis ea ON e.id = ea.event_id
            LEFT JOIN ticket_tiers tt ON e.id = tt.event_id
            {where_completed}
            GROUP BY e.id, e.event_name, e.event_date, ea.actual_attendance
            ORDER BY utilization_percent DESC
            LIMIT 10
        ''')
        capacity_data = cursor.fetchall()

        if capacity_data:
            self.create_data_table(
                ["Event Name", "Date", "Tickets Available", "Attendance", "Utilization"],
                [
                    [
                        row['event_name'],
                        datetime.strptime(row['event_date'], '%Y-%m-%d').strftime('%d %b %Y'),
                        str(row['tickets_available'] or 0),
                        str(row['actual_attendance'] or 0),
                        f"{row['utilization_percent']:.1f}%" if row['utilization_percent'] is not None else 'N/A'
                    ]
                    for row in capacity_data
                ]
            )
        else:
            self.create_empty_message("No capacity data available")

        # === TOP PERFORMING EVENTS ===
        self.create_section_header("Top 10 Events by Revenue")

        cursor.execute(f'''
            SELECT
                e.event_name,
                e.event_date,
                et.name as event_type,
                ea.actual_attendance,
                ea.revenue_total,
                ea.profit_margin,
                ea.attendee_satisfaction as satisfaction,
                ea.event_smoothness,
                ea.overall_success_score
            FROM events e
            LEFT JOIN event_types et ON e.event_type_id = et.id
            JOIN event_analysis ea ON e.id = ea.event_id
            {where_completed}
            ORDER BY ea.revenue_total DESC
            LIMIT 10
        ''')
        top_events = cursor.fetchall()

        if top_events:
            self.create_data_table(
                ["Event Name", "Date", "Type", "Attendance", "Revenue", "Profit", "Satisfaction", "Smoothness", "Success Score"],
                [
                    [
                        row['event_name'],
                        datetime.strptime(row['event_date'], '%Y-%m-%d').strftime('%d %b %Y'),
                        row['event_type'] or 'Unknown',
                        str(row['actual_attendance'] or 0),
                        f"${row['revenue_total']:.2f}" if row['revenue_total'] is not None else '$0.00',
                        f"${row['profit_margin']:.2f}" if row['profit_margin'] is not None else '$0.00',
                        f"{row['satisfaction']:.1f}/10" if row['satisfaction'] else 'N/A',
                        f"{row['event_smoothness']:.1f}/10" if row['event_smoothness'] is not None else 'N/A',
                        f"{row['overall_success_score']:.1f}/10" if row['overall_success_score'] is not None else 'N/A'
                    ]
                    for row in top_events
                ]
            )
        else:
            self.create_empty_message("No event data available")

        # === COST BREAKDOWN ===
        self.create_section_header("Cost Analysis by Category")

        cursor.execute(f'''
            SELECT
                cc.name as category,
                COUNT(ec.id) as count,
                SUM(ec.amount) as total_cost,
                AVG(ec.amount) as avg_cost
            FROM event_costs ec
            JOIN cost_categories cc ON ec.category_id = cc.id
            JOIN events e ON ec.event_id = e.id
            {where_completed}
            GROUP BY cc.name
            ORDER BY total_cost DESC
        ''')
        cost_breakdown = cursor.fetchall()

        if cost_breakdown:
            self.create_data_table(
                ["Cost Category", "Number of Costs", "Total Cost", "Average Cost"],
                [
                    [
                        row['category'],
                        str(row['count']),
                        f"${row['total_cost']:.2f}" if row['total_cost'] is not None else '$0.00',
                        f"${row['avg_cost']:.2f}" if row['avg_cost'] is not None else '$0.00'
                    ]
                    for row in cost_breakdown
                ]
            )
        else:
            self.create_empty_message("No cost data available")

        # === TICKET TIER ANALYSIS ===
        self.create_section_header("Ticket Tier Performance")

        cursor.execute(f'''
            SELECT
                tt.tier_name,
                COUNT(DISTINCT tt.event_id) as events_used,
                SUM(tt.quantity_sold) as total_sold,
                AVG(tt.price) as avg_price,
                SUM(tt.quantity_sold * tt.price) as total_revenue,
                AVG(tt.quantity_sold * 100.0 / NULLIF(tt.quantity_available, 0)) as avg_sell_through
            FROM ticket_tiers tt
            JOIN events e ON tt.event_id = e.id
            {where_completed}
            GROUP BY tt.tier_name
            ORDER BY total_revenue DESC
        ''')
        ticket_performance = cursor.fetchall()

        if ticket_performance:
            self.create_data_table(
                ["Tier Name", "Events Used", "Total Sold", "Avg Price", "Revenue", "Avg Sell-Through"],
                [
                    [
                        row['tier_name'],
                        str(row['events_used']),
                        str(row['total_sold'] or 0),
                        f"${row['avg_price']:.2f}" if row['avg_price'] is not None else '$0.00',
                        f"${row['total_revenue']:.2f}" if row['total_revenue'] is not None else '$0.00',
                        f"{row['avg_sell_through']:.1f}%" if row['avg_sell_through'] else 'N/A'
                    ]
                    for row in ticket_performance
                ]
            )
        else:
            self.create_empty_message("No ticket data available")

        # === CANCELLED EVENTS ===
        cursor.execute(f'''
            SELECT COUNT(*) as cancelled_count
            FROM events
            WHERE is_cancelled = 1 {f'AND {date_filter}' if date_filter else ''}
        ''')
        if cursor.fetchone()['cancelled_count'] > 0:
            self.create_section_header("Cancelled Events")

            cursor.execute(f'''
                SELECT
                    e.event_name,
                    e.event_date,
                    et.name as event_type,
                    e.cancelled_date,
                    e.cancellation_reason
                FROM events e
                LEFT JOIN event_types et ON e.event_type_id = et.id
                WHERE e.is_cancelled = 1 {f'AND {date_filter}' if date_filter else ''}
                ORDER BY e.cancelled_date DESC
            ''')
            cancelled_events = cursor.fetchall()

            self.create_data_table(
                ["Event Name", "Scheduled Date", "Type", "Cancelled Date", "Reason"],
                [
                    [
                        row['event_name'],
                        datetime.strptime(row['event_date'], '%Y-%m-%d').strftime('%d %b %Y'),
                        row['event_type'] or 'Unknown',
                        datetime.strptime(row['cancelled_date'], '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y') if row['cancelled_date'] else 'N/A',
                        row['cancellation_reason'] or 'No reason given'
                    ]
                    for row in cancelled_events
                ]
            )

        conn.close()

    def create_trend_graphs(self, cursor, where_completed):
        """Create trend graphs for attendance, revenue, and satisfaction"""
        # Get time series data
        cursor.execute(f'''
            SELECT
                e.event_date,
                e.event_name,
                ea.actual_attendance,
                ea.revenue_total,
                ea.attendee_satisfaction as satisfaction,
                ea.event_smoothness,
                ea.overall_success_score
            FROM events e
            JOIN event_analysis ea ON e.id = ea.event_id
            {where_completed}
            ORDER BY e.event_date ASC
        ''')

        time_series_data = cursor.fetchall()

        if not time_series_data or len(time_series_data) < 2:
            ctk.CTkLabel(
                self.scroll_frame,
                text="Not enough data points to display trends (need at least 2 completed events)",
                font=ctk.CTkFont(size=15),
                text_color="#999999"
            ).pack(pady=10, padx=10)
            return

        # Parse data
        dates = []
        attendances = []
        revenues = []
        satisfactions = []
        smoothness_ratings = []
        success_scores = []

        for row in time_series_data:
            date = datetime.strptime(row['event_date'], '%Y-%m-%d')
            dates.append(date)
            attendances.append(row['actual_attendance'] if row['actual_attendance'] is not None else 0)
            revenues.append(row['revenue_total'] if row['revenue_total'] is not None else 0)
            satisfactions.append(row['satisfaction'] if row['satisfaction'] is not None else 0)
            smoothness_ratings.append(row['event_smoothness'] if row['event_smoothness'] is not None else 0)
            success_scores.append(row['overall_success_score'] if row['overall_success_score'] is not None else 0)

        # Create matplotlib figure with five subplots
        plt.style.use('default')
        fig = Figure(figsize=(12, 14), facecolor='#F9F9F9')

        # Configure colors matching the app theme
        line_colors = ['#8B5FBF', '#C5A8D9', '#4A2D5E', '#81C784', '#4CAF50']

        # Attendance graph
        ax1 = fig.add_subplot(5, 1, 1)
        ax1.plot(dates, attendances, marker='o', linewidth=2, markersize=8, color=line_colors[0], label='Attendance')
        ax1.set_ylabel('Attendees', fontsize=11, fontweight='bold', color='#4A2D5E')
        ax1.set_title('Attendance Over Time', fontsize=13, fontweight='bold', color='#8B5FBF', pad=10)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_facecolor('white')
        ax1.tick_params(colors='#4A2D5E')

        # Format x-axis dates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
        fig.autofmt_xdate(rotation=45)

        # Revenue graph
        ax2 = fig.add_subplot(5, 1, 2)
        ax2.plot(dates, revenues, marker='s', linewidth=2, markersize=8, color=line_colors[1], label='Revenue')
        ax2.set_ylabel('Revenue ($)', fontsize=11, fontweight='bold', color='#4A2D5E')
        ax2.set_title('Ticket Revenue Over Time', fontsize=13, fontweight='bold', color='#8B5FBF', pad=10)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_facecolor('white')
        ax2.tick_params(colors='#4A2D5E')
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))

        # Satisfaction graph
        ax3 = fig.add_subplot(5, 1, 3)
        ax3.plot(dates, satisfactions, marker='^', linewidth=2, markersize=8, color=line_colors[2], label='Satisfaction')
        ax3.set_ylabel('Satisfaction (0-10)', fontsize=11, fontweight='bold', color='#4A2D5E')
        ax3.set_title('Attendee Satisfaction Over Time', fontsize=13, fontweight='bold', color='#8B5FBF', pad=10)
        ax3.grid(True, alpha=0.3, linestyle='--')
        ax3.set_facecolor('white')
        ax3.set_ylim(0, 10)
        ax3.tick_params(colors='#4A2D5E')
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))

        # Event Smoothness graph
        ax4 = fig.add_subplot(5, 1, 4)
        ax4.plot(dates, smoothness_ratings, marker='D', linewidth=2, markersize=8, color=line_colors[3], label='Smoothness')
        ax4.set_ylabel('Smoothness (0-10)', fontsize=11, fontweight='bold', color='#4A2D5E')
        ax4.set_title('Event Smoothness Over Time', fontsize=13, fontweight='bold', color='#8B5FBF', pad=10)
        ax4.grid(True, alpha=0.3, linestyle='--')
        ax4.set_facecolor('white')
        ax4.set_ylim(0, 10)
        ax4.tick_params(colors='#4A2D5E')
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))

        # Overall Success Score graph
        ax5 = fig.add_subplot(5, 1, 5)
        ax5.plot(dates, success_scores, marker='*', linewidth=2, markersize=10, color=line_colors[4], label='Success Score')
        ax5.set_ylabel('Success Score (0-10)', fontsize=11, fontweight='bold', color='#4A2D5E')
        ax5.set_xlabel('Event Date', fontsize=11, fontweight='bold', color='#4A2D5E')
        ax5.set_title('Overall Event Success Score Over Time', fontsize=13, fontweight='bold', color='#8B5FBF', pad=10)
        ax5.grid(True, alpha=0.3, linestyle='--')
        ax5.set_facecolor('white')
        ax5.set_ylim(0, 10)
        ax5.tick_params(colors='#4A2D5E')
        ax5.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))

        fig.tight_layout(pad=2.0)

        # Embed in tkinter
        canvas_frame = ctk.CTkFrame(self.scroll_frame, fg_color="white", corner_radius=8)
        canvas_frame.pack(fill="both", expand=False, padx=10, pady=(0, 20))

        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def create_section_header(self, text):
        """Create a section header"""
        header = ctk.CTkLabel(
            self.scroll_frame,
            text=text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8B5FBF",
            anchor="w"
        )
        header.pack(fill="x", padx=10, pady=(20, 10))

        # Divider
        divider = ctk.CTkFrame(self.scroll_frame, height=2, fg_color="#E6D9F2")
        divider.pack(fill="x", padx=10, pady=(0, 10))

    def create_data_table(self, headers, rows):
        """Create a data table"""
        table_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#F9F9F9", corner_radius=8)
        table_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Header row
        header_frame = ctk.CTkFrame(table_frame, fg_color="#E6D9F2", corner_radius=0)
        header_frame.pack(fill="x", padx=2, pady=2)

        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#4A2D5E",
                anchor="w",
                padx=10,
                wraplength=200
            )
            label.grid(row=0, column=i, sticky="ew", padx=5, pady=8)
            header_frame.grid_columnconfigure(i, weight=1)

        # Data rows
        for row_idx, row_data in enumerate(rows):
            row_color = "white" if row_idx % 2 == 0 else "#F5F5F5"
            row_frame = ctk.CTkFrame(table_frame, fg_color=row_color, corner_radius=0)
            row_frame.pack(fill="x", padx=2, pady=1)

            for col_idx, cell_data in enumerate(row_data):
                cell = ctk.CTkLabel(
                    row_frame,
                    text=cell_data,
                    font=ctk.CTkFont(size=15),
                    text_color="#4A2D5E",
                    anchor="w",
                    padx=10,
                    wraplength=200
                )
                cell.grid(row=0, column=col_idx, sticky="ew", padx=5, pady=6)
                row_frame.grid_columnconfigure(col_idx, weight=1)

    def create_empty_message(self, message):
        """Create an empty state message"""
        ctk.CTkLabel(
            self.scroll_frame,
            text=message,
            font=ctk.CTkFont(size=15),
            text_color="#999999"
        ).pack(pady=10, padx=10)
