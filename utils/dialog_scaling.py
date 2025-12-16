"""Utility functions for dialog window scaling"""
import customtkinter as ctk


def apply_dialog_scaling(dialog_window):
    """
    Apply the current application zoom level to a dialog window.
    Call this in the dialog's __init__ method after super().__init__().

    Args:
        dialog_window: The CTkToplevel dialog window instance
    """
    # Import here to avoid circular imports
    try:
        from main import BGEventsApp
        current_scale = BGEventsApp.get_current_scale()

        # The scaling is already set globally, but we ensure it's applied
        # by forcing the dialog to update
        dialog_window.update_idletasks()
    except:
        pass  # If we can't get the scale, just continue without it


def get_scaled_size(base_width, base_height):
    """
    Get scaled window dimensions based on current zoom level.

    Args:
        base_width: Base width in pixels
        base_height: Base height in pixels

    Returns:
        tuple: (scaled_width, scaled_height)
    """
    try:
        from main import BGEventsApp
        scale = BGEventsApp.get_current_scale()
        return int(base_width * scale), int(base_height * scale)
    except:
        return base_width, base_height
