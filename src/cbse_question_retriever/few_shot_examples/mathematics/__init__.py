"""Mathematics few-shot examples for CBSE classes.

Routes to class-specific examples based on class level.
"""

from typing import Optional

from ..base import get_generic_examples


def get_examples(class_level: int) -> dict:
    """Get mathematics examples for a specific class.

    Args:
        class_level: Class number (6-12)

    Returns:
        Dictionary with examples by format: {"MCQ": [...], "VSA": [...], ...}
    """
    if class_level == 10:
        try:
            from .class_10 import get_class_10_examples

            return get_class_10_examples()
        except ImportError:
            pass

    return get_generic_examples()
