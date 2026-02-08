"""Unit tests for blueprint JSON parsing."""

import pytest


class TestBlueprintMetadataExtraction:
    """Tests for extracting metadata from blueprint."""

    def test_extract_class_level(self, sample_blueprint):
        """Verify class level extraction."""
        metadata = sample_blueprint.get("metadata", {})
        assert metadata.get("class") == 10

    def test_extract_subject(self, sample_blueprint):
        """Verify subject extraction."""
        metadata = sample_blueprint.get("metadata", {})
        assert metadata.get("subject") == "Mathematics"

    def test_extract_total_marks(self, sample_blueprint):
        """Verify total marks extraction."""
        metadata = sample_blueprint.get("metadata", {})
        assert metadata.get("total_marks") == 50

    def test_extract_assessment_type(self, sample_blueprint):
        """Verify assessment type extraction."""
        metadata = sample_blueprint.get("metadata", {})
        assert metadata.get("assessment_type") == "First Term"

    def test_extract_duration(self, sample_blueprint):
        """Verify duration extraction."""
        assert sample_blueprint.get("duration_minutes") == 120


class TestSyllabusScopeExtraction:
    """Tests for extracting syllabus scope."""

    def test_extract_chapters(self, sample_blueprint):
        """Verify chapters extraction."""
        syllabus = sample_blueprint.get("syllabus_scope", {})
        chapters = syllabus.get("chapters", [])

        assert len(chapters) == 2
        assert chapters[0]["chapter_name"] == "Polynomials"
        assert chapters[1]["chapter_name"] == "Real Numbers"

    def test_extract_topics(self, sample_blueprint):
        """Verify topics extraction for each chapter."""
        syllabus = sample_blueprint.get("syllabus_scope", {})
        chapters = syllabus.get("chapters", [])

        polynomials = chapters[0]
        assert "Zeros of a Polynomial" in polynomials["topics"]
        assert "Relationship between Zeros" in polynomials["topics"]

    def test_build_chapter_topic_mapping(self, sample_blueprint):
        """Verify chapter to topics mapping."""
        chapters = sample_blueprint["syllabus_scope"]["chapters"]

        mapping = {}
        for chapter in chapters:
            mapping[chapter["chapter_name"]] = chapter["topics"]

        assert "Polynomials" in mapping
        assert "Real Numbers" in mapping
        assert len(mapping["Polynomials"]) == 2


class TestSectionExtraction:
    """Tests for extracting section details."""

    def test_extract_section_count(self, sample_blueprint):
        """Verify number of sections."""
        sections = sample_blueprint.get("sections", [])
        assert len(sections) == 1

    def test_extract_section_id(self, sample_blueprint):
        """Verify section ID extraction."""
        section = sample_blueprint["sections"][0]
        assert section["section_id"] == "A"

    def test_extract_question_format(self, sample_blueprint):
        """Verify question format extraction."""
        section = sample_blueprint["sections"][0]
        assert section["question_format"] == "MCQ"

    def test_extract_questions_provided(self, sample_blueprint):
        """Verify questions provided extraction."""
        section = sample_blueprint["sections"][0]
        assert section["questions_provided"] == 10

    def test_extract_marks_per_question(self, sample_blueprint):
        """Verify marks per question extraction."""
        section = sample_blueprint["sections"][0]
        assert section["marks_per_question"] == 1

    def test_extract_topic_focus(self, sample_blueprint):
        """Verify topic focus extraction."""
        section = sample_blueprint["sections"][0]
        topic_focus = section.get("topic_focus", [])

        assert "Zeros of a Polynomial" in topic_focus
        assert "Euclid's Division Lemma" in topic_focus

    def test_extract_allowed_natures(self, sample_blueprint):
        """Verify allowed question natures extraction."""
        section = sample_blueprint["sections"][0]
        natures = section.get("allowed_question_natures", [])

        assert "NUMERICAL" in natures
        assert "REASONING" in natures

    def test_extract_cognitive_hints(self, sample_blueprint):
        """Verify cognitive level hints extraction."""
        section = sample_blueprint["sections"][0]
        hints = section.get("cognitive_level_hint", [])

        assert "REMEMBER" in hints
        assert "UNDERSTAND" in hints


class TestBlueprintValidation:
    """Tests for validating blueprint structure."""

    def test_required_metadata_fields(self, sample_blueprint):
        """Verify required metadata fields present."""
        metadata = sample_blueprint.get("metadata", {})
        required = ["class", "subject", "total_marks"]

        for field in required:
            assert field in metadata, f"Missing required field: {field}"

    def test_required_syllabus_fields(self, sample_blueprint):
        """Verify required syllabus fields present."""
        syllabus = sample_blueprint.get("syllabus_scope", {})
        assert "chapters" in syllabus
        assert len(syllabus["chapters"]) > 0

    def test_required_section_fields(self, sample_blueprint):
        """Verify required section fields present."""
        section = sample_blueprint["sections"][0]
        required = ["section_id", "question_format", "questions_provided", "marks_per_question"]

        for field in required:
            assert field in section, f"Missing required field: {field}"


class TestTopicToChapterMapping:
    """Tests for mapping topics to chapters."""

    def test_find_chapter_for_topic(self, sample_blueprint):
        """Verify topic to chapter mapping."""
        chapters = sample_blueprint["syllabus_scope"]["chapters"]
        topic_to_find = "Zeros of a Polynomial"

        found_chapter = None
        for chapter in chapters:
            if topic_to_find in chapter["topics"]:
                found_chapter = chapter["chapter_name"]
                break

        assert found_chapter == "Polynomials"

    def test_all_topics_have_chapters(self, sample_blueprint):
        """Verify all topics in topic_focus have corresponding chapters."""
        sections = sample_blueprint.get("sections", [])
        chapters = sample_blueprint["syllabus_scope"]["chapters"]

        all_topics = []
        for section in sections:
            all_topics.extend(section.get("topic_focus", []))

        for topic in all_topics:
            found = any(
                topic in chapter["topics"] or chapter["topics"] == ["ALL_TOPICS"]
                for chapter in chapters
            )
            assert found, f"Topic '{topic}' not found in any chapter"
