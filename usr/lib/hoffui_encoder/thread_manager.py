"""
Threading Module for Background Operations
Handles all background tasks with proper UI feedback and error handling.
"""

import time
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

    def run_search_operation(self, search_func, args=(), kwargs={}):
        """Run user search operation with animated progress."""

        def search_with_animation():
            try:
                # Start search
                tkt.call_nosync(
                    self.main_window.status.configure, text="Searching for user ..."
                )
                tkt.call_nosync(self._disable_widgets)

                # Animate progress during search
                for i in range(1, 101):
                    tkt.call_nosync(self.main_window.progress.configure, value=i)
                    if i % 10 == 0:
                        tkt.call_nosync(
                            self.main_window.status.configure,
                            text=f"Searching for user ... {i}%",
                        )
                    time.sleep(0.02)  # Reduced sleep time for smoother animation

                # Execute actual search
                result = search_func(*args, **kwargs)

                # Store results in main window
                self.main_window.updateList = result

                if not result:
                    tkt.call_nosync(
                        show_toast, "COMPLETE!", "No Users by that name", "sad"
                    )
                else:
                    # Populate results
                    tkt.call_nosync(self._populate_search_results, result)

            except Exception as e:
                tkt.call_nosync(show_toast, "ERROR!", "Search failed", "angry")
                tkt.call_nosync(
                    self.main_window.messageBox, "Error", f"Search failed: {str(e)}"
                )

            finally:
                tkt.call_nosync(self._enable_widgets)
                tkt.call_nosync(self.main_window.status.configure, text="Idle...")
                tkt.call_nosync(self.main_window.progress.configure, value=0)

        thread = Thread(target=search_with_animation)
        thread.daemon = True
        thread.start()
        return thread

    def run_update_operation(
        self, update_func, data, completion_message="Operation completed"
    ):
        """Run user update operation with progress feedback."""

        def update_with_progress():
            try:
                selected_item = self.main_window.tree4.selection()[0]
                tkt.call_nosync(
                    self.main_window.status.configure,
                    text=f"Updating {data['first']} {data['last']}",
                )
                tkt.call_nosync(self._disable_widgets)
                tkt.call_nosync(self.main_window.progress.configure, value=10)

                # Simulate preparation phase
                tkt.call_nosync(
                    self.main_window.status.configure, text="Gathering Information..."
                )
                time.sleep(0.5)
                tkt.call_nosync(self.main_window.progress.configure, value=30)

                # Execute the update
                tkt.call_nosync(
                    self.main_window.status.configure, text="Updating user..."
                )
                result = update_func(data)  # noqa
                tkt.call_nosync(self.main_window.progress.configure, value=90)

                # Finalization
                tkt.call_nosync(self.main_window.progress.configure, value=100)
                tkt.call_nosync(show_toast, "SUCCESS!!", completion_message, "happy")

            except Exception as e:
                tkt.call_nosync(show_toast, "ERROR!!", "Update failed", "angry")
                tkt.call_nosync(
                    self.main_window.messageBox, "Error", f"Update failed: {str(e)}"
                )

            finally:
                try:
                    selected_item = self.main_window.tree4.selection()[0]
                    tkt.call_nosync(
                        self.main_window.tree4.selection_remove, selected_item
                    )
                except Exception as e:
                    print(f"Error removing selection: {e}")
                    pass
                tkt.call_nosync(self._reset_selection)
                tkt.call_nosync(self._enable_widgets)
                tkt.call_nosync(self.main_window.status.configure, text="Idle...")
                tkt.call_nosync(self.main_window.progress.configure, value=0)

        thread = Thread(target=update_with_progress)
        thread.daemon = True
        thread.start()
        return thread

    def _disable_widgets(self):
        """Disable UI widgets during operations."""
        # Note: Specific widget disabling handled by individual operations
        pass

    def _enable_widgets(self):
        """Enable UI widgets after operations."""
        # Note: Specific widget enabling handled by individual operations
        pass

    def _populate_search_results(self, results):
        """Populate search results in the treeview."""
        self.main_window.status.configure(text="Populating list...")
        for user_key in results:
            user_data = results[user_key]
            self.main_window.tree4.insert(
                "",
                "end",
                values=(
                    user_key,
                    user_data["name"],
                    user_data["ou"],
                ),
            )

    def _reset_selection(self):
        """Reset selected item and clear entry fields."""
        self.main_window.selected_item = []
        # Clear entry fields if they exist
        try:
            for entry in [
                self.main_window.description_entry,
                self.main_window.title_entry,
                self.main_window.login_name_entry,
                self.main_window.domain_entry,
                self.main_window.lname_entry,
                self.main_window.fname_entry,
            ]:
                entry.configure(state="normal")
                entry.delete(0, "end")
            self.main_window.domain_entry.configure(state="readonly")
        except AttributeError:
            pass  # Widgets might not exist yet

    def stop_all_threads(self):
        """Stop all active threads (for cleanup)."""
        # Note: Python threads cannot be forcefully stopped
        # This method is here for future enhancement if needed
        self.active_threads.clear()
