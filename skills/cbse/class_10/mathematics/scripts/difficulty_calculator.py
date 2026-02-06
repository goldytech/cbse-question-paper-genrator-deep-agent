"""
Difficulty calculator for CBSE Question Paper Generator.

Ensures 40% easy, 40% medium, 20% hard difficulty distribution
across all questions in the question paper.
"""

from typing import List, Dict, Any


def calculate_difficulty_distribution(question_count: int) -> Dict[str, int]:
    """
    Calculate optimal difficulty distribution for a given number of questions.

    Follows CBSE guideline: 40% easy, 40% medium, 20% hard.

    Args:
        question_count: Total number of questions

    Returns:
        Dictionary with counts for easy, medium, hard

    Examples:
        >>> calculate_difficulty_distribution(20)
        {'easy': 8, 'medium': 8, 'hard': 4}

        >>> calculate_difficulty_distribution(15)
        {'easy': 6, 'medium': 6, 'hard': 3}
    """
    easy_count = int(question_count * 0.4)
    medium_count = int(question_count * 0.4)
    hard_count = question_count - easy_count - medium_count

    return {"easy": easy_count, "medium": medium_count, "hard": hard_count}


def adjust_distribution(current: Dict[str, int], target: Dict[str, int]) -> List[str]:
    """
    Determine which difficulties to add/remove to reach target distribution.

    Args:
        current: Current difficulty counts {'easy': n, 'medium': n, 'hard': n}
        target: Target difficulty counts

    Returns:
        List of difficulties to add (e.g., ['easy', 'medium', 'hard'])

    Examples:
        >>> adjust_distribution({'easy': 5, 'medium': 5, 'hard': 2}, {'easy': 8, 'medium': 8, 'hard': 4})
        ['easy', 'easy', 'easy', 'medium', 'medium', 'medium', 'hard', 'hard']
    """
    to_add = []

    for difficulty, target_count in target.items():
        current_count = current.get(difficulty, 0)
        needed = target_count - current_count

        for _ in range(max(0, needed)):
            to_add.append(difficulty)

    return to_add


def validate_distribution(distribution: Dict[str, int]) -> bool:
    """
    Validate if distribution follows 40/40/20 guideline.

    Args:
        distribution: Difficulty counts

    Returns:
        True if distribution is within acceptable range (~±10%)

    Examples:
        >>> validate_distribution({'easy': 8, 'medium': 8, 'hard': 4})
        True
    """
    total = sum(distribution.values())
    if total == 0:
        return False

    easy_pct = distribution.get("easy", 0) / total
    medium_pct = distribution.get("medium", 0) / total
    hard_pct = distribution.get("hard", 0) / total

    return 0.35 <= easy_pct <= 0.45 and 0.35 <= medium_pct <= 0.45 and 0.15 <= hard_pct <= 0.25


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        count = int(sys.argv[1])
        dist = calculate_difficulty_distribution(count)
        print(f"Distribution for {count} questions:")
        print(f"  Easy (40%): {dist['easy']}")
        print(f"  Medium (40%): {dist['medium']}")
        print(f"  Hard (20%): {dist['hard']}")
