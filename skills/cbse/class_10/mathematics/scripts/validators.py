"""
Validators for CBSE Question Paper Generator.

Helper functions to validate mark calculations,
blueprint constraints, and question consistency.
"""

from typing import List, Dict, Any, List


def validate_blueprint_section_totals(blueprint: Dict) -> List[str]:
    """
    Validate that section marks sum to total_marks in exam_metadata.

    Args:
        blueprint: Blueprint dictionary with sections and exam_metadata

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if "sections" not in blueprint:
        errors.append("Blueprint missing required 'sections' field")
        return errors

    if "exam_metadata" not in blueprint:
        errors.append("Blueprint missing required 'exam_metadata' field")
        return errors

    total_marks = blueprint.get("exam_metadata", {}).get("total_marks", 0)
    calculated_total = sum(
        section.get("marks_per_question", 0) * section.get("questions_provided", 0)
        for section in blueprint.get("sections", [])
    )

    if calculated_total != total_marks:
        errors.append(
            f"Section marks sum ({calculated_total}) does not equal total_marks ({total_marks})"
        )

    return errors


def validate_internal_choice(section: Dict) -> List[str]:
    """
    Validate internal choice constraints for a section.

    Args:
        section: Section dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    internal_choice = section.get("internal_choice", {})
    ic_type = internal_choice.get("type", "none")
    count_provided = section.get("questions_provided", 0)
    count_attempt = section.get("questions_to_attempt", count_provided)

    if ic_type not in ["none", "any_n_out_of_m", "either_or"]:
        errors.append(f"Invalid internal_choice type: {ic_type}")

    if ic_type == "any_n_out_of_m":
        if count_attempt > count_provided:
            errors.append(f"Attempt count ({count_attempt}) > provided ({count_provided})")

    return errors


def validate_question_count(required: int, generated: int, tolerance: int = 0) -> List[str]:
    """
    Validate generated question count matches required.

    Args:
        required: Required number from blueprint
        generated: Generated number
        tolerance: Allowed difference

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    difference = abs(required - generated)
    if difference > tolerance:
        errors.append(
            f"Generated {generated} questions, required {required} (difference: {difference})"
        )

    return errors


def validate_mark_calculation(section: Dict) -> List[str]:
    """
    Validate mark calculations for a section.

    Args:
        section: Section dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    marks_per = section.get("marks_per_question", 0)
    questions = section.get("questions_provided", 0)
    total_marks = section.get("total_section_marks", marks_per * questions)

    expected = marks_per * questions

    if total_marks != expected:
        errors.append(
            f"Section marks: {marks_per} × {questions} = {expected}, but total_section_marks = {total_marks}"
        )

    return errors


def validate_chapter_coverage(blueprint: Dict, generated_questions: List[Dict]) -> List[str]:
    """
    Validate that generated questions only use chapters from blueprint.

    Args:
        blueprint: Blueprint dictionary with sections and chapter assignments
        generated_questions: List of generated question dictionaries

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not blueprint.get("sections"):
        return ["Blueprint has no sections"]

    allowed_chapters = set()
    for section in blueprint.get("sections", []):
        chapter = section.get("chapter")
        if chapter:
            allowed_chapters.add(chapter)

    for question in generated_questions:
        chapter = question.get("chapter")
        if chapter not in allowed_chapters:
            errors.append(f"Question from invalid chapter: {chapter}")

    return errors


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        blueprint_path = sys.argv[1]
        with open(blueprint_path) as f:
            blueprint = json.load(f)

        errors = []
        errors.extend(validate_blueprint_section_totals(blueprint))

        if errors:
            print("Blueprint validation errors:")
            for err in errors:
                print(f"  - {err}")
        else:
            print("Blueprint validation passed!")
