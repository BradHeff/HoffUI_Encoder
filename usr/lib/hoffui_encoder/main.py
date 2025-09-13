"""
HoffUI FFMPEG Encoder - Main Application Module

This module contains the main entry point and primary application class for the 
HoffUI FFMPEG Encoder, a professional video encoding tool with AI-powered optimization.

The application provides a modern GUI interface for video encoding operations using
FFMPEG, with automatic system detection and performance optimization capabilities.

Author: Brad Heffernan
Email: brad.heffernan83@outlook.com
Project: HoffUI Encoder
License: GNU General Public License v3.0

Features:
- Multi-threaded video encoding operations
- Real-time progress tracking and monitoring
- System resource analytics and optimization
- AI-powered encoding parameter optimization
- Cross-platform compatibility (Linux, Windows, macOS)
- Hardware acceleration support detection

Dependencies:
- ttkbootstrap: Modern GUI framework
- Functions: Shared utility functions
- Gui: User interface components
- thread_manager: Background operation management
- ffmpeg_encoder: Core encoding functionality
"""

import sys
from signal import SIGINT, signal

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
import Functions as func
import Gui
from thread_manager import ThreadManager
from ffmpeg_encoder import FFMPEGEncoder

# Constants
WINDOW_TITLE = "HoffUI FFMPEG Encoder v{}"


class HoffUIEncoder(ttk.Window):
    """Main Class for HoffUI FFMPEG Encoder"""

    def __init__(self):
        super(HoffUIEncoder, self).__init__(themename="litera")
        self._hide()
        self._setup_window()
        self._initialize_variables()
        self._setup_gui()
        self._show()

    def _setup_window(self):
        self.bind_all("<Control-c>", self.on_closing)
        signal(SIGINT, lambda x, y: print("") or self.on_closing())
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title(WINDOW_TITLE.format(func.Version[4:]))

    def _initialize_variables(self):
        self.data = {}
        self.options = []

        # Initialize managers
        self.thread_manager = ThreadManager(self)

    def _setup_gui(self):
        Gui.main_ui(self)

    def is_not_blank(self, s):
        return bool(s and not s.isspace())

    def on_closing(self):
        """Handle application closing with proper cleanup."""
        # Stop resource analytics monitoring if active
        if hasattr(self, "resource_analytics") and self.resource_analytics:
            self.resource_analytics.stop_monitoring_process()

        # Stop any active encoding operations
        if hasattr(self, "thread_manager"):
            self.thread_manager.stop_current_operation()

        print("Thanks for using HoffUI FFMPEG Encoder!\n")
        self.destroy()

    def _hide(self):
        self.withdraw()

    def _show(self):
        self.update()
        self.deiconify()

    def messageBox(self, title, message):
        Messagebox.show_info(title=title, message=message)


if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--system-info", "-si", "--sysinfo"]:
            print("🔍 Displaying System Information for Encoding Optimization")
            print("=" * 60)
            try:
                encoder = FFMPEGEncoder()
                encoder.display_system_info()
                print(
                    "💡 This information is automatically detected when encoding starts."
                )
                print("   The application will use these optimal settings dynamically.")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error detecting system info: {e}")
                sys.exit(1)
        elif sys.argv[1] in ["--help", "-h"]:
            print("HoffUI FFMPEG Encoder - Video Encoding Tool")
            print("=" * 50)
            print("Usage:")
            print("  python main.py                 # Start GUI application")
            print("  python main.py --system-info   # Show system detection results")
            print("  python main.py --help          # Show this help")
            print("")
            print("The application automatically detects your system capabilities")
            print("and optimizes encoding settings for maximum performance.")
            sys.exit(0)

    # Start GUI application
    root = HoffUIEncoder()
    root.mainloop()
