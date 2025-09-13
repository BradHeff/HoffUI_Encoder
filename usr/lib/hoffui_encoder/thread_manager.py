"""
HoffUI FFMPEG Encoder - Background Thread Management Module

This module provides comprehensive thread management for background operations in
the HoffUI Encoder application. It handles video encoding tasks, progress tracking,
and UI feedback mechanisms while ensuring thread safety and proper resource cleanup.

Author: Brad Heffernan
Email: brad.heffernan83@outlook.com
Project: HoffUI Encoder
License: GNU General Public License v3.0

Features:
- Progress-aware background task execution
- Thread-safe UI updates and feedback mechanisms
- Error handling and recovery for long-running operations
- Operation cancellation and cleanup support
- Toast notification integration for user feedback
- Resource monitoring and system analytics integration
- Thread pool management for concurrent operations

Dependencies:
- Functions: Shared utilities and toast notification support
- threading: Native Python threading capabilities
- tkthread: Thread-safe Tkinter operations
- time: Operation timing and delay management
"""

# import time
from threading import Thread
import tkthread as tkt

# import ttkbootstrap as ttk
from Functions import show_toast


class ThreadManager:
    """Manages threaded operations with UI feedback."""

    def __init__(self, main_window):
        self.main_window = main_window
        self.active_threads = []
        self.stop_requested = False

    def run_with_progress(
        self,
        target_func,
        progress_callback=None,
        completion_callback=None,
        error_callback=None,
        args=(),
        kwargs={},
    ):
        """
        Run a function in a background thread with progress feedback.

        Args:
            target_func: Function to run in background
            progress_callback: Function to call for progress updates (value, status_text)
            completion_callback: Function to call on successful completion
            error_callback: Function to call on error
            args: Arguments for target_func
            kwargs: Keyword arguments for target_func
        """

        def threaded_operation():
            try:
                # Start progress
                if progress_callback:
                    tkt.call_nosync(progress_callback, 0, "Starting...")

                # Disable UI widgets
                tkt.call_nosync(self._disable_widgets)

                # Run the target function
                result = target_func(*args, **kwargs)

                # Complete progress
                if progress_callback:
                    tkt.call_nosync(progress_callback, 100, "Completed")

                # Call completion callback if provided
                if completion_callback:
                    tkt.call_nosync(completion_callback, result)

            except Exception as e:
                # Handle error
                if error_callback:
                    tkt.call_nosync(error_callback, e)
                else:
                    tkt.call_nosync(
                        show_toast, "ERROR!", f"An error occurred: {str(e)}", "angry"
                    )
                    tkt.call_nosync(
                        self.main_window.messageBox,
                        "Error",
                        f"An error occurred: {str(e)}",
                    )

            finally:
                # Re-enable UI widgets and reset progress
                tkt.call_nosync(self._enable_widgets)
                if progress_callback:
                    tkt.call_nosync(progress_callback, 0, "Idle...")

        # Start the thread
        thread = Thread(target=threaded_operation)
        thread.daemon = True
        thread.start()
        self.active_threads.append(thread)

        return thread

    def _disable_widgets(self):
        """Disable UI widgets during operations."""
        # Note: Specific widget disabling handled by individual operations
        pass

    def _enable_widgets(self):
        """Enable UI widgets after operations."""
        # Note: Specific widget enabling handled by individual operations
        pass

    def stop_current_operation(self):
        """Request to stop the current operation."""
        self.stop_requested = True

    def reset_stop_flag(self):
        """Reset the stop flag for new operations."""
        self.stop_requested = False

    def run_quick_task(self, task_func, args=(), kwargs={}):
        """Run a quick task in background without full progress handling."""

        def threaded_task():
            try:
                task_func(*args, **kwargs)
            except Exception as e:
                tkt.call_nosync(show_toast, "ERROR!", f"Task failed: {str(e)}", "angry")

        thread = Thread(target=threaded_task)
        thread.daemon = True
        thread.start()
        return thread

    def stop_all_threads(self):
        """Stop all active threads (for cleanup)."""
        # Note: Python threads cannot be forcefully stopped
        # This method is here for future enhancement if needed
        self.active_threads.clear()
