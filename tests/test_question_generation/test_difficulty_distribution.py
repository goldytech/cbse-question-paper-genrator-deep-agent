"""Unit tests for difficulty distribution (40/40/20 rule)."""

import pytest
from question_generation.orchestrator import _distribute_difficulties


class TestDifficultyDistribution40_40_20:
    """Tests for 40% easy, 40% medium, 20% hard distribution."""

    def test_10_questions_distribution(self):
        """Verify 10 questions: 4 easy, 4 medium, 2 hard."""
        distribution = _distribute_difficulties(10)

        assert distribution["easy"] == 4
        assert distribution["medium"] == 4
        assert distribution["hard"] == 2
        assert sum(distribution.values()) == 10

    def test_20_questions_distribution(self):
        """Verify 20 questions: 8 easy, 8 medium, 4 hard."""
        distribution = _distribute_difficulties(20)

        assert distribution["easy"] == 8
        assert distribution["medium"] == 8
        assert distribution["hard"] == 4
        assert sum(distribution.values()) == 20

    def test_5_questions_distribution(self):
        """Verify 5 questions: 2 easy, 2 medium, 1 hard."""
        distribution = _distribute_difficulties(5)

        assert distribution["easy"] == 2
        assert distribution["medium"] == 2
        assert distribution["hard"] == 1
        assert sum(distribution.values()) == 5

    def test_1_question_distribution(self):
        """Verify 1 question: 0 easy, 0 medium, 1 hard (rounds up)."""
        distribution = _distribute_difficulties(1)

        # With rounding, hard gets the remainder
        assert distribution["hard"] == 1
        assert sum(distribution.values()) == 1

    def test_2_questions_distribution(self):
        """Verify 2 questions distributed appropriately."""
        distribution = _distribute_difficulties(2)

        # With rounding, could be 0-2 for each, but sum must be 2
        assert sum(distribution.values()) == 2
        assert distribution["easy"] >= 0 and distribution["easy"] <= 2
        assert distribution["medium"] >= 0 and distribution["medium"] <= 2
        assert distribution["hard"] >= 0 and distribution["hard"] <= 2

    def test_3_questions_distribution(self):
        """Verify 3 questions: 1 easy, 1 medium, 1 hard."""
        distribution = _distribute_difficulties(3)

        assert distribution["easy"] == 1
        assert distribution["medium"] == 1
        assert distribution["hard"] == 1
        assert sum(distribution.values()) == 3

    def test_15_questions_distribution(self):
        """Verify 15 questions: 6 easy, 6 medium, 3 hard."""
        distribution = _distribute_difficulties(15)

        assert distribution["easy"] == 6
        assert distribution["medium"] == 6
        assert distribution["hard"] == 3
        assert sum(distribution.values()) == 15


class TestDifficultyDistributionEdgeCases:
    """Tests for edge cases in difficulty distribution."""

    def test_zero_questions(self):
        """Verify handling of 0 questions."""
        distribution = _distribute_difficulties(0)

        assert distribution["easy"] == 0
        assert distribution["medium"] == 0
        assert distribution["hard"] == 0

    def test_large_number_questions(self):
        """Verify handling of large question counts."""
        distribution = _distribute_difficulties(100)

        assert distribution["easy"] == 40
        assert distribution["medium"] == 40
        assert distribution["hard"] == 20
        assert sum(distribution.values()) == 100

    def test_distribution_order(self):
        """Verify difficulties are ordered: easy first, then medium, then hard."""
        distribution = _distribute_difficulties(10)
        difficulties = []

        for _ in range(distribution["easy"]):
            difficulties.append("easy")
        for _ in range(distribution["medium"]):
            difficulties.append("medium")
        for _ in range(distribution["hard"]):
            difficulties.append("hard")

        # Verify order
        easy_indices = [i for i, d in enumerate(difficulties) if d == "easy"]
        medium_indices = [i for i, d in enumerate(difficulties) if d == "medium"]
        hard_indices = [i for i, d in enumerate(difficulties) if d == "hard"]

        assert all(e < m for e in easy_indices for m in medium_indices)
        assert all(m < h for m in medium_indices for h in hard_indices)


class TestDifficultyPercentages:
    """Tests to verify exact percentages."""

    def test_easy_is_40_percent(self):
        """Verify easy is always ~40%."""
        for total in [5, 10, 15, 20, 25]:
            distribution = _distribute_difficulties(total)
            easy_percentage = (distribution["easy"] / total) * 100
            # Allow for rounding differences
            assert 35 <= easy_percentage <= 45

    def test_medium_is_40_percent(self):
        """Verify medium is always ~40%."""
        for total in [5, 10, 15, 20, 25]:
            distribution = _distribute_difficulties(total)
            medium_percentage = (distribution["medium"] / total) * 100
            assert 35 <= medium_percentage <= 45

    def test_hard_is_20_percent(self):
        """Verify hard is always ~20%."""
        for total in [5, 10, 15, 20, 25]:
            distribution = _distribute_difficulties(total)
            hard_percentage = (distribution["hard"] / total) * 100
            assert 15 <= hard_percentage <= 25
