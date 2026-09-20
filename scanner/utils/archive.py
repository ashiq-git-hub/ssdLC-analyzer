"""
Secure archive handling utilities.

Provides safe extraction of ZIP archives with protection against:
- Path traversal attacks
- Absolute path injection
- Archive bombs (decompression bombs)
- Excessive file count
- Resource exhaustion
"""

import os
import zipfile
import shutil
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class ArchiveConfig:
    """Configuration for secure archive extraction."""
    max_file_size: int = 50 * 1024 * 1024  # 50 MB per file
    max_total_size: int = 250 * 1024 * 1024  # 250 MB total extracted
    max_file_count: int = 10000  # Max files in archive
    max_zip_size: int = 100 * 1024 * 1024  # 100 MB zip upload limit


class ArchiveSecurityError(Exception):
    """Raised when an archive violates security constraints."""
    pass


def validate_zip_path(target_dir: str, member_name: str) -> str:
    """
    Validate and construct a safe extraction path for a ZIP member.

    Args:
        target_dir: Base directory where archive will be extracted
        member_name: Name of the file inside the ZIP

    Returns:
        Safe absolute path for extraction

    Raises:
        ArchiveSecurityError: If the path would escape the target directory
    """
    # Normalize paths
    abs_target = os.path.abspath(target_dir)

    # Clean the member path
    # Remove leading slashes and drive letters
    cleaned_name = os.path.normpath(member_name)
    if cleaned_name.startswith(("/", "\\")):
        cleaned_name = cleaned_name.lstrip("/\\")

    # Handle Windows drive letters
    if len(cleaned_name) > 1 and cleaned_name[1] == ":":
        cleaned_name = cleaned_name[2:].lstrip("/\\")

    # Combine and resolve absolute path
    target_path = os.path.abspath(os.path.join(abs_target, cleaned_name))

    # Verify path doesn't escape target directory
    if not target_path.startswith(abs_target + os.sep) and target_path != abs_target:
        raise ArchiveSecurityError(
            f"Path traversal detected: {member_name} would extract outside target directory"
        )

    return target_path


def inspect_archive(zip_path: str, config: Optional[ArchiveConfig] = None) -> Tuple[int, int, List[str]]:
    """
    Inspect a ZIP archive without extracting it.

    Args:
        zip_path: Path to the ZIP file
        config: Security configuration

    Returns:
        Tuple of (file_count, total_uncompressed_size, list_of_filenames)

    Raises:
        ArchiveSecurityError: If archive violates security limits
        zipfile.BadZipFile: If file is not a valid ZIP
    """
    cfg = config or ArchiveConfig()

    # Check zip file size
    zip_size = os.path.getsize(zip_path)
    if zip_size > cfg.max_zip_size:
        raise ArchiveSecurityError(
            f"Archive size ({zip_size / 1024 / 1024:.1f} MB) exceeds maximum allowed size ({cfg.max_zip_size / 1024 / 1024:.1f} MB)"
        )

    file_count = 0
    total_size = 0
    filenames = []

    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            file_count += 1
            total_size += info.file_size
            filenames.append(info.filename)

            # Check individual file size
            if info.file_size > cfg.max_file_size:
                raise ArchiveSecurityError(
                    f"File {info.filename} ({info.file_size / 1024 / 1024:.1f} MB) exceeds maximum file size limit"
                )

            # Check running file count
            if file_count > cfg.max_file_count:
                raise ArchiveSecurityError(
                    f"Archive contains too many files (>{cfg.max_file_count})"
                )

            # Check running total size (compression bomb detection)
            if total_size > cfg.max_total_size:
                raise ArchiveSecurityError(
                    f"Extracted archive size would exceed maximum allowed size ({cfg.max_total_size / 1024 / 1024:.1f} MB)"
                )

    return file_count, total_size, filenames


def safe_extract_zip(
    zip_path: str,
    extract_to: str,
    config: Optional[ArchiveConfig] = None
) -> str:
    """
    Safely extract a ZIP archive to a destination directory.

    Args:
        zip_path: Path to the ZIP file
        extract_to: Directory to extract into
        config: Security configuration

    Returns:
        Path to the root of the extracted project

    Raises:
        ArchiveSecurityError: If the archive violates security policies
        zipfile.BadZipFile: If the archive is corrupt
    """
    cfg = config or ArchiveConfig()

    # Pre-validate the archive
    inspect_archive(zip_path, cfg)

    os.makedirs(extract_to, exist_ok=True)
    abs_extract_to = os.path.abspath(extract_to)

    extracted_files = 0
    extracted_bytes = 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            # Validate path
            safe_path = validate_zip_path(abs_extract_to, member.filename)

            # Skip directories, they will be created as needed
            if member.is_dir() or member.filename.endswith(("/", "\\")):
                os.makedirs(safe_path, exist_ok=True)
                continue

            # Ensure parent directory exists
            os.makedirs(os.path.dirname(safe_path), exist_ok=True)

            # Safe extraction with size tracking
            with zf.open(member) as source, open(safe_path, "wb") as target:
                while True:
                    chunk = source.read(65536)  # 64KB chunks
                    if not chunk:
                        break
                    extracted_bytes += len(chunk)
                    if extracted_bytes > cfg.max_total_size:
                        raise ArchiveSecurityError("Archive exceeded total size limit during extraction")
                    target.write(chunk)

            extracted_files += 1

    # Check if there's a single top-level directory (common in github archives)
    entries = os.listdir(abs_extract_to)
    if len(entries) == 1:
        single_dir = os.path.join(abs_extract_to, entries[0])
        if os.path.isdir(single_dir):
            return single_dir

    return abs_extract_to
