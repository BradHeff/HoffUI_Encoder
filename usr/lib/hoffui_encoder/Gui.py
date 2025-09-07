"""
Comprehensive FFMPEG Encoder GUI Module
Features tabbed settings, video info display, progress tracking,
and file/folder selection.
"""

import io
import os
import base64
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import SUCCESS, WARNING, DISABLED
from PIL import Image, ImageTk
from Functions import DEBUG, show_toast
from icon import himage
from ffmpeg_encoder import FFMPEGEncoder, EncodingSettings
from thread_manager import ThreadManager
from openai_analyzer import OpenAIVideoAnalyzer
from settings_manager import SettingsManager


def setup_window(self):
    """Setup main window with optimized dimensions."""
    self.W, self.H = 1050, 1010
    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()
    center_x = int(screen_width / 2 - self.W / 2)
    center_y = int(screen_height / 2 - self.H / 2)
    self.geometry(f"{self.W}x{self.H}+{center_x}+{center_y}")
    self.resizable(True, True)
    self.minsize(1050, 1010)
    if DEBUG:
        print("WINDOW SETUP")


def setup_icon(self):
    """Setup application icon."""
    try:
        b64_img = io.BytesIO(base64.b64decode(himage))
        img = Image.open(b64_img, mode="r")
        photo = ImageTk.PhotoImage(image=img)
        self.wm_iconphoto(False, photo)
        if DEBUG:
            print("ICON SETUP - Success")
    except Exception as e:
        if DEBUG:
            print(f"Icon setup error: {e}")
        # Continue without icon - not critical for functionality
        pass


def create_main_gui(self):
    """Create the main GUI with comprehensive layout."""
    setup_window(self)
    setup_icon(self)

    # Initialize encoder components
    self.encoder = FFMPEGEncoder()
    self.thread_manager = ThreadManager(self)
    self.ai_analyzer = OpenAIVideoAnalyzer()
    self.settings_manager = SettingsManager()
    self.current_video_info = None
    self.selected_files = []
    self.encoding_settings = EncodingSettings()
    self._loading_settings = False  # Flag to prevent auto-save during settings loading

    # Load settings if they exist and auto-load is enabled
    self.app_settings = self.settings_manager.load_settings()

    # Auto-populate API key from .env if DEBUG is enabled
    auto_api_key = self.settings_manager.get_auto_load_api_key()
    if auto_api_key:
        self.app_settings.openai_api_key = auto_api_key

    # GUI variables
    self.progress_var = ttk.DoubleVar()
    self.status_var = ttk.StringVar(value="Ready")
    self.current_file_var = ttk.StringVar(value="")

    # AI Encoding variables - initialize from settings
    self.ai_encoding_var = ttk.BooleanVar(value=self.app_settings.ai_encoding_enabled)
    self.openai_api_key_var = ttk.StringVar(value=self.app_settings.openai_api_key)
    self.notebook = None  # Will store reference to the notebook for tab control

    # Video settings variables - initialize from settings
    self.video_codec_var = ttk.StringVar(value=self.app_settings.video_codec)
    self.video_bitrate_var = ttk.StringVar(value=self.app_settings.video_bitrate)
    self.resolution_var = ttk.StringVar(value=self.app_settings.resolution)
    self.fps_var = ttk.StringVar(value=self.app_settings.fps)
    self.crf_var = ttk.IntVar(value=self.app_settings.crf)
    self.preset_var = ttk.StringVar(value=self.app_settings.preset)

    # Audio settings variables - initialize from settings
    self.audio_codec_var = ttk.StringVar(value=self.app_settings.audio_codec)
    self.audio_bitrate_var = ttk.StringVar(value=self.app_settings.audio_bitrate)
    self.audio_sample_rate_var = ttk.StringVar(
        value=self.app_settings.audio_sample_rate
    )
    self.audio_channels_var = ttk.StringVar(value=self.app_settings.audio_channels)

    # Output settings - initialize from settings
    self.output_format_var = ttk.StringVar(value=self.app_settings.output_format)
    self.output_dir_var = ttk.StringVar(value=self.app_settings.output_directory)
    self.maintain_structure_var = ttk.BooleanVar(
        value=self.app_settings.maintain_structure
    )

    # Processing mode - initialize from settings
    self.processing_mode = ttk.StringVar(value=self.app_settings.processing_mode)

    # System information dictionary
    self.system_info_dict = {}

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

    # Apply AI toggle state on startup if AI is enabled
    if self.ai_encoding_var.get():
        on_ai_toggle_changed(self)

    if DEBUG:
        print("MAIN GUI CREATED")


def create_header(self):
    """Create header with title and file/folder selection."""
    header_frame = ttk.Frame(self)
    header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    header_frame.columnconfigure(1, weight=1)

    # Title and Settings
    title_frame = ttk.Frame(header_frame)
    title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
    title_frame.columnconfigure(0, weight=1)

    title_label = ttk.Label(
        title_frame,
        text="HoffUI FFMPEG Encoder",
        font=("Arial", 16, "bold"),
    )
    title_label.grid(row=0, column=0, sticky="w")

    # Settings buttons
    settings_frame = ttk.Frame(title_frame)
    settings_frame.grid(row=0, column=1, sticky="e")

    ttk.Button(
        settings_frame,
        text="Save Settings",
        command=lambda: save_current_settings(self),
        width=12,
    ).pack(side="right", padx=(5, 0))

    ttk.Button(
        settings_frame,
        text="Load Settings",
        command=lambda: load_saved_settings(self),
        width=12,
    ).pack(side="right")

    # AI Encoding Section
    ai_frame = ttk.LabelFrame(header_frame, text="AI Encoding (Beta)", padding=10)
    ai_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
    ai_frame.columnconfigure(1, weight=1)

    # AI Toggle
    ai_check = ttk.Checkbutton(
        ai_frame,
        text="Enable AI-Optimized Encoding",
        variable=self.ai_encoding_var,
        command=lambda: on_ai_toggle_changed(self),
        bootstyle=SUCCESS,
    )
    ai_check.grid(row=0, column=0, sticky="w", pady=(0, 5))

    # AI Description
    ai_desc = ttk.Label(
        ai_frame,
        text="Uses AI analysis to optimize encoding settings for smallest file size with maximum quality",
        font=("Arial", 8),
        foreground="gray",
    )
    ai_desc.grid(row=0, column=1, columnspan=2, sticky="w", padx=(10, 0), pady=(0, 5))

    # OpenAI API Key
    ttk.Label(ai_frame, text="OpenAI API Key:").grid(
        row=1, column=0, sticky="w", pady=(5, 0)
    )

    api_key_frame = ttk.Frame(ai_frame)
    api_key_frame.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))
    api_key_frame.columnconfigure(0, weight=1)

    self.api_key_entry = ttk.Entry(
        api_key_frame, textvariable=self.openai_api_key_var, show="*", state="normal"
    )
    self.api_key_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

    ttk.Label(
        api_key_frame,
        text="(Optional - uses rule-based fallback if not provided)",
        font=("Arial", 8),
        foreground="gray",
    ).grid(row=0, column=1)

    # Mode selection
    mode_frame = ttk.Frame(header_frame)
    mode_frame.grid(row=2, column=0, columnspan=3, pady=(10, 0))

    ttk.Label(mode_frame, text="Processing Mode:", font=("Arial", 10, "bold")).pack(
        side="left", padx=(0, 10)
    )

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
    selection_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
    selection_frame.columnconfigure(1, weight=1)

    self.browse_btn = ttk.Button(
        selection_frame,
        text="Browse File",
        command=lambda: browse_file_or_folder(self),
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
    self.notebook = ttk.Notebook(self)
    self.notebook.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # Video Settings Tab
    video_tab = ttk.Frame(self.notebook)
    self.notebook.add(video_tab, text="Video Settings")
    create_video_settings_tab(self, video_tab)

    # Audio Settings Tab
    audio_tab = ttk.Frame(self.notebook)
    self.notebook.add(audio_tab, text="Audio Settings")
    create_audio_settings_tab(self, audio_tab)

    # Output Settings Tab
    output_tab = ttk.Frame(self.notebook)
    self.notebook.add(output_tab, text="Output Settings")
    create_output_settings_tab(self, output_tab)

    # Extras Tab (Resource Analytics)
    extras_tab = ttk.Frame(self.notebook)
    self.notebook.add(extras_tab, text="Extras")
    create_extras_tab(self, extras_tab)

    # System Information Tab
    system_tab = ttk.Frame(self.notebook)
    self.notebook.add(system_tab, text="System")
    create_system_info_tab(self, system_tab)

    return self.notebook


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


def create_extras_tab(self, parent):
    """Create extras tab with Resource Analytics toggle and other advanced features using horizontal layout."""

    # Create main container with minimal padding for maximum space utilization
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # Configure grid layout for horizontal arrangement
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(1, weight=1)  # Main content expandable

    # === TOP SECTION: Title (Full Width) ===
    title_frame = ttk.Frame(main_frame)
    title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

    title_label = ttk.Label(
        title_frame, text="🚀 Extra Features & Analytics", font=("Arial", 14, "bold")
    )
    title_label.pack()

    # === MAIN CONTENT: Two Column Layout ===

    # Left Column - Resource Analytics
    left_column = ttk.Frame(main_frame)
    left_column.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
    left_column.rowconfigure(0, weight=1)

    # Right Column - Future Features
    right_column = ttk.Frame(main_frame)
    right_column.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
    right_column.rowconfigure(0, weight=1)

    # === LEFT COLUMN: Resource Analytics Section ===
    analytics_frame = ttk.LabelFrame(
        left_column, text="📊 Resource Usage Analytics", padding=15
    )
    analytics_frame.grid(row=0, column=0, sticky="nsew")

    # Description
    desc_label = ttk.Label(
        analytics_frame,
        text="Monitor system resources and FFmpeg processes\nin real-time with graphical displays.",
        font=("Arial", 10),
        foreground="gray",
        justify="center",
    )
    desc_label.pack(pady=(0, 15))

    # Analytics toggle with enhanced styling
    toggle_frame = ttk.Frame(analytics_frame)
    toggle_frame.pack(fill="x", pady=(0, 15))

    # Initialize the analytics toggle variable
    if not hasattr(self, "resource_analytics_enabled"):
        self.resource_analytics_enabled = ttk.BooleanVar(value=False)

    analytics_check = ttk.Checkbutton(
        toggle_frame,
        text="Enable Resource Analytics",
        variable=self.resource_analytics_enabled,
        command=lambda: toggle_resource_analytics(self),
        style="success.TCheckbutton",
    )
    analytics_check.pack(side="left")

    # Status indicator
    self.analytics_status_label = ttk.Label(
        toggle_frame, text="● Disabled", font=("Arial", 9), foreground="red"
    )
    self.analytics_status_label.pack(side="right")

    # Analytics features description - compact format
    features_text = """✓ Real-time CPU, Memory, Network monitoring
✓ FFmpeg process tracking & metrics
✓ Interactive charts with history data
✓ Companion window positioning
✓ Live performance analytics"""

    features_label = ttk.Label(
        analytics_frame,
        text=features_text,
        font=("Arial", 9),
        justify="left",
        foreground="gray",
    )
    features_label.pack(anchor="w")

    # === RIGHT COLUMN: Future Features Section ===
    future_frame = ttk.LabelFrame(right_column, text="🚀 Coming Soon", padding=15)
    future_frame.grid(row=0, column=0, sticky="nsew")

    # Future features - compact format
    future_text = """✓ Video quality comparison tools
✓ Encoding presets marketplace
✓ Batch operation templates
✓ Advanced filtering options
✓ Cloud storage integration
✓ Performance benchmarking
✓ Custom encoding profiles"""

    future_label = ttk.Label(
        future_frame,
        text=future_text,
        font=("Arial", 9),
        justify="left",
        foreground="gray",
    )
    future_label.pack(anchor="w", pady=(10, 0))

    # Add some spacing and additional info
    info_label = ttk.Label(
        future_frame,
        text="\nThese features are planned for future releases.\nStay tuned for updates!",
        font=("Arial", 8),
        justify="center",
        foreground="darkgray",
    )
    info_label.pack(pady=(20, 0))

    # Initialize resource analytics (but don't start monitoring yet)
    if not hasattr(self, "resource_analytics"):
        self.resource_analytics = None


def create_system_info_tab(self, parent):
    """Create system information tab showing detected capabilities - optimized for 1050x940."""

    # Create main container with minimal padding for maximum space utilization
    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # Configure grid layout for optimal space usage
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.columnconfigure(2, weight=1)
    main_frame.rowconfigure(1, weight=1)  # System info section expandable

    # === TOP SECTION: Detection Controls (Full Width) ===
    top_frame = ttk.Frame(main_frame)
    top_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
    top_frame.columnconfigure(1, weight=1)  # Space between elements

    # Title and button side by side
    title_label = ttk.Label(
        top_frame,
        text="🖥️ System Detection & Performance Analysis",
        font=("Arial", 14, "bold"),
    )
    title_label.grid(row=0, column=0, sticky="w")

    self.detect_button = ttk.Button(
        top_frame,
        text="🔍 Detect System Capabilities",
        command=lambda: detect_system_info_handler(self),
        style="Accent.TButton",
        width=25,
    )
    self.detect_button.grid(row=0, column=2, sticky="e")

    # Status in second row
    self.detection_status_var = ttk.StringVar(
        value="Click 'Detect System Capabilities' to analyze your system hardware and optimize encoding settings"
    )
    status_label = ttk.Label(
        top_frame,
        textvariable=self.detection_status_var,
        font=("Arial", 9),
        foreground="blue",
        wraplength=900,
    )
    status_label.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5, 0))

    # === MAIN CONTENT: Three Column Layout ===

    # Left Column - CPU & Memory
    left_column = ttk.Frame(main_frame)
    left_column.grid(row=1, column=0, sticky="nsew", padx=(0, 3))
    left_column.rowconfigure(0, weight=1)
    left_column.rowconfigure(1, weight=1)

    # Middle Column - GPU & Hardware Acceleration
    middle_column = ttk.Frame(main_frame)
    middle_column.grid(row=1, column=1, sticky="nsew", padx=3)
    middle_column.rowconfigure(0, weight=1)
    middle_column.rowconfigure(1, weight=1)

    # Right Column - Performance & Settings
    right_column = ttk.Frame(main_frame)
    right_column.grid(row=1, column=2, sticky="nsew", padx=(3, 0))
    right_column.rowconfigure(0, weight=1)
    right_column.rowconfigure(1, weight=1)

    # Store references for later use
    self.system_left_column = left_column
    self.system_middle_column = middle_column
    self.system_right_column = right_column

    # Initial empty state
    create_compact_empty_display_handler(self)


def create_compact_empty_display_handler(self):
    """Create empty system display for compact three-column layout."""
    # Clear existing content
    for col in [
        self.system_left_column,
        self.system_middle_column,
        self.system_right_column,
    ]:
        for widget in col.winfo_children():
            widget.destroy()

    # Left Column - CPU & Memory section
    cpu_frame = ttk.LabelFrame(
        self.system_left_column, text="🖥️ CPU & Memory", padding=8
    )
    cpu_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))

    cpu_label = ttk.Label(
        cpu_frame,
        text="No system detection performed",
        font=("Arial", 9),
        foreground="gray",
    )
    cpu_label.pack()

    # Memory section in left column
    mem_frame = ttk.LabelFrame(
        self.system_left_column, text="🧠 System Memory", padding=8
    )
    mem_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    mem_label = ttk.Label(
        mem_frame,
        text="Memory info will appear here",
        font=("Arial", 9),
        foreground="gray",
    )
    mem_label.pack()

    # Middle Column - GPU & Hardware
    gpu_frame = ttk.LabelFrame(
        self.system_middle_column, text="🎮 GPU & Graphics", padding=8
    )
    gpu_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))

    gpu_label = ttk.Label(
        gpu_frame, text="GPU detection pending", font=("Arial", 9), foreground="gray"
    )
    gpu_label.pack()

    # Hardware acceleration section
    hw_frame = ttk.LabelFrame(
        self.system_middle_column, text="⚡ Hardware Acceleration", padding=8
    )
    hw_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    hw_label = ttk.Label(
        hw_frame,
        text="Acceleration support will be shown here",
        font=("Arial", 9),
        foreground="gray",
    )
    hw_label.pack()

    # Right Column - Performance & Settings
    perf_frame = ttk.LabelFrame(
        self.system_right_column, text="⚡ Performance Settings", padding=8
    )
    perf_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))

    perf_label = ttk.Label(
        perf_frame,
        text="Optimal settings will appear here",
        font=("Arial", 9),
        foreground="gray",
    )
    perf_label.pack()

    # Summary section in right column
    summary_frame = ttk.LabelFrame(
        self.system_right_column, text="📊 Quick Summary", padding=8
    )
    summary_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    summary_label = ttk.Label(
        summary_frame,
        text="Click 'Detect System Capabilities' to begin",
        font=("Arial", 9),
        foreground="gray",
    )
    summary_label.pack()


def update_system_summary(self):
    """Update status - no longer needed with compact layout but kept for compatibility."""
    # This function is now minimal since we don't have a separate summary panel
    pass


def detect_system_info_handler(self):
    """Detect and display system information."""
    try:
        self.detection_status_var.set("🔍 Detecting system capabilities...")
        self.detect_button.config(state="disabled")
        self.update()

        # Get system specs and optimal settings
        system_specs, optimal_settings = self.encoder.get_system_info()

        if system_specs and optimal_settings:
            # Populate system info dictionary
            self.system_info_dict = {
                "cpu_physical_cores": system_specs.cpu_cores_physical,
                "cpu_logical_cores": system_specs.cpu_cores_logical,
                "cpu_brand": system_specs.cpu_brand,
                "memory_total_gb": system_specs.memory_total_gb,
                "memory_available_gb": system_specs.memory_available_gb,
                "gpu_info": system_specs.gpu_info,
                "hw_acceleration": system_specs.hw_acceleration,
                "ffmpeg_encoders": system_specs.ffmpeg_encoders,
                "optimal_threads": optimal_settings.optimal_threads,
                "conservative_threads": optimal_settings.conservative_threads,
                "preferred_hwaccel": optimal_settings.preferred_hwaccel,
                "buffer_size": optimal_settings.buffer_size,
                "mux_queue_size": optimal_settings.mux_queue_size,
                "reasoning": optimal_settings.reasoning,
            }

            self.detection_status_var.set("✅ System detection completed successfully!")
            update_system_summary(self)
            create_system_display_handler(self)
        else:
            self.detection_status_var.set("❌ System detection failed")

    except Exception as e:
        self.detection_status_var.set(f"❌ Error during detection: {str(e)}")
        if DEBUG:
            print(f"System detection error: {e}")
    finally:
        self.detect_button.config(state="normal")


def create_system_display_handler(self):
    """Create compact system information display for three-column layout."""
    # Clear existing content
    for col in [
        self.system_left_column,
        self.system_middle_column,
        self.system_right_column,
    ]:
        for widget in col.winfo_children():
            widget.destroy()

    # LEFT COLUMN - CPU & Memory Information
    cpu_frame = ttk.LabelFrame(
        self.system_left_column, text="💻 CPU Information", padding=6
    )
    cpu_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))

    cpu_info = [
        ("Physical Cores:", f"{self.system_info_dict['cpu_physical_cores']}"),
        ("Logical Cores:", f"{self.system_info_dict['cpu_logical_cores']}"),
        (
            "CPU Model:",
            (
                self.system_info_dict["cpu_brand"][:30] + "..."
                if len(self.system_info_dict["cpu_brand"]) > 30
                else self.system_info_dict["cpu_brand"]
            ),
        ),
    ]

    for label, value in cpu_info:
        row_frame = ttk.Frame(cpu_frame)
        row_frame.pack(fill="x", pady=1)
        ttk.Label(row_frame, text=label, font=("Arial", 9, "bold"), width=12).pack(
            side="left", anchor="w"
        )
        ttk.Label(row_frame, text=value, font=("Arial", 9)).pack(
            side="left", padx=(5, 0)
        )

    # Memory section in left column
    memory_frame = ttk.LabelFrame(
        self.system_left_column, text="🧠 Memory Information", padding=6
    )
    memory_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    memory_info = [
        ("Total Memory:", f"{self.system_info_dict['memory_total_gb']:.1f} GB"),
        ("Available:", f"{self.system_info_dict['memory_available_gb']:.1f} GB"),
        (
            "Usage:",
            f"{((self.system_info_dict['memory_total_gb'] - self.system_info_dict['memory_available_gb']) / self.system_info_dict['memory_total_gb'] * 100):.1f}%",
        ),
    ]

    for label, value in memory_info:
        row_frame = ttk.Frame(memory_frame)
        row_frame.pack(fill="x", pady=1)
        ttk.Label(row_frame, text=label, font=("Arial", 9, "bold"), width=12).pack(
            side="left", anchor="w"
        )
        ttk.Label(row_frame, text=value, font=("Arial", 9)).pack(
            side="left", padx=(5, 0)
        )

    # MIDDLE COLUMN - GPU & Hardware Acceleration
    gpu_frame = ttk.LabelFrame(
        self.system_middle_column, text="🎮 GPU Information", padding=6
    )
    gpu_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))

    if self.system_info_dict["gpu_info"]:
        for i, gpu in enumerate(self.system_info_dict["gpu_info"]):
            gpu_short = gpu[:35] + "..." if len(gpu) > 35 else gpu
            ttk.Label(gpu_frame, text=f"GPU {i + 1}:", font=("Arial", 9, "bold")).pack(
                anchor="w"
            )
            ttk.Label(gpu_frame, text=gpu_short, font=("Arial", 8)).pack(
                anchor="w", padx=(10, 0)
            )
    else:
        ttk.Label(
            gpu_frame, text="No GPU detected", font=("Arial", 9), foreground="orange"
        ).pack(anchor="w")

    # Hardware acceleration in middle column
    hwaccel_frame = ttk.LabelFrame(
        self.system_middle_column, text="⚡ Hardware Acceleration", padding=6
    )
    hwaccel_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    if self.system_info_dict["hw_acceleration"]:
        ttk.Label(hwaccel_frame, text="Available:", font=("Arial", 9, "bold")).pack(
            anchor="w"
        )
        hwaccel_text = (
            ", ".join(self.system_info_dict["hw_acceleration"])[:40] + "..."
            if len(", ".join(self.system_info_dict["hw_acceleration"])) > 40
            else ", ".join(self.system_info_dict["hw_acceleration"])
        )
        ttk.Label(hwaccel_frame, text=hwaccel_text, font=("Arial", 8)).pack(
            anchor="w", padx=(10, 0)
        )

        if self.system_info_dict["preferred_hwaccel"]:
            ttk.Label(hwaccel_frame, text="Preferred:", font=("Arial", 9, "bold")).pack(
                anchor="w", pady=(3, 0)
            )
            ttk.Label(
                hwaccel_frame,
                text=self.system_info_dict["preferred_hwaccel"],
                font=("Arial", 9),
                foreground="green",
            ).pack(anchor="w", padx=(10, 0))
    else:
        ttk.Label(
            hwaccel_frame,
            text="Software encoding only",
            font=("Arial", 9),
            foreground="orange",
        ).pack(anchor="w")

    # RIGHT COLUMN - Performance & Settings
    settings_frame = ttk.LabelFrame(
        self.system_right_column, text="⚡ Optimal Settings", padding=6
    )
    settings_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))

    settings_info = [
        ("Optimal Threads:", f"{self.system_info_dict['optimal_threads']}"),
        ("Conservative:", f"{self.system_info_dict['conservative_threads']}"),
        ("Buffer Size:", self.system_info_dict["buffer_size"]),
        ("Mux Queue:", str(self.system_info_dict["mux_queue_size"])),
    ]

    for label, value in settings_info:
        row_frame = ttk.Frame(settings_frame)
        row_frame.pack(fill="x", pady=1)
        ttk.Label(row_frame, text=label, font=("Arial", 9, "bold"), width=11).pack(
            side="left", anchor="w"
        )
        ttk.Label(row_frame, text=value, font=("Arial", 9), foreground="green").pack(
            side="left", padx=(5, 0)
        )

    # Performance estimate in right column
    perf_frame = ttk.LabelFrame(
        self.system_right_column, text="📊 Performance Analysis", padding=6
    )
    perf_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    speed_improvement = self.system_info_dict["optimal_threads"] / 4

    perf_info = [
        ("Previous:", "4 threads"),
        ("New:", f"{self.system_info_dict['optimal_threads']} threads"),
        ("Speed Gain:", f"{speed_improvement:.1f}x faster"),
        ("HW Boost:", "Yes" if self.system_info_dict["preferred_hwaccel"] else "No"),
    ]

    for label, value in perf_info:
        row_frame = ttk.Frame(perf_frame)
        row_frame.pack(fill="x", pady=1)
        ttk.Label(row_frame, text=label, font=("Arial", 9, "bold"), width=11).pack(
            side="left", anchor="w"
        )
        color = "green" if "faster" in value or value == "Yes" else "black"
        ttk.Label(row_frame, text=value, font=("Arial", 9), foreground=color).pack(
            side="left", padx=(5, 0)
        )


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

    # Current file label
    current_file_label = ttk.Label(
        progress_frame,
        textvariable=self.current_file_var,
        font=("Arial", 9),
        foreground="blue",
    )
    current_file_label.grid(row=1, column=0, sticky="w", pady=(0, 2))

    # Status label
    status_label = ttk.Label(progress_frame, textvariable=self.status_var)
    status_label.grid(row=2, column=0, sticky="w")

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


def save_current_settings(self):
    """Save current GUI settings to file."""
    try:
        # Update app_settings from current GUI state
        self.app_settings.openai_api_key = self.openai_api_key_var.get()
        self.app_settings.ai_encoding_enabled = self.ai_encoding_var.get()

        # Only save manual settings if AI is not enabled
        if not self.ai_encoding_var.get():
            self.app_settings.video_codec = self.video_codec_var.get()
            self.app_settings.video_bitrate = self.video_bitrate_var.get()
            self.app_settings.resolution = self.resolution_var.get()
            self.app_settings.fps = self.fps_var.get()
            self.app_settings.crf = self.crf_var.get()
            self.app_settings.preset = self.preset_var.get()

            self.app_settings.audio_codec = self.audio_codec_var.get()
            self.app_settings.audio_bitrate = self.audio_bitrate_var.get()
            self.app_settings.audio_sample_rate = self.audio_sample_rate_var.get()
            self.app_settings.audio_channels = self.audio_channels_var.get()

        self.app_settings.output_format = self.output_format_var.get()
        self.app_settings.output_directory = self.output_dir_var.get()
        self.app_settings.maintain_structure = self.maintain_structure_var.get()
        self.app_settings.processing_mode = self.processing_mode.get()

        # Save to file
        if self.settings_manager.save_settings(self.app_settings):
            self.status_var.set("Settings saved successfully!")
            show_toast("Success", "Settings saved to configuration file!")
        else:
            self.status_var.set("Failed to save settings")
            show_toast("Error", "Failed to save settings")

    except Exception as e:
        self.status_var.set(f"Error saving settings: {str(e)}")
        print(f"Settings save error: {e}")


def load_saved_settings(self):
    """Load settings from file and apply to GUI."""
    try:
        if not self.settings_manager.settings_exist():
            self.status_var.set("No saved settings found")
            show_toast("Info", "No saved settings file found")
            return

        # Set loading flag to prevent auto-save during loading
        self._loading_settings = True

        # Load settings
        self.app_settings = self.settings_manager.load_settings()

        # Apply to GUI variables
        self.openai_api_key_var.set(self.app_settings.openai_api_key)
        self.ai_encoding_var.set(self.app_settings.ai_encoding_enabled)

        # Only load manual settings if AI is not enabled in saved settings
        if not self.app_settings.ai_encoding_enabled:
            self.video_codec_var.set(self.app_settings.video_codec)
            self.video_bitrate_var.set(self.app_settings.video_bitrate)
            self.resolution_var.set(self.app_settings.resolution)
            self.fps_var.set(self.app_settings.fps)
            self.crf_var.set(self.app_settings.crf)
            self.preset_var.set(self.app_settings.preset)

            self.audio_codec_var.set(self.app_settings.audio_codec)
            self.audio_bitrate_var.set(self.app_settings.audio_bitrate)
            self.audio_sample_rate_var.set(self.app_settings.audio_sample_rate)
            self.audio_channels_var.set(self.app_settings.audio_channels)

        self.output_format_var.set(self.app_settings.output_format)
        self.output_dir_var.set(self.app_settings.output_directory)
        self.maintain_structure_var.set(self.app_settings.maintain_structure)
        self.processing_mode.set(self.app_settings.processing_mode)

        # Update mode selection UI
        update_mode_selection(self)

        # Update CRF label if it exists
        if hasattr(self, "crf_label"):
            self.crf_label.configure(text=str(self.crf_var.get()))

        # Clear loading flag before triggering AI toggle
        self._loading_settings = False

        # Trigger AI toggle to update UI state
        on_ai_toggle_changed(self)

        self.status_var.set("Settings loaded successfully!")
        show_toast("Success", "Settings loaded from configuration file!")

    except Exception as e:
        self.status_var.set(f"Error loading settings: {str(e)}")
        print(f"Settings load error: {e}")
    finally:
        # Ensure loading flag is cleared
        self._loading_settings = False


def on_ai_toggle_changed(self):
    """Handle AI encoding toggle change."""
    if self.ai_encoding_var.get():
        # AI mode enabled - disable video and audio tabs, switch to output tab
        if self.notebook:
            # Disable video and audio tabs
            self.notebook.tab(0, state="disabled")  # Video tab
            self.notebook.tab(1, state="disabled")  # Audio tab
            # Switch to output tab
            self.notebook.select(2)  # Output tab

        # Set up AI analyzer with API key
        api_key = self.openai_api_key_var.get().strip()
        if api_key:
            self.ai_analyzer.set_api_key(api_key)

        self.status_var.set("AI Encoding enabled - settings will be auto-optimized")
    else:
        # AI mode disabled - re-enable all tabs
        if self.notebook:
            self.notebook.tab(0, state="normal")  # Video tab
            self.notebook.tab(1, state="normal")  # Audio tab

        self.status_var.set("Manual encoding mode - configure settings manually")

    # Auto-save settings when AI toggle changes (unless we're loading settings)
    if hasattr(self, "_loading_settings") and self._loading_settings:
        return
    if hasattr(self, "settings_manager"):
        save_current_settings(self)


def update_ai_encoding_settings(self, file_path):
    """Update encoding settings based on AI analysis."""
    if not self.ai_encoding_var.get() or not self.current_video_info:
        return

    try:
        self.status_var.set("AI analyzing video for optimal settings...")

        # Perform AI analysis
        analysis, optimized_settings = self.ai_analyzer.analyze_video(
            file_path, self.current_video_info
        )

        # Update encoding settings
        self.encoding_settings = optimized_settings

        # Update GUI displays (for output tab)
        self.video_codec_var.set(optimized_settings.video_codec)
        self.output_format_var.set(optimized_settings.output_format)

        # Show AI analysis results
        complexity_desc = {
            "low": "Low complexity - optimized for file size",
            "medium": "Medium complexity - balanced quality/size",
            "high": "High complexity - optimized for quality",
        }.get(analysis.motion_level, "Analyzed")

        self.status_var.set(
            f"AI Analysis: {complexity_desc} (CRF: {analysis.recommended_crf}, Preset: {analysis.recommended_preset})"
        )

    except Exception as e:
        self.status_var.set(f"AI Analysis failed: {str(e)} - using fallback settings")
        print(f"AI Analysis error: {e}")


def create_folder_browser_dialog(title="Select Folder", initial_dir=None):
    """Create a custom folder browser dialog that's larger and easier to use."""
    root = tk.Toplevel()
    root.title(title)
    root.geometry("800x600")
    root.grab_set()  # Make dialog modal
    root.resizable(True, True)

    selected_folder = None

    def on_select():
        nonlocal selected_folder
        selection = tree.selection()
        if selection:
            item = selection[0]
            selected_folder = (
                tree.item(item)["values"][0] if tree.item(item)["values"] else None
            )
        root.destroy()

    def on_cancel():
        nonlocal selected_folder
        selected_folder = None
        root.destroy()

    def on_double_click(event):
        on_select()

    # Create treeview for folder selection
    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(frame, show="tree")
    tree.pack(fill="both", expand=True)

    scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar_y.set)

    scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    scrollbar_x.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=scrollbar_x.set)

    # Populate tree with directories
    def populate_tree(parent, path):
        try:
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    node = tree.insert(
                        parent, "end", text=item, values=[item_path], open=False
                    )
                    # Add dummy child to show expand arrow
                    tree.insert(node, "end", text="Loading...", values=[])
        except PermissionError:
            pass

    def on_tree_expand(event):
        item = tree.focus()
        children = tree.get_children(item)
        if children and tree.item(children[0])["text"] == "Loading...":
            tree.delete(children[0])
            item_path = tree.item(item)["values"][0]
            populate_tree(item, item_path)

    # Start with home directory or provided initial directory
    start_dir = initial_dir or os.path.expanduser("~")
    root_node = tree.insert("", "end", text=start_dir, values=[start_dir], open=True)
    populate_tree(root_node, start_dir)

    tree.bind("<<TreeviewOpen>>", on_tree_expand)
    tree.bind("<Double-1>", on_double_click)

    # Buttons frame
    button_frame = ttk.Frame(root)
    button_frame.pack(fill="x", padx=10, pady=(0, 10))

    ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(
        side="right", padx=(5, 0)
    )
    ttk.Button(button_frame, text="Select", command=on_select).pack(side="right")

    # Center the dialog
    root.transient()
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (800 // 2)
    y = (root.winfo_screenheight() // 2) - (600 // 2)
    root.geometry(f"800x600+{x}+{y}")

    root.wait_window()
    return selected_folder


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
        # Use custom folder browser for better user experience
        folder_path = create_folder_browser_dialog(
            title="Select Video Folder", initial_dir=os.path.expanduser("~")
        )
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
    directory = create_folder_browser_dialog(
        title="Select Output Directory", initial_dir=os.path.expanduser("~")
    )
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

            # Trigger AI analysis if enabled (for preview only)
            # Note: Full AI analysis will happen during encoding
            if self.ai_encoding_var.get():
                self.status_var.set("AI mode enabled - will analyze during encoding")
                # Don't run analysis here to avoid double processing
                # update_ai_encoding_settings(self, file_path)
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


def toggle_resource_analytics(self):
    """Toggle Resource Usage Analytics on/off."""
    try:
        if self.resource_analytics_enabled.get():
            # Import and initialize resource analytics
            from resource_analytics import ResourceAnalytics

            if not self.resource_analytics:
                self.resource_analytics = ResourceAnalytics(self)

            # Update status
            self.analytics_status_label.configure(text="● Enabled", foreground="green")
            show_toast(
                self,
                "Resource Analytics Enabled",
                "Monitoring will start when encoding begins.",
            )

            if DEBUG:
                print("Resource analytics enabled")
        else:
            # Disable analytics
            if self.resource_analytics:
                self.resource_analytics.close_analytics_window()
                self.resource_analytics = None

            # Update status
            self.analytics_status_label.configure(text="● Disabled", foreground="red")
            show_toast(
                self, "Resource Analytics Disabled", "Monitoring has been stopped."
            )

            if DEBUG:
                print("Resource analytics disabled")

    except ImportError as e:
        # Handle missing dependencies
        self.resource_analytics_enabled.set(False)
        self.analytics_status_label.configure(
            text="● Error (Missing Dependencies)", foreground="red"
        )
        show_toast(
            self,
            "Dependencies Missing",
            "Please install: pip install matplotlib psutil",
        )
        if DEBUG:
            print(f"Resource analytics import error: {e}")
    except Exception as e:
        # Handle other errors
        self.resource_analytics_enabled.set(False)
        self.analytics_status_label.configure(text="● Error", foreground="red")
        show_toast(self, "Error", f"Failed to toggle analytics: {str(e)}")
        if DEBUG:
            print(f"Error toggling resource analytics: {e}")


def start_encoding(self):
    """Start the encoding process."""
    # IMMEDIATE UI feedback - disable button and show status FIRST
    self.start_btn.configure(state=DISABLED)
    self.stop_btn.configure(state="normal")
    self.status_var.set("Initializing encoding process...")

    # Force immediate UI update
    self.update()

    if not self.selected_files:
        messagebox.showwarning("No Files", "Please select files to encode.")
        # Re-enable button if validation fails
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state=DISABLED)
        return

    if not self.output_dir_var.get():
        messagebox.showwarning("No Output", "Please select output directory.")
        # Re-enable button if validation fails
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state=DISABLED)
        return

    # Update encoding settings from GUI
    update_encoding_settings_from_gui(self)

    # Refresh system information for optimal encoding settings
    try:
        self.status_var.set("Updating system information for optimal performance...")
        self.update()

        # Force refresh of system detection to get latest capabilities
        system_specs, optimal_settings = self.encoder.refresh_system_info()

        # Update system tab display if system info is available
        if system_specs and optimal_settings and hasattr(self, "system_info_dict"):
            self.system_info_dict = {
                "cpu_physical_cores": system_specs.cpu_cores_physical,
                "cpu_logical_cores": system_specs.cpu_cores_logical,
                "cpu_brand": system_specs.cpu_brand,
                "memory_total_gb": system_specs.memory_total_gb,
                "memory_available_gb": system_specs.memory_available_gb,
                "gpu_info": system_specs.gpu_info,
                "hw_acceleration": system_specs.hw_acceleration,
                "ffmpeg_encoders": system_specs.ffmpeg_encoders,
                "optimal_threads": optimal_settings.optimal_threads,
                "conservative_threads": optimal_settings.conservative_threads,
                "preferred_hwaccel": optimal_settings.preferred_hwaccel,
                "buffer_size": optimal_settings.buffer_size,
                "mux_queue_size": optimal_settings.mux_queue_size,
                "reasoning": optimal_settings.reasoning,
            }
            # Update system display with current info
            create_system_display_handler(self)

        self.status_var.set(
            f"System optimized - using {optimal_settings.optimal_threads if optimal_settings else 8} threads"
        )
        self.update()

    except Exception as e:
        print(f"DEBUG: System info update failed: {e}")
        self.status_var.set("Warning: Using default encoding settings")

    # Reset stop flag
    self.thread_manager.reset_stop_flag()

    # Start resource analytics monitoring if enabled
    if (
        hasattr(self, "resource_analytics_enabled")
        and self.resource_analytics_enabled.get()
        and hasattr(self, "resource_analytics")
        and self.resource_analytics
    ):
        try:
            self.status_var.set("Starting resource monitoring...")
            self.update()
            self.resource_analytics.start_monitoring()
            if DEBUG:
                print("Resource analytics monitoring started")
        except Exception as e:
            if DEBUG:
                print(f"Failed to start resource analytics: {e}")
            show_toast(self, "Analytics Warning", "Resource monitoring failed to start")

    print("DEBUG: Starting encoding thread...")

    # Start encoding in background thread using simple threading
    import threading

    def encoding_thread():
        try:
            print("DEBUG: Encoding thread started, calling encode_all_files...")
            success = encode_all_files(self)
            print(f"DEBUG: encode_all_files returned: {success}")
            # Update UI from main thread
            self.after(0, lambda: on_encoding_complete(self, success))
        except Exception as e:
            print(f"ERROR: Encoding thread error: {e}")
            import traceback

            traceback.print_exc()
            self.after(0, lambda: on_encoding_complete(self, False))

    thread = threading.Thread(target=encoding_thread, daemon=True)
    thread.start()
    print("DEBUG: Encoding thread started successfully")


def encode_all_files(self):
    """Encode all selected files."""
    total_files = len(self.selected_files)

    # Immediately update UI with file count and show we're starting
    self.after(0, lambda: self.status_var.set(f"Processing {total_files} file(s)..."))
    self.after(0, lambda: self.current_file_var.set("Preparing files for encoding..."))

    # Small delay to ensure UI updates are visible
    import time

    time.sleep(0.1)

    # Get the original base path for folder structure
    original_base_path = None
    if self.processing_mode.get() == "folder":
        original_base_path = self.selected_path_var.get()

    for i, file_path in enumerate(self.selected_files):
        # Check if stop was requested
        if self.thread_manager.stop_requested:
            self.after(0, lambda: self.current_file_var.set("Encoding stopped by user"))
            return False

        # Update current file display immediately
        file_name = os.path.basename(file_path)
        self.after(
            0, lambda fn=file_name: self.current_file_var.set(f"Processing: {fn}")
        )

        # Generate output path first to check for conflicts
        current_encoding_settings = self.encoding_settings
        output_path = self.encoder.get_output_path(
            file_path,
            self.output_dir_var.get(),
            current_encoding_settings,
            self.maintain_structure_var.get(),
            original_base_path,
        )

        # Check if output file already exists
        if os.path.exists(output_path):
            # Show immediate warning about file overwrite
            self.after(
                0,
                lambda: self.status_var.set(
                    f"Warning: Will overwrite existing file {os.path.basename(output_path)}"
                ),
            )
            print(f"DEBUG: Output file already exists: {output_path}")

        # Perform AI analysis if enabled
        if self.ai_encoding_var.get():
            try:
                # Show immediate status that AI analysis is starting
                self.after(
                    0,
                    lambda fn=file_name: self.status_var.set(
                        f"AI analyzing video: {fn}"
                    ),
                )
                self.after(
                    0, lambda: self.current_file_var.set("Loading video information...")
                )

                # Load video info for this file
                video_info = self.encoder.get_video_info(file_path)
                if video_info:
                    # Show video info immediately
                    self.after(
                        0,
                        lambda vi=video_info, fn=file_name: self.current_file_var.set(
                            f"Video: {fn} - {vi.width}x{vi.height} ({vi.duration:.1f}s)"
                        ),
                    )

                    # Update status before analysis
                    self.after(
                        0,
                        lambda fn=file_name: self.status_var.set(
                            f"AI optimizing encoding for {fn}..."
                        ),
                    )

                    # Perform AI analysis for this specific file
                    print(f"DEBUG: Starting AI analysis for {file_name}")

                    # Create progress callback for AI analysis
                    def ai_progress_callback(progress, status):
                        self.after(
                            0,
                            lambda p=progress, s=status: self.status_var.set(
                                f"AI Analysis: {s} ({p}%)"
                            ),
                        )
                        self.after(0, lambda p=progress: self.progress_var.set(p))

                    analysis, optimized_settings = self.ai_analyzer.analyze_video(
                        file_path, video_info, ai_progress_callback
                    )
                    current_encoding_settings = optimized_settings

                    # Debug output for AI results
                    print(f"DEBUG: AI Analysis Results for {file_name}:")
                    print(f"  - Complexity Score: {analysis.complexity_score}")
                    print(f"  - Motion Level: {analysis.motion_level}")
                    print(f"  - Recommended CRF: {analysis.recommended_crf}")
                    print(f"  - Recommended Preset: {analysis.recommended_preset}")
                    print(f"  - Has Fine Details: {analysis.has_fine_details}")
                    print(f"  - Has Grain: {analysis.has_grain}")

                    # Debug output for optimized settings
                    print("DEBUG: Optimized encoding settings:")
                    print(f"  - Video Codec: {optimized_settings.video_codec}")
                    print(f"  - CRF: {optimized_settings.crf}")
                    print(f"  - Preset: '{optimized_settings.preset}'")
                    print(f"  - Output Format: {optimized_settings.output_format}")

                    # Update status with AI analysis results
                    self.after(
                        0,
                        lambda a=analysis, fn=file_name: self.status_var.set(
                            f"AI optimized {fn}: CRF {a.recommended_crf}, {a.recommended_preset} preset"
                        ),
                    )
            except Exception as e:
                print(f"AI analysis failed for {file_name}: {e}")
                self.after(
                    0,
                    lambda fn=file_name: self.status_var.set(
                        f"AI analysis failed for {fn}, using default settings"
                    ),
                )
                # Continue with default settings

        # Update status before encoding starts
        self.after(
            0, lambda fn=file_name: self.status_var.set(f"Starting encode: {fn}")
        )

        # Encode file
        try:
            print(f"DEBUG: Starting encoding for {file_name}")
            success = self.encoder.encode_video(
                file_path,
                output_path,
                current_encoding_settings,
                progress_callback=lambda p, s: update_encoding_progress(
                    self, i, total_files, p, s
                ),
                stop_flag_callback=lambda: self.thread_manager.stop_requested,
            )
            print(f"DEBUG: Encoding result for {file_name}: {success}")
        except FileExistsError:
            error_msg = f"File already exists: {os.path.basename(output_path)}"
            print(f"ERROR: {error_msg}")
            self.after(
                0, lambda msg=error_msg: messagebox.showerror("File Exists", msg)
            )
            return False
        except PermissionError:
            error_msg = f"Permission denied writing to: {os.path.basename(output_path)}"
            print(f"ERROR: {error_msg}")
            self.after(
                0, lambda msg=error_msg: messagebox.showerror("Permission Error", msg)
            )
            return False
        except Exception as e:
            error_msg = f"Encoding failed for {file_name}: {str(e)}"
            print(f"ERROR: {error_msg}")
            import traceback

            traceback.print_exc()
            self.after(
                0, lambda msg=error_msg: messagebox.showerror("Encoding Error", msg)
            )
            return False

        # Check if stop was requested during encoding
        if self.thread_manager.stop_requested:
            print("DEBUG: Stop was requested during encoding")
            self.after(0, lambda: self.current_file_var.set("Encoding stopped by user"))
            return False

        if not success:
            print(f"DEBUG: Encoding failed for {file_name} - success was False")
            return False

    print("DEBUG: All files processed successfully, returning True")
    return True


def update_encoding_progress(self, current_file, total_files, file_progress, status):
    """Update encoding progress during encoding."""
    overall_progress = (current_file / total_files) * 100 + (
        file_progress / total_files
    )

    status_text = f"File {current_file + 1}/{total_files}: {status}"

    # Update UI in main thread using after()
    self.after(0, lambda: self.progress_var.set(overall_progress))
    self.after(0, lambda: self.status_var.set(status_text))


def update_progress(self, progress, status):
    """Update progress bar and status."""
    # Update UI in main thread using after()
    self.after(0, lambda: self.progress_var.set(progress))
    self.after(0, lambda: self.status_var.set(status))


def on_encoding_complete(self, success):
    """Handle encoding completion."""
    print(f"DEBUG: Encoding completed with success={success}")

    # Stop resource analytics monitoring
    if hasattr(self, "resource_analytics") and self.resource_analytics:
        self.resource_analytics.stop_monitoring_process()

    # Re-enable controls
    self.start_btn.configure(state="normal")
    self.stop_btn.configure(state=DISABLED)

    if success:
        self.status_var.set("Encoding completed successfully!")
        self.current_file_var.set("All files encoded successfully!")
        show_toast("Success", "All videos encoded successfully!")
    else:
        if self.thread_manager.stop_requested:
            self.status_var.set("Encoding stopped by user.")
            self.current_file_var.set("Encoding stopped by user")
            show_toast("Info", "Encoding stopped by user")
        else:
            self.status_var.set("Encoding failed or was interrupted.")
            self.current_file_var.set("Encoding failed - check logs for details")
            show_toast("Error", "Encoding failed - check console for details")

    self.progress_var.set(0)


def stop_encoding(self):
    """Stop the encoding process."""
    # Stop resource analytics monitoring
    if hasattr(self, "resource_analytics") and self.resource_analytics:
        self.resource_analytics.stop_monitoring_process()

    # Request stop from thread manager
    self.thread_manager.stop_current_operation()

    # Update UI immediately
    self.start_btn.configure(state="normal")
    self.stop_btn.configure(state=DISABLED)
    self.status_var.set("Stopping encoding...")
    self.current_file_var.set("Stopping...")


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
    self.current_file_var.set("")


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

    print("DEBUG: Updated encoding settings:")
    print(f"  Video Codec: {self.encoding_settings.video_codec}")
    print(f"  CRF: {self.encoding_settings.crf}")
    print(f"  Preset: {self.encoding_settings.preset}")
    print(f"  Output Format: {self.encoding_settings.output_format}")


def get_system_info_dict(self):
    """
    Get the system information dictionary for use by the encoder.

    Returns:
        dict: System information dictionary containing detected hardware specs
              and optimal encoding settings, or empty dict if not detected yet.
    """
    return getattr(self, "system_info_dict", {})


def is_system_detected(self):
    """
    Check if system detection has been performed.

    Returns:
        bool: True if system detection has been performed and data is available.
    """
    return bool(getattr(self, "system_info_dict", {}))


# Main function to initialize GUI
def main_ui(self):
    """Initialize the comprehensive encoder GUI - main entry point."""
    # Initialize the GUI
    create_main_gui(self)

    if DEBUG:
        print("ENCODER GUI INITIALIZED")
