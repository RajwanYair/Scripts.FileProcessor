#!/usr/bin/env python3
"""
hardware_detector.py

Advanced hardware detection and auto-tuning system for optimal performance.
Detects storage type (SSD/HDD/Network), GPU capabilities, and system resources.
"""

import logging
import os
import platform
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class HardwareProfile:
    """Complete hardware profile for performance optimization."""

    os_name: str
    cpu_count: int
    total_memory: int  # bytes
    storage_type: str | None  # 'ssd', 'hdd', 'network', 'unknown'
    network_fs: bool
    gpu_vendor: str  # 'nvidia', 'amd', 'intel', 'none'
    gpu_backend: str | None  # 'cupy', 'torch', 'opencl', 'directml', None
    gpu_vram_bytes: int
    gpu_device_count: int

    def __str__(self) -> str:
        storage = self.storage_type or "unknown"
        gpu_info = f"{self.gpu_vendor}"
        if self.gpu_vram_bytes > 0:
            gpu_info += f" ({self.gpu_vram_bytes // (1024**3)}GB)"
        return (
            f"OS: {self.os_name}, CPU: {self.cpu_count} cores, "
            f"RAM: {self.total_memory // (1024**3)}GB, "
            f"Storage: {storage}, GPU: {gpu_info}"
        )


@dataclass
class PerformanceProfile:
    """Optimized performance settings based on hardware."""

    max_workers: int
    io_buffer_size: int  # bytes
    hash_chunk_size: int  # bytes
    batch_size: int
    gpu_enabled: bool
    gpu_batch_size: int
    use_zero_copy: bool
    prefetch_enabled: bool

    def __str__(self) -> str:
        return (
            f"Workers: {self.max_workers}, "
            f"I/O Buffer: {self.io_buffer_size // (1024**2)}MB, "
            f"Hash Chunk: {self.hash_chunk_size // (1024**2)}MB, "
            f"GPU: {'enabled' if self.gpu_enabled else 'disabled'}"
        )


class HardwareDetector:
    """Advanced hardware detection with cross-platform support."""

    @staticmethod
    def detect_memory() -> int:
        """Detect total system memory in bytes."""
        try:
            import psutil

            return psutil.virtual_memory().total
        except ImportError:
            # Fallback methods
            if platform.system() == "Linux":
                try:
                    with open("/proc/meminfo") as f:
                        for line in f:
                            if line.startswith("MemTotal:"):
                                kb = int(line.split()[1])
                                return kb * 1024
                except Exception:
                    logger.debug("Failed to read /proc/meminfo", exc_info=True)
            elif platform.system() == "Windows":
                try:
                    import ctypes

                    class MEMORYSTATUSEX(ctypes.Structure):
                        _fields_ = [
                            ("dwLength", ctypes.c_ulong),
                            ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                        ]

                    memory_status = MEMORYSTATUSEX()
                    memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
                    return memory_status.ullTotalPhys
                except Exception:
                    logger.debug("Failed to query Windows memory via ctypes", exc_info=True)

            # Ultimate fallback - assume 8GB
            return 8 * 1024**3

    @staticmethod
    def _parse_proc_mounts() -> list[tuple[str, str, str]]:
        """Parse /proc/mounts on Linux."""
        mounts = []
        try:
            with open("/proc/mounts") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 3:
                        src, mnt, fstype = parts[0], parts[1], parts[2]
                        mounts.append((src, mnt, fstype))
        except Exception:
            logger.debug("Failed to parse /proc/mounts", exc_info=True)
        return mounts

    @staticmethod
    def _find_mount_point(path: Path) -> Path:
        """Find the mount point for a given path."""
        path = path.resolve()
        while not path.is_mount():
            parent = path.parent
            if parent == path:
                break
            path = parent
        return path

    @staticmethod
    def _block_device_from_path(device_path: str) -> str | None:
        """Extract block device name from device path."""
        if not device_path.startswith("/dev/"):
            return None
        name = os.path.basename(device_path)

        # Handle different device naming patterns
        # nvme: nvme0n1p1 -> nvme0n1
        if name.startswith("nvme"):
            match = re.match(r"(nvme\d+n\d+)", name)
            return match.group(1) if match else name

        # mmcblk: mmcblk0p1 -> mmcblk0
        if name.startswith("mmcblk"):
            match = re.match(r"(mmcblk\d+)", name)
            return match.group(1) if match else name

        # Standard drives: sda1 -> sda, vda1 -> vda
        return re.sub(r"\d+$", "", name)

    @staticmethod
    def detect_storage_type(path: Path) -> tuple[str | None, bool]:
        """
        Detect storage type and network filesystem.
        Returns (storage_type, is_network_fs)
        """
        os_name = platform.system().lower()

        if os_name == "linux":
            return HardwareDetector._detect_linux_storage(path)
        elif os_name == "windows":
            return HardwareDetector._detect_windows_storage(path)
        elif os_name == "darwin":
            return HardwareDetector._detect_macos_storage(path)
        else:
            return None, False

    @staticmethod
    def _detect_linux_storage(path: Path) -> tuple[str | None, bool]:
        """Linux-specific storage detection."""
        mounts = HardwareDetector._parse_proc_mounts()
        if not mounts:
            return None, False

        mount_point = HardwareDetector._find_mount_point(path)
        mount_str = str(mount_point)

        # Find matching mount entry
        device_path, fstype = None, None
        for src, mnt, fs in mounts:
            if mnt == mount_str:
                device_path, fstype = src, fs
                break

        # Check for network filesystem
        network_fs = False
        if fstype:
            fs_lower = fstype.lower()
            network_types = {"nfs", "nfs4", "cifs", "smbfs", "afpfs", "davfs", "sshfs"}
            if (
                fs_lower in network_types
                or fs_lower.startswith("fuse.")
                or fs_lower.startswith("nfs")
            ):
                network_fs = True

        # Detect SSD vs HDD using rotational flag
        storage_type = None
        if device_path and not network_fs:
            block_device = HardwareDetector._block_device_from_path(device_path)
            if block_device:
                rotational_file = Path(f"/sys/block/{block_device}/queue/rotational")
                try:
                    with open(rotational_file) as f:
                        rotational = f.read().strip()
                        if rotational == "0":
                            storage_type = "ssd"
                        elif rotational == "1":
                            storage_type = "hdd"
                except Exception:
                    # Try alternative detection methods
                    # Check if it's an NVMe drive (typically SSD)
                    if block_device.startswith("nvme"):
                        storage_type = "ssd"
                    # Check for SSD in device model name
                    try:
                        model_file = Path(f"/sys/block/{block_device}/device/model")
                        if model_file.exists():
                            with open(model_file) as f:
                                model = f.read().strip().lower()
                                if any(keyword in model for keyword in ["ssd", "solid", "nvme"]):
                                    storage_type = "ssd"
                    except Exception:
                        logger.debug("Failed to read device model for SSD detection", exc_info=True)

        if network_fs:
            storage_type = "network"

        return storage_type, network_fs

    @staticmethod
    def _detect_windows_storage(path: Path) -> tuple[str | None, bool]:
        """Windows-specific storage detection."""
        try:
            # Get drive letter
            drive = str(path).split(":")[0] + ":"

            # Use WMI to detect drive type
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f'Get-WmiObject -Class Win32_LogicalDisk | Where-Object {{$_.DeviceID -eq "{drive}"}} | Select-Object DriveType',
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if "3" in output:  # Fixed disk
                    # Try to detect SSD vs HDD
                    media_result = subprocess.run(
                        [
                            "powershell",
                            "-Command",
                            f'Get-PhysicalDisk | Where-Object {{$_.DeviceID -eq (Get-Partition -DriveLetter "{drive[0]}").DiskNumber}} | Select-Object MediaType',
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    if media_result.returncode == 0:
                        media_output = media_result.stdout.lower()
                        if "ssd" in media_output or "solid" in media_output:
                            return "ssd", False
                        elif "hdd" in media_output or "hard" in media_output:
                            return "hdd", False
                elif "4" in output:  # Network drive
                    return "network", True
        except Exception:
            logger.debug("Failed to detect Windows storage type", exc_info=True)

        return None, False

    @staticmethod
    def _detect_macos_storage(path: Path) -> tuple[str | None, bool]:
        """macOS-specific storage detection."""
        try:
            # Use diskutil to get disk info
            result = subprocess.run(
                ["diskutil", "info", str(path)], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                output = result.stdout.lower()
                if "solid state" in output or "ssd" in output:
                    return "ssd", False
                elif "rotational" in output or "hdd" in output:
                    return "hdd", False
                elif "network" in output or "mounted from" in output:
                    return "network", True
        except Exception:
            logger.debug("Failed to detect macOS storage type", exc_info=True)

        return None, False

    @staticmethod
    def detect_gpu_advanced() -> tuple[str, str | None, int, int]:
        """
        Advanced GPU detection with VRAM measurement.
        Returns (vendor, backend, vram_bytes, device_count)
        """
        vendor = "none"
        backend = None
        vram_bytes = 0
        device_count = 0

        # Check NVIDIA (highest priority)
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                device_count = len(lines)
                if device_count > 0:
                    vendor = "nvidia"
                    vram_bytes = int(lines[0]) * 1024 * 1024  # MB to bytes

                    # Check for CuPy
                    try:
                        import cupy  # noqa: F401

                        backend = "cupy"
                    except ImportError:
                        try:
                            import torch

                            if torch.cuda.is_available():
                                backend = "torch"
                        except ImportError:
                            pass
        except Exception:
            logger.debug("Failed to detect NVIDIA GPU", exc_info=True)

        # Check AMD (if no NVIDIA found)
        if vendor == "none":
            try:
                # Try ROCm
                result = subprocess.run(
                    ["rocm-smi", "--showmeminfo", "vram"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    vendor = "amd"
                    device_count = 1  # Simplified
                    vram_bytes = 8 * 1024**3  # Default assumption

                    # Check for PyTorch ROCm
                    try:
                        import torch

                        if torch.cuda.is_available():  # ROCm uses CUDA API
                            backend = "torch"
                    except ImportError:
                        pass

                    # Check for OpenCL
                    if backend is None:
                        try:
                            import pyopencl  # noqa: F401

                            backend = "opencl"
                        except ImportError:
                            pass
            except Exception:
                logger.debug("Failed to detect AMD GPU", exc_info=True)

        # Check Intel (if no discrete GPU found)
        if vendor == "none":
            try:
                # Check for Intel GPU via OpenCL
                import pyopencl as cl

                platforms = cl.get_platforms()
                for cl_platform in platforms:
                    if "intel" in cl_platform.name.lower():
                        vendor = "intel"
                        device_count = 1
                        vram_bytes = 4 * 1024**3  # Typical integrated GPU
                        backend = "opencl"
                        break
            except ImportError:
                pass

            # Check DirectML on Windows
            if vendor == "none" and platform.system() == "Windows":
                try:
                    import onnxruntime

                    providers = onnxruntime.get_available_providers()
                    if "DmlExecutionProvider" in providers:
                        vendor = "intel"  # Or could be AMD
                        device_count = 1
                        vram_bytes = 4 * 1024**3
                        backend = "directml"
                except ImportError:
                    pass

        return vendor, backend, vram_bytes, device_count

    @classmethod
    def detect_hardware(cls, reference_path: Path | None = None) -> HardwareProfile:
        """Detect complete hardware profile."""
        if reference_path is None:
            reference_path = Path.cwd()

        os_name = platform.system().lower()
        cpu_count = os.cpu_count() or 4
        total_memory = cls.detect_memory()

        storage_type, network_fs = cls.detect_storage_type(reference_path)
        gpu_vendor, gpu_backend, gpu_vram_bytes, gpu_device_count = cls.detect_gpu_advanced()

        return HardwareProfile(
            os_name=os_name,
            cpu_count=cpu_count,
            total_memory=total_memory,
            storage_type=storage_type,
            network_fs=network_fs,
            gpu_vendor=gpu_vendor,
            gpu_backend=gpu_backend,
            gpu_vram_bytes=gpu_vram_bytes,
            gpu_device_count=gpu_device_count,
        )


class PerformanceOptimizer:
    """Optimize performance settings based on hardware profile."""

    @staticmethod
    def optimize_for_hardware(
        hw: HardwareProfile, user_workers: int | None = None, enable_gpu: bool = True
    ) -> PerformanceProfile:
        """Generate optimized performance profile."""

        # Base settings
        max_workers = user_workers or max(2, min(32, hw.cpu_count + 2))
        io_buffer_size = 8 * 1024 * 1024  # 8MB default
        hash_chunk_size = 4 * 1024 * 1024  # 4MB default
        batch_size = 100
        gpu_enabled = False
        gpu_batch_size = 1000
        use_zero_copy = hw.os_name in ["linux", "darwin"]
        prefetch_enabled = True

        # Storage-specific optimizations
        if hw.network_fs:
            # Network storage: reduce workers and buffer sizes
            max_workers = max(2, min(8, hw.cpu_count // 2))
            io_buffer_size = 1 * 1024 * 1024  # 1MB
            hash_chunk_size = 1 * 1024 * 1024  # 1MB
            batch_size = 50
            prefetch_enabled = False
            use_zero_copy = False
        elif hw.storage_type == "ssd":
            # SSD: increase workers and buffer sizes
            max_workers = max(4, min(48, hw.cpu_count * 2))
            io_buffer_size = 16 * 1024 * 1024  # 16MB
            hash_chunk_size = 8 * 1024 * 1024  # 8MB
            batch_size = 200
        elif hw.storage_type == "hdd":
            # HDD: fewer workers, smaller buffers
            max_workers = max(2, min(12, hw.cpu_count))
            io_buffer_size = 2 * 1024 * 1024  # 2MB
            hash_chunk_size = 2 * 1024 * 1024  # 2MB
            batch_size = 50

        # Memory-based adjustments
        memory_gb = hw.total_memory // (1024**3)
        if memory_gb < 4:
            # Low memory: reduce buffer sizes
            io_buffer_size = min(io_buffer_size, 2 * 1024 * 1024)
            hash_chunk_size = min(hash_chunk_size, 2 * 1024 * 1024)
            batch_size = min(batch_size, 50)
        elif memory_gb >= 16:
            # High memory: increase buffer sizes
            io_buffer_size = max(io_buffer_size, 32 * 1024 * 1024)
            hash_chunk_size = max(hash_chunk_size, 16 * 1024 * 1024)
            batch_size = max(batch_size, 500)

        # GPU optimizations
        if enable_gpu and hw.gpu_vendor != "none" and hw.gpu_backend:
            gpu_enabled = True
            vram_gb = hw.gpu_vram_bytes // (1024**3)

            # Adjust GPU batch size based on VRAM
            if vram_gb >= 8:
                gpu_batch_size = 5000
            elif vram_gb >= 4:
                gpu_batch_size = 2000
            else:
                gpu_batch_size = 1000

        return PerformanceProfile(
            max_workers=max_workers,
            io_buffer_size=io_buffer_size,
            hash_chunk_size=hash_chunk_size,
            batch_size=batch_size,
            gpu_enabled=gpu_enabled,
            gpu_batch_size=gpu_batch_size,
            use_zero_copy=use_zero_copy,
            prefetch_enabled=prefetch_enabled,
        )


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("🔍 Detecting Hardware...")
    hw = HardwareDetector.detect_hardware()
    print(f"Hardware Profile: {hw}")

    print("\n⚡ Optimizing Performance...")
    perf = PerformanceOptimizer.optimize_for_hardware(hw)
    print(f"Performance Profile: {perf}")
