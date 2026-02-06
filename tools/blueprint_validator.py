"""Blueprint validation tool for CBSE question papers."""

import json
from typing import Dict, List, Optional
from langchain_core.tools import tool


@tool
def validate_blueprint_tool(
    blueprint_path: str, validate_rules: Optional[List[str]] = None
) -> Dict:
    """
    Validates CBSE blueprint JSON constraints.

    Args:
        blueprint_path: Path to blueprint JSON file
        validate_rules: List of validation rules to check (optional)

    Returns:
        {
          valid: bool,
          errors: list[str],
          warnings: list[str]
        }
    """
    errors = []
    warnings = []

    try:
        # Read blueprint from file using read_file (harness tool)
        # Note: This is a stub - actual implementation would use read_file tool
        with open(blueprint_path, "r") as f:
            blueprint = json.load(f)

        # Rule 1: Check required fields
        required_fields = ["exam_metadata", "syllabus_scope", "sections"]
        for field in required_fields:
            if field not in blueprint:
                errors.append(f"Missing required field: {field}")

        if blueprint.get("exam_metadata"):
            exam_meta = blueprint["exam_metadata"]
            required_meta = ["board", "class", "subject", "total_marks", "duration_minutes"]
            for field in required_meta:
                if field not in exam_meta:
                    errors.append(f"Missing exam_metadata field: {field}")

        # Rule 2: Check total marks calculation
        total_marks = blueprint.get("exam_metadata", {}).get("total_marks", 0)
        section_marks = 0

        for section in blueprint.get("sections", []):
            marks_per_q = section.get("marks_per_question", 0)
            questions_attempt = section.get(
                "questions_attempt", section.get("questions", {}).get("attempt", 0)
            )
            section_marks += marks_per_q * questions_attempt

        if total_marks > 0 and total_marks != section_marks:
            errors.append(
                f"Total marks mismatch: expected {total_marks}, calculated {section_marks}"
            )

        # Rule 3: Check internal_choice types
        valid_ic_types = ["none", "any_n_out_of_m", "either_or"]
        for section in blueprint.get("sections", []):
            ic_config = section.get("internal_choice", {})
            ic_type = ic_config.get("type") if isinstance(ic_config, dict) else None

            if ic_type and ic_type not in valid_ic_types:
                errors.append(
                    f"Section {section.get('section_id')}: invalid internal_choice type '{ic_type}'"
                )

            # Check attempt ≤ provided for any_n_out_of_m
            if ic_type == "any_n_out_of_m":
                ic_data = section.get("internal_choice", {})
                provided = ic_data.get("provided", 0)
                attempt = section.get(
                    "questions_attempt", section.get("questions", {}).get("attempt", 0)
                )

                if attempt > provided:
                    errors.append(
                        f"Section {section.get('section_id')}: attempt ({attempt}) > provided ({provided})"
                    )

        # Rule 4: Validate marks_per_question values
        valid_marks = [1, 2, 3, 4, 5]
        for section in blueprint.get("sections", []):
            marks = section.get("marks_per_question", 0)
            if marks > 0 and marks not in valid_marks:
                warnings.append(
                    f"Section {section.get('section_id')}: unusual marks_per_question {marks}"
                )

        # Rule 5: Check sections have valid question formats
        valid_formats = ["MCQ", "VERY_SHORT", "SHORT", "LONG", "CASE_STUDY", "ASSERTION_REASON"]
        for section in blueprint.get("sections", []):
            q_format = section.get("question_format")
            if q_format and q_format not in valid_formats:
                errors.append(
                    f"Section {section.get('section_id')}: invalid question format '{q_format}'"
                )

    except FileNotFoundError:
        errors.append(f"Blueprint file not found: {blueprint_path}")
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in blueprint: {str(e)}")
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
