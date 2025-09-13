"""
HoffUI FFMPEG Encoder - Core Utility Functions Module

This module provides essential utility functions, constants, and shared functionality
used throughout the HoffUI FFMPEG Encoder application. It serves as the foundation
for common operations like file handling, notifications, and application settings.

Author: Brad Heffernan
Email: brad.heffernan83@outlook.com
Project: HoffUI Encoder
License: GNU General Public License v3.0

Features:
- Application version management and constants
- Toast notification system for user feedback
- File and directory management utilities
- String processing and validation functions
- Analytics window positioning calculations
- Debug and development support flags

Dependencies:
- ttkbootstrap: Toast notification system
- pathlib: Modern path handling
- os: Directory creation operations
"""

from os import makedirs
from ttkbootstrap.toast import ToastNotification
from pathlib import Path

# Constants
DEBUG = False
Version_Number = "1.0.6.8"
Version = f"v{Version_Number}"


# Generic utility functions and constants



def show_toast(title, message, type="happy"):
    """Show a toast notification."""
    icons = {"happy": "😀", "sad": "😟", "angry": "🤬"}
    icon = icons.get(type, icons["happy"])

    toast = ToastNotification(
        title=title,
        message=message,
        icon=icon,
        duration=10000,
    )
    toast.show_toast()


def is_not_blank(s):
    """Check if string is not blank or whitespace only."""
    return bool(s and not s.isspace())



def calculate_analytics_window_position(parent_window):
    """
    Calculate optimal position for Resource Analytics window.
    Returns (x, y, width, height) for analytics window placement.
    Determines if there's enough room on left or right of main window.
    """
    try:
        # Get main window geometry
        geometry = parent_window.geometry()
        # Parse geometry string: "widthxheight+x+y"
        size_pos = geometry.split("+")
        width_height = size_pos[0].split("x")

        main_width = int(width_height[0])
        main_height = int(width_height[1])
        main_x = int(size_pos[1]) if len(size_pos) > 1 else 0
        main_y = int(size_pos[2]) if len(size_pos) > 2 else 0

        # Get screen dimensions
        screen_width = parent_window.winfo_screenwidth()
        screen_height = parent_window.winfo_screenheight()

        # Analytics window dimensions
        analytics_width = 420  # Slightly wider for better display
        analytics_height = main_height

        # Determine placement (left or right of main window)
        left_edge_space = main_x
        right_edge_space = screen_width - (main_x + main_width)

        if left_edge_space >= analytics_width + 20:  # Prefer left side if there's room
            # Place to the left of main window
            analytics_x = main_x - analytics_width - 10
        elif (
            right_edge_space >= analytics_width + 20
        ):  # Use right side if left doesn't fit
            # Place to the right of main window
            analytics_x = main_x + main_width + 10
        else:
            # Neither side has enough room, place where there's more space
            if left_edge_space > right_edge_space:
                analytics_x = max(10, main_x - analytics_width - 10)
            else:
                analytics_x = min(
                    screen_width - analytics_width - 10, main_x + main_width + 10
                )

        # Ensure analytics window doesn't go off screen
        analytics_x = max(10, min(analytics_x, screen_width - analytics_width - 10))
        analytics_y = main_y  # Same Y position as main window

        # Ensure Y position is valid
        analytics_y = max(0, min(analytics_y, screen_height - analytics_height))

        return analytics_x, analytics_y, analytics_width, analytics_height

    except Exception as e:
        if DEBUG:
            print(f"Error calculating analytics window position: {e}")
        # Fallback position - right side of screen
        screen_width = parent_window.winfo_screenwidth() if parent_window else 1920
        return screen_width - 430, 100, 420, 700
