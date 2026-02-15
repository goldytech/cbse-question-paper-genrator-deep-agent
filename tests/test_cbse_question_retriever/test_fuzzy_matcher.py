"""Tests for fuzzy topic matcher."""

import pytest
from cbse_question_retriever.fuzzy_matcher import FuzzyTopicMatcher


class TestFuzzyTopicMatcher:
    """Test suite for fuzzy topic matching."""

    def test_exact_match(self):
        """Test exact topic matching."""
        matcher = FuzzyTopicMatcher(threshold=80)
        available = ["Zeros of a Polynomial", "Graphical Method", "Euclid's Division Algorithm"]

        match, score, suggestions = matcher.find_best_match("Zeros of a Polynomial", available)

        assert match == "Zeros of a Polynomial"
        assert score == 100.0
        assert len(suggestions) > 0

    def test_typo_match(self):
        """Test matching with typos."""
        matcher = FuzzyTopicMatcher(threshold=80)
        available = ["Zeros of a Polynomial", "Graphical Method", "Euclid's Division Algorithm"]

        match, score, suggestions = matcher.find_best_match("Zeroes of Polynomial", available)

        assert match == "Zeros of a Polynomial"
        assert score >= 80

    def test_no_match_below_threshold(self):
        """Test that low scores return None."""
        matcher = FuzzyTopicMatcher(threshold=80)
        available = ["Zeros of a Polynomial", "Graphical Method"]

        match, score, suggestions = matcher.find_best_match("Completely Different Topic", available)

        assert match is None
        assert score < 80
        assert len(suggestions) > 0

    def test_case_insensitive(self):
        """Test case insensitive matching."""
        matcher = FuzzyTopicMatcher(threshold=80)
        available = ["Zeros of a Polynomial"]

        match, score, _ = matcher.find_best_match("zeros of a polynomial", available)

        assert match == "Zeros of a Polynomial"

    def test_partial_match(self):
        """Test partial/topic name matching."""
        matcher = FuzzyTopicMatcher(threshold=60)  # Lower threshold for partial
        available = [
            "Relationship between Zeroes and Coefficients",
            "Geometrical Meaning of Zeroes",
            "Zeros of a Polynomial",
        ]

        match, score, _ = matcher.find_best_match("Zeroes and Coefficients", available)

        assert match is not None
        assert score >= 60


class TestFuzzyMatcherBatch:
    """Test batch matching."""

    def test_batch_matching(self):
        """Test matching multiple queries at once."""
        matcher = FuzzyTopicMatcher(threshold=70)
        queries = ["Zeros of Polynomial", "Graphical Method", "Euclid Algorithm"]
        available = ["Zeros of a Polynomial", "Graphical Method", "Euclid's Division Algorithm"]

        results = matcher.find_matches_batch(queries, available)

        assert len(results) == 3
        assert all(match is not None for match, _ in results)
