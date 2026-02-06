"""Unit tests for blueprint_validator.py

Tests for CBSE Question Paper Generator blueprint validation logic.
Uses real blueprint files from fixtures for testing.
"""

import json
import pytest
from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def run_validation(exam_path, master_path=None):
    """Helper function to run validation by calling the underlying function."""
    from tools.blueprint_validator import validate_blueprint_tool

    # Access the underlying function through the tool's func attribute
    return validate_blueprint_tool.func(exam_path, master_path)


class TestSchemaVersion:
    """Tests for schema version validation."""

    def test_valid_schema_11(self, valid_exam_blueprint_path, master_blueprint_path):
        """Test that schema version 1.1 passes validation."""
        result = run_validation(valid_exam_blueprint_path, master_blueprint_path)

        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["validation_details"]["schema_version"] == "1.1"

    def test_invalid_schema_10(self, invalid_schema_10_path, master_blueprint_path):
        """Test that schema version 1.0 fails validation."""
        result = run_validation(invalid_schema_10_path, master_blueprint_path)

        assert result["valid"] is False
        assert any("1.1" in error and "1.0" in error for error in result["errors"])
        assert result["validation_details"]["schema_version"] == "1.0"


class TestQuestionFormatWhitelist:
    """Tests for QUESTION_FORMAT_WHITELIST validation."""

    def test_valid_format(self, valid_exam_blueprint_path, master_blueprint_path):
        """Test that valid question formats pass."""
        result = run_validation(valid_exam_blueprint_path, master_blueprint_path)

        assert result["valid"] is True
        assert "QUESTION_FORMAT_WHITELIST" in result["validation_details"]["strict_checks_passed"]

    def test_invalid_format(self, invalid_format_path, master_blueprint_data, tmp_path):
        """Test that invalid question formats fail with STRICT mode."""
        # Use STRICT mode to ensure errors are caught
        modified_master = master_blueprint_data.copy()
        modified_master["cognitive_levels"]["enforcement_mode"] = "STRICT"

        temp_master = tmp_path / "strict_master.json"
        with open(temp_master, "w") as f:
            json.dump(modified_master, f)

        result = run_validation(invalid_format_path, str(temp_master))

        assert result["valid"] is False
        assert any("INVALID_FORMAT" in error for error in result["errors"])
        assert "QUESTION_FORMAT_WHITELIST" in result["validation_details"]["strict_checks_failed"]

    @pytest.mark.parametrize(
        "format_name", ["MCQ", "MCQ_ASSERTION_REASON", "VERY_SHORT", "SHORT", "LONG", "CASE_STUDY"]
    )
    def test_allowed_formats(
        self, format_name, valid_exam_blueprint_data, master_blueprint_path, tmp_path
    ):
        """Test that all whitelisted formats are accepted."""
        # Modify blueprint to use the format
        valid_exam_blueprint_data["sections"][0]["question_format"] = format_name

        # Write to temp file
        temp_file = tmp_path / f"test_{format_name.lower()}.json"
        with open(temp_file, "w") as f:
            json.dump(valid_exam_blueprint_data, f)

        result = run_validation(str(temp_file), master_blueprint_path)

        assert result["valid"] is True, f"Format {format_name} should be valid"


class TestInternalChoiceArithmetic:
    """Tests for INTERNAL_CHOICE_ARITHMETIC validation."""

    def test_valid_internal_choice(self, valid_exam_blueprint_path, master_blueprint_path):
        """Test valid internal choice (attempt <= provided)."""
        result = run_validation(valid_exam_blueprint_path, master_blueprint_path)

        # Valid blueprint has no internal_choice or valid one
        if result["valid"]:
            assert (
                "INTERNAL_CHOICE_ARITHMETIC" in result["validation_details"]["strict_checks_passed"]
            )

    def test_invalid_internal_choice_attempt_gt_provided(
        self, invalid_internal_choice_path, master_blueprint_data, tmp_path
    ):
        """Test that attempt > provided fails with STRICT mode."""
        # Use STRICT mode to ensure errors are caught
        modified_master = master_blueprint_data.copy()
        modified_master["cognitive_levels"]["enforcement_mode"] = "STRICT"

        temp_master = tmp_path / "strict_master.json"
        with open(temp_master, "w") as f:
            json.dump(modified_master, f)

        result = run_validation(invalid_internal_choice_path, str(temp_master))

        assert result["valid"] is False
        assert any(
            "attempt" in error.lower() and "provided" in error.lower() for error in result["errors"]
        )

    def test_invalid_internal_choice_type(
        self, comprehensive_violations_path, master_blueprint_data, tmp_path
    ):
        """Test that unsupported internal choice type fails with STRICT mode."""
        # Use STRICT mode to ensure errors are caught
        modified_master = master_blueprint_data.copy()
        modified_master["cognitive_levels"]["enforcement_mode"] = "STRICT"

        temp_master = tmp_path / "strict_master.json"
        with open(temp_master, "w") as f:
            json.dump(modified_master, f)

        result = run_validation(comprehensive_violations_path, str(temp_master))

        assert result["valid"] is False
        assert any(
            "invalid_type" in error.lower() or "unsupported" in error.lower()
            for error in result["errors"]
        )


class TestSyllabusScopeEnforcement:
    """Tests for SYLLABUS_SCOPE_ENFORCEMENT validation."""

    def test_valid_syllabus_scope(self, valid_exam_blueprint_path, master_blueprint_path):
        """Test that chapters with topics pass."""
        result = run_validation(valid_exam_blueprint_path, master_blueprint_path)

        assert result["valid"] is True
        assert "SYLLABUS_SCOPE_ENFORCEMENT" in result["validation_details"]["strict_checks_passed"]

    def test_missing_topics(self, missing_topics_path, master_blueprint_data, tmp_path):
        """Test that chapter without topics fails when topic_selection_required is true with STRICT mode."""
        # Use STRICT mode to ensure errors are caught
        modified_master = master_blueprint_data.copy()
        modified_master["cognitive_levels"]["enforcement_mode"] = "STRICT"

        temp_master = tmp_path / "strict_master.json"
        with open(temp_master, "w") as f:
            json.dump(modified_master, f)

        result = run_validation(missing_topics_path, str(temp_master))

        assert result["valid"] is False
        assert any(
            "topics" in error.lower() and "polynomials" in error.lower()
            for error in result["errors"]
        )
        assert "SYLLABUS_SCOPE_ENFORCEMENT" in result["validation_details"]["strict_checks_failed"]

    def test_all_topics_keyword(self, all_topics_keyword_path, master_blueprint_path):
        """Test that ALL_TOPICS keyword is accepted."""
        result = run_validation(all_topics_keyword_path, master_blueprint_path)

        # Should pass because Polynomials chapter uses ALL_TOPICS
        assert result["valid"] is True


class TestTopicScopeEnforcement:
    """Tests for TOPIC_SCOPE_ENFORCEMENT validation."""

    def test_valid_topic_focus(self, valid_exam_blueprint_path, master_blueprint_path):
        """Test that valid topic_focus passes."""
        result = run_validation(valid_exam_blueprint_path, master_blueprint_path)

        assert result["valid"] is True
        assert "TOPIC_SCOPE_ENFORCEMENT" in result["validation_details"]["strict_checks_passed"]

    def test_invalid_topic_focus(self, invalid_topic_focus_path, master_blueprint_data, tmp_path):
        """Test that invalid topic_focus fails with STRICT mode."""
        # Use STRICT mode to ensure errors are caught
        modified_master = master_blueprint_data.copy()
        modified_master["cognitive_levels"]["enforcement_mode"] = "STRICT"

        temp_master = tmp_path / "strict_master.json"
        with open(temp_master, "w") as f:
            json.dump(modified_master, f)

        result = run_validation(invalid_topic_focus_path, str(temp_master))

        assert result["valid"] is False
        assert any(
            "non-existent" in error.lower() or "not in syllabus" in error.lower()
            for error in result["errors"]
        )

    def test_missing_topic_focus(self, missing_topic_focus_path, master_blueprint_path):
        """Test that missing topic_focus passes (inherits global scope)."""
        result = run_validation(missing_topic_focus_path, master_blueprint_path)

        # Should pass because missing topic_focus is allowed
        assert result["valid"] is True

    def test_invalid_topic_focus_type(
        self, invalid_topic_focus_type_path, master_blueprint_data, tmp_path
    ):
        """Test that non-array topic_focus fails with STRICT mode."""
        # Use STRICT mode to ensure errors are caught
        modified_master = master_blueprint_data.copy()
        modified_master["cognitive_levels"]["enforcement_mode"] = "STRICT"

        temp_master = tmp_path / "strict_master.json"
        with open(temp_master, "w") as f:
            json.dump(modified_master, f)

        result = run_validation(invalid_topic_focus_type_path, str(temp_master))

        assert result["valid"] is False
        assert any("must be an array" in error.lower() for error in result["errors"])

    def test_all_topics_accepts_any_topic(self, all_topics_keyword_path, master_blueprint_path):
        """Test that chapter with ALL_TOPICS accepts any topic in topic_focus."""
        result = run_validation(all_topics_keyword_path, master_blueprint_path)

        # Should pass because Polynomials chapter uses ALL_TOPICS
        assert result["valid"] is True


class TestAdvisoryChecks:
    """Tests for advisory validation checks."""

    def test_cognitive_distribution_warning(self, valid_exam_blueprint_path, master_blueprint_path):
        """Test that cognitive distribution advisory check runs."""
        result = run_validation(valid_exam_blueprint_path, master_blueprint_path)

        # Advisory checks may or may not produce warnings depending on blueprint
        # Just verify the field exists
        assert "advisory_checks_warnings" in result["validation_details"]

    def test_question_nature_balance_warning(
        self, valid_exam_blueprint_path, master_blueprint_path
    ):
        """Test that question nature balance advisory check runs."""
        result = run_validation(valid_exam_blueprint_path, master_blueprint_path)

        # Just verify the field exists
        assert "advisory_checks_warnings" in result["validation_details"]


class TestEnforcementModes:
    """Tests for different enforcement modes."""

    def test_enforcement_mode_advisory(
        self, invalid_format_path, master_blueprint_path, master_blueprint_data, tmp_path
    ):
        """Test ADVISORY mode converts strict check errors to warnings."""
        # Modify master blueprint to use ADVISORY mode
        modified_master = master_blueprint_data.copy()
        modified_master["cognitive_levels"]["enforcement_mode"] = "ADVISORY"

        temp_master = tmp_path / "advisory_master.json"
        with open(temp_master, "w") as f:
            json.dump(modified_master, f)

        result = run_validation(invalid_format_path, str(temp_master))

        # In advisory mode, strict checks become warnings
        assert result["valid"] is True or len(result["warnings"]) > 0


class TestComprehensiveViolations:
    """Tests for blueprints with multiple violations."""

    def test_comprehensive_violations_detected(
        self, comprehensive_violations_path, master_blueprint_data, tmp_path
    ):
        """Test that all violations in a comprehensive invalid blueprint are detected with STRICT mode."""
        # Use STRICT mode to ensure errors are caught
        modified_master = master_blueprint_data.copy()
        modified_master["cognitive_levels"]["enforcement_mode"] = "STRICT"

        temp_master = tmp_path / "strict_master.json"
        with open(temp_master, "w") as f:
            json.dump(modified_master, f)

        result = run_validation(comprehensive_violations_path, str(temp_master))

        assert result["valid"] is False
        assert len(result["errors"]) >= 3  # Should detect multiple issues

        # Check for various violation types
        error_text = " ".join(result["errors"]).lower()
        assert "invalid_format" in error_text or "invalid" in error_text
        assert "polynomials" in error_text or "topics" in error_text


class TestBlueprintDiscovery:
    """Tests for master blueprint auto-discovery."""

    def test_auto_discovery_from_metadata(
        self, valid_exam_blueprint_path, master_blueprint_path, project_root
    ):
        """Test that master blueprint is auto-discovered from exam blueprint metadata."""
        # Change to project root for relative path resolution
        import os

        original_dir = os.getcwd()
        os.chdir(project_root)

        try:
            result = run_validation(valid_exam_blueprint_path)

            # Should auto-discover and validate
            assert "validation_details" in result
        finally:
            os.chdir(original_dir)

    def test_custom_master_blueprint_path(self, valid_exam_blueprint_path, master_blueprint_path):
        """Test that custom master blueprint path is used."""
        result = run_validation(valid_exam_blueprint_path, master_blueprint_path)

        assert result["valid"] is True

    def test_missing_master_blueprint(self, valid_exam_blueprint_path):
        """Test error handling when master blueprint is missing."""
        result = run_validation(valid_exam_blueprint_path, "nonexistent/path.json")

        assert result["valid"] is False
        assert any("not found" in error.lower() for error in result["errors"])


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_invalid_json_file(self, master_blueprint_path, tmp_path):
        """Test handling of invalid JSON file."""
        # Create invalid JSON file
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{invalid json")

        result = run_validation(str(invalid_file), master_blueprint_path)

        assert result["valid"] is False
        assert any("json" in error.lower() for error in result["errors"])

    def test_missing_required_fields(self, master_blueprint_data, tmp_path):
        """Test handling of blueprint missing required fields with STRICT mode."""
        # Create blueprint missing sections
        invalid_blueprint = {"schema_version": "1.1"}

        invalid_file = tmp_path / "missing_fields.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_blueprint, f)

        # Use STRICT mode to ensure errors are caught
        modified_master = master_blueprint_data.copy()
        modified_master["cognitive_levels"]["enforcement_mode"] = "STRICT"

        temp_master = tmp_path / "strict_master.json"
        with open(temp_master, "w") as f:
            json.dump(modified_master, f)

        result = run_validation(str(invalid_file), str(temp_master))

        # Should fail validation
        assert result["valid"] is False

    def test_empty_sections_array(self, valid_exam_blueprint_data, master_blueprint_path, tmp_path):
        """Test handling of empty sections array."""
        # Modify blueprint to have empty sections
        valid_exam_blueprint_data["sections"] = []

        temp_file = tmp_path / "empty_sections.json"
        with open(temp_file, "w") as f:
            json.dump(valid_exam_blueprint_data, f)

        result = run_validation(str(temp_file), master_blueprint_path)

        # Empty sections is technically valid but useless
        # The validator should handle it gracefully
        assert "validation_details" in result


class TestValidationDetails:
    """Tests for validation details structure."""

    def test_validation_details_structure(self, valid_exam_blueprint_path, master_blueprint_path):
        """Test that validation_details has correct structure."""
        result = run_validation(valid_exam_blueprint_path, master_blueprint_path)

        assert "validation_details" in result
        details = result["validation_details"]

        assert "schema_version" in details
        assert "enforcement_mode" in details
        assert "strict_checks_passed" in details
        assert "strict_checks_failed" in details
        assert "advisory_checks_warnings" in details

        assert isinstance(details["strict_checks_passed"], list)
        assert isinstance(details["strict_checks_failed"], list)
        assert isinstance(details["advisory_checks_warnings"], list)

    def test_passed_checks_populated(self, valid_exam_blueprint_path, master_blueprint_path):
        """Test that passed checks are populated for valid blueprint."""
        result = run_validation(valid_exam_blueprint_path, master_blueprint_path)

        assert len(result["validation_details"]["strict_checks_passed"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
