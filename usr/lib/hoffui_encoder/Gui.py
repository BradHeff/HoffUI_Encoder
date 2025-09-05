"""
Comprehensive FFMPEG Encoder GUI Module
Features tabbed settings, video info display, progress tracking,
and file/folder selection.
"""

import io
import base64
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import SUCCESS, WARNING, DISABLED
from PIL import Image, ImageTk
from Functions import DEBUG, show_toast
from icon import himage
from ffmpeg_encoder import FFMPEGEncoder, EncodingSettings
from thread_manager import ThreadManager


def setup_window(self):
    """Setup main window with optimized dimensions."""
    self.W, self.H = 900, 800
    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()
    center_x = int(screen_width / 2 - self.W / 2)
    center_y = int(screen_height / 2 - self.H / 2)
    self.geometry(f"{self.W}x{self.H}+{center_x}+{center_y}")
    self.resizable(True, True)
    self.minsize(800, 600)
    if DEBUG:
        print("WINDOW SETUP")


def setup_icon(self):
    """Setup application icon."""
    try:
        b64_img = io.BytesIO(base64.b64decode(himage))
        img = Image.open(b64_img, mode="r")
        photo = ImageTk.PhotoImage(image=img)
        self.wm_iconphoto(False, photo)
    except Exception as e:
        print(f"Icon setup error: {e}")
    if DEBUG:
        print("ICON SETUP")


def create_main_gui(self):
    """Create the main GUI with comprehensive layout."""
    setup_window(self)
    setup_icon(self)

    # Initialize encoder components
    self.encoder = FFMPEGEncoder()
    self.thread_manager = ThreadManager(self)
    self.current_video_info = None
    self.selected_files = []
    self.encoding_settings = EncodingSettings()

    # GUI variables
    self.progress_var = ttk.DoubleVar()
    self.status_var = ttk.StringVar(value="Ready")

    # Video settings variables
    self.video_codec_var = ttk.StringVar(value="H.264 (libx264)")
    self.video_bitrate_var = ttk.StringVar(value="2000k")
    self.resolution_var = ttk.StringVar(value="Original")
    self.fps_var = ttk.StringVar(value="Original")
    self.crf_var = ttk.IntVar(value=23)
    self.preset_var = ttk.StringVar(value="medium")

    # Audio settings variables
    self.audio_codec_var = ttk.StringVar(value="AAC")
    self.audio_bitrate_var = ttk.StringVar(value="128k")
    self.audio_sample_rate_var = ttk.StringVar(value="Original")
    self.audio_channels_var = ttk.StringVar(value="Original")

    # Output settings
    self.output_format_var = ttk.StringVar(value="mp4")
    self.output_dir_var = ttk.StringVar(value="")

    # Processing mode
    self.processing_mode = ttk.StringVar(value="single")

    # Configure main grid
    self.columnconfigure(0, weight=1)
    self.rowconfigure(2, weight=1)  # Give weight to main content area

    # Create header
    create_header(self)

    # Create video info section
    create_video_info_section(self)

    # Create main content area (tabs)
    create_main_content_tabs(self)

    # Create footer with controls and progress
    create_footer_controls(self)

    if DEBUG:
        print("MAIN GUI CREATED")


def create_header(self):
    """Create header with title and file/folder selection."""
    header_frame = ttk.Frame(self)
    header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    header_frame.columnconfigure(1, weight=1)

    # Title
    title_label = ttk.Label(
        header_frame,
        text="HoffUI FFMPEG Encoder",
        font=("Arial", 16, "bold"),
    )
    title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

    # Mode selection
    mode_frame = ttk.LabelFrame(header_frame, text="Processing Mode", padding=10)
    mode_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))

    single_radio = ttk.Radiobutton(
        mode_frame,
        text="Single File",
        variable=self.processing_mode,
        value="single",
        command=lambda: update_mode_selection(self),
    )
    single_radio.pack(side="left", padx=(0, 20))

    folder_radio = ttk.Radiobutton(
        mode_frame,
        text="Folder (Recursive)",
        variable=self.processing_mode,
        value="folder",
        command=lambda: update_mode_selection(self),
    )
    folder_radio.pack(side="left")

    # File/Folder selection
    selection_frame = ttk.Frame(header_frame)
    selection_frame.grid(row=2, column=0, columnspan=3, sticky="ew")
    selection_frame.columnconfigure(1, weight=1)

    self.browse_btn = ttk.Button(
        selection_frame, text="Browse File", command=lambda: browse_file_or_folder(self)
    )
    self.browse_btn.grid(row=0, column=0, padx=(0, 10))

    self.selected_path_var = ttk.StringVar(value="No file selected")
    path_label = ttk.Label(
        selection_frame, textvariable=self.selected_path_var, font=("Arial", 9)
    )
    path_label.grid(row=0, column=1, sticky="w")

    # Output directory selection
    ttk.Label(selection_frame, text="Output Directory:").grid(
        row=1, column=0, sticky="w", pady=(10, 0)
    )

    output_frame = ttk.Frame(selection_frame)
    output_frame.grid(row=1, column=1, sticky="ew", pady=(10, 0))
    output_frame.columnconfigure(0, weight=1)

    self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var)
    self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

    output_browse_btn = ttk.Button(
        output_frame, text="Browse", command=lambda: browse_output_directory(self)
    )
    output_browse_btn.grid(row=0, column=1)


def create_video_info_section(self):
    """Create video information display section."""
    info_frame = ttk.LabelFrame(self, text="Video Information", padding=10)
    info_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
    info_frame.columnconfigure(1, weight=1)
    info_frame.columnconfigure(3, weight=1)

    # Video info labels
    self.info_labels = {}
    info_items = [
        ("Filename:", "filename"),
        ("Duration:", "duration"),
        ("Resolution:", "resolution"),
        ("Aspect Ratio:", "aspect_ratio"),
        ("Video Codec:", "video_codec"),
        ("Audio Codec:", "audio_codec"),
        ("Bitrate:", "bitrate"),
        ("File Size:", "file_size"),
    ]

    for i, (label_text, key) in enumerate(info_items):
        row = i // 2
        col_start = (i % 2) * 2

        ttk.Label(info_frame, text=label_text, font=("Arial", 9, "bold")).grid(
            row=row, column=col_start, sticky="w", padx=(0, 5)
        )

        info_label = ttk.Label(info_frame, text="N/A", font=("Arial", 9))
        info_label.grid(row=row, column=col_start + 1, sticky="w", padx=(0, 20))
        self.info_labels[key] = info_label


def create_main_content_tabs(self):
    """Create main tabbed content area with encoding settings."""
    notebook = ttk.Notebook(self)
    notebook.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # Video Settings Tab
    video_tab = ttk.Frame(notebook)
    notebook.add(video_tab, text="Video Settings")
    create_video_settings_tab(self, video_tab)

    # Audio Settings Tab
    audio_tab = ttk.Frame(notebook)
    notebook.add(audio_tab, text="Audio Settings")
    create_audio_settings_tab(self, audio_tab)

    # Output Settings Tab
    output_tab = ttk.Frame(notebook)
    notebook.add(output_tab, text="Output Settings")
    create_output_settings_tab(self, output_tab)


def create_video_settings_tab(self, parent):
    """Create video encoding settings tab with horizontal layout."""
    # Create main container with padding
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # Configure grid layout for 3 columns
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.columnconfigure(2, weight=1)

    # Video Codec Section (Column 1)
    codec_frame = ttk.LabelFrame(main_frame, text="Video Codec", padding=10)
    codec_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))

    ttk.Label(codec_frame, text="Codec:", font=("Arial", 9, "bold")).pack(
        anchor="w", pady=(0, 3)
    )
    codec_combo = ttk.Combobox(
        codec_frame,
        textvariable=self.video_codec_var,
        values=list(self.encoder.VIDEO_CODECS.keys()),
        state="readonly",
        width=25,
    )
    codec_combo.pack(fill="x", pady=(0, 8))

    ttk.Label(codec_frame, text="Preset:", font=("Arial", 9, "bold")).pack(
        anchor="w", pady=(0, 3)
    )
    preset_combo = ttk.Combobox(
        codec_frame,
        textvariable=self.preset_var,
        values=self.encoder.PRESETS,
        state="readonly",
        width=25,
    )
    preset_combo.pack(fill="x")

    # Quality Settings (Column 2)
    quality_frame = ttk.LabelFrame(main_frame, text="Quality Settings", padding=10)
    quality_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=(0, 10))

    ttk.Label(quality_frame, text="CRF (Quality):", font=("Arial", 9, "bold")).pack(
        anchor="w", pady=(0, 3)
    )

    crf_container = ttk.Frame(quality_frame)
    crf_container.pack(fill="x", pady=(0, 8))

    crf_scale = ttk.Scale(
        crf_container,
        from_=0,
        to=51,
        variable=self.crf_var,
        orient="horizontal",
        length=150,
    )
    crf_scale.pack(side="left", fill="x", expand=True, padx=(0, 8))

    self.crf_label = ttk.Label(
        crf_container, text="23", width=3, font=("Arial", 9, "bold")
    )
    self.crf_label.pack(side="right")

    crf_scale.configure(
        command=lambda v: self.crf_label.configure(text=str(int(float(v))))
    )

    ttk.Label(quality_frame, text="Bitrate:", font=("Arial", 9, "bold")).pack(
        anchor="w", pady=(0, 3)
    )
    bitrate_combo = ttk.Combobox(
        quality_frame,
        textvariable=self.video_bitrate_var,
        values=["Auto", "1000k", "2000k", "4000k", "8000k", "16000k"],
        width=25,
    )
    bitrate_combo.pack(fill="x")

    # Resolution Settings (Column 3)
    resolution_frame = ttk.LabelFrame(main_frame, text="Resolution & FPS", padding=10)
    resolution_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=(0, 10))

    ttk.Label(resolution_frame, text="Resolution:", font=("Arial", 9, "bold")).pack(
        anchor="w", pady=(0, 3)
    )
    resolution_combo = ttk.Combobox(
        resolution_frame,
        textvariable=self.resolution_var,
        values=list(self.encoder.RESOLUTIONS.keys()),
        state="readonly",
        width=25,
    )
    resolution_combo.pack(fill="x", pady=(0, 8))

    ttk.Label(resolution_frame, text="Frame Rate:", font=("Arial", 9, "bold")).pack(
        anchor="w", pady=(0, 3)
    )
    fps_combo = ttk.Combobox(
        resolution_frame,
        textvariable=self.fps_var,
        values=["Original", "24", "30", "60"],
        state="readonly",
        width=25,
    )
    fps_combo.pack(fill="x")


def create_audio_settings_tab(self, parent):
    """Create audio encoding settings tab with horizontal layout."""
    # Create main container with padding
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # Configure grid layout for 2 columns (audio has fewer settings)
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)

    # Audio Codec Section (Column 1)
    codec_frame = ttk.LabelFrame(main_frame, text="Audio Codec", padding=10)
    codec_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))

    ttk.Label(codec_frame, text="Codec:", font=("Arial", 9, "bold")).pack(
        anchor="w", pady=(0, 3)
    )
    audio_codec_combo = ttk.Combobox(
        codec_frame,
        textvariable=self.audio_codec_var,
        values=list(self.encoder.AUDIO_CODECS.keys()),
        state="readonly",
        width=30,
    )
    audio_codec_combo.pack(fill="x", pady=(0, 8))

    ttk.Label(codec_frame, text="Channels:", font=("Arial", 9, "bold")).pack(
        anchor="w", pady=(0, 3)
    )
    channels_combo = ttk.Combobox(
        codec_frame,
        textvariable=self.audio_channels_var,
        values=["Original", "1", "2"],
        state="readonly",
        width=30,
    )
    channels_combo.pack(fill="x")

    # Audio Quality Settings (Column 2)
    quality_frame = ttk.LabelFrame(main_frame, text="Quality Settings", padding=10)
    quality_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))

    ttk.Label(quality_frame, text="Bitrate:", font=("Arial", 9, "bold")).pack(
        anchor="w", pady=(0, 3)
    )
    audio_bitrate_combo = ttk.Combobox(
        quality_frame,
        textvariable=self.audio_bitrate_var,
        values=["Auto", "64k", "128k", "192k", "256k", "320k"],
        width=30,
    )
    audio_bitrate_combo.pack(fill="x", pady=(0, 8))

    ttk.Label(quality_frame, text="Sample Rate:", font=("Arial", 9, "bold")).pack(
        anchor="w", pady=(0, 3)
    )
    sample_rate_combo = ttk.Combobox(
        quality_frame,
        textvariable=self.audio_sample_rate_var,
        values=["Original", "22050", "44100", "48000"],
        width=30,
    )
    sample_rate_combo.pack(fill="x")


def create_output_settings_tab(self, parent):
    """Create output settings tab."""
    settings_frame = ttk.Frame(parent)
    settings_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Output Format
    format_frame = ttk.LabelFrame(settings_frame, text="Output Format", padding=15)
    format_frame.pack(fill="x", pady=(0, 20))

    ttk.Label(format_frame, text="Container Format:").pack(anchor="w")
    format_combo = ttk.Combobox(
        format_frame,
        textvariable=self.output_format_var,
        values=["mp4", "mkv", "avi", "webm"],
        state="readonly",
        width=40,
    )
    format_combo.pack(fill="x", pady=(5, 0))

    # Advanced Options
    advanced_frame = ttk.LabelFrame(settings_frame, text="Advanced Options", padding=15)
    advanced_frame.pack(fill="x")

    self.maintain_structure_var = ttk.BooleanVar(value=True)
    maintain_check = ttk.Checkbutton(
        advanced_frame,
        text="Maintain folder structure in output",
        variable=self.maintain_structure_var,
    )
    maintain_check.pack(anchor="w", pady=(0, 10))

    self.overwrite_var = ttk.BooleanVar(value=False)
    overwrite_check = ttk.Checkbutton(
        advanced_frame, text="Overwrite existing files", variable=self.overwrite_var
    )
    overwrite_check.pack(anchor="w")


def create_footer_controls(self):
    """Create footer with progress bar and control buttons."""
    footer_frame = ttk.Frame(self)
    footer_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
    footer_frame.columnconfigure(1, weight=1)

    # Progress section
    progress_frame = ttk.LabelFrame(footer_frame, text="Progress", padding=10)
    progress_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
    progress_frame.columnconfigure(0, weight=1)

    # Progress bar
    self.progress_bar = ttk.Progressbar(
        progress_frame, variable=self.progress_var, maximum=100, length=400
    )
    self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))

    # Status label
    status_label = ttk.Label(progress_frame, textvariable=self.status_var)
    status_label.grid(row=1, column=0, sticky="w")

    # Control buttons
    button_frame = ttk.Frame(footer_frame)
    button_frame.grid(row=1, column=0, columnspan=3)

    self.start_btn = ttk.Button(
        button_frame,
        text="Start Encoding",
        bootstyle=SUCCESS,
        command=lambda: start_encoding(self),
    )
    self.start_btn.pack(side="left", padx=(0, 10))

    self.stop_btn = ttk.Button(
        button_frame,
        text="Stop",
        bootstyle=WARNING,
        command=lambda: stop_encoding(self),
        state=DISABLED,
    )
    self.stop_btn.pack(side="left", padx=(0, 10))

    ttk.Button(button_frame, text="Clear", command=lambda: clear_all(self)).pack(
        side="left"
    )


# Helper functions for GUI interactions


def update_mode_selection(self):
    """Update UI based on processing mode selection."""
    if self.processing_mode.get() == "single":
        self.browse_btn.configure(text="Browse File")
    else:
        self.browse_btn.configure(text="Browse Folder")


def browse_file_or_folder(self):
    """Browse for file or folder based on current mode."""
    if self.processing_mode.get() == "single":
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                (
                    "Video Files",
                    " ".join(f"*{ext}" for ext in self.encoder.SUPPORTED_VIDEO_FORMATS),
                ),
                ("All Files", "*.*"),
            ],
        )
        if file_path:
            self.selected_path_var.set(file_path)
            self.selected_files = [file_path]
            load_video_info(self, file_path)
    else:
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            self.selected_path_var.set(folder_path)
            # Load files in background thread
            self.thread_manager.run_with_progress(
                target_func=lambda: self.encoder.find_video_files(
                    folder_path, recursive=True
                ),
                completion_callback=lambda files: on_folder_loaded(self, files),
                progress_callback=lambda p, s: self.status_var.set(s),
                args=(),
            )


def browse_output_directory(self):
    """Browse for output directory."""
    directory = filedialog.askdirectory(title="Select Output Directory")
    if directory:
        self.output_dir_var.set(directory)


def load_video_info(self, file_path):
    """Load and display video information."""

    def load_info():
        return self.encoder.get_video_info(file_path)

    def update_info(video_info):
        if video_info:
            self.current_video_info = video_info
            self.info_labels["filename"].configure(text=video_info.filename)
            self.info_labels["duration"].configure(
                text=self.encoder.format_duration(video_info.duration)
            )
            self.info_labels["resolution"].configure(
                text=f"{video_info.width}x{video_info.height}"
            )
            self.info_labels["aspect_ratio"].configure(text=video_info.aspect_ratio)
            self.info_labels["video_codec"].configure(text=video_info.video_codec)
            self.info_labels["audio_codec"].configure(text=video_info.audio_codec)
            self.info_labels["bitrate"].configure(
                text=(
                    f"{video_info.bitrate} bps" if video_info.bitrate > 0 else "Unknown"
                )
            )
            self.info_labels["file_size"].configure(
                text=self.encoder.format_file_size(video_info.file_size)
            )
        else:
            # Clear info if loading failed
            for label in self.info_labels.values():
                label.configure(text="N/A")

    self.thread_manager.run_with_progress(
        target_func=load_info,
        completion_callback=update_info,
        progress_callback=lambda p, s: self.status_var.set(s),
        args=(),
    )


def on_folder_loaded(self, files):
    """Handle folder loading completion."""
    self.selected_files = files
    self.status_var.set(f"Found {len(files)} video files")
    if files:
        # Load info for first file as preview
        load_video_info(self, files[0])


def start_encoding(self):
    """Start the encoding process."""
    if not self.selected_files:
        messagebox.showwarning("No Files", "Please select files to encode.")
        return

    if not self.output_dir_var.get():
        messagebox.showwarning("No Output", "Please select output directory.")
        return

    # Update encoding settings from GUI
    update_encoding_settings_from_gui(self)

    # Disable controls
    self.start_btn.configure(state=DISABLED)
    self.stop_btn.configure(state="normal")

    # Start encoding in background
    self.thread_manager.run_with_progress(
        target_func=lambda: encode_all_files(self),
        completion_callback=lambda success: on_encoding_complete(self, success),
        progress_callback=lambda p, s: update_progress(self, p, s),
        args=(),
    )


def encode_all_files(self):
    """Encode all selected files."""
    total_files = len(self.selected_files)

    for i, file_path in enumerate(self.selected_files):
        # Generate output path
        output_path = self.encoder.get_output_path(
            file_path,
            self.output_dir_var.get(),
            self.encoding_settings,
            self.maintain_structure_var.get(),
        )

        # Encode file
        success = self.encoder.encode_video(
            file_path,
            output_path,
            self.encoding_settings,
            progress_callback=lambda p, s: update_encoding_progress(
                self, i, total_files, p, s
            ),
        )

        if not success:
            return False

        return True

    def update_encoding_progress(
        self, current_file, total_files, file_progress, status
    ):
        """Update encoding progress during encoding."""
        overall_progress = (current_file / total_files) * 100 + (
            file_progress / total_files
        )

        status_text = f"File {current_file + 1}/{total_files}: {status}"

        # Update UI in main thread
        self.progress_var.set(overall_progress)
        self.status_var.set(status_text)


def update_progress(self, progress, status):
    """Update progress bar and status."""
    self.progress_var.set(progress)
    self.status_var.set(status)


def on_encoding_complete(self, success):
    """Handle encoding completion."""
    # Re-enable controls
    self.start_btn.configure(state="normal")
    self.stop_btn.configure(state=DISABLED)

    if success:
        self.status_var.set("Encoding completed successfully!")
        show_toast("Success", "All videos encoded successfully!")
    else:
        self.status_var.set("Encoding failed or was interrupted.")
        show_toast("Error", "Encoding failed. Check console for details.")

    self.progress_var.set(0)


def stop_encoding(self):
    """Stop the encoding process."""
    # TODO: Implement proper cancellation
    self.start_btn.configure(state="normal")
    self.stop_btn.configure(state=DISABLED)
    self.status_var.set("Encoding stopped by user.")
    self.progress_var.set(0)


def clear_all(self):
    """Clear all selections and reset interface."""
    self.selected_files = []
    self.selected_path_var.set("No file selected")
    self.output_dir_var.set("")
    self.current_video_info = None

    # Clear video info
    for label in self.info_labels.values():
        label.configure(text="N/A")

    # Reset progress
    self.progress_var.set(0)
    self.status_var.set("Ready")


def update_encoding_settings_from_gui(self):
    """Update encoding settings from GUI values."""
    self.encoding_settings.video_codec = self.encoder.VIDEO_CODECS.get(
        self.video_codec_var.get(), "libx264"
    )
    self.encoding_settings.video_bitrate = self.video_bitrate_var.get()
    self.encoding_settings.resolution = self.resolution_var.get()
    self.encoding_settings.fps = self.fps_var.get()
    self.encoding_settings.crf = self.crf_var.get()
    self.encoding_settings.preset = self.preset_var.get()

    self.encoding_settings.audio_codec = self.encoder.AUDIO_CODECS.get(
        self.audio_codec_var.get(), "aac"
    )
    self.encoding_settings.audio_bitrate = self.audio_bitrate_var.get()
    self.encoding_settings.audio_sample_rate = self.audio_sample_rate_var.get()
    self.encoding_settings.audio_channels = self.audio_channels_var.get()

    self.encoding_settings.output_format = self.output_format_var.get()
    self.encoding_settings.output_directory = self.output_dir_var.get()


# Main function to initialize GUI
def main_ui(self):
    """Initialize the comprehensive encoder GUI - main entry point."""
    # Initialize the GUI
    create_main_gui(self)

    if DEBUG:
        print("ENCODER GUI INITIALIZED")
