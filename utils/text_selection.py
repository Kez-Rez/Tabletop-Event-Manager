"""Utility functions to make text selectable and copyable throughout the application"""
import tkinter as tk
import customtkinter as ctk


def create_selectable_text(parent, text, font=None, text_color="#000000", **kwargs):
    """
    Create a text widget that looks like a label but supports full mouse text selection.
    This is a workaround since CTkLabel doesn't support drag-to-select.
    """
    # Create a Text widget configured to look and behave like a label
    text_widget = tk.Text(
        parent,
        height=1,
        wrap="word",
        relief="flat",
        highlightthickness=0,
        bg=parent.cget("bg") if hasattr(parent, "cget") else "white",
        fg=text_color,
        font=font if font else ("Helvetica", 12),
        cursor="xterm",
        **kwargs
    )

    # Insert the text
    text_widget.insert("1.0", text)

    # Make it read-only but still selectable
    text_widget.config(state="disabled")

    # Enable text selection even when disabled
    text_widget.bind("<Button-1>", lambda e: text_widget.focus_set())

    # Override the disabled state to allow selection
    def enable_selection(event):
        text_widget.config(state="normal")
        return "break"

    def disable_editing(event):
        text_widget.config(state="disabled")
        return "break"

    text_widget.bind("<Button-1>", enable_selection)
    text_widget.bind("<ButtonRelease-1>", disable_editing)

    return text_widget


def make_label_selectable(label):
    """Make a CTkLabel widget's text copyable with keyboard shortcuts"""

    def on_click(event):
        # Single click to focus
        try:
            label.focus_set()
            label._text_for_copy = label.cget("text")
        except:
            pass

    def on_copy(event):
        # Copy text to clipboard
        try:
            text = label.cget("text")
            label.clipboard_clear()
            label.clipboard_append(text)
            # Visual feedback for copy
            original_bg = label.cget("fg_color")
            label.configure(fg_color="#90EE90")  # Light green for successful copy
            label.after(200, lambda: label.configure(fg_color=original_bg if original_bg else "transparent"))
        except:
            pass

    # Change cursor to indicate text can be copied
    label.configure(cursor="hand2")

    # Bind events
    label.bind("<Button-1>", on_click)
    label.bind("<Control-c>", on_copy)
    label.bind("<Control-C>", on_copy)


def setup_global_text_selection(root_window):
    """Enable text selection and copying throughout the application"""

    def recursive_setup(widget):
        """Recursively apply text selection to all labels"""
        try:
            # Make CTkLabel widgets selectable
            if isinstance(widget, ctk.CTkLabel):
                make_label_selectable(widget)

            # For Entry and Textbox widgets, ensure they support standard text selection
            # (they already do by default, but we can ensure copy works)
            if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                widget.bind("<Control-c>", lambda e: None)  # Allow default behavior
                widget.bind("<Control-C>", lambda e: None)

            # Recursively process all child widgets
            for child in widget.winfo_children():
                recursive_setup(child)
        except:
            pass

    # Initial setup
    recursive_setup(root_window)

    # Add global keyboard shortcut for copying selected label text
    def global_copy(event):
        try:
            focused = root_window.focus_get()
            if isinstance(focused, ctk.CTkLabel) and hasattr(focused, '_text_for_copy'):
                focused.clipboard_clear()
                focused.clipboard_append(focused._text_for_copy)
                return "break"
        except:
            pass

    root_window.bind_all("<Control-c>", global_copy, add=True)
    root_window.bind_all("<Control-C>", global_copy, add=True)
