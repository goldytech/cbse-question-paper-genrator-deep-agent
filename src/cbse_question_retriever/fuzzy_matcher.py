"""Fuzzy matching for topic names using rapidfuzz."""

import logging
from typing import List, Optional, Tuple

from rapidfuzz import fuzz, process

from cbse_question_retriever.settings import settings

logger = logging.getLogger(__name__)


class FuzzyTopicMatcher:
    """Matches query topics to available topics using fuzzy matching."""

    def __init__(self, threshold: int = 80):
        """Initialize matcher with threshold.

        Args:
            threshold: Minimum match score (0-100). Defaults to 80.
        """
        self.threshold = threshold

    def find_best_match(
        self, query: str, available_topics: List[str], limit: int = 3
    ) -> Tuple[Optional[str], float, List[str]]:
        """Find best matching topic using fuzzy matching.

        Args:
            query: Query topic name
            available_topics: List of available topic names
            limit: Number of top matches to return

        Returns:
            Tuple of (best_match, score, suggestions)
            - best_match: Best matching topic or None if below threshold
            - score: Match score (0-100)
            - suggestions: List of top matching topics
        """
        if not available_topics:
            return None, 0.0, []

        # Use rapidfuzz to find best matches
        matches = process.extract(query, available_topics, scorer=fuzz.ratio, limit=limit)

        if not matches:
            return None, 0.0, []

        best_match, score, _ = matches[0]

        # Extract all suggestions
        suggestions = [match[0] for match in matches]

        # Return best match only if above threshold
        if score >= self.threshold:
            return best_match, float(score), suggestions
        else:
            return None, float(score), suggestions

    def find_matches_batch(
        self,
        queries: List[str],
        available_topics: List[str],
    ) -> List[Tuple[Optional[str], float]]:
        """Find matches for multiple queries.

        Args:
            queries: List of query topics
            available_topics: List of available topics

        Returns:
            List of (best_match, score) tuples
        """
        results = []
        for query in queries:
            match, score, _ = self.find_best_match(query, available_topics, limit=1)
            results.append((match, score))
        return results


# Global fuzzy matcher instance
fuzzy_matcher = FuzzyTopicMatcher()
