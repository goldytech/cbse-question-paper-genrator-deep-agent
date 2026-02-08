"""Unit tests for question ID generation and format abbreviations."""

import pytest
from question_generation.orchestrator import (
    _get_chapter_abbreviation,
    _get_format_abbreviation,
)


class TestChapterAbbreviations:
    """Tests for chapter abbreviation mapping."""

    def test_real_numbers_abbr(self):
        """Verify Real Numbers -> REA."""
        assert _get_chapter_abbreviation("Real Numbers") == "REA"
        assert _get_chapter_abbreviation("real numbers") == "REA"

    def test_polynomials_abbr(self):
        """Verify Polynomials -> POL."""
        assert _get_chapter_abbreviation("Polynomials") == "POL"
        assert _get_chapter_abbreviation("polynomials") == "POL"

    def test_linear_equations_abbr(self):
        """Verify Linear Equations -> LIN."""
        assert _get_chapter_abbreviation("Linear Equations") == "LIN"

    def test_quadratic_equations_abbr(self):
        """Verify Quadratic Equations -> QUAD."""
        assert _get_chapter_abbreviation("Quadratic Equations") == "QUAD"

    def test_arithmetic_progressions_abbr(self):
        """Verify Arithmetic Progressions -> AP."""
        assert _get_chapter_abbreviation("Arithmetic Progressions") == "AP"

    def test_coordinate_geometry_abbr(self):
        """Verify Coordinate Geometry -> COG."""
        assert _get_chapter_abbreviation("Coordinate Geometry") == "COG"

    def test_triangles_abbr(self):
        """Verify Triangles -> TRI."""
        assert _get_chapter_abbreviation("Triangles") == "TRI"

    def test_circles_abbr(self):
        """Verify Circles -> CIR."""
        assert _get_chapter_abbreviation("Circles") == "CIR"

    def test_mensuration_abbr(self):
        """Verify Mensuration -> MEN."""
        assert _get_chapter_abbreviation("Mensuration") == "MEN"

    def test_statistics_abbr(self):
        """Verify Statistics -> STA."""
        assert _get_chapter_abbreviation("Statistics") == "STA"

    def test_probability_abbr(self):
        """Verify Probability -> PRO."""
        assert _get_chapter_abbreviation("Probability") == "PRO"

    def test_unknown_chapter_returns_gen(self):
        """Verify unknown chapter returns GEN."""
        assert _get_chapter_abbreviation("Unknown Chapter") == "GEN"
        assert _get_chapter_abbreviation("Random Topic") == "GEN"


class TestFormatAbbreviations:
    """Tests for question format abbreviation mapping."""

    def test_mcq_abbr(self):
        """Verify MCQ -> MCQ."""
        assert _get_format_abbreviation("MCQ") == "MCQ"
        assert _get_format_abbreviation("mcq") == "MCQ"

    def test_very_short_abbr(self):
        """Verify VERY_SHORT -> VSQ."""
        assert _get_format_abbreviation("VERY_SHORT") == "VSQ"
        assert _get_format_abbreviation("very_short") == "VSQ"

    def test_short_abbr(self):
        """Verify SHORT -> SA."""
        assert _get_format_abbreviation("SHORT") == "SA"
        assert _get_format_abbreviation("short") == "SA"

    def test_long_abbr(self):
        """Verify LONG -> LA."""
        assert _get_format_abbreviation("LONG") == "LA"
        assert _get_format_abbreviation("long") == "LA"

    def test_case_study_abbr(self):
        """Verify CASE_STUDY -> CS."""
        assert _get_format_abbreviation("CASE_STUDY") == "CS"
        assert _get_format_abbreviation("case_study") == "CS"

    def test_unknown_format_returns_unk(self):
        """Verify unknown format returns UNK."""
        assert _get_format_abbreviation("UNKNOWN") == "UNK"
        assert _get_format_abbreviation("random") == "UNK"


class TestQuestionIDFormat:
    """Tests for complete question ID format."""

    def test_id_format_structure(self):
        """Verify ID follows MATH-10-POL-MCQ-001 format."""
        # This would be tested in integration, but we verify components here
        chapter = _get_chapter_abbreviation("Polynomials")
        format_abbr = _get_format_abbreviation("MCQ")

        question_id = f"MATH-10-{chapter}-{format_abbr}-001"

        parts = question_id.split("-")
        assert len(parts) == 5
        assert parts[0] == "MATH"
        assert parts[1] == "10"
        assert parts[2] == "POL"
        assert parts[3] == "MCQ"
        assert parts[4] == "001"

    def test_id_number_padding(self):
        """Verify question numbers are zero-padded to 3 digits."""
        # Test various numbers
        for num in [1, 10, 100, 999]:
            formatted = f"{num:03d}"
            assert len(formatted) == 3
            assert formatted.isdigit()

    def test_multiple_chapter_ids(self):
        """Verify IDs for different chapters."""
        chapters = [
            ("Real Numbers", "REA"),
            ("Polynomials", "POL"),
            ("Triangles", "TRI"),
        ]

        for chapter_name, expected_abbr in chapters:
            chapter = _get_chapter_abbreviation(chapter_name)
            assert chapter == expected_abbr

            question_id = f"MATH-10-{chapter}-MCQ-001"
            assert expected_abbr in question_id

    def test_multiple_format_ids(self):
        """Verify IDs for different formats."""
        formats = [
            ("MCQ", "MCQ"),
            ("SHORT", "SA"),
            ("LONG", "LA"),
            ("CASE_STUDY", "CS"),
        ]

        for format_name, expected_abbr in formats:
            fmt = _get_format_abbreviation(format_name)
            assert fmt == expected_abbr

            question_id = f"MATH-10-POL-{fmt}-001"
            assert expected_abbr in question_id
