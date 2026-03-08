#!/usr/bin/env python3
"""
Enhanced Password Scanner and Brute-Force System
================================================

Comprehensive password detection and removal system that:
1. Scans files to detect password protection
2. Tests customer-provided passwords
3. Attempts brute-force with common password lists
4. Supports multiple file types (PDF, ZIP, RAR, 7Z, Office documents)
"""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
import itertools
import logging
from pathlib import Path
import string
import time

logger = logging.getLogger(__name__)


class PasswordProtectionType(Enum):
    """Types of password protection."""

    PDF = "PDF Document"
    ZIP = "ZIP Archive"
    RAR = "RAR Archive"
    SEVEN_ZIP = "7-Zip Archive"
    DOCX = "Word Document"
    XLSX = "Excel Spreadsheet"
    PPTX = "PowerPoint Presentation"
    DOC = "Legacy Word Document"
    XLS = "Legacy Excel Spreadsheet"
    UNKNOWN = "Unknown Type"


class AttackMode(Enum):
    """Password attack modes."""

    CUSTOM = "custom"  # User-provided passwords
    COMMON = "common"  # Common passwords list
    DICTIONARY = "dictionary"  # Dictionary attack
    BRUTEFORCE_NUMERIC = "bruteforce_numeric"  # Only numbers
    BRUTEFORCE_ALPHA = "bruteforce_alpha"  # Only letters
    BRUTEFORCE_ALPHANUM = "bruteforce_alphanum"  # Letters + numbers
    BRUTEFORCE_FULL = "bruteforce_full"  # All characters


@dataclass
class PasswordAttempt:
    """Record of a password attempt."""

    password: str
    attack_mode: AttackMode
    timestamp: float = field(default_factory=time.time)
    success: bool = False


@dataclass
class ProtectedFileInfo:
    """Information about a password-protected file."""

    path: Path
    file_type: PasswordProtectionType
    size_bytes: int
    detected_time: float = field(default_factory=time.time)

    # Password attempt tracking
    attempts: list[PasswordAttempt] = field(default_factory=list)
    found_password: str | None = None
    is_cracked: bool = False

    # Metadata
    encryption_method: str | None = None
    estimated_strength: str | None = None  # weak, medium, strong


@dataclass
class ScanResult:
    """Results from scanning a directory."""

    total_files_scanned: int = 0
    protected_files: list[ProtectedFileInfo] = field(default_factory=list)
    unprotected_files: int = 0
    scan_errors: dict[str, str] = field(default_factory=dict)
    scan_duration: float = 0.0


class CommonPasswords:
    """Common password lists for brute-force attacks."""

    # Top 100 most common passwords
    TOP_100 = [
        "123456",
        "password",
        "123456789",
        "12345678",
        "12345",
        "1234567",
        "password1",
        "123123",
        "1234567890",
        "000000",
        "abc123",
        "qwerty",
        "iloveyou",
        "monkey",
        "dragon",
        "111111",
        "letmein",
        "sunshine",
        "master",
        "welcome",
        "shadow",
        "ashley",
        "football",
        "jesus",
        "michael",
        "ninja",
        "mustang",
        "password123",
        "admin",
        "administrator",
        "root",
        "toor",
        "pass",
        "test",
        "guest",
        "changeme",
        "default",
        "qwerty123",
        "welcome123",
        "hello",
        "hello123",
        "secret",
        "god",
        "love",
        "sex",
        "money",
        "freedom",
        "whatever",
        "qazwsx",
        "trustno1",
        "jordan",
        "harley",
        "robert",
        "matthew",
        "daniel",
        "andrew",
        "andrea",
        "joshua",
        "1q2w3e4r",
        "zaq1zaq1",
        "qwertyuiop",
        "charlie",
        "aa123456",
        "donald",
        "bailey",
        "passw0rd",
        "mysql",
        "Login",
        "starwars",
        "solo",
        "1qaz2wsx",
        "computer",
        "internet",
        "corvette",
        "mercedes",
        "samsung",
        "apple",
        "oracle",
        "killer",
        "pepper",
        "hunter",
        "sunshine",
        "banana",
        "junior",
        "chelsea",
        "sophie",
        "summer",
        "princess",
        "thomas",
        "hockey",
        "ranger",
        "diamond",
        "tigger",
        "jackson",
        "sweet",
        "buster",
        "batman",
        "victor",
        "edward",
    ]

    # Common number patterns
    NUMBER_PATTERNS = [
        "0000",
        "1111",
        "2222",
        "3333",
        "4444",
        "5555",
        "6666",
        "7777",
        "8888",
        "9999",
        "1234",
        "4321",
        "2468",
        "1357",
        "9876",
        "5678",
        "8765",
    ]

    # Common word variations
    COMMON_WORDS = [
        "password",
        "admin",
        "user",
        "test",
        "demo",
        "sample",
        "temp",
        "document",
        "file",
        "secure",
        "private",
        "confidential",
        "secret",
    ]

    @classmethod
    def get_common_list(cls, max_count: int = 100) -> list[str]:
        """Get list of common passwords."""
        passwords = set()

        # Add top passwords
        passwords.update(cls.TOP_100[:max_count])

        # Add number patterns
        passwords.update(cls.NUMBER_PATTERNS)

        # Add word variations (with numbers)
        for word in cls.COMMON_WORDS:
            passwords.add(word)
            passwords.add(word.capitalize())
            passwords.add(word.upper())
            for i in range(10):
                passwords.add(f"{word}{i}")
                passwords.add(f"{word}{i}{i}")
                passwords.add(f"{i}{word}")
            for year in range(2020, 2026):
                passwords.add(f"{word}{year}")

        return list(passwords)

    @classmethod
    def generate_numeric_bruteforce(cls, min_length: int = 4, max_length: int = 8):
        """Generate numeric brute-force passwords."""
        for length in range(min_length, max_length + 1):
            for combo in itertools.product(string.digits, repeat=length):
                yield "".join(combo)

    @classmethod
    def generate_alpha_bruteforce(cls, min_length: int = 4, max_length: int = 6):
        """Generate alphabetic brute-force passwords."""
        chars = string.ascii_lowercase
        for length in range(min_length, max_length + 1):
            for combo in itertools.product(chars, repeat=length):
                yield "".join(combo)

    @classmethod
    def generate_alphanum_bruteforce(cls, min_length: int = 4, max_length: int = 6):
        """Generate alphanumeric brute-force passwords."""
        chars = string.ascii_lowercase + string.digits
        for length in range(min_length, max_length + 1):
            for combo in itertools.product(chars, repeat=length):
                yield "".join(combo)


class PasswordDetector:
    """Detect password-protected files."""

    @staticmethod
    def is_pdf_protected(file_path: Path) -> tuple[bool, str | None]:
        """Check if PDF is password protected."""
        try:
            import PyPDF2

            with open(file_path, "rb") as f:
                try:
                    reader = PyPDF2.PdfReader(f)

                    # Check if encrypted
                    if reader.is_encrypted:
                        # Try to get encryption method
                        encryption_method = "Unknown"
                        if hasattr(reader, "_encryption"):
                            encryption_method = str(reader._encryption)
                        return True, encryption_method

                    return False, None

                except Exception as e:
                    if "encrypted" in str(e).lower() or "password" in str(e).lower():
                        return True, "Unknown"
                    raise

        except ImportError:
            logger.warning("PyPDF2 not installed, cannot check PDF protection")
            return False, "PyPDF2 not available"
        except Exception as e:
            logger.debug(f"Error checking PDF {file_path}: {e}")
            return False, None

    @staticmethod
    def is_zip_protected(file_path: Path) -> tuple[bool, str | None]:
        """Check if ZIP is password protected."""
        try:
            import zipfile

            with zipfile.ZipFile(file_path, "r") as zf:
                # Check if any file in archive needs password
                for info in zf.infolist():
                    if info.flag_bits & 0x1:  # Bit 0 indicates encryption
                        return True, "Standard ZIP encryption"

                # Try to read first file
                if zf.namelist():
                    try:
                        zf.read(zf.namelist()[0])
                        return False, None
                    except RuntimeError as e:
                        if "password" in str(e).lower():
                            return True, "Password required"
                        raise

                return False, None

        except Exception as e:
            logger.debug(f"Error checking ZIP {file_path}: {e}")
            return False, None

    @staticmethod
    def is_rar_protected(file_path: Path) -> tuple[bool, str | None]:
        """Check if RAR is password protected."""
        try:
            import rarfile

            with rarfile.RarFile(file_path, "r") as rf:
                # Check if needs password
                if rf.needs_password():
                    return True, "RAR encryption"

                # Try to read first file
                if rf.namelist():
                    try:
                        rf.read(rf.namelist()[0])
                        return False, None
                    except (rarfile.PasswordRequired, RuntimeError):
                        return True, "Password required"

                return False, None

        except ImportError:
            logger.warning("rarfile not installed, cannot check RAR protection")
            return False, "rarfile not available"
        except Exception as e:
            logger.debug(f"Error checking RAR {file_path}: {e}")
            return False, None

    @staticmethod
    def is_7z_protected(file_path: Path) -> tuple[bool, str | None]:
        """Check if 7Z is password protected."""
        try:
            import py7zr

            with py7zr.SevenZipFile(file_path, "r") as szf:
                # Check if needs password
                if szf.needs_password():
                    return True, "7-Zip encryption"

                # Try to extract info
                try:
                    szf.list()
                    return False, None
                except Exception as e:
                    if "password" in str(e).lower():
                        return True, "Password required"
                    raise

        except ImportError:
            logger.warning("py7zr not installed, cannot check 7Z protection")
            return False, "py7zr not available"
        except Exception as e:
            logger.debug(f"Error checking 7Z {file_path}: {e}")
            return False, None

    @staticmethod
    def is_office_protected(file_path: Path) -> tuple[bool, str | None]:
        """Check if Office document is password protected."""
        try:
            import zipfile

            # Modern Office files (docx, xlsx, pptx) are ZIP archives
            try:
                with zipfile.ZipFile(file_path, "r") as zf:
                    # Try to read the encryption info
                    if "EncryptionInfo" in zf.namelist():
                        return True, "Office encryption"

                    # Try to read core properties
                    try:
                        zf.read("docProps/core.xml")
                        return False, None
                    except RuntimeError as e:
                        if "password" in str(e).lower() or "encrypted" in str(e).lower():
                            return True, "Password required"
                        raise

            except zipfile.BadZipFile:
                # Might be legacy Office format (doc, xls, ppt)
                # These use OLE format which is harder to detect
                # For now, we'll use file size and magic bytes heuristics
                with open(file_path, "rb") as f:
                    header = f.read(8)
                    # OLE header: D0 CF 11 E0 A1 B1 1A E1
                    if header == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
                        # It's an OLE file, but we can't easily detect password
                        return False, "Legacy format (detection limited)"

                return False, None

        except Exception as e:
            logger.debug(f"Error checking Office file {file_path}: {e}")
            return False, None

    @classmethod
    def detect_protection(
        cls, file_path: Path
    ) -> tuple[bool, PasswordProtectionType, str | None]:
        """
        Detect if file is password protected.

        Returns:
            (is_protected, file_type, encryption_method)
        """
        suffix = file_path.suffix.lower()

        # PDF files
        if suffix == ".pdf":
            is_protected, method = cls.is_pdf_protected(file_path)
            return is_protected, PasswordProtectionType.PDF, method

        # ZIP files
        elif suffix == ".zip":
            is_protected, method = cls.is_zip_protected(file_path)
            return is_protected, PasswordProtectionType.ZIP, method

        # RAR files
        elif suffix in [".rar"]:
            is_protected, method = cls.is_rar_protected(file_path)
            return is_protected, PasswordProtectionType.RAR, method

        # 7-Zip files
        elif suffix == ".7z":
            is_protected, method = cls.is_7z_protected(file_path)
            return is_protected, PasswordProtectionType.SEVEN_ZIP, method

        # Office files
        elif suffix in [".docx", ".doc"]:
            is_protected, method = cls.is_office_protected(file_path)
            file_type = (
                PasswordProtectionType.DOCX if suffix == ".docx" else PasswordProtectionType.DOC
            )
            return is_protected, file_type, method

        elif suffix in [".xlsx", ".xls"]:
            is_protected, method = cls.is_office_protected(file_path)
            file_type = (
                PasswordProtectionType.XLSX if suffix == ".xlsx" else PasswordProtectionType.XLS
            )
            return is_protected, file_type, method

        elif suffix in [".pptx", ".ppt"]:
            is_protected, method = cls.is_office_protected(file_path)
            file_type = PasswordProtectionType.PPTX
            return is_protected, file_type, method

        # Unknown type
        return False, PasswordProtectionType.UNKNOWN, None


class PasswordCracker:
    """Crack passwords for protected files."""

    @staticmethod
    def test_pdf_password(file_path: Path, password: str) -> bool:
        """Test password on PDF file."""
        try:
            import PyPDF2

            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                if reader.is_encrypted:
                    # Try to decrypt with password
                    result = reader.decrypt(password)
                    return result != 0  # 0 = failure, 1/2 = success

                return False  # Not encrypted

        except Exception as e:
            logger.debug(f"Error testing PDF password: {e}")
            return False

    @staticmethod
    def test_zip_password(file_path: Path, password: str) -> bool:
        """Test password on ZIP file."""
        try:
            import zipfile

            with zipfile.ZipFile(file_path, "r") as zf:
                if zf.namelist():
                    # Try to read first file with password
                    zf.read(zf.namelist()[0], pwd=password.encode("utf-8"))
                    return True

                return False

        except RuntimeError:
            return False  # Wrong password
        except Exception as e:
            logger.debug(f"Error testing ZIP password: {e}")
            return False

    @staticmethod
    def test_rar_password(file_path: Path, password: str) -> bool:
        """Test password on RAR file."""
        try:
            import rarfile

            with rarfile.RarFile(file_path, "r") as rf:
                rf.setpassword(password)

                if rf.namelist():
                    # Try to read first file
                    rf.read(rf.namelist()[0])
                    return True

                return False

        except (rarfile.PasswordRequired, RuntimeError, rarfile.BadRarFile):
            return False  # Wrong password
        except Exception as e:
            logger.debug(f"Error testing RAR password: {e}")
            return False

    @staticmethod
    def test_7z_password(file_path: Path, password: str) -> bool:
        """Test password on 7Z file."""
        try:
            import py7zr

            with py7zr.SevenZipFile(file_path, "r", password=password) as szf:
                # Try to list files
                szf.list()
                return True

        except Exception:
            return False  # Wrong password or error

    @classmethod
    def test_password(
        cls, file_path: Path, file_type: PasswordProtectionType, password: str
    ) -> bool:
        """
        Test password on file based on type.

        Returns:
            True if password is correct, False otherwise
        """
        try:
            if file_type == PasswordProtectionType.PDF:
                return cls.test_pdf_password(file_path, password)

            elif file_type == PasswordProtectionType.ZIP:
                return cls.test_zip_password(file_path, password)

            elif file_type == PasswordProtectionType.RAR:
                return cls.test_rar_password(file_path, password)

            elif file_type == PasswordProtectionType.SEVEN_ZIP:
                return cls.test_7z_password(file_path, password)

            # Office files require different approach
            elif file_type in [
                PasswordProtectionType.DOCX,
                PasswordProtectionType.XLSX,
                PasswordProtectionType.PPTX,
            ]:
                # Office password testing is complex, would need additional libraries
                logger.warning(f"Password testing for {file_type.value} not fully implemented")
                return False

            return False

        except Exception as e:
            logger.debug(f"Error testing password: {e}")
            return False


class EnhancedPasswordScanner:
    """
    Main password scanner and cracker.

    Features:
    - Scan directories for password-protected files
    - Test customer-provided passwords
    - Brute-force with common passwords
    - Multiple attack modes
    - Progress tracking
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.detector = PasswordDetector()
        self.cracker = PasswordCracker()

        # Statistics
        self.total_attempts = 0
        self.successful_cracks = 0

    def scan_directory(
        self, directory: Path, recursive: bool = True, file_extensions: set[str] | None = None
    ) -> ScanResult:
        """
        Scan directory for password-protected files.

        Args:
            directory: Directory to scan
            recursive: Scan subdirectories
            file_extensions: Filter by extensions (e.g., {'.pdf', '.zip'})

        Returns:
            ScanResult with protected files found
        """
        start_time = time.time()
        result = ScanResult()

        # Default extensions to check
        if file_extensions is None:
            file_extensions = {
                ".pdf",
                ".zip",
                ".rar",
                ".7z",
                ".docx",
                ".xlsx",
                ".pptx",
                ".doc",
                ".xls",
                ".ppt",
            }

        # Get files to scan
        if recursive:
            files = [
                f
                for f in directory.rglob("*")
                if f.is_file() and f.suffix.lower() in file_extensions
            ]
        else:
            files = [
                f
                for f in directory.glob("*")
                if f.is_file() and f.suffix.lower() in file_extensions
            ]

        result.total_files_scanned = len(files)

        logger.info(f"Scanning {result.total_files_scanned} files for password protection...")

        # Scan each file
        for file_path in files:
            try:
                is_protected, file_type, encryption_method = self.detector.detect_protection(
                    file_path
                )

                if is_protected:
                    info = ProtectedFileInfo(
                        path=file_path,
                        file_type=file_type,
                        size_bytes=file_path.stat().st_size,
                        encryption_method=encryption_method,
                    )
                    result.protected_files.append(info)
                    logger.info(f"Found protected file: {file_path.name} ({file_type.value})")
                else:
                    result.unprotected_files += 1

            except Exception as e:
                result.scan_errors[str(file_path)] = str(e)
                logger.error(f"Error scanning {file_path}: {e}")

        result.scan_duration = time.time() - start_time

        logger.info(
            f"Scan complete: {len(result.protected_files)} protected files found in {result.scan_duration:.2f}s"
        )

        return result

    def crack_password(
        self,
        file_info: ProtectedFileInfo,
        custom_passwords: list[str] | None = None,
        attack_modes: list[AttackMode] | None = None,
        max_attempts: int = 10000,
        callback: Callable[[int, str], None] | None = None,
    ) -> bool:
        """
        Attempt to crack password for a protected file.

        Args:
            file_info: Protected file information
            custom_passwords: Customer-provided passwords to try first
            attack_modes: Attack modes to use (in order)
            max_attempts: Maximum password attempts
            callback: Progress callback(attempts_count, current_password)

        Returns:
            True if password cracked, False otherwise
        """
        if file_info.is_cracked:
            logger.info(f"File {file_info.path.name} already cracked")
            return True

        # Default attack modes
        if attack_modes is None:
            attack_modes = [
                AttackMode.CUSTOM,
                AttackMode.COMMON,
                AttackMode.BRUTEFORCE_NUMERIC,
            ]

        logger.info(f"Starting password crack on {file_info.path.name}")
        logger.info(f"Attack modes: {[mode.value for mode in attack_modes]}")

        attempts = 0

        # Attack mode: Custom passwords
        if AttackMode.CUSTOM in attack_modes and custom_passwords:
            logger.info(f"Trying {len(custom_passwords)} custom passwords...")

            for password in custom_passwords:
                if attempts >= max_attempts:
                    break

                attempts += 1
                self.total_attempts += 1

                if callback:
                    callback(attempts, password)

                # Test password
                if self.cracker.test_password(file_info.path, file_info.file_type, password):
                    file_info.found_password = password
                    file_info.is_cracked = True
                    self.successful_cracks += 1

                    attempt = PasswordAttempt(
                        password=password, attack_mode=AttackMode.CUSTOM, success=True
                    )
                    file_info.attempts.append(attempt)

                    logger.info(f"✓ Password found: '{password}' (custom password #{attempts})")
                    return True

        # Attack mode: Common passwords
        if AttackMode.COMMON in attack_modes:
            common_list = CommonPasswords.get_common_list(max_count=1000)
            logger.info(f"Trying {len(common_list)} common passwords...")

            for password in common_list:
                if attempts >= max_attempts:
                    break

                attempts += 1
                self.total_attempts += 1

                if callback:
                    callback(attempts, password)

                if self.cracker.test_password(file_info.path, file_info.file_type, password):
                    file_info.found_password = password
                    file_info.is_cracked = True
                    self.successful_cracks += 1

                    attempt = PasswordAttempt(
                        password=password, attack_mode=AttackMode.COMMON, success=True
                    )
                    file_info.attempts.append(attempt)

                    logger.info(f"✓ Password found: '{password}' (common password #{attempts})")
                    return True

        # Attack mode: Numeric brute-force
        if AttackMode.BRUTEFORCE_NUMERIC in attack_modes:
            logger.info("Starting numeric brute-force (4-8 digits)...")

            for password in CommonPasswords.generate_numeric_bruteforce(4, 8):
                if attempts >= max_attempts:
                    break

                attempts += 1
                self.total_attempts += 1

                if attempts % 100 == 0 and callback:
                    callback(attempts, password)

                if self.cracker.test_password(file_info.path, file_info.file_type, password):
                    file_info.found_password = password
                    file_info.is_cracked = True
                    self.successful_cracks += 1

                    attempt = PasswordAttempt(
                        password=password, attack_mode=AttackMode.BRUTEFORCE_NUMERIC, success=True
                    )
                    file_info.attempts.append(attempt)

                    logger.info(f"✓ Password found: '{password}' (numeric brute-force #{attempts})")
                    return True

        # Attack mode: Alpha brute-force (warning: very slow)
        if AttackMode.BRUTEFORCE_ALPHA in attack_modes:
            logger.warning("Alpha brute-force is very slow and may take hours/days!")
            logger.info("Starting alpha brute-force (4-6 characters)...")

            for password in CommonPasswords.generate_alpha_bruteforce(4, 6):
                if attempts >= max_attempts:
                    break

                attempts += 1
                self.total_attempts += 1

                if attempts % 1000 == 0 and callback:
                    callback(attempts, password)

                if self.cracker.test_password(file_info.path, file_info.file_type, password):
                    file_info.found_password = password
                    file_info.is_cracked = True
                    self.successful_cracks += 1

                    attempt = PasswordAttempt(
                        password=password, attack_mode=AttackMode.BRUTEFORCE_ALPHA, success=True
                    )
                    file_info.attempts.append(attempt)

                    logger.info(f"✓ Password found: '{password}' (alpha brute-force #{attempts})")
                    return True

        logger.warning(f"✗ Password not found after {attempts} attempts")
        return False

    def crack_multiple(
        self,
        protected_files: list[ProtectedFileInfo],
        custom_passwords: dict[str, list[str]] | None = None,
        attack_modes: list[AttackMode] | None = None,
        max_attempts_per_file: int = 10000,
    ) -> dict[str, bool]:
        """
        Crack passwords for multiple files (parallel processing).

        Args:
            protected_files: List of protected files
            custom_passwords: Dict of filename -> custom passwords
            attack_modes: Attack modes to use
            max_attempts_per_file: Max attempts per file

        Returns:
            Dict of filename -> success status
        """
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            for file_info in protected_files:
                filename = file_info.path.name
                custom_pwd = custom_passwords.get(filename, []) if custom_passwords else None

                future = executor.submit(
                    self.crack_password, file_info, custom_pwd, attack_modes, max_attempts_per_file
                )
                futures[future] = filename

            for future in as_completed(futures):
                filename = futures[future]
                try:
                    success = future.result()
                    results[filename] = success
                except Exception as e:
                    logger.error(f"Error cracking {filename}: {e}")
                    results[filename] = False

        return results

    def get_statistics(self) -> dict[str, any]:
        """Get scanner statistics."""
        return {
            "total_attempts": self.total_attempts,
            "successful_cracks": self.successful_cracks,
            "success_rate": (self.successful_cracks / max(self.total_attempts, 1)) * 100,
        }


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Create scanner
    scanner = EnhancedPasswordScanner(max_workers=4)

    # Example: Scan current directory
    current_dir = Path.cwd()

    print("=" * 70)
    print("Enhanced Password Scanner - Demo")
    print("=" * 70)
    print()

    # Scan for protected files
    print("Scanning for password-protected files...")
    scan_result = scanner.scan_directory(
        current_dir,
        recursive=False,  # Only current directory for demo
        file_extensions={".pdf", ".zip", ".rar", ".7z"},
    )

    print("\nScan Results:")
    print(f"  Files scanned: {scan_result.total_files_scanned}")
    print(f"  Protected files: {len(scan_result.protected_files)}")
    print(f"  Unprotected files: {scan_result.unprotected_files}")
    print(f"  Scan duration: {scan_result.scan_duration:.2f}s")

    if scan_result.protected_files:
        print("\nProtected Files Found:")
        for file_info in scan_result.protected_files:
            print(f"  • {file_info.path.name}")
            print(f"    Type: {file_info.file_type.value}")
            print(f"    Size: {file_info.size_bytes:,} bytes")
            print(f"    Encryption: {file_info.encryption_method}")

        # Demo: Try to crack passwords
        print("\n" + "=" * 70)
        print("Password Cracking Demo")
        print("=" * 70)

        # Example custom passwords
        custom_passwords = ["password", "123456", "test", "demo"]

        for file_info in scan_result.protected_files[:1]:  # Just first file for demo
            print(f"\nAttempting to crack: {file_info.path.name}")
            print(f"Custom passwords: {custom_passwords}")

            def progress_callback(attempts, password):
                if attempts % 100 == 0:
                    print(f"  Attempt {attempts}: trying '{password}'...")

            success = scanner.crack_password(
                file_info,
                custom_passwords=custom_passwords,
                attack_modes=[AttackMode.CUSTOM, AttackMode.COMMON],
                max_attempts=500,  # Limited for demo
                callback=progress_callback,
            )

            if success:
                print(f"\n✓ SUCCESS! Password found: '{file_info.found_password}'")
            else:
                print(f"\n✗ Password not found (tried {len(file_info.attempts)} passwords)")

    # Statistics
    print("\n" + "=" * 70)
    print("Statistics")
    print("=" * 70)
    stats = scanner.get_statistics()
    print(f"Total attempts: {stats['total_attempts']}")
    print(f"Successful cracks: {stats['successful_cracks']}")
    print(f"Success rate: {stats['success_rate']:.2f}%")
