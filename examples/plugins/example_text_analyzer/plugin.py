#!/usr/bin/env python3
"""
Text Analyzer Plugin
===================

Advanced text analysis with NLP: sentiment, keywords, language detection, statistics.
"""

import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "core"))

from plugin_system import PluginContext, PluginMetadata, PluginType, ProcessorPlugin


class TextAnalyzerPlugin(ProcessorPlugin):
    """Plugin for advanced text analysis."""

    def __init__(self):
        self.context = None
        self.common_words = {
            "the",
            "be",
            "to",
            "of",
            "and",
            "a",
            "in",
            "that",
            "have",
            "i",
            "it",
            "for",
            "not",
            "on",
            "with",
            "he",
            "as",
            "you",
            "do",
            "at",
        }

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="com.example.text-analyzer",
            name="Text Analyzer Plugin",
            version="1.0.0",
            author="File Processing Suite Team",
            description="Advanced text analysis: sentiment, keywords, language detection",
            plugin_type=PluginType.ANALYZER,
            supported_formats=[".txt", ".md", ".log", ".csv"],
            capabilities=["sentiment_analysis", "keyword_extraction", "statistics"],
        )

    def initialize(self, context: PluginContext) -> bool:
        try:
            self.context = context
            context.logger.info("Text Analyzer Plugin initialized")
            return True
        except Exception as e:
            if context:
                context.logger.error(f"Failed to initialize: {e}")
            return False

    def shutdown(self) -> bool:
        if self.context:
            self.context.logger.info("Text Analyzer Plugin shutting down")
        return True

    def can_process(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in [".txt", ".md", ".log", ".csv", ".json"]

    async def process(
        self, file_path: Path, context: PluginContext, **kwargs
    ) -> Dict[str, Any]:
        """Analyze text file.

        Args:
            file_path: Path to text file
            context: Plugin execution context
            **kwargs: Analysis options
                - operations: List of operations ['stats', 'keywords', 'sentiment', 'readability']
        """
        try:
            context.logger.info(f"Analyzing text file: {file_path}")

            # Read file
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="latin-1") as f:
                    text = f.read()

            operations = kwargs.get("operations", ["stats", "keywords", "sentiment"])
            results = {
                "success": True,
                "input_path": str(file_path),
                "file_size": file_path.stat().st_size,
            }

            # Basic statistics (always included)
            results["statistics"] = self._get_statistics(text)

            # Optional operations
            if "keywords" in operations:
                results["keywords"] = self._extract_keywords(text, context)

            if "sentiment" in operations:
                results["sentiment"] = self._analyze_sentiment(text)

            if "readability" in operations:
                results["readability"] = self._calculate_readability(text)

            if "patterns" in operations:
                results["patterns"] = self._find_patterns(text)

            return results

        except Exception as e:
            context.logger.error(f"Failed to analyze {file_path}: {e}")
            return {"success": False, "input_path": str(file_path), "error": str(e)}

    def _get_statistics(self, text: str) -> Dict[str, Any]:
        """Calculate basic text statistics."""
        # Character counts
        char_count = len(text)
        char_count_no_spaces = len(
            text.replace(" ", "").replace("\n", "").replace("\t", "")
        )

        # Word counts
        words = re.findall(r"\b\w+\b", text.lower())
        word_count = len(words)
        unique_words = len(set(words))

        # Line counts
        lines = text.split("\n")
        line_count = len(lines)
        non_empty_lines = len([l for l in lines if l.strip()])

        # Sentence counts (approximate)
        sentences = re.split(r"[.!?]+", text)
        sentence_count = len([s for s in sentences if s.strip()])

        # Paragraph counts
        paragraphs = re.split(r"\n\s*\n", text)
        paragraph_count = len([p for p in paragraphs if p.strip()])

        # Average word length
        avg_word_length = (
            sum(len(word) for word in words) / word_count if word_count > 0 else 0
        )

        # Average words per sentence
        avg_words_per_sentence = (
            word_count / sentence_count if sentence_count > 0 else 0
        )

        return {
            "characters": char_count,
            "characters_no_spaces": char_count_no_spaces,
            "words": word_count,
            "unique_words": unique_words,
            "lexical_diversity": (
                f"{(unique_words / word_count * 100):.2f}%" if word_count > 0 else "0%"
            ),
            "lines": line_count,
            "non_empty_lines": non_empty_lines,
            "sentences": sentence_count,
            "paragraphs": paragraph_count,
            "avg_word_length": f"{avg_word_length:.2f}",
            "avg_words_per_sentence": f"{avg_words_per_sentence:.2f}",
        }

    def _extract_keywords(self, text: str, context: PluginContext) -> Dict[str, Any]:
        """Extract keywords from text."""
        config = context.config
        min_length = config.get("min_word_length", 3)
        top_n = config.get("top_keywords", 10)

        # Tokenize and clean
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter: remove short words and common words
        filtered_words = [
            word
            for word in words
            if len(word) >= min_length and word not in self.common_words
        ]

        # Count frequencies
        word_freq = Counter(filtered_words)
        top_keywords = word_freq.most_common(top_n)

        return {
            "top_keywords": [
                {"word": word, "count": count} for word, count in top_keywords
            ],
            "total_unique_keywords": len(word_freq),
        }

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Perform basic sentiment analysis."""
        # Simple rule-based sentiment analysis
        positive_words = {
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "love",
            "best",
            "happy",
            "joy",
            "perfect",
            "brilliant",
            "awesome",
        }
        negative_words = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "hate",
            "worst",
            "sad",
            "angry",
            "poor",
            "disappointing",
            "fail",
            "failed",
        }

        words = set(re.findall(r"\b\w+\b", text.lower()))

        positive_count = len(words & positive_words)
        negative_count = len(words & negative_words)

        # Calculate sentiment score (-1 to 1)
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words > 0:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
        else:
            sentiment_score = 0

        # Classify sentiment
        if sentiment_score > 0.2:
            sentiment = "positive"
        elif sentiment_score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "score": f"{sentiment_score:.2f}",
            "positive_words": positive_count,
            "negative_words": negative_count,
            "confidence": "low",  # Simple method has low confidence
        }

    def _calculate_readability(self, text: str) -> Dict[str, Any]:
        """Calculate readability scores."""
        words = re.findall(r"\b\w+\b", text)
        sentences = re.split(r"[.!?]+", text)
        sentences = [s for s in sentences if s.strip()]

        word_count = len(words)
        sentence_count = len(sentences)

        if word_count == 0 or sentence_count == 0:
            return {"error": "Insufficient text for readability analysis"}

        # Count syllables (approximate)
        syllable_count = sum(self._count_syllables(word) for word in words)

        # Flesch Reading Ease
        # Score = 206.835 - 1.015 × (words/sentences) - 84.6 × (syllables/words)
        avg_words_per_sentence = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count

        flesch_score = (
            206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        )
        flesch_score = max(0, min(100, flesch_score))  # Clamp to 0-100

        # Interpret score
        if flesch_score >= 90:
            difficulty = "Very Easy"
        elif flesch_score >= 80:
            difficulty = "Easy"
        elif flesch_score >= 70:
            difficulty = "Fairly Easy"
        elif flesch_score >= 60:
            difficulty = "Standard"
        elif flesch_score >= 50:
            difficulty = "Fairly Difficult"
        elif flesch_score >= 30:
            difficulty = "Difficult"
        else:
            difficulty = "Very Difficult"

        # Flesch-Kincaid Grade Level (approximate)
        grade_level = (
            (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59
        )
        grade_level = max(0, grade_level)

        return {
            "flesch_reading_ease": f"{flesch_score:.1f}",
            "difficulty": difficulty,
            "grade_level": f"{grade_level:.1f}",
            "avg_words_per_sentence": f"{avg_words_per_sentence:.1f}",
            "avg_syllables_per_word": f"{avg_syllables_per_word:.2f}",
        }

    def _count_syllables(self, word: str) -> int:
        """Approximate syllable count."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Adjust for silent 'e'
        if word.endswith("e"):
            syllable_count -= 1

        # Every word has at least one syllable
        if syllable_count == 0:
            syllable_count = 1

        return syllable_count

    def _find_patterns(self, text: str) -> Dict[str, Any]:
        """Find common patterns in text."""
        patterns = {}

        # Email addresses
        emails = re.findall(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text
        )
        if emails:
            patterns["emails"] = list(set(emails))

        # URLs
        urls = re.findall(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            text,
        )
        if urls:
            patterns["urls"] = list(set(urls))

        # Phone numbers (simple pattern)
        phones = re.findall(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", text)
        if phones:
            patterns["phone_numbers"] = list(set(phones))

        # Dates (MM/DD/YYYY or DD/MM/YYYY)
        dates = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text)
        if dates:
            patterns["dates"] = list(set(dates))

        # Numbers
        numbers = re.findall(r"\b\d+\.\d+\b|\b\d+\b", text)
        if len(numbers) > 5:  # Only report if there are many numbers
            patterns["contains_many_numbers"] = len(numbers)

        return patterns if patterns else {"none_found": True}

    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            "status": "healthy",
            "message": "Plugin is operational",
            "algorithms": [
                "basic_stats",
                "keyword_extraction",
                "sentiment",
                "readability",
            ],
        }


Plugin = TextAnalyzerPlugin
