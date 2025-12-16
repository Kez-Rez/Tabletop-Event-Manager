"""Feedback view for displaying feedback items from events"""
import customtkinter as ctk
from tkinter import messagebox


class FeedbackView(ctk.CTkFrame):
    """View for managing feedback items"""

    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, **kwargs)

        self.db = db

        # Title
        title = ctk.CTkLabel(
            self,
            text="Feedback",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#8B5FBF"
        )
        title.pack(pady=30, padx=30, anchor="w")

        # Info label
        info = ctk.CTkLabel(
            self,
            text="Feedback saved from post-event analysis. You can dismiss items here, but they will remain on the original event.",
            font=ctk.CTkFont(size=15),
            text_color="#666666"
        )
        info.pack(padx=30, anchor="w", pady=(0, 20))

        # Scrollable frame for feedback cards
        self.feedback_scroll = ctk.CTkScrollableFrame(self, fg_color="white")
        self.feedback_scroll.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # Load feedback
        self.load_feedback()

    def load_feedback(self):
        """Load all non-dismissed feedback items"""
        for widget in self.feedback_scroll.winfo_children():
            widget.destroy()

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get all feedback items that haven't been dismissed
        cursor.execute('''
            SELECT
                f.id,
                f.feedback_text,
                f.created_at,
                f.is_dismissed,
                e.event_name,
                e.event_date
            FROM feedback_items f
            JOIN events e ON f.event_id = e.id
            WHERE f.is_dismissed = 0
            ORDER BY f.created_at DESC
        ''')

        feedback_items = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not feedback_items:
            ctk.CTkLabel(
                self.feedback_scroll,
                text="No feedback items yet.\n\nAdd feedback from the post-event analysis page.",
                font=ctk.CTkFont(size=15),
                text_color="#999999"
            ).pack(pady=40)
            return

        for item in feedback_items:
            self.create_feedback_card(item)

    def create_feedback_card(self, item: dict):
        """Create a visual card for a feedback item"""
        card = ctk.CTkFrame(self.feedback_scroll, fg_color="#F9F5FA", border_width=2, border_color="#E6D9F2")
        card.pack(fill="x", padx=10, pady=8)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=15)

        # Top row - event name and date
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            top_row,
            text=item['event_name'],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#8B5FBF",
            anchor="w"
        ).pack(side="left")

        # Event date badge
        from datetime import datetime
        event_date = datetime.strptime(item['event_date'], '%Y-%m-%d')
        date_str = event_date.strftime('%d %b %Y')

        ctk.CTkLabel(
            top_row,
            text=date_str,
            fg_color="#C5A8D9",
            text_color="white",
            corner_radius=8,
            padx=8,
            pady=4,
            font=ctk.CTkFont(size=15)
        ).pack(side="right")

        # Feedback text
        text_label = ctk.CTkLabel(
            content,
            text=item['feedback_text'],
            text_color="#4A2D5E",
            font=ctk.CTkFont(size=15),
            anchor="w",
            wraplength=900,
            justify="left"
        )
        text_label.pack(fill="x", pady=(0, 10))

        # Bottom row - created date and dismiss button
        bottom_row = ctk.CTkFrame(content, fg_color="transparent")
        bottom_row.pack(fill="x")

        # Created date
        created_date = datetime.strptime(item['created_at'], '%Y-%m-%d %H:%M:%S')
        created_str = created_date.strftime('%d %b %Y at %H:%M')

        ctk.CTkLabel(
            bottom_row,
            text=f"Added: {created_str}",
            text_color="#999999",
            font=ctk.CTkFont(size=15),
            anchor="w"
        ).pack(side="left")

        # Dismiss button
        btn_dismiss = ctk.CTkButton(
            bottom_row,
            text="Dismiss",
            command=lambda i=item: self.dismiss_feedback(i['id']),
            fg_color="#E57373",
            hover_color="#D32F2F",
            text_color="white",
            width=80,
            height=28,
            font=ctk.CTkFont(size=15)
        )
        btn_dismiss.pack(side="right")

    def dismiss_feedback(self, feedback_id: int):
        """Dismiss a feedback item"""
        if not messagebox.askyesno("Dismiss Feedback",
            "Dismiss this feedback item from the Feedback menu?\n\nNote: It will remain on the original event."):
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE feedback_items
            SET is_dismissed = 1
            WHERE id = ?
        ''', (feedback_id,))

        conn.commit()
        conn.close()

        # Reload feedback
        self.load_feedback()
