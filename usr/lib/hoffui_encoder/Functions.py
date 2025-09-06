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
