"""Few-shot examples for LLM question generation.

Provides subject-specific and class-specific examples for different CBSE subjects.
"""

from typing import Optional

from .base import get_generic_examples


def get_examples_for_subject(subject: str, class_level: int) -> dict:
    """Get few-shot examples for a specific subject and class.

    Args:
        subject: Subject name (e.g., "mathematics", "science")
        class_level: Class number (e.g., 10)

    Returns:
        Dictionary with examples by format: {"MCQ": [...], "VSA": [...], ...}
    """
    subject_lower = subject.lower().strip()

    if subject_lower == "mathematics":
        try:
            from .mathematics import get_examples

            return get_examples(class_level)
        except ImportError:
            pass

    return get_generic_examples()
