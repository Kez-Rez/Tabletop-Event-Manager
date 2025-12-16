"""Feature Requests View - Manage feature ideas and suggestions"""
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

class FeatureRequestsView(ctk.CTkFrame):
    """View for managing feature requests and ideas"""

    def __init__(self, parent, database, **kwargs):
        super().__init__(parent, **kwargs)
        self.db = database

        # Title
        title = ctk.CTkLabel(
            self,
            text="Feature Requests & Ideas",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(pady=30, padx=30, anchor="w")

        # Description
        desc = ctk.CTkLabel(
            self,
            text="Track feature ideas and improvements you'd like to see in future updates",
            font=ctk.CTkFont(size=15),
            text_color="#666666"
        )
        desc.pack(pady=(0, 20), padx=30, anchor="w")

        # Buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(0, 20))

        self.btn_add = ctk.CTkButton(
            button_frame,
            text="+ Add New Request",
            command=self.add_request,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.btn_add.pack(side="left", padx=(0, 10))

        self.btn_refresh = ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=self.load_requests,
            fg_color="#D4A5D4",
            hover_color="#C494C4",
            text_color="#4A2D5E",
            width=100
        )
        self.btn_refresh.pack(side="left")

        # Filter frame
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=30, pady=(0, 10))

        ctk.CTkLabel(
            filter_frame,
            text="Filter by Status:",
            font=ctk.CTkFont(size=15),
            text_color="#4A2D5E"
        ).pack(side="left", padx=(0, 10))

        self.status_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Submitted", "Under Review", "Planned", "In Progress", "Completed", "Declined"],
            command=lambda _: self.load_requests(),
            fg_color="#C5A8D9",
            button_color="#B491CC",
            button_hover_color="#A380BB",
            text_color="#4A2D5E"
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(
            filter_frame,
            text="Filter by Priority:",
            font=ctk.CTkFont(size=15),
            text_color="#4A2D5E"
        ).pack(side="left", padx=(0, 10))

        self.priority_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Low", "Medium", "High"],
            command=lambda _: self.load_requests(),
            fg_color="#C5A8D9",
            button_color="#B491CC",
            button_hover_color="#A380BB",
            text_color="#4A2D5E"
        )
        self.priority_filter.set("All")
        self.priority_filter.pack(side="left")

        # Scrollable frame for requests
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="white")
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Load requests
        self.load_requests()

    def load_requests(self):
        """Load and display all feature requests"""
        # Clear existing items
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Build query with filters
        query = "SELECT * FROM feature_requests WHERE 1=1"
        params = []

        status_filter = self.status_filter.get()
        if status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)

        priority_filter = self.priority_filter.get()
        if priority_filter != "All":
            query += " AND priority = ?"
            params.append(priority_filter)

        query += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END, submitted_date DESC"

        cursor.execute(query, params)
        requests = cursor.fetchall()
        conn.close()

        if not requests:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No feature requests found.\nClick 'Add New Request' to create one!",
                font=ctk.CTkFont(size=15),
                text_color="#999999"
            ).pack(pady=40)
            return

        for req in requests:
            self.create_request_card(dict(req))

    def create_request_card(self, request):
        """Create a card for displaying a request"""
        # Determine colors based on priority and status
        if request['priority'] == 'High':
            border_color = "#E57373"
            priority_bg = "#FFEBEE"
        elif request['priority'] == 'Medium':
            border_color = "#FFB74D"
            priority_bg = "#FFF3E0"
        else:
            border_color = "#81C784"
            priority_bg = "#E8F5E9"

        if request['status'] == 'Completed':
            border_color = "#81C784"
        elif request['status'] == 'Declined':
            border_color = "#9E9E9E"

        # Card frame
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="white",
            border_width=2,
            border_color=border_color
        )
        card.pack(fill="x", padx=10, pady=8)

        # Header frame
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        # Title
        ctk.CTkLabel(
            header,
            text=request['title'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF",
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # Priority badge
        priority_badge = ctk.CTkLabel(
            header,
            text=request['priority'],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#4A2D5E",
            fg_color=priority_bg,
            corner_radius=5,
            padx=10,
            pady=3
        )
        priority_badge.pack(side="right", padx=(10, 0))

        # Status badge
        status_colors = {
            'Submitted': '#E3F2FD',
            'Under Review': '#FFF9C4',
            'Planned': '#F3E5F5',
            'In Progress': '#E1F5FE',
            'Completed': '#E8F5E9',
            'Declined': '#F5F5F5'
        }
        status_badge = ctk.CTkLabel(
            header,
            text=request['status'],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#4A2D5E",
            fg_color=status_colors.get(request['status'], '#F5F5F5'),
            corner_radius=5,
            padx=10,
            pady=3
        )
        status_badge.pack(side="right")

        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=request['description'],
            font=ctk.CTkFont(size=15),
            text_color="#4A2D5E",
            anchor="w",
            justify="left",
            wraplength=1000
        )
        desc_label.pack(fill="x", padx=20, pady=(5, 10), anchor="w")

        # Footer with metadata
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(5, 15))

        # Submitted by and date
        submitted_date = datetime.strptime(request['submitted_date'], '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y')
        meta_text = f"Submitted by: {request['submitted_by'] or 'Unknown'} | {submitted_date}"

        ctk.CTkLabel(
            footer,
            text=meta_text,
            font=ctk.CTkFont(size=15),
            text_color="#999999",
            anchor="w"
        ).pack(side="left")

        # Action buttons
        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="Edit",
            command=lambda: self.edit_request(request),
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=70,
            height=28,
            font=ctk.CTkFont(size=15)
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=lambda: self.delete_request(request),
            fg_color="#E57373",
            hover_color="#D76C6C",
            text_color="white",
            width=70,
            height=28,
            font=ctk.CTkFont(size=15)
        ).pack(side="left")

    def add_request(self):
        """Open dialog to add a new request"""
        dialog = RequestDialog(self, self.db, title="Add Feature Request")
        self.wait_window(dialog)
        self.load_requests()

    def edit_request(self, request):
        """Open dialog to edit a request"""
        dialog = RequestDialog(self, self.db, request=request, title="Edit Feature Request")
        self.wait_window(dialog)
        self.load_requests()

    def delete_request(self, request):
        """Delete a feature request"""
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this feature request?\n\n{request['title']}"
        ):
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feature_requests WHERE id = ?", (request['id'],))
            conn.commit()
            conn.close()
            self.load_requests()


class RequestDialog(ctk.CTkToplevel):
    """Dialog for adding/editing feature requests"""

    def __init__(self, parent, database, request=None, **kwargs):
        # Extract title before calling super().__init__
        dialog_title = kwargs.pop('title', 'Feature Request')
        super().__init__(parent, **kwargs)
        self.db = database
        self.request = request

        self.title(dialog_title)
        self.geometry("600x650")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="#F5F0F6")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(
            main_frame,
            text="Title",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", pady=(10, 5))

        self.title_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Brief title for the feature request",
            height=35,
            font=ctk.CTkFont(size=15)
        )
        self.title_entry.pack(fill="x", pady=(0, 15))

        # Description
        ctk.CTkLabel(
            main_frame,
            text="Description",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", pady=(0, 5))

        self.desc_text = ctk.CTkTextbox(
            main_frame,
            height=250,
            font=ctk.CTkFont(size=15)
        )
        self.desc_text.pack(fill="both", expand=True, pady=(0, 15))

        # Priority
        ctk.CTkLabel(
            main_frame,
            text="Priority",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", pady=(0, 5))

        self.priority_menu = ctk.CTkOptionMenu(
            main_frame,
            values=["Low", "Medium", "High"],
            fg_color="#C5A8D9",
            button_color="#B491CC",
            button_hover_color="#A380BB"
        )
        self.priority_menu.set("Medium")
        self.priority_menu.pack(fill="x", pady=(0, 15))

        # Status (only when editing)
        if request:
            ctk.CTkLabel(
                main_frame,
                text="Status",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color="#4A2D5E"
            ).pack(anchor="w", pady=(0, 5))

            self.status_menu = ctk.CTkOptionMenu(
                main_frame,
                values=["Submitted", "Under Review", "Planned", "In Progress", "Completed", "Declined"],
                fg_color="#C5A8D9",
                button_color="#B491CC",
                button_hover_color="#A380BB"
            )
            self.status_menu.set("Submitted")
            self.status_menu.pack(fill="x", pady=(0, 15))

        # Submitted by
        ctk.CTkLabel(
            main_frame,
            text="Submitted By (optional)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#4A2D5E"
        ).pack(anchor="w", pady=(0, 5))

        self.submitter_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Your name",
            height=35,
            font=ctk.CTkFont(size=15)
        )
        self.submitter_entry.pack(fill="x", pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#9E9E9E",
            hover_color="#8E8E8E",
            text_color="white",
            width=120
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save,
            fg_color="#C5A8D9",
            hover_color="#B491CC",
            text_color="#4A2D5E",
            width=120
        ).pack(side="right")

        # Load data if editing
        if request:
            self.load_data()

    def load_data(self):
        """Load existing request data into form"""
        self.title_entry.insert(0, self.request['title'])
        self.desc_text.insert("1.0", self.request['description'])
        self.priority_menu.set(self.request['priority'])
        if hasattr(self, 'status_menu'):
            self.status_menu.set(self.request['status'])
        if self.request['submitted_by']:
            self.submitter_entry.insert(0, self.request['submitted_by'])

    def save(self):
        """Save the feature request"""
        title = self.title_entry.get().strip()
        description = self.desc_text.get("1.0", "end-1c").strip()
        priority = self.priority_menu.get()
        status = self.status_menu.get() if hasattr(self, 'status_menu') else "Submitted"
        submitter = self.submitter_entry.get().strip() or None

        if not title:
            messagebox.showerror("Validation Error", "Please enter a title", parent=self)
            return

        if not description:
            messagebox.showerror("Validation Error", "Please enter a description", parent=self)
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()

        if self.request:
            # Update existing request
            cursor.execute('''
                UPDATE feature_requests
                SET title = ?, description = ?, priority = ?, status = ?,
                    submitted_by = ?, updated_at = ?
                WHERE id = ?
            ''', (title, description, priority, status, submitter, datetime.now(), self.request['id']))
        else:
            # Insert new request
            cursor.execute('''
                INSERT INTO feature_requests (title, description, priority, status, submitted_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description, priority, status, submitter))

        conn.commit()
        conn.close()

        self.destroy()
