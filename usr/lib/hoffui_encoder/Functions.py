from os import makedirs
from ttkbootstrap.toast import ToastNotification
from pathlib import Path

# Constants
DEBUG_SVR = False
DEBUG = False
Version_Number = "1.0.6.8"
Version = f"v{Version_Number}"


# Generic utility functions and constants


def ensure_directory_exists(directory):
    """Check if the directory exists, and create it if it doesn't."""
    if not Path(directory).exists():
        makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")


def ensure_file_exists(file_path):
    if not Path(file_path).is_file():
        return False
    else:
        return True


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


def search_string_in_list(string, lists):
    """Check if string is in the list (case-insensitive)."""
    return string.lower() in [item.lower() for item in lists]


def is_not_blank(s):
    """Check if string is not blank or whitespace only."""
    return bool(s and not s.isspace())


def split_string_by_delimiter(text, delimiter=","):
    """Split a string by delimiter and return cleaned list."""
    if not text:
        return []
    return [item.strip() for item in text.split(delimiter) if item.strip()]


def get_list_index_safe(lst, index, default=None):
    """Safely get item from list by index, return default if index out of range."""
    try:
        return lst[index]
    except (IndexError, TypeError):
        return default


def capitalize_name(name):
    """Properly capitalize a name."""
    if not name:
        return ""
    return name.strip().capitalize()


def format_display_name(first_name, last_name):
    """Format display name from first and last name."""
    first = capitalize_name(first_name)
    last = capitalize_name(last_name)
    return f"{first} {last}".strip()


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
