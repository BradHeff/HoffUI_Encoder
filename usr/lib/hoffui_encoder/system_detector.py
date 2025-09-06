"""
System Detection Module
Detects system capabilities for optimal encoding performance.
"""

import os
import subprocess
import psutil
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from Functions import DEBUG


@dataclass
class SystemSpecs:
    """Data class to hold system specifications."""

    # CPU Information
    cpu_cores_physical: int
    cpu_cores_logical: int
    cpu_brand: str
    cpu_frequency_max: float

    # Memory Information
    memory_total_gb: float
    memory_available_gb: float

    # Hardware Acceleration
    hw_acceleration: List[str]
    gpu_info: List[str]

    # FFmpeg Capabilities
    ffmpeg_encoders: List[str]
    ffmpeg_hwaccels: List[str]


@dataclass
class OptimalSettings:
    """Data class to hold optimal encoding settings."""

    # Threading
    optimal_threads: int
    conservative_threads: int
    max_threads: int

    # Hardware Acceleration
    preferred_hwaccel: Optional[str]
    hw_decoder: Optional[str]
    hw_encoder: Optional[str]

    # Performance Settings
    buffer_size: str
    mux_queue_size: int
    probe_size: str
    analyze_duration: str

    # Reasoning
    reasoning: str


class SystemDetector:
    """Detects system capabilities and calculates optimal encoding settings."""

    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            raise RuntimeError(
                "FFMPEG not found. Please install FFMPEG and add it to PATH."
            )

    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFMPEG executable in system PATH."""
        try:
            result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        # Try common paths
        common_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg",
            "ffmpeg",
        ]

        for path in common_paths:
            try:
                subprocess.run([path, "-version"], capture_output=True, timeout=5)
                return path
            except Exception:
                continue

        return None

    def detect_cpu_info(self) -> Dict:
        """Detect CPU information."""
        try:
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "max_frequency": 0.0,
                "brand": "Unknown",
            }

            # Get CPU frequency
            try:
                freq_info = psutil.cpu_freq()
                if freq_info:
                    cpu_info["max_frequency"] = (
                        freq_info.max or freq_info.current or 0.0
                    )
            except Exception:
                pass

            # Try to get CPU brand from /proc/cpuinfo on Linux
            try:
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            cpu_info["brand"] = line.split(":")[1].strip()
                            break
            except Exception:
                pass

            if DEBUG:
                print(
                    f"DEBUG: CPU Info - Physical: {cpu_info['physical_cores']}, "
                    f"Logical: {cpu_info['logical_cores']}, Brand: {cpu_info['brand']}"
                )

            return cpu_info

        except Exception as e:
            if DEBUG:
                print(f"DEBUG: Error detecting CPU info: {e}")
            return {
                "physical_cores": os.cpu_count() or 4,
                "logical_cores": os.cpu_count() or 4,
                "max_frequency": 0.0,
                "brand": "Unknown",
            }

    def detect_memory_info(self) -> Dict:
        """Detect memory information."""
        try:
            memory = psutil.virtual_memory()
            memory_info = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent_used": memory.percent,
            }

            if DEBUG:
                print(
                    f"DEBUG: Memory - Total: {memory_info['total_gb']}GB, "
                    f"Available: {memory_info['available_gb']}GB"
                )

            return memory_info

        except Exception as e:
            if DEBUG:
                print(f"DEBUG: Error detecting memory info: {e}")
            return {"total_gb": 8.0, "available_gb": 4.0, "percent_used": 50.0}

    def detect_gpu_info(self) -> List[str]:
        """Detect GPU information."""
        gpu_info = []

        try:
            # Try nvidia-smi for NVIDIA GPUs
            result = subprocess.run(
                ["nvidia-smi", "-L"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "GPU" in line:
                        gpu_info.append(f"NVIDIA {line}")
        except Exception:
            pass

        try:
            # Try lspci for general GPU detection
            result = subprocess.run(
                ["lspci", "-nn"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if any(
                        term in line.lower()
                        for term in ["vga", "gpu", "display", "graphics"]
                    ):
                        if "intel" in line.lower():
                            gpu_info.append(f"Intel {line.split(':')[-1].strip()}")
                        elif "amd" in line.lower():
                            gpu_info.append(f"AMD {line.split(':')[-1].strip()}")
                        elif "nvidia" not in line.lower():  # Avoid duplicates
                            gpu_info.append(line.split(":")[-1].strip())
        except Exception:
            pass

        if DEBUG and gpu_info:
            print(f"DEBUG: Detected GPUs: {gpu_info}")
        elif DEBUG:
            print("DEBUG: No GPU information detected")

        return gpu_info

    def detect_hardware_acceleration(self) -> List[str]:
        """Detect available hardware acceleration methods."""
        hw_accels = []

        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-hwaccels"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines[1:]:  # Skip header
                    line = line.strip()
                    if line and line != "Hardware acceleration methods:":
                        hw_accels.append(line)

            if DEBUG:
                print(f"DEBUG: Available hardware acceleration: {hw_accels}")

        except Exception as e:
            if DEBUG:
                print(f"DEBUG: Error detecting hardware acceleration: {e}")

        return hw_accels

    def detect_ffmpeg_encoders(self) -> List[str]:
        """Detect available FFmpeg encoders."""
        encoders = []

        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-encoders"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "libx264" in line:
                        encoders.append("libx264")
                    elif "libx265" in line:
                        encoders.append("libx265")
                    elif "h264_nvenc" in line:
                        encoders.append("h264_nvenc")
                    elif "hevc_nvenc" in line:
                        encoders.append("hevc_nvenc")
                    elif "h264_vaapi" in line:
                        encoders.append("h264_vaapi")
                    elif "hevc_vaapi" in line:
                        encoders.append("hevc_vaapi")
                    elif "h264_qsv" in line:
                        encoders.append("h264_qsv")
                    elif "hevc_qsv" in line:
                        encoders.append("hevc_qsv")

            if DEBUG:
                print(f"DEBUG: Available encoders: {encoders}")

        except Exception as e:
            if DEBUG:
                print(f"DEBUG: Error detecting encoders: {e}")
            # Default fallback
            encoders = ["libx264"]

        return encoders

    def get_system_specs(self) -> SystemSpecs:
        """Get complete system specifications."""
        cpu_info = self.detect_cpu_info()
        memory_info = self.detect_memory_info()
        gpu_info = self.detect_gpu_info()
        hw_accels = self.detect_hardware_acceleration()
        encoders = self.detect_ffmpeg_encoders()

        return SystemSpecs(
            cpu_cores_physical=cpu_info["physical_cores"],
            cpu_cores_logical=cpu_info["logical_cores"],
            cpu_brand=cpu_info["brand"],
            cpu_frequency_max=cpu_info["max_frequency"],
            memory_total_gb=memory_info["total_gb"],
            memory_available_gb=memory_info["available_gb"],
            hw_acceleration=hw_accels,
            gpu_info=gpu_info,
            ffmpeg_encoders=encoders,
            ffmpeg_hwaccels=hw_accels,
        )

    def calculate_optimal_settings(self, system_specs: SystemSpecs) -> OptimalSettings:
        """Calculate optimal encoding settings based on system specs."""

        # Threading calculations
        physical_cores = system_specs.cpu_cores_physical
        logical_cores = system_specs.cpu_cores_logical
        memory_gb = system_specs.memory_total_gb

        # Base threading strategy
        if physical_cores >= 16:  # High-end systems (16+ physical cores)
            optimal_threads = min(20, physical_cores)
            conservative_threads = min(12, physical_cores // 2)
        elif physical_cores >= 8:  # Mid-range systems (8-15 physical cores)
            optimal_threads = min(16, physical_cores + 2)
            conservative_threads = min(8, physical_cores // 2)
        elif physical_cores >= 4:  # Entry systems (4-7 physical cores)
            optimal_threads = min(8, physical_cores * 2)
            conservative_threads = min(6, physical_cores)
        else:  # Very low-end systems (1-3 physical cores)
            optimal_threads = min(4, logical_cores)
            conservative_threads = min(2, physical_cores)

        max_threads = logical_cores

        # Memory-based threading adjustment
        if memory_gb < 8:  # Low memory systems
            optimal_threads = min(optimal_threads, 6)
            conservative_threads = min(conservative_threads, 4)
        elif memory_gb > 32:  # High memory systems
            optimal_threads = min(optimal_threads + 4, logical_cores)

        # Hardware acceleration detection
        preferred_hwaccel = None
        hw_decoder = None
        hw_encoder = None

        # Priority: NVENC > VAAPI > QSV > Software
        if any("nvidia" in gpu.lower() for gpu in system_specs.gpu_info):
            if "cuda" in system_specs.hw_acceleration:
                preferred_hwaccel = "cuda"
                hw_decoder = "cuda"
            if "h264_nvenc" in system_specs.ffmpeg_encoders:
                hw_encoder = "h264_nvenc"
        elif "vaapi" in system_specs.hw_acceleration:
            preferred_hwaccel = "vaapi"
            hw_decoder = "vaapi"
            if "h264_vaapi" in system_specs.ffmpeg_encoders:
                hw_encoder = "h264_vaapi"
        elif "qsv" in system_specs.hw_acceleration:
            preferred_hwaccel = "qsv"
            hw_decoder = "qsv"
            if "h264_qsv" in system_specs.ffmpeg_encoders:
                hw_encoder = "h264_qsv"

        # Performance settings based on system capabilities
        if memory_gb >= 16:
            buffer_size = "200M"
            mux_queue_size = 2048
            probe_size = "200M"
            analyze_duration = "200M"
        elif memory_gb >= 8:
            buffer_size = "100M"
            mux_queue_size = 1024
            probe_size = "100M"
            analyze_duration = "100M"
        else:
            buffer_size = "50M"
            mux_queue_size = 512
            probe_size = "50M"
            analyze_duration = "50M"

        # Generate reasoning
        reasoning = f"""
System Analysis:
- CPU: {physical_cores} physical cores, {logical_cores} logical cores
- Memory: {memory_gb}GB total
- GPU: {', '.join(system_specs.gpu_info) if system_specs.gpu_info else 'Software only'}
- Hardware Acceleration: {preferred_hwaccel or 'None'}

Threading Strategy:
- Optimal: {optimal_threads} threads (for maximum performance)
- Conservative: {conservative_threads} threads (for stability fallback)
- Reasoning: Balanced for {'high-end' if physical_cores >= 16 else 'mid-range' if physical_cores >= 8 else 'entry-level'} system
        """.strip()

        return OptimalSettings(
            optimal_threads=optimal_threads,
            conservative_threads=conservative_threads,
            max_threads=max_threads,
            preferred_hwaccel=preferred_hwaccel,
            hw_decoder=hw_decoder,
            hw_encoder=hw_encoder,
            buffer_size=buffer_size,
            mux_queue_size=mux_queue_size,
            probe_size=probe_size,
            analyze_duration=analyze_duration,
            reasoning=reasoning,
        )

    def detect_and_optimize(self) -> Tuple[SystemSpecs, OptimalSettings]:
        """Detect system and return optimal settings."""
        print("🔍 Detecting system capabilities...")

        system_specs = self.get_system_specs()
        optimal_settings = self.calculate_optimal_settings(system_specs)

        if DEBUG:
            print("🖥️  System Detection Results:")
            print(
                f"   CPU: {system_specs.cpu_cores_physical} cores ({system_specs.cpu_brand})"
            )
            print(f"   Memory: {system_specs.memory_total_gb}GB")
            print(
                f"   GPU: {', '.join(system_specs.gpu_info) if system_specs.gpu_info else 'Software only'}"
            )
            print(
                f"   Hardware Acceleration: {', '.join(system_specs.hw_acceleration)}"
            )
            print(f"⚡ Optimal Threading: {optimal_settings.optimal_threads} threads")
            print(
                f"🛡️  Conservative Threading: {optimal_settings.conservative_threads} threads"
            )
            if optimal_settings.preferred_hwaccel:
                print(f"🚀 Hardware Acceleration: {optimal_settings.preferred_hwaccel}")

        return system_specs, optimal_settings
