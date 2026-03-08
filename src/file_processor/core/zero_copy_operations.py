#!/usr/bin/env python3
"""
zero_copy_operations.py

High-performance file operations with zero-copy techniques and platform-specific optimizations.
Supports Linux FICLONE, macOS clonefile, copy_file_range, sendfile, and optimized buffered copy.
"""

import logging
import os
import platform
import shutil
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class ZeroCopyOperations:
    """High-performance file operations with zero-copy optimizations."""

    def __init__(self, io_buffer_size: int = 8 * 1024 * 1024):
        self.os_name = platform.system().lower()
        self.io_buffer_size = io_buffer_size

        # Check for available zero-copy methods
        self.has_reflink = self._check_reflink_support()
        self.has_clonefile = self._check_clonefile_support()
        self.has_copy_file_range = self._check_copy_file_range_support()
        self.has_sendfile = self._check_sendfile_support()

        logger.debug(
            f"Zero-copy capabilities: reflink={self.has_reflink}, "
            f"clonefile={self.has_clonefile}, copy_file_range={self.has_copy_file_range}, "
            f"sendfile={self.has_sendfile}"
        )

    def _check_reflink_support(self) -> bool:
        """Check if Linux FICLONE reflink is available."""
        if self.os_name != "linux":
            return False
        try:
            import fcntl

            return hasattr(fcntl, "FICLONE") or True  # FICLONE might not be in fcntl constants
        except ImportError:
            return False

    def _check_clonefile_support(self) -> bool:
        """Check if macOS clonefile is available."""
        if self.os_name != "darwin":
            return False
        try:
            from ctypes import cdll

            libc = cdll.LoadLibrary("libSystem.dylib")
            return hasattr(libc, "clonefile")
        except Exception:
            return False

    def _check_copy_file_range_support(self) -> bool:
        """Check if copy_file_range is available (Linux 4.5+)."""
        return hasattr(os, "copy_file_range")

    def _check_sendfile_support(self) -> bool:
        """Check if sendfile is available (Linux/macOS)."""
        return hasattr(os, "sendfile")

    def same_filesystem(self, src: Path, dst: Path) -> bool:
        """Check if two paths are on the same filesystem."""
        try:
            src_stat = src.stat()
            dst_parent = dst.parent
            dst_parent.mkdir(parents=True, exist_ok=True)
            dst_stat = dst_parent.stat()
            return src_stat.st_dev == dst_stat.st_dev
        except Exception:
            # Fallback: check if they have the same drive/mount point
            try:
                return src.anchor == dst.anchor
            except Exception:
                return False

    def try_reflink_copy(self, src: Path, dst: Path) -> bool:
        """
        Attempt copy using Linux FICLONE ioctl (reflink/COW copy).
        This creates a copy-on-write clone that shares blocks until modified.
        """
        if not self.has_reflink:
            return False

        try:
            import fcntl

            # FICLONE ioctl constant (might not be in fcntl module)
            ficlone = getattr(fcntl, "FICLONE", 0x40049409)

            with open(src, "rb") as src_file, open(dst, "wb") as dst_file:
                fcntl.ioctl(dst_file.fileno(), ficlone, src_file.fileno())

            # Copy metadata
            shutil.copystat(src, dst, follow_symlinks=True)
            logger.debug(f"Reflink copy successful: {src} -> {dst}")
            return True

        except Exception as e:
            logger.debug(f"Reflink copy failed: {e}")
            return False

    def try_clonefile_copy(self, src: Path, dst: Path) -> bool:
        """
        Attempt copy using macOS clonefile() system call.
        Creates a copy-on-write clone on APFS filesystems.
        """
        if not self.has_clonefile:
            return False

        try:
            from ctypes import c_char_p, c_int, cdll

            libc = cdll.LoadLibrary("libSystem.dylib")
            clonefile = libc.clonefile
            clonefile.argtypes = [c_char_p, c_char_p, c_int]
            clonefile.restype = c_int

            src_bytes = str(src).encode("utf-8")
            dst_bytes = str(dst).encode("utf-8")

            result = clonefile(src_bytes, dst_bytes, 0)

            if result == 0:
                logger.debug(f"Clonefile copy successful: {src} -> {dst}")
                return True
            else:
                logger.debug(f"Clonefile copy failed with code: {result}")
                return False

        except Exception as e:
            logger.debug(f"Clonefile copy failed: {e}")
            return False

    def try_copy_file_range(self, src: Path, dst: Path) -> bool:
        """
        Attempt copy using copy_file_range() system call (Linux 4.5+).
        Performs server-side copy when possible, avoiding userspace buffers.
        """
        if not self.has_copy_file_range:
            return False

        try:
            file_size = src.stat().st_size
            bytes_copied = 0

            with open(src, "rb") as src_file, open(dst, "wb") as dst_file:
                src_fd = src_file.fileno()
                dst_fd = dst_file.fileno()

                while bytes_copied < file_size:
                    remaining = file_size - bytes_copied
                    chunk_size = min(self.io_buffer_size, remaining)

                    copied = os.copy_file_range(src_fd, dst_fd, chunk_size)
                    if copied == 0:
                        break

                    bytes_copied += copied

            if bytes_copied == file_size:
                # Copy metadata
                shutil.copystat(src, dst, follow_symlinks=True)
                logger.debug(f"copy_file_range successful: {src} -> {dst}")
                return True
            else:
                logger.debug(f"copy_file_range incomplete: {bytes_copied}/{file_size} bytes")
                return False

        except Exception as e:
            logger.debug(f"copy_file_range failed: {e}")
            return False

    def try_sendfile_copy(self, src: Path, dst: Path) -> bool:
        """
        Attempt copy using sendfile() system call.
        Efficient kernel-space copying without userspace buffers.
        """
        if not self.has_sendfile:
            return False

        try:
            file_size = src.stat().st_size
            bytes_copied = 0

            with open(src, "rb") as src_file, open(dst, "wb") as dst_file:
                src_fd = src_file.fileno()
                dst_fd = dst_file.fileno()

                while bytes_copied < file_size:
                    remaining = file_size - bytes_copied
                    chunk_size = min(self.io_buffer_size, remaining)

                    copied = os.sendfile(dst_fd, src_fd, bytes_copied, chunk_size)
                    if copied == 0:
                        break

                    bytes_copied += copied

            if bytes_copied == file_size:
                # Copy metadata
                shutil.copystat(src, dst, follow_symlinks=True)
                logger.debug(f"sendfile copy successful: {src} -> {dst}")
                return True
            else:
                logger.debug(f"sendfile incomplete: {bytes_copied}/{file_size} bytes")
                return False

        except Exception as e:
            logger.debug(f"sendfile failed: {e}")
            return False

    def optimized_buffered_copy(self, src: Path, dst: Path) -> bool:
        """
        Optimized buffered copy with platform-specific optimizations.
        Uses large buffers and unbuffered I/O for better performance.
        """
        try:
            # Use unbuffered I/O for large files to avoid double buffering
            file_size = src.stat().st_size
            buffer_size = self.io_buffer_size

            # For very large files, use larger buffers
            if file_size > 100 * 1024 * 1024:  # > 100MB
                buffer_size = min(32 * 1024 * 1024, self.io_buffer_size * 4)

            with open(src, "rb", buffering=0) as src_file, open(dst, "wb", buffering=0) as dst_file:
                # Copy in chunks
                while True:
                    chunk = src_file.read(buffer_size)
                    if not chunk:
                        break
                    dst_file.write(chunk)

            # Copy metadata
            shutil.copystat(src, dst, follow_symlinks=True)
            logger.debug(f"Optimized buffered copy successful: {src} -> {dst}")
            return True

        except Exception as e:
            logger.debug(f"Optimized buffered copy failed: {e}")
            return False

    def fast_copy(self, src: Path, dst: Path) -> bool:
        """
        Perform the fastest available copy operation.
        Tries methods in order of efficiency: reflink -> clonefile -> copy_file_range -> sendfile -> buffered.
        """
        src = Path(src)
        dst = Path(dst)

        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        # If destination exists, remove it
        if dst.exists():
            dst.unlink()

        # Try zero-copy methods first (most efficient)
        if self.os_name == "linux":
            # Linux: try reflink first, then copy_file_range, then sendfile
            if self.same_filesystem(src, dst) and self.try_reflink_copy(src, dst):
                return True

            if self.try_copy_file_range(src, dst):
                return True

            if self.try_sendfile_copy(src, dst):
                return True

        elif self.os_name == "darwin":
            # macOS: try clonefile first, then sendfile
            if self.same_filesystem(src, dst) and self.try_clonefile_copy(src, dst):
                return True

            if self.try_sendfile_copy(src, dst):
                return True

        elif self.os_name == "windows":
            # Windows: use shutil.copy2 which is optimized for Windows
            try:
                shutil.copy2(src, dst)
                logger.debug(f"Windows copy2 successful: {src} -> {dst}")
                return True
            except Exception as e:
                logger.debug(f"Windows copy2 failed: {e}")

        # Final fallback: optimized buffered copy
        return self.optimized_buffered_copy(src, dst)

    def fast_move(self, src: Path, dst: Path) -> bool:
        """
        Perform the fastest available move operation.
        Tries atomic rename first, then fast copy + delete.
        """
        src = Path(src)
        dst = Path(dst)

        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Try atomic rename first (fastest for same filesystem)
        try:
            os.replace(src, dst)
            logger.debug(f"Atomic move successful: {src} -> {dst}")
            return True
        except OSError:
            # Cross-filesystem move: copy then delete
            if self.fast_copy(src, dst):
                try:
                    src.unlink()
                    logger.debug(f"Cross-filesystem move successful: {src} -> {dst}")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to remove source after copy: {src} ({e})")
                    return False
            return False

    def benchmark_copy_methods(self, test_file: Path, iterations: int = 3) -> dict[str, float]:
        """
        Benchmark different copy methods with a test file.
        Returns average times for each method.
        """
        import tempfile

        results = {}
        test_size = test_file.stat().st_size

        methods = [
            ("shutil.copy2", lambda s, d: shutil.copy2(s, d)),
            ("fast_copy", self.fast_copy),
            ("optimized_buffered", self.optimized_buffered_copy),
        ]

        if self.has_sendfile:
            methods.append(("sendfile", self.try_sendfile_copy))

        if self.has_copy_file_range:
            methods.append(("copy_file_range", self.try_copy_file_range))

        if self.has_reflink:
            methods.append(("reflink", self.try_reflink_copy))

        if self.has_clonefile:
            methods.append(("clonefile", self.try_clonefile_copy))

        for method_name, method_func in methods:
            times = []

            for _i in range(iterations):
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = Path(tmp.name)

                try:
                    start_time = time.time()
                    success = method_func(test_file, tmp_path)
                    end_time = time.time()

                    if success:
                        times.append(end_time - start_time)
                    else:
                        times.append(float("inf"))  # Failed

                finally:
                    if tmp_path.exists():
                        tmp_path.unlink()

            avg_time = sum(times) / len(times) if times else float("inf")
            throughput = (test_size / avg_time) / (1024 * 1024) if avg_time != float("inf") else 0

            results[method_name] = {
                "avg_time": avg_time,
                "throughput_mb_s": throughput,
                "success_rate": sum(1 for t in times if t != float("inf")) / len(times),
            }

        return results


# Example usage and testing
if __name__ == "__main__":
    import argparse
    import tempfile

    def main():
        parser = argparse.ArgumentParser(description="Zero-copy file operations testing")
        parser.add_argument(
            "--benchmark", action="store_true", help="Run benchmark of copy methods"
        )
        parser.add_argument(
            "--test-size", type=int, default=100, help="Test file size in MB for benchmark"
        )
        parser.add_argument("--src", type=Path, help="Source file for copy test")
        parser.add_argument("--dst", type=Path, help="Destination for copy test")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

        args = parser.parse_args()

        # Setup logging
        level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

        zero_copy = ZeroCopyOperations()

        if args.benchmark:
            # Create test file
            args.test_size * 1024 * 1024  # MB to bytes
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = Path(tmp.name)

                print(f"Creating {args.test_size}MB test file...")
                with open(tmp_path, "wb") as f:
                    chunk = b"x" * (1024 * 1024)  # 1MB chunk
                    for _ in range(args.test_size):
                        f.write(chunk)

            try:
                print("Benchmarking copy methods...")
                results = zero_copy.benchmark_copy_methods(tmp_path)

                print("\n📊 Copy Method Benchmark Results")
                print(f"{'=' * 60}")
                print(f"{'Method':<20} {'Time (s)':<12} {'Speed (MB/s)':<15} {'Success'}")
                print(f"{'=' * 60}")

                for method, stats in sorted(results.items(), key=lambda x: x[1]["avg_time"]):
                    time_str = (
                        f"{stats['avg_time']:.3f}"
                        if stats["avg_time"] != float("inf")
                        else "FAILED"
                    )
                    speed_str = (
                        f"{stats['throughput_mb_s']:.1f}" if stats["throughput_mb_s"] > 0 else "N/A"
                    )
                    success_str = f"{stats['success_rate'] * 100:.0f}%"

                    print(f"{method:<20} {time_str:<12} {speed_str:<15} {success_str}")

            finally:
                tmp_path.unlink()

        elif args.src and args.dst:
            # Test copy operation
            print(f"Testing fast copy: {args.src} -> {args.dst}")
            start_time = time.time()
            success = zero_copy.fast_copy(args.src, args.dst)
            end_time = time.time()

            if success:
                file_size = args.src.stat().st_size
                speed = (file_size / (end_time - start_time)) / (1024 * 1024)
                print(f"✅ Copy successful in {end_time - start_time:.3f}s ({speed:.1f} MB/s)")
            else:
                print("❌ Copy failed")

        else:
            # Show capabilities
            print("🔧 Zero-Copy Capabilities")
            print(f"{'=' * 40}")
            print(f"OS: {zero_copy.os_name}")
            print(f"Reflink (Linux): {zero_copy.has_reflink}")
            print(f"Clonefile (macOS): {zero_copy.has_clonefile}")
            print(f"copy_file_range: {zero_copy.has_copy_file_range}")
            print(f"sendfile: {zero_copy.has_sendfile}")
            print(f"Buffer size: {zero_copy.io_buffer_size // (1024 * 1024)}MB")

        return 0

    exit(main())
