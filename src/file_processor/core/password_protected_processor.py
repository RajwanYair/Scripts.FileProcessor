"""
Password Protected File Processor
=================================
Advanced password removal and protection handling for various file formats.
Supports PDF, Office documents, and archive files with multiple password attempts.

This module provides comprehensive password removal capabilities using external
tools and libraries, with cross-platform compatibility and graceful fallbacks.
"""

import contextlib
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any


@dataclass
class PasswordRemovalResult:
    """Result of password removal operation."""

    success: bool
    method_used: str | None = None
    password_used: str | None = None
    error_message: str | None = None
    file_modified: bool = False


class PasswordProtectedFileProcessor:
    """
    Advanced password-protected file processor with multi-format support.

    Supported formats:
    - PDF files (using qpdf)
    - Office documents (using msoffcrypto-tool)
    - ZIP/RAR archives (using 7z)
    - Comic book archives (CBZ, CBR, CB7, CBT)

    Features:
    - Multiple password attempts
    - Cross-platform external tool integration
    - Graceful fallback when tools are unavailable
    - Detailed operation logging
    """

    def __init__(self, password_list: list[str] | None = None, log_callback=None):
        """
        Initialize the password processor.

        Args:
            password_list: List of passwords to try (default common passwords)
            log_callback: Function to call for logging messages
        """
        self.password_list = password_list or self._get_default_passwords()
        self.log_callback = log_callback or print
        self.external_tools = self._detect_external_tools()

        # Supported file extensions for password protection
        self.password_protected_extensions = {
            "pdf": self._remove_pdf_password,
            "docx": self._remove_office_password,
            "xlsx": self._remove_office_password,
            "pptx": self._remove_office_password,
            "zip": self._remove_zip_password,
            "cbz": self._remove_zip_password,
            "cb7": self._remove_zip_password,
            "cbt": self._remove_zip_password,
            "rar": self._remove_rar_password,
            "cbr": self._remove_rar_password,
        }

    def _get_default_passwords(self) -> list[str]:
        """Get default password list for common protected files."""
        return [
            "@Manhwa_Arena",
            r"\@Manhwa_Arena",
            "password",
            "123456",
            "admin",
            "user",
            "test",
            "demo",
            "sample",
            "",  # Empty password
        ]

    def _detect_external_tools(self) -> dict[str, bool]:
        """Detect available external tools for password removal."""
        tools = {}
        for tool in ["qpdf", "msoffcrypto-cli", "7z", "unrar"]:
            tools[tool] = self._command_exists(tool)
        return tools

    def _command_exists(self, cmd: str) -> bool:
        """Check if an external command exists in the system PATH."""
        return shutil.which(cmd) is not None

    def is_password_protected(self, file_path: Path) -> bool:
        """
        Check if a file is password protected.

        Args:
            file_path: Path to the file to check

        Returns:
            True if file appears to be password protected
        """
        if not file_path.exists():
            return False

        ext = file_path.suffix.lower().lstrip(".")

        if ext == "pdf":
            return self._is_pdf_encrypted(file_path)
        elif ext in ["docx", "xlsx", "pptx"]:
            return self._is_office_encrypted(file_path)
        elif ext in ["zip", "cbz", "cb7", "cbt"]:
            return self._is_zip_encrypted(file_path)
        elif ext in ["rar", "cbr"]:
            return self._is_rar_encrypted(file_path)

        return False

    def remove_password(self, file_path: Path) -> PasswordRemovalResult:
        """
        Remove password protection from a file.

        Args:
            file_path: Path to the password-protected file

        Returns:
            PasswordRemovalResult with operation details
        """
        if not file_path.exists():
            return PasswordRemovalResult(
                success=False, error_message=f"File not found: {file_path}"
            )

        ext = file_path.suffix.lower().lstrip(".")

        if ext not in self.password_protected_extensions:
            return PasswordRemovalResult(
                success=True,
                error_message=f"File extension .{ext} not supported for password removal",
            )

        # Check if file is actually password protected
        if not self.is_password_protected(file_path):
            return PasswordRemovalResult(
                success=True, error_message="File is not password protected"
            )

        # Try to remove password using appropriate method
        removal_method = self.password_protected_extensions[ext]
        return removal_method(file_path)

    def _is_pdf_encrypted(self, file_path: Path) -> bool:
        """Check if PDF file is encrypted."""
        if not self.external_tools.get("qpdf", False):
            return False

        try:
            result = subprocess.run(
                ["qpdf", "--show-encryption", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return "encrypted" in result.stdout.lower()
        except Exception:
            return False

    def _is_office_encrypted(self, file_path: Path) -> bool:
        """Check if Office document is encrypted."""
        with contextlib.suppress(Exception), open(file_path, "rb") as f:
            # Try to read the file header to detect encryption
            header = f.read(512)
            # Office files start with specific signatures
            # Encrypted files have different patterns
            if b"EncryptedPackage" in header or b"Microsoft Office Document" in header:
                return True
        return False

    def _is_zip_encrypted(self, file_path: Path) -> bool:
        """Check if ZIP file is encrypted."""
        if not self.external_tools.get("7z", False):
            return False

        try:
            result = subprocess.run(
                ["7z", "l", str(file_path)], capture_output=True, text=True, timeout=30
            )
            # Look for encryption indicators in the output
            return not re.search(r"Encrypted\s*=\s*No", result.stdout, re.IGNORECASE)
        except Exception:
            return False

    def _is_rar_encrypted(self, file_path: Path) -> bool:
        """Check if RAR file is encrypted."""
        if not self.external_tools.get("unrar", False):
            return False

        try:
            result = subprocess.run(
                ["unrar", "l", str(file_path)], capture_output=True, text=True, timeout=30
            )
            return "*" in result.stdout  # RAR shows * for encrypted files
        except Exception:
            return False

    def _remove_pdf_password(self, file_path: Path) -> PasswordRemovalResult:
        """Remove password from PDF file using qpdf."""
        if not self.external_tools.get("qpdf", False):
            return PasswordRemovalResult(
                success=False, error_message="qpdf not available for PDF password removal"
            )

        for password in self.password_list:
            temp_path = file_path.with_suffix(file_path.suffix + ".temp")

            try:
                # Attempt to decrypt with current password
                cmd = [
                    "qpdf",
                    f"--password={password}",
                    "--decrypt",
                    str(file_path),
                    str(temp_path),
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0 and temp_path.exists():
                    # Success! Replace original file
                    temp_path.replace(file_path)
                    self.log_callback(f"Removed PDF password using: {password}")
                    return PasswordRemovalResult(
                        success=True, method_used="qpdf", password_used=password, file_modified=True
                    )
                else:
                    # Clean up temp file if it exists
                    if temp_path.exists():
                        temp_path.unlink()

            except Exception as e:
                self.log_callback(f"Error removing PDF password: {e}")
                if temp_path.exists():
                    temp_path.unlink()
                continue

        return PasswordRemovalResult(
            success=False, error_message="Failed to remove PDF password with any provided password"
        )

    def _remove_office_password(self, file_path: Path) -> PasswordRemovalResult:
        """Remove password from Office document using msoffcrypto-tool."""
        if not self.external_tools.get("msoffcrypto-cli", False):
            return PasswordRemovalResult(
                success=False,
                error_message="msoffcrypto-cli not available for Office password removal",
            )

        for password in self.password_list:
            temp_path = file_path.with_suffix(file_path.suffix + ".temp")

            try:
                cmd = ["msoffcrypto-cli", str(file_path), str(temp_path), "-p", password]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0 and temp_path.exists():
                    # Success! Replace original file
                    temp_path.replace(file_path)
                    self.log_callback(f"Removed Office password using: {password}")
                    return PasswordRemovalResult(
                        success=True,
                        method_used="msoffcrypto-cli",
                        password_used=password,
                        file_modified=True,
                    )
                else:
                    if temp_path.exists():
                        temp_path.unlink()

            except Exception as e:
                self.log_callback(f"Error removing Office password: {e}")
                if temp_path.exists():
                    temp_path.unlink()
                continue

        return PasswordRemovalResult(
            success=False,
            error_message="Failed to remove Office password with any provided password",
        )

    def _remove_zip_password(self, file_path: Path) -> PasswordRemovalResult:
        """Remove password from ZIP file using 7z."""
        if not self.external_tools.get("7z", False):
            return PasswordRemovalResult(
                success=False, error_message="7z not available for ZIP password removal"
            )

        for password in self.password_list:
            temp_dir = file_path.parent / (file_path.stem + "_temp_extract")
            temp_zip = file_path.with_suffix(file_path.suffix + ".temp")

            try:
                # Clean up any existing temp directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                temp_dir.mkdir(exist_ok=True)

                # Extract with password
                extract_cmd = ["7z", "x", str(file_path), f"-o{temp_dir}", f"-p{password}", "-y"]
                extract_result = subprocess.run(
                    extract_cmd, capture_output=True, text=True, timeout=120
                )

                if extract_result.returncode == 0:
                    # Re-compress without password
                    create_cmd = ["7z", "a", str(temp_zip), f"{temp_dir}/*", "-y"]
                    create_result = subprocess.run(
                        create_cmd, capture_output=True, text=True, timeout=120
                    )

                    if create_result.returncode == 0 and temp_zip.exists():
                        # Success! Replace original file
                        temp_zip.replace(file_path)
                        shutil.rmtree(temp_dir)
                        self.log_callback(f"Removed ZIP password using: {password}")
                        return PasswordRemovalResult(
                            success=True,
                            method_used="7z",
                            password_used=password,
                            file_modified=True,
                        )
                    else:
                        if temp_zip.exists():
                            temp_zip.unlink()

                # Clean up temp directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)

            except Exception as e:
                self.log_callback(f"Error removing ZIP password: {e}")
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
                if temp_zip.exists():
                    temp_zip.unlink()
                continue

        return PasswordRemovalResult(
            success=False, error_message="Failed to remove ZIP password with any provided password"
        )

    def _remove_rar_password(self, file_path: Path) -> PasswordRemovalResult:
        """Remove password from RAR file (extract and re-compress)."""
        if not self.external_tools.get("unrar", False) or not self.external_tools.get("7z", False):
            return PasswordRemovalResult(
                success=False, error_message="unrar and 7z required for RAR password removal"
            )

        for password in self.password_list:
            temp_dir = file_path.parent / (file_path.stem + "_temp_extract")
            temp_archive = file_path.with_suffix(".zip")  # Convert to ZIP

            try:
                # Clean up any existing temp directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                temp_dir.mkdir(exist_ok=True)

                # Extract RAR with password
                extract_cmd = ["unrar", "x", str(file_path), str(temp_dir), f"-p{password}", "-y"]
                extract_result = subprocess.run(
                    extract_cmd, capture_output=True, text=True, timeout=120
                )

                if extract_result.returncode == 0:
                    # Re-compress as ZIP without password
                    create_cmd = ["7z", "a", str(temp_archive), f"{temp_dir}/*", "-y"]
                    create_result = subprocess.run(
                        create_cmd, capture_output=True, text=True, timeout=120
                    )

                    if create_result.returncode == 0 and temp_archive.exists():
                        # Success! Replace original file
                        file_path.unlink()  # Remove original RAR
                        self.log_callback(
                            f"Converted RAR to ZIP, removed password using: {password}"
                        )
                        shutil.rmtree(temp_dir)
                        return PasswordRemovalResult(
                            success=True,
                            method_used="unrar+7z",
                            password_used=password,
                            file_modified=True,
                        )
                    else:
                        if temp_archive.exists():
                            temp_archive.unlink()

                # Clean up temp directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)

            except Exception as e:
                self.log_callback(f"Error removing RAR password: {e}")
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
                if temp_archive.exists():
                    temp_archive.unlink()
                continue

        return PasswordRemovalResult(
            success=False, error_message="Failed to remove RAR password with any provided password"
        )

    def batch_process(self, file_paths: list[Path]) -> dict[str, PasswordRemovalResult]:
        """
        Process multiple files for password removal.

        Args:
            file_paths: List of file paths to process

        Returns:
            Dictionary mapping file paths to results
        """
        results = {}

        for file_path in file_paths:
            try:
                result = self.remove_password(file_path)
                results[str(file_path)] = result

                if result.success and result.file_modified:
                    self.log_callback(f"Successfully processed: {file_path}")
                elif not result.success:
                    self.log_callback(f"Failed to process: {file_path} - {result.error_message}")

            except Exception as e:
                results[str(file_path)] = PasswordRemovalResult(
                    success=False, error_message=f"Unexpected error: {e}"
                )
                self.log_callback(f"Error processing {file_path}: {e}")

        return results

    def get_tool_availability(self) -> dict[str, Any]:
        """Get information about available external tools."""
        return {
            "external_tools": self.external_tools,
            "supported_formats": list(self.password_protected_extensions.keys()),
            "password_list_size": len(self.password_list),
            "recommendations": self._get_tool_recommendations(),
        }

    def _get_tool_recommendations(self) -> list[str]:
        """Get recommendations for installing missing tools."""
        recommendations = []

        if not self.external_tools.get("qpdf", False):
            recommendations.append(
                "Install qpdf for PDF password removal: sudo apt-get install qpdf (Linux) or choco install qpdf (Windows)"
            )

        if not self.external_tools.get("msoffcrypto-cli", False):
            recommendations.append(
                "Install msoffcrypto-tool for Office documents: pip install msoffcrypto-tool"
            )

        if not self.external_tools.get("7z", False):
            recommendations.append(
                "Install 7z for archive processing: sudo apt-get install p7zip-full (Linux) or choco install 7zip (Windows)"
            )

        if not self.external_tools.get("unrar", False):
            recommendations.append(
                "Install unrar for RAR files: sudo apt-get install unrar (Linux) or choco install unrar (Windows)"
            )

        return recommendations
