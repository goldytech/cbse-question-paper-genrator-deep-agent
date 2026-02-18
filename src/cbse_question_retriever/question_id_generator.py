"""Question ID generator following CBSE format."""

import logging

from .data_types import (
    CHAPTER_ABBREVIATIONS,
    FORMAT_ABBREVIATIONS,
    SUBJECT_ABBREVIATIONS,
)

logger = logging.getLogger(__name__)


class QuestionIDGenerator:
    """Generates question IDs in format: SUBJECT-CLASS-CHAPTER-FORMAT-NUM"""

    def generate_id(
        self,
        subject: str,
        class_level: int,
        chapter: str,
        question_format: str,
        question_number: int,
    ) -> str:
        """Generate question ID.

        Format: {SUBJECT}-{CLASS}-{CHAPTER_ABBR}-{FORMAT_ABBR}-{NUM}
        Example: MATH-10-POL-MCQ-001

        Args:
            subject: Subject name (e.g., "Mathematics")
            class_level: Class number (e.g., 10)
            chapter: Chapter name (e.g., "Polynomials")
            question_format: Format (e.g., "MCQ", "SHORT")
            question_number: Question number within section (1-based)

        Returns:
            Formatted question ID string
        """
        # Get abbreviations
        subject_abbr = self._get_subject_abbreviation(subject)
        chapter_abbr = self._get_chapter_abbreviation(chapter)
        format_abbr = self._get_format_abbreviation(question_format)

        # Format number with zero padding
        num_str = f"{question_number:03d}"

        # Build ID
        question_id = f"{subject_abbr}-{class_level}-{chapter_abbr}-{format_abbr}-{num_str}"

        logger.debug(f"Generated question ID: {question_id}")

        return question_id

    def _get_subject_abbreviation(self, subject: str) -> str:
        """Get subject abbreviation."""
        subject_lower = subject.lower().strip()
        return SUBJECT_ABBREVIATIONS.get(subject_lower, subject[:4].upper())

    def _get_chapter_abbreviation(self, chapter: str) -> str:
        """Get chapter abbreviation."""
        chapter_lower = chapter.lower().strip()
        return CHAPTER_ABBREVIATIONS.get(chapter_lower, self._generate_abbr(chapter))

    def _get_format_abbreviation(self, question_format: str) -> str:
        """Get format abbreviation."""
        format_upper = question_format.upper().strip()
        return FORMAT_ABBREVIATIONS.get(format_upper, format_upper[:3])

    def _generate_abbr(self, text: str) -> str:
        """Generate abbreviation from text.

        Takes first letter of each word (up to 4 letters).
        Example: "Linear Equations" -> "LINE"
        """
        words = text.split()
        abbr = "".join(word[0].upper() for word in words if word)
        return abbr[:4] if len(abbr) > 4 else abbr


# Global question ID generator instance
question_id_generator = QuestionIDGenerator()
