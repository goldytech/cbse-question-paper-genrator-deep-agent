"""Tests for question ID generator."""

import pytest
from cbse_question_retriever.question_id_generator import question_id_generator


class TestQuestionIDGenerator:
    """Test suite for question ID generation."""

    def test_mcq_id_format(self):
        """Test MCQ question ID format."""
        qid = question_id_generator.generate_id(
            subject="Mathematics",
            class_level=10,
            chapter="Polynomials",
            question_format="MCQ",
            question_number=1,
        )

        assert qid == "MATH-10-POL-MCQ-001"

    def test_short_id_format(self):
        """Test SHORT question ID format."""
        qid = question_id_generator.generate_id(
            subject="Mathematics",
            class_level=10,
            chapter="Real Numbers",
            question_format="SHORT",
            question_number=5,
        )

        assert qid == "MATH-10-REA-SA-005"

    def test_long_id_format(self):
        """Test LONG question ID format."""
        qid = question_id_generator.generate_id(
            subject="Mathematics",
            class_level=10,
            chapter="Triangles",
            question_format="LONG",
            question_number=12,
        )

        assert qid == "MATH-10-TRI-LA-012"

    def test_number_padding(self):
        """Test that numbers are zero-padded to 3 digits."""
        qid_1 = question_id_generator.generate_id(
            subject="Mathematics",
            class_level=10,
            chapter="Polynomials",
            question_format="MCQ",
            question_number=1,
        )
        qid_99 = question_id_generator.generate_id(
            subject="Mathematics",
            class_level=10,
            chapter="Polynomials",
            question_format="MCQ",
            question_number=99,
        )

        assert qid_1.endswith("-001")
        assert qid_99.endswith("-099")

    def test_unknown_chapter(self):
        """Test ID generation for unknown chapter."""
        qid = question_id_generator.generate_id(
            subject="Mathematics",
            class_level=10,
            chapter="Unknown Chapter Name",
            question_format="MCQ",
            question_number=1,
        )

        # Should generate abbreviation from chapter name (UCN = Unknown Chapter Name)
        assert "UCN" in qid

    def test_case_insensitive_subject(self):
        """Test case insensitive subject handling."""
        qid1 = question_id_generator.generate_id(
            subject="mathematics",
            class_level=10,
            chapter="Polynomials",
            question_format="MCQ",
            question_number=1,
        )
        qid2 = question_id_generator.generate_id(
            subject="MATHEMATICS",
            class_level=10,
            chapter="Polynomials",
            question_format="MCQ",
            question_number=1,
        )

        assert qid1 == qid2
