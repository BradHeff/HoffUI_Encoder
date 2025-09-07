"""
Resource Analytics Module for HoffUI Encoder

Provides real-time system monitoring, FFmpeg process tracking,
and companion window visualization for resource usage analysis.
"""

import time
import threading
import ttkbootstrap as ttk
import psutil
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from Functions import DEBUG
from collections import deque
from datetime import datetime
from typing import Dict, List, Tuple

matplotlib.use("TkAgg")


class ResourceAnalytics:
    """Main resource analytics tracking class."""

    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.analytics_window = None
        self.is_monitoring = False
        self.monitoring_thread = None

        # Data storage (store last 60 data points for 1-minute history)
        self.max_data_points = 60
        self.cpu_data = deque(maxlen=self.max_data_points)
        self.memory_data = deque(maxlen=self.max_data_points)
        self.gpu_data = deque(maxlen=self.max_data_points)
        self.network_data = deque(maxlen=self.max_data_points)
        self.disk_data = deque(maxlen=self.max_data_points)
        self.timestamps = deque(maxlen=self.max_data_points)

        # FFmpeg specific monitoring
        self.ffmpeg_processes = []
        self.ffmpeg_cpu_data = deque(maxlen=self.max_data_points)
        self.ffmpeg_memory_data = deque(maxlen=self.max_data_points)

        # Threading control
        self.stop_monitoring = threading.Event()

        # Initialize matplotlib style
        style.use("default")
        plt.rcParams.update(
            {
                "font.size": 8,
                "axes.linewidth": 0.5,
                "lines.linewidth": 1.5,
            }
        )

    def get_window_position(self) -> Tuple[int, int, int, int]:
        """Get main window position and determine analytics window placement."""
        try:
            # Get main window geometry
            geometry = self.parent_window.geometry()
            # Parse geometry string: "widthxheight+x+y"
            size_pos = geometry.split("+")
            width_height = size_pos[0].split("x")

            main_width = int(width_height[0])
            main_height = int(width_height[1])
            main_x = int(size_pos[1]) if len(size_pos) > 1 else 0
            main_y = int(size_pos[2]) if len(size_pos) > 2 else 0

            # Get screen dimensions
            screen_width = self.parent_window.winfo_screenwidth()

            # Analytics window dimensions
            analytics_width = 400
            analytics_height = main_height

            # Determine placement (left or right of main window)
            if main_x < analytics_width + 50:  # Too close to left edge
                # Place to the right of main window
                analytics_x = main_x + main_width + 10
            else:
                # Place to the left of main window
                analytics_x = main_x - analytics_width - 10

            # Ensure analytics window doesn't go off screen
            if analytics_x + analytics_width > screen_width:
                analytics_x = screen_width - analytics_width - 10
            if analytics_x < 0:
                analytics_x = 10

            analytics_y = main_y  # Same Y position as main window

            return analytics_x, analytics_y, analytics_width, analytics_height

        except Exception as e:
            if DEBUG:
                print(f"Error calculating window position: {e}")
            # Fallback position
            return 100, 100, 400, 600

    def create_analytics_window(self):
        """Create the resource analytics window."""
        if self.analytics_window is not None:
            return

        # Calculate window position
        x, y, width, height = self.get_window_position()

        # Create analytics window
        self.analytics_window = ttk.Toplevel(self.parent_window)
        self.analytics_window.title("Resource Usage Analytics")
        self.analytics_window.geometry(f"{width}x{height}+{x}+{y}")
        self.analytics_window.resizable(True, True)

        # Make window stay on top and follow main window
        self.analytics_window.transient(self.parent_window)

        # Create main container with scrollable area
        main_frame = ttk.Frame(self.analytics_window)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create notebook for different analytics categories
        self.analytics_notebook = ttk.Notebook(main_frame)
        self.analytics_notebook.pack(fill="both", expand=True)

        # System Overview Tab
        self.create_system_overview_tab()

        # FFmpeg Processes Tab
        self.create_ffmpeg_tab()

        # Historical Data Tab
        self.create_historical_tab()

        # Bind window close event
        self.analytics_window.protocol("WM_DELETE_WINDOW", self.close_analytics_window)

        # Bind main window move events to update analytics window position
        self.parent_window.bind("<Configure>", self.on_main_window_configure)

    def create_system_overview_tab(self):
        """Create system overview tab with real-time metrics."""
        system_tab = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(system_tab, text="System Overview")

        # Create scrollable frame
        canvas = ttk.Canvas(system_tab)
        scrollbar = ttk.Scrollbar(system_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # CPU Usage Section
        cpu_frame = ttk.LabelFrame(scrollable_frame, text="CPU Usage", padding=10)
        cpu_frame.pack(fill="x", pady=(0, 10))

        self.cpu_percent_label = ttk.Label(
            cpu_frame, text="CPU: 0%", font=("Arial", 12, "bold")
        )
        self.cpu_percent_label.pack()

        self.cpu_progress = ttk.Progressbar(cpu_frame, mode="determinate", length=350)
        self.cpu_progress.pack(pady=5)

        # CPU Core breakdown
        self.cpu_cores_frame = ttk.Frame(cpu_frame)
        self.cpu_cores_frame.pack(fill="x", pady=5)
        self.cpu_core_labels = []
        self.cpu_core_bars = []

        # Memory Usage Section
        memory_frame = ttk.LabelFrame(scrollable_frame, text="Memory Usage", padding=10)
        memory_frame.pack(fill="x", pady=(0, 10))

        self.memory_label = ttk.Label(
            memory_frame, text="Memory: 0 GB / 0 GB (0%)", font=("Arial", 10)
        )
        self.memory_label.pack()

        self.memory_progress = ttk.Progressbar(
            memory_frame, mode="determinate", length=350
        )
        self.memory_progress.pack(pady=5)

        # Disk Usage Section
        disk_frame = ttk.LabelFrame(scrollable_frame, text="Disk Usage", padding=10)
        disk_frame.pack(fill="x", pady=(0, 10))

        self.disk_labels = {}
        self.disk_progress_bars = {}

        # Network Usage Section
        network_frame = ttk.LabelFrame(
            scrollable_frame, text="Network Usage", padding=10
        )
        network_frame.pack(fill="x", pady=(0, 10))

        self.network_sent_label = ttk.Label(
            network_frame, text="Sent: 0 MB/s", font=("Arial", 9)
        )
        self.network_sent_label.pack()

        self.network_recv_label = ttk.Label(
            network_frame, text="Received: 0 MB/s", font=("Arial", 9)
        )
        self.network_recv_label.pack()

        # GPU Usage Section (if available)
        gpu_frame = ttk.LabelFrame(scrollable_frame, text="GPU Usage", padding=10)
        gpu_frame.pack(fill="x", pady=(0, 10))

        self.gpu_labels = {}
        self.gpu_progress_bars = {}

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_ffmpeg_tab(self):
        """Create FFmpeg processes monitoring tab."""
        ffmpeg_tab = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(ffmpeg_tab, text="FFmpeg Processes")

        # Create main container
        main_container = ttk.Frame(ffmpeg_tab)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Process count label
        self.ffmpeg_count_label = ttk.Label(
            main_container,
            text="Active FFmpeg Processes: 0",
            font=("Arial", 12, "bold"),
        )
        self.ffmpeg_count_label.pack(pady=(0, 10))

        # Create treeview for process details
        columns = ("PID", "CPU%", "Memory", "Command")
        self.ffmpeg_tree = ttk.Treeview(
            main_container, columns=columns, show="headings", height=8
        )

        # Configure columns
        self.ffmpeg_tree.heading("PID", text="Process ID")
        self.ffmpeg_tree.heading("CPU%", text="CPU Usage")
        self.ffmpeg_tree.heading("Memory", text="Memory Usage")
        self.ffmpeg_tree.heading("Command", text="Command Line")

        self.ffmpeg_tree.column("PID", width=80)
        self.ffmpeg_tree.column("CPU%", width=80)
        self.ffmpeg_tree.column("Memory", width=100)
        self.ffmpeg_tree.column("Command", width=300)

        # Add scrollbar
        tree_scroll = ttk.Scrollbar(
            main_container, orient="vertical", command=self.ffmpeg_tree.yview
        )
        self.ffmpeg_tree.configure(yscrollcommand=tree_scroll.set)

        # Pack treeview and scrollbar
        tree_frame = ttk.Frame(main_container)
        tree_frame.pack(fill="both", expand=True)

        self.ffmpeg_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        # FFmpeg aggregate stats
        stats_frame = ttk.LabelFrame(
            main_container, text="Aggregate FFmpeg Usage", padding=10
        )
        stats_frame.pack(fill="x", pady=(10, 0))

        stats_container = ttk.Frame(stats_frame)
        stats_container.pack(fill="x")

        # Total CPU usage by FFmpeg
        left_stats = ttk.Frame(stats_container)
        left_stats.pack(side="left", fill="both", expand=True)

        self.ffmpeg_cpu_total_label = ttk.Label(left_stats, text="Total FFmpeg CPU: 0%")
        self.ffmpeg_cpu_total_label.pack()

        self.ffmpeg_cpu_progress = ttk.Progressbar(
            left_stats, mode="determinate", length=180
        )
        self.ffmpeg_cpu_progress.pack(pady=2)

        # Total Memory usage by FFmpeg
        right_stats = ttk.Frame(stats_container)
        right_stats.pack(side="right", fill="both", expand=True)

        self.ffmpeg_memory_total_label = ttk.Label(
            right_stats, text="Total FFmpeg Memory: 0 MB"
        )
        self.ffmpeg_memory_total_label.pack()

        self.ffmpeg_memory_progress = ttk.Progressbar(
            right_stats, mode="determinate", length=180
        )
        self.ffmpeg_memory_progress.pack(pady=2)

    def create_historical_tab(self):
        """Create historical data visualization tab."""
        historical_tab = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(historical_tab, text="Historical Data")

        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 10), dpi=80, facecolor="white")
        self.fig.suptitle(
            "Resource Usage History (Last 60 seconds)", fontsize=12, fontweight="bold"
        )

        # Create subplots
        self.ax1 = self.fig.add_subplot(411)  # CPU
        self.ax2 = self.fig.add_subplot(412)  # Memory
        self.ax3 = self.fig.add_subplot(413)  # Network
        self.ax4 = self.fig.add_subplot(414)  # FFmpeg specific

        # Configure subplots
        self.ax1.set_title("CPU Usage (%)", fontsize=10)
        self.ax1.set_ylabel("CPU %")
        self.ax1.set_ylim(0, 100)
        self.ax1.grid(True, alpha=0.3)

        self.ax2.set_title("Memory Usage (%)", fontsize=10)
        self.ax2.set_ylabel("Memory %")
        self.ax2.set_ylim(0, 100)
        self.ax2.grid(True, alpha=0.3)

        self.ax3.set_title("Network I/O (MB/s)", fontsize=10)
        self.ax3.set_ylabel("MB/s")
        self.ax3.grid(True, alpha=0.3)

        self.ax4.set_title("FFmpeg Resource Usage", fontsize=10)
        self.ax4.set_ylabel("Usage %")
        self.ax4.set_xlabel("Time (seconds ago)")
        self.ax4.grid(True, alpha=0.3)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, historical_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # Initialize empty plots
        (self.cpu_line,) = self.ax1.plot([], [], "b-", label="CPU Usage")
        (self.memory_line,) = self.ax2.plot([], [], "g-", label="Memory Usage")
        (self.network_sent_line,) = self.ax3.plot([], [], "r-", label="Sent")
        (self.network_recv_line,) = self.ax3.plot([], [], "orange", label="Received")
        (self.ffmpeg_cpu_line,) = self.ax4.plot([], [], "m-", label="FFmpeg CPU")
        (self.ffmpeg_memory_line,) = self.ax4.plot([], [], "c-", label="FFmpeg Memory")

        # Add legends
        self.ax1.legend(loc="upper right", fontsize=8)
        self.ax2.legend(loc="upper right", fontsize=8)
        self.ax3.legend(loc="upper right", fontsize=8)
        self.ax4.legend(loc="upper right", fontsize=8)

    def start_monitoring(self):
        """Start resource monitoring."""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.stop_monitoring.clear()

        # Create analytics window
        self.create_analytics_window()

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()

        if DEBUG:
            print("Resource monitoring started")

    def stop_monitoring_process(self):
        """Stop resource monitoring."""
        self.is_monitoring = False
        self.stop_monitoring.set()

        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)

        if DEBUG:
            print("Resource monitoring stopped")

    def close_analytics_window(self):
        """Close analytics window and stop monitoring."""
        self.stop_monitoring_process()

        if self.analytics_window:
            self.analytics_window.destroy()
            self.analytics_window = None

    def on_main_window_configure(self, event):
        """Handle main window move/resize events."""
        if self.analytics_window and event.widget == self.parent_window:
            # Update analytics window position to follow main window
            try:
                x, y, width, height = self.get_window_position()
                self.analytics_window.geometry(f"{width}x{height}+{x}+{y}")
            except Exception as e:
                if DEBUG:
                    print(f"Error updating analytics window position: {e}")

    def _monitoring_loop(self):
        """Main monitoring loop running in separate thread."""
        network_io_prev = psutil.net_io_counters()

        while not self.stop_monitoring.is_set():
            try:
                current_time = datetime.now()

                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()

                # Network I/O
                network_io = psutil.net_io_counters()
                network_sent_speed = (
                    (network_io.bytes_sent - network_io_prev.bytes_sent) / 1024 / 1024
                )  # MB/s
                network_recv_speed = (
                    (network_io.bytes_recv - network_io_prev.bytes_recv) / 1024 / 1024
                )  # MB/s
                network_io_prev = network_io

                # FFmpeg processes
                ffmpeg_processes = self._get_ffmpeg_processes()
                ffmpeg_cpu_total = sum(proc["cpu_percent"] for proc in ffmpeg_processes)
                ffmpeg_memory_total = sum(
                    proc["memory_mb"] for proc in ffmpeg_processes
                )

                # Store data
                self.timestamps.append(current_time)
                self.cpu_data.append(cpu_percent)
                self.memory_data.append(memory.percent)
                self.network_data.append(
                    {"sent": network_sent_speed, "recv": network_recv_speed}
                )
                self.ffmpeg_cpu_data.append(ffmpeg_cpu_total)
                self.ffmpeg_memory_data.append(ffmpeg_memory_total)

                # Update GUI (schedule on main thread)
                if self.analytics_window:
                    self.analytics_window.after(
                        0,
                        self._update_gui_metrics,
                        {
                            "cpu_percent": cpu_percent,
                            "memory": memory,
                            "network_sent": network_sent_speed,
                            "network_recv": network_recv_speed,
                            "ffmpeg_processes": ffmpeg_processes,
                            "ffmpeg_cpu_total": ffmpeg_cpu_total,
                            "ffmpeg_memory_total": ffmpeg_memory_total,
                        },
                    )

                # Sleep for 1 second
                time.sleep(1.0)

            except Exception as e:
                if DEBUG:
                    print(f"Error in monitoring loop: {e}")
                time.sleep(1.0)

    def _get_ffmpeg_processes(self) -> List[Dict]:
        """Get information about running FFmpeg processes."""
        ffmpeg_processes = []

        try:
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_info", "cmdline"]
            ):
                try:
                    if proc.info["name"] and "ffmpeg" in proc.info["name"].lower():
                        memory_mb = (
                            proc.info["memory_info"].rss / 1024 / 1024
                            if proc.info["memory_info"]
                            else 0
                        )

                        ffmpeg_processes.append(
                            {
                                "pid": proc.info["pid"],
                                "cpu_percent": proc.info["cpu_percent"] or 0,
                                "memory_mb": memory_mb,
                                "cmdline": (
                                    " ".join(proc.info["cmdline"][:3]) + "..."
                                    if proc.info["cmdline"]
                                    else "N/A"
                                ),
                            }
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            if DEBUG:
                print(f"Error getting FFmpeg processes: {e}")

        return ffmpeg_processes

    def _update_gui_metrics(self, metrics):
        """Update GUI with current metrics (called on main thread)."""
        try:
            # Update system overview
            self._update_system_overview(metrics)

            # Update FFmpeg tab
            self._update_ffmpeg_tab(metrics)

            # Update historical charts
            self._update_historical_charts()

        except Exception as e:
            if DEBUG:
                print(f"Error updating GUI metrics: {e}")

    def _update_system_overview(self, metrics):
        """Update system overview tab."""
        try:
            # CPU
            cpu_percent = metrics["cpu_percent"]
            self.cpu_percent_label.configure(text=f"CPU: {cpu_percent:.1f}%")
            self.cpu_progress["value"] = cpu_percent

            # CPU cores
            cpu_cores = psutil.cpu_percent(percpu=True)
            self._update_cpu_cores(cpu_cores)

            # Memory
            memory = metrics["memory"]
            memory_gb_used = memory.used / 1024 / 1024 / 1024
            memory_gb_total = memory.total / 1024 / 1024 / 1024
            self.memory_label.configure(
                text=f"Memory: {memory_gb_used:.1f} GB / {memory_gb_total:.1f} GB ({memory.percent:.1f}%)"
            )
            self.memory_progress["value"] = memory.percent

            # Network
            self.network_sent_label.configure(
                text=f"Sent: {metrics['network_sent']:.2f} MB/s"
            )
            self.network_recv_label.configure(
                text=f"Received: {metrics['network_recv']:.2f} MB/s"
            )

            # Disk usage
            self._update_disk_usage()

            # GPU usage (if available)
            self._update_gpu_usage()

        except Exception as e:
            if DEBUG:
                print(f"Error updating system overview: {e}")

    def _update_cpu_cores(self, cpu_cores):
        """Update CPU core usage display."""
        try:
            # Clear existing core displays
            for widget in self.cpu_cores_frame.winfo_children():
                widget.destroy()

            self.cpu_core_labels.clear()
            self.cpu_core_bars.clear()

            # Create new core displays (max 8 to avoid overcrowding)
            cores_to_show = min(len(cpu_cores), 8)
            cols = 4
            rows = (cores_to_show + cols - 1) // cols  # noqa

            for i in range(cores_to_show):
                row = i // cols
                col = i % cols

                core_frame = ttk.Frame(self.cpu_cores_frame)
                core_frame.grid(row=row, column=col, padx=2, pady=1, sticky="ew")

                label = ttk.Label(
                    core_frame, text=f"Core {i}: {cpu_cores[i]:.0f}%", font=("Arial", 8)
                )
                label.pack()

                progress = ttk.Progressbar(core_frame, mode="determinate", length=80)
                progress.pack()
                progress["value"] = cpu_cores[i]

                self.cpu_core_labels.append(label)
                self.cpu_core_bars.append(progress)

            # Configure grid weights
            for col in range(cols):
                self.cpu_cores_frame.columnconfigure(col, weight=1)

        except Exception as e:
            if DEBUG:
                print(f"Error updating CPU cores: {e}")

    def _update_disk_usage(self):
        """Update disk usage display."""
        try:
            disk_partitions = psutil.disk_partitions()

            # Clear existing disk displays
            for widget in self.disk_labels.values():
                widget.destroy()
            for widget in self.disk_progress_bars.values():
                widget.destroy()

            self.disk_labels.clear()
            self.disk_progress_bars.clear()

            # Get parent frame (disk_frame)
            disk_frame = None
            for child in self.analytics_window.winfo_children():
                if isinstance(child, ttk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.Canvas):
                            canvas_frame = grandchild.winfo_children()[0]
                            for ggchild in canvas_frame.winfo_children():
                                if isinstance(
                                    ggchild, ttk.LabelFrame
                                ) and "Disk Usage" in str(ggchild):
                                    disk_frame = ggchild
                                    break

            if not disk_frame:
                return

            # Add disk usage for each partition
            for i, partition in enumerate(disk_partitions[:3]):  # Limit to 3 partitions
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    used_gb = usage.used / 1024 / 1024 / 1024
                    total_gb = usage.total / 1024 / 1024 / 1024
                    percent = (usage.used / usage.total) * 100

                    label = ttk.Label(
                        disk_frame,
                        text=f"{partition.device}: {used_gb:.1f} GB / {total_gb:.1f} GB ({percent:.1f}%)",
                        font=("Arial", 8),
                    )
                    label.pack()

                    progress = ttk.Progressbar(
                        disk_frame, mode="determinate", length=300
                    )
                    progress.pack(pady=2)
                    progress["value"] = percent

                    self.disk_labels[partition.device] = label
                    self.disk_progress_bars[partition.device] = progress

                except (PermissionError, FileNotFoundError):
                    continue

        except Exception as e:
            if DEBUG:
                print(f"Error updating disk usage: {e}")

    def _update_gpu_usage(self):
        """Update GPU usage display (if available)."""
        try:
            # This would require nvidia-ml-py for NVIDIA GPUs
            # For now, we'll just show a placeholder
            pass
        except Exception as e:
            if DEBUG:
                print(f"Error updating GPU usage: {e}")

    def _update_ffmpeg_tab(self, metrics):
        """Update FFmpeg processes tab."""
        try:
            # Update process count
            ffmpeg_processes = metrics["ffmpeg_processes"]
            self.ffmpeg_count_label.configure(
                text=f"Active FFmpeg Processes: {len(ffmpeg_processes)}"
            )

            # Clear existing items
            for item in self.ffmpeg_tree.get_children():
                self.ffmpeg_tree.delete(item)

            # Add current processes
            for proc in ffmpeg_processes:
                self.ffmpeg_tree.insert(
                    "",
                    "end",
                    values=(
                        proc["pid"],
                        f"{proc['cpu_percent']:.1f}%",
                        f"{proc['memory_mb']:.1f} MB",
                        proc["cmdline"],
                    ),
                )

            # Update aggregate stats
            ffmpeg_cpu_total = metrics["ffmpeg_cpu_total"]
            ffmpeg_memory_total = metrics["ffmpeg_memory_total"]

            self.ffmpeg_cpu_total_label.configure(
                text=f"Total FFmpeg CPU: {ffmpeg_cpu_total:.1f}%"
            )
            self.ffmpeg_cpu_progress["value"] = min(ffmpeg_cpu_total, 100)

            self.ffmpeg_memory_total_label.configure(
                text=f"Total FFmpeg Memory: {ffmpeg_memory_total:.1f} MB"
            )
            # Set memory progress as percentage of total system memory
            memory_percent = (
                ffmpeg_memory_total / (psutil.virtual_memory().total / 1024 / 1024)
            ) * 100
            self.ffmpeg_memory_progress["value"] = min(memory_percent, 100)

        except Exception as e:
            if DEBUG:
                print(f"Error updating FFmpeg tab: {e}")

    def _update_historical_charts(self):
        """Update historical data charts."""
        try:
            if len(self.timestamps) < 2:
                return

            # Create time axis (seconds ago)
            now = datetime.now()
            time_axis = [(now - ts).total_seconds() for ts in self.timestamps]
            time_axis.reverse()  # Show most recent on right

            # Update CPU chart
            cpu_data_reversed = list(reversed(self.cpu_data))
            self.cpu_line.set_data(time_axis, cpu_data_reversed)
            self.ax1.set_xlim(0, max(time_axis) if time_axis else 60)
            self.ax1.relim()
            self.ax1.autoscale_view()

            # Update Memory chart
            memory_data_reversed = list(reversed(self.memory_data))
            self.memory_line.set_data(time_axis, memory_data_reversed)
            self.ax2.set_xlim(0, max(time_axis) if time_axis else 60)
            self.ax2.relim()
            self.ax2.autoscale_view()

            # Update Network chart
            network_sent = [data["sent"] for data in reversed(self.network_data)]
            network_recv = [data["recv"] for data in reversed(self.network_data)]
            self.network_sent_line.set_data(time_axis, network_sent)
            self.network_recv_line.set_data(time_axis, network_recv)
            self.ax3.set_xlim(0, max(time_axis) if time_axis else 60)
            self.ax3.relim()
            self.ax3.autoscale_view()

            # Update FFmpeg chart
            ffmpeg_cpu_reversed = list(reversed(self.ffmpeg_cpu_data))
            ffmpeg_memory_reversed = list(reversed(self.ffmpeg_memory_data))
            # Normalize memory to percentage of total system memory
            total_memory_mb = psutil.virtual_memory().total / 1024 / 1024
            ffmpeg_memory_percent = [
                (mem / total_memory_mb) * 100 for mem in ffmpeg_memory_reversed
            ]

            self.ffmpeg_cpu_line.set_data(time_axis, ffmpeg_cpu_reversed)
            self.ffmpeg_memory_line.set_data(time_axis, ffmpeg_memory_percent)
            self.ax4.set_xlim(0, max(time_axis) if time_axis else 60)
            self.ax4.relim()
            self.ax4.autoscale_view()

            # Redraw canvas
            self.canvas.draw_idle()

        except Exception as e:
            if DEBUG:
                print(f"Error updating historical charts: {e}")
