from signal import SIGINT, signal

import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox

import Functions as func
import Gui
from thread_manager import ThreadManager

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
        print("Thanks for using Horizon Password User Tool!\n")
        self.destroy()

    def _hide(self):
        self.withdraw()

    def _show(self):
        self.update()
        self.deiconify()

    def messageBox(self, title, message):
        Messagebox.show_info(title=title, message=message)


if __name__ == "__main__":
    root = HoffUIEncoder()
    root.mainloop()
