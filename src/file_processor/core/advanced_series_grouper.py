"""
Advanced Series Grouping Module
===============================
Intelligent file grouping based on similarity, series detection, and content analysis.
Supports both filename-based and content-based similarity matching.

This module provides advanced series detection and grouping capabilities using
multiple algorithms and configurable similarity thresholds.
"""

from dataclasses import dataclass
import difflib
import os
from pathlib import Path
import re
import shutil
from typing import Any


@dataclass
class SeriesGroup:
    """Represents a group of related files in a series."""

    series_name: str
    files: list[Path]
    similarity_score: float
    group_type: str  # 'filename', 'content', 'hybrid'
    suggested_folder: str
    volume_info: dict[str, Any] | None = None

    def __post_init__(self):
        if self.volume_info is None:
            self.volume_info = {}


@dataclass
class GroupingResult:
    """Result of series grouping operation."""

    groups_created: int
    files_grouped: int
    ungrouped_files: int
    groups: list[SeriesGroup]
    processing_time: float
    method_used: str


class AdvancedSeriesGrouper:
    """
    Advanced series grouping with multiple detection methods.

    Features:
    - Filename similarity analysis
    - Volume/chapter/episode detection
    - Configurable similarity thresholds
    - Multiple grouping strategies
    - Series folder creation and management
    - Cross-platform compatibility
    """

    def __init__(
        self,
        similarity_threshold: float = 0.8,
        min_group_size: int = 2,
        max_group_size: int = 100,
        log_callback=None,
    ):
        """
        Initialize the series grouper.

        Args:
            similarity_threshold: Minimum similarity score for grouping (0.0-1.0)
            min_group_size: Minimum number of files to form a group
            max_group_size: Maximum number of files in a single group
            log_callback: Function to call for logging messages
        """
        self.similarity_threshold = similarity_threshold
        self.min_group_size = min_group_size
        self.max_group_size = max_group_size
        self.log_callback = log_callback or print

        # Series detection patterns
        self.series_patterns = self._get_series_patterns()

        # Common words to ignore in similarity matching
        self.stop_words = self._get_stop_words()

    def _get_series_patterns(self) -> list[tuple[str, str]]:
        """Get patterns for detecting series information."""
        return [
            # Volume patterns
            (r"(?i)vol(?:ume)?[\s._-]*(\d+)", "volume"),
            (r"(?i)v(\d+)", "volume"),
            (r"(?i)tome[\s._-]*(\d+)", "volume"),
            # Chapter patterns
            (r"(?i)ch(?:apter)?[\s._-]*(\d+)", "chapter"),
            (r"(?i)c(\d+)", "chapter"),
            (r"(?i)chapitre[\s._-]*(\d+)", "chapter"),
            # Part patterns
            (r"(?i)part[\s._-]*(\d+)", "part"),
            (r"(?i)partie[\s._-]*(\d+)", "part"),
            (r"(?i)pt[\s._-]*(\d+)", "part"),
            # Episode patterns
            (r"(?i)ep(?:isode)?[\s._-]*(\d+)", "episode"),
            (r"(?i)e(\d+)", "episode"),
            (r"(?i)episode[\s._-]*(\d+)", "episode"),
            # Season patterns
            (r"(?i)season[\s._-]*(\d+)", "season"),
            (r"(?i)s(\d+)", "season"),
            (r"(?i)saison[\s._-]*(\d+)", "season"),
            # Combined patterns
            (r"(?i)s(\d+)e(\d+)", "season_episode"),  # S01E01
            (r"(?i)(\d+)x(\d+)", "season_episode"),  # 1x01
            # Generic number patterns
            (r"\b(\d{1,3})\b", "number"),
            (r"(?i)no[\s._-]*(\d+)", "number"),
            (r"(?i)#(\d+)", "number"),
        ]

    def _get_stop_words(self) -> set[str]:
        """Get common words to ignore in similarity matching."""
        return {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "a",
            "an",
            "as",
            "is",
            "was",
            "are",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "must",
            "shall",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "its",
            "our",
            "their",
            "ch",
            "vol",
            "volume",
            "chapter",
            "part",
            "episode",
            "ep",
            "season",
            "s",
            "e",
            "no",
            "number",
            "tome",
            "chapitre",
            "partie",
            "saison",
            "pt",
        }

    def extract_series_info(self, filename: str) -> dict[str, Any]:
        """
        Extract series information from filename.

        Args:
            filename: Filename to analyze

        Returns:
            Dictionary with extracted series information
        """
        # Remove file extension
        name_without_ext = os.path.splitext(filename)[0]

        # Remove date prefix if present
        name_clean = re.sub(r"^\d{8}_", "", name_without_ext)

        series_info = {
            "base_name": name_clean,
            "volume": None,
            "chapter": None,
            "part": None,
            "episode": None,
            "season": None,
            "number": None,
            "is_series": False,
            "series_indicators": [],
        }

        # Apply patterns to extract series information
        for pattern, info_type in self.series_patterns:
            matches = re.finditer(pattern, name_clean)
            for match in matches:
                series_info["is_series"] = True
                series_info["series_indicators"].append(info_type)

                if info_type == "season_episode":
                    # Handle combined season/episode patterns
                    groups = match.groups()
                    if len(groups) >= 2:
                        series_info["season"] = int(groups[0])
                        series_info["episode"] = int(groups[1])
                elif len(match.groups()) >= 1:
                    try:
                        value = int(match.group(1))
                        if series_info[info_type] is None:
                            series_info[info_type] = value
                    except (ValueError, KeyError):
                        continue

        # Extract base series name (remove series indicators)
        base_name = name_clean
        for pattern, _ in self.series_patterns:
            base_name = re.sub(pattern, "", base_name)

        # Clean up the base name
        base_name = re.sub(r"[_\s-]+", " ", base_name).strip()
        series_info["base_name"] = base_name

        return series_info

    def calculate_filename_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two filenames.

        Args:
            name1: First filename
            name2: Second filename

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Extract base names without series indicators
        info1 = self.extract_series_info(name1)
        info2 = self.extract_series_info(name2)

        base1 = info1["base_name"].lower()
        base2 = info2["base_name"].lower()

        # Remove stop words
        words1 = {
            word for word in re.split(r"[_\s-]+", base1) if word and word not in self.stop_words
        }
        words2 = {
            word for word in re.split(r"[_\s-]+", base2) if word and word not in self.stop_words
        }

        # If no meaningful words remain, fall back to full name comparison
        if not words1 or not words2:
            return difflib.SequenceMatcher(None, base1, base2).ratio()

        # Calculate word-level similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        if union == 0:
            return 0.0

        word_similarity = intersection / union

        # Calculate character-level similarity for additional precision
        char_similarity = difflib.SequenceMatcher(None, base1, base2).ratio()

        # Combine both similarities (weighted toward word similarity)
        combined_similarity = (word_similarity * 0.7) + (char_similarity * 0.3)

        return combined_similarity

    def find_similar_groups(self, files: list[Path]) -> list[list[Path]]:
        """
        Find groups of similar files based on filename analysis.

        Args:
            files: List of file paths to analyze

        Returns:
            List of file groups
        """
        if len(files) < self.min_group_size:
            return []

        groups = []
        processed = set()

        for i, file1 in enumerate(files):
            if file1 in processed:
                continue

            current_group = [file1]
            processed.add(file1)

            for _j, file2 in enumerate(files[i + 1 :], i + 1):
                if file2 in processed:
                    continue

                similarity = self.calculate_filename_similarity(file1.name, file2.name)

                if similarity >= self.similarity_threshold:
                    current_group.append(file2)
                    processed.add(file2)

            # Only keep groups that meet minimum size requirement
            if len(current_group) >= self.min_group_size:
                groups.append(current_group[: self.max_group_size])

        return groups

    def create_series_folder_name(self, group: list[Path]) -> str:
        """
        Create an appropriate folder name for a series group.

        Args:
            group: List of files in the group

        Returns:
            Suggested folder name
        """
        if not group:
            return "series_unknown"

        # Extract series info from all files
        series_infos = [self.extract_series_info(f.name) for f in group]

        # Find the most common base name
        base_names = [info["base_name"] for info in series_infos if info["base_name"]]

        if base_names:
            # Use the longest common base name
            common_base = os.path.commonprefix(base_names).strip()
            if len(common_base) < 3:
                # If common prefix is too short, use the most frequent base name
                from collections import Counter

                counter = Counter(base_names)
                common_base = counter.most_common(1)[0][0]
        else:
            common_base = "series"

        # Clean up the base name for folder use
        folder_name = re.sub(r"[^\w\s-]", "", common_base)
        folder_name = re.sub(r"\s+", "_", folder_name.strip())

        # Add series indicator
        folder_name = f"series_{folder_name}" if folder_name else "series_unknown"

        return folder_name[:50]  # Limit folder name length

    def group_files_in_directory(
        self, directory: Path, create_folders: bool = True, move_files: bool = True
    ) -> GroupingResult:
        """
        Group similar files in a directory into series folders.

        Args:
            directory: Directory to process
            create_folders: Whether to create series folders
            move_files: Whether to move files into series folders

        Returns:
            GroupingResult with operation details
        """
        import time

        start_time = time.time()

        try:
            # Get all files in directory
            files = [f for f in directory.iterdir() if f.is_file()]

            if len(files) < self.min_group_size:
                return GroupingResult(
                    groups_created=0,
                    files_grouped=0,
                    ungrouped_files=len(files),
                    groups=[],
                    processing_time=time.time() - start_time,
                    method_used="insufficient_files",
                )

            # Find similar groups
            similar_groups = self.find_similar_groups(files)

            series_groups = []
            files_grouped = 0

            for group in similar_groups:
                if len(group) < self.min_group_size:
                    continue

                # Create series folder name
                folder_name = self.create_series_folder_name(group)
                series_folder = directory / folder_name

                # Calculate average similarity for the group
                total_similarity = 0
                comparisons = 0
                for i, file1 in enumerate(group):
                    for file2 in group[i + 1 :]:
                        total_similarity += self.calculate_filename_similarity(
                            file1.name, file2.name
                        )
                        comparisons += 1

                avg_similarity = total_similarity / comparisons if comparisons > 0 else 0.0

                # Create SeriesGroup object
                series_group = SeriesGroup(
                    series_name=folder_name,
                    files=group,
                    similarity_score=avg_similarity,
                    group_type="filename",
                    suggested_folder=str(series_folder),
                )

                series_groups.append(series_group)

                # Create folder and move files if requested
                if create_folders and move_files:
                    try:
                        series_folder.mkdir(exist_ok=True)

                        for file_path in group:
                            dest_path = series_folder / file_path.name
                            if not dest_path.exists():
                                shutil.move(str(file_path), str(dest_path))
                                files_grouped += 1
                                self.log_callback(f"Moved {file_path.name} to {folder_name}")
                            else:
                                self.log_callback(
                                    f"File already exists in destination: {file_path.name}"
                                )

                    except Exception as e:
                        self.log_callback(f"Error creating series folder {folder_name}: {e}")
                        continue
                else:
                    files_grouped += len(group)

            processing_time = time.time() - start_time
            ungrouped_files = len(files) - files_grouped

            return GroupingResult(
                groups_created=len(series_groups),
                files_grouped=files_grouped,
                ungrouped_files=ungrouped_files,
                groups=series_groups,
                processing_time=processing_time,
                method_used="filename_similarity",
            )

        except Exception as e:
            self.log_callback(f"Error grouping files in {directory}: {e}")
            return GroupingResult(
                groups_created=0,
                files_grouped=0,
                ungrouped_files=0,
                groups=[],
                processing_time=time.time() - start_time,
                method_used="error",
            )

    def batch_group_directories(
        self, directories: list[Path], create_folders: bool = True, move_files: bool = True
    ) -> dict[str, GroupingResult]:
        """
        Group files in multiple directories.

        Args:
            directories: List of directories to process
            create_folders: Whether to create series folders
            move_files: Whether to move files into series folders

        Returns:
            Dictionary mapping directory paths to grouping results
        """
        results = {}

        for directory in directories:
            if not directory.exists() or not directory.is_dir():
                self.log_callback(f"Skipping invalid directory: {directory}")
                continue

            try:
                result = self.group_files_in_directory(
                    directory, create_folders=create_folders, move_files=move_files
                )
                results[str(directory)] = result

                self.log_callback(
                    f"Processed {directory}: {result.groups_created} groups, "
                    f"{result.files_grouped} files grouped in {result.processing_time:.2f}s"
                )

            except Exception as e:
                self.log_callback(f"Error processing directory {directory}: {e}")
                results[str(directory)] = GroupingResult(
                    groups_created=0,
                    files_grouped=0,
                    ungrouped_files=0,
                    groups=[],
                    processing_time=0.0,
                    method_used="error",
                )

        return results

    def cleanup_empty_directories(self, base_directory: Path) -> int:
        """
        Remove empty directories after grouping operations.

        Args:
            base_directory: Base directory to clean up

        Returns:
            Number of directories removed
        """
        removed_count = 0

        try:
            # Walk through directories bottom-up
            for root, dirs, _files in os.walk(str(base_directory), topdown=False):
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    try:
                        # Check if directory is empty
                        if not any(dir_path.iterdir()):
                            dir_path.rmdir()
                            removed_count += 1
                            self.log_callback(f"Removed empty directory: {dir_path}")
                    except Exception as e:
                        self.log_callback(f"Error removing directory {dir_path}: {e}")

        except Exception as e:
            self.log_callback(f"Error during cleanup: {e}")

        return removed_count

    def get_grouping_stats(self) -> dict[str, Any]:
        """Get grouping statistics and configuration."""
        return {
            "similarity_threshold": self.similarity_threshold,
            "min_group_size": self.min_group_size,
            "max_group_size": self.max_group_size,
            "series_patterns_count": len(self.series_patterns),
            "stop_words_count": len(self.stop_words),
            "supported_indicators": list({pattern[1] for pattern in self.series_patterns}),
        }
