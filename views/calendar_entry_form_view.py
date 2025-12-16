"""Calendar entry creation/editing form as an in-window view"""
import customtkinter as ctk
from tkinter import messagebox
from utils.navigation import NavigableView


class CalendarEntryFormView(NavigableView):
    """Form view for creating or editing calendar entries"""

    def __init__(self, parent, navigation_manager, context=None):
        super().__init__(parent, navigation_manager, context)

        self.db = context.get('db')
        self.date = context.get('date')
        self.entry_data = context.get('entry_data')  # None for new entry

        self.create_ui()

    def create_ui(self):
        """Create the form UI"""
        # Header with back button
        title = "Edit Calendar Entry" if self.entry_data else "New Calendar Entry"
        self.create_header_with_back(title)

        # Main content
        content_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        form_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=40, pady=40)

        # Date display
        ctk.CTkLabel(
            form_container,
            text=f"Date: {self.date.strftime('%d %B %Y')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8B5FBF"
        ).pack(pady=(0, 20))

        # Title
        ctk.CTkLabel(
            form_container,
            text="Title *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.title_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="e.g., Australia Day",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.title_entry.pack(fill="x", pady=(0, 20))

        # Description
        ctk.CTkLabel(
            form_container,
            text="Description (optional)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.desc_textbox = ctk.CTkTextbox(
            form_container,
            height=100,
            font=ctk.CTkFont(size=14)
        )
        self.desc_textbox.pack(fill="x", pady=(0, 20))

        # Type
        ctk.CTkLabel(
            form_container,
            text="Type *",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4A2D5E",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        self.type_var = ctk.StringVar(value="misc")

        type_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        type_frame.pack(anchor="w", pady=(0, 10))

        ctk.CTkRadioButton(
            type_frame,
            text="Public Holiday (Grey)",
            variable=self.type_var,
            value="public_holiday",
            command=self.update_color_preview,
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 20))

        ctk.CTkRadioButton(
            type_frame,
            text="Miscellaneous (Yellow)",
            variable=self.type_var,
            value="misc",
            command=self.update_color_preview,
            font=ctk.CTkFont(size=13)
        ).pack(side="left")

        # Color preview
        self.color_preview = ctk.CTkFrame(
            form_container,
            width=400,
            height=40,
            corner_radius=5
        )
        self.color_preview.pack(pady=(10, 30))

        # Populate if editing
        if self.entry_data:
            self.populate_form()

        self.update_color_preview()

        # Action Buttons
        button_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        # Save Button
        btn_save = ctk.CTkButton(
            button_frame,
            text="Save Entry",
            command=self.save_entry,
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

    def update_color_preview(self):
        """Update color preview based on type"""
        color_map = {
            'public_holiday': '#E0E0E0',  # Grey
            'misc': '#FFF59D'  # Yellow
        }
        color = color_map.get(self.type_var.get(), '#FFF59D')
        self.color_preview.configure(fg_color=color)

    def populate_form(self):
        """Populate form with existing entry data"""
        if not self.entry_data:
            return

        self.title_entry.insert(0, self.entry_data['title'])

        if self.entry_data.get('description'):
            self.desc_textbox.insert("1.0", self.entry_data['description'])

        self.type_var.set(self.entry_data['entry_type'])

    def save_entry(self):
        """Validate and save the calendar entry"""
        # Get form data
        title = self.title_entry.get().strip()
        description = self.desc_textbox.get("1.0", "end-1c").strip() or None
        entry_type = self.type_var.get()

        # Validation
        if not title:
            messagebox.showerror("Validation Error", "Title is required", parent=self)
            return

        # Determine color
        color_map = {
            'public_holiday': '#E0E0E0',
            'misc': '#FFF59D'
        }
        color = color_map.get(entry_type, '#FFF59D')

        try:
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

            # Go back to calendar
            self.navigation_manager.go_back()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry: {str(e)}", parent=self)
